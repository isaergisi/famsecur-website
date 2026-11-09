import DashboardLayout from "../../components/DashboardLayout";

const LINKS = [
  ["/yonetim", "Genel bakış", "📊"],
  ["/yonetim/kullanicilar", "Kullanıcılar", "👥"],
  ["/yonetim/talepler", "İletişim talepleri", "✉️"],
  ["/yonetim/sss", "SSS içerikleri", "❓"],
  ["/yonetim/tehdit-kaynaklari", "Tehdit kaynakları", "🛡️"],
];

export default function AdminLayout() {
  return <DashboardLayout title="Yönetim paneli" links={LINKS} switchLink={["/panel", "Ebeveyn paneline geç →"]} />;
}
