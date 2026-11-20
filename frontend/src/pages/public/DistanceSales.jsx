import { Link } from "react-router-dom";
import usePageTitle from "../../components/usePageTitle";
import { LEGAL_UPDATED, PLANS, PLAN_ORDER, SELLER, SUPPORT, TL, sellerField } from "../../site";

function Info({ value }) {
  return <span className={value ? "" : "missing"}>{sellerField(value)}</span>;
}

export default function DistanceSales() {
  usePageTitle("Ön Bilgilendirme Formu ve Mesafeli Satış Sözleşmesi");
  return (
    <section className="section page">
      <div className="container narrow legal">
        <span className="eyebrow">Yasal</span>
        <h1>Ön Bilgilendirme Formu ve Mesafeli Satış Sözleşmesi</h1>
        <p className="muted small">Son güncelleme: {LEGAL_UPDATED}</p>
        <p>
          Bu metin, 6502 sayılı Tüketicinin Korunması Hakkında Kanun ve Mesafeli Sözleşmeler Yönetmeliği uyarınca,
          sözleşme kurulmadan önce bilgilendirilmeniz ve sözleşmenin kurulması için hazırlanmıştır. Kayıt ekranında
          onay kutusunu işaretleyerek bu metni onaylarsınız; onaylanan sürüm hesabınızda saklanır ve dilediğiniz zaman
          bu sayfadan görüntülenebilir.
        </p>

        <h2>Bölüm A: Ön bilgilendirme formu</h2>

        <h3>1. Satıcı / hizmet sağlayıcı</h3>
        <ul>
          <li>Unvan: <Info value={SELLER.title} /></li>
          <li>Adres: <Info value={SELLER.address} /></li>
          <li>MERSİS no: <Info value={SELLER.mersis} /></li>
          <li>Vergi dairesi ve no: <Info value={SELLER.taxOffice} /></li>
          <li>Telefon / WhatsApp: {SELLER.phone}</li>
          <li>E-posta: <a href={`mailto:${SELLER.email}`}>{SELLER.email}</a></li>
          {SELLER.kep && <li>KEP: {SELLER.kep}</li>}
        </ul>

        <h3>2. Hizmetin temel nitelikleri</h3>
        <p>
          FamSecur, ev ağınızdaki cihazların alan adı (DNS) sorgularını inceleyerek riskli siteleri raporlayan ve pakete
          göre engelleyen bir abonelik hizmetidir. Bir abonelik bir ev ağını kapsar, cihaz sayısı sınırsızdır.
        </p>

        <h3>3. Fiyatlar (KDV dâhil toplam)</h3>
        <div className="card table-wrap">
          <table className="data-table">
            <thead><tr><th>Paket</th><th>Aylık</th><th>Yıllık</th><th>Kapsam</th></tr></thead>
            <tbody>
              {PLAN_ORDER.map((id) => (
                <tr key={id}>
                  <td data-label="Paket"><b>{PLANS[id].name}</b></td>
                  <td data-label="Aylık">{TL(PLANS[id].monthly)} TL</td>
                  <td data-label="Yıllık">{TL(PLANS[id].yearly)} TL</td>
                  <td data-label="Kapsam">{PLANS[id].short}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p>Fiyatlara KDV dâhildir. Hizmet dijital olarak sunulduğu için teslimat ücreti yoktur.</p>

        <h3>4. Ödeme, deneme ve yenileme</h3>
        <ul>
          <li>İlk 7 gün ücretsizdir. Kart bilgileri ödeme kuruluşu tarafından alınır; deneme süresince ücret çekilmez.</li>
          <li>Deneme sonunda ücretli dönemin başlaması için kayıt ekranında ayrıca onayınız alınır. Deneme bitmeden 2 gün önce e-postayla hatırlatma gönderilir.</li>
          <li><b>Aylık abonelik</b> belirsiz sürelidir; her ay başında o ayın ücreti tahsil edilir ve siz iptal edene kadar devam eder.</li>
          <li><b>Yıllık abonelik</b> bir yıl sürelidir ve kendiliğinden yenilenmez. Bitiminden 30 gün önce hatırlatılır; yeni dönem yalnızca onayınızla başlar.</li>
          <li>Fiyat değişiklikleri yürürlüğe girmeden önce bildirilir ve ödenmiş dönemi etkilemez.</li>
        </ul>

        <h3>5. Hizmetin başlaması</h3>
        <p>Hizmet, kayıt tamamlandığı anda elektronik ortamda başlar ve ebeveyn paneli hemen kullanılabilir.</p>

        <h3>6. Cayma hakkı</h3>
        <ul>
          <li>Sözleşmenin kurulduğu (kayıt) tarihten itibaren 14 gün içinde hiçbir gerekçe göstermeden ve cezai şart ödemeden cayabilirsiniz.</li>
          <li>Cayma bildiriminizi panelinizdeki <b>Hesabım</b> sayfasından aboneliği iptal ederek, <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a> adresine e-postayla veya yukarıdaki adrese yazılı olarak iletebilirsiniz.</li>
          <li>Cayma süresi içinde ödediğiniz bir tutar varsa, bildiriminizin bize ulaştığı tarihten itibaren 14 gün içinde, ödemede kullandığınız yöntemle ve tamamı iade edilir.</li>
        </ul>

        <h3>7. Şikâyet ve itirazlar</h3>
        <p>
          Şikâyetlerinizi yukarıdaki iletişim kanallarından iletebilirsiniz. Uyuşmazlıklarda, Ticaret Bakanlığı'nca
          her yıl ilan edilen parasal sınırlar dâhilinde tüketici hakem heyetlerine, bu sınırların üzerinde tüketici
          mahkemelerine başvurabilirsiniz.
        </p>

        <h2>Bölüm B: Mesafeli satış sözleşmesi</h2>
        <h3>Madde 1. Taraflar</h3>
        <p>
          Bu sözleşme, Bölüm A'da bilgileri yer alan satıcı ("FamSecur") ile kayıt ekranında bilgilerini giren ve bu
          sözleşmeyi onaylayan tüketici ("Abone") arasında elektronik ortamda kurulmuştur.
        </p>
        <h3>Madde 2. Konu</h3>
        <p>
          Sözleşmenin konusu, Abone'nin kayıt sırasında seçtiği paket ve ödeme dönemine göre FamSecur hizmetinin
          sunulması ve bedelinin ödenmesidir. Paket kapsamı, fiyat, ödeme, yenileme ve cayma koşulları Bölüm A'da ve{" "}
          <Link to="/kullanim-kosullari">Kullanım Koşulları</Link>'nda belirtildiği gibidir ve bu sözleşmenin ayrılmaz
          parçasıdır.
        </p>
        <h3>Madde 3. Tarafların yükümlülükleri</h3>
        <ul>
          <li>FamSecur, hizmeti paket kapsamında ve Gizlilik Politikası'na uygun olarak sunar; kesintileri mümkün olan en kısa sürede giderir.</li>
          <li>Abone, hizmeti yalnızca kendi ev ağında ve yasalara uygun kullanır; hesap bilgilerini korur.</li>
        </ul>
        <h3>Madde 4. Fesih</h3>
        <p>
          Abone sözleşmeyi dilediği zaman, kurulduğu yöntemle (panelden tek tıkla) veya e-postayla feshedebilir.
          Fesih ödenmiş dönemin sonunda hüküm doğurur; sonraki dönem için ücret alınmaz. FamSecur fesih bildirimlerini
          kesintisiz alabilecek şekilde bu kanalları açık tutar.
        </p>
        <h3>Madde 5. Yürürlük</h3>
        <p>
          Abone, kayıt ekranında bu metni okuyup onayladığında sözleşme kurulur. Onaylanan metnin sürümü ve onay zamanı
          kaydedilir.
        </p>
      </div>
    </section>
  );
}
