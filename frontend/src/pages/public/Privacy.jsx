import { Link } from "react-router-dom";
import usePageTitle from "../../components/usePageTitle";
import { DATA_INVENTORY, DATA_NEVER, SUPPORT } from "../../site";

const UPDATED = "19 Kasım 2026";

const PROCESSORS = [
  ["Barındırma hizmeti sağlayıcısı", "Hesap, cihaz, beyaz liste, engel olayı ve iletişim verileri", "Sitenin ve panelin çalıştığı sunucuların sağlanması"],
  ["Ödeme kuruluşu", "Kart ve ödeme bilgileri", "Abonelik ücretinin güvenli şekilde tahsili; kart bilgileri FamSecur'a iletilmez"],
  ["Cloudflare (1.1.1.1 DNS)", "Engellenmeyen sitelerin adı ve DNS sorgusunu ileten ağın IP adresi", "İzin verilen sitelerin adresinin çözülmesi"],
];

export default function Privacy() {
  usePageTitle("Gizlilik Politikası");
  return (
    <section className="section page">
      <div className="container narrow legal">
        <span className="eyebrow">Yasal</span>
        <h1>Gizlilik Politikası ve KVKK Aydınlatma Metni</h1>
        <p className="muted small">Son güncelleme: {UPDATED}</p>

        <p>
          FamSecur'un temel ilkesi, çocuğunuzu gözetlemeden korumaktır. Bu metin, 6698 sayılı Kişisel Verilerin Korunması
          Kanunu (KVKK) kapsamında hangi verileri, hangi amaçla ve ne kadar süreyle işlediğimizi açıklar.
        </p>

        <h2>1. Veri sorumlusu</h2>
        <p>
          Veri sorumlusu FamSecur'dur. Bize <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a> adresinden veya{" "}
          <a href={SUPPORT.whatsappLink} target="_blank" rel="noreferrer">{SUPPORT.whatsapp}</a> numaralı WhatsApp
          hattından ulaşabilirsiniz.
        </p>

        <h2>2. İşlediğimiz veriler ve saklama süreleri</h2>
        <div className="card table-wrap">
          <table className="data-table">
            <thead><tr><th>Veri</th><th>İçerik</th><th>Amaç</th><th>Hukuki sebep</th><th>Saklama süresi</th></tr></thead>
            <tbody>
              {DATA_INVENTORY.map((d) => (
                <tr key={d.name}>
                  <td data-label="Veri"><b>{d.name}</b></td>
                  <td data-label="İçerik">{d.content}</td>
                  <td data-label="Amaç">{d.purpose}</td>
                  <td data-label="Hukuki sebep">{d.basis}</td>
                  <td data-label="Saklama süresi" className="muted">{d.period}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2>3. Hiçbir zaman işlemediğimiz veriler</h2>
        <ul className="check-list">
          {DATA_NEVER.map((item) => <li className="no" key={item}>{item}</li>)}
        </ul>

        <h2>4. Koruma nasıl çalışır, hangi veri nereye gider?</h2>
        <p>
          Bir site açılmak istendiğinde cihaz yalnızca sitenin adını (alan adını) sorar. FamSecur bu adı tehdit
          listeleri, risk işaretleri ve yapay zekâ modeliyle değerlendirir. HTTPS trafiği açılmaz, sayfa içerikleri
          okunmaz.
        </p>
        <ul>
          <li><b>İzin verilen istekler</b> kaydedilmez. Sitenin açılabilmesi için istek, yanıtı veren DNS sunucusuna (varsayılan olarak Cloudflare 1.1.1.1) iletilir.</li>
          <li><b>Engellenen istekler</b> yalnızca yukarıdaki tabloda belirtilen bilgilerle ve belirtilen süre boyunca saklanır.</li>
          <li><b>Yapay zekâ analizi</b> FamSecur'un kendi sunucusunda yapılır; alan adları harici bir yapay zekâ hizmetine gönderilmez.</li>
          <li><b>Canlı demo</b>da yazdığınız alan adları kaydedilmez.</li>
        </ul>

        <h2>5. Hizmet sağlayıcıları ve aktarım</h2>
        <p>
          Verileriniz satılmaz ve reklam amacıyla paylaşılmaz. Yalnızca hizmetin çalışması için aşağıdaki hizmet
          sağlayıcılarıyla, gerekli olduğu ölçüde paylaşılır. Kanunen yetkili kurum ve kuruluşların talepleri saklıdır.
        </p>
        <div className="card table-wrap">
          <table className="data-table">
            <thead><tr><th>Hizmet sağlayıcı</th><th>Paylaşılan veri</th><th>Amaç</th></tr></thead>
            <tbody>
              {PROCESSORS.map(([who, what, why]) => (
                <tr key={who}>
                  <td data-label="Hizmet sağlayıcı"><b>{who}</b></td>
                  <td data-label="Paylaşılan veri">{what}</td>
                  <td data-label="Amaç">{why}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2>6. Yurt dışına aktarım</h2>
        <p>
          Cloudflare'in DNS sunucuları ve hizmet sağlayıcılarımızın bir kısmı yurt dışında bulunabilir. Bu durumda
          verileriniz, KVKK'nın 9. maddesinde öngörülen şartlara uygun olarak ve yalnızca yukarıdaki amaçlarla
          aktarılır.
        </p>

        <h2>7. Tarayıcıda saklanan bilgiler</h2>
        <p>
          Oturumunuzun açık kalması için giriş anahtarları tarayıcınızın yerel deposunda (localStorage) tutulur. Reklam
          veya izleme çerezi kullanılmaz.
        </p>

        <h2>8. Verilerin silinmesi ve hesabın kapatılması</h2>
        <ul>
          <li>Engel olaylarını panelinizdeki <b>Engel olayları</b> sayfasından tek tek veya tümüyle, cihazları ve beyaz liste kayıtlarını ilgili sayfalardan dilediğiniz zaman silebilirsiniz.</li>
          <li>Hesabınızın kapatılmasını ve tüm verilerinizin silinmesini <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a> adresinden veya WhatsApp hattımızdan isteyebilirsiniz. Talebiniz en geç 30 gün içinde yerine getirilir ve size bildirilir.</li>
          <li>Hesap kapatıldığında hesap, aile, cihaz, beyaz liste ve engel olayı verileri kalıcı olarak silinir. Mevzuat gereği saklanması gereken ödeme kayıtları, yasal süre dolana kadar saklanır.</li>
        </ul>

        <h2>9. Haklarınız</h2>
        <p>
          KVKK'nın 11. maddesi uyarınca kişisel verilerinizin işlenip işlenmediğini öğrenme, bilgi talep etme, düzeltilmesini
          veya silinmesini isteme, aktarıldığı üçüncü kişileri öğrenme ve itiraz etme haklarına sahipsiniz. Taleplerinizi{" "}
          <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a> adresine iletebilirsiniz; en geç 30 gün içinde
          yanıtlanır.
        </p>

        <p className="muted small">
          Sorularınız için <Link to="/iletisim">İletişim</Link> sayfasını kullanabilirsiniz.
        </p>
      </div>
    </section>
  );
}
