"""USOM listelerini resmî API'den günceller: python manage.py update_usom

T.C. Siber Güvenlik Başkanlığı'nın (USOM) herkese açık zararlı bağlantılar
API'sinden kayıtları indirir ve "USOM Zararlı Bağlantılar" ile "USOM Zararlı
Yazılım" tehdit kaynaklarının alan adı listelerini doldurur. İnternet bağlantısı
gerekir; anahtar veya hesap gerekmez.

- USOM kodları PH ve BP → oltalama (phishing), MD, MU ve MC → zararlı yazılım.
- Kritiklik 1 (en yüksek) ile 10 arasındadır; varsayılan olarak 1-4 alınır.
- DNS yalnızca alan adını görebildiği için URL kayıtlarının yalnızca ana
  bilgisayar adı alınır.
- Var olan kayıtlar silinmez, yeniler eklenir. Tekrar çalıştırmak güvenlidir.
"""

import json
from datetime import timedelta
from urllib.error import URLError
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from shield.classifier import normalize_domain
from shield.models import ThreatSource

USOM_API = "https://siberguvenlik.gov.tr/api/address/index"
CATEGORY_BY_CODE = {"PH": "phishing", "BP": "phishing", "MD": "malware", "MU": "malware", "MC": "malware"}
SOURCES = {
    "phishing": {
        "name": "USOM Zararlı Bağlantılar",
        "description": "T.C. Siber Güvenlik Başkanlığı (USOM) tarafından yayımlanan oltalama bağlantıları. "
                       "Kritiklik seviyesi 1-4 arası kayıtlar engellenir.",
    },
    "malware": {
        "name": "USOM Zararlı Yazılım",
        "description": "USOM listesindeki zararlı yazılım dağıtan alan adları.",
    },
}


def hostname(address: str) -> str:
    address = address.strip()
    parsed = urlparse(address if "://" in address else "//" + address)
    return normalize_domain(parsed.hostname or "")


def fetch_usom(days: int, max_criticality: int, timeout: int) -> tuple[dict[str, set[str]], int]:
    """USOM API'sini sayfa sayfa okur; kategori → alan adları ve taranan kayıt sayısını döndürür."""
    since = (timezone.now() - timedelta(days=days)).date().isoformat()
    found = {"phishing": set(), "malware": set()}
    scanned = 0
    for address_type in ("domain", "url"):
        page = 1
        while True:
            query = urlencode({"type": address_type, "per-page": 9999, "page": page, "date_gte": since})
            with urlopen(f"{USOM_API}?{query}", timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            models = payload.get("models") or []
            scanned += len(models)
            for item in models:
                category = CATEGORY_BY_CODE.get(str(item.get("desc", "")))
                level = item.get("criticality_level")
                if category is None or not isinstance(level, int) or level > max_criticality:
                    continue
                domain = hostname(str(item.get("url", "")))
                if domain and "." in domain:
                    found[category].add(domain)
            if page >= int(payload.get("pageCount") or 0):
                break
            page += 1
    return found, scanned


class Command(BaseCommand):
    help = "USOM zararlı bağlantı ve zararlı yazılım listelerini resmî API'den indirip tehdit kaynaklarına yazar."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=30, help="Kaç günlük kayıt alınsın (varsayılan 30)")
        parser.add_argument("--max-criticality", type=int, default=4, help="1 en kritik, 10 en düşük (varsayılan 4)")
        parser.add_argument("--timeout", type=int, default=60, help="İstek başına zaman aşımı, saniye")

    def handle(self, *args, days, max_criticality, timeout, **options):
        if not 1 <= max_criticality <= 10:
            raise CommandError("--max-criticality 1 ile 10 arasında olmalı.")
        self.stdout.write(f"USOM API'sinden son {days} günün kayıtları indiriliyor…")
        try:
            found, scanned = fetch_usom(days, max_criticality, timeout)
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise CommandError(f"USOM API'sine ulaşılamadı: {exc}. İnternet bağlantınızı kontrol edip tekrar deneyin.")

        for category, domains in found.items():
            meta = SOURCES[category]
            source, _ = ThreatSource.objects.get_or_create(
                name=meta["name"],
                defaults={"category": category, "description": meta["description"], "source_url": "https://www.usom.gov.tr/adres"},
            )
            lines = dict.fromkeys(line for line in source.domains.splitlines() if line.strip())
            before = len(lines)
            lines.update(dict.fromkeys(sorted(domains)))
            source.domains = "\n".join(lines)
            source.save(update_fields=["domains", "updated_at"])
            self.stdout.write(f"  {meta['name']}: {len(lines) - before} yeni, toplam {len(lines)} alan adı")

        self.stdout.write(self.style.SUCCESS(f"USOM listeleri güncellendi ({scanned} kayıt tarandı)."))
