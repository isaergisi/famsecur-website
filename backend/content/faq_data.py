"""Sitedeki Sıkça Sorulan Sorular'ın varsayılan içeriği (seed_demo ve veri migration'ları kullanır)."""

FAQS = [
    ('FamSecur nasıl çalışır?',
     'Bir sitenin açılabilmesi için cihazınız önce o sitenin adresini sorar; bu işleme DNS denir. FamSecur bu soruyu '
     'ev ağınızda yanıtlar: Site güvenliyse bağlantı her zamanki gibi kurulur, zararlı bir listede yer alıyorsa ya da '
     'riskli görünüyorsa site açılmaz. Sayfaların içeriğine, mesajlara veya ekrana hiçbir zaman bakılmaz.'),
    ('FamSecur çocuğumun mesajlarını veya geçmişini okuyor mu?',
     'Hayır. FamSecur yalnızca açılmak istenen sitenin adına bakar; mesajlar, ekran görüntüleri, sayfa içerikleri ve '
     'arama geçmişi hiçbir pakette toplanmaz. Başlangıç ve Ebeveyn paketlerinde yalnızca riskli bulunan istekler '
     'kaydedilir. Aile Plus paketinde ise, yalnızca açık rızanızla, ağınızda hangi sitelere günde kaç kez girildiğinin'
     ' özeti tutulur; sayfa adresi veya içerik tutulmaz.'),
    ('Hangi içerikleri engelliyor?',
     'Kumar ve bahis, yetişkin içerik, uyuşturucu, oltalama (phishing) ve zararlı yazılım. Oltalama verisi T.C. Siber '
     "Güvenlik Başkanlığı'nın USOM listesinden, yasa dışı kumar alan adları Polonya Maliye Bakanlığı'nın resmî "
     "sicilinden, zararlı yazılım ve uyuşturucu alan adları Toulouse Capitole Üniversitesi'nin UT1 listelerinden "
     'gelir. Listeler her gün güncellenir. Listelerde olmayan siteler adlarındaki risk işaretlerine göre '
     'değerlendirilir; yapay zekâ modeli de yeni riskli sitelerde sizi uyarır.'),
    ('Kurulum için ne gerekiyor?',
     "Modeminizin (router) DNS ayarını FamSecur'a yönlendirmeniz yeterlidir; çocuğunuzun cihazına uygulama yüklemeniz "
     'gerekmez. Kurulumun herhangi bir adımında WhatsApp hattımızdan veya destek e-postamızdan yardım alabilirsiniz.'),
    ('Hangi cihazlarda çalışır?',
     'Ev ağınıza bağlanan her cihazda çalışır: telefon, tablet, bilgisayar, oyun konsolu ve akıllı TV. Cihazın markası'
     ' veya işletim sistemi fark etmez; cihaz sayısında sınır yoktur.'),
    ('FamSecur ev dışında da koruma sağlar mı?',
     "FamSecur ev ağınızda çalışır; cihazlar ev Wi-Fi'ınıza bağlıyken korunur. Mobil veriyle, VPN üzerinden ya da "
     'tarayıcının kendi güvenli DNS ayarıyla bağlanan bir cihaz bu korumanın dışında kalabilir. Çocuğunuzun cihazında '
     'VPN uygulamalarını ve tarayıcıdaki güvenli DNS ayarını kontrol etmenizi öneririz.'),
    ('Hangi verileri saklıyorsunuz?',
     'Hesabınız, aile ve cihaz bilgileriniz, beyaz listeniz ve engel listeniz dışında yalnızca riskli bulunan '
     'istekleri (alan adı, kategori, risk puanı, gerekçe ve zaman) saklarız. Ebeveyn ve Aile Plus paketlerinde isteği '
     'yapan cihaz da kaydedilir; Başlangıç paketinde cihaz kaydedilmez. Bu kayıtlar varsayılan olarak 30 gün tutulur; '
     "süreyi panelden 1 ile 365 gün arasında değiştirebilirsiniz. Aile Plus'ta, açık rızanızla, günlük site sayıları "
     "30 gün saklanır. Ayrıntılar Gizlilik Politikası'nda yer alır."),
    ('Bir site yanlışlıkla engellenirse ne olur?',
     'Panelde her engelin nedenini görürsünüz. Yanlışlıkla engellenen siteyi tek tıkla beyaz listeye ekleyebilirsiniz;'
     ' sitenin alt adresleri de otomatik olarak açılır.'),
    ('Bir siteyi elle nasıl engellerim?',
     'Panelinizdeki Engel listem sayfasına sitenin adını yazmanız yeterlidir; alt adresleri de engellenir. Olaylar '
     'sayfasındaki "Engelle" düğmesiyle tek tıkla da ekleyebilirsiniz. Engel listesi üç pakette de çalışır. Beyaz '
     'listenizdeki bir site her zaman önceliklidir.'),
    ('Aile Plus günlük özetinde neler var?',
     'Her gün en çok girilen siteler, sosyal medya, video, oyun ve eğitim gibi kategorilere dağılım, cihaz bazında '
     'kullanım, gece 00.00-06.00 arasındaki kullanım ve ilk kez görülen siteler. Cihazların arka planda kendiliğinden '
     'sorduğu adresler sayılmaz. Hangi cihazların özete gireceğini siz seçersiniz; 18 yaşından büyük birinin cihazını '
     'onun bilgisi ve onayı olmadan dahil etmemelisiniz. Özet açık rızanızla çalışır ve rızanızı dilediğiniz an geri '
     'alabilirsiniz.'),
    ('Sessiz engel ile uyarı sayfası arasındaki fark nedir?',
     'Sessiz engellemede site açılmaz ve cihazda bağlantı hatası görünür; çocuğunuz engellenen içeriğin türünü '
     'öğrenmez. Uyarı sayfası modunda engelin nedeni bir FamSecur sayfasında gösterilir. Ancak bu sayfa yalnızca '
     'şifresiz (HTTP) sitelerde görünebilir; HTTPS kullanan sitelerde tarayıcı bir güvenlik uyarısı gösterir. Bu '
     'nedenle sessiz engellemeyi öneririz.'),
    ('Risk eşiği ne işe yarar?',
     'Her alan adı 0-100 arasında bir risk puanı alır. Eşiği düşürdüğünüzde koruma sıkılaşır, yükselttiğinizde '
     'yalnızca açık riskler engellenir. Küçük çocuklar için daha düşük, ergenler için daha yüksek bir eşik '
     "seçebilirsiniz. Varsayılan değer 70'tir."),
    ('Yapay zekâ nasıl karar veriyor?',
     'Model yalnızca alan adının harflerine bakar ve onu daha önce gördüğü binlerce kumar, yetişkin içerik ve temiz '
     'site adıyla karşılaştırır. Risk tahmini %60 ve üzerindeyse sizi uyarır. Ebeveyn ve Aile Plus paketlerinde "yapay'
     ' zekâ ile otomatik engel" ayarını açarsanız, hiçbir listede olmayan ama tahmini %85 ve üzerinde olan siteler de '
     'engellenir. Model sitenin içeriğini görmediği için yanılabilir; yanlış engellenen siteyi beyaz listenize '
     "ekleyebilirsiniz. Analiz FamSecur'un kendi sunucusunda yapılır."),
    ('Paketler arasındaki fark nedir?',
     'Başlangıç (aylık 100 TL veya yıllık 1.099 TL) ağınızda riskli bir siteye girildiğinde bunu panelinizde gösterir;'
     ' hangi cihazdan girildiğini göstermez ve otomatik engel yapmaz, yalnızca sizin engel listenize eklediğiniz '
     'siteleri engeller. Ebeveyn (aylık 149 TL veya yıllık 1.490 TL) riskli siteleri otomatik engeller, her olayın '
     'hangi cihazdan geldiğini gösterir ve siteleri elle de engellemenizi sağlar; isterseniz yapay zekâ ile otomatik '
     'engeli açabilirsiniz. Aile Plus (aylık 199 TL veya yıllık 2.099 TL) Ebeveyn paketinin tamamına ek olarak, açık '
     'rızanızla, ağınızda girilen tüm sitelerin her gün detaylı özetini sunar. Paketinizi değiştirmek için WhatsApp '
     'hattımıza veya destek e-postamıza yazabilirsiniz.'),
    ('Ücretsiz deneme nasıl işler?',
     'Üç pakette de deneme süresi 7 gündür ve seçtiğiniz paketin tüm özellikleri açıktır. Kayıt sırasında kart '
     'bilgileriniz ödeme kuruluşu tarafından alınır, deneme süresince ücret çekilmez. Deneme sonunda ücretli '
     'aboneliğin başlaması için kayıt ekranında ayrıca onayınız alınır ve deneme bitmeden 2 gün önce hatırlatma '
     'gönderilir. Aylık abonelik siz iptal edene kadar her ay yenilenir; yıllık abonelik kendiliğinden yenilenmez, '
     'yalnızca onayınızla yeni döneme geçilir.'),
    ('Aboneliğimi nasıl iptal ederim?',
     'Panelinizdeki Hesabım sayfasından tek tıkla iptal edebilirsiniz; WhatsApp hattımız ve destek e-postamız da '
     'kullanılabilir. Deneme süresi içinde iptal ederseniz hiçbir ücret alınmaz. Ücretli dönemde iptal ettiğinizde '
     'korumanız ödemesi yapılmış dönemin sonuna kadar devam eder; sonraki dönem için ücret alınmaz. Kayıttan itibaren '
     '14 gün içinde cayma hakkınız vardır ve bu sürede ödediğiniz tutar tamamen iade edilir.'),
    ('Verilerimi nasıl silerim?',
     'Olayları, cihazları, beyaz liste ve engel listesi kayıtlarını panelinizden dilediğiniz zaman silebilirsiniz. '
     'Aile Plus günlük özet rızanızı Hesabım sayfasından geri aldığınızda özet verileri hemen silinir. Hesabınızın '
     'kapatılmasını ve tüm verilerinizin silinmesini WhatsApp hattımızdan veya destek e-postamızdan isteyebilirsiniz; '
     'talebiniz en geç 30 gün içinde yerine getirilir. Mevzuat gereği saklanması gereken ödeme ve sözleşme kayıtları '
     'yasal süre dolana kadar saklanır.'),
    ('Çocuğum cihazın DNS ayarını değiştirirse ne olur?',
     'FamSecur modemin DNS ayarı üzerinden çalıştığı için cihazda elle farklı bir DNS sunucusu girilirse, tarayıcının '
     'güvenli DNS özelliği açılırsa ya da bir VPN uygulaması kullanılırsa o cihaz korumanın dışında kalabilir. Bunu '
     'önlemek için cihazlarda yönetici şifresi kullanmanızı, VPN uygulamalarının yüklenmesini ebeveyn denetimiyle '
     'kısıtlamanızı ve modeminizin yönetim şifresini değiştirmenizi öneririz.'),
]
