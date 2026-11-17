"""Eğitimde ve tahminde ortak kullanılan alan adı ön işleme adımları.

Model aynı alan adını eğitimde ve tahminde *aynı biçimde* görmelidir; bu yüzden
normalleştirme tek bir yerde tanımlanır.
"""

from __future__ import annotations

from functools import lru_cache

import tldextract

# suffix_list_urls=() → internetten Public Suffix List indirmez, paketle gelen
# anlık görüntüyü kullanır. Böylece sunucu çevrimdışı da çalışır.
_EXTRACT = tldextract.TLDExtract(suffix_list_urls=(), include_psl_private_domains=True)


@lru_cache(maxsize=4096)
def registered_domain(domain: str) -> str:
    """``www.m.ornekbahis.com`` → ``ornekbahis.com`` (kayıtlı alan adı).

    Alt alan adları (www, m, cdn …) çoğunlukla risk hakkında bilgi taşımaz ve
    eğitim verisindeki kaynaklar arasında farklı oranlarda bulunur. Hepsini
    kayıtlı alan adına indirmek, modelin "alt alan adı var mı" gibi yanıltıcı
    bir kısayol öğrenmesini önler.
    """
    domain = (domain or "").strip().lower().rstrip(".")
    parts = _EXTRACT(domain)
    if not parts.domain or not parts.suffix:
        return ""
    return f"{parts.domain}.{parts.suffix}"


def model_text(domain: str) -> str:
    """Modelin okuduğu metin: başlangıç/bitiş işaretli kayıtlı alan adı."""
    return f"^{domain}$"
