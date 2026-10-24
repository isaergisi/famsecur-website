import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth";
import Alert from "../../components/Alert";
import Field from "../../components/Field";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to={user.role === "admin" ? "/yonetim" : "/panel"} replace />;

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const u = await login(form.email, form.password);
      navigate(u.role === "admin" ? "/yonetim" : "/panel");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="section page">
      <div className="container auth-box">
        <h1>Giriş yap</h1>
        <form className="card form" onSubmit={submit}>
          <Alert>{error}</Alert>
          <Field label="E-posta">
            <input type="email" autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          </Field>
          <Field label="Şifre">
            <input type="password" autoComplete="current-password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          </Field>
          <button className="btn btn-primary" disabled={busy}>
            {busy ? "Giriş yapılıyor…" : "Giriş yap"}
          </button>
          <p className="muted small">
            Hesabınız yok mu? <Link to="/kayit">Kayıt olun</Link>
          </p>
        </form>
      </div>
    </section>
  );
}
