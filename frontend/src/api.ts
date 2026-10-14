import type { Session } from "./types";

export class ApiError extends Error {}

let token = localStorage.getItem("token") ?? "";
let email = localStorage.getItem("user_email") ?? "";
let unauthorizedHandler: (() => void) | null = null;

export function getSession(): Session | null {
  return token ? { token, email } : null;
}

export function saveSession(newToken: string, newEmail: string): void {
  token = newToken;
  email = newEmail;
  localStorage.setItem("token", newToken);
  localStorage.setItem("user_email", newEmail);
}

export function clearSession(): void {
  token = "";
  email = "";
  localStorage.removeItem("token");
  localStorage.removeItem("user_email");
}

/** Called whenever the API answers 401 so the app can bounce to the login view. */
export function onUnauthorized(handler: () => void): void {
  unauthorizedHandler = handler;
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) ?? {}),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(path, { ...options, headers });

  if (res.status === 401 && !path.endsWith("/login")) {
    clearSession();
    unauthorizedHandler?.();
    throw new ApiError("Please log in to continue.");
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = (await res.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(detail);
  }

  return (await res.json()) as T;
}
