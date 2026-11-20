const SOURCE_LABELS = {
  threat_list: "Güvenilir bir tehdit listesinde eşleşme bulundu.",
  official_list: "Resmî yasa dışı kumar sicilinde eşleşme bulundu.",
  signals: "Listelerde eşleşme yok; karar alan adındaki risk işaretlerine göre verildi.",
  whitelist: "Site beyaz listenizde.",
  manual_list: "Site engel listenizde.",
  ai: "Listelerde eşleşme yok; yapay zekâ risk tahmini çok yüksek ve otomatik engel ayarınız açık.",
  none: "Listelerde eşleşme yok; adında risk işareti de bulunmadı.",
  device_off: "Bu cihazda koruma kapalı.",
};

export default function DecisionResult({ decision, message, ai }) {
  if (!decision) return null;
  const blocked = decision.action === "block";
  const listed = ["threat_list", "official_list", "manual_list"].includes(decision.source);
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
      <dl className="decision-facts">
        <div><dt>Sonuç</dt><dd>{blocked ? "Engellenir, site açılmaz." : "İzin verilir, site açılır."}</dd></div>
        {decision.category_label && <div><dt>Kategori</dt><dd><b>{decision.category_label}</b></dd></div>}
        {SOURCE_LABELS[decision.source] && <div><dt>Karar kaynağı</dt><dd>{SOURCE_LABELS[decision.source]}</dd></div>}
        {(ai || listed) && (
          <div>
            <dt>Yapay zekâ</dt>
            <dd>
              {decision.source === "ai"
                ? "Tahmin çok yüksek ve yapay zekâ ile otomatik engel ayarınız açık olduğu için site engellendi."
                : ai
                  ? "Değerlendirildi (aşağıda). Otomatik engel ayarı açık değilse yapay zekâ yalnızca uyarır."
                  : "Değerlendirilmedi; site bir listede yer aldığı için karar kesindir."}
            </dd>
          </div>
        )}
      </dl>
      <p className="muted small">Neden?</p>
      <ul className="reasons">
        {decision.reasons.map((r) => (
          <li key={r}>{r}</li>
        ))}
      </ul>
      {message && <p className="small">{message}</p>}
      {ai && <AiRisk ai={ai} blocked={blocked} />}
    </div>
  );
}

// Eğitilmiş yapay zekâ modelinin tahmini. Yalnızca hiçbir listede olmayan alan
// adları için gelir; engel kararını değiştirmez, ebeveyne ek bir uyarıdır.
function AiRisk({ ai, blocked = false }) {
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
          ? `Dikkat: Bu alan adı hiçbir listede yok ama adı ${ai.category_label ? ai.category_label.toLocaleLowerCase("tr-TR") + " sitelerine" : "riskli sitelere"} benziyor. ${blocked ? "Engellendi." : "Engellenmedi; isterseniz kontrol edin."}`
          : "Bu alan adı hiçbir listede yok; yapay zekâ modeli de adında belirgin bir risk görmedi."}
      </p>
      <p className="muted small">Model yalnızca alan adının harflerine bakar, sitenin içeriğini görmez. Tahmin yanılabilir.</p>
    </div>
  );
}
