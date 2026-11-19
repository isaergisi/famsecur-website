"""Demo verisi: python manage.py seed_demo

Bir yönetici, bir demo ebeveyn hesabı, cihazlar, beyaz liste, örnek engel
olayları, SSS ve tehdit kaynakları oluşturur. Tekrar çalıştırmak güvenlidir.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from content.faq_data import FAQS
from content.models import FAQ
from shield.models import Device, Family, ThreatSource
from shield.services import check_domain

OFFICIAL_POOL_DESCRIPTION = (
    "Polonya Maliye Bakanlığı'nın resmî yasa dışı kumar sicili. Kaynak adresinden güncellenir; yalnızca tam alan "
    "adı ve alt alan adı eşleşmesiyle karar verir."
)

SOURCES = [
    {
        "name": "USOM Zararlı Bağlantılar",
        "category": "phishing",
        "description": "T.C. Siber Güvenlik Başkanlığı (USOM) tarafından yayımlanan oltalama bağlantıları. "
                       "Kritiklik seviyesi 1-4 arası kayıtlar engellenir.",
        "source_url": "https://www.usom.gov.tr/adres",
        "domains": "e-devlet-giris-dogrula.com\nptt-kargo-takip-odeme.net",
        "auto_update": True,
    },
    {
        "name": "Resmî Kumar Alan Adı Havuzu",
        "category": "gambling",
        "description": OFFICIAL_POOL_DESCRIPTION,
        "source_url": "https://hazard.mf.gov.pl/api/Register",
        "auto_update": True,
        "domains": "",
    },
    {
        "name": "UT1 Kara Listeleri (Toulouse Capitole Üniversitesi)",
        "category": "gambling",
        "description": "Toulouse Capitole Üniversitesi'nin 1990'lardan beri güncellenen açık kara listeleri: kumar, "
                       "uyuşturucu, oltalama ve zararlı yazılım alt listeleri. Her kayıt kendi kategorisiyle alınır.",
        "source_url": "https://dsi.ut-capitole.fr/blacklists/",
        "auto_update": True,
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

        for order, (question, answer) in enumerate(FAQS):
            FAQ.objects.get_or_create(question=question, defaults={"answer": answer, "order": order})
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
                (tablet, "ptt-kargo-takip-odeme.net"), (phone, "canlibahis-tv.top"), (tablet, "eba.gov.tr"),
            ]:
                check_domain(family, domain, device)

        self.stdout.write(self.style.SUCCESS(
            "Demo verisi hazır.\n"
            "  Yönetici: admin@famsecur.com / Admin.12345\n"
            "  Ebeveyn : ebeveyn@famsecur.com / Ebeveyn.12345"
        ))
