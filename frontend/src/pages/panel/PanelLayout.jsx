import { useAuth } from "../../auth";
import DashboardLayout from "../../components/DashboardLayout";

const LINKS = [
  ["/panel", "Genel bakış", "📊"],
  ["/panel/cihazlar", "Cihazlar", "📱"],
  ["/panel/politika", "Koruma politikası", "🎚️"],
  ["/panel/beyaz-liste", "Beyaz liste", "✅"],
  ["/panel/olaylar", "Engel olayları", "🚫"],
  ["/panel/test", "Alan adı test et", "🔍"],
  ["/panel/hesap", "Hesabım", "👤"],
];

export default function PanelLayout() {
  const { isAdmin } = useAuth();
  return <DashboardLayout title="Ebeveyn paneli" links={LINKS} switchLink={isAdmin ? ["/yonetim", "Yönetim paneline geç →"] : null} />;
}
