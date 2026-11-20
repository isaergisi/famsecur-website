// Sitenin her yerinde aynı görünmesi gereken iletişim ve ürün bilgileri.
export const SUPPORT = {
  email: "destek@famsecur.com",
  whatsapp: "0553 453 20 19",
  whatsappLink: "https://wa.me/905534532019",
  responseTime: "en geç 1 iş günü içinde",
};

// Satıcı / hizmet sağlayıcı bilgileri. 6563 sayılı Kanun m.3 ve Mesafeli Sözleşmeler Yönetmeliği m.5 gereği
// sitede ve ön bilgilendirme formunda gösterilmesi zorunludur. Boş (null) alanlar "doldurulacak" olarak görünür;
// canlıya almadan önce gerçek bilgilerle doldurulmalıdır.
export const SELLER = {
  title: null, // Ticaret unvanı veya şahıs şirketi sahibinin adı soyadı
  address: null, // Açık adres
  mersis: null, // MERSİS numarası (varsa)
  taxOffice: null, // Vergi dairesi ve vergi kimlik numarası
  kep: null, // KEP adresi (varsa)
  phone: SUPPORT.whatsapp,
  email: SUPPORT.email,
};
export const sellerField = (value) => value || "[doldurulacak]";

// Sözleşme ve aydınlatma metinlerinin sürümü (backend/accounts/serializers.py: LEGAL_VERSION ile aynı).
export const LEGAL_UPDATED = "20 Kasım 2026";

// Üç paket. Fiyatlar Ana sayfa, Kayıt ekranı, SSS, Kullanım Koşulları ve Mesafeli Satış metninde buradan okunur.
// Kimlikler (izleme/tam/plus) backend'deki Family.Plan ile aynıdır.
export const PLANS = {
  izleme: {
    id: "izleme",
    name: "Başlangıç",
    tagline: "Riskli girişleri görün, istediğinizi engelleyin",
    short: "Riskli girişleri gösterir, cihazı göstermez; yalnızca sizin eklediğiniz siteleri engeller.",
    monthly: 100,
    yearly: 1099,
    features: [
      "Ağınızda riskli bir siteye girildiğinde panelinizde görürsünüz: site, kategori ve zaman",
      "Kendi engel listeniz: istediğiniz siteyi tek tek engelleyin",
      "Resmî kumar sicili, güvenilir tehdit kaynakları ve yapay zekâ ile risk tespiti",
      "Haftalık özet raporu",
      "Evdeki tüm cihazlar, sınırsız",
    ],
    limits: [
      "Otomatik engel yok; yalnızca engel listenizdeki siteler engellenir",
      "İsteğin hangi cihazdan geldiği gösterilmez",
    ],
  },
  tam: {
    id: "tam",
    name: "Ebeveyn",
    tagline: "Kim girdi görün, otomatik ya da elle engelleyin",
    short: "Riskli siteleri otomatik engeller, hangi cihazdan girildiğini gösterir; elle de engelleyebilirsiniz.",
    monthly: 149,
    yearly: 1490,
    perDayNote: "Günde 5 TL'den az.",
    features: [
      "Zararlı siteler açılmadan otomatik engellenir",
      "Her olayın hangi cihazdan geldiğini görürsünüz",
      "Kendi engel listeniz ve tek tıkla \"Engelle\" düğmesi",
      "İsterseniz yapay zekâ ile otomatik engel: hiçbir listede olmayan ama çok riskli görünen siteler de engellenir",
      "Sessiz engelleme, beyaz liste ve ayarlanabilir koruma seviyesi",
      "Haftalık özet raporu",
      "Evdeki tüm cihazlar, sınırsız",
    ],
  },
  plus: {
    id: "plus",
    name: "Aile Plus",
    tagline: "Ağınızda neler oluyor, her gün detaylı özet",
    short: "Ebeveyn paketinin tamamı ve her gün tüm sitelerin detaylı özeti.",
    monthly: 199,
    yearly: 2099,
    features: [
      "Ebeveyn paketindeki her şey",
      "Her gün detaylı özet: en çok girilen siteler, sosyal medya, video, oyun ve eğitim gibi kategorilere dağılım",
      "Cihaz bazında kullanım, gece saatlerindeki kullanım ve ilk kez görülen siteler",
      "Özete hangi cihazların gireceğini siz seçersiniz",
      "Ham kayıt tutulmaz; günlük site sayıları 30 gün sonra silinir",
    ],
    note: "Günlük özet açık rızanızla çalışır; rızanızı panelden dilediğiniz an geri alabilirsiniz.",
  },
};
export const PLAN_ORDER = ["izleme", "tam", "plus"];
export const DEFAULT_PLAN = "tam";
export const planFromQuery = (value) => (value in PLANS ? value : DEFAULT_PLAN);
export const TL = (n) => n.toLocaleString("tr-TR");
// Yıllık ödeme tam 2 ay bedavaya denk geliyorsa bu söylenir; değilse yalnızca yıllık fiyat yazılır.
export const yearlySaving = (plan) => (plan.yearly === plan.monthly * 10 ? "2 ay ücretsiz" : null);

const priceList = PLAN_ORDER.map((id) => `${PLANS[id].name} ${PLANS[id].monthly} TL`).join(", ");

export const TRIAL_TERMS = [
  "Üç pakette de ilk 7 gün ücretsizdir; seçtiğiniz paketin tüm özellikleri açıktır.",
  "Kayıt sırasında kart bilgileriniz ödeme kuruluşu tarafından alınır, ancak deneme süresince herhangi bir ücret çekilmez.",
  `Deneme bittiğinde ücretli aboneliğin başlaması için kayıt ekranında ayrıca onayınız alınır. Deneme bitmeden 2 gün önce size e-postayla hatırlatma gönderilir; o güne kadar iptal etmezseniz seçtiğiniz dönemin ücreti (aylık: ${priceList}) kartınızdan tahsil edilir.`,
  "Aylık abonelik siz iptal edene kadar her ay yenilenir. Yıllık abonelik kendiliğinden yenilenmez: bitiminden 30 gün önce size hatırlatma gönderilir ve yalnızca onay verirseniz yeni dönem başlar.",
  "Aboneliğinizi panelinizdeki Hesabım sayfasından tek tıkla, ayrıca WhatsApp hattımızdan veya destek e-postamızdan iptal edebilirsiniz. İptal ettiğinizde hizmet ödenmiş dönemin sonuna kadar sürer; sonraki dönem için ücret alınmaz.",
  "Kayıt tarihinden itibaren 14 gün içinde gerekçe göstermeden cayabilirsiniz; bu süre içinde ödediğiniz bir tutar varsa tamamı 14 gün içinde iade edilir.",
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
    content: "Ad, soyad, e-posta adresi, şifrenin özeti (şifrenin kendisi saklanmaz), paket ve ödeme dönemi",
    purpose: "Hesabın açılması, oturum yönetimi ve aboneliğin yürütülmesi",
    basis: "Sözleşmenin kurulması ve ifası (KVKK m. 5/2-c)",
    period: "Hesabınız kapatılana kadar",
  },
  {
    name: "Aile ve cihaz bilgileri",
    short: "Aile adı; cihaz adı, türü, kullanan kişi ve isteğe bağlı MAC adresi",
    content: "Aile adı; cihaz adı, türü, kullanan kişinin adı, isteğe bağlı MAC adresi ve cihazın günlük özete dahil olup olmadığı",
    purpose: "Korumanın cihaz bazında uygulanması",
    basis: "Sözleşmenin ifası (KVKK m. 5/2-c)",
    period: "Siz silene veya hesabınız kapatılana kadar",
  },
  {
    name: "Riskli istek ve engel olayları",
    short: "Riskli bulunan istek: alan adı, kategori, risk puanı, gerekçe ve zaman; Ebeveyn ve Aile Plus'ta ayrıca cihaz",
    content: "Riskli bulunan veya engel listenizdeki alan adı, kategori, risk puanı, gerekçe, engellenip engellenmediği ve zaman. Ebeveyn ve Aile Plus paketlerinde isteği yapan cihaz da kaydedilir; Başlangıç paketinde cihaz bilgisi kaydedilmez.",
    purpose: "Riskli isteklerin ve engellerin panelinizde gösterilmesi ve haftalık özet",
    basis: "Sözleşmenin ifası (KVKK m. 5/2-c)",
    period: "Varsayılan 30 gün; panelden 1-365 gün arasında ayarlanabilir. Süresi dolanlar her gün otomatik silinir.",
  },
  {
    name: "Günlük site özeti (yalnızca Aile Plus)",
    short: "Aile Plus'ta, açık rızanızla: gün, cihaz ve site başına sorgu sayısı",
    content: "Yalnızca Aile Plus paketinde ve açık rızanızla: gün, cihaz, sitenin kayıtlı adı (ör. youtube.com) ve o gün kaç kez, kaçının gece 00.00-06.00 arasında sorgulandığı. Sayfa adresi, içerik ve saat saat ham kayıt tutulmaz. Özete dahil etmediğiniz cihazlar sayılmaz.",
    purpose: "Size her gün ağınızdaki kullanımın özetinin sunulması",
    basis: "Açık rıza (KVKK m. 5/1); çocuklar adına yasal temsilci olarak ebeveyn",
    period: "30 gün; rızanızı geri aldığınızda hemen silinir",
  },
  {
    name: "Beyaz liste ve engel listesi",
    short: "İzin verdiğiniz ve elle engellediğiniz siteler ile notlarınız",
    content: "Sizin izin verdiğiniz veya engellediğiniz alan adları ve eklediğiniz notlar",
    purpose: "Korumanın sizin tercihlerinize göre uygulanması",
    basis: "Sözleşmenin ifası (KVKK m. 5/2-c)",
    period: "Siz silene veya hesabınız kapatılana kadar",
  },
  {
    name: "Onay kayıtları",
    short: "Hangi metni hangi sürümüyle ne zaman onayladığınız",
    content: "Onaylanan metnin türü ve sürümü, onay ve geri alma zamanı",
    purpose: "Sözleşme ve rıza süreçlerinin ispatı",
    basis: "Hukuki yükümlülük ve bir hakkın tesisi, kullanılması veya korunması (KVKK m. 5/2-ç, 5/2-e)",
    period: "Sözleşme süresince ve sona ermesinden sonra 10 yıl (genel zamanaşımı süresi)",
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
  "Sayfa içerikleri, tam sayfa adresleri, arama ve izleme geçmişi",
  "Başlangıç ve Ebeveyn paketlerinde ziyaret edilen sitelerin geçmişi (yalnızca riskli bulunan istekler kaydedilir)",
  "DNS kayıtlarında IP adresiniz",
];
