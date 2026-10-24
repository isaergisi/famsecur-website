"""Koruma iş kuralları: alan adı kontrolü, olay kaydı ve saklama süresi."""

from datetime import timedelta

from django.utils import timezone

from .classifier import Decision, analyze_domain
from .models import BlockEvent, Device, Family, ThreatSource

BLOCK_MESSAGES = {
    "silent": "İstek sessizce engellendi (NXDOMAIN). Cihazda site açılmaz.",
    "warning": "Cihaz FamSecur uyarı sayfasına yönlendirildi ve engelin nedeni gösterildi.",
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


def check_domain(family: Family, domain: str, device: Device | None = None) -> dict:
    """Bir DNS sorgusunu aile politikasına göre değerlendirir.

    Engellenen istekler olay günlüğüne yazılır; izin verilenler hiçbir yerde
    saklanmaz (FamSecur gizlilik ilkesi).
    """
    if device is not None and not device.is_protected:
        decision = Decision(domain.strip().lower(), "allow", None, None, 0, ["Bu cihazda koruma kapalı"])
        return {"decision": decision.to_dict(), "event": None, "message": "Cihaz korumada olmadığı için istek iletildi."}

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
    return {"decision": decision.to_dict(), "event": event, "message": message}


def prune_events(family: Family) -> int:
    cutoff = timezone.now() - timedelta(days=family.policy.retention_days)
    deleted, _ = family.events.filter(created_at__lt=cutoff).delete()
    return deleted
