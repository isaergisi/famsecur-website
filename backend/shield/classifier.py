"""FamSecur açıklanabilir alan adı karar motoru.

Ana FamSecur deposundaki (isaergisi/FamSecur) DNS karar motorunun web API'ye
uyarlanmış sürümüdür. Her karar; kategori, 0-100 risk puanı ve okunabilir
gerekçelerle birlikte döner. Böylece ebeveyn bir engelin nedenini görebilir ve
yanlış kararları beyaz listeyle düzeltebilir.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

CATEGORY_LABELS = {
    "gambling": "Kumar / bahis",
    "adult": "Yetişkin içerik",
    "drugs": "Uyuşturucu",
    "phishing": "Dolandırıcılık / phishing",
    "malware": "Kötü amaçlı yazılım",
}

# Kumar kategorisi, ebeveynin talebiyle yüksek yakalama modunda çalışır. Bu
# havuz genel terimleri, oyun türlerini, bahis terimlerini ve kamuya açık
# listelerde gözlenen yaygın marka parçalarını içerir.
GAMBLING_SIGNALS = (
    # Türkçe bahis ve şans oyunu terimleri
    "bahis", "bahse", "bahsin", "bahisci", "iddaa", "iddaa", "kupon", "oran",
    "canlibahis", "canlioran", "tahmin", "tuttur", "toto", "piyango", "tombala",
    "kazikazan", "sans", "talih", "rulet", "kumar", "kasino",
    # İngilizce genel bahis terimleri
    "bet", "betting", "bettor", "bookmaker", "bookie", "sportsbook", "sportbook",
    "wager", "wagering", "odds", "parlay", "propbet", "tipster", "gamble",
    "gambling", "igaming", "casino", "casin", "livecasino",
    # Casino oyunları ve sağlayıcı terimleri
    "slot", "slots", "freespin", "spin", "megaways", "poker", "holdem",
    "blackjack", "baccarat", "roulette", "craps", "bingo", "keno", "lottery",
    "jackpot", "sweepstake", "raffle", "pragmatic", "evolution", "netent",
    "microgaming", "playtech", "betsoft", "pushgaming", "nolimit",
    # Yüksek yakalama için istenen kazanım / promosyon kelimeleri
    "win", "winner", "winning", "lucky", "fortune", "prize", "bonus", "cash",
    # Kamuya açık listelerde görülen yaygın bahis marka/ad parçaları
    "matbet", "rexbet", "mobilbahis", "ngsbahis", "oddsring", "hiperbet",
    "casinodunya", "betsat", "betebet", "betboo", "betbaba", "baymavi",
    "bahsegel", "bahisnow", "artemisbet", "melbet", "wsbetting", "vogbet",
    "bahigo", "betpas", "bahsine", "bahsegir", "betist", "bahisarena",
    "vikabet", "wonnodds", "wettenbet", "truvabet", "tipbet", "tempobet",
    "sekabet", "adiosbet", "xbet", "vdcasino", "parasino", "bet365",
    "betano", "betfair", "betway", "betwinner",
)

# Tek başına güçlü yetişkin içerik göstergesi olan terimler ve özellikle talep
# edilen yaygın Türkçe alan adı/marka parçaları doğrudan eşik üstüne çıkar.
ADULT_HIGH_CONFIDENCE_SIGNALS = (
    "porn", "porno", "xxx", "adult", "sexcam", "erotic", "erotik", "nude",
    "naked", "hentai", "camgirl", "fetish", "bdsm", "nsfw", "gangbang",
    "masturb", "orgasm", "hardcore", "striptease", "blowjob", "sakso",
    "seks", "bosal", "azgin", "azmak", "milf", "sikis", "sikmek",
    "7dk", "doeda", "badtv", "yetiskin", "cinsel",
)

# Bu parçalar masum adlarda da görülebilir. Tek başına 35 puan üretir; ikinci
# bir yetişkin sinyaliyle birlikte engel eşiğine ulaşır veya doğrulanmış domain
# beslemesindeki kayıt üzerinden 100 puan alır.
ADULT_AMBIGUOUS_SIGNALS = (
    "sex", "teen", "31", "arzu", "webcam", "escort", "mature", "swinger",
)
ADULT_SIGNALS = ADULT_HIGH_CONFIDENCE_SIGNALS + ADULT_AMBIGUOUS_SIGNALS

# Açıklanabilir ilk katman: diğer kategorilerde yanlış pozitif riski daha
# düşük puanlamayla denetlenir.
SIGNALS: dict[str, tuple[str, ...]] = {
    "gambling": GAMBLING_SIGNALS,
    "adult": ADULT_SIGNALS,
    "drugs": ("cocaine", "cannabis-shop", "weed-shop", "buy-mdma", "buy-lsd"),
    "phishing": ("verify-wallet", "wallet-verify", "account-verify", "login-secure", "gift-card"),
    "malware": ("crack-download", "keygen", "free-ransomware", "malware-download"),
}
RISKY_TLDS = {"zip", "mov", "top", "xyz", "click", "gq", "work"}

OFFICIAL_GAMBLING_FEED = Path(__file__).with_name("feeds") / "poland_official_gambling_domains_20260723.txt"
ALL_CATEGORIES = tuple(CATEGORY_LABELS)


@lru_cache(maxsize=1)
def official_gambling_domains() -> frozenset[str]:
    """Sürümlenmiş resmî kumar alan adı havuzunu bir kez belleğe alır."""
    try:
        return frozenset(
            line.strip().lower()
            for line in OFFICIAL_GAMBLING_FEED.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        )
    except OSError:
        # Besleme dosyası yoksa sözcüksel sinyal katmanı çalışmaya devam eder.
        return frozenset()


def normalize_domain(value: str) -> str:
    """Kullanıcı girdisini (URL veya alan adı) yalın, küçük harfli alan adına çevirir."""
    value = (value or "").strip().lower()
    if "://" in value:
        value = urlparse(value).hostname or ""
    else:
        value = value.split("/", 1)[0].split(":", 1)[0]
    return value.rstrip(".")


def domain_suffixes(domain: str) -> list[str]:
    """``a.b.example.com`` için ``[a.b.example.com, b.example.com, example.com, com]``."""
    parts = domain.split(".")
    return [".".join(parts[i:]) for i in range(len(parts))]


def matches_any(domain: str, entries) -> bool:
    """Tam alan adı veya alt alan adı eşleşmesi (benzer adları yanlışlıkla eşleştirmez)."""
    entries = set(entries)
    return any(suffix in entries for suffix in domain_suffixes(domain))


@dataclass(frozen=True)
class Decision:
    domain: str
    action: str
    category: str | None
    category_label: str | None
    score: int
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _signal_score(label: str, word: str) -> tuple[int, str]:
    """Bir alan adı parçası ile sinyal kelimesi eşleşmesinin puanı ve gerekçesi."""
    if label.count(word) >= 2:
        return 80, f"tekrarlanan risk sinyali ({word} × {label.count(word)})"
    if label == word:
        return 75, word
    if label.startswith(word):
        suffix = label[len(word):]
        if suffix.isalnum() and any(char.isdigit() for char in suffix):
            return 75, f"{word} + sayısal varyasyon ({label})"
    if label.endswith(word):
        prefix = label[: -len(word)]
        if prefix.isalnum() and any(char.isdigit() for char in prefix):
            return 75, f"{word} + sayısal varyasyon ({label})"
    return 35, word


def analyze_domain(
    value: str,
    enabled_categories: list[str] | tuple[str, ...] = ALL_CATEGORIES,
    threshold: int = 70,
    whitelist: list[str] | tuple[str, ...] = (),
    blocked_domains: dict[str, str] | None = None,
) -> Decision:
    """Bir alan adı için izin/engel kararı üretir.

    ``blocked_domains``: yöneticinin tehdit kaynaklarına eklediği ek alan adları
    (alan adı -> kategori).
    """
    domain = normalize_domain(value)
    if not domain or "." not in domain:
        return Decision(domain, "allow", None, None, 0, ["Geçerli bir alan adı çözümlenemedi"])
    if whitelist and matches_any(domain, whitelist):
        return Decision(domain, "allow", None, None, 0, ["Beyaz listede izinli"])

    if blocked_domains:
        for suffix in domain_suffixes(domain):
            category = blocked_domains.get(suffix)
            if category and category in enabled_categories:
                return Decision(
                    domain, "block", category, CATEGORY_LABELS[category], 100,
                    [f"tehdit istihbaratı kaynağında kayıtlı ({suffix})"],
                )

    if "gambling" in enabled_categories and matches_any(domain, official_gambling_domains()):
        return Decision(
            domain, "block", "gambling", CATEGORY_LABELS["gambling"], 100,
            ["resmî kumar alan adı havuzunda kayıtlı"],
        )

    labels = domain.replace("-", ".").replace("_", ".").split(".")
    scores: dict[str, int] = {category: 0 for category in SIGNALS}
    matches: dict[str, list[str]] = {category: [] for category in SIGNALS}
    for category, words in SIGNALS.items():
        for word in dict.fromkeys(words):
            if word not in domain:
                continue
            matching_label = next((label for label in labels if word in label), "")
            if category == "gambling":
                # Yüksek yakalama politikası: kumar sözlüğündeki her eşleşme
                # doğrudan engel eşiğini aşar ("better" gibi yanlış pozitifler
                # beyaz listeyle düzeltilir).
                score, reason = 75, f"kumar anahtar kelimesi ({word})"
            elif category == "adult" and word in ADULT_HIGH_CONFIDENCE_SIGNALS:
                score, reason = 75, f"yüksek güvenli yetişkin içerik sinyali ({word})"
            elif category == "adult":
                score, reason = 35, f"belirsiz yetişkin içerik sinyali ({word})"
            else:
                score, reason = _signal_score(matching_label, word)
            scores[category] += score
            matches[category].append(reason)

    tld = domain.rsplit(".", 1)[-1]
    if tld in RISKY_TLDS:
        for category in scores:
            if scores[category]:
                scores[category] += 12
                matches[category].append(f".{tld} yüksek riskli TLD")
    if len(domain) > 55 or domain.count("-") >= 4:
        for category in scores:
            if scores[category]:
                scores[category] += 8
                matches[category].append("olağandışı alan adı biçimi")

    category = max(scores, key=scores.get)
    score = min(scores[category], 100)
    if not score:
        return Decision(domain, "allow", None, None, 0, ["Zararlı sinyal bulunamadı"])
    action = "block" if score >= threshold and category in enabled_categories else "allow"
    reasons = matches[category]
    if action == "allow" and category not in enabled_categories:
        reasons = reasons + ["kategori bu politikada kapalı"]
    elif action == "allow":
        reasons = reasons + [f"puan eşiğin altında ({score} < {threshold})"]
    return Decision(domain, action, category, CATEGORY_LABELS[category], score, reasons)
