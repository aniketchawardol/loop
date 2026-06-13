import { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const reload = async () => {
    try {
      const d = await api.get("/auth/me");
      setUser(d.user);
      return d.user;
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    api
      .get("/auth/me")
      .then((d) => setUser(d.user))
      .finally(() => setLoading(false));
  }, []);

  const login = async (username, password) => {
    const u = await api.post("/auth/login", { username, password });
    setUser(u);
    return u;
  };
  const register = async (username, password, role) => {
    const u = await api.post("/auth/register", { username, password, role });
    setUser(u);
    return u;
  };
  const logout = async () => {
    await api.post("/auth/logout");
    setUser(null);
  };

  return (
    <AuthCtx.Provider
      value={{ user, loading, login, register, logout, reload }}
    >
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
