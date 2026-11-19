"""Otomatik güncellenen tehdit kaynaklarını adreslerinden yeniler: python manage.py refresh_sources

"Adresten otomatik güncelle" işaretli ve aktif tüm kaynaklar için kaynak
adresinden alan adlarını çeker. Bir kaynak başarısız olursa onun eski listesi
korunur, diğerleri güncellenmeye devam eder. Düzenli çalıştırmak için Windows
Görev Zamanlayıcı'ya veya cron'a eklenebilir.
"""

from django.core.management.base import BaseCommand

from shield.fetchers import refresh_source
from shield.models import ThreatSource


class Command(BaseCommand):
    help = "Otomatik güncellenen tehdit kaynaklarını kaynak adreslerinden yeniler."

    def add_arguments(self, parser):
        parser.add_argument("--timeout", type=int, default=60, help="İstek başına zaman aşımı, saniye")

    def handle(self, *args, timeout, **options):
        sources = ThreatSource.objects.filter(is_active=True, auto_update=True)
        if not sources:
            self.stdout.write("Otomatik güncellenecek aktif kaynak yok.")
            return
        failed = 0
        for source in sources:
            try:
                count = refresh_source(source, timeout=timeout)
                self.stdout.write(self.style.SUCCESS(f"✓ {source.name}: {count} alan adı alındı"))
            except Exception as exc:
                failed += 1
                self.stdout.write(self.style.ERROR(f"✗ {source.name}: güncellenemedi, eski liste korundu ({exc})"))
        if failed:
            self.stdout.write(self.style.WARNING(f"{failed} kaynak güncellenemedi."))
