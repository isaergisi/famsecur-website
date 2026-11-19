
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shield", "0005_metin_guncellemeleri"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blockevent",
            name="category",
            field=models.CharField(
                choices=[
                    ("gambling", "Kumar / bahis"),
                    ("adult", "Yetişkin içerik"),
                    ("drugs", "Uyuşturucu"),
                    ("phishing", "Oltalama / dolandırıcılık"),
                    ("malware", "Zararlı yazılım"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="threatsource",
            name="category",
            field=models.CharField(
                choices=[
                    ("gambling", "Kumar / bahis"),
                    ("adult", "Yetişkin içerik"),
                    ("drugs", "Uyuşturucu"),
                    ("phishing", "Oltalama / dolandırıcılık"),
                    ("malware", "Zararlı yazılım"),
                ],
                max_length=20,
            ),
        ),
    ]
