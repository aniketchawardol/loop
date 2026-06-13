import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../auth";
import { useToast } from "../components/Toast";
import { GiSeedling } from "react-icons/gi";
import { FaGift } from "react-icons/fa";
import { AiOutlineLoading3Quarters } from "react-icons/ai";

export default function Rewards() {
  const { reload } = useAuth();
  const [balance, setBalance] = useState(0);
  const [impact, setImpact] = useState({});
  const [rewards, setRewards] = useState([]);
  const [loading, setLoading] = useState(true);
  const { push } = useToast();

  useEffect(() => {
    setLoading(true);
    Promise.all([api.get("/credits"), api.get("/rewards")])
      .then(([c, r]) => {
        setBalance(c.balance);
        setImpact(c.impact || {});
        setRewards(r);
      })
      .finally(() => setLoading(false));
  }, []);

  const claim = async (id, cost) => {
    try {
      const res = await api.post(`/rewards/${id}/claim`);
      setBalance(res.new_balance);
      reload();
      push("Reward claimed", "success");
    } catch (e) {
      push(e.response?.data?.message || "Claim failed", "error");
    }
  };

  return (
    <div className="page">
      <h2>
        <GiSeedling style={{ verticalAlign: "middle", marginRight: 8 }} /> Green
        Credits
      </h2>
      {loading ? (
        <div className="card skeleton">
          <div className="thumb skeleton" />
          <div className="line skeleton" />
          <div className="line short skeleton" />
        </div>
      ) : (
        <div className="card">
          <h3>
            Your Balance: {balance} <GiSeedling style={{ marginLeft: 8 }} />
          </h3>
          <p>Items saved: {impact.items_saved_from_landfill}</p>
          <p>CO₂ avoided: {impact.co2_avoided_kg} kg</p>
        </div>
      )}

      <h3>Rewards Store</h3>
      <div className="grid">
        {rewards.map((r) => (
          <div key={r.id} className="card">
            <div style={{ fontSize: 28, color: "var(--accent2)" }}>
              <FaGift />
            </div>
            <div>{r.title}</div>
            <div className="muted">{r.description}</div>
            <div className="price">{r.cost}</div>
            <button onClick={() => claim(r.id)}>Claim</button>
          </div>
        ))}
      </div>
    </div>
  );
}
