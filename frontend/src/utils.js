export const formatDate = (value) =>
  value ? new Date(value).toLocaleString("tr-TR", { dateStyle: "medium", timeStyle: "short" }) : "—";

export const CATEGORY_COLORS = {
  gambling: "var(--coral)",
  adult: "#e06c9f",
  drugs: "#c99a2e",
  phishing: "var(--blue-light)",
  malware: "var(--lime)",
  manual: "#9b8cff",
};

// Silme gibi geri alınamaz işlemlerden önce onay ister.
export const confirmAction = (message) => window.confirm(message);

// Kategori adları backend ile aynı olmalı (shield/classifier.py: CATEGORY_LABELS).
export const CATEGORY_LABELS = {
  gambling: "Kumar / bahis",
  adult: "Yetişkin içerik",
  drugs: "Uyuşturucu",
  phishing: "Oltalama / dolandırıcılık",
  malware: "Zararlı yazılım",
};

// Olaylarda ek olarak görünen kategori: ailenin kendi engel listesi.
export const EVENT_CATEGORY_LABELS = { ...CATEGORY_LABELS, manual: "Engel listeniz" };
