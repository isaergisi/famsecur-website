import { useEffect, useState } from "react";
import { api, fieldErrors } from "../../api";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import PageHead from "../../components/PageHead";
import Spinner from "../../components/Spinner";
import { useToast } from "../../components/Toast";
import useFetch from "../../components/useFetch";
import { formatDate } from "../../utils";

const LOCKED = ["phishing", "malware"];

export default function PolicyPage() {
  const notify = useToast();
  const { data, setData, error, loading } = useFetch("/policy/");
  const [form, setForm] = useState(null);
  const [errors, setErrors] = useState({});
  const [saveError, setSaveError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (data) setForm(data);
  }, [data]);

  if (loading || (!form && !error)) return <Spinner />;
  if (error) return <Alert>{error.message}</Alert>;

  const toggleCategory = (key) =>
    setForm({
      ...form,
      enabled_categories: form.enabled_categories.includes(key)
        ? form.enabled_categories.filter((c) => c !== key)
        : [...form.enabled_categories, key],
    });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setErrors({});
    setSaveError("");
    try {
      const { risk_threshold, enforcement_mode, enabled_categories, retention_days } = form;
      setData(await api.put("/policy/", { risk_threshold: Number(risk_threshold), enforcement_mode, enabled_categories, retention_days: Number(retention_days) }));
      notify("Politika kaydedildi. Yeni kurallar hemen uygulanır.");
    } catch (err) {
      setErrors(fieldErrors(err));
      setSaveError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const strictness = form.risk_threshold <= 50 ? "Sıkı" : form.risk_threshold <= 80 ? "Dengeli" : "Esnek";
  return (
    <>
      <PageHead title="Koruma politikası" desc={`Son güncelleme: ${formatDate(data.updated_at)}`} />
      <form className="card form" onSubmit={submit}>
        <Alert>{saveError}</Alert>
        <Field label={`Risk eşiği: ${form.risk_threshold} (${strictness})`} error={errors.risk_threshold} hint="Puanı bu değere eşit veya üstünde olan alan adları engellenir. Düşük eşik daha sıkı korur.">
          <input type="range" min="30" max="100" step="5" value={form.risk_threshold} onChange={(e) => setForm({ ...form, risk_threshold: Number(e.target.value) })} />
        </Field>

        <fieldset className="field">
          <span className="field-label">Engelleme biçimi</span>
          <div className="radio-cards">
            {[
              ["silent", "Sessiz engel", "Site hiç açılmaz; cihaz bağlantı hatası görür."],
              ["warning", "Uyarı sayfası", "Cihaz, engelin nedenini açıklayan FamSecur sayfasına yönlenir."],
            ].map(([value, title, text]) => (
              <label key={value} className={`radio-card ${form.enforcement_mode === value ? "active" : ""}`}>
                <input type="radio" name="mode" value={value} checked={form.enforcement_mode === value} onChange={() => setForm({ ...form, enforcement_mode: value })} />
                <b>{title}</b>
                <span className="muted small">{text}</span>
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset className="field">
          <span className="field-label">Engellenecek kategoriler</span>
          <div className="check-grid">
            {Object.entries(form.category_labels).map(([key, label]) => (
              <label key={key} className="switch">
                <input type="checkbox" checked={form.enabled_categories.includes(key)} disabled={LOCKED.includes(key)} onChange={() => toggleCategory(key)} />
                <span>{label}{LOCKED.includes(key) && <em className="muted small"> (her zaman açık)</em>}</span>
              </label>
            ))}
          </div>
          {errors.enabled_categories && <span className="field-error">{errors.enabled_categories}</span>}
        </fieldset>

        <Field label="Engel olaylarını saklama süresi (gün)" error={errors.retention_days} hint="Süresi dolan olaylar otomatik silinir (1-365).">
          <input type="number" min="1" max="365" value={form.retention_days} onChange={(e) => setForm({ ...form, retention_days: e.target.value })} />
        </Field>
        <button className="btn btn-primary" disabled={busy}>{busy ? "Kaydediliyor…" : "Politikayı kaydet"}</button>
      </form>
    </>
  );
}
