import { useEffect, useState } from "react";

import { clearSession, getSession, onUnauthorized, saveSession } from "./api";
import Categories from "./components/Categories";
import Customers from "./components/Customers";
import Login from "./components/Login";
import Orders from "./components/Orders";
import { addToastListener, toast } from "./toast";
import type { Session } from "./types";

type View = "login" | "customers" | "orders" | "categories";

const TABS: { id: Exclude<View, "login">; label: string }[] = [
  { id: "customers", label: "Customers" },
  { id: "orders", label: "Orders" },
  { id: "categories", label: "Categories" },
];

export default function App() {
  const [session, setSession] = useState<Session | null>(() => getSession());
  const [view, setView] = useState<View>("customers");
  const [toastMessage, setToastMessage] = useState("");

  const isAuthed = session !== null;

  useEffect(() => {
    // Any 401 from the API drops the session and shows the login view.
    onUnauthorized(() => {
      setSession(null);
      setView("login");
    });
  }, []);

  useEffect(() => addToastListener(setToastMessage), []);

  useEffect(() => {
    if (!toastMessage) return;
    const timer = setTimeout(() => setToastMessage(""), 2500);
    return () => clearTimeout(timer);
  }, [toastMessage]);

  const handleLogin = (next: Session) => {
    saveSession(next.token, next.email);
    setSession(next);
    setView("customers");
    toast("Logged in");
  };

  const handleLogout = () => {
    clearSession();
    setSession(null);
    setView("login");
    toast("Logged out");
  };

  return (
    <>
      <header className="topbar">
        <div className="brand">Customer Management</div>
        <nav className="tabs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={`tab${view === tab.id ? " active" : ""}`}
              onClick={() => setView(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
        <div className="user">
          <span className="muted">{session?.email}</span>
          {isAuthed && (
            <button className="btn btn-ghost" onClick={handleLogout}>
              Log out
            </button>
          )}
        </div>
      </header>

      <main>
        {view === "login" && <Login onLogin={handleLogin} />}
        {view === "customers" && <Customers isAuthed={isAuthed} />}
        {view === "orders" && <Orders isAuthed={isAuthed} />}
        {view === "categories" && <Categories />}
      </main>

      <div className={`toast${toastMessage ? "" : " hidden"}`}>{toastMessage}</div>
    </>
  );
}
