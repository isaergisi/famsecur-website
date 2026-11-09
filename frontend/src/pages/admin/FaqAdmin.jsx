import { useState } from "react";
import { api, fieldErrors } from "../../api";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import Modal from "../../components/Modal";
import PageHead from "../../components/PageHead";
import Spinner from "../../components/Spinner";
import { useToast } from "../../components/Toast";
import useFetch from "../../components/useFetch";
import { confirmAction } from "../../utils";

const EMPTY = { question: "", answer: "", order: 0, is_published: true };

function FaqForm({ initial, onClose, onSaved }) {
  const [form, setForm] = useState(initial || EMPTY);
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  async function submit(e) {
    e.preventDefault();
    const payload = { ...form, order: Number(form.order) || 0 };
    try {
      const saved = initial ? await api.put(`/faqs/${initial.id}/`, payload) : await api.post("/faqs/", payload);
      onSaved(saved, Boolean(initial));
    } catch (err) {
      setErrors(fieldErrors(err));
      setError(err.message);
    }
  }

  return (
    <Modal title={initial ? "Soruyu düzenle" : "Yeni soru"} onClose={onClose}>
      <form className="form" onSubmit={submit} noValidate>
        <Alert>{error}</Alert>
        <Field label="Soru" error={errors.question}><input value={form.question} onChange={set("question")} /></Field>
        <Field label="Cevap" error={errors.answer}><textarea rows={5} value={form.answer} onChange={set("answer")} /></Field>
        <div className="form-row">
          <Field label="Sıra" error={errors.order}><input type="number" min="0" value={form.order} onChange={set("order")} /></Field>
          <label className="switch"><input type="checkbox" checked={form.is_published} onChange={set("is_published")} /><span>Sitede yayında</span></label>
        </div>
        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose}>Vazgeç</button>
          <button className="btn btn-primary">Kaydet</button>
        </div>
      </form>
    </Modal>
  );
}

export default function FaqAdmin() {
  const notify = useToast();
  const { data, error, loading, reload } = useFetch("/faqs/");
  const [editing, setEditing] = useState(null);

  async function remove(item) {
    if (!confirmAction(`"${item.question}" silinsin mi?`)) return;
    try {
      await api.delete(`/faqs/${item.id}/`);
      notify("Soru silindi.");
      reload();
    } catch (err) {
      notify(err.message, "error");
    }
  }

  return (
    <>
      <PageHead title="SSS içerikleri" desc="Sitedeki Sıkça Sorulan Sorular sayfasını yönetin.">
        <button className="btn btn-primary" onClick={() => setEditing({})}>+ Soru ekle</button>
      </PageHead>
      {loading && <Spinner />}
      <Alert>{error?.message}</Alert>
      <div className="stack">
        {data?.map((f) => (
          <div key={f.id} className="card faq-admin">
            <div>
              <b>{f.order}. {f.question}</b> {!f.is_published && <span className="tag">Taslak</span>}
              <p className="muted small">{f.answer}</p>
            </div>
            <div className="row-actions">
              <button className="btn btn-ghost btn-sm" onClick={() => setEditing(f)}>Düzenle</button>
              <button className="btn btn-danger btn-sm" onClick={() => remove(f)}>Sil</button>
            </div>
          </div>
        ))}
        {data?.length === 0 && <div className="card empty">Henüz soru yok.</div>}
      </div>
      {editing && (
        <FaqForm
          initial={editing.id ? editing : null}
          onClose={() => setEditing(null)}
          onSaved={(_, updated) => {
            notify(updated ? "Soru güncellendi." : "Soru eklendi.");
            setEditing(null);
            reload();
          }}
        />
      )}
    </>
  );
}
