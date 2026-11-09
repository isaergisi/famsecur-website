import { useState } from "react";
import { Link } from "react-router-dom";
import { api, asList } from "../../api";
import Alert from "../../components/Alert";
import DecisionResult from "../../components/DecisionResult";
import Field from "../../components/Field";
import PageHead from "../../components/PageHead";
import { useToast } from "../../components/Toast";
import useFetch from "../../components/useFetch";

export default function TestDomain() {
  const notify = useToast();
  const devices = useFetch("/devices/");
  const [form, setForm] = useState({ domain: "", device: "" });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const res = await api.post("/check/", { domain: form.domain, device: form.device ? Number(form.device) : null });
      setResult(res);
      if (res.event) notify("Engel olayı kaydedildi.", "info");
    } catch (err) {
      setResult(null);
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHead title="Alan adı test et" desc="Bir cihazdan gelen DNS sorgusunu sizin politikanız, beyaz listeniz ve tehdit kaynaklarıyla değerlendirin." />
      <div className="two-col">
        <form className="card form" onSubmit={submit}>
          <Alert>{error}</Alert>
          <Field label="Alan adı veya bağlantı">
            <input value={form.domain} onChange={(e) => setForm({ ...form, domain: e.target.value })} placeholder="ornek.com" required />
          </Field>
          <Field label="Cihaz" hint="Koruması kapalı cihazlarda istek filtrelenmez.">
            <select value={form.device} onChange={(e) => setForm({ ...form, device: e.target.value })}>
              <option value="">Cihaz seçilmedi</option>
              {asList(devices.data).map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </Field>
          <button className="btn btn-primary" disabled={busy}>{busy ? "Kontrol ediliyor…" : "Kontrol et"}</button>
          <p className="muted small">Sonuç beklediğiniz gibi değil mi? <Link to="/panel/politika">Politikanızı</Link> veya <Link to="/panel/beyaz-liste">beyaz listenizi</Link> düzenleyin.</p>
        </form>
        <div>
          {result ? <DecisionResult decision={result.decision} message={result.message} /> : <div className="decision decision-empty">Sonuç burada görünecek.</div>}
        </div>
      </div>
    </>
  );
}
