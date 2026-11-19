import { asList } from "../../api";
import Alert from "../../components/Alert";
import PageHead from "../../components/PageHead";
import Spinner from "../../components/Spinner";
import useFetch from "../../components/useFetch";
import { formatDate } from "../../utils";
import { BlockedDomainsBrowser } from "../admin/BlockedDomains";

// Koruma listelerindeki önemli gelişmeler. Yeni kaynak veya özellik eklendikçe başa yeni satır eklenir.
const MILESTONES = [
  { date: "2026-11-19", title: "UT1 Kara Listeleri eklendi", text: "Toulouse Capitole Üniversitesi'nin kumar, uyuşturucu, oltalama ve zararlı yazılım listeleri korumaya katıldı." },
  { date: "2026-11-19", title: "Listeler kaynağından güncelleniyor", text: "Listeler artık doğrudan yayımlandıkları adreslerden yenileniyor; her güncelleme bu sayfada tarihiyle görünür." },
  { date: "2026-11-19", title: "USOM resmî API'ye bağlandı", text: "T.C. Siber Güvenlik Başkanlığı'nın yayımladığı oltalama bağlantıları doğrudan alınıyor." },
  { date: "2026-07-23", title: "Resmî kumar alan adı havuzu", text: "Polonya Maliye Bakanlığı'nın yasa dışı kumar sicili (36.282 alan adı) ile koruma başladı." },
];

function Updates({ sources }) {
  const live = sources
    .filter((s) => s.last_fetched_at)
    .map((s) => ({
      date: s.last_fetched_at,
      title: `${s.name} güncellendi`,
      text: `${(s.last_fetch_count ?? 0).toLocaleString("tr-TR")} alan adı denetlendi ve listeye işlendi.`,
      live: true,
    }));
  const items = [...live, ...MILESTONES].sort((a, b) => new Date(b.date) - new Date(a.date));
  return (
    <div className="card">
      <h3>Güncellemeler ve yenilikler</h3>
      <p className="muted small">FamSecur'un koruma listeleri büyümeye devam ediyor: yeni kaynaklar ekleniyor, mevcut listeler güncelleniyor.</p>
      <ul className="timeline">
        {items.map((item, i) => (
          <li key={i}>
            <span className="muted small">
              {item.live ? `${formatDate(item.date)} · otomatik güncelleme` : new Date(item.date).toLocaleDateString("tr-TR", { dateStyle: "medium" })}
            </span>
            <b>{item.title}</b>
            <span className="small">{item.text}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function ProtectionLists() {
  const { data, error, loading } = useFetch("/threat-sources/");
  const sources = asList(data);
  const total = sources.reduce((sum, s) => sum + (s.domain_count || 0), 0);

  return (
    <>
      <PageHead
        title="Koruma listeleri"
        desc="Ailenizi koruyan güvenilir kaynaklar ve engellenen alan adları. Bu sayfa bilgilendirme amaçlıdır; listeler FamSecur tarafından yönetilir."
      />
      {loading && <Spinner />}
      <Alert>{error?.message}</Alert>
      {sources.length > 0 && (
        <>
          <p className="muted small">Toplam {total.toLocaleString("tr-TR")} alan adı, {sources.length} kaynaktan.</p>
          <div className="source-cards">
            {sources.map((s) => (
              <div className="card" key={s.id}>
                <span className="tag">{s.category_label}</span>
                <h3>{s.name}</h3>
                <p className="muted small">{s.description}</p>
                <p className="small">
                  <b>{(s.domain_count || 0).toLocaleString("tr-TR")}</b> alan adı
                  {" · "}
                  {s.last_fetched_at ? `Son güncelleme: ${formatDate(s.last_fetched_at)}` : s.auto_update ? "Otomatik güncelleniyor" : "Elle yönetiliyor"}
                </p>
              </div>
            ))}
          </div>
          <Updates sources={sources} />
        </>
      )}
      <h2 className="section-title">Engellenen alan adları</h2>
      <BlockedDomainsBrowser path="/blocked-domains/" />
    </>
  );
}
