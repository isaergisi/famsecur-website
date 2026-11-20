import { useState } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { fieldErrors } from "../../api";
import { useAuth } from "../../auth";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import usePageTitle from "../../components/usePageTitle";
import { PLANS, PLAN_ORDER, TL, TRIAL_TERMS, planFromQuery } from "../../site";

// Onay kutuları: hiçbiri önceden işaretli değildir (KVKK ve 6563 sayılı Kanun gereği).
const CONSENTS = {
  accept_contract: false,
  accept_privacy_notice: false,
  accept_trial_to_paid: false,
  household_ack: false,
  plus_consent: false,
  marketing_consent: false,
};

function Consent({ name, form, setForm, error, optional = false, children }) {
  return (
    <div className="consent">
      <label className="consent-check">
        <input type="checkbox" checked={form[name]} onChange={(e) => setForm({ ...form, [name]: e.target.checked })} />
        <span>
          {children}
          {optional && <em className="muted"> (isteğe bağlı)</em>}
        </span>
      </label>
      {error && <span className="field-error">{error}</span>}
    </div>
  );
}

export default function Register() {
  usePageTitle("Kayıt ol");
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [form, setForm] = useState({
    first_name: "", last_name: "", email: "", password: "", family_name: "", plan: planFromQuery(params.get("paket")),
    billing_period: params.get("donem") === "yillik" ? "yillik" : "aylik", ...CONSENTS,
  });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  if (user) return <Navigate to="/panel" replace />;
  const plan = PLANS[form.plan];
  const yearly = form.billing_period === "yillik";
  const price = yearly ? plan.yearly : plan.monthly;
  const newTab = { target: "_blank", rel: "noreferrer" };

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setErrors({});
    try {
      await register(form);
      navigate("/panel");
    } catch (err) {
      setErrors(fieldErrors(err));
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="section page">
      <div className="container auth-box wide">
        <h1>Ebeveyn hesabı oluşturun</h1>
        <p className="muted">Üç pakette de 7 gün ücretsiz deneme ile başlarsınız. Kayıttan sonra üç adımda kurulumu tamamlarsınız:</p>
        <ol className="auth-steps muted">
          <li>Cihazlarınızı ekleyin.</li>
          <li>Koruma ayarlarınızı seçin.</li>
          <li>Modeminizin DNS ayarını FamSecur'a yönlendirin.</li>
        </ol>
        <form className="card form" onSubmit={submit} noValidate>
          <Alert>{error}</Alert>
          <fieldset className="field">
            <span className="field-label">Paket</span>
            <div className="radio-cards three">
              {PLAN_ORDER.map((id) => PLANS[id]).map((p) => (
                <label key={p.id} className={`radio-card ${form.plan === p.id ? "active" : ""}`}>
                  <input type="radio" name="plan" value={p.id} checked={form.plan === p.id} onChange={set("plan")} />
                  <b>{p.name}</b>
                  <span>{TL(p.monthly)} TL/ay · {TL(p.yearly)} TL/yıl</span>
                  <span className="muted small">{p.short}</span>
                </label>
              ))}
            </div>
            {errors.plan && <span className="field-error">{errors.plan}</span>}
          </fieldset>
          <fieldset className="field">
            <span className="field-label">Ödeme dönemi</span>
            <div className="segmented">
              {[["aylik", "Aylık"], ["yillik", "Yıllık"]].map(([value, label]) => (
                <label key={value} className={form.billing_period === value ? "active" : ""}>
                  <input type="radio" name="billing_period" value={value} checked={form.billing_period === value} onChange={set("billing_period")} />
                  {label}
                </label>
              ))}
            </div>
            <div className="order-summary">
              <div><span>Bugün ödenecek</span><b>0 TL</b></div>
              <div>
                <span>7 günlük deneme bittiğinde</span>
                <b>{TL(price)} TL / {yearly ? "yıl" : "ay"}</b>
              </div>
              <p className="muted small">
                {yearly
                  ? "Yıllık abonelik kendiliğinden yenilenmez; bitiminden 30 gün önce hatırlatılır ve yalnızca onayınızla yenilenir."
                  : "Aylık abonelik siz iptal edene kadar her ay yenilenir; Hesabım sayfasından tek tıkla iptal edebilirsiniz."}{" "}
                Fiyatlara KDV dâhildir.
              </p>
            </div>
          </fieldset>
          <div className="form-row">
            <Field label="Ad" error={errors.first_name}>
              <input value={form.first_name} onChange={set("first_name")} required />
            </Field>
            <Field label="Soyad" error={errors.last_name}>
              <input value={form.last_name} onChange={set("last_name")} />
            </Field>
          </div>
          <Field label="E-posta" error={errors.email}>
            <input type="email" autoComplete="email" value={form.email} onChange={set("email")} required />
          </Field>
          <Field label="Şifre" error={errors.password || errors.non_field_errors} hint="En az 8 karakter; yalnızca rakam olamaz.">
            <input type="password" autoComplete="new-password" value={form.password} onChange={set("password")} required />
          </Field>
          <Field label="Aile adı (isteğe bağlı)" error={errors.family_name}>
            <input value={form.family_name} onChange={set("family_name")} placeholder="Yılmaz Ailesi" />
          </Field>
          <div className="trial-terms">
            <h4>Deneme ve ödeme koşulları</h4>
            <ul>
              {TRIAL_TERMS.map((t) => <li key={t}>{t}</li>)}
            </ul>
          </div>
          <fieldset className="field consents">
            <span className="field-label">Onaylar</span>
            <Consent name="accept_contract" form={form} setForm={setForm} error={errors.accept_contract}>
              <Link to="/mesafeli-satis" {...newTab}>Ön Bilgilendirme Formu ve Mesafeli Satış Sözleşmesi</Link>'ni ve{" "}
              <Link to="/kullanim-kosullari" {...newTab}>Kullanım Koşulları</Link>'nı okudum, onaylıyorum.
            </Consent>
            <Consent name="accept_privacy_notice" form={form} setForm={setForm} error={errors.accept_privacy_notice}>
              <Link to="/gizlilik" {...newTab}>KVKK Aydınlatma Metni ve Gizlilik Politikası</Link>'nı okudum.
            </Consent>
            <Consent name="accept_trial_to_paid" form={form} setForm={setForm} error={errors.accept_trial_to_paid}>
              7 günlük deneme bittiğinde, o güne kadar iptal etmezsem {plan.name} paketinin {yearly ? "yıllık" : "aylık"}{" "}
              ücretinin ({TL(price)} TL) kartımdan tahsil edilmesini onaylıyorum.
            </Consent>
            {form.plan !== "izleme" && (
              <Consent name="household_ack" form={form} setForm={setForm} error={errors.household_ack}>
                Bu pakette riskli isteklerin hangi cihazdan geldiği kaydedilir. Evdeki 18 yaşından büyük kişileri bu
                konuda bilgilendireceğimi ve hizmeti yalnızca kendi ev ağımda kullanacağımı beyan ederim.
              </Consent>
            )}
            {form.plan === "plus" && (
              <Consent name="plus_consent" form={form} setForm={setForm} error={errors.plus_consent}>
                <Link to="/acik-riza" {...newTab}>Aile Plus Açık Rıza Metni</Link>'ni okudum. Ev ağımdaki cihazların
                girdiği sitelerin günlük özetinin çıkarılmasına kendim için ve çocuklarım adına yasal temsilcileri
                olarak açık rıza veriyorum. Bu rızayı panelden dilediğim an geri alabileceğimi biliyorum.
              </Consent>
            )}
            <Consent name="marketing_consent" form={form} setForm={setForm} error={errors.marketing_consent} optional>
              Kampanya ve yeniliklerden e-postayla haberdar olmak istiyorum.
            </Consent>
          </fieldset>
          <button className="btn btn-primary" disabled={busy}>
            {busy ? "Hesap oluşturuluyor…" : "Ücretsiz denemeyi başlat"}
          </button>
          <p className="muted small">
            Zaten hesabınız var mı? <Link to="/giris">Giriş yapın</Link>
          </p>
        </form>
      </div>
    </section>
  );
}
