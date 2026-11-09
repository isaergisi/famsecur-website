import { useState } from "react";
import { api, fieldErrors } from "../../api";
import { useAuth } from "../../auth";
import Alert from "../../components/Alert";
import Field from "../../components/Field";
import PageHead from "../../components/PageHead";
import { useToast } from "../../components/Toast";

export default function Account() {
  const { user, setUser } = useAuth();
  const notify = useToast();
  const [profile, setProfile] = useState({ first_name: user.first_name, last_name: user.last_name });
  const [pw, setPw] = useState({ current_password: "", new_password: "" });
  const [pwErrors, setPwErrors] = useState({});
  const [pwError, setPwError] = useState("");

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
    </>
  );
}
