import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../auth";
import { useToast } from "../components/Toast";
import { Link } from "react-router-dom";
import { AiOutlineLoading3Quarters } from "react-icons/ai";
import { FaHeartbeat } from "react-icons/fa";

export default function PreLoved() {
  const [listings, setListings] = useState([]);
  const { user, reload } = useAuth();
  const { push } = useToast();
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .get("/listings/preloved")
      .then((res) => setListings(res))
      .finally(() => setLoading(false));
  }, []);

  const buy = async (listingId) => {
    setMsg("");
    if (!user) return window.location.assign("/login");
    const prevBal = user?.green_credits?.balance || 0;
    try {
      await api.post("/orders/place", { listing_id: listingId });
      push("Order placed", "success");
      // reload auth and compute balance diff
      try {
        const me = await reload();
        const newBal = me?.green_credits?.balance || 0;
        if (newBal > prevBal)
          push(`+${newBal - prevBal} green credits`, "success");
      } catch (e) {}
    } catch (e) {
      push(e.message || "Order failed", "error");
    }
  };

  return (
    <div className="page">
      <h2>Pre-Loved Shop</h2>
      {/* toasts handled globally */}
      <div className="grid">
        {loading
          ? Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="card skeleton">
                <div className="thumb skeleton" />
                <div className="line skeleton" />
                <div className="line short skeleton" />
              </div>
            ))
          : listings.map((l) => (
              <Link
                key={l.id}
                className="card"
                to={`/p/${l.product.id}`}
                style={{ color: "inherit", textDecoration: "none" }}
              >
                {(() => {
                  const src =
                    (l.photo_urls && l.photo_urls[0]) ||
                    l.product.image_url ||
                    l.product.thumbnail_url;
                  return src ? (
                    <img
                      src={src}
                      style={{
                        width: "100%",
                        height: 110,
                        objectFit: "cover",
                        borderRadius: 8,
                        marginBottom: 8,
                      }}
                    />
                  ) : null;
                })()}
                <div className="muted">
                  Grade {l.grade} · {l.source}
                </div>
                <h3>{l.product.title}</h3>
                <div className="muted">
                  ₹{l.price} <s>₹{l.product.mrp}</s>
                </div>
                <div>
                  Save {Math.round(100 - (l.price * 100) / l.product.mrp)}%
                </div>
                <div className="card-actions">
                  <button
                    className="button"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      buy(l.id);
                    }}
                  >
                    Buy
                  </button>
                  <a
                    className="button green"
                    href={`/unit/${l.unit_id}`}
                    onClick={(e) => {
                      e.stopPropagation();
                    }}
                  >
                    <FaHeartbeat style={{ marginRight: 6 }} />
                    Health
                  </a>
                </div>
              </Link>
            ))}
      </div>
    </div>
  );
}
