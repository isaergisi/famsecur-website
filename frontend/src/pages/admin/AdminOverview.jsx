import { Link } from "react-router-dom";
import Alert from "../../components/Alert";
import PageHead from "../../components/PageHead";
import Spinner from "../../components/Spinner";
import useFetch from "../../components/useFetch";

const LABELS = { gambling: "Kumar / bahis", adult: "Yetişkin içerik", drugs: "Uyuşturucu", phishing: "Dolandırıcılık / phishing", malware: "Kötü amaçlı yazılım" };

export default function AdminOverview() {
  const { data, error, loading } = useFetch("/admin/stats/");
  if (loading) return <Spinner />;
  if (error) return <Alert>{error.message}</Alert>;
  const max = Math.max(1, ...data.events_by_category.map((c) => c.count));
  return (
    <>
      <PageHead title="Yönetim paneli" desc="FamSecur platformunun genel durumu." />
      <div className="stat-grid">
        <div className="card stat"><span>Kullanıcı</span><b>{data.users}</b></div>
        <div className="card stat"><span>Aile</span><b>{data.families}</b></div>
        <div className="card stat"><span>Cihaz</span><b>{data.devices}</b></div>
        <div className="card stat"><span>Engel (7 gün)</span><b>{data.block_events_7d}</b></div>
      </div>
      <div className="two-col">
        <div className="card">
          <h3>Platform genelinde engeller</h3>
          {data.events_by_category.map((c) => (
            <div key={c.category} className="bar-row">
              <span>{LABELS[c.category]}</span>
              <div className="bar"><span style={{ width: `${(c.count / max) * 100}%` }} /></div>
              <b>{c.count}</b>
            </div>
          ))}
          {data.events_by_category.length === 0 && <p className="muted">Henüz engel yok.</p>}
        </div>
        <div className="card">
          <h3>Yapılacaklar</h3>
          <ul className="simple-list">
            <li><span>Açık iletişim talebi</span><Link to="/yonetim/talepler"><b>{data.open_contact_requests}</b></Link></li>
            <li><span>Aktif tehdit kaynağı</span><Link to="/yonetim/tehdit-kaynaklari"><b>{data.threat_sources}</b></Link></li>
            <li><span>Toplam engel olayı</span><b>{data.block_events}</b></li>
          </ul>
        </div>
      </div>
    </>
  );
}
