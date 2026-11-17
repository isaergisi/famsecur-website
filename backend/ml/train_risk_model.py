"""FamSecur alan adı risk modelini eğitir.

Kullanım (backend/ klasöründen):

    python -m ml.train_risk_model --download        # verileri indir + eğit
    python -m ml.train_risk_model                   # ml/data içindeki verilerle eğit

Model ne yapar?
    Bir alan adının harf dizilerine (karakter n-gram) bakarak üç sınıftan
    hangisine benzediğini tahmin eder: ``clean`` (temiz), ``gambling`` (kumar),
    ``adult`` (yetişkin). Risk puanı = 1 - P(clean).

Adımlar:
    1. Veri: resmî kumar listesi + Block List Project kumar/yetişkin listeleri
       (riskli), Cisco Umbrella ilk 1 milyon + Türkiye CrUX listesi (temiz).
    2. Her alan adı kayıtlı alan adına indirilir (www.x.com → x.com).
    3. Temiz listelerde kural motorunun açıkça engellediği adlar riskli
       örneğe dönüştürülür (Türkçe bahis/yetişkin adları için).
    4. Küme: 100.000 kumar + 100.000 yetişkin + tüm temiz alan adları.
       Sınıf dengesizliği ``class_weight="balanced"`` ile giderilir.
    5. %80 eğitim / %20 test (hold-out) ayrımı.
    6. Özellik çıkarma: karakter 2-5 gram → hashing → TF-IDF.
    7. Sınıflandırıcı: Lojistik Regresyon.
    8. Test kümesinde doğruluk ölçülür, model joblib ile kaydedilir.
       ``--compare eski.joblib`` verilirse eski model aynı kümede ölçülür.
"""

from __future__ import annotations

import argparse
import csv
import gzip
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
from urllib.parse import urlparse

import joblib
import numpy as np
import sklearn
from sklearn.feature_extraction.text import HashingVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from shield.classifier import analyze_domain

from .features import model_text, registered_domain

ML_DIR = Path(__file__).resolve().parent
DATA_DIR = ML_DIR / "data"  # git'e eklenmez (büyük ham veriler)
MODEL_DIR = ML_DIR / "model"
MODEL_PATH = MODEL_DIR / "domain_risk.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"

GAMBLING_FEED = ML_DIR.parent / "shield" / "feeds" / "poland_official_gambling_domains_20260723.txt"
SOURCES = {
    # Riskli: yetişkin içerik ve kumar listeleri (The Block List Project, MIT lisansı)
    "adult": ("https://raw.githubusercontent.com/blocklistproject/Lists/master/porn.txt", DATA_DIR / "adult_porn.txt"),
    "gambling": ("https://raw.githubusercontent.com/blocklistproject/Lists/master/gambling.txt", DATA_DIR / "gambling_blp.txt"),
    # Temiz: dünyada en çok sorgulanan 1 milyon alan adı (Cisco Umbrella)
    "umbrella": ("https://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip", DATA_DIR / "umbrella_top-1m.csv"),
    # Temiz: Türkiye'de Chrome ile en çok ziyaret edilen siteler (Google CrUX)
    "crux_tr": ("https://raw.githubusercontent.com/zakird/crux-top-lists/main/data/country/tr/202610.csv.gz", DATA_DIR / "crux_tr.csv"),
}

GAMBLING_TARGET = 100_000
ADULT_TARGET = 100_000
CLEAN_TARGET: int | None = None  # None → tüm temiz alan adları
# Bir kayıtlı alan adı riskli listelerde bu kadar farklı alt alan adıyla
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
    elif url.endswith(".gz"):
        data = gzip.decompress(data)
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


def read_crux(path: Path) -> list[str]:
    """CrUX satırları ``https://www.ornek.com.tr,1000`` biçimindedir."""
    with path.open(encoding="utf-8", errors="ignore") as handle:
        rows = csv.reader(handle)
        next(rows, None)  # başlık satırı
        return [urlparse(row[0]).hostname or "" for row in rows if row]


def flagged_by_rules(domain: str) -> str | None:
    """Kural tabanlı karar motoru bu adı kumar/yetişkin olarak engelliyorsa kategorisini döner.

    Türkiye'de popüler siteler listesinde, henüz hiçbir kara listeye girmemiş
    yasa dışı bahis ve yetişkin siteleri de var. Bunları "temiz" diye öğretmek
    modeli bozar. Bu siteler temiz kümeden çıkarılır ve kural motorunun verdiği
    kategoriyle riskli örnek olarak eklenir (zayıf etiketleme). Kara listeler
    çoğunlukla yabancı sitelerden oluştuğu için modelin Türkçe riskli adları
    (ör. "canlibahis", "yenibahisadresi") öğrenmesini sağlayan budur.
    """
    decision = analyze_domain(domain, enabled_categories=("gambling", "adult"))
    return decision.category if decision.action == "block" else None


def to_registered(domains: list[str]) -> Counter:
    """Kayıtlı alan adlarını ve kaç farklı ham kayıttan geldiklerini sayar."""
    counts: Counter = Counter()
    for domain in domains:
        reg = registered_domain(domain)
        if reg:
            counts[reg] += 1
    return counts


def build_dataset(rng: random.Random) -> tuple[list[str], list[str], list[str], dict]:
    """Alan adları, etiketler ve her örneğin kaynağını (ör. ``crux_tr``) döner."""
    gambling_counts = to_registered(read_domain_lines(GAMBLING_FEED) + read_domain_lines(SOURCES["gambling"][1]))
    adult_counts = to_registered(read_domain_lines(SOURCES["adult"][1]))
    platforms = {d for counts in (gambling_counts, adult_counts) for d, n in counts.items() if n >= PLATFORM_MIN_SUBDOMAINS}
    gambling = set(gambling_counts) - platforms
    adult = set(adult_counts) - platforms - gambling
    listed = set(gambling_counts) | set(adult_counts)  # listede olan hiçbir şey "temiz" sayılmaz

    clean_source: dict[str, str] = {}
    rule_labeled: dict[str, str] = {}
    removed_by_rules = Counter()
    for source, domains in (("crux_tr", read_crux(SOURCES["crux_tr"][1])), ("umbrella", read_umbrella(SOURCES["umbrella"][1]))):
        for domain in to_registered(domains):
            if domain in listed or domain in clean_source or domain in rule_labeled or domain.endswith(".arpa"):
                continue
            category = flagged_by_rules(domain)
            if category:
                removed_by_rules[source] += 1
                rule_labeled[domain] = category
                continue
            clean_source[domain] = source

    gambling_list, adult_list, clean_list = sorted(gambling), sorted(adult), sorted(clean_source)
    for items in (gambling_list, adult_list, clean_list):
        rng.shuffle(items)
    # Kural etiketli Türkiye örneklerinin hepsi kullanılır; geri kalan kota
    # kara listelerden doldurulur.
    rule_gambling = sorted(d for d, c in rule_labeled.items() if c == "gambling")
    rule_adult = sorted(d for d, c in rule_labeled.items() if c == "adult")
    gambling_sample = rule_gambling + gambling_list[: GAMBLING_TARGET - len(rule_gambling)]
    adult_sample = rule_adult + adult_list[: ADULT_TARGET - len(rule_adult)]
    clean_sample = clean_list[:CLEAN_TARGET]

    domains = gambling_sample + adult_sample + clean_sample
    labels = ["gambling"] * len(gambling_sample) + ["adult"] * len(adult_sample) + ["clean"] * len(clean_sample)
    sources = ["risky"] * (len(gambling_sample) + len(adult_sample)) + [clean_source[d] for d in clean_sample]
    stats = {
        "gambling_available": len(gambling_list),
        "adult_available": len(adult_list),
        "platforms_removed": len(platforms),
        "clean_available": len(clean_list),
        "clean_by_source": dict(Counter(clean_source.values())),
        "rule_labeled_risky_by_source": dict(removed_by_rules),
        "rule_labeled_gambling": len(rule_gambling),
        "rule_labeled_adult": len(rule_adult),
        "gambling_used": len(gambling_sample),
        "adult_used": len(adult_sample),
        "clean_used": len(clean_sample),
    }
    return domains, labels, sources, stats


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


# Türkiye'de çok kullanılan, risksiz siteler. Model eğitiminde ayrıca
# kullanılmaz; yalnızca Türkçe adlardaki hataları gözle kontrol etmek içindir.
TURKISH_PROBES = (
    "sahibinden.com", "hepsiburada.com", "trendyol.com", "eksisozluk.com", "n11.com",
    "yemeksepeti.com", "turkiye.gov.tr", "meb.gov.tr", "hurriyet.com.tr", "sozcu.com.tr",
    "milliyet.com.tr", "haberturk.com", "ntv.com.tr", "letgo.com", "getir.com",
    "akakce.com", "cimri.com", "kitapyurdu.com", "dr.com.tr", "mynet.com",
    "donanimhaber.com", "sikayetvar.com", "isbank.com.tr", "ziraatbank.com.tr", "garantibbva.com.tr",
    "pttavm.com", "turkcell.com.tr", "vodafone.com.tr", "thy.com", "obilet.com",
    "kariyer.net", "emlakjet.com", "arabam.com", "yandex.com.tr", "osym.gov.tr",
    "anadolu.edu.tr", "odtu.edu.tr", "bilkent.edu.tr", "sabah.com.tr", "cumhuriyet.com.tr",
)


def evaluate(model: Pipeline, x_test: list[str], y_test: list[str], sources: list[str]) -> dict:
    """Bir modeli ortak test kümesinde ve Türkçe kontrol listesinde ölçer."""
    clean_index = list(model.classes_).index("clean")
    risk = 1 - model.predict_proba(x_test)[:, clean_index]
    risky = np.array([label != "clean" for label in y_test])
    from_tr = np.array([source == "crux_tr" for source in sources])
    probe_risk = 1 - model.predict_proba([model_text(d) for d in TURKISH_PROBES])[:, clean_index]
    return {
        "accuracy_3class": round(accuracy_score(y_test, model.predict(x_test)), 4),
        "accuracy_risky_vs_clean": round(float(((risk >= 0.5) == risky).mean()), 4),
        "risky_recall": round(float((risk[risky] >= 0.5).mean()), 4),
        "clean_recall": round(float((risk[~risky] < 0.5).mean()), 4),
        "clean_recall_turkey_popular": round(float((risk[from_tr] < 0.5).mean()), 4),
        "turkish_probes_false_alarms": int((probe_risk >= 0.5).sum()),
        "turkish_probes_warnings": int((probe_risk >= 0.6).sum()),
        "turkish_probes_mean_risk": round(float(probe_risk.mean()) * 100, 1),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FamSecur alan adı risk modelini eğitir.")
    parser.add_argument("--download", action="store_true", help="Ham verileri internetten indir")
    parser.add_argument("--compare", type=Path, help="Aynı test kümesinde karşılaştırılacak eski model dosyası")
    args = parser.parse_args(argv)

    for url, path in SOURCES.values():
        if args.download or not path.exists():
            download(url, path)

    rng = random.Random(SEED)
    print("Veri kümesi hazırlanıyor…")
    domains, labels, sources, stats = build_dataset(rng)
    print(f"  {len(domains):,} alan adı: {Counter(labels)}")

    texts = [model_text(d) for d in domains]
    x_train, x_test, y_train, y_test, _, src_test = train_test_split(
        texts, labels, sources, test_size=0.2, random_state=SEED, stratify=labels,
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
    metrics["evaluation"] = {"new_model": evaluate(model, x_test, y_test, src_test)}
    if args.compare:
        old = joblib.load(args.compare)
        metrics["evaluation"]["old_model"] = evaluate(old, x_test, y_test, src_test)
        print("Aynı test kümesinde eski / yeni model:")
        for key, value in metrics["evaluation"]["new_model"].items():
            print(f"  {key:32} {metrics['evaluation']['old_model'][key]}  →  {value}")

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
