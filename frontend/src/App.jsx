import { Navigate, NavLink, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import { GiSeedling } from "react-icons/gi";
import Shop from "./pages/Shop";
import ProductPage from "./pages/ProductPage";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Orders from "./pages/Orders";
import Resell from "./pages/Resell";
import SellerPortal from "./pages/SellerPortal";
import FacilityPortal from "./pages/FacilityPortal";
import HealthCard from "./pages/HealthCard";
import PreLoved from "./pages/PreLoved";
import Rewards from "./pages/Rewards";

function Guard({ need, children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="page muted">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (need && user.role !== need) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  const { user, logout } = useAuth();
  return (
    <>
      <nav className="nav">
        <NavLink to="/" className="brand">
          Loop
        </NavLink>
        <NavLink to="/">Shop</NavLink>
        {user && <NavLink to="/orders">Orders</NavLink>}
        {user && <NavLink to="/resell">Resell</NavLink>}
        {user?.role === "SELLER" && <NavLink to="/seller">Seller</NavLink>}
        {user?.role === "FACILITY" && (
          <NavLink to="/facility">Facility</NavLink>
        )}
        <NavLink to="/preloved">Pre-Loved</NavLink>
        <span className="spacer" />
        {user ? (
          <>
            <span className="muted">
              {user.username} · {user.role}
            </span>
            <NavLink to="/rewards" className="muted">
              <GiSeedling style={{ marginRight: 6 }} />{" "}
              {user.green_credits?.balance ?? 0}
            </NavLink>
            <button className="secondary" onClick={logout}>
              Logout
            </button>
          </>
        ) : (
          <NavLink to="/login">Login</NavLink>
        )}
      </nav>
      <Routes>
        <Route path="/" element={<Shop />} />
        <Route path="/p/:id" element={<ProductPage />} />
        <Route path="/preloved" element={<PreLoved />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/unit/:id" element={<HealthCard />} />
        <Route
          path="/orders"
          element={
            <Guard>
              <Orders />
            </Guard>
          }
        />
        <Route
          path="/resell"
          element={
            <Guard>
              <Resell />
            </Guard>
          }
        />
        <Route
          path="/seller/*"
          element={
            <Guard need="SELLER">
              <SellerPortal />
            </Guard>
          }
        />
        <Route
          path="/facility/*"
          element={
            <Guard need="FACILITY">
              <FacilityPortal />
            </Guard>
          }
        />
        <Route
          path="/rewards"
          element={
            <Guard>
              <Rewards />
            </Guard>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}
