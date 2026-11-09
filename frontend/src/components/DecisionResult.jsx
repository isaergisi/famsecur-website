export default function DecisionResult({ decision, message }) {
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
    </div>
  );
}
