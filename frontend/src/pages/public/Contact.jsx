import { useState } from "react";
import { api, fieldErrors } from "../../api";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import { Clock, Mail, MessageCircle } from "lucide-react";
import usePageTitle from "../../components/usePageTitle";
import { SUPPORT } from "../../site";

const EMPTY = { name: "", email: "", topic: "demo", message: "" };

export default function Contact() {
  usePageTitle("İletişim");
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
        <h1>Size nasıl yardımcı olabiliriz?</h1>
        <p className="muted">Kurulum, abonelik, demo veya iş birliği için bize dilediğiniz kanaldan ulaşabilirsiniz.</p>
        <div className="contact-channels">
          <a className="card contact-channel" href={SUPPORT.whatsappLink} target="_blank" rel="noreferrer">
            <MessageCircle aria-hidden strokeWidth={1.8} />
            <span><b>WhatsApp</b><span className="muted small">{SUPPORT.whatsapp}</span></span>
          </a>
          <a className="card contact-channel" href={`mailto:${SUPPORT.email}`}>
            <Mail aria-hidden strokeWidth={1.8} />
            <span><b>E-posta</b><span className="muted small">{SUPPORT.email}</span></span>
          </a>
          <div className="card contact-channel">
            <Clock aria-hidden strokeWidth={1.8} />
            <span><b>Yanıt süresi</b><span className="muted small">Mesajlarınıza {SUPPORT.responseTime} dönüş yapıyoruz.</span></span>
          </div>
        </div>
        <h2 className="section-title">İletişim formu</h2>
        {sent && <Alert type="success">Mesajınız bize ulaştı, teşekkür ederiz. {SUPPORT.responseTime[0].toLocaleUpperCase("tr-TR") + SUPPORT.responseTime.slice(1)} size dönüş yapacağız.</Alert>}
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
