import { useState } from "react";
import { api, asList, fieldErrors } from "../../api";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import PageHead from "../../components/PageHead";
import Spinner from "../../components/Spinner";
import { useToast } from "../../components/Toast";
import useFetch from "../../components/useFetch";
import { confirmAction, formatDate } from "../../utils";

export default function Blocklist() {
  const notify = useToast();
  const [search, setSearch] = useState("");
  const { data, error, loading, reload } = useFetch(`/blocklist/?search=${encodeURIComponent(search)}`);
  const [form, setForm] = useState({ domain: "", note: "" });
  const [errors, setErrors] = useState({});
  const [editId, setEditId] = useState(null);
  const [editNote, setEditNote] = useState("");

  async function add(e) {
    e.preventDefault();
    setErrors({});
    try {
      const entry = await api.post("/blocklist/", form);
      notify(`${entry.domain} engel listenize eklendi.`);
      setForm({ domain: "", note: "" });
      reload();
    } catch (err) {
      setErrors({ ...fieldErrors(err), _: err.message });
    }
  }

  async function saveNote(entry) {
    try {
      await api.patch(`/blocklist/${entry.id}/`, { note: editNote });
      setEditId(null);
      notify("Not güncellendi.");
      reload();
    } catch (err) {
      notify(err.message, "error");
    }
  }

  async function remove(entry) {
    if (!confirmAction(`${entry.domain} engel listenizden çıkarılsın mı?`)) return;
    try {
      await api.delete(`/blocklist/${entry.id}/`);
      notify("Kayıt silindi.");
      reload();
    } catch (err) {
      notify(err.message, "error");
    }
  }

  const entries = asList(data);
  return (
    <>
      <PageHead
        title="Engel listem"
        desc="Buraya eklediğiniz siteler her pakette engellenir; alt alan adları da engellenir. Beyaz listenizdeki siteler her zaman önceliklidir."
      />
      <form className="card form" onSubmit={add} noValidate>
        {errors._ && !errors.domain && <Alert>{errors._}</Alert>}
        <div className="form-row">
          <Field label="Alan adı" error={errors.domain}>
            <input value={form.domain} onChange={(e) => setForm({ ...form, domain: e.target.value })} placeholder="ornek.com veya https://ornek.com" required />
          </Field>
          <Field label="Not" error={errors.note}>
            <input value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} placeholder="Neden engellendi?" />
          </Field>
        </div>
        <button className="btn btn-primary">Engel listesine ekle</button>
      </form>

      <div className="toolbar">
        <input type="search" placeholder="Alan adı ara…" value={search} onChange={(e) => setSearch(e.target.value)} aria-label="Ara" />
      </div>
      {loading && <Spinner />}
      <Alert>{error?.message}</Alert>
      {!loading && entries.length === 0 && <div className="card empty">Engel listenizde site yok. Olaylar sayfasındaki "Engelle" düğmesiyle de ekleyebilirsiniz.</div>}
      {entries.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead><tr><th>Alan adı</th><th>Not</th><th>Eklenme</th><th /></tr></thead>
            <tbody>
              {entries.map((w) => (
                <tr key={w.id}>
                  <td><code>{w.domain}</code></td>
                  <td>
                    {editId === w.id ? (
                      <div className="inline-form">
                        <input value={editNote} onChange={(e) => setEditNote(e.target.value)} aria-label="Not" />
                        <button className="btn btn-primary btn-sm" onClick={() => saveNote(w)}>Kaydet</button>
                      </div>
                    ) : (
                      w.note || <span className="muted">—</span>
                    )}
                  </td>
                  <td className="muted small">{formatDate(w.created_at)}</td>
                  <td className="row-actions">
                    <button className="btn btn-ghost btn-sm" onClick={() => { setEditId(w.id); setEditNote(w.note); }}>Notu düzenle</button>
                    <button className="btn btn-danger btn-sm" onClick={() => remove(w)}>Sil</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
