import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function Shop() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");

  useEffect(() => {
    setLoading(true);
    const t = setTimeout(() => {
      api
        .get(`/products${q ? `?q=${encodeURIComponent(q)}` : ""}`)
        .then((res) => setProducts(res.data || res))
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(t);
  }, [q]);

  return (
    <div className="page">
      <div className="row" style={{ marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Shop</h2>
        <input
          style={{ maxWidth: 320 }}
          className="right"
          placeholder="Search products…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </div>
      <div className="grid">
        {loading
          ? Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="card skeleton">
                <div className="thumb skeleton" />
                <div className="line skeleton" />
                <div className="line short skeleton" />
              </div>
            ))
          : products.map((p) => (
              <Link
                className="card"
                key={p.id}
                to={`/p/${p.id}`}
                style={{ color: "inherit", textDecoration: "none" }}
              >
                {(() => {
                  const src =
                    p.thumbnail_url ||
                    (p.listings &&
                      p.listings[0] &&
                      p.listings[0].photo_urls &&
                      p.listings[0].photo_urls[0]) ||
                    p.image_url;
                  return src ? (
                    <img
                      src={src}
                      alt={p.title}
                      style={{
                        width: "100%",
                        height: 110,
                        objectFit: "cover",
                        borderRadius: 8,
                        marginBottom: 8,
                      }}
                      onError={(e) => {
                        e.target.style.display = "none";
                      }}
                    />
                  ) : null;
                })()}
                <span className="badge">{p.category}</span>
                <h3>{p.title}</h3>
                <div>
                  <span className="price">₹{p.mrp}</span>
                </div>
                <div className="muted">by {p.seller_name}</div>
              </Link>
            ))}
        {products.length === 0 && (
          <div className="muted">No products found.</div>
        )}
      </div>
    </div>
  );
}
