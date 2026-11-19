import { Link } from "react-router-dom";
import usePageTitle from "../../components/usePageTitle";
import { PLANS, SUPPORT, TL } from "../../site";

const UPDATED = "19 Kasım 2026";

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

        <h2>1. Hizmetin kapsamı ve paketler</h2>
        <p>
          FamSecur, ev ağınıza bağlanan cihazların sitelere yaptığı istekleri DNS düzeyinde inceler. Bir abonelik bir
          ev ağını kapsar; cihaz sayısında sınır yoktur. Hizmet iki paket hâlinde sunulur:
        </p>
        <ul>
          <li>
            <b>{PLANS.izleme.name}</b> (aylık {TL(PLANS.izleme.monthly)} TL veya yıllık {TL(PLANS.izleme.yearly)} TL): Ağınızda riskli bir siteye girilmeye
            çalışıldığında bu durum panelinizde raporlanır. Siteler engellenmez ve isteğin hangi cihazdan geldiği
            gösterilmez.
          </li>
          <li>
            <b>{PLANS.tam.name}</b> (aylık {TL(PLANS.tam.monthly)} TL veya yıllık {TL(PLANS.tam.yearly)} TL): Zararlı
            sitelere erişim engellenir ve her engelin hangi cihazdan geldiği panelinizde gösterilir.
          </li>
        </ul>
        <p>Paketinizi değiştirmek için destek kanallarımızdan bize ulaşabilirsiniz.</p>

        <h2>2. Ücretsiz deneme ve abonelik</h2>
        <ul>
          <li>Her iki pakette de deneme süresi 7 gündür ve seçtiğiniz paketin tüm özellikleri açıktır.</li>
          <li>Kayıt sırasında kart bilgileriniz alınır; deneme süresince herhangi bir ücret çekilmez.</li>
          <li>
            Deneme süresi dolmadan iptal etmezseniz seçtiğiniz paketin aylık üyeliği başlar ve aylık ücret
            ({PLANS.izleme.name} için {TL(PLANS.izleme.monthly)} TL, {PLANS.tam.name} için {TL(PLANS.tam.monthly)} TL)
            kartınızdan otomatik olarak tahsil edilir. Üyelik, iptal edilene kadar her ay aynı şekilde yenilenir.
          </li>
          <li>Yıllık ücretler {PLANS.izleme.name} için {TL(PLANS.izleme.yearly)} TL, {PLANS.tam.name} için {TL(PLANS.tam.yearly)} TL'dir. Fiyatlara KDV dâhildir.</li>
        </ul>

        <h2>3. İptal</h2>
        <p>
          Aboneliğinizi dilediğiniz zaman <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a> adresinden veya{" "}
          <a href={SUPPORT.whatsappLink} target="_blank" rel="noreferrer">{SUPPORT.whatsapp}</a> numaralı WhatsApp
          hattından iptal edebilirsiniz. Deneme süresi içinde iptal ederseniz hiçbir ücret alınmaz. Ücretli dönemde iptal
          ettiğinizde hizmetiniz ödemesi yapılmış dönemin sonuna kadar devam eder; sonraki dönem için ücret alınmaz.
        </p>

        <h2>4. Hizmetin sınırları</h2>
        <ul>
          <li>Koruma, cihazlar ev ağınıza bağlıyken ve DNS ayarları değiştirilmediği sürece geçerlidir. Mobil veri, VPN, tarayıcıdaki güvenli DNS ayarı veya cihazda elle değiştirilen DNS ayarı korumayı devre dışı bırakabilir.</li>
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
