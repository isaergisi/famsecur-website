import { useState } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { fieldErrors } from "../../api";
import { useAuth } from "../../auth";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import usePageTitle from "../../components/usePageTitle";
import { PLANS, TL, TRIAL_TERMS, planFromQuery } from "../../site";

export default function Register() {
  usePageTitle("Kayıt ol");
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [form, setForm] = useState({
    first_name: "", last_name: "", email: "", password: "", family_name: "", plan: planFromQuery(params.get("paket")),
  });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  if (user) return <Navigate to="/panel" replace />;

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
      <div className="container auth-box">
        <h1>Ebeveyn hesabı oluşturun</h1>
        <p className="muted">İki pakette de 7 gün ücretsiz deneme ile başlarsınız. Kayıttan sonra üç adımda kurulumu tamamlarsınız:</p>
        <ol className="auth-steps muted">
          <li>Cihazlarınızı ekleyin.</li>
          <li>Koruma ayarlarınızı seçin.</li>
          <li>Modeminizin DNS ayarını FamSecur'a yönlendirin.</li>
        </ol>
        <form className="card form" onSubmit={submit} noValidate>
          <Alert>{error}</Alert>
          <fieldset className="field">
            <span className="field-label">Paket</span>
            <div className="radio-cards">
              {Object.values(PLANS).map((plan) => (
                <label key={plan.id} className={`radio-card ${form.plan === plan.id ? "active" : ""}`}>
                  <input type="radio" name="plan" value={plan.id} checked={form.plan === plan.id} onChange={set("plan")} />
                  <b>{plan.name}</b>
                  <span>{TL(plan.monthly)} TL/ay</span>
                  <span className="muted small">{plan.short}</span>
                </label>
              ))}
            </div>
            {errors.plan && <span className="field-error">{errors.plan}</span>}
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
          <button className="btn btn-primary" disabled={busy}>
            {busy ? "Hesap oluşturuluyor…" : "Ücretsiz denemeyi başlat"}
          </button>
          <div className="trial-terms">
            <h4>Deneme ve ödeme koşulları</h4>
            <ul>
              {TRIAL_TERMS.map((t) => <li key={t}>{t}</li>)}
            </ul>
          </div>
          <p className="muted small">
            Kayıt olarak <Link to="/kullanim-kosullari">Kullanım Koşulları</Link>'nı ve{" "}
            <Link to="/gizlilik">Gizlilik Politikası</Link>'nı kabul etmiş olursunuz.
          </p>
          <p className="muted small">
            Zaten hesabınız var mı? <Link to="/giris">Giriş yapın</Link>
          </p>
        </form>
      </div>
    </section>
  );
}
