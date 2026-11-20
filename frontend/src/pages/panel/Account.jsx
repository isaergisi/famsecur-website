import { useState } from "react";
import { Link } from "react-router-dom";
import { api, fieldErrors } from "../../api";
import { useAuth } from "../../auth";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import PageHead from "../../components/PageHead";
import { useToast } from "../../components/Toast";
import useFetch from "../../components/useFetch";
import { PLANS, SUPPORT, TL } from "../../site";
import { confirmAction, formatDate } from "../../utils";

export default function Account() {
  const { user, setUser } = useAuth();
  const notify = useToast();
  const [profile, setProfile] = useState({ first_name: user.first_name, last_name: user.last_name });
  const [pw, setPw] = useState({ current_password: "", new_password: "" });
  const [pwErrors, setPwErrors] = useState({});
  const [pwError, setPwError] = useState("");

  const family = useFetch("/family/");
  const consents = useFetch("/consents/");

  async function cancelSubscription(undo = false) {
    if (!undo && !confirmAction("Aboneliğiniz iptal edilsin mi? Hizmet ödenmiş dönemin sonuna kadar sürer, sonraki dönem için ücret alınmaz.")) return;
    try {
      family.setData(undo ? await api.delete("/subscription/cancel/") : await api.post("/subscription/cancel/"));
      notify(undo ? "İptal talebiniz geri alındı." : "Aboneliğiniz iptal edildi. Hizmet ödenmiş dönemin sonuna kadar sürer.");
    } catch (err) {
      notify(err.message, "error");
    }
  }

  async function setConsent(kind, give) {
    if (!give && kind === "plus_ozet" && !confirmAction("Günlük özet rızanız geri alınsın mı? O ana kadarki günlük özet verileri hemen silinir.")) return;
    try {
      consents.setData(await api.post("/consents/", { kind, give }));
      family.reload();
      notify(give ? "Onayınız kaydedildi." : "Onayınız geri alındı.");
    } catch (err) {
      notify(err.message, "error");
    }
  }

  async function saveProfile(e) {
    e.preventDefault();
    try {
      setUser(await api.patch("/auth/me/", profile));
      notify("Profiliniz güncellendi.");
    } catch (err) {
      notify(err.message, "error");
    }
  }

  async function changePassword(e) {
    e.preventDefault();
    setPwErrors({});
    setPwError("");
    try {
      const res = await api.post("/auth/change-password/", pw);
      notify(res.detail);
      setPw({ current_password: "", new_password: "" });
    } catch (err) {
      setPwErrors(fieldErrors(err));
      setPwError(err.message);
    }
  }

  return (
    <>
      <PageHead title="Hesabım" desc={user.email} />
      <div className="two-col">
        <form className="card form" onSubmit={saveProfile}>
          <h3>Profil</h3>
          <Field label="Ad"><input value={profile.first_name} onChange={(e) => setProfile({ ...profile, first_name: e.target.value })} /></Field>
          <Field label="Soyad"><input value={profile.last_name} onChange={(e) => setProfile({ ...profile, last_name: e.target.value })} /></Field>
          <button className="btn btn-primary">Kaydet</button>
        </form>
        <form className="card form" onSubmit={changePassword} noValidate>
          <h3>Şifre değiştir</h3>
          <Alert>{pwError}</Alert>
          <Field label="Mevcut şifre" error={pwErrors.current_password}>
            <input type="password" autoComplete="current-password" value={pw.current_password} onChange={(e) => setPw({ ...pw, current_password: e.target.value })} />
          </Field>
          <Field label="Yeni şifre" error={pwErrors.new_password}>
            <input type="password" autoComplete="new-password" value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} />
          </Field>
          <button className="btn btn-primary">Şifreyi güncelle</button>
        </form>
      </div>
      {family.data && <Subscription f={family.data} onCancel={cancelSubscription} />}
      {consents.data && family.data && <Consents list={consents.data} plan={family.data.plan} onChange={setConsent} />}
    </>
  );
}

function Subscription({ f, onCancel }) {
  const plan = PLANS[f.plan];
  const yearly = f.billing_period === "yillik";
  return (
    <div className="card">
      <h3>Aboneliğim</h3>
      <ul className="simple-list">
        <li><span>Paket</span><b>{f.plan_label}</b></li>
        <li><span>Ödeme dönemi</span><b>{yearly ? `Yıllık · ${TL(plan.yearly)} TL` : `Aylık · ${TL(plan.monthly)} TL`}</b></li>
        <li>
          <span>Yenileme</span>
          <span className="muted">
            {yearly ? "Kendiliğinden yenilenmez; bitiminden 30 gün önce hatırlatılır." : "Siz iptal edene kadar her ay yenilenir."}
          </span>
        </li>
        {f.cancel_requested_at && (
          <li><span>İptal talebi</span><b>{formatDate(f.cancel_requested_at)}</b></li>
        )}
      </ul>
      <p className="muted small">
        Paket değiştirmek için <a href={SUPPORT.whatsappLink} target="_blank" rel="noreferrer">WhatsApp</a> veya{" "}
        <a href={`mailto:${SUPPORT.email}`}>{SUPPORT.email}</a>. Kayıttan itibaren 14 gün içinde cayma hakkınız vardır;
        ayrıntılar <Link to="/mesafeli-satis" target="_blank">Mesafeli Satış Sözleşmesi</Link>'nde.
      </p>
      {f.cancel_requested_at ? (
        <button className="btn btn-ghost" onClick={() => onCancel(true)}>İptal talebini geri al</button>
      ) : (
        <button className="btn btn-danger" onClick={() => onCancel(false)}>Aboneliği iptal et</button>
      )}
    </div>
  );
}

const CONSENT_TEXTS = {
  plus_ozet: ["Aile Plus günlük özeti", "Ev ağınızdaki sitelerin günlük özetinin çıkarılması.", "/acik-riza"],
  ticari_ileti: ["Kampanya ve yenilik e-postaları", "Ticari elektronik ileti onayı; dilediğiniz an geri alabilirsiniz.", null],
};

function Consents({ list, plan, onChange }) {
  const active = (kind) => list.some((c) => c.kind === kind && !c.withdrawn_at);
  const kinds = plan === "plus" ? ["plus_ozet", "ticari_ileti"] : ["ticari_ileti"];
  return (
    <div className="card">
      <h3>Onaylarım</h3>
      <ul className="simple-list">
        {kinds.map((kind) => {
          const [title, desc, link] = CONSENT_TEXTS[kind];
          const on = active(kind);
          return (
            <li key={kind}>
              <span>
                <b>{title}</b>
                <span className="muted small"> · {desc} {link && <Link to={link} target="_blank">Metni oku</Link>}</span>
              </span>
              <button className={`pill ${on ? "pill-on" : "pill-off"}`} onClick={() => onChange(kind, !on)}>
                {on ? "Verildi · geri al" : "Verilmedi · ver"}
              </button>
            </li>
          );
        })}
      </ul>
      <details className="consent-history">
        <summary className="small">Onay geçmişi</summary>
        <ul className="simple-list small">
          {list.map((c) => (
            <li key={c.id}>
              <span>{c.kind_label} <span className="muted">(sürüm {c.version})</span></span>
              <span className="muted">
                {formatDate(c.accepted_at)}{c.withdrawn_at && ` · geri alındı ${formatDate(c.withdrawn_at)}`}
              </span>
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}
