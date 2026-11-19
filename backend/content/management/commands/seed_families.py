"""Örnek aileler ve iletişim talepleri: python manage.py seed_families

10 ebeveyn hesabı (her birine aile, varsayılan politika, cihazlar ve birkaç
engel olayı) ile 3 iletişim talebi oluşturur. Tekrar çalıştırmak güvenlidir:
var olan kayıtlar yeniden oluşturulmaz.

Tüm örnek ebeveynlerin şifresi: Aile.12345
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from content.models import ContactRequest
from shield.models import Device, Family
from shield.services import check_domain

PASSWORD = "Aile.12345"

# (ad, soyad, e-posta, [(cihaz adı, tür, kullanan), ...], [engellenecek alan adları])
FAMILIES = [
    ("Mehmet", "Demir", "mehmet.demir@ornek.com",
     [("Zeynep'in telefonu", "phone", "Zeynep"), ("Ev bilgisayarı", "computer", "")],
     ["bet2x.com", "casino777.xyz"]),
    ("Fatma", "Kaya", "fatma.kaya@ornek.com",
     [("Emir'in tableti", "tablet", "Emir")],
     ["canlibahis-tv.top"]),
    ("Ahmet", "Çelik", "ahmet.celik@ornek.com",
     [("Defne'nin telefonu", "phone", "Defne"), ("Oyun konsolu", "console", "Kerem")],
     ["free-crack-indir.org", "yenibahisadresi.net"]),
    ("Elif", "Şahin", "elif.sahin@ornek.com",
     [("Mert'in bilgisayarı", "computer", "Mert")],
     ["e-devlet-giris-dogrula.com"]),
    ("Mustafa", "Yıldız", "mustafa.yildiz@ornek.com",
     [("Ecrin'in tableti", "tablet", "Ecrin"), ("Salon TV", "tv", "")],
     []),
    ("Zeynep", "Arslan", "zeynep.arslan@ornek.com",
     [("Yusuf'un telefonu", "phone", "Yusuf")],
     ["bet2x.com"]),
    ("Hüseyin", "Doğan", "huseyin.dogan@ornek.com",
     [("Asel'in tableti", "tablet", "Asel"), ("Ömer'in telefonu", "phone", "Ömer")],
     ["casino777.xyz", "ptt-kargo-takip-odeme.net", "canlibahis-tv.top"]),
    ("Emine", "Kılıç", "emine.kilic@ornek.com",
     [("Ali'nin bilgisayarı", "computer", "Ali")],
     []),
    ("Ali", "Aydın", "ali.aydin@ornek.com",
     [("Nehir'in telefonu", "phone", "Nehir")],
     ["yenibahisadresi.net"]),
    ("Hatice", "Öztürk", "hatice.ozturk@ornek.com",
     [("Eymen'in tableti", "tablet", "Eymen"), ("Oyun konsolu", "console", "Eymen")],
     ["free-crack-indir.org"]),
]

CONTACT_REQUESTS = [
    {
        "name": "Serkan Koç",
        "email": "serkan.koc@ornek.com",
        "topic": ContactRequest.Topic.DEMO,
        "message": "Merhaba, iki çocuğum var ve evdeki tüm cihazları korumak istiyorum. "
                   "Kurulum için bir demo görüşmesi ayarlayabilir miyiz?",
    },
    {
        "name": "Derya Aksoy",
        "email": "derya.aksoy@ornek.com",
        "topic": ContactRequest.Topic.SUPPORT,
        "message": "Kızımın ödev için kullandığı bir site engellendi. Beyaz listeye ekledim ama "
                   "yine de açılmadı, yardımcı olabilir misiniz?",
    },
    {
        "name": "Burak Polat",
        "email": "burak.polat@ornek.com",
        "topic": ContactRequest.Topic.PARTNERSHIP,
        "message": "Bir okulun bilgi işlem sorumlusuyum. FamSecur'u okul ağımızda kullanmak için "
                   "iş birliği seçeneklerinizi öğrenmek istiyoruz.",
    },
]


class Command(BaseCommand):
    help = "10 örnek aile (ebeveyn hesabı, cihazlar, engel olayları) ve 3 iletişim talebi oluşturur."

    @transaction.atomic
    def handle(self, *args, **options):
        new_families = 0
        for first_name, last_name, email, devices, domains in FAMILIES:
            user, created = User.objects.get_or_create(
                email=email, defaults={"first_name": first_name, "last_name": last_name}
            )
            if not created:
                continue
            user.set_password(PASSWORD)
            user.save()
            family = Family.create_with_defaults(owner=user, name=f"{last_name} Ailesi")
            created_devices = [
                Device.objects.create(family=family, name=name, device_type=kind, member_name=member)
                for name, kind, member in devices
            ]
            for i, domain in enumerate(domains):
                check_domain(family, domain, created_devices[i % len(created_devices)])
            new_families += 1

        new_requests = 0
        for data in CONTACT_REQUESTS:
            _, created = ContactRequest.objects.get_or_create(
                email=data["email"], message=data["message"], defaults=data
            )
            new_requests += created

        self.stdout.write(self.style.SUCCESS(
            f"{new_families} yeni aile ve {new_requests} yeni iletişim talebi eklendi.\n"
            f"  Örnek ebeveynlerin şifresi: {PASSWORD} (ör. mehmet.demir@ornek.com)"
        ))
