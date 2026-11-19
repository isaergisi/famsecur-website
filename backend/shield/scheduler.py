"""Günlük bakım görevleri: tehdit listelerini yenileme ve süresi dolan engel olaylarını silme.

Sunucu çalışırken arka planda bir iş parçacığı saatte bir uyanır:
- "Adresten otomatik güncelle" işaretli her aktif kaynak, son başarılı
  güncellemesinin üzerinden 24 saat geçtiyse yenilenir. Başarısız olursa eski
  liste korunur ve 6 saat sonra yeniden denenir.
- Her ailenin saklama süresi dolan engel olayları silinir.

Yöneticinin "Şimdi güncelle" düğmesi ve ``python manage.py refresh_sources``
komutu bu zamanlamadan bağımsız olarak her zaman çalışır.

Açma/kapama: ``runserver`` ile kendiliğinden başlar. Başka bir sunucuda
(gunicorn vb.) ``FAMSECUR_AUTO_UPDATE=1``, tamamen kapatmak için
``FAMSECUR_AUTO_UPDATE=0`` ortam değişkeni kullanılır.
"""

import logging
import os
import sys
import threading
import time
from datetime import timedelta

from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)

REFRESH_EVERY = timedelta(hours=24)
RETRY_AFTER_FAILURE = timedelta(hours=6)
WAKE_SECONDS = 3600
FIRST_RUN_DELAY_SECONDS = 60

_failed_at: dict[int, object] = {}
_started = False


def refresh_due_sources(now=None) -> list[str]:
    """Güncelleme zamanı gelen kaynakları yeniler; yenilenen kaynak adlarını döndürür."""
    from .fetchers import refresh_source
    from .models import ThreatSource

    now = now or timezone.now()
    refreshed = []
    for source in ThreatSource.objects.filter(is_active=True, auto_update=True):
        if source.last_fetched_at and now - source.last_fetched_at < REFRESH_EVERY:
            continue
        failed_at = _failed_at.get(source.id)
        if failed_at and now - failed_at < RETRY_AFTER_FAILURE:
            continue
        try:
            refresh_source(source)
            _failed_at.pop(source.id, None)
            refreshed.append(source.name)
        except Exception:  # eski liste korunur, hata kaynağa yazılmıştır
            _failed_at[source.id] = now
            logger.warning("Otomatik güncelleme başarısız: %s", source.name)
    return refreshed


def prune_all_families() -> int:
    """Tüm ailelerde saklama süresi dolan engel olaylarını siler."""
    from .models import Family
    from .services import prune_events

    return sum(prune_events(family) for family in Family.objects.select_related("policy"))


def run_daily_tasks() -> None:
    close_old_connections()
    try:
        refresh_due_sources()
        prune_all_families()
    except Exception:
        logger.exception("Günlük bakım görevi çalışmadı")
    finally:
        close_old_connections()


def _loop() -> None:
    time.sleep(FIRST_RUN_DELAY_SECONDS)
    while True:
        run_daily_tasks()
        time.sleep(WAKE_SECONDS)


def should_start() -> bool:
    flag = os.environ.get("FAMSECUR_AUTO_UPDATE", "")
    if flag == "0":
        return False
    if flag == "1":
        return True
    # runserver otomatik yeniden yüklemede iki süreç açar; yalnızca asıl sunucu sürecinde başlat.
    return len(sys.argv) > 1 and sys.argv[1] == "runserver" and os.environ.get("RUN_MAIN") == "true"


def start() -> None:
    global _started
    if _started or not should_start():
        return
    _started = True
    threading.Thread(target=_loop, name="famsecur-gunluk-bakim", daemon=True).start()
