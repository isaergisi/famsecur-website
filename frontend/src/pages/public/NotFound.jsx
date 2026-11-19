import { Link } from "react-router-dom";
import usePageTitle from "../../components/usePageTitle";

export default function NotFound() {
  usePageTitle("Sayfa bulunamadı");
  return (
    <section className="section page">
      <div className="container narrow center">
        <h1>Sayfa bulunamadı</h1>
        <p className="muted">Aradığınız sayfa taşınmış veya hiç var olmamış olabilir.</p>
        <Link className="btn btn-primary" to="/">Ana sayfaya dön</Link>
      </div>
    </section>
  );
}
