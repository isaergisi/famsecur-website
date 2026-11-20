import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, asList } from "../../api";
import Alert from "../../components/Alert";
import PageHead from "../../components/PageHead";
import { PLANS } from "../../site";
import Spinner from "../../components/Spinner";
import { useToast } from "../../components/Toast";
import useFetch from "../../components/useFetch";
import WeeklySummary from "../../components/WeeklySummary";
import { CATEGORY_COLORS, EVENT_CATEGORY_LABELS, formatDate } from "../../utils";

export default function Overview() {
  const notify = useToast();
  const family = useFetch("/family/");
  const stats = useFetch("/events/stats/");
  const recent = useFetch("/events/?page=1");
  const [name, setName] = useState("");
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    if (family.data) setName(family.data.name);
  }, [family.data]);

  async function saveName(e) {
    e.preventDefault();
    try {
      family.setData(await api.patch("/family/", { name }));
      setEditing(false);
      notify("Aile adı güncellendi.");
    } catch (err) {
      notify(err.message, "error");
    }
  }

  if (family.loading || stats.loading) return <Spinner />;
  const error = family.error || stats.error;
  if (error) return <Alert>{error.message}</Alert>;
  const f = family.data;
  const s = stats.data;
  const max = Math.max(1, ...s.by_category.map((c) => c.count));

  return (
    <>
      <PageHead title={f.name} desc={`${f.plan_label ?? PLANS[f.plan]?.name} paketi · Ailenizin koruma durumuna genel bakış.`}>
        {editing ? (
          <form onSubmit={saveName} className="inline-form">
            <input value={name} onChange={(e) => setName(e.target.value)} aria-label="Aile adı" required />
            <button className="btn btn-primary btn-sm">Kaydet</button>
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setEditing(false)}>Vazgeç</button>
          </form>
        ) : (
          <button className="btn btn-ghost btn-sm" onClick={() => setEditing(true)}>Aile adını düzenle</button>
        )}
      </PageHead>

      {f.device_count === 0 && (
        <div className="card first-steps">
          <h3>Hoş geldiniz! Korumaya üç adımda başlayın</h3>
          <ol className="muted">
            <li><Link to="/panel/cihazlar">Cihazlarınızı ekleyin</Link>{f.shows_devices ? "; böylece olayların hangi cihazdan geldiğini görebilirsiniz." : "."}</li>
            <li><Link to="/panel/politika">Koruma ayarlarınızı seçin</Link>: risk eşiği, engelleme biçimi ve kategoriler.</li>
            <li>Modeminizin DNS ayarını FamSecur'a yönlendirin. Takıldığınız adımda <Link to="/iletisim">destek ekibimize</Link> ulaşabilirsiniz.</li>
          </ol>
        </div>
      )}
      {s.weekly && <WeeklySummary weekly={s.weekly} categoryLabels={EVENT_CATEGORY_LABELS} autoBlocks={f.auto_blocks} />}

      <div className="stat-grid">
        <div className="card stat"><span>Korunan cihaz</span><b>{f.device_count}</b></div>
        <div className="card stat"><span>{f.auto_blocks ? "Toplam olay" : "Riskli istek"}</span><b>{s.total}</b></div>
        <div className="card stat"><span>Son 7 gün</span><b>{s.last_7_days}</b></div>
        <div className="card stat">
          <span>Politika</span>
          <b className="stat-sm">Eşik {f.policy.risk_threshold} · {f.policy.enforcement_mode === "silent" ? "Sessiz" : "Uyarılı"}</b>
        </div>
      </div>

      <div className="two-col">
        <div className="card">
          <h3>Kategoriye göre olaylar</h3>
          {s.by_category.length === 0 && <p className="muted">Henüz engellenen bir istek yok.</p>}
          {s.by_category.map((c) => (
            <div key={c.category} className="bar-row">
              <span>{EVENT_CATEGORY_LABELS[c.category] || c.category}</span>
              <div className="bar"><span style={{ width: `${(c.count / max) * 100}%`, background: CATEGORY_COLORS[c.category] }} /></div>
              <b>{c.count}</b>
            </div>
          ))}
        </div>
        <div className="card">
          <h3>En sık görülen riskli alan adları</h3>
          {s.top_domains.length === 0 && <p className="muted">Kayıt yok.</p>}
          <ul className="simple-list">
            {s.top_domains.map((d) => (
              <li key={d.domain}><code>{d.domain}</code><b>{d.count}</b></li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card">
        <div className="card-head">
          <h3>Son olaylar</h3>
          <Link to="/panel/olaylar" className="small">Tümünü gör →</Link>
        </div>
        <ul className="simple-list">
          {asList(recent.data).slice(0, 5).map((e) => (
            <li key={e.id}>
              <span><code>{e.domain}</code> <span className="tag">{e.category_label}</span></span>
              <span className="muted small">{e.device_name || (f.shows_devices ? "Bilinmeyen cihaz" : "Cihaz gösterilmez")} · {formatDate(e.created_at)}</span>
            </li>
          ))}
          {asList(recent.data).length === 0 && <li className="muted">Henüz olay yok.</li>}
        </ul>
      </div>
    </>
  );
}
