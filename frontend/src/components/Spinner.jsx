export default function Spinner({ full = false }) {
  return (
    <div className={full ? "spinner-wrap full" : "spinner-wrap"}>
      <span className="spinner" aria-label="Yükleniyor" />
    </div>
  );
}
