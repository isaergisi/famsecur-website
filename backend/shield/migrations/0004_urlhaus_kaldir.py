from django.db import migrations


def remove_urlhaus(apps, schema_editor):
    """abuse.ch URLhaus hosts dosyasını kaldırdı (HTTP 410); kimlik doğrulamasız güvenilir bir adres
    doğrulanamadığı için kaynak tamamen kaldırılır."""
    ThreatSource = apps.get_model("shield", "ThreatSource")
    ThreatSource.objects.filter(name="URLhaus (abuse.ch)").delete()


class Migration(migrations.Migration):
    dependencies = [("shield", "0003_ut1_urlhaus_kaynaklari")]

    operations = [migrations.RunPython(remove_urlhaus, migrations.RunPython.noop)]
