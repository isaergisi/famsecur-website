"""Tehdit kaynaklarını kaynak adresinden (source_url) otomatik günceller.

Desteklenen adresler:
- USOM / Siber Güvenlik Başkanlığı (usom.gov.tr, siberguvenlik.gov.tr): resmî
  API'den kaynağın kategorisine uyan kayıtlar alınır, eski kayıtlara eklenir.
- Diğer her adres: düz metin liste (satır başına bir alan adı, hosts dosyası
  biçimi veya URL) ya da XML sicil (ör. Polonya Maliye Bakanlığı kumar sicili,
  <AdresDomeny> etiketleri). Gelen liste eskisinin yerine geçer.

Çekme başarısız olursa eski liste olduğu gibi korunur, hata kaynağa yazılır.
"""

import json
import re
from datetime import timedelta
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from django.utils import timezone

from .classifier import OFFICIAL_SOURCE_NAME, normalize_domain

USOM_API = "https://siberguvenlik.gov.tr/api/address/index"
USOM_HOSTS = {"usom.gov.tr", "www.usom.gov.tr", "siberguvenlik.gov.tr", "www.siberguvenlik.gov.tr"}
USOM_CODES = {"phishing": {"PH", "BP"}, "malware": {"MD", "MU", "MC"}}
DOMAIN_RE = re.compile(r"^(?=.{4,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
XML_DOMAIN_RE = re.compile(r"<AdresDomeny>\s*([^<\s]+)\s*</AdresDomeny>", re.IGNORECASE)
MAX_BYTES = 50 * 1024 * 1024


def hostname(address: str) -> str:
    address = address.strip()
    parsed = urlparse(address if "://" in address else "//" + address)
    return normalize_domain(parsed.hostname or "")


def _get(url: str, timeout: int) -> bytes:
    request = Request(url, headers={"User-Agent": "FamSecur/1.0", "Accept": "*/*"})
    with urlopen(request, timeout=timeout) as response:
        return response.read(MAX_BYTES)


def fetch_usom(category: str, days: int = 30, max_criticality: int = 4, timeout: int = 60) -> set[str]:
    """USOM API'sinden kategoriye uyan kayıtların alan adlarını sayfa sayfa okur."""
    codes = USOM_CODES.get(category)
    if not codes:
        raise ValueError("USOM yalnızca oltalama (phishing) ve zararlı yazılım (malware) kategorileri yayımlar.")
    since = (timezone.now() - timedelta(days=days)).date().isoformat()
    found = set()
    for address_type in ("domain", "url"):
        page = 1
        while True:
            query = urlencode({"type": address_type, "per-page": 9999, "page": page, "date_gte": since})
            payload = json.loads(_get(f"{USOM_API}?{query}", timeout).decode("utf-8"))
            for item in payload.get("models") or []:
                level = item.get("criticality_level")
                if str(item.get("desc", "")) not in codes or not isinstance(level, int) or level > max_criticality:
                    continue
                domain = hostname(str(item.get("url", "")))
                if DOMAIN_RE.match(domain):
                    found.add(domain)
            if page >= int(payload.get("pageCount") or 0):
                break
            page += 1
    return found


def parse_list(text: str) -> set[str]:
    """Düz metin, hosts dosyası veya XML sicilden alan adlarını çıkarır."""
    xml_domains = XML_DOMAIN_RE.findall(text)
    candidates = xml_domains or [
        line.split("#", 1)[0].split()[-1]
        for line in text.splitlines()
        if line.split("#", 1)[0].split() and not line.lstrip().startswith(("!", ";"))
    ]
    domains = set()
    for value in candidates:
        domain = hostname(value)
        if domain.startswith("*."):
            domain = domain[2:]
        if DOMAIN_RE.match(domain):
            domains.add(domain)
    return domains


def refresh_source(source, timeout: int = 60) -> int:
    """Kaynağı adresinden günceller; gelen alan adı sayısını döndürür. Hata olursa eski liste korunur."""
    try:
        if not source.source_url:
            raise ValueError("Kaynak adresi (URL) girilmemiş.")
        if urlparse(source.source_url).hostname in USOM_HOSTS:
            fetched = fetch_usom(source.category, timeout=timeout)
            existing = source.domains.splitlines()
            known = {line.split()[0].lower() for line in existing if line.strip()}
            lines = [line for line in existing if line.strip()] + sorted(fetched - known)
        else:
            fetched = parse_list(_get(source.source_url, timeout).decode("utf-8", errors="replace"))
            if not fetched:
                raise ValueError("Adresten okunabilir alan adı gelmedi; liste değiştirilmedi.")
            lines = sorted(fetched)
    except Exception as exc:  # ağ, zaman aşımı, biçim hatası: eski liste kalır
        source.last_fetch_error = f"{type(exc).__name__}: {exc}"[:500]
        source.save(update_fields=["last_fetch_error"])
        raise
    source.domains = "\n".join(lines)
    source.last_fetched_at = timezone.now()
    source.last_fetch_count = len(fetched)
    source.last_fetch_error = ""
    source.save(update_fields=["domains", "last_fetched_at", "last_fetch_count", "last_fetch_error", "updated_at"])
    return len(fetched)


def uses_file_feed(source) -> bool:
    """Resmî havuz kaynağı henüz adresinden güncellenmediyse alan adları sürümlenmiş dosyadan gelir."""
    return source.name == OFFICIAL_SOURCE_NAME and not source.domains.strip()
