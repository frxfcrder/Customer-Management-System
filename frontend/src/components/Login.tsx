import { useState, type FormEvent } from "react";

import { api } from "../api";
import type { Session } from "../types";

export default function Login({ onLogin }: { onLogin: (session: Session) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      const res = await api<{ access_token: string }>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: email.trim(), password }),
      });
      onLogin({ token: res.access_token, email: email.trim() });
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <section className="card login-card">
      <h2>Sign in</h2>
      <p className="muted">Log in to create and edit records.</p>
      <form onSubmit={submit}>
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
            placeholder="••••••••"
            required
          />
        </label>
        <button className="btn btn-primary" type="submit">
          Log in
        </button>
        {error && <p className="error">{error}</p>}
      </form>
      <p className="muted small">Browsing needs no login — only writes are protected.</p>
    </section>
  );
}
