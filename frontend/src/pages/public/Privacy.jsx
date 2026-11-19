import { Link } from "react-router-dom";
import usePageTitle from "../../components/usePageTitle";
import { SUPPORT } from "../../site";

const UPDATED = "19 Kasım 2026";

const DATA = [
  ["Hesap bilgileri", "Ad, soyad, e-posta adresi, şifrenin özeti (şifrenin kendisi saklanmaz)", "Hesabın açılması ve oturum yönetimi", "Hesabınız silinene kadar"],
  ["Aile ve cihaz bilgileri", "Aile adı; cihaz adı, türü, kullanan kişinin adı ve isteğe bağlı MAC adresi", "Korumanın cihaz bazında uygulanması", "Siz silene kadar"],
  ["Engel olayları", "Engellenen alan adı, kategori, risk puanı, gerekçe, cihaz ve zaman", "Engellerin panelinizde gösterilmesi ve haftalık özet", "Varsayılan 30 gün; panelden 1-365 gün arasında ayarlanabilir, süresi dolanlar her gün otomatik silinir"],
  ["Beyaz liste", "İzin verdiğiniz alan adları ve notlarınız", "Yanlış engellerin düzeltilmesi", "Siz silene kadar"],
  ["İletişim talepleri", "Ad, e-posta adresi, konu ve mesaj", "Talebinize yanıt verilmesi", "Talebiniz sonuçlanana kadar"],
  ["Ödeme bilgileri", "Kart bilgileri ve abonelik durumu", "Deneme sonrası aylık üyelik ücretinin tahsili", "Kart bilgileri FamSecur sunucularında saklanmaz; ödeme kuruluşunda yasal süre boyunca tutulur"],
];

const NEVER = [
  "Mesajlar, sohbetler, e-postalar",
  "Ekran görüntüleri ve tuş kayıtları",
  "Ziyaret edilen sayfaların içeriği, arama ve izleme geçmişi",
  "İzin verilen sitelerin listesi",
  "DNS kayıtlarında cihazların IP adresleri",
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
            <thead><tr><th>Veri</th><th>İçerik</th><th>Amaç</th><th>Saklama süresi</th></tr></thead>
            <tbody>
              {DATA.map(([name, content, purpose, period]) => (
                <tr key={name}><td><b>{name}</b></td><td>{content}</td><td>{purpose}</td><td className="muted">{period}</td></tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2>3. Hiçbir zaman işlemediğimiz veriler</h2>
        <ul className="check-list">
          {NEVER.map((item) => <li className="no" key={item}>{item}</li>)}
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

        <h2>5. İşlemenin hukuki sebebi</h2>
        <p>
          Verileriniz, KVKK'nın 5. maddesi uyarınca hizmet sözleşmesinin kurulması ve ifası, hukuki yükümlülüklerimizin
          yerine getirilmesi ve hizmetin güvenliğinin sağlanması için meşru menfaatimiz hukuki sebeplerine dayanılarak
          işlenir.
        </p>

        <h2>6. Verilerin aktarılması</h2>
        <p>
          Verileriniz satılmaz ve reklam amacıyla paylaşılmaz. Yalnızca hizmetin çalışması için gerekli olduğu ölçüde
          barındırma hizmeti sağlayıcısına, ödeme kuruluşuna ve DNS yanıtı için üst DNS sunucusuna aktarılır. Kanunen
          yetkili kurumların talepleri saklıdır.
        </p>

        <h2>7. Tarayıcıda saklanan bilgiler</h2>
        <p>
          Oturumunuzun açık kalması için giriş anahtarları tarayıcınızın yerel deposunda (localStorage) tutulur. Reklam
          veya izleme çerezi kullanılmaz.
        </p>

        <h2>8. Haklarınız</h2>
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
