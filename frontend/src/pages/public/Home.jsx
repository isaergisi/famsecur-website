import { useState } from "react";
import { Link } from "react-router-dom";
import { api, asList } from "../../api";
import Alert from "../../components/Alert";
import DecisionResult from "../../components/DecisionResult";
import useFetch from "../../components/useFetch";

const FEATURES = [
  { icon: "🛡️", title: "Ağ seviyesinde koruma", text: "Router'daki DNS katmanında çalışır. Gizli mod, tarayıcı değişikliği veya uygulama silme korumayı kapatmaz." },
  { icon: "🤖", title: "Yapay zeka destekli analiz", text: "Kendi eğittiğimiz model, hiçbir listede olmayan yeni kumar ve yetişkin içerik sitelerini adından tanır ve sizi uyarır. Hiçbir veri dışarı gönderilmez." },
  { icon: "🔍", title: "Açıklanabilir kararlar", text: "Her engelin kategorisi, risk puanı ve gerekçesi panelde görünür. Kara kutu yok." },
  { icon: "🇹🇷", title: "Resmî kaynaklar", text: "Oltalama ve zararlı yazılım için USOM verisi, yasa dışı bahis için resmî alan adı havuzu kullanılır." },
  { icon: "✅", title: "Beyaz liste", text: "Yanlış engellenen bir siteyi tek tıkla izinli hâle getirin; alt alan adları da otomatik açılır." },
  { icon: "🎚️", title: "Ayarlanabilir eşik", text: "Risk eşiğini ailenize göre belirleyin; kategori bazında açıp kapatın." },
  { icon: "🔕", title: "Sessiz veya uyarılı engel", text: "Site sessizce açılmasın ya da çocuğunuz nedenini anlatan bir uyarı sayfası görsün." },
];

const WHY = [
  { icon: "👁️‍🗨️", title: "Gözetlemeden korur", text: "Birçok ebeveyn kontrol uygulaması çocuğun mesajlarını, ekranını ve gezinme geçmişini izler; bu da aile içinde güveni zedeler. FamSecur yalnızca zararlı siteyi durdurur. Mesajlara, ekrana ya da geçmişe hiç bakmaz." },
  { icon: "🎯", title: "Türkiye'deki yasa dışı bahse odaklı", text: "Bahis siteleri her gün adres değiştiriyor (ör. yenibahis123.net) ve listeler buna yetişemiyor. FamSecur'un yapay zeka modeli, hiçbir listede olmayan yeni bir adresi adından tanır ve sizi uyarır. Model, Türkiye'de popüler sitelerle eğitildi." },
  { icon: "📶", title: "Tek kurulum, tüm cihazlar", text: "FamSecur ev ağında çalışır. Telefon, tablet ve oyun konsoluna ayrı ayrı uygulama kurmanız gerekmez. Cihazda uygulama olmadığı için çocuk onu silerek korumayı kapatamaz." },
  { icon: "🤫", title: "Çocuk merak etmeden güvende kalır", text: "Sessiz engel modunda zararlı site yalnızca açılmaz; çocuk \"kumar\" ya da \"yetişkin içerik\" yazan bir uyarıyla karşılaşmaz. Bu yaş grubunda böyle içeriklerin varlığını öğrenmek bile merak uyandırabilir. FamSecur bu kapıyı hiç aralamaz." },
];

const PLAN_FEATURES = [
  "Resmi kumar ve yetişkin içerik listelerine karşı koruma",
  "Yapay zeka ile risk tahmini: listede olmayan yeni riskli sitelerde sizi uyarır",
  "Sessiz engelleme modu",
  "Haftalık özet raporu",
  "Evdeki tüm cihazlar (sınırsız)",
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
            <span className="eyebrow">Yapay zeka destekli, gizlilik odaklı aile internet kalkanı</span>
            <h1>
              Müdahale etmeden, <span className="lime">Aileni koru.</span>
            </h1>
            <p className="lead">
              FamSecur ev ağınızda çalışır ve yalnızca kumar, yetişkin içerik, oltalama ve zararlı yazılım sitelerini
              engeller. Mesajlar, ekran ya da gezinme geçmişi asla toplanmaz. Yapay zeka destekli risk analizi, listelerde
              henüz olmayan yeni siteleri de adından tanır ve sizi uyarır.
            </p>
            <div className="hero-actions">
              <Link to="/kayit" className="btn btn-primary">
                7 gün ücretsiz dene
              </Link>
              <a href="#demo" className="btn btn-ghost">
                Canlı demoyu dene
              </a>
            </div>
            <ul className="hero-stats">
              <li><b>36.000+</b><span>resmî bahis alan adı</span></li>
              <li><b>%93</b><span>yapay zeka doğruluğu</span></li>
              <li><b>0</b><span>kaydedilen izinli istek</span></li>
            </ul>
          </div>
          <div className="hero-visual">
            <img
              className="hero-photo"
              src="/images/aile-kanepe.webp"
              alt="Evde kanepede birlikte gülümseyen dört kişilik aile"
              width="1200"
              height="800"
            />
            <div className="hero-badge">
              <img src="/famsecur-logo.jpg" alt="" width="44" height="44" />
              <div>
                <b>Ev ağınız korunuyor</b>
                <span>Yalnızca zararlı istekler engellenir</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section" id="neden-famsecur">
        <div className="container">
          <span className="eyebrow">Neden FamSecur?</span>
          <h2>Korur, ama gözetlemez.</h2>
          <div className="card-grid">
            {WHY.map((w) => (
              <article className="card feature" key={w.title}>
                <span className="feature-icon" aria-hidden>{w.icon}</span>
                <h3>{w.title}</h3>
                <p className="muted">{w.text}</p>
              </article>
            ))}
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
            <img
              className="section-photo"
              src="/images/ebeveyn-cocuk-bilgisayar.webp"
              alt="Mutfak masasında dizüstü bilgisayara birlikte bakan baba ve oğul"
              width="1100"
              height="743"
              loading="lazy"
            />
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

      <section className="section" id="fiyatlar">
        <div className="container pricing">
          <span className="eyebrow">Fiyatlar</span>
          <h2>Günde 5 TL'ye çocuğunu koru</h2>
          <p className="muted">
            7 gün ücretsiz deneyin, beğenmezseniz ödeme yapmazsınız. İstediğiniz zaman iptal edebilirsiniz.
          </p>
          <article className="card price-card">
            <h3>Aile paketi</h3>
            <div className="price-options">
              <div className="price-option">
                <span className="price-label">Aylık</span>
                <b className="price">149 TL<small>/ay</small></b>
                <span className="muted">Günde 5 TL'den az</span>
              </div>
              <div className="price-option">
                <span className="price-label">Yıllık</span>
                <b className="price">1.490 TL<small>/yıl</small></b>
                <span className="muted">Ayda ~124 TL, 2 ay bedava</span>
              </div>
            </div>
            <ul className="check-list">
              {PLAN_FEATURES.map((f) => (
                <li className="yes" key={f}>{f}</li>
              ))}
            </ul>
            <Link to="/kayit" className="btn btn-primary">7 gün ücretsiz dene</Link>
            <p className="muted price-note">Paket bir ev ağını kapsar. Fiyatlara KDV dahildir.</p>
          </article>
        </div>
      </section>

      <section className="section cta">
        <div className="container cta-box">
          <img
            className="cta-photo"
            src="/images/aile-disarida.webp"
            alt="Dışarıda kol kola poz veren mutlu dört kişilik aile"
            width="1100"
            height="733"
            loading="lazy"
          />
          <div className="cta-text">
            <h2>Ailenizi bugün koruma altına alın</h2>
            <p>Hesabınızı oluşturun, cihazlarınızı ekleyin ve politikanızı birkaç dakikada belirleyin.</p>
            <Link to="/kayit" className="btn btn-dark">Hemen başla</Link>
          </div>
        </div>
      </section>
    </>
  );
}
