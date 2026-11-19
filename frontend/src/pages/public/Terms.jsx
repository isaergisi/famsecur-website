import { Link } from "react-router-dom";
import usePageTitle from "../../components/usePageTitle";
import { PRICES, SUPPORT } from "../../site";

const UPDATED = "19 Kasım 2026";
const TL = (n) => n.toLocaleString("tr-TR");

export default function Terms() {
  usePageTitle("Kullanım Koşulları");
  return (
    <section className="section page">
      <div className="container narrow legal">
        <span className="eyebrow">Yasal</span>
        <h1>Kullanım Koşulları</h1>
        <p className="muted small">Son güncelleme: {UPDATED}</p>

        <p>
          Bu koşullar, FamSecur aile internet koruma hizmetinin ("Hizmet") kullanımını düzenler. Hesap oluşturarak bu
          koşulları kabul etmiş olursunuz.
        </p>

        <h2>1. Hizmetin kapsamı</h2>
        <p>
          FamSecur, ev ağınıza bağlanan cihazların zararlı sitelere erişimini DNS düzeyinde engeller. Bir abonelik bir ev
          ağını kapsar; cihaz sayısında sınır yoktur.
        </p>

        <h2>2. Ücretsiz deneme ve abonelik</h2>
        <ul>
          <li>Deneme süresi 7 gündür ve tüm özellikler açıktır.</li>
          <li>Kayıt sırasında kart bilgileriniz alınır; deneme süresince herhangi bir ücret çekilmez.</li>
          <li>
            Deneme süresi dolmadan iptal etmezseniz aylık üyeliğiniz başlar ve aylık {TL(PRICES.monthly)} TL ücret
            kartınızdan otomatik olarak tahsil edilir. Üyelik, iptal edilene kadar her ay aynı şekilde yenilenir.
          </li>
          <li>Yıllık paket ücreti {TL(PRICES.yearly)} TL'dir. Fiyatlara KDV dâhildir.</li>
        </ul>

        <h2>3. İptal</h2>
        <p>
          Aboneliğinizi dilediğiniz zaman <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a> adresinden veya{" "}
          <a href={SUPPORT.whatsappLink} target="_blank" rel="noreferrer">{SUPPORT.whatsapp}</a> numaralı WhatsApp
          hattından iptal edebilirsiniz. Deneme süresi içinde iptal ederseniz hiçbir ücret alınmaz.
        </p>

        <h2>4. Hizmetin sınırları</h2>
        <ul>
          <li>Koruma, cihazlar ev ağınıza bağlıyken geçerlidir. Mobil veri, VPN veya tarayıcıdaki güvenli DNS ayarıyla bağlanan cihazlar korumanın dışında kalabilir.</li>
          <li>Hiçbir filtreleme yöntemi tüm zararlı siteleri yakalayamaz. Listeler her gün güncellense de yeni açılan siteler bir süre listelerde yer almayabilir.</li>
          <li>Yapay zekâ modeli yalnızca uyarı verir; tahminleri yanılabilir ve engelleme kararı yerine geçmez.</li>
          <li>Masum bir site yanlışlıkla engellenebilir; bu durumda siteyi beyaz listenize ekleyebilirsiniz.</li>
        </ul>

        <h2>5. Kullanıcının sorumlulukları</h2>
        <p>
          Hesap bilgilerinizin gizliliğinden siz sorumlusunuz. Hizmeti yalnızca kendi ev ağınızda ve yasalara uygun
          şekilde kullanmayı kabul edersiniz.
        </p>

        <h2>6. Kişisel veriler</h2>
        <p>
          Kişisel verilerinizin nasıl işlendiği <Link to="/gizlilik">Gizlilik Politikası</Link>'nda açıklanmıştır.
        </p>

        <h2>7. Değişiklikler</h2>
        <p>
          Bu koşullarda değişiklik yapılması hâlinde güncel metin bu sayfada yayımlanır ve önemli değişiklikler size
          e-postayla bildirilir.
        </p>

        <h2>8. İletişim</h2>
        <p>
          Sorularınız için <Link to="/iletisim">İletişim</Link> sayfasından bize ulaşabilirsiniz.
        </p>
      </div>
    </section>
  );
}
