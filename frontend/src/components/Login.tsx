import { useState, type FormEvent } from "react";

import { api } from "../api";
import type { Session } from "../types";

type Mode = "login" | "register";

export default function Login({ onLogin }: { onLogin: (session: Session) => void }) {
  const [mode, setMode] = useState<Mode>("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const switchMode = (next: Mode) => {
    setMode(next);
    setError("");
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      const res =
        mode === "login"
          ? await api<{ access_token: string }>("/api/auth/login", {
              method: "POST",
              body: JSON.stringify({ email: email.trim(), password }),
            })
          : await api<{ access_token: string }>("/api/auth/register", {
              method: "POST",
              body: JSON.stringify({ name: name.trim() || null, email: email.trim(), password }),
            });
      onLogin({ token: res.access_token, email: email.trim() });
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <section className="card login-card">
      <h2>{mode === "login" ? "Sign in" : "Create account"}</h2>
      <p className="muted">
        {mode === "login"
          ? "Log in to create and edit records."
          : "Register the first account, then log in with it."}
      </p>

      <form onSubmit={submit}>
        {mode === "register" && (
          <label>
            Name
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Jane Doe"
            />
          </label>
        )}
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={mode === "register" ? "At least 8 characters" : "••••••••"}
            minLength={mode === "register" ? 8 : undefined}
            required
          />
        </label>
        <button className="btn btn-primary" type="submit">
          {mode === "login" ? "Log in" : "Register"}
        </button>
        {error && <p className="error">{error}</p>}
      </form>

      <p className="muted small">
        {mode === "login" ? (
          <>
            No account yet?{" "}
            <button className="link" type="button" onClick={() => switchMode("register")}>
              Create one
            </button>
          </>
        ) : (
          <>
            Already registered?{" "}
            <button className="link" type="button" onClick={() => switchMode("login")}>
              Sign in
            </button>
          </>
        )}
      </p>
      <p className="muted small">Browsing needs no login — only writes are protected.</p>
    </section>
  );
}
