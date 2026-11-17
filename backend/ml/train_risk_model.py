"""FamSecur alan adı risk modelini eğitir.

Kullanım (backend/ klasöründen):

    python -m ml.train_risk_model --download        # verileri indir + eğit
    python -m ml.train_risk_model                   # ml/data içindeki verilerle eğit

Model ne yapar?
    Bir alan adının harf dizilerine (karakter n-gram) bakarak üç sınıftan
    hangisine benzediğini tahmin eder: ``clean`` (temiz), ``gambling`` (kumar),
    ``adult`` (yetişkin). Risk puanı = 1 - P(clean).

Adımlar:
    1. Veri: resmî kumar listesi + yetişkin içerik listesi (riskli),
       Cisco Umbrella en popüler 1 milyon alan adı (temiz).
    2. Her alan adı kayıtlı alan adına indirilir (www.x.com → x.com).
    3. Küme: ~100.000 riskli + bulunabilen tüm temiz alan adları (~238.000).
       Sınıf dengesizliği ``class_weight="balanced"`` ile giderilir: az örneği
       olan sınıfın her hatası daha pahalı sayılır. Daha çok temiz örnek,
       modelin "sahibinden.com" gibi masum Türkçe adları yanlış işaretlemesini
       azaltır.
    4. %80 eğitim / %20 test (hold-out) ayrımı.
    5. Özellik çıkarma: karakter 2-5 gram → hashing → TF-IDF.
    6. Sınıflandırıcı: Lojistik Regresyon.
    7. Test kümesinde doğruluk ölçülür, model joblib ile kaydedilir.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import random
import sys
import time
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.feature_extraction.text import HashingVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .features import model_text, registered_domain

ML_DIR = Path(__file__).resolve().parent
DATA_DIR = ML_DIR / "data"  # git'e eklenmez (büyük ham veriler)
MODEL_DIR = ML_DIR / "model"
MODEL_PATH = MODEL_DIR / "domain_risk.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"

GAMBLING_FEED = ML_DIR.parent / "shield" / "feeds" / "poland_official_gambling_domains_20260723.txt"
ADULT_URL = "https://raw.githubusercontent.com/blocklistproject/Lists/master/porn.txt"
CLEAN_URL = "https://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"
ADULT_FILE = DATA_DIR / "adult_porn.txt"
CLEAN_FILE = DATA_DIR / "umbrella_top-1m.csv"

RISKY_TARGET = 100_000
CLEAN_TARGET: int | None = None  # None → tüm temiz alan adları
# Bir kayıtlı alan adı yetişkin listesinde bu kadar farklı alt alan adıyla
# geçiyorsa (ör. tumblr.com) bu bir barındırma platformudur; tek başına riskli
# sayılmaz ve iki sınıftan da çıkarılır.
PLATFORM_MIN_SUBDOMAINS = 20
SEED = 42


def download(url: str, target: Path) -> None:
    print(f"İndiriliyor: {url}")
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    if url.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            data = archive.read(archive.namelist()[0])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(f"  → {target} ({len(data) / 1e6:.1f} MB)")


def read_domain_lines(path: Path) -> list[str]:
    """Düz liste veya hosts biçimindeki (``0.0.0.0 ornek.com``) satırları okur."""
    domains = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        domains.append(line.split()[-1].lower())
    return domains


def read_umbrella(path: Path) -> list[str]:
    with path.open(encoding="utf-8", errors="ignore") as handle:
        return [row[1].strip().lower() for row in csv.reader(handle) if len(row) >= 2]


def to_registered(domains: list[str]) -> Counter:
    """Kayıtlı alan adlarını ve kaç farklı ham kayıttan geldiklerini sayar."""
    counts: Counter = Counter()
    for domain in domains:
        reg = registered_domain(domain)
        if reg:
            counts[reg] += 1
    return counts


def build_dataset(rng: random.Random) -> tuple[list[str], list[str], dict]:
    gambling = to_registered(read_domain_lines(GAMBLING_FEED))
    adult_counts = to_registered(read_domain_lines(ADULT_FILE))
    platforms = {d for d, n in adult_counts.items() if n >= PLATFORM_MIN_SUBDOMAINS}
    adult = set(adult_counts) - platforms - set(gambling)

    clean = set(to_registered(read_umbrella(CLEAN_FILE)))
    clean -= set(gambling) | set(adult_counts)  # listede olan hiçbir şey "temiz" sayılmaz
    clean = {d for d in clean if not d.endswith(".arpa")}

    gambling_list = sorted(gambling)
    adult_list = sorted(adult)
    clean_list = sorted(clean)
    rng.shuffle(gambling_list)
    rng.shuffle(adult_list)
    rng.shuffle(clean_list)

    gambling_sample = gambling_list[:RISKY_TARGET]
    adult_sample = adult_list[: RISKY_TARGET - len(gambling_sample)]
    clean_sample = clean_list[:CLEAN_TARGET]

    domains = gambling_sample + adult_sample + clean_sample
    labels = ["gambling"] * len(gambling_sample) + ["adult"] * len(adult_sample) + ["clean"] * len(clean_sample)
    stats = {
        "gambling_available": len(gambling_list),
        "adult_available": len(adult_list),
        "adult_platforms_removed": sorted(platforms)[:50],
        "clean_available": len(clean_list),
        "gambling_used": len(gambling_sample),
        "adult_used": len(adult_sample),
        "clean_used": len(clean_sample),
    }
    return domains, labels, stats


def make_pipeline() -> Pipeline:
    return Pipeline([
        # Karakter 2-5 gramları: "bahis", "casin", "porn", "bet" gibi parçaları
        # sözlük tutmadan sabit boyutlu bir vektöre (hashing) yerleştirir.
        ("ngrams", HashingVectorizer(
            analyzer="char", ngram_range=(2, 5), n_features=2**18,
            alternate_sign=False, norm=None, lowercase=True,
        )),
        # TF-IDF: her alan adında sık, genelde nadir parçalar daha ağır basar.
        ("tfidf", TfidfTransformer(sublinear_tf=True)),
        ("clf", LogisticRegression(C=4.0, max_iter=2000, class_weight="balanced")),
    ])


def shrink(model: Pipeline) -> None:
    """Ağırlıkları float32'ye çevirir: dosya yarıya iner, doğruluk değişmez."""
    clf = model.named_steps["clf"]
    clf.coef_ = clf.coef_.astype(np.float32)
    clf.intercept_ = clf.intercept_.astype(np.float32)
    tfidf = model.named_steps["tfidf"]
    tfidf.idf_ = tfidf.idf_.astype(np.float32)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FamSecur alan adı risk modelini eğitir.")
    parser.add_argument("--download", action="store_true", help="Ham verileri internetten indir")
    args = parser.parse_args(argv)

    if args.download or not ADULT_FILE.exists():
        download(ADULT_URL, ADULT_FILE)
    if args.download or not CLEAN_FILE.exists():
        download(CLEAN_URL, CLEAN_FILE)

    rng = random.Random(SEED)
    print("Veri kümesi hazırlanıyor…")
    domains, labels, stats = build_dataset(rng)
    print(f"  {len(domains):,} alan adı: {Counter(labels)}")

    texts = [model_text(d) for d in domains]
    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=SEED, stratify=labels,
    )

    print("Model eğitiliyor…")
    started = time.time()
    model = make_pipeline()
    model.fit(x_train, y_train)
    shrink(model)
    train_seconds = time.time() - started

    predictions = model.predict(x_test)
    proba = model.predict_proba(x_test)
    clean_index = list(model.classes_).index("clean")
    risk = 1 - proba[:, clean_index]
    y_test_risky = np.array([label != "clean" for label in y_test])
    pred_risky = risk >= 0.5

    report = classification_report(y_test, predictions, digits=4, output_dict=True)
    metrics = {
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sklearn_version": sklearn.__version__,
        "train_size": len(x_train),
        "test_size": len(x_test),
        "train_seconds": round(train_seconds, 1),
        "accuracy_3class": round(accuracy_score(y_test, predictions), 4),
        "accuracy_risky_vs_clean": round(float((pred_risky == y_test_risky).mean()), 4),
        "risky_recall": round(float(pred_risky[y_test_risky].mean()), 4),
        "clean_recall": round(float((~pred_risky[~y_test_risky]).mean()), 4),
        "roc_auc_risky_vs_clean": round(float(roc_auc_score(y_test_risky, risk)), 4),
        "per_class": {
            label: {k: round(v, 4) for k, v in report[label].items()}
            for label in model.classes_
        },
        "confusion_matrix": {
            "labels": list(model.classes_),
            "rows_true_cols_pred": confusion_matrix(y_test, predictions, labels=model.classes_).tolist(),
        },
        "data": stats,
    }

    print(classification_report(y_test, predictions, digits=4))
    print(f"3 sınıf doğruluğu:            {metrics['accuracy_3class']:.2%}")
    print(f"Riskli/temiz doğruluğu:       {metrics['accuracy_risky_vs_clean']:.2%}")
    print(f"Riskli yakalama oranı:        {metrics['risky_recall']:.2%}")
    print(f"Temizi doğru bırakma oranı:   {metrics['clean_recall']:.2%}")
    print(f"ROC AUC (riskli/temiz):       {metrics['roc_auc_risky_vs_clean']:.4f}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH, compress=("xz", 9))
    METRICS_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Model kaydedildi: {MODEL_PATH} ({MODEL_PATH.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
