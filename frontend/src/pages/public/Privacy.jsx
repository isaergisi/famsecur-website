import { Link } from "react-router-dom";
import usePageTitle from "../../components/usePageTitle";
import { DATA_INVENTORY, DATA_NEVER, LEGAL_UPDATED, SELLER, SUPPORT, sellerField } from "../../site";

const PROCESSORS = [
  ["Barındırma hizmeti sağlayıcısı", "Hesap, cihaz, liste, olay, günlük özet, onay ve iletişim verileri", "Sitenin ve panelin çalıştığı sunucuların sağlanması"],
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
        <p className="muted small">Son güncelleme: {LEGAL_UPDATED}</p>

        <p>
          FamSecur'un temel ilkesi, çocuğunuzu gözetlemeden korumaktır. Bu metin, 6698 sayılı Kişisel Verilerin Korunması
          Kanunu (KVKK) m. 10 ve Aydınlatma Yükümlülüğünün Yerine Getirilmesinde Uyulacak Usul ve Esaslar Hakkında
          Tebliğ uyarınca hangi verileri, hangi amaçla, hangi hukuki sebeple, nasıl topladığımızı, kimlere aktardığımızı
          ve haklarınızı açıklar.
        </p>

        <h2>1. Veri sorumlusu</h2>
        <p>
          Veri sorumlusu <span className={SELLER.title ? "" : "missing"}>{sellerField(SELLER.title)}</span> ("FamSecur"),
          adres: <span className={SELLER.address ? "" : "missing"}>{sellerField(SELLER.address)}</span>. Bize{" "}
          <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a> adresinden veya{" "}
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

        <h2>3. Verileri nasıl topluyoruz?</h2>
        <p>
          Verileriniz elektronik ortamda, otomatik yollarla toplanır: kayıt formu ve ebeveyn paneline girdiğiniz bilgiler,
          ev ağınızda modeminizin DNS ayarı üzerinden FamSecur'a gelen alan adı sorguları ve iletişim formu. Ödeme
          bilgileri doğrudan ödeme kuruluşu tarafından toplanır.
        </p>

        <h2>4. Pakete göre ne kaydedilir?</h2>
        <ul>
          <li><b>Başlangıç:</b> Yalnızca riskli bulunan veya engel listenizdeki istekler, cihaz bilgisi olmadan kaydedilir.</li>
          <li><b>Ebeveyn:</b> Yalnızca riskli bulunan veya engellenen istekler, isteği yapan cihazla birlikte kaydedilir.</li>
          <li>
            <b>Aile Plus:</b> Ebeveyn paketindekilere ek olarak, yalnızca <Link to="/acik-riza">açık rızanızla</Link> ve
            yalnızca günlük özete dahil ettiğiniz cihazlar için, her gün hangi sitenin (kayıtlı adıyla, ör. youtube.com)
            kaç kez sorgulandığı sayılır. Sayfa adresi, içerik, saat saat liste veya ham DNS kaydı saklanmaz; sayılar 30
            gün sonra silinir. Cihazların arka planda kendiliğinden sorduğu adresler (güncelleme, reklam, içerik dağıtım
            ağları) sayılmaz.
          </li>
        </ul>

        <h2>5. Hiçbir zaman işlemediğimiz veriler</h2>
        <ul className="check-list">
          {DATA_NEVER.map((item) => <li className="no" key={item}>{item}</li>)}
        </ul>

        <h2>6. Koruma nasıl çalışır, hangi veri nereye gider?</h2>
        <p>
          Bir site açılmak istendiğinde cihaz yalnızca sitenin adını (alan adını) sorar. FamSecur bu adı tehdit
          listeleri, risk işaretleri ve yapay zekâ modeliyle değerlendirir. HTTPS trafiği açılmaz, sayfa içerikleri
          okunmaz.
        </p>
        <ul>
          <li><b>İzin verilen istekler</b> olay günlüğüne yazılmaz (Aile Plus'ta yalnızca günlük sayıya eklenir). Sitenin açılabilmesi için istek, yanıtı veren DNS sunucusuna (varsayılan olarak Cloudflare 1.1.1.1) iletilir.</li>
          <li><b>Riskli ve engellenen istekler</b> yalnızca yukarıdaki tabloda belirtilen bilgilerle ve belirtilen süre boyunca saklanır.</li>
          <li><b>Yapay zekâ analizi</b> FamSecur'un kendi sunucusunda yapılır; alan adları harici bir yapay zekâ hizmetine gönderilmez.</li>
          <li><b>Canlı demo</b>da yazdığınız alan adları kaydedilmez.</li>
        </ul>

        <h2>7. Çocukların ve hane bireylerinin verileri</h2>
        <ul>
          <li>Cihazları kullanan çocuklarınızın verileri, velayet hakkına sahip ebeveyn olarak sizin talimatınızla ve onların korunması amacıyla işlenir. Aile Plus günlük özeti için çocuklarınız adına açık rızayı yasal temsilcileri olarak siz verirsiniz.</li>
          <li>Evdeki 18 yaşından büyük kişilerin cihazlarını kendi bilgileri ve onayları olmadan günlük özete dahil etmemeniz gerekir. Bir cihazı özetten çıkardığınızda o cihaz için yeni sayı tutulmaz.</li>
          <li>FamSecur, sitelerin adlarından sağlık, din veya cinsel hayat gibi özel nitelikli kişisel veri çıkarımı yapmaz ve bu amaçla profil oluşturmaz.</li>
        </ul>

        <h2>8. Hizmet sağlayıcıları ve aktarım</h2>
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

        <h2>9. Yurt dışına aktarım</h2>
        <p>
          Cloudflare'in DNS sunucuları ve hizmet sağlayıcılarımızın bir kısmı yurt dışında bulunabilir. Bu durumda
          verileriniz yalnızca yukarıdaki amaçlarla ve KVKK'nın 9. maddesinde öngörülen güvencelerden biri
          (yeterlilik kararı veya Kurul'a bildirilen standart sözleşme gibi) sağlanarak aktarılır.
        </p>

        <h2>10. Tarayıcıda saklanan bilgiler</h2>
        <p>
          Oturumunuzun açık kalması için giriş anahtarları tarayıcınızın yerel deposunda (localStorage) tutulur. Reklam
          veya izleme çerezi kullanılmaz.
        </p>

        <h2>11. Verilerin silinmesi, rızanın geri alınması ve hesabın kapatılması</h2>
        <ul>
          <li>Olayları panelinizdeki <b>Olaylar</b> sayfasından tek tek veya tümüyle, cihazları, beyaz liste ve engel listesi kayıtlarını ilgili sayfalardan dilediğiniz zaman silebilirsiniz.</li>
          <li>Aile Plus günlük özet rızanızı <b>Hesabım</b> sayfasından tek tıkla geri alabilirsiniz. Rıza geri alındığı anda yeni sayı tutulmaz ve o ana kadarki günlük özet verileri silinir.</li>
          <li>Hesabınızın kapatılmasını ve tüm verilerinizin silinmesini <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a> adresinden veya WhatsApp hattımızdan isteyebilirsiniz. Talebiniz en geç 30 gün içinde yerine getirilir ve size bildirilir.</li>
          <li>Hesap kapatıldığında hesap, aile, cihaz, beyaz liste ve engel olayı verileri kalıcı olarak silinir. Mevzuat gereği saklanması gereken ödeme kayıtları, yasal süre dolana kadar saklanır.</li>
        </ul>

        <h2>12. Haklarınız ve başvuru</h2>
        <p>
          KVKK'nın 11. maddesi uyarınca kişisel verilerinizin işlenip işlenmediğini öğrenme, bilgi talep etme, düzeltilmesini
          veya silinmesini isteme, aktarıldığı üçüncü kişileri öğrenme, otomatik sistemlerle analiz sonucu aleyhinize bir
          sonuç çıkmasına itiraz etme ve zarar hâlinde tazminat isteme haklarına sahipsiniz. Taleplerinizi, Veri
          Sorumlusuna Başvuru Usul ve Esasları Hakkında Tebliğ uyarınca, kayıtlı e-posta adresinizden{" "}
          <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a> adresine, yazılı olarak yukarıdaki adresimize
          {SELLER.kep ? <> veya KEP adresimiz {SELLER.kep}'e</> : null} iletebilirsiniz. Talebiniz en geç 30 gün içinde
          ücretsiz yanıtlanır. Yanıtı yeterli bulmazsanız Kişisel Verileri Koruma Kurulu'na şikâyette bulunabilirsiniz.
        </p>

        <p className="muted small">
          Sorularınız için <Link to="/iletisim">İletişim</Link> sayfasını kullanabilirsiniz.
        </p>
      </div>
    </section>
  );
}
