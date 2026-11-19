"""Tehdit kaynaklarını kaynak adresinden (source_url) otomatik günceller.

Desteklenen adresler:
- USOM / Siber Güvenlik Başkanlığı (usom.gov.tr, siberguvenlik.gov.tr): resmî
  API'den kaynağın kategorisine uyan kayıtlar alınır, eski kayıtlara eklenir.
- Diğer her adres: düz metin liste (satır başına bir alan adı, hosts dosyası
  biçimi veya URL) ya da XML sicil (ör. Polonya Maliye Bakanlığı kumar sicili,
  <AdresDomeny> etiketleri). Gelen liste eskisinin yerine geçer.

Çekme başarısız olursa eski liste olduğu gibi korunur, hata kaynağa yazılır.
"""

import io
import json
import re
import socket
import ssl
import tarfile
import time
from datetime import timedelta
from urllib.parse import urlencode, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.utils import timezone

from .classifier import OFFICIAL_SOURCE_NAME, normalize_domain

USOM_API = "https://siberguvenlik.gov.tr/api/address/index"
USOM_HOSTS = {"usom.gov.tr", "www.usom.gov.tr", "siberguvenlik.gov.tr", "www.siberguvenlik.gov.tr"}
USOM_CODES = {"phishing": {"PH", "BP"}, "malware": {"MD", "MU", "MC"}}
DOMAIN_RE = re.compile(r"^(?=.{4,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
# UT1 (Toulouse Capitole Üniversitesi) kara listeleri: kategori başına tar.gz, içinde "<kategori>/domains".
# Yetişkin listesi milyonlarca kayıt içerdiği için alınmaz; yetişkin içerik sinyal ve yapay zeka katmanıyla yakalanır.
UT1_HOSTS = {"dsi.ut-capitole.fr", "dsi.univ-tlse1.fr"}
UT1_DOWNLOAD = "https://dsi.ut-capitole.fr/blacklists/download/{name}.tar.gz"
UT1_CATEGORIES = {"gambling": "gambling", "drogue": "drugs", "phishing": "phishing", "malware": "malware"}
XML_DOMAIN_RE = re.compile(r"<AdresDomeny>\s*([^<\s]+)\s*</AdresDomeny>", re.IGNORECASE)
MAX_BYTES = 50 * 1024 * 1024
# Resmî kumar sicili ~60.000 kayıtlık büyük bir XML; yavaş yanıt verebilir.
DEFAULT_TIMEOUT = 180
RETRY_DELAY = 5


def hostname(address: str) -> str:
    address = address.strip()
    parsed = urlparse(address if "://" in address else "//" + address)
    return normalize_domain(parsed.hostname or "")


def _ssl_context():
    # Windows'ta Python'un sertifika deposu eksik olabildiğinden varsa certifi paketi kullanılır.
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _download(url: str, timeout: int) -> bytes:
    request = Request(url, headers={"User-Agent": "FamSecur/1.0", "Accept": "*/*"})
    with urlopen(request, timeout=timeout, context=_ssl_context()) as response:
        return response.read(MAX_BYTES)


def _get(url: str, timeout: int) -> bytes:
    """İndirir; zaman aşımı veya bağlantı hatasında bir kez daha dener (HTTP hata kodlarında denemez)."""
    try:
        return _download(url, timeout)
    except HTTPError:
        raise
    except (URLError, TimeoutError, socket.timeout, ConnectionError):
        time.sleep(RETRY_DELAY)
        return _download(url, timeout)


def fetch_usom(category: str, days: int = 30, max_criticality: int = 4, timeout: int = DEFAULT_TIMEOUT) -> set[str]:
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


def fetch_ut1(timeout: int = DEFAULT_TIMEOUT) -> dict[str, str]:
    """UT1 listelerini indirir; alan adı → FamSecur kategorisi döndürür."""
    found: dict[str, str] = {}
    for name, category in UT1_CATEGORIES.items():
        data = _get(UT1_DOWNLOAD.format(name=name), timeout)
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            member = next((m for m in archive.getmembers() if m.isfile() and m.name.endswith("/domains")), None)
            if member is None:
                raise ValueError(f"UT1 '{name}' arşivinde domains dosyası yok.")
            text = archive.extractfile(member).read().decode("utf-8", errors="replace")
        for domain in parse_list(text):
            found.setdefault(domain, category)
    return found


def explain_error(exc: Exception) -> str:
    """Hatayı panelde gösterilecek anlaşılır Türkçe bir cümleye çevirir (teknik ayrıntı parantez içinde)."""
    reason = getattr(exc, "reason", exc)
    if isinstance(exc, HTTPError):
        text = f"Sunucu isteği reddetti (HTTP {exc.code})."
    elif isinstance(reason, ssl.SSLCertVerificationError) or isinstance(exc, ssl.SSLError):
        text = "Sitenin SSL sertifikası doğrulanamadı. Python'un sertifika deposu eksik olabilir: pip install -r requirements.txt"
    elif isinstance(reason, (socket.timeout, TimeoutError)) or isinstance(exc, (socket.timeout, TimeoutError)):
        text = "Sunucu zamanında yanıt vermedi (iki deneme de zaman aşımına uğradı). Biraz sonra tekrar deneyin."
    elif isinstance(exc, URLError):
        text = "Sunucuya bağlanılamadı (internet bağlantısı, güvenlik duvarı veya site erişilemez)."
    elif isinstance(exc, ValueError):
        return str(exc)
    else:
        text = "Beklenmeyen hata."
    return f"{text} ({type(exc).__name__}: {reason})"[:500]


def refresh_source(source, timeout: int = DEFAULT_TIMEOUT) -> int:
    """Kaynağı adresinden günceller; gelen alan adı sayısını döndürür. Hata olursa eski liste korunur."""
    try:
        if not source.source_url:
            raise ValueError("Kaynak adresi (URL) girilmemiş.")
        if urlparse(source.source_url).hostname in UT1_HOSTS:
            # Kayıt bazlı kategori: "alan-adi.com gambling"
            entries = fetch_ut1(timeout=timeout)
            if not entries:
                raise ValueError("UT1 listelerinden alan adı gelmedi; liste değiştirilmedi.")
            fetched = set(entries)
            lines = [f"{domain} {category}" for domain, category in sorted(entries.items())]
        elif urlparse(source.source_url).hostname in USOM_HOSTS:
            fetched = fetch_usom(source.category, timeout=timeout)
            existing = source.domains.splitlines()
            known = {line.split()[0].lower() for line in existing if line.strip()}
            lines = [line for line in existing if line.strip()] + sorted(fetched - known)
        else:
            url = source.source_url
            parsed = urlparse(url)
            if parsed.hostname in ("hazard.mf.gov.pl", "www.hazard.mf.gov.pl") and parsed.path in ("", "/"):
                # Sitenin ana sayfası verilmişse sicilin indirme adresi kullanılır.
                url = "https://hazard.mf.gov.pl/api/Register"
            text = _get(url, timeout).decode("utf-8", errors="replace")
            if text.lstrip()[:200].lower().startswith(("<!doctype html", "<html")):
                raise ValueError(
                    "Adres bir web sayfası döndürdü, alan adı listesi değil. Kaynak adresine listenin kendisini "
                    "yazın (resmî kumar havuzu için: https://hazard.mf.gov.pl/api/Register)."
                )
            fetched = parse_list(text)
            if not fetched:
                raise ValueError("Adresten okunabilir alan adı gelmedi; liste değiştirilmedi.")
            lines = sorted(fetched)
    except Exception as exc:  # ağ, zaman aşımı, biçim hatası: eski liste kalır
        source.last_fetch_error = explain_error(exc)
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
