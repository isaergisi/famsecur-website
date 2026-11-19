export default function DecisionResult({ decision, message, ai }) {
  if (!decision) return null;
  const blocked = decision.action === "block";
  return (
    <div className={`decision ${blocked ? "decision-block" : "decision-allow"}`}>
      <div className="decision-head">
        <span className="decision-badge">{blocked ? "Engellendi" : "İzin verildi"}</span>
        <code>{decision.domain}</code>
      </div>
      <div className="score">
        <div className="score-bar">
          <span style={{ width: `${decision.score}%` }} />
        </div>
        <span>
          Risk puanı <b>{decision.score}</b>/100
        </span>
      </div>
      {decision.category_label && (
        <p>
          Kategori: <b>{decision.category_label}</b>
        </p>
      )}
      <p className="muted small">Neden?</p>
      <ul className="reasons">
        {decision.reasons.map((r) => (
          <li key={r}>{r}</li>
        ))}
      </ul>
      {message && <p className="small">{message}</p>}
      {ai && <AiRisk ai={ai} />}
    </div>
  );
}

// Eğitilmiş yapay zekâ modelinin tahmini. Yalnızca hiçbir listede olmayan alan
// adları için gelir; engel kararını değiştirmez, ebeveyne ek bir uyarıdır.
function AiRisk({ ai }) {
  return (
    <div className={`ai-risk ${ai.warning ? "ai-risk-warn" : ""}`}>
      <div className="score">
        <span>
          Yapay zekâ risk tahmini: <b>%{ai.risk}</b>
        </span>
        <div className="score-bar">
          <span style={{ width: `${ai.risk}%` }} />
        </div>
      </div>
      <p className="small">
        {ai.warning
          ? `Dikkat: Bu alan adı hiçbir listede yok ama adı ${ai.category_label ? ai.category_label.toLocaleLowerCase("tr-TR") + " sitelerine" : "riskli sitelere"} benziyor. Engellenmedi; isterseniz kontrol edin.`
          : "Bu alan adı hiçbir listede yok; yapay zekâ modeli de adında belirgin bir risk görmedi."}
      </p>
      <p className="muted small">Model yalnızca alan adının harflerine bakar, sitenin içeriğini görmez. Tahmin yanılabilir.</p>
    </div>
  );
}
