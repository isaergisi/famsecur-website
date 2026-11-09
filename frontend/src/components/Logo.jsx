import { Link } from "react-router-dom";

export default function Logo({ to = "/" }) {
  return (
    <Link to={to} className="logo">
      <img src="/famsecur-logo.jpg" alt="" width="36" height="36" />
      <span>
        Fam<b>Secur</b>
      </span>
    </Link>
  );
}
