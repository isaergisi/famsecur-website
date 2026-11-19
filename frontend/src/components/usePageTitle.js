import { useEffect } from "react";

const BASE = "FamSecur";
const DEFAULT_TITLE = "FamSecur | Ev ağı için gizlilik odaklı aile internet koruması";

// Sayfa başlığını ayarlar; null verilirse ana sayfa başlığı kullanılır.
export default function usePageTitle(title) {
  useEffect(() => {
    document.title = title ? `${title} | ${BASE}` : DEFAULT_TITLE;
  }, [title]);
}
