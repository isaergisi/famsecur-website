import { useState } from "react";
import { Link } from "react-router-dom";
import { api, asList } from "../../api";
import Alert from "../../components/Alert";
import DecisionResult from "../../components/DecisionResult";
import useFetch from "../../components/useFetch";

const FEATURES = [
  { icon: "🛡️", title: "Ağ seviyesinde koruma", text: "Router'daki DNS katmanında çalışır. Gizli mod, tarayıcı değişikliği veya uygulama silme korumayı kapatmaz." },
  { icon: "🔍", title: "Açıklanabilir kararlar", text: "Her engelin kategorisi, risk puanı ve gerekçesi panelde görünür. Kara kutu yok." },
  { icon: "🇹🇷", title: "Resmî kaynaklar", text: "Oltalama ve zararlı yazılım için USOM verisi, yasa dışı bahis için resmî alan adı havuzu kullanılır." },
  { icon: "✅", title: "Beyaz liste", text: "Yanlış engellenen bir siteyi tek tıkla izinli hâle getirin; alt alan adları da otomatik açılır." },
  { icon: "🎚️", title: "Ayarlanabilir eşik", text: "Risk eşiğini ailenize göre belirleyin; kategori bazında açıp kapatın." },
  { icon: "🔕", title: "Sessiz veya uyarılı engel", text: "Site sessizce açılmasın ya da çocuğunuz nedenini anlatan bir uyarı sayfası görsün." },
];

const STEPS = [
  ["Router'a bağlayın", "Ev router'ınızın DNS ayarını FamSecur'a yönlendirin. Çocuğun cihazına uygulama gerekmez."],
  ["Politikanızı seçin", "Hangi kategorilerin hangi eşikte engelleneceğine ebeveyn panelinden karar verin."],
  ["Gerisini FamSecur yapsın", "Zararlı alan adları milisaniyeler içinde engellenir, yalnızca engel olayları size raporlanır."],
];

const CATEGORIES = ["Kumar / bahis", "Yetişkin içerik", "Dolandırıcılık / phishing", "Kötü amaçlı yazılım", "Uyuşturucu"];
const EXAMPLES = ["casino777.xyz", "bet2x.com", "e-devlet-giris-dogrula.com", "eba.gov.tr"];

function LiveDemo() {
  const [domain, setDomain] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function analyze(value) {
    setBusy(true);
    setError("");
    try {
      setResult(await api.post("/analyze/", { domain: value }, { auth: false }));
    } catch (err) {
      setResult(null);
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="section" id="demo">
      <div className="container demo-grid">
        <div>
          <span className="eyebrow">Canlı demo</span>
          <h2>Karar motorunu kendiniz deneyin</h2>
          <p className="muted">
            Bir alan adı yazın; FamSecur'un gerçek karar motoru riski puanlasın ve nedenini açıklasın. Bu demoda
            yazdığınız hiçbir şey kaydedilmez.
          </p>
          <form
            className="demo-form"
            onSubmit={(e) => {
              e.preventDefault();
              analyze(domain);
            }}
          >
            <input value={domain} onChange={(e) => setDomain(e.target.value)} placeholder="ornek.com" aria-label="Alan adı" required />
            <button className="btn btn-primary" disabled={busy}>
              {busy ? "Analiz ediliyor…" : "Analiz et"}
            </button>
          </form>
          <div className="chips">
            {EXAMPLES.map((ex) => (
              <button key={ex} type="button" className="chip" onClick={() => { setDomain(ex); analyze(ex); }}>
                {ex}
              </button>
            ))}
          </div>
        </div>
        <div>
          <Alert>{error}</Alert>
          {result ? (
            <DecisionResult decision={result} />
          ) : (
            !error && <div className="decision decision-empty">Sonuç burada görünecek.</div>
          )}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const { data: sources } = useFetch("/threat-sources/");
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <span className="eyebrow">Gizlilik odaklı aile internet kalkanı</span>
            <h1>
              Müdahale etmeden, <span className="lime">Aileni koru.</span>
            </h1>
            <p className="lead">
              FamSecur ev ağınızda çalışır ve yalnızca kumar, yetişkin içerik, oltalama ve zararlı yazılım sitelerini
              engeller. Mesajlar, ekran ya da gezinme geçmişi asla toplanmaz.
            </p>
            <div className="hero-actions">
              <Link to="/kayit" className="btn btn-primary">
                Ücretsiz hesap oluştur
              </Link>
              <a href="#demo" className="btn btn-ghost">
                Canlı demoyu dene
              </a>
            </div>
            <ul className="hero-stats">
              <li><b>36.000+</b><span>resmî bahis alan adı</span></li>
              <li><b>5</b><span>risk kategorisi</span></li>
              <li><b>0</b><span>kaydedilen izinli istek</span></li>
            </ul>
          </div>
          <div className="hero-visual">
            <img src="/famsecur-logo.jpg" alt="FamSecur logosu: evi koruyan kalkan" />
          </div>
        </div>
      </section>

      <section className="section" id="ozellikler">
        <div className="container">
          <span className="eyebrow">Özellikler</span>
          <h2>Ebeveyn kontrolü, gözetim olmadan</h2>
          <div className="card-grid">
            {FEATURES.map((f) => (
              <article className="card feature" key={f.title}>
                <span className="feature-icon" aria-hidden>{f.icon}</span>
                <h3>{f.title}</h3>
                <p className="muted">{f.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section alt" id="nasil-calisir">
        <div className="container">
          <span className="eyebrow">Nasıl çalışır</span>
          <h2>Üç adımda koruma</h2>
          <ol className="steps">
            {STEPS.map(([title, text], i) => (
              <li key={title} className="card">
                <span className="step-no">{i + 1}</span>
                <h3>{title}</h3>
                <p className="muted">{text}</p>
              </li>
            ))}
          </ol>
          <div className="chips center">
            {CATEGORIES.map((c) => (
              <span key={c} className="chip static">{c}</span>
            ))}
          </div>
        </div>
      </section>

      <LiveDemo />

      <section className="section alt" id="gizlilik">
        <div className="container privacy">
          <div>
            <span className="eyebrow">Gizlilik ilkemiz</span>
            <h2>Neyi görmediğimiz, neyi gördüğümüz kadar önemli</h2>
            <p className="muted">
              FamSecur yalnızca istenen alan adına bakar. HTTPS trafiğini açmaz, içerik okumaz. İzin verilen her istek
              iz bırakmadan geçer; panelinize yalnızca engellenen alan adı, kategori, puan ve zaman düşer.
            </p>
          </div>
          <ul className="check-list">
            <li className="no">Mesajlar ve sohbetler</li>
            <li className="no">Ekran görüntüsü ve tuş kaydı</li>
            <li className="no">Arama ve izleme geçmişi</li>
            <li className="yes">Yalnızca engellenen alan adları</li>
          </ul>
        </div>
      </section>

      {asList(sources).length > 0 && (
        <section className="section">
          <div className="container">
            <span className="eyebrow">Tehdit istihbaratı</span>
            <h2>Kaynaklarımız</h2>
            <div className="card-grid">
              {asList(sources).map((s) => (
                <article className="card" key={s.id}>
                  <span className="tag">{s.category_label}</span>
                  <h3>{s.name}</h3>
                  <p className="muted">{s.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="section cta">
        <div className="container cta-box">
          <h2>Ailenizi bugün koruma altına alın</h2>
          <p>Hesabınızı oluşturun, cihazlarınızı ekleyin ve politikanızı birkaç dakikada belirleyin.</p>
          <Link to="/kayit" className="btn btn-dark">Hemen başla</Link>
        </div>
      </section>
    </>
  );
}
