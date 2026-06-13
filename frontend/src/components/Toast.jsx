import { createContext, useContext, useState } from "react";
import {
  FaCheckCircle,
  FaExclamationCircle,
  FaInfoCircle,
} from "react-icons/fa";

const ToastCtx = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const push = (msg, level = "info") => {
    const id = Date.now() + Math.random();
    setToasts((t) => [...t, { id, msg, level }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3500);
  };
  const remove = (id) => setToasts((t) => t.filter((x) => x.id !== id));
  return (
    <ToastCtx.Provider value={{ push, remove }}>
      {children}
      <div style={{ position: "fixed", right: 18, top: 18, zIndex: 9999 }}>
        {toasts.map((t) => (
          <div
            key={t.id}
            className="no-hover"
            role="status"
            aria-live="polite"
            style={{
              background: "#232a37",
              color: "#e8eaf0",
              padding: "10px 14px",
              borderRadius: 8,
              marginBottom: 8,
              boxShadow: "0 6px 18px rgba(0,0,0,0.6)",
              minWidth: 220,
            }}
          >
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <div
                style={{
                  fontWeight: 700,
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                {t.level === "error" ? (
                  <FaExclamationCircle color="#ff6b6b" />
                ) : t.level === "success" ? (
                  <FaCheckCircle color="#6ee7b7" />
                ) : (
                  <FaInfoCircle color="#60a5fa" />
                )}
                <div>
                  {t.level === "error"
                    ? "Error"
                    : t.level === "success"
                      ? "Success"
                      : "Info"}
                </div>
              </div>
            </div>
            <div style={{ marginTop: 6 }}>{t.msg}</div>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}

export const useToast = () => useContext(ToastCtx);
