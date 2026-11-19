// Sitenin her yerinde aynı görünmesi gereken iletişim ve ürün bilgileri.
export const SUPPORT = {
  email: "destek@famsecur.com",
  whatsapp: "0553 453 20 19",
  whatsappLink: "https://wa.me/905534532019",
  responseTime: "en geç 1 iş günü içinde",
};

export const PRICES = { monthly: 149, yearly: 1490 };

export const TRIAL_TERMS = [
  "İlk 7 gün ücretsizdir; tüm özellikler açıktır.",
  "Kayıt sırasında kart bilgileriniz alınır, ancak deneme süresince herhangi bir ücret çekilmez.",
  `Deneme süresi dolmadan iptal etmezseniz aylık üyeliğiniz başlar ve ${PRICES.monthly} TL kartınızdan otomatik olarak tahsil edilir.`,
  "Aboneliğinizi dilediğiniz zaman WhatsApp hattımızdan veya destek e-postamızdan iptal edebilirsiniz. İptal ettiğinizde korumanız ödemesi yapılmış dönemin sonuna kadar devam eder; sonraki dönem için ücret alınmaz.",
  "Fiyatlara KDV dâhildir.",
];

// Yapay zekâ modelinin test sonuçları: backend/ml/model/metrics.json → at_warning_threshold ile aynı tutulmalı.
export const AI_METRICS = {
  testedAt: "19 Kasım 2026",
  testSize: "144.850",
  testMix: "20.000 kumar, 20.000 yetişkin içerik ve 104.850 temiz",
  threshold: 60,
  accuracy: "%92,6",
  recall: "%90,0",
  precision: "%84,3",
  falseAlarm: "%6,4",
  falseAlarmTurkey: "%5,4",
};

// Tek veri envanteri: ana sayfa, Gizlilik Politikası ve Kullanım Koşulları bu listeyi kullanır.
// short: ana sayfadaki kısa tablo için; diğer alanlar Gizlilik Politikası'ndaki ayrıntılı tablo için.
export const DATA_INVENTORY = [
  {
    name: "Hesap bilgileri",
    short: "Hesap: ad, soyad, e-posta ve şifrenin özeti (şifrenin kendisi değil)",
    content: "Ad, soyad, e-posta adresi, şifrenin özeti (şifrenin kendisi saklanmaz)",
    purpose: "Hesabın açılması ve oturum yönetimi",
    basis: "Sözleşmenin kurulması ve ifası (KVKK m. 5/2-c)",
    period: "Hesabınız kapatılana kadar",
  },
  {
    name: "Aile ve cihaz bilgileri",
    short: "Aile adı; cihaz adı, türü, kullanan kişi ve isteğe bağlı MAC adresi",
    content: "Aile adı; cihaz adı, türü, kullanan kişinin adı ve isteğe bağlı MAC adresi",
    purpose: "Korumanın cihaz bazında uygulanması",
    basis: "Sözleşmenin ifası (KVKK m. 5/2-c)",
    period: "Siz silene veya hesabınız kapatılana kadar",
  },
  {
    name: "Engel olayları",
    short: "Engellenen istek: alan adı, kategori, risk puanı, gerekçe, cihaz ve zaman",
    content: "Engellenen alan adı, kategori, risk puanı, gerekçe, isteği yapan cihaz ve zaman",
    purpose: "Engellerin panelinizde gösterilmesi ve haftalık özet",
    basis: "Sözleşmenin ifası (KVKK m. 5/2-c)",
    period: "Varsayılan 30 gün; panelden 1-365 gün arasında ayarlanabilir. Süresi dolanlar her gün otomatik silinir.",
  },
  {
    name: "Beyaz liste",
    short: "Beyaz listenize eklediğiniz siteler ve notlarınız",
    content: "Sizin izin verdiğiniz alan adları ve eklediğiniz notlar",
    purpose: "Yanlış engellerin düzeltilmesi",
    basis: "Sözleşmenin ifası (KVKK m. 5/2-c)",
    period: "Siz silene veya hesabınız kapatılana kadar",
  },
  {
    name: "İletişim talepleri",
    short: "İletişim formu: ad, e-posta ve mesaj",
    content: "Ad, e-posta adresi, konu ve mesaj",
    purpose: "Talebinize yanıt verilmesi",
    basis: "Meşru menfaat (KVKK m. 5/2-f)",
    period: "Talebiniz sonuçlanana kadar",
  },
  {
    name: "Ödeme bilgileri",
    short: "Abonelik durumu (kart bilgileri ödeme kuruluşunda tutulur)",
    content: "Abonelik durumu ve ödeme kayıtları; kart bilgileri FamSecur sunucularında saklanmaz, ödeme kuruluşu tarafından işlenir",
    purpose: "Abonelik ücretinin tahsili ve faturalandırma",
    basis: "Sözleşmenin ifası ve hukuki yükümlülük (KVKK m. 5/2-c, 5/2-ç)",
    period: "Vergi mevzuatının öngördüğü süre boyunca",
  },
];

// Hiçbir zaman toplanmayan veriler. "İzin verilen siteler" yerine "ziyaret geçmişi" denir:
// beyaz liste (ebeveynin izin verdiği siteler) saklanır, çocuğun ziyaret ettiği siteler saklanmaz.
export const DATA_NEVER = [
  "Mesajlar, sohbetler ve e-postalar",
  "Ekran görüntüleri ve tuş kayıtları",
  "Sayfa içerikleri, arama ve izleme geçmişi",
  "Ziyaret edilen ve engellenmeyen sitelerin geçmişi",
  "DNS kayıtlarında IP adresiniz",
];
