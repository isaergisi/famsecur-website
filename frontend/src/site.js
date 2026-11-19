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
  "Aboneliğinizi dilediğiniz zaman WhatsApp hattımızdan veya destek e-postamızdan iptal edebilirsiniz.",
  "Fiyatlara KDV dâhildir.",
];

// Yapay zekâ modelinin test sonuçları: backend/ml/model/metrics.json → at_warning_threshold ile aynı tutulmalı.
export const AI_METRICS = {
  testSize: "144.850",
  threshold: 60,
  accuracy: "%92,6",
  recall: "%90,0",
  precision: "%84,3",
  falseAlarm: "%6,4",
  falseAlarmTurkey: "%5,4",
};
