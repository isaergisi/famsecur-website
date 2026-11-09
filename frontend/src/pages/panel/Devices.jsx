import { useState } from "react";
import { api, asList, fieldErrors } from "../../api";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import Modal from "../../components/Modal";
import PageHead from "../../components/PageHead";
import Spinner from "../../components/Spinner";
import { useToast } from "../../components/Toast";
import useFetch from "../../components/useFetch";
import { confirmAction } from "../../utils";

const TYPES = { phone: "Telefon", tablet: "Tablet", computer: "Bilgisayar", console: "Oyun konsolu", tv: "Akıllı TV", other: "Diğer" };
const EMPTY = { name: "", device_type: "phone", member_name: "", mac_address: "", is_protected: true };

function DeviceForm({ initial, onClose, onSaved }) {
  const [form, setForm] = useState(initial || EMPTY);
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  async function submit(e) {
    e.preventDefault();
    try {
      const saved = initial ? await api.put(`/devices/${initial.id}/`, form) : await api.post("/devices/", form);
      onSaved(saved, Boolean(initial));
    } catch (err) {
      setErrors(fieldErrors(err));
      setError(err.message);
    }
  }

  return (
    <Modal title={initial ? "Cihazı düzenle" : "Yeni cihaz"} onClose={onClose}>
      <form className="form" onSubmit={submit} noValidate>
        <Alert>{error}</Alert>
        <Field label="Cihaz adı" error={errors.name}>
          <input value={form.name} onChange={set("name")} placeholder="Elif'in tableti" required />
        </Field>
        <div className="form-row">
          <Field label="Tür" error={errors.device_type}>
            <select value={form.device_type} onChange={set("device_type")}>
              {Object.entries(TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </Field>
          <Field label="Kullanan aile üyesi" error={errors.member_name}>
            <input value={form.member_name} onChange={set("member_name")} />
          </Field>
        </div>
        <Field label="MAC adresi (isteğe bağlı)" error={errors.mac_address} hint="Router'ın cihazı tanıması için kullanılır.">
          <input value={form.mac_address} onChange={set("mac_address")} placeholder="AA:BB:CC:DD:EE:FF" />
        </Field>
        <label className="switch">
          <input type="checkbox" checked={form.is_protected} onChange={set("is_protected")} />
          <span>Bu cihazda koruma açık</span>
        </label>
        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose}>Vazgeç</button>
          <button className="btn btn-primary">Kaydet</button>
        </div>
      </form>
    </Modal>
  );
}

export default function Devices() {
  const notify = useToast();
  const { data, error, loading, reload } = useFetch("/devices/");
  const [editing, setEditing] = useState(null); // null: kapalı, {}: yeni, cihaz: düzenle

  async function remove(device) {
    if (!confirmAction(`"${device.name}" silinsin mi? Cihaza ait engel olaylarında cihaz adı görünmeyecek.`)) return;
    try {
      await api.delete(`/devices/${device.id}/`);
      notify("Cihaz silindi.");
      reload();
    } catch (err) {
      notify(err.message, "error");
    }
  }

  async function toggle(device) {
    try {
      await api.patch(`/devices/${device.id}/`, { is_protected: !device.is_protected });
      notify(device.is_protected ? "Koruma kapatıldı." : "Koruma açıldı.");
      reload();
    } catch (err) {
      notify(err.message, "error");
    }
  }

  const devices = asList(data);
  return (
    <>
      <PageHead title="Cihazlar" desc="Ailenizin ağa bağlı cihazlarını yönetin.">
        <button className="btn btn-primary" onClick={() => setEditing({})}>+ Cihaz ekle</button>
      </PageHead>
      {loading && <Spinner />}
      <Alert>{error?.message}</Alert>
      {!loading && devices.length === 0 && <div className="card empty">Henüz cihaz eklemediniz.</div>}
      {devices.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr><th>Cihaz</th><th>Tür</th><th>Kullanan</th><th>Engel</th><th>Koruma</th><th /></tr>
            </thead>
            <tbody>
              {devices.map((d) => (
                <tr key={d.id}>
                  <td><b>{d.name}</b>{d.mac_address && <div className="muted small">{d.mac_address}</div>}</td>
                  <td>{d.device_type_label}</td>
                  <td>{d.member_name || "—"}</td>
                  <td>{d.block_count}</td>
                  <td>
                    <button className={`pill ${d.is_protected ? "pill-on" : "pill-off"}`} onClick={() => toggle(d)}>
                      {d.is_protected ? "Açık" : "Kapalı"}
                    </button>
                  </td>
                  <td className="row-actions">
                    <button className="btn btn-ghost btn-sm" onClick={() => setEditing(d)}>Düzenle</button>
                    <button className="btn btn-danger btn-sm" onClick={() => remove(d)}>Sil</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {editing && (
        <DeviceForm
          initial={editing.id ? editing : null}
          onClose={() => setEditing(null)}
          onSaved={(_, updated) => {
            notify(updated ? "Cihaz güncellendi." : "Cihaz eklendi.");
            setEditing(null);
            reload();
          }}
        />
      )}
    </>
  );
}
