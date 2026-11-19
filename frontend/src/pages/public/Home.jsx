import { useState } from "react";
import { Link } from "react-router-dom";
import {
  BellOff, Database, EyeOff, FileSearch, Gauge, ListChecks, Router, ShieldCheck, SlidersHorizontal, Sparkles, Wifi,
} from "lucide-react";
import { api, asList } from "../../api";
import Alert from "../../components/Alert";
import DecisionResult from "../../components/DecisionResult";
import useFetch from "../../components/useFetch";
import usePageTitle from "../../components/usePageTitle";
import { AI_METRICS, DATA_INVENTORY, DATA_NEVER, PRICES, SUPPORT, TRIAL_TERMS } from "../../site";
import { CATEGORY_LABELS, formatDate } from "../../utils";

const WHY = [
  { icon: EyeOff, title: "Çocuğunuzun özel alanına saygı", text: "Yalnızca açılmak istenen sitenin adına bakılır. Mesajlar, ekran görüntüleri ve gezinme geçmişi hiçbir zaman toplanmaz." },
  { icon: ShieldCheck, title: "Zararlı siteler açılmadan durur", text: "Yasa dışı bahis, yetişkin içerik, dolandırıcılık ve zararlı yazılım siteleri sayfa yüklenmeden engellenir." },
  { icon: Router, title: "Bir kez kurulur, tüm ev korunur", text: "Telefon, tablet, bilgisayar, oyun konsolu ve akıllı TV için ayrı ayrı uygulama kurmanız gerekmez." },
  { icon: SlidersHorizontal, title: "Kontrol her zaman sizde", text: "Neyin neden engellendiğini görür, yanlışlıkla engellenen bir siteye tek tıkla izin verirsiniz." },
];

const FEATURES = [
  {
    icon: Wifi,
    title: "Evdeki tüm cihazlarda koruma",
    text: "Modeminizin DNS ayarı üzerinden çalışır: Ev ağına bağlı cihazlar, kendi DNS ayarları değiştirilmediği sürece site adreslerini FamSecur'a sorar. Gizli sekme açmak ya da başka bir tarayıcı kullanmak tek başına korumayı kaldırmaz; ancak cihazın veya tarayıcının DNS ayarı değiştirilirse koruma aşılabilir.",
    example: "Arkadaşının tableti ev Wi-Fi'ınıza bağlandığında o cihaz da korunur.",
  },
  {
    icon: Sparkles,
    title: "Yeni sitelere karşı erken uyarı",
    text: "Yasa dışı bahis siteleri sık sık adres değiştirir. Yapay zekâ modelimiz, henüz hiçbir listede olmayan bir adresi adından tanır ve sizi uyarır. Model yalnızca uyarır, siteyi kendiliğinden engellemez.",
    example: "yenibahisadresi.net hiçbir listede olmasa da yüksek risk tahminiyle size bildirilir.",
  },
  {
    icon: FileSearch,
    title: "Her kararın gerekçesi",
    text: "Engellenen her sitenin kategorisi, risk puanı ve gerekçesi panelinizde açıkça görünür.",
    example: "bet2x.com · Kumar / bahis · 75 puan · adında kumar/bahis kelimesi var (bet)",
  },
  {
    icon: ListChecks,
    title: "Beyaz liste",
    text: "Yanlışlıkla engellenen bir siteye tek tıkla izin verin; sitenin alt adresleri de otomatik olarak açılır.",
    example: "Çocuğunuzun ödev için kullandığı bir site engellendiyse panelden hemen izin verebilirsiniz.",
  },
  {
    icon: Gauge,
    title: "Ayarlanabilir koruma seviyesi",
    text: "Risk eşiğini ailenizin ihtiyacına göre belirleyin; kumar, yetişkin içerik ve uyuşturucu kategorilerini dilediğiniz gibi açıp kapatın. Oltalama ve zararlı yazılım koruması güvenliğiniz için her zaman açık kalır.",
    example: "Küçük çocuklar için eşiği düşürerek daha sıkı, ergenler için yükselterek yalnızca açık riskleri engelleyen bir koruma seçebilirsiniz.",
  },
  {
    icon: BellOff,
    title: "Sessiz engelleme",
    text: "Engellenen site açılmaz ve cihazda bağlantı hatası görünür. Çocuğunuz engellenen içeriğin türünü öğrenmez; bu yaşlarda böyle içeriklerin varlığını öğrenmek bile merak uyandırabilir.",
  },
  {
    icon: Database,
    title: "Güvenilir kaynaklar, her gün güncel",
    text: "Oltalama için T.C. Siber Güvenlik Başkanlığı'nın USOM verisi, yasa dışı kumar için Polonya Maliye Bakanlığı'nın resmî sicili, zararlı yazılım ve uyuşturucu için Toulouse Capitole Üniversitesi'nin UT1 listeleri kullanılır. Listeler her gün güncellenir.",
  },
];

const STEPS = [
  ["Modeminize bağlayın", "Modeminizin DNS ayarını FamSecur'a yönlendirin. Çocuğunuzun cihazına uygulama kurmanıza gerek yok."],
  ["Koruma ayarlarınızı seçin", "Hangi kategorilerin hangi seviyede engelleneceğini ebeveyn panelinden belirleyin."],
  ["FamSecur arka planda çalışsın", "Zararlı siteler açılmadan engellenir; panelinizde yalnızca engellenen istekler görünür."],
];

const APPROACH = [
  ["Nerede çalışır", "Ev ağınızda, modeminizin DNS ayarı üzerinden"],
  ["Cihaza kurulum", "Gerekmez"],
  ["Neye bakar", "Yalnızca açılmak istenen sitenin adına"],
  ["Neye bakmaz", "Mesajlar, ekran, sayfa içerikleri, arama geçmişi"],
  ["Ne kaydeder", "Engellenen istekler (varsayılan 30 gün) ile sizin girdiğiniz hesap, cihaz ve beyaz liste bilgileri"],
  ["Yeni siteler", "Listede yoksa yapay zekâ sizi uyarır, karar sizindir"],
  ["Nerede korumaz", "Mobil veri, VPN, tarayıcıdaki güvenli DNS ayarı veya cihazın DNS ayarı değiştirildiğinde"],
];

const PLAN_FEATURES = [
  "Resmî kumar sicili ve güvenilir tehdit kaynaklarıyla koruma",
  "Yapay zekâ destekli erken uyarı",
  "Sessiz engelleme ve ayarlanabilir koruma seviyesi",
  "Haftalık özet raporu",
  "Evdeki tüm cihazlar için sınırsız koruma",
];

// [alan adı, risk tahmini, uyarı verildi mi, gerçek durum]. Hata örnekleri test kümesinden alındı.
const AI_EXAMPLES = [
  ["yenibahisadresi.net", "%100", true, "doğru"],
  ["canlimacizle-bahis.com", "%97", true, "doğru"],
  ["sahibinden.com", "%10", false, "doğru"],
  ["eba.gov.tr", "%0", false, "doğru"],
];
const AI_ERRORS = [
  ["vibram.com", "%72", true, "yanlış alarm: temiz bir ayakkabı markası"],
  ["pgadmin.org", "%72", true, "yanlış alarm: temiz bir yazılım sitesi"],
  ["stakers.com", "%42", false, "kaçırıldı: listede kumar sitesi olarak kayıtlı"],
  ["carousel.co.za", "%7", false, "kaçırıldı: listede kumar sitesi olarak kayıtlı"],
];
const AI_METHOD = [
  ["Test tarihi", AI_METRICS.testedAt],
  ["Veri kaynakları", "Riskli: Polonya Maliye Bakanlığı kumar sicili ve The Block List Project kumar/yetişkin listeleri. Temiz: Cisco Umbrella'nın en çok sorgulanan 1 milyon alan adı ve Google Chrome'un Türkiye'de en çok ziyaret edilen sitelerinin listesi (CrUX)."],
  ["Test kümesi", `${AI_METRICS.testSize} alan adı: ${AI_METRICS.testMix}`],
  ["Eğitim/test ayrımı", "Verinin %80'i eğitime, %20'si teste rastgele ve sınıf oranları korunarak ayrıldı. Test kümesindeki adlar eğitimde hiç kullanılmadı."],
  ["Risk puanı ne demek?", "Modelin bu adın temiz olmadığına dair hesapladığı olasılıktır (lojistik regresyon). %60 ve üzeri uyarı üretir. \"%100\", olasılığın %99,5'in üzerinde olduğunu gösterir; kesinlik anlamına gelmez."],
  ["Dikkat edilmesi gereken", "Ayrım rastgele yapıldığı için birbirine çok benzeyen adlar hem eğitim hem test kümesine düşebilir; bu, sonuçları bir miktar iyimser gösterebilir. Bazı Türkçe riskli örneklerin etiketi kural motorundan geldiği için o dilimdeki başarı da iyimser olabilir."],
];

const CATEGORIES = [
  CATEGORY_LABELS.gambling, CATEGORY_LABELS.adult, CATEGORY_LABELS.phishing, CATEGORY_LABELS.malware, CATEGORY_LABELS.drugs,
];
const EXAMPLES = ["casino777.xyz", "bet2x.com", "e-devlet-giris-dogrula.com", "eba.gov.tr", "better.com"];
const TL = (n) => n.toLocaleString("tr-TR");

// Kaynaklardaki toplam alan adı sayısı, binlik aşağı yuvarlanır (ör. 61.523 → "61.000+").
function listSummary(sources) {
  const list = asList(sources);
  const total = list.reduce((sum, s) => sum + (s.domain_count || 0), 0);
  if (total === 0) return null;
  const dates = list.map((s) => s.last_fetched_at).filter(Boolean).sort();
  return {
    total: total < 1000 ? TL(total) : `${TL(Math.floor(total / 1000) * 1000)}+`,
    updated: dates.length ? formatDate(dates[dates.length - 1]) : null,
  };
}

function SectionHead({ eyebrow, title, children }) {
  return (
    <>
      <span className="eyebrow">{eyebrow}</span>
      <h2>{title}</h2>
      {children && <p className="muted section-lead">{children}</p>}
    </>
  );
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
          <SectionHead eyebrow="Canlı demo" title="Bir siteyi FamSecur'un gözünden görün">
            Merak ettiğiniz bir site adını yazın; FamSecur'un bu siteyi engelleyip engellemeyeceğini ve nedenini görün.
            Demo, gerçek karar motorunu kullanır. <b>Yazdığınız alan adları kaydedilmez.</b>
          </SectionHead>
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
          <p className="muted small">
            <b>better.com</b>, masum bir sitenin yanlışlıkla engellenmesine örnektir; adında "bet" geçtiği için kural
            motoru engeller. Böyle durumlarda siteyi tek tıkla beyaz listenize ekleyebilirsiniz.
          </p>
          <h3 className="demo-how-title">Nasıl değerlendiriyoruz?</h3>
          <ol className="demo-how muted">
            <li><b>Tehdit listeleri:</b> Site adı USOM, resmî kumar sicili ve UT1 listelerinde aranır.</li>
            <li><b>Risk işaretleri:</b> Listede yoksa adındaki kelimelere ve uzantıya bakılır.</li>
            <li><b>Yapay zekâ:</b> Hiçbir listede olmayan adlar için ayrıca bir risk tahmini yapılır.</li>
          </ol>
        </div>
        <div>
          <Alert>{error}</Alert>
          {result ? (
            <DecisionResult decision={result} ai={result.ai} />
          ) : (
            !error && <div className="decision decision-empty">Sonuç burada görünecek.</div>
          )}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  usePageTitle(null);
  const { data: sources } = useFetch("/threat-sources/");
  const lists = listSummary(sources);
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <span className="eyebrow hero-eyebrow">Yapay zekâ destekli, gizlilik odaklı aile internet kalkanı</span>
            <h1>
              Müdahale etmeden <span className="lime">aileni koru.</span>
            </h1>
            <p className="lead">
              FamSecur, ev internetinize bağlanan her cihazda zararlı siteleri açılmadan engeller. Bir takip uygulaması
              değildir: Mesajları, ekranı ve gezinme geçmişini görmez.
            </p>
            <p className="hero-sub">
              Koruma, modeminizin DNS ayarı üzerinden çalışır; çocuğunuzun cihazına uygulama kurulmaz.
            </p>
            <div className="hero-actions">
              <Link to="/kayit" className="btn btn-primary">7 gün ücretsiz deneyin</Link>
              <a href="#nasil-calisir" className="btn btn-ghost">Nasıl çalıştığını görün</a>
            </div>
            <ul className="hero-stats">
              {lists && (
                <li>
                  <b>{lists.total}</b>
                  <span>zararlı alan adı listelerimizde</span>
                  <small>USOM, Polonya Maliye Bakanlığı ve UT1 · her gün güncellenir</small>
                </li>
              )}
              <li>
                <b>Kurulum yok</b>
                <span>çocuğun cihazına uygulama yüklenmez</span>
              </li>
              <li>
                <b>Geçmiş tutulmaz</b>
                <span>yalnızca engellenen istekler kaydedilir</span>
              </li>
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
          <SectionHead eyebrow="Neden FamSecur?" title="Korur ama gözetlemez." />
          <div className="card-grid">
            {WHY.map(({ icon: Icon, title, text }) => (
              <article className="card feature" key={title}>
                <Icon className="feature-icon" aria-hidden strokeWidth={1.8} />
                <h3>{title}</h3>
                <p className="muted">{text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section alt" id="nasil-calisir">
        <div className="container">
          <SectionHead eyebrow="Nasıl çalışır?" title="Üç adımda koruma" />
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

      <section className="section" id="ozellikler">
        <div className="container">
          <SectionHead eyebrow="Özellikler" title="Günlük hayatta işinize yarayan özellikler" />
          <div className="card-grid">
            {FEATURES.map(({ icon: Icon, title, text, example }) => (
              <article className="card feature" key={title}>
                <Icon className="feature-icon" aria-hidden strokeWidth={1.8} />
                <h3>{title}</h3>
                <p className="muted">{text}</p>
                {example && <p className="feature-example"><b>Örnek:</b> {example}</p>}
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section alt" id="koruma-yaklasimi">
        <div className="container">
          <SectionHead eyebrow="Koruma yaklaşımı" title="FamSecur'un koruma yaklaşımı">
            FamSecur'un neyi nasıl yaptığını ve nerede yetersiz kaldığını açıkça paylaşıyoruz.
          </SectionHead>
          <div className="card table-wrap approach-wrap">
            <table className="approach">
              <tbody>
                {APPROACH.map(([label, value], i) => (
                  <tr key={label} className={i === APPROACH.length - 1 ? "approach-limit" : ""}>
                    <th scope="row">{label}</th>
                    <td>{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="section" id="yapay-zeka">
        <div className="container">
          <SectionHead eyebrow="Yapay zekâ" title="Yapay zekâ modelimiz nasıl ölçüldü?">
            Model, eğitimde hiç görmediği {AI_METRICS.testSize} alan adı üzerinde, sitede uyarı verdiği %{AI_METRICS.threshold} risk
            eşiğinde test edildi.
          </SectionHead>
          <div className="metric-grid">
            <div className="card metric"><b>{AI_METRICS.accuracy}</b><span>doğruluk (riskli / temiz ayrımı)</span></div>
            <div className="card metric"><b>{AI_METRICS.recall}</b><span>riskli siteleri yakalama oranı</span></div>
            <div className="card metric"><b>{AI_METRICS.precision}</b><span>uyarıların gerçekten riskli çıkma oranı</span></div>
            <div className="card metric">
              <b>{AI_METRICS.falseAlarm}</b>
              <span>temiz sitelerde yanlış alarm oranı (Türkiye'de popüler sitelerde {AI_METRICS.falseAlarmTurkey})</span>
            </div>
          </div>
          <div className="card ai-method">
            <h3>Nasıl ölçtük?</h3>
            <dl>
              {AI_METHOD.map(([term, desc]) => (
                <div key={term}><dt>{term}</dt><dd className="muted">{desc}</dd></div>
              ))}
            </dl>
          </div>
          <div className="ai-explain">
            <div className="card">
              <h3>Sınırları</h3>
              <p className="muted">
                Model yalnızca alan adının harflerine bakar, sitenin içeriğini görmez. "better.com" gibi masum adlarda
                yanılabilir; bu yüzden siteleri engellemez, yalnızca sizi uyarır. Analiz FamSecur'un kendi sunucusunda
                yapılır; alan adları harici bir yapay zekâ hizmetine gönderilmez.
              </p>
            </div>
            <div className="card">
              <h3>Örnek tahminler</h3>
              <ul className="ai-examples">
                {AI_EXAMPLES.map(([name, risk, warn]) => (
                  <li key={name}>
                    <code>{name}</code>
                    <span className={warn ? "tag tag-warn" : "tag"}>{risk} · {warn ? "uyarı" : "uyarı yok"}</span>
                  </li>
                ))}
              </ul>
              <h3 className="ai-errors-title">Hata örnekleri</h3>
              <ul className="ai-examples">
                {AI_ERRORS.map(([name, risk, warn, note]) => (
                  <li key={name}>
                    <span><code>{name}</code><span className="muted small ai-note">{note}</span></span>
                    <span className={warn ? "tag tag-warn" : "tag"}>{risk} · {warn ? "uyarı" : "uyarı yok"}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      <LiveDemo />

      <section className="section alt" id="gizlilik">
        <div className="container privacy">
          <div>
            <SectionHead eyebrow="Gizlilik" title="Neleri işliyoruz, neleri asla işlemiyoruz" />
            <div className="card table-wrap">
              <table className="data-table">
                <thead><tr><th>İşlenen veri</th><th>Saklama süresi</th></tr></thead>
                <tbody>
                  {DATA_INVENTORY.map((d) => (
                    <tr key={d.name}>
                      <td data-label="İşlenen veri">{d.short}</td>
                      <td data-label="Saklama süresi" className="muted">{d.period}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="muted small privacy-note">
              Ziyaret edilen ve engellenmeyen siteler kaydedilmez. Ancak sitenin açılabilmesi için istek, yanıtı veren DNS sunucusuna
              (varsayılan olarak Cloudflare 1.1.1.1) iletilir. FamSecur HTTPS trafiğini açmaz ve sayfa içeriklerini
              okumaz. Ayrıntılar için <Link to="/gizlilik">Gizlilik Politikası</Link>'na bakabilirsiniz.
            </p>
          </div>
          <div>
            <img
              className="section-photo"
              src="/images/ebeveyn-cocuk-bilgisayar.webp"
              alt="Mutfak masasında dizüstü bilgisayara birlikte bakan baba ve oğul"
              width="1100"
              height="743"
              loading="lazy"
            />
            <h3>Asla işlenmeyenler</h3>
            <ul className="check-list">
              {DATA_NEVER.map((item) => <li className="no" key={item}>{item}</li>)}
            </ul>
          </div>
        </div>
      </section>

      {asList(sources).length > 0 && (
        <section className="section">
          <div className="container">
            <SectionHead eyebrow="Tehdit istihbaratı" title="Güvendiğimiz kaynaklar">
              Listeler her gün otomatik olarak güncellenir.{lists?.updated && ` Son güncelleme: ${lists.updated}.`}
            </SectionHead>
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
          <SectionHead eyebrow="Fiyatlandırma" title="Tek paket, tüm özellikler dâhil">
            Paket bir ev ağını kapsar; cihaz sayısında sınır yoktur.
          </SectionHead>
          <article className="card price-card">
            <h3>Aile paketi</h3>
            <div className="price-options">
              <div className="price-option">
                <span className="price-label">Aylık</span>
                <b className="price">{TL(PRICES.monthly)} TL<small>/ay</small></b>
                <span className="muted">Her ay yenilenir</span>
              </div>
              <div className="price-option">
                <span className="price-label">Yıllık</span>
                <b className="price">{TL(PRICES.yearly)} TL<small>/yıl</small></b>
                <span className="muted">Aylık ödemeye göre yılda {TL(PRICES.monthly * 12 - PRICES.yearly)} TL daha az</span>
              </div>
            </div>
            <ul className="check-list">
              {PLAN_FEATURES.map((f) => (
                <li className="yes" key={f}>{f}</li>
              ))}
            </ul>
            <Link to="/kayit" className="btn btn-primary">7 gün ücretsiz deneyin</Link>
            <div className="trial-terms">
              <h4>Deneme ve ödeme koşulları</h4>
              <ul>
                {TRIAL_TERMS.map((t) => <li key={t}>{t}</li>)}
              </ul>
            </div>
          </article>
        </div>
      </section>

      <section className="section" id="gelistirici">
        <div className="container maker">
          <SectionHead eyebrow="Türkiye'de geliştirildi" title="Türkiye'deki aileler için geliştirildi" />
          <p className="lead">
            FamSecur, yazılım mühendisi <b>İsa Ergişi</b> tarafından geliştirildi.
          </p>
          <p className="muted">
            Yapay zekâ modeli Türkiye'de sık ziyaret edilen sitelerle eğitildi; oltalama verisi T.C. Siber Güvenlik
            Başkanlığı'nın USOM listesinden alınıyor. Sık sık adres değiştiren yasa dışı bahis sitelerine karşı, bu sorunu
            yakından bilen biri tarafından geliştirildi.
          </p>
          <blockquote className="maker-quote">Amacım basit: çocuğunuzu gözetlemeden korumak.</blockquote>
          <p className="maker-sign">
            <b>İsa Ergişi</b>, FamSecur'un geliştiricisi
          </p>
          <p className="muted small">
            Bize ulaşın: <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a>
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
            <p>Hesabınızı oluşturun, cihazlarınızı ekleyin ve koruma ayarlarınızı birkaç dakika içinde belirleyin.</p>
            <Link to="/kayit" className="btn btn-dark">7 gün ücretsiz deneyin</Link>
          </div>
        </div>
      </section>
    </>
  );
}
