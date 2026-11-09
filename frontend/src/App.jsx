import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import PublicLayout from "./components/PublicLayout";
import Spinner from "./components/Spinner";
import Home from "./pages/public/Home";
import Faq from "./pages/public/Faq";
import Contact from "./pages/public/Contact";
import Login from "./pages/public/Login";
import Register from "./pages/public/Register";
import NotFound from "./pages/public/NotFound";
import PanelLayout from "./pages/panel/PanelLayout";
import Overview from "./pages/panel/Overview";
import Devices from "./pages/panel/Devices";
import PolicyPage from "./pages/panel/Policy";
import Whitelist from "./pages/panel/Whitelist";
import Events from "./pages/panel/Events";
import TestDomain from "./pages/panel/TestDomain";
import Account from "./pages/panel/Account";
import AdminLayout from "./pages/admin/AdminLayout";
import AdminOverview from "./pages/admin/AdminOverview";
import Users from "./pages/admin/Users";
import ContactRequests from "./pages/admin/ContactRequests";
import FaqAdmin from "./pages/admin/FaqAdmin";
import ThreatSources from "./pages/admin/ThreatSources";

function RequireAuth({ children, admin = false }) {
  const { user, loading, isAdmin } = useAuth();
  if (loading) return <Spinner full />;
  if (!user) return <Navigate to="/giris" replace />;
  if (admin && !isAdmin) return <Navigate to="/panel" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route path="sss" element={<Faq />} />
        <Route path="iletisim" element={<Contact />} />
        <Route path="giris" element={<Login />} />
        <Route path="kayit" element={<Register />} />
        <Route path="*" element={<NotFound />} />
      </Route>
      <Route path="panel" element={<RequireAuth><PanelLayout /></RequireAuth>}>
        <Route index element={<Overview />} />
        <Route path="cihazlar" element={<Devices />} />
        <Route path="politika" element={<PolicyPage />} />
        <Route path="beyaz-liste" element={<Whitelist />} />
        <Route path="olaylar" element={<Events />} />
        <Route path="test" element={<TestDomain />} />
        <Route path="hesap" element={<Account />} />
      </Route>
      <Route path="yonetim" element={<RequireAuth admin><AdminLayout /></RequireAuth>}>
        <Route index element={<AdminOverview />} />
        <Route path="kullanicilar" element={<Users />} />
        <Route path="talepler" element={<ContactRequests />} />
        <Route path="sss" element={<FaqAdmin />} />
        <Route path="tehdit-kaynaklari" element={<ThreatSources />} />
      </Route>
    </Routes>
  );
}
