"""Sitedeki Sıkça Sorulan Sorular'ın varsayılan içeriği (seed_demo ve veri migration'ları kullanır)."""

FAQS = [
    ("FamSecur nasıl çalışır?",
     "Bir sitenin açılabilmesi için cihazınız önce o sitenin adresini sorar; bu işleme DNS denir. FamSecur bu soruyu "
     "ev ağınızda yanıtlar: Site güvenliyse bağlantı her zamanki gibi kurulur, zararlı bir listede yer alıyorsa ya da "
     "riskli görünüyorsa site açılmaz. Sayfaların içeriğine, mesajlara veya ekrana hiçbir zaman bakılmaz."),
    ("FamSecur çocuğumun mesajlarını veya geçmişini okuyor mu?",
     "Hayır. FamSecur yalnızca açılmak istenen sitenin adına bakarak karar verir. Mesajlar, ekran görüntüleri, arama "
     "ve izleme geçmişi toplanmaz. Ziyaret edilen ve engellenmeyen siteler kaydedilmez; panelinizde yalnızca "
     "engellenen siteler, kategorisi ve gerekçesiyle birlikte görünür."),
    ("Hangi içerikleri engelliyor?",
     "Kumar ve bahis, yetişkin içerik, uyuşturucu, oltalama (phishing) ve zararlı yazılım. Oltalama verisi T.C. "
     "Siber Güvenlik Başkanlığı'nın USOM listesinden, yasa dışı kumar alan adları Polonya Maliye Bakanlığı'nın resmî "
     "sicilinden, zararlı yazılım ve uyuşturucu alan adları Toulouse Capitole Üniversitesi'nin UT1 listelerinden gelir. "
     "Listeler her gün güncellenir. Listelerde olmayan siteler adlarındaki risk işaretlerine göre değerlendirilir; "
     "yapay zekâ modeli de yeni riskli sitelerde sizi uyarır."),
    ("Kurulum için ne gerekiyor?",
     "Modeminizin (router) DNS ayarını FamSecur'a yönlendirmeniz yeterlidir; çocuğunuzun cihazına uygulama yüklemeniz "
     "gerekmez. Kurulumun herhangi bir adımında WhatsApp hattımızdan veya destek e-postamızdan yardım alabilirsiniz."),
    ("Hangi cihazlarda çalışır?",
     "Ev ağınıza bağlanan her cihazda çalışır: telefon, tablet, bilgisayar, oyun konsolu ve akıllı TV. Cihazın "
     "markası veya işletim sistemi fark etmez; cihaz sayısında sınır yoktur."),
    ("FamSecur ev dışında da koruma sağlar mı?",
     "FamSecur ev ağınızda çalışır; cihazlar ev Wi-Fi'ınıza bağlıyken korunur. Mobil veriyle, VPN üzerinden ya da "
     "tarayıcının kendi güvenli DNS ayarıyla bağlanan bir cihaz bu korumanın dışında kalabilir. Çocuğunuzun "
     "cihazında VPN uygulamalarını ve tarayıcıdaki güvenli DNS ayarını kontrol etmenizi öneririz."),
    ("Hangi verileri saklıyorsunuz?",
     "Hesabınız, aile ve cihaz bilgileriniz ile beyaz listeniz dışında yalnızca engellenen istekleri (alan adı, "
     "kategori, risk puanı, gerekçe, isteği yapan cihaz ve zaman) saklarız. Engel kayıtları varsayılan olarak 30 gün "
     "tutulur; bu süreyi panelden 1 ile 365 gün arasında değiştirebilirsiniz. Ziyaret edilen ve engellenmeyen "
     "siteler, mesajlar, ekran görüntüleri ve arama geçmişi kaydedilmez. Ayrıntılar Gizlilik Politikası'nda yer alır."),
    ("Bir site yanlışlıkla engellenirse ne olur?",
     "Panelde her engelin nedenini görürsünüz. Yanlışlıkla engellenen siteyi tek tıkla beyaz listeye ekleyebilirsiniz; "
     "sitenin alt adresleri de otomatik olarak açılır."),
    ("Sessiz engel ile uyarı sayfası arasındaki fark nedir?",
     "Sessiz engellemede site açılmaz ve cihazda bağlantı hatası görünür; çocuğunuz engellenen içeriğin türünü "
     "öğrenmez. Uyarı sayfası modunda engelin nedeni bir FamSecur sayfasında gösterilir. Ancak bu sayfa yalnızca "
     "şifresiz (HTTP) sitelerde görünebilir; HTTPS kullanan sitelerde tarayıcı bir güvenlik uyarısı gösterir. Bu "
     "nedenle sessiz engellemeyi öneririz."),
    ("Risk eşiği ne işe yarar?",
     "Her alan adı 0-100 arasında bir risk puanı alır. Eşiği düşürdüğünüzde koruma sıkılaşır, yükselttiğinizde "
     "yalnızca açık riskler engellenir. Küçük çocuklar için daha düşük, ergenler için daha yüksek bir eşik "
     "seçebilirsiniz. Varsayılan değer 70'tir."),
    ("Yapay zekâ nasıl karar veriyor?",
     "Model yalnızca alan adının harflerine bakar ve onu daha önce gördüğü binlerce kumar, yetişkin içerik ve temiz "
     "site adıyla karşılaştırır. Risk tahmini %60 ve üzerindeyse sizi uyarır, ancak siteyi engellemez. Sitenin "
     "içeriğini görmediği için \"better.com\" gibi masum adlarda yanılabilir. Analiz FamSecur'un kendi sunucusunda "
     "yapılır; alan adları harici bir yapay zekâ hizmetine gönderilmez."),
    ("Ücretsiz deneme nasıl işler?",
     "Deneme süresi 7 gündür ve tüm özellikler açıktır. Kayıt sırasında kart bilgileriniz alınır, ancak deneme "
     "süresince herhangi bir ücret çekilmez. Süre dolmadan iptal etmezseniz aylık üyeliğiniz başlar ve aylık ücret "
     "kartınızdan otomatik olarak tahsil edilir."),
    ("Aboneliğimi nasıl iptal ederim?",
     "Aboneliğinizi dilediğiniz zaman WhatsApp hattımızdan veya destek e-postamızdan iptal edebilirsiniz. Deneme "
     "süresi içinde iptal ederseniz hiçbir ücret alınmaz. Ücretli dönemde iptal ettiğinizde korumanız ödemesi "
     "yapılmış dönemin sonuna kadar devam eder; sonraki dönem için ücret alınmaz."),
    ("Verilerimi nasıl silerim?",
     "Engel kayıtlarını, cihazları ve beyaz liste kayıtlarını panelinizden dilediğiniz zaman silebilirsiniz. Hesabınızın "
     "kapatılmasını ve tüm verilerinizin silinmesini WhatsApp hattımızdan veya destek e-postamızdan isteyebilirsiniz; "
     "talebiniz en geç 30 gün içinde yerine getirilir. Mevzuat gereği saklanması gereken ödeme kayıtları yasal süre "
     "dolana kadar saklanır."),
    ("Çocuğum cihazın DNS ayarını değiştirirse ne olur?",
     "FamSecur modemin DNS ayarı üzerinden çalıştığı için cihazda elle farklı bir DNS sunucusu girilirse, tarayıcının "
     "güvenli DNS özelliği açılırsa ya da bir VPN uygulaması kullanılırsa o cihaz korumanın dışında kalabilir. Bunu "
     "önlemek için cihazlarda yönetici şifresi kullanmanızı, VPN uygulamalarının yüklenmesini ebeveyn denetimiyle "
     "kısıtlamanızı ve modeminizin yönetim şifresini değiştirmenizi öneririz."),
]
