import { Link } from "react-router-dom";
import usePageTitle from "../../components/usePageTitle";
import { LEGAL_UPDATED, PLANS, SELLER, sellerField } from "../../site";

export default function ExplicitConsent() {
  usePageTitle("Aile Plus Açık Rıza Metni");
  return (
    <section className="section page">
      <div className="container narrow legal">
        <span className="eyebrow">Yasal</span>
        <h1>{PLANS.plus.name} Açık Rıza Metni</h1>
        <p className="muted small">Son güncelleme: {LEGAL_UPDATED}</p>
        <p>
          Bu metin, yalnızca {PLANS.plus.name} paketindeki <b>günlük özet</b> özelliği içindir. Diğer tüm işlemler{" "}
          <Link to="/gizlilik">KVKK Aydınlatma Metni</Link>'nde açıklanan hukuki sebeplere dayanır ve rıza gerektirmez.
          Bu rızayı vermek zorunda değilsiniz; vermezseniz {PLANS.tam.name} paketini kullanabilirsiniz.
        </p>

        <h2>Hangi veri işlenir?</h2>
        <ul>
          <li>Günlük özete dahil ettiğiniz cihazların sorguladığı sitelerin kayıtlı adı (ör. <code>youtube.com</code>; <code>m.youtube.com</code> gibi alt adresler tek sitede toplanır).</li>
          <li>Her site için gün içinde kaç kez sorgulandığı ve bunun kaçının gece 00.00-06.00 arasında olduğu.</li>
          <li>Sorgunun hangi cihazdan geldiği (cihaz adıyla).</li>
        </ul>
        <p>
          Tam sayfa adresi, sayfa içeriği, arama terimleri, mesajlar, saat saat liste veya ham DNS kaydı{" "}
          <b>işlenmez</b>. Cihazların arka planda kendiliğinden sorduğu adresler (güncelleme, reklam, içerik dağıtım
          ağları) sayılmaz.
        </p>

        <h2>Amaç</h2>
        <p>Ev ağınızdaki internet kullanımının size her gün özet olarak sunulması.</p>

        <h2>Kimin verisi, kim adına rıza?</h2>
        <ul>
          <li>Kendi cihazlarınız için rızayı kendiniz verirsiniz.</li>
          <li>18 yaşından küçük çocuklarınızın cihazları için rızayı, velayet hakkına sahip yasal temsilcileri olarak siz verirsiniz.</li>
          <li>Evdeki 18 yaşından büyük kişilerin cihazlarını yalnızca onların bilgisi ve onayıyla özete dahil edebilirsiniz. Cihazlar sayfasından her cihazı özetten çıkarabilirsiniz.</li>
        </ul>

        <h2>Saklama süresi</h2>
        <p>Günlük sayılar 30 gün saklanır, ardından otomatik silinir.</p>

        <h2>Aktarım</h2>
        <p>
          Özet verileri yalnızca FamSecur'un barındırma hizmeti sağlayıcısının sunucularında tutulur; reklam, analiz
          veya başka bir amaçla üçüncü kişilerle paylaşılmaz, harici bir yapay zekâ hizmetine gönderilmez.
        </p>

        <h2>Rızanın geri alınması</h2>
        <p>
          Rızanızı panelinizdeki <b>Hesabım</b> sayfasından dilediğiniz an tek tıkla geri alabilirsiniz. Geri aldığınız
          anda yeni sayı tutulmaz ve o ana kadarki günlük özet verileri silinir. Paketinizin diğer özellikleri çalışmaya
          devam eder.
        </p>

        <h2>Veri sorumlusu</h2>
        <p>
          <span className={SELLER.title ? "" : "missing"}>{sellerField(SELLER.title)}</span> · {SELLER.email}. KVKK m.
          11'deki haklarınız ve başvuru yolları <Link to="/gizlilik">Aydınlatma Metni</Link>'nde yer alır.
        </p>

        <h2>Rıza beyanı</h2>
        <blockquote className="legal-quote">
          {PLANS.plus.name} Açık Rıza Metni'ni okudum. Ev ağımdaki cihazların girdiği sitelerin günlük özetinin
          çıkarılmasına kendim için ve çocuklarım adına yasal temsilcileri olarak açık rıza veriyorum. Bu rızayı panelden
          dilediğim an geri alabileceğimi biliyorum.
        </blockquote>
      </div>
    </section>
  );
}
