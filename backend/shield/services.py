"""Koruma iş kuralları: alan adı kontrolü, olay kaydı ve saklama süresi."""

from datetime import timedelta

from django.utils import timezone

from .classifier import Decision, analyze_domain, domain_suffixes, matches_any, official_gambling_domains
from .ml_risk import predict_risk
from .models import BlockEvent, Device, Family, ThreatSource

BLOCK_MESSAGES = {
    "silent": "İstek sessizce engellendi. Site cihazda açılmaz, bağlantı hatası görünür.",
    "warning": "Cihaz FamSecur uyarı sayfasına yönlendirildi. Uyarı sayfası yalnızca şifresiz (HTTP) sitelerde görünür; "
               "HTTPS sitelerde tarayıcı bağlantı hatası gösterir.",
}


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
    """Bir DNS sorgusunu aile politikasına göre değerlendirir.

    Engellenen istekler olay günlüğüne yazılır; izin verilenler hiçbir yerde
    saklanmaz (FamSecur gizlilik ilkesi).
    """
    if device is not None and not device.is_protected:
        decision = Decision(domain.strip().lower(), "allow", None, None, 0, ["bu cihazda koruma kapalı"])
        return {"decision": decision.to_dict(), "event": None, "ai": None, "message": "Cihaz korumada olmadığı için istek iletildi."}

    decision = decide_for_family(family, domain)
    event = None
    message = "İstek güvenli bulundu ve iletildi. İzin verilen istekler kaydedilmez."
    if decision.action == "block":
        mode = family.policy.enforcement_mode
        event = BlockEvent.objects.create(
            family=family,
            device=device,
            domain=decision.domain,
            category=decision.category,
            score=decision.score,
            reasons=decision.reasons,
            enforcement_mode=mode,
        )
        message = BLOCK_MESSAGES[mode]
        prune_events(family)
    return {"decision": decision.to_dict(), "event": event, "ai": ai_prediction(family, decision), "message": message}


def prune_events(family: Family) -> int:
    cutoff = timezone.now() - timedelta(days=family.policy.retention_days)
    deleted, _ = family.events.filter(created_at__lt=cutoff).delete()
    return deleted
