// Ebeveyn paneli: son 7 günün özeti ve gün gün engellenen istek grafiği.
const DAY_FMT = new Intl.DateTimeFormat("tr-TR", { weekday: "short" });
const LONG_FMT = new Intl.DateTimeFormat("tr-TR", { day: "numeric", month: "long", weekday: "long" });

const parseDay = (iso) => {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
};

function trend(total, previous) {
  if (total === 0 && previous === 0) return { text: "Geçen hafta da engellenen istek yoktu.", tone: "flat" };
  if (previous === 0) return { text: "Geçen hafta hiç engel yoktu.", tone: "up" };
  const diff = total - previous;
  if (diff === 0) return { text: "Geçen haftayla aynı.", tone: "flat" };
  const pct = Math.round((Math.abs(diff) / previous) * 100);
  return diff > 0
    ? { text: `Geçen haftaya göre %${pct} fazla (${previous} → ${total}).`, tone: "up" }
    : { text: `Geçen haftaya göre %${pct} az (${previous} → ${total}).`, tone: "down" };
}

export default function WeeklySummary({ weekly, categoryLabels }) {
  const { total, previous_total: previous, days, top_category: topCat, top_device: topDevice } = weekly;
  const max = Math.max(1, ...days.map((d) => d.count));
  const t = trend(total, previous);
  const label = days.map((d) => `${LONG_FMT.format(parseDay(d.day))}: ${d.count}`).join(", ");

  return (
    <div className="card weekly">
      <div className="weekly-text">
        <span className="eyebrow">Bu hafta</span>
        <h3 className="weekly-headline">
          {total === 0 ? (
            "Bu hafta riskli bir istek olmadı."
          ) : (
            <>Bu hafta <b>{total}</b> riskli istek durduruldu.</>
          )}
        </h3>
        <p className={`weekly-trend trend-${t.tone}`}>{t.text}</p>
        {total > 0 && (
          <ul className="weekly-facts">
            {topCat && (
              <li>En sık kategori: <b>{categoryLabels[topCat.category] || topCat.category}</b> ({topCat.count})</li>
            )}
            {topDevice && <li>En çok engellenen cihaz: <b>{topDevice.name}</b> ({topDevice.count})</li>}
          </ul>
        )}
        <p className="muted small">Yalnızca engellenen istekler sayılır; izin verilen trafik kaydedilmez.</p>
      </div>
      <figure className="week-chart" role="img" aria-label={`Son 7 günde engellenen istekler. ${label}`}>
        <div className="week-bars">
          {days.map((d, i) => {
            const isToday = i === days.length - 1;
            return (
              <div key={d.day} className="week-col" title={`${LONG_FMT.format(parseDay(d.day))}: ${d.count} engel`}>
                <span className="week-val">{d.count > 0 ? d.count : ""}</span>
                <div className="week-track">
                  <span
                    className={`week-bar${d.count === 0 ? " is-zero" : ""}`}
                    style={{ height: `${(d.count / max) * 100}%` }}
                  />
                </div>
                <span className={`week-day${isToday ? " is-today" : ""}`}>{isToday ? "Bugün" : DAY_FMT.format(parseDay(d.day))}</span>
              </div>
            );
          })}
        </div>
      </figure>
    </div>
  );
}
