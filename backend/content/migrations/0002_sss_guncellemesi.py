from django.db import migrations

# Eski varsayılan cevaplar: yalnızca bunlardan biriyle aynı olan kayıtlar güncellenir,
# yöneticinin elle değiştirdiği cevaplara dokunulmaz.
OLD_ANSWERS = {'Bir site yanlışlıkla engellenirse ne olur?': ['Panelde her engelin nedenini görürsünüz. Yanlış engellenen '
                                                'siteyi tek tıkla beyaz listeye ekleyebilirsiniz; alt alan '
                                                'adları da otomatik olarak izinli olur.'],
 'FamSecur ev dışında da koruma sağlar mı?': ["FamSecur ev ağınızda çalışır; cihazlar ev Wi-Fi'ınıza "
                                              'bağlıyken korunur. Mobil veriyle, VPN üzerinden ya da '
                                              'tarayıcının kendi güvenli DNS ayarıyla bağlanan bir cihaz bu '
                                              'korumanın dışında kalabilir. Çocuğunuzun cihazında VPN '
                                              'uygulamalarını ve tarayıcıdaki güvenli DNS ayarını kontrol '
                                              'etmenizi öneririz.'],
 'FamSecur çocuğumun mesajlarını veya geçmişini okuyor mu?': ['Hayır. FamSecur yalnızca DNS katmanında, '
                                                              'istenen alan adına bakarak karar verir. '
                                                              'Mesajlar, ekran, arama ve izleme geçmişi '
                                                              'toplanmaz. İzin verilen istekler hiçbir yerde '
                                                              'kaydedilmez; yalnızca engellenen alan adları, '
                                                              'kategori ve gerekçeyle birlikte panelinizde '
                                                              'görünür.'],
 'Hangi içerikleri engelliyor?': ['Kumar ve bahis, yetişkin içerik, uyuşturucu, oltalama (phishing) ve '
                                  "zararlı yazılım. Oltalama verisi T.C. Siber Güvenlik Başkanlığı'nın USOM "
                                  "listesinden, yasa dışı kumar alan adları Polonya Maliye Bakanlığı'nın "
                                  'resmî sicilinden, zararlı yazılım ve uyuşturucu alan adları Toulouse '
                                  "Capitole Üniversitesi'nin UT1 listelerinden gelir. Listelerde olmayan "
                                  'siteler açıklanabilir alan adı sinyalleriyle değerlendirilir; yapay zeka '
                                  'modeli de yeni riskli sitelerde sizi uyarır.'],
 'Kurulum için ne gerekiyor?': ["FamSecur ev router'ınızda veya ağdaki küçük bir cihazda çalışır. Router'ın "
                                "DNS ayarını FamSecur'a yönlendirmeniz yeterlidir; çocuğunuzun cihazına "
                                'uygulama yüklemeniz gerekmez.',
                                "FamSecur ev router'ınızda veya ağdaki küçük bir cihazda çalışır. Router'ın "
                                "DNS ayarını FamSecur'a yönlendirmeniz yeterlidir; çocuğun cihazına uygulama "
                                'yüklemeniz gerekmez.'],
 'Risk eşiği ne işe yarar?': ['Her alan adı 0-100 arası bir risk puanı alır. Eşiği düşürdüğünüzde koruma '
                              'sıkılaşır, yükselttiğinizde yalnızca çok net riskler engellenir. Varsayılan '
                              "değer 70'tir."],
 'Sessiz engel ile uyarı sayfası arasındaki fark nedir?': ['Sessiz engelde site hiç açılmaz (NXDOMAIN). '
                                                           'Uyarı modunda cihaz, engelin nedenini açıklayan '
                                                           'FamSecur sayfasına yönlendirilir.']}

FAQS = [('FamSecur nasıl çalışır?',
  'Bir sitenin açılabilmesi için cihazınız önce o sitenin adresini sorar; bu işleme DNS denir. FamSecur bu '
  'soruyu ev ağınızda yanıtlar: Site güvenliyse bağlantı her zamanki gibi kurulur, zararlı bir listede yer '
  'alıyorsa ya da riskli görünüyorsa site açılmaz. Sayfaların içeriğine, mesajlara veya ekrana hiçbir zaman '
  'bakılmaz.'),
 ('FamSecur çocuğumun mesajlarını veya geçmişini okuyor mu?',
  'Hayır. FamSecur yalnızca açılmak istenen sitenin adına bakarak karar verir. Mesajlar, ekran görüntüleri, '
  'arama ve izleme geçmişi toplanmaz. İzin verilen istekler hiçbir yerde kaydedilmez; panelinizde yalnızca '
  'engellenen siteler, kategorisi ve gerekçesiyle birlikte görünür.'),
 ('Hangi içerikleri engelliyor?',
  'Kumar ve bahis, yetişkin içerik, uyuşturucu, oltalama (phishing) ve zararlı yazılım. Oltalama verisi T.C. '
  "Siber Güvenlik Başkanlığı'nın USOM listesinden, yasa dışı kumar alan adları Polonya Maliye Bakanlığı'nın "
  "resmî sicilinden, zararlı yazılım ve uyuşturucu alan adları Toulouse Capitole Üniversitesi'nin UT1 "
  'listelerinden gelir. Listeler her gün güncellenir. Listelerde olmayan siteler adlarındaki risk '
  'işaretlerine göre değerlendirilir; yapay zekâ modeli de yeni riskli sitelerde sizi uyarır.'),
 ('Kurulum için ne gerekiyor?',
  "Modeminizin (router) DNS ayarını FamSecur'a yönlendirmeniz yeterlidir; çocuğunuzun cihazına uygulama "
  'yüklemeniz gerekmez. Kurulumun herhangi bir adımında WhatsApp hattımızdan veya destek e-postamızdan '
  'yardım alabilirsiniz.'),
 ('Hangi cihazlarda çalışır?',
  'Ev ağınıza bağlanan her cihazda çalışır: telefon, tablet, bilgisayar, oyun konsolu ve akıllı TV. Cihazın '
  'markası veya işletim sistemi fark etmez; cihaz sayısında sınır yoktur.'),
 ('FamSecur ev dışında da koruma sağlar mı?',
  "FamSecur ev ağınızda çalışır; cihazlar ev Wi-Fi'ınıza bağlıyken korunur. Mobil veriyle, VPN üzerinden ya "
  'da tarayıcının kendi güvenli DNS ayarıyla bağlanan bir cihaz bu korumanın dışında kalabilir. Çocuğunuzun '
  'cihazında VPN uygulamalarını ve tarayıcıdaki güvenli DNS ayarını kontrol etmenizi öneririz.'),
 ('Hangi verileri saklıyorsunuz?',
  'Yalnızca engellenen istekleri (alan adı, kategori, risk puanı, gerekçe ve zaman) varsayılan olarak 30 gün '
  'saklarız; bu süreyi panelden 1 ile 365 gün arasında değiştirebilirsiniz. İzin verilen siteler, mesajlar, '
  "ekran görüntüleri ve arama geçmişi hiçbir zaman kaydedilmez. Ayrıntılar Gizlilik Politikası'nda yer "
  'alır.'),
 ('Bir site yanlışlıkla engellenirse ne olur?',
  'Panelde her engelin nedenini görürsünüz. Yanlışlıkla engellenen siteyi tek tıkla beyaz listeye '
  'ekleyebilirsiniz; sitenin alt adresleri de otomatik olarak açılır.'),
 ('Sessiz engel ile uyarı sayfası arasındaki fark nedir?',
  'Sessiz engellemede site açılmaz ve cihazda bağlantı hatası görünür; çocuğunuz engellenen içeriğin türünü '
  'öğrenmez. Uyarı sayfası modunda engelin nedeni bir FamSecur sayfasında gösterilir. Ancak bu sayfa '
  'yalnızca şifresiz (HTTP) sitelerde görünebilir; HTTPS kullanan sitelerde tarayıcı bir güvenlik uyarısı '
  'gösterir. Bu nedenle sessiz engellemeyi öneririz.'),
 ('Risk eşiği ne işe yarar?',
  'Her alan adı 0-100 arasında bir risk puanı alır. Eşiği düşürdüğünüzde koruma sıkılaşır, yükselttiğinizde '
  'yalnızca açık riskler engellenir. Küçük çocuklar için daha düşük, ergenler için daha yüksek bir eşik '
  "seçebilirsiniz. Varsayılan değer 70'tir."),
 ('Yapay zekâ nasıl karar veriyor?',
  'Model yalnızca alan adının harflerine bakar ve onu daha önce gördüğü binlerce kumar, yetişkin içerik ve '
  'temiz site adıyla karşılaştırır. Risk tahmini %60 ve üzerindeyse sizi uyarır, ancak siteyi engellemez. '
  'Sitenin içeriğini görmediği için "better.com" gibi masum adlarda yanılabilir. Analiz FamSecur\'un kendi '
  'sunucusunda yapılır; alan adları harici bir yapay zekâ hizmetine gönderilmez.'),
 ('Ücretsiz deneme nasıl işler?',
  'Deneme süresi 7 gündür ve tüm özellikler açıktır. Kayıt sırasında kart bilgileriniz alınır, ancak deneme '
  'süresince herhangi bir ücret çekilmez. Süre dolmadan iptal etmezseniz aylık üyeliğiniz başlar ve aylık '
  'ücret kartınızdan otomatik olarak tahsil edilir.'),
 ('Aboneliğimi nasıl iptal ederim?',
  'Aboneliğinizi dilediğiniz zaman WhatsApp hattımızdan veya destek e-postamızdan iptal edebilirsiniz. '
  'Deneme süresi içinde iptal ederseniz hiçbir ücret alınmaz.')]


def update_faqs(apps, schema_editor):
    FAQ = apps.get_model("content", "FAQ")
    if not FAQ.objects.exists():
        return  # boş veritabanını seed_demo doldurur
    for order, (question, answer) in enumerate(FAQS):
        item = FAQ.objects.filter(question=question).first()
        if item is None:
            FAQ.objects.create(question=question, answer=answer, order=order)
        elif item.answer in OLD_ANSWERS.get(question, []):
            item.answer = answer
            item.order = order
            item.save(update_fields=["answer", "order"])


class Migration(migrations.Migration):
    dependencies = [("content", "0001_initial"), ("shield", "0005_metin_guncellemeleri")]

    operations = [migrations.RunPython(update_faqs, migrations.RunPython.noop)]
