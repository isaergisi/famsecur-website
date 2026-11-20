"""Koruma iş kuralları: alan adı kontrolü, olay kaydı ve saklama süresi."""

from dataclasses import replace
from datetime import timedelta

from django.utils import timezone

from .classifier import (
    CATEGORY_LABELS,
    Decision,
    analyze_domain,
    domain_suffixes,
    matches_any,
    official_gambling_domains,
)
from .ml_risk import predict_risk
from .models import MANUAL_CATEGORY, BlockEvent, Device, Family, ThreatSource

# Yapay zekâ ile otomatik engel yalnızca bu puanın üzerindeki tahminlerde uygulanır. Uyarı eşiğinden (60)
# bilinçli olarak yüksektir: model sitenin içeriğini görmez ve yanlış engel, eksik uyarıdan daha rahatsız edicidir.
AI_BLOCK_THRESHOLD = 85

BLOCK_MESSAGES = {
    "silent": "İstek sessizce engellendi. Site cihazda açılmaz, bağlantı hatası görünür.",
    "warning": "Cihaz FamSecur uyarı sayfasına yönlendirildi. Uyarı sayfası yalnızca şifresiz (HTTP) sitelerde görünür; "
               "HTTPS sitelerde tarayıcı bağlantı hatası gösterir.",
}
OBSERVED_MESSAGE = (
    "Riskli bir siteye girildi ve panelinize kaydedildi. Başlangıç paketinde otomatik engel yoktur; "
    "bu siteyi engellemek için engel listenize ekleyebilirsiniz."
)


def manual_block_match(family: Family, domain: str) -> str | None:
    """Alan adı ailenin engel listesindeyse eşleşen kaydı döner (alt alan adları dâhil)."""
    entries = set(family.blocklist.values_list("domain", flat=True))
    return next((suffix for suffix in domain_suffixes(domain) if suffix in entries), None)


def decide_for_family(family: Family, domain: str) -> Decision:
    policy = family.policy
    return analyze_domain(
        domain,
        enabled_categories=policy.enabled_categories,
        threshold=policy.risk_threshold,
        whitelist=list(family.whitelist.values_list("domain", flat=True)),
        blocked_domains=ThreatSource.active_domain_map(),
    )


def is_in_known_list(family: Family | None, domain: str) -> bool:
    """Alan adı beyaz listede (aile verilmişse), tehdit kaynaklarında veya resmî havuzda mı?"""
    if family is not None and matches_any(domain, family.whitelist.values_list("domain", flat=True)):
        return True
    if any(suffix in ThreatSource.active_domain_map() for suffix in domain_suffixes(domain)):
        return True
    return matches_any(domain, official_gambling_domains())


def ai_prediction(family: Family | None, decision: Decision) -> dict | None:
    """Hiçbir listede olmayan alan adları için yapay zekâ risk tahmini.

    Listede olan alan adının sonucu zaten kesindir; model yalnızca bilinmeyen
    alan adları için ek bir uyarı üretir ve kararı değiştirmez.
    """
    if not decision.domain or "." not in decision.domain or is_in_known_list(family, decision.domain):
        return None
    return predict_risk(decision.domain)


def check_domain(family: Family, domain: str, device: Device | None = None) -> dict:
    """Bir DNS sorgusunu aile politikasına ve paketine göre değerlendirir.

    Öncelik: beyaz liste → ailenin engel listesi → otomatik koruma (listeler, sinyaller, isteğe bağlı yapay zekâ).
    Paket kuralları:
      - Başlangıç: yalnızca engel listesi uygulanır; riskli siteler engellenmez, cihaz bilgisi olmadan kaydedilir.
      - Ebeveyn ve Aile Plus: otomatik ve elle engel; olaylar cihaz bilgisiyle kaydedilir.
    Riskli bulunmayan istekler olay günlüğüne yazılmaz.
    """
    if device is not None and not device.is_protected:
        decision = Decision(domain.strip().lower(), "allow", None, None, 0, ["bu cihazda koruma kapalı"], "device_off")
        return {"decision": decision.to_dict(), "event": None, "ai": None, "message": "Cihaz korumada olmadığı için istek iletildi."}

    policy = family.policy
    decision = decide_for_family(family, domain)
    ai = ai_prediction(family, decision)
    manual = manual_block_match(family, decision.domain) if decision.source != "whitelist" else None
    if manual:
        decision = Decision(
            decision.domain, "block", MANUAL_CATEGORY, "Engel listeniz", 100,
            [f"engel listenize eklediğiniz bir site ({manual})"], "manual_list",
        )
    elif (
        decision.action == "allow" and family.auto_blocks and policy.ai_auto_block and ai
        and ai["risk"] >= AI_BLOCK_THRESHOLD and ai["category"] in policy.enabled_categories
    ):
        decision = Decision(
            decision.domain, "block", ai["category"], CATEGORY_LABELS[ai["category"]], ai["risk"],
            decision.reasons + [f"yapay zekâ risk tahmini çok yüksek (%{ai['risk']}); otomatik engel ayarınız açık"],
            "ai",
        )

    event = None
    message = "İstek güvenli bulundu ve iletildi. İzin verilen istekler olay günlüğüne yazılmaz."
    if decision.action == "block":
        action = BlockEvent.Action.BLOCKED
        if not family.auto_blocks and decision.source != "manual_list":
            # Başlangıç paketi: otomatik engel yok, riskli istek yalnızca kaydedilir.
            decision = replace(decision, action="allow", reasons=decision.reasons + [
                "Başlangıç paketinde otomatik engel yok; site engellenmedi, yalnızca kaydedildi",
            ])
            action = BlockEvent.Action.OBSERVED
        mode = policy.enforcement_mode
        event = BlockEvent.objects.create(
            family=family,
            device=device if family.shows_devices else None,
            domain=decision.domain,
            category=decision.category,
            action=action,
            score=decision.score,
            reasons=decision.reasons,
            enforcement_mode=mode,
        )
        message = OBSERVED_MESSAGE if action == BlockEvent.Action.OBSERVED else BLOCK_MESSAGES[mode]
        prune_events(family)
    return {"decision": decision.to_dict(), "event": event, "ai": ai, "message": message}


def prune_events(family: Family) -> int:
    cutoff = timezone.now() - timedelta(days=family.policy.retention_days)
    deleted, _ = family.events.filter(created_at__lt=cutoff).delete()
    return deleted
