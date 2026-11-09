import { Fragment, useState } from "react";
import { api, asList } from "../../api";
import Alert from "../../components/Alert";
import PageHead from "../../components/PageHead";
import Pagination from "../../components/Pagination";
import Spinner from "../../components/Spinner";
import { useToast } from "../../components/Toast";
import useFetch from "../../components/useFetch";
import { confirmAction, formatDate } from "../../utils";

const CATEGORIES = { gambling: "Kumar / bahis", adult: "Yetişkin içerik", drugs: "Uyuşturucu", phishing: "Dolandırıcılık / phishing", malware: "Kötü amaçlı yazılım" };

export default function Events() {
  const notify = useToast();
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ category: "", device: "", search: "" });
  const query = new URLSearchParams({ page, ...filters }).toString();
  const { data, error, loading, reload } = useFetch(`/events/?${query}`);
  const devices = useFetch("/devices/");
  const [open, setOpen] = useState(null);
  const setFilter = (key) => (e) => {
    setPage(1);
    setFilters({ ...filters, [key]: e.target.value });
  };

  async function remove(event) {
    try {
      await api.delete(`/events/${event.id}/`);
      notify("Olay silindi.");
      reload();
    } catch (err) {
      notify(err.message, "error");
    }
  }

  async function clearAll() {
    if (!confirmAction("Tüm engel olayları kalıcı olarak silinsin mi?")) return;
    try {
      const res = await api.delete("/events/clear/");
      notify(res.detail);
      setPage(1);
      reload();
    } catch (err) {
      notify(err.message, "error");
    }
  }

  const events = asList(data);
  return (
    <>
      <PageHead title="Engel olayları" desc="Yalnızca engellenen istekler kaydedilir. İzin verilen trafik hiçbir yerde tutulmaz.">
        <button className="btn btn-danger" onClick={clearAll} disabled={!data?.count}>Tümünü temizle</button>
      </PageHead>
      <div className="toolbar">
        <input type="search" placeholder="Alan adı ara…" value={filters.search} onChange={setFilter("search")} aria-label="Ara" />
        <select value={filters.category} onChange={setFilter("category")} aria-label="Kategori">
          <option value="">Tüm kategoriler</option>
          {Object.entries(CATEGORIES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <select value={filters.device} onChange={setFilter("device")} aria-label="Cihaz">
          <option value="">Tüm cihazlar</option>
          {asList(devices.data).map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
      </div>
      {loading && <Spinner />}
      <Alert>{error?.message}</Alert>
      {!loading && events.length === 0 && <div className="card empty">Bu filtrelerle eşleşen olay yok.</div>}
      {events.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead><tr><th>Alan adı</th><th>Kategori</th><th>Puan</th><th>Cihaz</th><th>Zaman</th><th /></tr></thead>
            <tbody>
              {events.map((e) => (
                <Fragment key={e.id}>
                  <tr>
                    <td><code>{e.domain}</code></td>
                    <td><span className="tag">{e.category_label}</span></td>
                    <td><b>{e.score}</b></td>
                    <td>{e.device_name || <span className="muted">—</span>}</td>
                    <td className="muted small">{formatDate(e.created_at)}</td>
                    <td className="row-actions">
                      <button className="btn btn-ghost btn-sm" onClick={() => setOpen(open === e.id ? null : e.id)}>Neden?</button>
                      <button className="btn btn-danger btn-sm" onClick={() => remove(e)}>Sil</button>
                    </td>
                  </tr>
                  {open === e.id && (
                    <tr className="detail-row">
                      <td colSpan={6}>
                        <ul className="reasons">{e.reasons.map((r) => <li key={r}>{r}</li>)}</ul>
                        <span className="muted small">Uygulanan biçim: {e.enforcement_mode === "silent" ? "Sessiz engel" : "Uyarı sayfası"}</span>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Pagination data={data} page={page} setPage={setPage} />
    </>
  );
}
