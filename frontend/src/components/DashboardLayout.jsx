import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import Logo from "./Logo";

export default function DashboardLayout({ title, links, switchLink }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  return (
    <div className="dash">
      <aside className={open ? "dash-side open" : "dash-side"}>
        <Logo />
        <p className="dash-title">{title}</p>
        <nav onClick={() => setOpen(false)}>
          {links.map(([to, label, icon]) => (
            <NavLink key={to} to={to} end>
              <span aria-hidden>{icon}</span> {label}
            </NavLink>
          ))}
        </nav>
        <div className="dash-foot">
          {switchLink && (
            <NavLink to={switchLink[0]} className="small">
              {switchLink[1]}
            </NavLink>
          )}
          <NavLink to="/" className="small">← Siteye dön</NavLink>
          <div className="dash-user">
            <b>{user.first_name || user.email}</b>
            <span className="muted small">{user.email}</span>
          </div>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => {
              logout();
              navigate("/giris");
            }}
          >
            Çıkış yap
          </button>
        </div>
      </aside>
      <div className="dash-main">
        <button className="nav-toggle dash-toggle" onClick={() => setOpen(!open)} aria-label="Menü">
          ☰
        </button>
        <Outlet />
      </div>
    </div>
  );
}
