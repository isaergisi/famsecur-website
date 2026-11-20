import { Link } from "react-router-dom";
import usePageTitle from "../../components/usePageTitle";
import { LEGAL_UPDATED, PLANS, PLAN_ORDER, SUPPORT, TL, TRIAL_TERMS } from "../../site";

const PLAN_SCOPE = {
  izleme: "Ağınızda riskli bir siteye girildiğinde bu durum panelinizde raporlanır. Otomatik engel yoktur; yalnızca sizin engel listenize eklediğiniz siteler engellenir. İsteğin hangi cihazdan geldiği gösterilmez.",
  tam: "Zararlı sitelere erişim otomatik engellenir, siteleri elle de engelleyebilirsiniz ve her olayın hangi cihazdan geldiği panelinizde gösterilir. İsterseniz yapay zekâ ile otomatik engeli açabilirsiniz.",
  plus: "Ebeveyn paketinin tüm özelliklerine ek olarak, açık rızanızla ve seçtiğiniz cihazlar için, ağınızda girilen sitelerin günlük özeti sunulur.",
};

export default function Terms() {
  usePageTitle("Kullanım Koşulları");
  return (
    <section className="section page">
      <div className="container narrow legal">
        <span className="eyebrow">Yasal</span>
        <h1>Kullanım Koşulları</h1>
        <p className="muted small">Son güncelleme: {LEGAL_UPDATED}</p>

        <p>
          Bu koşullar, FamSecur aile internet koruma hizmetinin ("Hizmet") kullanımını düzenler. Satın alma ile ilgili
          zorunlu bilgiler ve cayma hakkı <Link to="/mesafeli-satis">Ön Bilgilendirme Formu ve Mesafeli Satış Sözleşmesi</Link>'nde
          yer alır; iki metin arasında fark olursa tüketici lehine olan hüküm uygulanır.
        </p>

        <h2>1. Hizmetin kapsamı ve paketler</h2>
        <p>
          FamSecur, ev ağınıza bağlanan cihazların sitelere yaptığı istekleri DNS düzeyinde, yalnızca sitenin adına
          bakarak inceler. Bir abonelik bir ev ağını kapsar; cihaz sayısında sınır yoktur. Hizmet üç paket hâlinde sunulur:
        </p>
        <ul>
          {PLAN_ORDER.map((id) => (
            <li key={id}>
              <b>{PLANS[id].name}</b> (aylık {TL(PLANS[id].monthly)} TL veya yıllık {TL(PLANS[id].yearly)} TL): {PLAN_SCOPE[id]}
            </li>
          ))}
        </ul>
        <p>
          Paketinizi değiştirmek için destek kanallarımızdan bize ulaşabilirsiniz. Aile Plus paketine geçişte günlük
          özet için açık rızanız ayrıca alınır.
        </p>

        <h2>2. Ücretsiz deneme, ödeme ve yenileme</h2>
        <ul>
          {TRIAL_TERMS.map((t) => <li key={t}>{t}</li>)}
        </ul>

        <h2>3. İptal ve cayma hakkı</h2>
        <p>
          Aboneliğinizi dilediğiniz zaman panelinizdeki <b>Hesabım</b> sayfasından, <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a> adresinden veya{" "}
          <a href={SUPPORT.whatsappLink} target="_blank" rel="noreferrer">{SUPPORT.whatsapp}</a> numaralı WhatsApp
          hattından iptal edebilirsiniz. Deneme süresi içinde iptal ederseniz hiçbir ücret alınmaz. Ücretli dönemde iptal
          ettiğinizde hizmetiniz ödemesi yapılmış dönemin sonuna kadar devam eder; sonraki dönem için ücret alınmaz.
          Kayıt tarihinden itibaren 14 gün içinde gerekçe göstermeden cayabilirsiniz; ayrıntılar Mesafeli Satış
          Sözleşmesi'ndedir.
        </p>

        <h2>4. Hizmetin sınırları</h2>
        <ul>
          <li>Koruma, cihazlar ev ağınıza bağlıyken ve DNS ayarları değiştirilmediği sürece geçerlidir. Mobil veri, VPN, tarayıcıdaki güvenli DNS ayarı veya cihazda elle değiştirilen DNS ayarı korumayı devre dışı bırakabilir.</li>
          <li>Hiçbir filtreleme yöntemi tüm zararlı siteleri yakalayamaz. Listeler her gün güncellense de yeni açılan siteler bir süre listelerde yer almayabilir.</li>
          <li>Yapay zekâ modeli sitenin içeriğini görmez ve yanılabilir. Yapay zekâ ile otomatik engel yalnızca siz açarsanız ve tahmin çok yüksekse uygulanır; yanlış engellenen siteyi beyaz listenize ekleyebilirsiniz.</li>
          <li>FamSecur bir internet erişim sağlayıcısı değildir; internet bağlantınızı aldığınız operatörün sunduğu hizmetlerin (ör. güvenli internet hizmeti) yerine geçmez.</li>
        </ul>

        <h2>5. Kullanıcının sorumlulukları</h2>
        <ul>
          <li>Hesap bilgilerinizin gizliliğinden siz sorumlusunuz.</li>
          <li>Hizmeti yalnızca kendi ev ağınızda ve yasalara uygun şekilde kullanırsınız. Başkasına ait bir ağda veya kişilerin bilgisi dışında onları izlemek amacıyla kullanamazsınız.</li>
          <li>Ebeveyn ve Aile Plus paketlerinde evdeki 18 yaşından büyük kişileri cihaz bazında kayıt tutulduğu konusunda bilgilendirirsiniz. Aile Plus günlük özetine, bilgisi ve onayı olmadan 18 yaşından büyük birinin cihazını dahil etmezsiniz.</li>
          <li>Çocuklarınız adına verdiğiniz onayları, velayet hakkınıza dayanarak ve onların üstün yararını gözeterek verirsiniz.</li>
        </ul>

        <h2>6. Kişisel veriler</h2>
        <p>
          Kişisel verilerinizin nasıl işlendiği <Link to="/gizlilik">KVKK Aydınlatma Metni ve Gizlilik Politikası</Link>'nda,
          Aile Plus günlük özeti için verdiğiniz rıza <Link to="/acik-riza">Açık Rıza Metni</Link>'nde açıklanmıştır.
        </p>

        <h2>7. Değişiklikler</h2>
        <p>
          Bu koşullarda değişiklik yapılması hâlinde güncel metin bu sayfada yayımlanır ve önemli değişiklikler size
          e-postayla bildirilir. Fiyat artışları yürürlüğe girmeden önce bildirilir ve mevcut ödenmiş döneminizi etkilemez.
        </p>

        <h2>8. Uyuşmazlıklar ve iletişim</h2>
        <p>
          Şikâyetleriniz için önce <Link to="/iletisim">İletişim</Link> sayfasından bize ulaşabilirsiniz. Uyuşmazlık
          hâlinde, Ticaret Bakanlığı'nca her yıl ilan edilen parasal sınırlar içinde yerleşim yerinizdeki veya işlemi
          yaptığınız yerdeki tüketici hakem heyetine, bu sınırların üzerinde tüketici mahkemesine başvurabilirsiniz.
        </p>
      </div>
    </section>
  );
}
