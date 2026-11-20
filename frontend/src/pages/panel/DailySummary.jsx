import { useState } from "react";
import { Link } from "react-router-dom";
import Alert from "../../components/Alert";
import PageHead from "../../components/PageHead";
import Spinner from "../../components/Spinner";
import useFetch from "../../components/useFetch";
import { PLANS, SUPPORT, TL } from "../../site";

const DAY_FMT = new Intl.DateTimeFormat("tr-TR", { day: "numeric", month: "long", weekday: "long" });
const parseDay = (iso) => {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
};
const CATEGORY_COLORS = {
  social: "#e06c9f", video: "var(--coral)", games: "#9b8cff", education: "var(--lime)", search: "var(--blue-light)",
  news: "#c99a2e", shopping: "#5fc4b8", messaging: "#7fb2ff", music: "#f0a35e", other: "var(--muted)",
};

function Locked({ plan }) {
  if (plan !== "plus") {
    return (
      <div className="card upsell">
        <h3>Günlük özet {PLANS.plus.name} paketinde</h3>
        <p className="muted">
          {PLANS.plus.name} ile her gün ağınızda en çok girilen siteleri, sosyal medya, video, oyun ve eğitim gibi
          kategorilere dağılımı, cihaz bazında ve gece saatlerindeki kullanımı görürsünüz. Aylık {TL(PLANS.plus.monthly)} TL
          veya yıllık {TL(PLANS.plus.yearly)} TL.
        </p>
        <p className="muted small">
          Paket değiştirmek için <a href={SUPPORT.whatsappLink} target="_blank" rel="noreferrer">WhatsApp hattımıza</a> veya{" "}
          <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a> adresine yazabilirsiniz. Günlük özet açık rızanızla çalışır.
        </p>
      </div>
    );
  }
  return (
    <div className="card upsell">
      <h3>Günlük özet kapalı</h3>
      <p className="muted">
        Günlük özet için açık rızanız yok veya geri alındı. <Link to="/panel/hesap">Hesabım</Link> sayfasından{" "}
        <Link to="/acik-riza" target="_blank">Açık Rıza Metni</Link>'ni okuyup yeniden verebilirsiniz.
      </p>
    </div>
  );
}

function Bars({ rows, labelKey = "label", colorOf }) {
  const max = Math.max(1, ...rows.map((r) => r.count));
  return rows.map((r) => (
    <div key={r[labelKey]} className="bar-row">
      <span>{r[labelKey]}</span>
      <div className="bar"><span style={{ width: `${(r.count / max) * 100}%`, background: colorOf?.(r) }} /></div>
      <b>{r.count}</b>
    </div>
  ));
}

export default function DailySummary() {
  const family = useFetch("/family/");
  const [day, setDay] = useState("");
  const { data: s, error, loading } = useFetch(`/daily-summary/${day ? `?day=${day}` : ""}`);

  if (loading || family.loading) return <Spinner />;
  if (error?.status === 403) {
    return (
      <>
        <PageHead title="Günlük özet" desc="Ağınızda her gün neler olduğunun özeti." />
        <Locked plan={family.data?.plan} />
      </>
    );
  }
  if (error) return <Alert>{error.message}</Alert>;

  const days = s.available_days.includes(s.day) ? s.available_days : [s.day, ...s.available_days];
  return (
    <>
      <PageHead
        title="Günlük özet"
        desc={`${DAY_FMT.format(parseDay(s.day))} · Sayılar ${s.retention_days} gün saklanır. Arka plan adresleri (güncelleme, reklam, CDN) sayılmaz.`}
      >
        <select value={s.day} onChange={(e) => setDay(e.target.value)} aria-label="Gün seç">
          {days.map((d) => <option key={d} value={d}>{DAY_FMT.format(parseDay(d))}</option>)}
        </select>
      </PageHead>

      {s.total_queries === 0 ? (
        <div className="card empty">
          Bu gün için kayıt yok. Ev cihazınız FamSecur'a bağlandığında özet her gün burada oluşur.
        </div>
      ) : (
        <>
          <div className="stat-grid">
            <div className="card stat"><span>Farklı site</span><b>{s.site_count}</b></div>
            <div className="card stat"><span>Toplam sorgu</span><b>{s.total_queries.toLocaleString("tr-TR")}</b></div>
            <div className="card stat"><span>Gece 00.00-06.00</span><b>{s.night_total}</b></div>
            <div className="card stat">
              <span>Riskli istek</span>
              <b>{s.risky_events}</b>
              {s.risky_events > 0 && <Link to="/panel/olaylar" className="small">Olaylara git →</Link>}
            </div>
          </div>

          <div className="two-col">
            <div className="card">
              <h3>En çok girilen siteler</h3>
              <ul className="simple-list">
                {s.top_sites.map((site) => (
                  <li key={site.domain}>
                    <span><b>{site.label}</b> <span className="muted small">{site.category_label}</span></span>
                    <b>{site.count}</b>
                  </li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h3>Kategorilere göre</h3>
              <Bars rows={s.by_category} colorOf={(r) => CATEGORY_COLORS[r.category]} />
              <h3 className="spaced">Cihazlara göre</h3>
              <Bars rows={s.by_device} labelKey="device" />
            </div>
          </div>

          <div className="two-col">
            <div className="card">
              <h3>Gece kullanımı</h3>
              {s.night_sites.length === 0 ? (
                <p className="muted">Gece 00.00-06.00 arasında site sorgusu olmadı.</p>
              ) : (
                <ul className="simple-list">
                  {s.night_sites.map((site) => (
                    <li key={site.domain}><span>{site.label}</span><b>{site.night}</b></li>
                  ))}
                </ul>
              )}
            </div>
            <div className="card">
              <h3>İlk kez görülen siteler</h3>
              {s.new_sites.length === 0 ? (
                <p className="muted">Son 30 günde görülmemiş yeni bir site yok.</p>
              ) : (
                <ul className="simple-list">
                  {s.new_sites.map((site) => (
                    <li key={site.domain}><span>{site.label}</span><span className="muted small">{site.category_label}</span></li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </>
      )}
      <p className="muted small">
        Özete dahil olacak cihazları <Link to="/panel/cihazlar">Cihazlar</Link> sayfasından, açık rızanızı{" "}
        <Link to="/panel/hesap">Hesabım</Link> sayfasından yönetebilirsiniz.
      </p>
    </>
  );
}
