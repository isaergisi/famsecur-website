export default function Pagination({ data, page, setPage, pageSize = 20 }) {
  if (!data?.count || data.count <= pageSize) return null;
  const pages = Math.ceil(data.count / pageSize);
  return (
    <div className="pagination">
      <button className="btn btn-ghost btn-sm" disabled={!data.previous} onClick={() => setPage(page - 1)}>
        ← Önceki
      </button>
      <span className="muted small">
        {page} / {pages}
      </span>
      <button className="btn btn-ghost btn-sm" disabled={!data.next} onClick={() => setPage(page + 1)}>
        Sonraki →
      </button>
    </div>
  );
}
