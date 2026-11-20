"""Demo verisi: python manage.py seed_demo

Bir yönetici, bir demo ebeveyn hesabı, cihazlar, beyaz liste, örnek engel
olayları, SSS ve tehdit kaynakları oluşturur. Tekrar çalıştırmak güvenlidir.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from content.faq_data import FAQS
from content.models import FAQ
from shield.models import ConsentRecord, DailyDomainStat, Device, Family, ThreatSource
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

        self.seed_plus_family()

        self.stdout.write(self.style.SUCCESS(
            "Demo verisi hazır.\n"
            "  Yönetici : admin@famsecur.com / Admin.12345\n"
            "  Ebeveyn  : ebeveyn@famsecur.com / Ebeveyn.12345\n"
            "  Aile Plus: plus@famsecur.com / Plus.12345"
        ))

    def seed_plus_family(self):
        """Aile Plus örneği: son 7 günün günlük özet sayıları (ev ajanı bağlanana kadar örnek veri)."""
        from accounts.serializers import LEGAL_VERSION

        parent, created = User.objects.get_or_create(
            email="plus@famsecur.com", defaults={"first_name": "Murat", "last_name": "Aksoy"}
        )
        if not created:
            return
        parent.set_password("Plus.12345")
        parent.save()
        family = Family.create_with_defaults(owner=parent, name="Aksoy Ailesi", plan=Family.Plan.PLUS)
        for kind in (ConsentRecord.Kind.CONTRACT, ConsentRecord.Kind.PRIVACY_NOTICE, ConsentRecord.Kind.TRIAL_TO_PAID,
                     ConsentRecord.Kind.HOUSEHOLD, ConsentRecord.Kind.PLUS_SUMMARY):
            ConsentRecord.objects.create(user=parent, kind=kind, version=LEGAL_VERSION)
        deniz = Device.objects.create(family=family, name="Deniz'in telefonu", device_type="phone", member_name="Deniz")
        ada = Device.objects.create(family=family, name="Ada'nın tableti", device_type="tablet", member_name="Ada")
        Device.objects.create(family=family, name="Babanın bilgisayarı", device_type="computer", in_daily_summary=False)
        # (cihaz, alan adı, günlük sorgu, gece sorgusu)
        pattern = [
            (deniz, "instagram.com", 180, 22), (deniz, "tiktok.com", 240, 35), (deniz, "youtube.com", 120, 8),
            (deniz, "whatsapp.com", 90, 4), (deniz, "eba.gov.tr", 25, 0), (deniz, "google.com", 60, 2),
            (deniz, "spotify.com", 40, 6), (ada, "youtube.com", 150, 0), (ada, "roblox.com", 110, 0),
            (ada, "khanacademy.org", 30, 0), (ada, "duolingo.com", 18, 0), (ada, "google.com", 20, 0),
        ]
        today = timezone.localdate()
        rows = []
        for offset in range(7):
            day = today - timedelta(days=offset)
            scale = 1 - offset * 0.07
            for device, domain, count, night in pattern:
                rows.append(DailyDomainStat(family=family, device=device, day=day, domain=domain,
                                            count=int(count * scale), night_count=int(night * scale)))
        rows += [
            DailyDomainStat(family=family, device=deniz, day=today, domain="discord.com", count=45, night_count=12),
            DailyDomainStat(family=family, device=ada, day=today, domain="minecraft.net", count=28),
        ]
        DailyDomainStat.objects.bulk_create(rows)
        check_domain(family, "casino777.xyz", deniz)
