"""Aile Plus günlük özeti.

Ev ajanı izin verilen sorguları ham hâliyle panele göndermez; her sorgu kayıtlı alan adına
(``i.instagram.com`` → ``instagram.com``) indirilir, arka plan adresleri (reklam, CDN, güncelleme,
telemetri) atlanır ve yalnızca gün + cihaz + site başına sayı tutulur. Bu sayılar 30 gün sonra silinir.

Özet yalnızca Aile Plus paketinde, açık rıza verilmiş ve geri alınmamışsa ve cihaz "günlük özete
dahil" ise oluşturulur.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from django.db.models import F, Sum
from django.utils import timezone

from ml.features import registered_domain

from .models import DailyDomainStat, Device, Family

SUMMARY_RETENTION_DAYS = 30
NIGHT_END_HOUR = 6  # 00.00-06.00 arası "gece" sayılır

# Sık görülen sitelerin okunur adı ve genel kategorisi. Listede olmayan siteler "Diğer" sayılır.
GENERAL_CATEGORIES = {
    "social": "Sosyal medya",
    "video": "Video ve dizi",
    "games": "Oyun",
    "education": "Eğitim",
    "search": "Arama ve araçlar",
    "news": "Haber",
    "shopping": "Alışveriş",
    "messaging": "Mesajlaşma",
    "music": "Müzik",
    "other": "Diğer",
}

KNOWN_SITES = {
    "instagram.com": ("Instagram", "social"),
    "tiktok.com": ("TikTok", "social"),
    "snapchat.com": ("Snapchat", "social"),
    "x.com": ("X (Twitter)", "social"),
    "twitter.com": ("X (Twitter)", "social"),
    "facebook.com": ("Facebook", "social"),
    "reddit.com": ("Reddit", "social"),
    "pinterest.com": ("Pinterest", "social"),
    "youtube.com": ("YouTube", "video"),
    "netflix.com": ("Netflix", "video"),
    "twitch.tv": ("Twitch", "video"),
    "disneyplus.com": ("Disney+", "video"),
    "exxen.com": ("Exxen", "video"),
    "blutv.com": ("BluTV", "video"),
    "roblox.com": ("Roblox", "games"),
    "minecraft.net": ("Minecraft", "games"),
    "epicgames.com": ("Epic Games", "games"),
    "steampowered.com": ("Steam", "games"),
    "brawlstars.com": ("Brawl Stars", "games"),
    "supercell.com": ("Supercell", "games"),
    "eba.gov.tr": ("EBA", "education"),
    "meb.gov.tr": ("MEB", "education"),
    "khanacademy.org": ("Khan Academy", "education"),
    "duolingo.com": ("Duolingo", "education"),
    "wikipedia.org": ("Vikipedi", "education"),
    "google.com": ("Google", "search"),
    "google.com.tr": ("Google", "search"),
    "bing.com": ("Bing", "search"),
    "chatgpt.com": ("ChatGPT", "search"),
    "hurriyet.com.tr": ("Hürriyet", "news"),
    "trthaber.com": ("TRT Haber", "news"),
    "trendyol.com": ("Trendyol", "shopping"),
    "hepsiburada.com": ("Hepsiburada", "shopping"),
    "whatsapp.com": ("WhatsApp", "messaging"),
    "whatsapp.net": ("WhatsApp", "messaging"),
    "discord.com": ("Discord", "messaging"),
    "telegram.org": ("Telegram", "messaging"),
    "spotify.com": ("Spotify", "music"),
}

# Cihazların arka planda kendiliğinden sorduğu adresler: kullanıcının girdiği bir site değildir.
BACKGROUND_DOMAINS = frozenset({
    "googleapis.com", "gstatic.com", "googleusercontent.com", "googlevideo.com", "ggpht.com",
    "doubleclick.net", "googlesyndication.com", "googleadservices.com", "google-analytics.com",
    "googletagmanager.com", "app-measurement.com", "crashlytics.com", "firebaseio.com",
    "apple.com", "icloud.com", "mzstatic.com", "apple-dns.net", "aaplimg.com", "cdn-apple.com",
    "microsoft.com", "windows.com", "windowsupdate.com", "live.com", "msftconnecttest.com", "msn.com",
    "akamaiedge.net", "akamaized.net", "akamai.net", "cloudfront.net", "cloudflare.com", "fastly.net",
    "amazonaws.com", "azureedge.net", "edgekey.net", "fbcdn.net", "cdninstagram.com", "tiktokcdn.com",
    "ytimg.com", "samsung.com", "samsungcloud.com", "xiaomi.com", "miui.com", "ntp.org",
    "use-application-dns.net",
})


def site_info(domain: str) -> tuple[str, str]:
    """Kayıtlı alan adı için (okunur ad, genel kategori anahtarı)."""
    label, category = KNOWN_SITES.get(domain, (domain, "other"))
    return label, category


def normalize_visit(domain: str) -> str | None:
    """Sorgulanan adı özete girecek kayıtlı alan adına çevirir; arka plan adresleri için ``None``."""
    reg = registered_domain(domain)
    if not reg or reg in BACKGROUND_DOMAINS:
        return None
    return reg


def record_visit(family: Family, domain: str, device: Device | None = None, at: datetime | None = None) -> bool:
    """Bir DNS sorgusunu günlük özete sayar. Özet kapsamı dışındaysa hiçbir şey yazmaz ve ``False`` döner."""
    if not family.daily_summary_enabled:
        return False
    if device is not None and not device.in_daily_summary:
        return False
    reg = normalize_visit(domain)
    if reg is None:
        return False
    at = timezone.localtime(at or timezone.now())
    stat, _ = DailyDomainStat.objects.get_or_create(family=family, device=device, day=at.date(), domain=reg)
    night = 1 if at.hour < NIGHT_END_HOUR else 0
    DailyDomainStat.objects.filter(pk=stat.pk).update(count=F("count") + 1, night_count=F("night_count") + night)
    return True


def prune_daily_stats(family: Family) -> int:
    cutoff = timezone.localdate() - timedelta(days=SUMMARY_RETENTION_DAYS)
    deleted, _ = family.daily_stats.filter(day__lt=cutoff).delete()
    return deleted


def build_summary(family: Family, day: date) -> dict:
    """Seçilen günün özeti: en çok girilen siteler, kategoriler, cihazlar, gece kullanımı ve yeni siteler."""
    prune_daily_stats(family)
    stats = family.daily_stats.filter(day=day)
    total = stats.aggregate(total=Sum("count"), night=Sum("night_count"))

    sites: dict[str, dict] = {}
    for row in stats.values("domain").annotate(count=Sum("count"), night=Sum("night_count")):
        label, category = site_info(row["domain"])
        sites[row["domain"]] = {
            "domain": row["domain"], "label": label, "category": category,
            "category_label": GENERAL_CATEGORIES[category], "count": row["count"], "night": row["night"],
        }
    top_sites = sorted(sites.values(), key=lambda s: -s["count"])[:15]

    categories: dict[str, int] = {}
    for site in sites.values():
        categories[site["category"]] = categories.get(site["category"], 0) + site["count"]
    by_category = [
        {"category": key, "label": GENERAL_CATEGORIES[key], "count": count}
        for key, count in sorted(categories.items(), key=lambda kv: -kv[1])
    ]

    by_device = [
        {"device": row["device__name"] or "Cihaz eşleşmedi", "count": row["count"], "night": row["night"]}
        for row in stats.values("device__name").annotate(count=Sum("count"), night=Sum("night_count")).order_by("-count")
    ]

    seen_before = set(
        family.daily_stats.filter(day__lt=day, day__gte=day - timedelta(days=SUMMARY_RETENTION_DAYS))
        .values_list("domain", flat=True)
    )
    has_history = family.daily_stats.filter(day__lt=day).exists()
    new_sites = [s for s in top_sites if s["domain"] not in seen_before] if has_history else []

    night_sites = sorted((s for s in sites.values() if s["night"]), key=lambda s: -s["night"])[:5]
    risky = family.events.filter(created_at__date=day).count()

    return {
        "day": day.isoformat(),
        "available_days": [d.isoformat() for d in family.daily_stats.values_list("day", flat=True).distinct().order_by("-day")],
        "total_queries": total["total"] or 0,
        "site_count": len(sites),
        "night_total": total["night"] or 0,
        "top_sites": top_sites,
        "by_category": by_category,
        "by_device": by_device,
        "night_sites": night_sites,
        "new_sites": new_sites[:10],
        "risky_events": risky,
        "retention_days": SUMMARY_RETENTION_DAYS,
    }
