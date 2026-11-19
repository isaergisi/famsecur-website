import { useState } from "react";
import { Link } from "react-router-dom";
import { api, asList } from "../../api";
import Alert from "../../components/Alert";
import DecisionResult from "../../components/DecisionResult";
import useFetch from "../../components/useFetch";
import { CATEGORY_LABELS } from "../../utils";

const FEATURES = [
  { icon: "🛡️", title: "Ağ seviyesinde koruma", text: "Ev router'ınızın DNS katmanında çalışır. Gizli sekme açmak ya da cihazdan bir uygulamayı silmek korumayı kapatmaz." },
  { icon: "🤖", title: "Yapay zeka destekli analiz", text: "Kendi eğittiğimiz model, henüz hiçbir listede olmayan yeni kumar ve yetişkin içerik sitelerini adından tanır ve sizi uyarır. Analiz FamSecur'un içinde yapılır; alan adları üçüncü taraf bir yapay zeka hizmetine gönderilmez." },
  { icon: "🔍", title: "Açıklanabilir kararlar", text: "Her engelin kategorisi, risk puanı ve gerekçesi panelinizde açıkça görünür. Hiçbir karar kara kutuda verilmez." },
  { icon: "📚", title: "Güvenilir kaynaklar", text: "Oltalama için T.C. Siber Güvenlik Başkanlığı'nın USOM verisi, yasa dışı kumar için Polonya Maliye Bakanlığı'nın resmî sicili, zararlı yazılım ve uyuşturucu için Toulouse Capitole Üniversitesi'nin UT1 listeleri kullanılır." },
  { icon: "✅", title: "Beyaz liste", text: "Yanlışlıkla engellenen bir siteye tek tıkla izin verin; alt alan adları da otomatik olarak açılır." },
  { icon: "🎚️", title: "Ayarlanabilir eşik", text: "Risk eşiğini ailenizin ihtiyacına göre ayarlayın, kategorileri tek tek açıp kapatın." },
  { icon: "🔕", title: "Sessiz veya uyarılı engel", text: "Site sessizce açılmasın ya da çocuğunuz nedenini anlatan nazik bir uyarı sayfası görsün; seçim sizin." },
];

const WHY = [
  { icon: "👁️‍🗨️", title: "Gözetlemeden korur", text: "Pek çok ebeveyn kontrol uygulaması çocuğun mesajlarını, ekranını ve gezinme geçmişini izler; bu da aile içindeki güveni zedeleyebilir. FamSecur yalnızca zararlı siteyi durdurur; mesajlara, ekrana ya da geçmişe hiç bakmaz." },
  { icon: "🎯", title: "Yasa dışı bahse karşı özel dikkat", text: "Yasa dışı bahis siteleri sık sık adres değiştirir (ör. yenibahis123.net) ve listeler her zaman yetişemez. FamSecur'un yapay zeka modeli, henüz hiçbir listede olmayan yeni bir adresi adından tanır ve sizi uyarır. Model, Türkiye'de sık ziyaret edilen sitelerle de eğitildi." },
  { icon: "📶", title: "Tek kurulum, evdeki tüm cihazlar", text: "FamSecur ev ağınızda çalışır; telefon, tablet ve oyun konsoluna tek tek uygulama kurmanız gerekmez. Cihazda uygulama olmadığı için silinerek devre dışı bırakılamaz. Koruma, cihazlar ev Wi-Fi'ınıza bağlıyken geçerlidir." },
  { icon: "🤫", title: "Merak uyandırmadan korur", text: "Sessiz engel modunda zararlı site yalnızca açılmaz; çocuğunuz \"kumar\" ya da \"yetişkin içerik\" yazan bir uyarıyla karşılaşmaz. Bu yaşlarda böyle içeriklerin varlığını öğrenmek bile merak uyandırabilir; FamSecur bu kapıyı hiç aralamaz." },
];

const COMPARE_ROWS = [
  ["Kumar ve yetişkin içerik sitelerini engeller", true, true],
  ["Engellenen siteleri ebeveyn panelinde raporlar", true, true],
  ["Mesajları, ekranı ve geçmişi gözetlemez", true, [false, 1]],
  ["Listede olmayan yeni bahis sitesini tanır", true, [false, 2]],
  ["Tek kurulumla evdeki tüm cihazları korur", true, false],
  ["Çocuk uygulamayı silerek korumayı kapatamaz", true, false],
  ["Engelin nedenini gösterir (kategori, risk puanı, gerekçe)", true, [false, 3]],
];
const COMPARE_NOTES = [
  "Birçok uygulama mesajları, ekranı veya gezinme geçmişini izler.",
  "Çoğu uygulama hazır site listelerine dayanır.",
  "Bazı uygulamalarda kısmen bulunur.",
];

function Mark({ value }) {
  const [ok, note] = Array.isArray(value) ? value : [value, null];
  return (
    <>
      <span className={ok ? "mark-yes" : "mark-no"} aria-hidden>{ok ? "✓" : "✗"}</span>
      <span className="sr-only">{ok ? "Evet" : "Hayır"}</span>
      {note && <sup className="compare-ref">{note}</sup>}
    </>
  );
}

const PLAN_FEATURES = [
  "Resmî kumar sicili ve güvenilir tehdit kaynaklarıyla koruma",
  "Yapay zeka destekli risk tahmini: listelerde henüz olmayan riskli sitelerde sizi uyarır",
  "Sessiz engelleme modu",
  "Haftalık özet raporu",
  "Evdeki tüm cihazlar için sınırsız koruma",
];

const STEPS = [
  ["Router'ınıza bağlayın", "Ev router'ınızın DNS ayarını FamSecur'a yönlendirin. Çocuğunuzun cihazına uygulama kurmanıza gerek yok."],
  ["Politikanızı belirleyin", "Hangi kategorilerin hangi risk eşiğinde engelleneceğini ebeveyn panelinden seçin."],
  ["Gerisini FamSecur'a bırakın", "Zararlı alan adları anında engellenir; size yalnızca engellenen istekler raporlanır."],
];

const CATEGORIES = [
  CATEGORY_LABELS.gambling, CATEGORY_LABELS.adult, CATEGORY_LABELS.phishing, CATEGORY_LABELS.malware, CATEGORY_LABELS.drugs,
];
const EXAMPLES = ["casino777.xyz", "bet2x.com", "e-devlet-giris-dogrula.com", "eba.gov.tr"];

// Kaynaklardaki toplam alan adı sayısı, binlik aşağı yuvarlanır (ör. 61.523 → "61.000+").
function domainTotalLabel(sources) {
  const total = asList(sources).reduce((sum, s) => sum + (s.domain_count || 0), 0);
  if (total === 0) return null;
  return total < 1000 ? total.toLocaleString("tr-TR") : `${(Math.floor(total / 1000) * 1000).toLocaleString("tr-TR")}+`;
}

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
  const domainTotal = domainTotalLabel(sources);
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <span className="eyebrow hero-eyebrow">Yapay zeka destekli, gizlilik odaklı aile internet kalkanı</span>
            <h1>
              Müdahale etmeden, <span className="lime">aileni koru.</span>
            </h1>
            <p className="lead">
              FamSecur ev ağınızda sessizce çalışır; kumar, yetişkin içerik, uyuşturucu, oltalama ve zararlı yazılım
              sitelerini çocuğunuza ulaşmadan durdurur. Mesajlara, ekrana ya da gezinme geçmişine hiçbir zaman bakmaz.
              Yapay zeka destekli risk analizi ise henüz hiçbir listeye girmemiş yeni siteleri adından tanır ve sizi uyarır.
            </p>
            <div className="hero-actions">
              <Link to="/kayit" className="btn btn-primary">
                7 gün ücretsiz deneyin
              </Link>
              <a href="#demo" className="btn btn-ghost">
                Canlı demoyu deneyin
              </a>
            </div>
            <ul className="hero-stats">
              {domainTotal && <li><b>{domainTotal}</b><span>engellenen alan adı</span></li>}
              <li><b>%93</b><span>test kümesinde yapay zeka doğruluğu</span></li>
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

      <section className="section alt" id="karsilastirma">
        <div className="container">
          <span className="eyebrow">Karşılaştırma</span>
          <h2>FamSecur'u ebeveyn kontrol uygulamalarıyla karşılaştırın</h2>
          <div className="card table-wrap compare-wrap">
            <table className="compare">
              <thead>
                <tr>
                  <th scope="col"><span className="sr-only">Özellik</span></th>
                  <th scope="col" className="compare-us">FamSecur</th>
                  <th scope="col">Ebeveyn kontrol uygulamaları</th>
                </tr>
              </thead>
              <tbody>
                {COMPARE_ROWS.map(([label, us, apps]) => (
                  <tr key={label}>
                    <th scope="row">{label}</th>
                    <td className="compare-us"><Mark value={us} /></td>
                    <td><Mark value={apps} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="compare-price">
            <b>FamSecur:</b> 149 TL/ay veya 1.490 TL/yıl, 7 gün ücretsiz deneme.
          </p>
          <ol className="muted small compare-notes">
            {COMPARE_NOTES.map((n) => <li key={n}>{n}</li>)}
          </ol>
          <p className="muted small">Genel bir karşılaştırmadır; tek tek ürünlerin özellikleri farklılık gösterebilir.</p>
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
              FamSecur yalnızca ziyaret edilmek istenen alan adına bakar; HTTPS trafiğini açmaz, sayfa içeriğini okumaz.
              İzin verilen her istek iz bırakmadan geçer. Panelinize yalnızca engellenen alan adı, kategori, risk puanı ve
              zaman bilgisi düşer.
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
            <h2>Güvendiğimiz kaynaklar</h2>
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
          <h2>Ailenizin dijital güvenliği, günde 5 TL'den az</h2>
          <p className="muted">
            İlk 7 gün ücretsiz; beğenmezseniz hiçbir ödeme yapmazsınız. Aboneliğinizi dilediğiniz zaman iptal edebilirsiniz.
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
                <span className="muted">Aylık yaklaşık 124 TL, 2 ay hediye</span>
              </div>
            </div>
            <ul className="check-list">
              {PLAN_FEATURES.map((f) => (
                <li className="yes" key={f}>{f}</li>
              ))}
            </ul>
            <Link to="/kayit" className="btn btn-primary">7 gün ücretsiz deneyin</Link>
            <p className="muted price-note">Paket bir ev ağını kapsar. Fiyatlara KDV dahildir.</p>
          </article>
        </div>
      </section>

      <section className="section" id="gelistirici">
        <div className="container maker">
          <span className="eyebrow">Yerli ve milli</span>
          <h2>Türkiye'de, Türk aileler için geliştirildi</h2>
          <p className="lead">
            FamSecur, Ankara'dan genç bir Türk mühendis olan <b>İsa Ergişi</b> tarafından geliştirildi.
          </p>
          <p className="muted">
            FamSecur, yabancı bir ürünün Türkçeye çevrilmiş hâli değil. Yapay zeka modeli Türkiye'de sık ziyaret edilen
            sitelerle eğitildi; oltalama verisi T.C. Siber Güvenlik Başkanlığı'nın USOM listesinden alınıyor. Sık sık adres
            değiştiren yasa dışı bahis sitelerine karşı, bu sorunu yakından bilen biri tarafından burada yazıldı.
          </p>
          <blockquote className="maker-quote">Amacım basit: çocuğunuzu gözetlemeden korumak.</blockquote>
          <p className="maker-sign">
            <b>İsa Ergişi</b>, FamSecur'un geliştiricisi
          </p>
          <p className="muted small">
            Özgeçmiş ve daha fazla bilgi için:{" "}
            <a href="mailto:iergisi23@posta.pau.edu.tr">iergisi23@posta.pau.edu.tr</a>
          </p>
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
            <p>Hesabınızı oluşturun, cihazlarınızı ekleyin ve koruma politikanızı birkaç dakika içinde belirleyin.</p>
            <Link to="/kayit" className="btn btn-dark">Hemen başlayın</Link>
          </div>
        </div>
      </section>
    </>
  );
}
