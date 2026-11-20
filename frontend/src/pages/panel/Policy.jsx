import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
  const family = useFetch("/family/");
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
      const { risk_threshold, enforcement_mode, enabled_categories, retention_days, ai_auto_block } = form;
      setData(await api.put("/policy/", { risk_threshold: Number(risk_threshold), enforcement_mode, enabled_categories, retention_days: Number(retention_days), ai_auto_block }));
      notify("Politika kaydedildi. Yeni kurallar hemen uygulanır.");
    } catch (err) {
      setErrors(fieldErrors(err));
      setSaveError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const autoBlocks = family.data?.auto_blocks ?? true;
  const strictness = form.risk_threshold <= 50 ? "Sıkı" : form.risk_threshold <= 80 ? "Dengeli" : "Esnek";
  return (
    <>
      <PageHead title="Koruma politikası" desc={`Son güncelleme: ${formatDate(data.updated_at)}`} />
      <form className="card form" onSubmit={submit}>
        <Alert>{saveError}</Alert>
        {!autoBlocks && (
          <div className="notice">
            Başlangıç paketinde otomatik engel yoktur. Buradaki ayarlar hangi sitelerin <b>riskli olarak kaydedileceğini</b>{" "}
            belirler; siteleri engellemek için <Link to="/panel/engel-listesi">Engel listem</Link> sayfasını kullanın.
          </div>
        )}
        <Field label={`Risk eşiği: ${form.risk_threshold} (${strictness})`} error={errors.risk_threshold} hint={autoBlocks ? "Puanı bu değere eşit veya üstünde olan alan adları engellenir. Düşük eşik daha sıkı korur." : "Puanı bu değere eşit veya üstünde olan alan adları riskli olarak kaydedilir."}>
          <input type="range" min="30" max="100" step="5" value={form.risk_threshold} onChange={(e) => setForm({ ...form, risk_threshold: Number(e.target.value) })} />
        </Field>

        <fieldset className="field">
          <span className="field-label">Engelleme biçimi</span>
          <div className="radio-cards">
            {[
              ["silent", "Sessiz engel (önerilen)", "Site açılmaz, cihazda bağlantı hatası görünür. Çocuğunuz engellenen içeriğin türünü öğrenmez."],
              ["warning", "Uyarı sayfası", "Engelin nedeni bir FamSecur sayfasında gösterilir. Bu sayfa yalnızca şifresiz (HTTP) sitelerde görünür; HTTPS sitelerde tarayıcı güvenlik uyarısı gösterir."],
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
          <span className="field-label">Yapay zekâ ile otomatik engel</span>
          <label className="switch">
            <input
              type="checkbox"
              checked={Boolean(form.ai_auto_block)}
              disabled={!autoBlocks}
              onChange={(e) => setForm({ ...form, ai_auto_block: e.target.checked })}
            />
            <span>
              Hiçbir listede olmayan ama yapay zekânın çok riskli bulduğu (%85 ve üzeri) siteleri de engelle
              {!autoBlocks && <em className="muted small"> (Ebeveyn ve Aile Plus paketlerinde)</em>}
            </span>
          </label>
          <span className="muted small">
            Model sitenin içeriğini görmez, yalnızca adına bakar; masum bir site engellenirse beyaz listenize ekleyin.
          </span>
          {errors.ai_auto_block && <span className="field-error">{errors.ai_auto_block}</span>}
        </fieldset>

        <fieldset className="field">
          <span className="field-label">{autoBlocks ? "Engellenecek kategoriler" : "Kaydedilecek kategoriler"}</span>
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

        <Field label="Olayları saklama süresi (gün)" error={errors.retention_days} hint="Süresi dolan olaylar otomatik silinir (1-365).">
          <input type="number" min="1" max="365" value={form.retention_days} onChange={(e) => setForm({ ...form, retention_days: e.target.value })} />
        </Field>
        <button className="btn btn-primary" disabled={busy}>{busy ? "Kaydediliyor…" : "Politikayı kaydet"}</button>
      </form>
    </>
  );
}
