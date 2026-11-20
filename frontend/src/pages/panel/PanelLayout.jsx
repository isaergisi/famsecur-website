import { useAuth } from "../../auth";
import DashboardLayout from "../../components/DashboardLayout";

const LINKS = [
  ["/panel", "Genel bakış", "📊"],
  ["/panel/cihazlar", "Cihazlar", "📱"],
  ["/panel/politika", "Koruma politikası", "🎚️"],
  ["/panel/olaylar", "Olaylar", "🚫"],
  ["/panel/engel-listesi", "Engel listem", "⛔"],
  ["/panel/beyaz-liste", "Beyaz liste", "✅"],
  ["/panel/gunluk-ozet", "Günlük özet", "📅"],
  ["/panel/test", "Alan adı test et", "🔍"],
  ["/panel/koruma-listeleri", "Koruma listeleri", "🛡️"],
  ["/panel/hesap", "Hesabım", "👤"],
];

export default function PanelLayout() {
  const { isAdmin } = useAuth();
  return <DashboardLayout title="Ebeveyn paneli" links={LINKS} switchLink={isAdmin ? ["/yonetim", "Yönetim paneline geç →"] : null} />;
}
