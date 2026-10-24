import { useState } from "react";
import { api, asList, fieldErrors } from "../../api";
import { useAuth } from "../../auth";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import Modal from "../../components/Modal";
import PageHead from "../../components/PageHead";
import Pagination from "../../components/Pagination";
import Spinner from "../../components/Spinner";
import { useToast } from "../../components/Toast";
import useFetch from "../../components/useFetch";
import { confirmAction, formatDate } from "../../utils";

const EMPTY = { email: "", first_name: "", last_name: "", role: "parent", is_active: true, password: "" };

function UserForm({ initial, onClose, onSaved }) {
  const [form, setForm] = useState(initial ? { ...initial, password: "" } : EMPTY);
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  async function submit(e) {
    e.preventDefault();
    const payload = { email: form.email, first_name: form.first_name, last_name: form.last_name, role: form.role, is_active: form.is_active };
    if (form.password) payload.password = form.password;
    try {
      const saved = initial ? await api.patch(`/admin/users/${initial.id}/`, payload) : await api.post("/admin/users/", payload);
      onSaved(saved, Boolean(initial));
    } catch (err) {
      setErrors(fieldErrors(err));
      setError(err.message);
    }
  }

  return (
    <Modal title={initial ? "Kullanıcıyı düzenle" : "Yeni kullanıcı"} onClose={onClose}>
      <form className="form" onSubmit={submit} noValidate>
        <Alert>{error}</Alert>
        <Field label="E-posta" error={errors.email}><input type="email" value={form.email} onChange={set("email")} /></Field>
        <div className="form-row">
          <Field label="Ad" error={errors.first_name}><input value={form.first_name} onChange={set("first_name")} /></Field>
          <Field label="Soyad" error={errors.last_name}><input value={form.last_name} onChange={set("last_name")} /></Field>
        </div>
        <div className="form-row">
          <Field label="Rol" error={errors.role}>
            <select value={form.role} onChange={set("role")}>
              <option value="parent">Ebeveyn</option>
              <option value="admin">Yönetici</option>
            </select>
          </Field>
          <Field label={initial ? "Yeni şifre (boş bırakılabilir)" : "Şifre"} error={errors.password}>
            <input type="password" autoComplete="new-password" value={form.password} onChange={set("password")} />
          </Field>
        </div>
        <label className="switch"><input type="checkbox" checked={form.is_active} onChange={set("is_active")} /><span>Hesap aktif</span></label>
        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose}>Vazgeç</button>
          <button className="btn btn-primary">Kaydet</button>
        </div>
      </form>
    </Modal>
  );
}

export default function Users() {
  const { user: me } = useAuth();
  const notify = useToast();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("");
  const { data, error, loading, reload } = useFetch(`/admin/users/?${new URLSearchParams({ page, search, role })}`);
  const [editing, setEditing] = useState(null);

  async function remove(u) {
    if (!confirmAction(`${u.email} ve bu kullanıcının tüm aile verileri kalıcı olarak silinsin mi?`)) return;
    try {
      await api.delete(`/admin/users/${u.id}/`);
      notify("Kullanıcı silindi.");
      reload();
    } catch (err) {
      notify(err.message, "error");
    }
  }

  const users = asList(data);
  return (
    <>
      <PageHead title="Kullanıcılar" desc={`${data?.count ?? 0} kayıtlı kullanıcı`}>
        <button className="btn btn-primary" onClick={() => setEditing({})}>+ Kullanıcı ekle</button>
      </PageHead>
      <div className="toolbar">
        <input type="search" placeholder="E-posta veya ad ara…" value={search} onChange={(e) => { setPage(1); setSearch(e.target.value); }} aria-label="Ara" />
        <select value={role} onChange={(e) => { setPage(1); setRole(e.target.value); }} aria-label="Rol">
          <option value="">Tüm roller</option>
          <option value="parent">Ebeveyn</option>
          <option value="admin">Yönetici</option>
        </select>
      </div>
      {loading && <Spinner />}
      <Alert>{error?.message}</Alert>
      {users.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead><tr><th>Kullanıcı</th><th>Rol</th><th>Aile</th><th>Cihaz</th><th>Durum</th><th>Kayıt</th><th /></tr></thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td><b>{u.first_name} {u.last_name}</b><div className="muted small">{u.email}</div></td>
                  <td><span className={`tag ${u.role === "admin" ? "tag-blue" : ""}`}>{u.role === "admin" ? "Yönetici" : "Ebeveyn"}</span></td>
                  <td>{u.family_name || "—"}</td>
                  <td>{u.device_count}</td>
                  <td><span className={`pill ${u.is_active ? "pill-on" : "pill-off"}`}>{u.is_active ? "Aktif" : "Pasif"}</span></td>
                  <td className="muted small">{formatDate(u.date_joined)}</td>
                  <td className="row-actions">
                    <button className="btn btn-ghost btn-sm" onClick={() => setEditing(u)}>Düzenle</button>
                    {u.id !== me.id && <button className="btn btn-danger btn-sm" onClick={() => remove(u)}>Sil</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {!loading && users.length === 0 && <div className="card empty">Kullanıcı bulunamadı.</div>}
      <Pagination data={data} page={page} setPage={setPage} />
      {editing && (
        <UserForm
          initial={editing.id ? editing : null}
          onClose={() => setEditing(null)}
          onSaved={(_, updated) => {
            notify(updated ? "Kullanıcı güncellendi." : "Kullanıcı oluşturuldu.");
            setEditing(null);
            reload();
          }}
        />
      )}
    </>
  );
}
