import { useEffect, useState } from "react";
import Alert from "../../components/Alert";
import PageHead from "../../components/PageHead";
import Spinner from "../../components/Spinner";
import useFetch from "../../components/useFetch";
import { CATEGORY_LABELS } from "../../utils";

const CATEGORIES = CATEGORY_LABELS;

// 1 … 4 5 [6] 7 8 … 726 biçiminde sayfa numaraları
function pageNumbers(current, total) {
  const pages = new Set([1, total]);
  for (let p = current - 2; p <= current + 2; p++) if (p > 0 && p <= total) pages.add(p);
  const sorted = [...pages].sort((a, b) => a - b);
  const out = [];
  sorted.forEach((p, i) => {
    if (i > 0 && p - sorted[i - 1] > 1) out.push("…" + p);
    out.push(p);
  });
  return out;
}

function NumberedPagination({ page, total, setPage }) {
  if (total <= 1) return null;
  return (
    <nav className="pagination numbered" aria-label="Sayfalar">
      <button className="btn btn-ghost btn-sm" disabled={page === 1} onClick={() => setPage(page - 1)}>‹</button>
      {pageNumbers(page, total).map((p) =>
        typeof p === "string" ? (
          <span key={p} className="muted small">…</span>
        ) : (
          <button key={p} className={`btn btn-sm ${p === page ? "btn-primary" : "btn-ghost"}`} onClick={() => setPage(p)} aria-current={p === page ? "page" : undefined}>
            {p}
          </button>
        )
      )}
      <button className="btn btn-ghost btn-sm" disabled={page === total} onClick={() => setPage(page + 1)}>›</button>
    </nav>
  );
}

// Arama + filtre + numaralı sayfalı tablo. Yönetim paneli ve ebeveyn paneli (salt okunur) birlikte kullanır.
export function BlockedDomainsBrowser({ path = "/admin/blocked-domains/" }) {
  const [page, setPage] = useState(1);
  const [input, setInput] = useState("");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [source, setSource] = useState("");

  // Yazmayı bitirince ara (her tuşta sunucuya gitmemek için)
  useEffect(() => {
    const t = setTimeout(() => { setPage(1); setSearch(input.trim()); }, 350);
    return () => clearTimeout(t);
  }, [input]);

  const { data, error, loading } = useFetch(`${path}?${new URLSearchParams({ page, search, category, source })}`);
  const rows = data?.results ?? [];
  const total = data ? Math.max(1, Math.ceil(data.count / data.page_size)) : 1;
  const start = data ? (page - 1) * data.page_size + 1 : 0;

  return (
    <>
      <div className="toolbar">
        <input type="search" placeholder="Alan adı ara…" value={input} onChange={(e) => setInput(e.target.value)} aria-label="Alan adı ara" />
        <select value={category} onChange={(e) => { setPage(1); setCategory(e.target.value); }} aria-label="Kategori">
          <option value="">Tüm kategoriler</option>
          {Object.entries(CATEGORIES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select value={source} onChange={(e) => { setPage(1); setSource(e.target.value); }} aria-label="Kaynak">
          <option value="">Tüm kaynaklar</option>
          {(data?.sources ?? []).map((s) => <option key={s.name} value={s.name}>{s.name} ({s.count.toLocaleString("tr-TR")})</option>)}
        </select>
      </div>
      <Alert>{error?.message}</Alert>
      {data && (
        <p className="muted small">
          {data.count === 0
            ? "Sonuç bulunamadı."
            : `Toplam ${data.count.toLocaleString("tr-TR")} kayıt · ${start.toLocaleString("tr-TR")}–${Math.min(start + rows.length - 1, data.count).toLocaleString("tr-TR")} arası gösteriliyor`}
        </p>
      )}
      {loading && !data && <Spinner />}
      {rows.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead><tr><th>#</th><th>Alan adı</th><th>Kategori</th><th>Kaynak</th></tr></thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={`${r.source}-${r.domain}`}>
                  <td className="muted small">{(start + i).toLocaleString("tr-TR")}</td>
                  <td><code>{r.domain}</code></td>
                  <td><span className="tag">{r.category_label}</span></td>
                  <td className="small">{r.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <NumberedPagination page={page} total={total} setPage={setPage} />
    </>
  );
}

export default function BlockedDomains() {
  return (
    <>
      <PageHead
        title="Engellenen alan adları"
        desc="Karar motorunun listelerden doğrudan engellediği alan adları: resmî kumar havuzu ve aktif tehdit kaynakları."
      />
      <BlockedDomainsBrowser />
    </>
  );
}
