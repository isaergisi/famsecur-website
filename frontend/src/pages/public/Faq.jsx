import { Link } from "react-router-dom";
import Alert from "../../components/Alert";
import Spinner from "../../components/Spinner";
import useFetch from "../../components/useFetch";

export default function Faq() {
  const { data, error, loading } = useFetch("/faqs/");
  return (
    <section className="section page">
      <div className="container narrow">
        <span className="eyebrow">Destek</span>
        <h1>Sıkça sorulan sorular</h1>
        {loading && <Spinner />}
        <Alert>{error?.message}</Alert>
        <div className="faq-list">
          {data?.map((item) => (
            <details key={item.id} className="card faq">
              <summary>{item.question}</summary>
              <p className="muted">{item.answer}</p>
            </details>
          ))}
          {data?.length === 0 && <p className="muted">Henüz soru eklenmedi.</p>}
        </div>
        <p className="muted">
          Sorunuzun cevabını bulamadınız mı? <Link to="/iletisim">Bize yazın</Link>.
        </p>
      </div>
    </section>
  );
}
