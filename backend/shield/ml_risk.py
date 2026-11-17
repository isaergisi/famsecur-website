"""Eğitilmiş yapay zeka modeliyle alan adı risk tahmini.

Model ``ml/train_risk_model.py`` ile eğitilir ve ``ml/model/domain_risk.joblib``
dosyasına kaydedilir. Burada yalnızca dosya bir kez belleğe yüklenir ve
tahmin yapılır; eğitim sunucuda çalışmaz.

Bu tahmin bir **uyarıdır**, engel kararı değildir: kesin engel kararını
açıklanabilir karar motoru (``classifier.py``) ve alan adı listeleri verir.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from .classifier import CATEGORY_LABELS

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "model" / "domain_risk.joblib"
# Bu puanın üzerindeki tahminler ebeveyne "dikkat" uyarısı olarak gösterilir.
WARNING_THRESHOLD = 60


@lru_cache(maxsize=1)
def load_model():
    """Modeli ilk kullanımda bir kez yükler. Yoksa ``None`` döner (site çalışmaya devam eder)."""
    try:
        import joblib

        return joblib.load(MODEL_PATH)
    except Exception as exc:  # dosya yok, scikit-learn kurulu değil, sürüm uyumsuz…
        logger.warning("Yapay zeka risk modeli yüklenemedi: %s", exc)
        return None


def predict_risk(domain: str) -> dict | None:
    """Alan adı için ``{"risk": 0-100, "category": ..., "warning": bool}`` döner.

    Model yoksa veya alan adı çözümlenemezse ``None`` döner.
    """
    model = load_model()
    if model is None:
        return None
    from ml.features import model_text, registered_domain

    reg = registered_domain(domain)
    if not reg:
        return None
    probabilities = dict(zip(model.classes_, model.predict_proba([model_text(reg)])[0]))
    risk = round((1 - probabilities["clean"]) * 100)
    category = max((c for c in probabilities if c != "clean"), key=probabilities.get)
    return {
        "risk": risk,
        "category": category if risk >= 50 else None,
        "category_label": CATEGORY_LABELS[category] if risk >= 50 else None,
        "warning": risk >= WARNING_THRESHOLD,
        "analyzed_domain": reg,
    }
