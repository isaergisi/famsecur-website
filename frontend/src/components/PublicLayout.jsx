import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth";
import { SUPPORT } from "../site";
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
            <a href="/#neden-famsecur">Neden FamSecur?</a>
            <a href="/#nasil-calisir">Nasıl çalışır?</a>
            <a href="/#demo">Canlı demo</a>
            <a href="/#fiyatlar">Fiyatlar</a>
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
                  Ücretsiz deneyin
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
            <p className="muted">Müdahale etmeden aileni koru.</p>
          </div>
          <div>
            <h4>Ürün</h4>
            <a href="/#neden-famsecur">Neden FamSecur?</a>
            <a href="/#ozellikler">Özellikler</a>
            <a href="/#koruma-yaklasimi">Koruma yaklaşımı</a>
            <a href="/#yapay-zeka">Yapay zekâ</a>
            <a href="/#demo">Canlı demo</a>
            <a href="/#fiyatlar">Fiyatlar</a>
          </div>
          <div>
            <h4>Destek</h4>
            <Link to="/sss">Sıkça sorulan sorular</Link>
            <Link to="/iletisim">İletişim</Link>
            <a href={SUPPORT.whatsappLink} target="_blank" rel="noreferrer">WhatsApp destek</a>
          </div>
          <div>
            <h4>Yasal</h4>
            <Link to="/gizlilik">Gizlilik Politikası</Link>
            <Link to="/kullanim-kosullari">Kullanım Koşulları</Link>
          </div>
        </div>
        <div className="container footer-bottom muted">© {new Date().getFullYear()} FamSecur</div>
      </footer>
    </>
  );
}
