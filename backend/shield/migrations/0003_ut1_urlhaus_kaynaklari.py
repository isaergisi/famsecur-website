from django.db import migrations

NEW_SOURCES = [
    {
        "name": "UT1 Kara Listeleri (Toulouse Capitole Üniversitesi)",
        "category": "gambling",
        "description": "Toulouse Capitole Üniversitesi'nin 1990'lardan beri güncellenen açık kara listeleri: kumar, "
                       "uyuşturucu, oltalama ve zararlı yazılım alt listeleri. Her kayıt kendi kategorisiyle alınır.",
        "source_url": "https://dsi.ut-capitole.fr/blacklists/",
    },
    {
        "name": "URLhaus (abuse.ch)",
        "category": "malware",
        "description": "abuse.ch'nin topluluk destekli, sürekli güncellenen zararlı yazılım dağıtan alan adları listesi.",
        "source_url": "https://urlhaus.abuse.ch/downloads/hostfile/",
    },
]


def add_sources(apps, schema_editor):
    ThreatSource = apps.get_model("shield", "ThreatSource")
    for data in NEW_SOURCES:
        ThreatSource.objects.get_or_create(name=data["name"], defaults={**data, "auto_update": True})


def remove_sources(apps, schema_editor):
    ThreatSource = apps.get_model("shield", "ThreatSource")
    ThreatSource.objects.filter(name__in=[d["name"] for d in NEW_SOURCES]).delete()


class Migration(migrations.Migration):
    dependencies = [("shield", "0002_kaynak_otomatik_guncelleme")]

    operations = [migrations.RunPython(add_sources, remove_sources)]
