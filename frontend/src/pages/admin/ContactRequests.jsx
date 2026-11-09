import { useState } from "react";
import { api, asList } from "../../api";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import Modal from "../../components/Modal";
import PageHead from "../../components/PageHead";
import Pagination from "../../components/Pagination";
import Spinner from "../../components/Spinner";
import { useToast } from "../../components/Toast";
import useFetch from "../../components/useFetch";
import { confirmAction, formatDate } from "../../utils";

const STATUSES = { new: "Yeni", in_progress: "İnceleniyor", resolved: "Çözüldü" };

export default function ContactRequests() {
  const notify = useToast();
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const { data, error, loading, reload } = useFetch(`/contact-requests/?${new URLSearchParams({ page, status })}`);
  const [selected, setSelected] = useState(null);

  async function save(e) {
    e.preventDefault();
    try {
      await api.patch(`/contact-requests/${selected.id}/`, { status: selected.status, admin_note: selected.admin_note });
      notify("Talep güncellendi.");
      setSelected(null);
      reload();
    } catch (err) {
      notify(err.message, "error");
    }
  }

  async function remove(item) {
    if (!confirmAction(`${item.name} kişisinin talebi silinsin mi?`)) return;
    try {
      await api.delete(`/contact-requests/${item.id}/`);
      notify("Talep silindi.");
      reload();
    } catch (err) {
      notify(err.message, "error");
    }
  }

  const items = asList(data);
  return (
    <>
      <PageHead title="İletişim talepleri" desc="Sitedeki iletişim formundan gelen demo ve destek talepleri." />
      <div className="toolbar">
        <select value={status} onChange={(e) => { setPage(1); setStatus(e.target.value); }} aria-label="Durum">
          <option value="">Tüm durumlar</option>
          {Object.entries(STATUSES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </div>
      {loading && <Spinner />}
      <Alert>{error?.message}</Alert>
      {!loading && items.length === 0 && <div className="card empty">Talep yok.</div>}
      {items.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead><tr><th>Gönderen</th><th>Konu</th><th>Mesaj</th><th>Durum</th><th>Tarih</th><th /></tr></thead>
            <tbody>
              {items.map((c) => (
                <tr key={c.id}>
                  <td><b>{c.name}</b><div className="muted small">{c.email}</div></td>
                  <td>{c.topic_label}</td>
                  <td className="truncate">{c.message}</td>
                  <td><span className={`pill status-${c.status}`}>{c.status_label}</span></td>
                  <td className="muted small">{formatDate(c.created_at)}</td>
                  <td className="row-actions">
                    <button className="btn btn-ghost btn-sm" onClick={() => setSelected(c)}>Aç</button>
                    <button className="btn btn-danger btn-sm" onClick={() => remove(c)}>Sil</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Pagination data={data} page={page} setPage={setPage} />
      {selected && (
        <Modal title={`${selected.name} · ${selected.topic_label}`} onClose={() => setSelected(null)}>
          <form className="form" onSubmit={save}>
            <p className="muted small"><a href={`mailto:${selected.email}`}>{selected.email}</a> · {formatDate(selected.created_at)}</p>
            <blockquote className="quote">{selected.message}</blockquote>
            <Field label="Durum">
              <select value={selected.status} onChange={(e) => setSelected({ ...selected, status: e.target.value })}>
                {Object.entries(STATUSES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </Field>
            <Field label="Yönetici notu">
              <textarea rows={3} value={selected.admin_note} onChange={(e) => setSelected({ ...selected, admin_note: e.target.value })} />
            </Field>
            <div className="modal-actions">
              <button type="button" className="btn btn-ghost" onClick={() => setSelected(null)}>Kapat</button>
              <button className="btn btn-primary">Kaydet</button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}
