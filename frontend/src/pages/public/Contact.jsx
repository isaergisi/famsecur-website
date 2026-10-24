import { useState } from "react";
import { api, fieldErrors } from "../../api";
import Alert from "../../components/Alert";
import Field from "../../components/Field";

const EMPTY = { name: "", email: "", topic: "demo", message: "" };

export default function Contact() {
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setErrors({});
    try {
      await api.post("/contact-requests/", form, { auth: false });
      setSent(true);
      setForm(EMPTY);
    } catch (err) {
      setErrors(fieldErrors(err));
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="section page">
      <div className="container narrow">
        <span className="eyebrow">İletişim</span>
        <h1>Demo talep edin veya bize yazın</h1>
        <p className="muted">Kurulum, demo veya iş birliği için formu doldurun; ekibimiz size e-postayla dönsün.</p>
        {sent && <Alert type="success">Mesajınız alındı. En kısa sürede size dönüş yapacağız.</Alert>}
        <form className="card form" onSubmit={submit} noValidate>
          <Alert>{error}</Alert>
          <div className="form-row">
            <Field label="Ad soyad" error={errors.name}>
              <input value={form.name} onChange={set("name")} required />
            </Field>
            <Field label="E-posta" error={errors.email}>
              <input type="email" value={form.email} onChange={set("email")} required />
            </Field>
          </div>
          <Field label="Konu" error={errors.topic}>
            <select value={form.topic} onChange={set("topic")}>
              <option value="demo">Demo talebi</option>
              <option value="support">Destek</option>
              <option value="partnership">İş birliği</option>
              <option value="other">Diğer</option>
            </select>
          </Field>
          <Field label="Mesaj" error={errors.message}>
            <textarea rows={5} value={form.message} onChange={set("message")} required />
          </Field>
          <button className="btn btn-primary" disabled={busy}>
            {busy ? "Gönderiliyor…" : "Gönder"}
          </button>
        </form>
      </div>
    </section>
  );
}
