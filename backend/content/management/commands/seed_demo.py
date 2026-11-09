"""Demo verisi: python manage.py seed_demo

Bir yönetici, bir demo ebeveyn hesabı, cihazlar, beyaz liste, örnek engel
olayları, SSS ve tehdit kaynakları oluşturur. Tekrar çalıştırmak güvenlidir.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from content.models import FAQ
from shield.models import Device, Family, ThreatSource
from shield.services import check_domain

FAQS = [
    ("FamSecur çocuğumun mesajlarını veya geçmişini okuyor mu?",
     "Hayır. FamSecur yalnızca DNS katmanında, istenen alan adına bakarak karar verir. Mesajlar, ekran, "
     "arama ve izleme geçmişi toplanmaz. İzin verilen istekler hiçbir yerde kaydedilmez; yalnızca engellenen "
     "alan adları, kategori ve gerekçeyle birlikte panelinizde görünür."),
    ("Hangi içerikleri engelliyor?",
     "Kumar/bahis, yetişkin içerik, uyuşturucu, oltalama (phishing) ve kötü amaçlı yazılım. Oltalama ve zararlı "
     "yazılım verileri T.C. Siber Güvenlik Başkanlığı'nın USOM listesinden, kumar alan adları resmî bir alan adı "
     "havuzundan ve açıklanabilir alan adı sinyallerinden gelir."),
    ("Bir site yanlışlıkla engellenirse ne olur?",
     "Panelde her engelin nedenini görürsünüz. Yanlış engellenen siteyi tek tıkla beyaz listeye ekleyebilirsiniz; "
     "alt alan adları da otomatik olarak izinli olur."),
    ("Sessiz engel ile uyarı sayfası arasındaki fark nedir?",
     "Sessiz engelde site hiç açılmaz (NXDOMAIN). Uyarı modunda cihaz, engelin nedenini açıklayan FamSecur "
     "sayfasına yönlendirilir."),
    ("Kurulum için ne gerekiyor?",
     "FamSecur ev router'ınızda veya ağdaki küçük bir cihazda çalışır. Router'ın DNS ayarını FamSecur'a "
     "yönlendirmeniz yeterlidir; çocuğun cihazına uygulama yüklemeniz gerekmez."),
    ("Risk eşiği ne işe yarar?",
     "Her alan adı 0-100 arası bir risk puanı alır. Eşiği düşürdüğünüzde koruma sıkılaşır, yükselttiğinizde "
     "yalnızca çok net riskler engellenir. Varsayılan değer 70'tir."),
]

SOURCES = [
    {
        "name": "USOM Zararlı Bağlantılar",
        "category": "phishing",
        "description": "T.C. Siber Güvenlik Başkanlığı (USOM) tarafından yayımlanan oltalama bağlantıları. "
                       "Kritiklik seviyesi 1-4 arası kayıtlar engellenir.",
        "source_url": "https://www.usom.gov.tr/adres",
        "domains": "e-devlet-giris-dogrula.com\nptt-kargo-takip-odeme.net",
    },
    {
        "name": "USOM Zararlı Yazılım",
        "category": "malware",
        "description": "USOM listesindeki zararlı yazılım dağıtan alan adları.",
        "source_url": "https://www.usom.gov.tr/adres",
        "domains": "free-crack-indir.org",
    },
    {
        "name": "Resmî Kumar Alan Adı Havuzu",
        "category": "gambling",
        "description": "36.282 benzersiz alan adından oluşan sürümlenmiş resmî yasa dışı bahis listesi; "
                       "yalnızca tam alan adı ve alt alan adı eşleşmesiyle karar verir.",
        "source_url": "https://hazard.mf.gov.pl/",
        "domains": "",
    },
]


class Command(BaseCommand):
    help = "Demo kullanıcıları, cihazlar, olaylar, SSS ve tehdit kaynakları oluşturur."

    @transaction.atomic
    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            email="admin@famsecur.com",
            defaults={"first_name": "FamSecur", "last_name": "Yönetici", "role": User.Role.ADMIN, "is_staff": True},
        )
        if created:
            admin.set_password("Admin.12345")
            admin.save()

        parent, created = User.objects.get_or_create(
            email="ebeveyn@famsecur.com", defaults={"first_name": "Ayşe", "last_name": "Yılmaz"}
        )
        if created:
            parent.set_password("Ebeveyn.12345")
            parent.save()
            Family.create_with_defaults(owner=parent, name="Yılmaz Ailesi")

        for question, answer in FAQS:
            FAQ.objects.get_or_create(question=question, defaults={"answer": answer, "order": FAQS.index((question, answer))})
        for source in SOURCES:
            ThreatSource.objects.get_or_create(name=source["name"], defaults=source)

        family = parent.family
        if not family.devices.exists():
            tablet = Device.objects.create(family=family, name="Elif'in tableti", device_type="tablet", member_name="Elif")
            phone = Device.objects.create(family=family, name="Can'ın telefonu", device_type="phone", member_name="Can")
            Device.objects.create(family=family, name="Salon TV", device_type="tv", is_protected=False)
            family.whitelist.create(domain="betterhelp.com", note="Yanlış pozitif: sağlık sitesi")
            for device, domain in [
                (tablet, "casino777.xyz"), (phone, "bet2x.com"), (phone, "e-devlet-giris-dogrula.com"),
                (tablet, "free-crack-indir.org"), (phone, "canlibahis-tv.top"), (tablet, "eba.gov.tr"),
            ]:
                check_domain(family, domain, device)

        self.stdout.write(self.style.SUCCESS(
            "Demo verisi hazır.\n"
            "  Yönetici: admin@famsecur.com / Admin.12345\n"
            "  Ebeveyn : ebeveyn@famsecur.com / Ebeveyn.12345"
        ))
