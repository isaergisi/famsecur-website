export default function PageHead({ title, desc, children }) {
  return (
    <div className="page-head">
      <div>
        <h1>{title}</h1>
        {desc && <p className="muted">{desc}</p>}
      </div>
      {children && <div className="page-actions">{children}</div>}
    </div>
  );
}
