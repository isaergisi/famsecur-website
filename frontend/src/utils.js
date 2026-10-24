export const formatDate = (value) =>
  value ? new Date(value).toLocaleString("tr-TR", { dateStyle: "medium", timeStyle: "short" }) : "—";

export const CATEGORY_COLORS = {
  gambling: "var(--coral)",
  adult: "#e06c9f",
  drugs: "#c99a2e",
  phishing: "var(--blue-light)",
  malware: "var(--lime)",
};

// Silme gibi geri alınamaz işlemlerden önce onay ister.
export const confirmAction = (message) => window.confirm(message);
