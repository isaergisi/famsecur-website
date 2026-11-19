from django.db import migrations

OLD_FAQ_Q = "Hangi içerikleri engelliyor?"
OLD_FAQ_A = (
    "Kumar/bahis, yetişkin içerik, uyuşturucu, oltalama (phishing) ve kötü amaçlı yazılım. Oltalama ve zararlı "
    "yazılım verileri T.C. Siber Güvenlik Başkanlığı'nın USOM listesinden, kumar alan adları resmî bir alan adı "
    "havuzundan ve açıklanabilir alan adı sinyallerinden gelir."
)


NEW_FAQ_A = (
    'Kumar ve bahis, yetişkin içerik, uyuşturucu, oltalama (phishing) ve zararlı yazılım. Oltalama verisi T.C.'
    " Siber Güvenlik Başkanlığı'nın USOM listesinden, yasa dışı kumar alan adları Polonya Maliye Bakanlığı'nın"
    " resmî sicilinden, zararlı yazılım ve uyuşturucu alan adları Toulouse Capitole Üniversitesi'nin UT1 "
    'listelerinden gelir. Listelerde olmayan siteler açıklanabilir alan adı sinyalleriyle değerlendirilir; '
    'yapay zeka modeli de yeni riskli sitelerde sizi uyarır.'
)
OUTSIDE_HOME_Q = (
    'FamSecur ev dışında da koruma sağlar mı?'
)
OUTSIDE_HOME_A = (
    "FamSecur ev ağınızda çalışır; cihazlar ev Wi-Fi'ınıza bağlıyken korunur. Mobil veriyle, VPN üzerinden ya "
    'da tarayıcının kendi güvenli DNS ayarıyla bağlanan bir cihaz bu korumanın dışında kalabilir. Çocuğunuzun '
    'cihazında VPN uygulamalarını ve tarayıcıdaki güvenli DNS ayarını kontrol etmenizi öneririz.'
)
OFFICIAL_POOL_DESCRIPTION = (
    "Polonya Maliye Bakanlığı'nın resmî yasa dışı kumar sicili. Kaynak adresinden güncellenir; yalnızca tam "
    'alan adı ve alt alan adı eşleşmesiyle karar verir.'
)


def update_texts(apps, schema_editor):
    """Eskimiş metinleri günceller: USOM artık yalnızca oltalama verir, zararlı yazılım UT1'den gelir; resmî
    havuzun alan adı sayısı otomatik güncellendiği için açıklamada sabit sayı tutulmaz. Yöneticinin elle
    değiştirdiği metinlere dokunulmaz."""
    FAQ = apps.get_model("content", "FAQ")
    ThreatSource = apps.get_model("shield", "ThreatSource")
    FAQ.objects.filter(question=OLD_FAQ_Q, answer=OLD_FAQ_A).update(answer=NEW_FAQ_A)
    # Yalnızca demo SSS'leri zaten yüklenmiş veritabanlarına yeni soru eklenir; boş veritabanını seed_demo doldurur.
    if FAQ.objects.filter(question=OLD_FAQ_Q).exists():
        FAQ.objects.get_or_create(
            question=OUTSIDE_HOME_Q,
            defaults={"answer": OUTSIDE_HOME_A, "order": 6},
        )
    ThreatSource.objects.filter(
        name="Resmî Kumar Alan Adı Havuzu", description__startswith="36.282 benzersiz alan adından"
    ).update(description=OFFICIAL_POOL_DESCRIPTION)


class Migration(migrations.Migration):
    dependencies = [("shield", "0004_urlhaus_kaldir"), ("content", "0001_initial")]

    operations = [migrations.RunPython(update_texts, migrations.RunPython.noop)]
