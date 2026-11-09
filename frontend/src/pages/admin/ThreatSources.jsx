import { useState } from "react";
import { api, asList, fieldErrors } from "../../api";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import Modal from "../../components/Modal";
import PageHead from "../../components/PageHead";
import Spinner from "../../components/Spinner";
import { useToast } from "../../components/Toast";
import useFetch from "../../components/useFetch";
import { confirmAction, formatDate } from "../../utils";

const CATEGORIES = { gambling: "Kumar / bahis", adult: "Yetişkin içerik", drugs: "Uyuşturucu", phishing: "Dolandırıcılık / phishing", malware: "Kötü amaçlı yazılım" };
const EMPTY = { name: "", category: "phishing", description: "", source_url: "", domains: "", is_active: true };

function SourceForm({ initial, onClose, onSaved }) {
  const [form, setForm] = useState(initial || EMPTY);
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  async function submit(e) {
    e.preventDefault();
    const { name, category, description, source_url, domains, is_active } = form;
    const payload = { name, category, description, source_url, domains, is_active };
    try {
      const saved = initial ? await api.put(`/threat-sources/${initial.id}/`, payload) : await api.post("/threat-sources/", payload);
      onSaved(saved, Boolean(initial));
    } catch (err) {
      setErrors(fieldErrors(err));
      setError(err.message);
    }
  }

  return (
    <Modal title={initial ? "Kaynağı düzenle" : "Yeni tehdit kaynağı"} onClose={onClose}>
      <form className="form" onSubmit={submit} noValidate>
        <Alert>{error}</Alert>
        <div className="form-row">
          <Field label="Ad" error={errors.name}><input value={form.name} onChange={set("name")} /></Field>
          <Field label="Kategori" error={errors.category}>
            <select value={form.category} onChange={set("category")}>
              {Object.entries(CATEGORIES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </Field>
        </div>
        <Field label="Açıklama" error={errors.description}><textarea rows={2} value={form.description} onChange={set("description")} /></Field>
        <Field label="Kaynak adresi" error={errors.source_url}><input value={form.source_url} onChange={set("source_url")} placeholder="https://" /></Field>
        <Field label="Engellenecek alan adları" error={errors.domains} hint="Her satıra bir alan adı. Alt alan adları da engellenir.">
          <textarea rows={6} value={form.domains} onChange={set("domains")} className="mono" />
        </Field>
        <label className="switch"><input type="checkbox" checked={form.is_active} onChange={set("is_active")} /><span>Kaynak aktif</span></label>
        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose}>Vazgeç</button>
          <button className="btn btn-primary">Kaydet</button>
        </div>
      </form>
    </Modal>
  );
}

export default function ThreatSources() {
  const notify = useToast();
  const { data, error, loading, reload } = useFetch("/threat-sources/");
  const [editing, setEditing] = useState(null);

  async function remove(item) {
    if (!confirmAction(`"${item.name}" kaynağı silinsin mi? Listedeki alan adları artık engellenmeyecek.`)) return;
    try {
      await api.delete(`/threat-sources/${item.id}/`);
      notify("Kaynak silindi.");
      reload();
    } catch (err) {
      notify(err.message, "error");
    }
  }

  const items = asList(data);
  return (
    <>
      <PageHead title="Tehdit kaynakları" desc="Aktif kaynaklardaki alan adları tüm ailelerde anında engellenir.">
        <button className="btn btn-primary" onClick={() => setEditing({})}>+ Kaynak ekle</button>
      </PageHead>
      {loading && <Spinner />}
      <Alert>{error?.message}</Alert>
      {items.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead><tr><th>Kaynak</th><th>Kategori</th><th>Alan adı</th><th>Durum</th><th>Güncelleme</th><th /></tr></thead>
            <tbody>
              {items.map((s) => (
                <tr key={s.id}>
                  <td><b>{s.name}</b><div className="muted small truncate">{s.description}</div></td>
                  <td><span className="tag">{s.category_label}</span></td>
                  <td>{s.domain_count}</td>
                  <td><span className={`pill ${s.is_active ? "pill-on" : "pill-off"}`}>{s.is_active ? "Aktif" : "Pasif"}</span></td>
                  <td className="muted small">{formatDate(s.updated_at)}</td>
                  <td className="row-actions">
                    <button className="btn btn-ghost btn-sm" onClick={() => setEditing(s)}>Düzenle</button>
                    <button className="btn btn-danger btn-sm" onClick={() => remove(s)}>Sil</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {!loading && items.length === 0 && <div className="card empty">Kaynak yok.</div>}
      {editing && (
        <SourceForm
          initial={editing.id ? editing : null}
          onClose={() => setEditing(null)}
          onSaved={(_, updated) => {
            notify(updated ? "Kaynak güncellendi." : "Kaynak eklendi.");
            setEditing(null);
            reload();
          }}
        />
      )}
    </>
  );
}
