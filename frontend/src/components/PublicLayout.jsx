import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth";
import Logo from "./Logo";

export default function PublicLayout() {
  const { user, isAdmin } = useAuth();
  const [open, setOpen] = useState(false);
  return (
    <>
      <header className="site-header">
        <div className="container nav">
          <Logo />
          <button className="nav-toggle" onClick={() => setOpen(!open)} aria-label="Menüyü aç/kapat">
            ☰
          </button>
          <nav className={open ? "nav-links open" : "nav-links"} onClick={() => setOpen(false)}>
            <a href="/#ozellikler">Özellikler</a>
            <a href="/#nasil-calisir">Nasıl çalışır</a>
            <a href="/#demo">Canlı demo</a>
            <NavLink to="/sss">SSS</NavLink>
            <NavLink to="/iletisim">İletişim</NavLink>
            {user ? (
              <Link className="btn btn-primary btn-sm" to={isAdmin ? "/yonetim" : "/panel"}>
                {isAdmin ? "Yönetim paneli" : "Ebeveyn paneli"}
              </Link>
            ) : (
              <>
                <NavLink to="/giris">Giriş</NavLink>
                <Link className="btn btn-primary btn-sm" to="/kayit">
                  Ücretsiz başla
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="site-footer">
        <div className="container footer-grid">
          <div>
            <Logo />
            <p className="muted">Müdahale etmeden, Aileni koru.</p>
          </div>
          <div>
            <h4>Ürün</h4>
            <a href="/#ozellikler">Özellikler</a>
            <a href="/#gizlilik">Gizlilik</a>
            <a href="/#demo">Canlı demo</a>
          </div>
          <div>
            <h4>Destek</h4>
            <Link to="/sss">Sıkça sorulan sorular</Link>
            <Link to="/iletisim">İletişim</Link>
            <a href="https://github.com/isaergisi/FamSecur" target="_blank" rel="noreferrer">
              GitHub
            </a>
          </div>
        </div>
        <div className="container footer-bottom muted">© {new Date().getFullYear()} FamSecur</div>
      </footer>
    </>
  );
}
