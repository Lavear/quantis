const BASE = import.meta.env.VITE_API_URL || "/api";

function token() { return localStorage.getItem("quantis_token"); }

async function req(path: string, opts: RequestInit = {}) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(opts.headers as Record<string, string>),
  };
  const t = token();
  if (t) headers["Authorization"] = `Bearer ${t}`;
  const res = await fetch(`${BASE}${path}`, { ...opts, headers });
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText);
  return res.json();
}

export const api = {
  async register(email: string, password: string) {
    const d = await req("/register", { method: "POST", body: JSON.stringify({ email, password }) });
    localStorage.setItem("quantis_token", d.access_token); return d;
  },
  async login(email: string, password: string) {
    const body = new URLSearchParams({ username: email, password });
    const res = await fetch(`${BASE}/login`, { method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
    if (!res.ok) throw new Error("Invalid credentials");
    const d = await res.json(); localStorage.setItem("quantis_token", d.access_token); return d;
  },
  logout() { localStorage.removeItem("quantis_token"); },
  isAuthed() { return !!token(); },
  saveProfile: (p: any) => req("/profile", { method: "POST", body: JSON.stringify(p) }),
  dashboard: () => req("/dashboard"),
  scenarios: () => req("/simulate-scenario", { method: "POST", body: JSON.stringify({ scenario: "all" }) }),
  monteCarlo: (years = 5, runs = 1000) => req("/monte-carlo", { method: "POST", body: JSON.stringify({ years, runs }) }),
  forecast: (growth = 0.08) => req("/forecast", { method: "POST", body: JSON.stringify({ growth }) }),
  recommendations: () => req("/recommendations"),
};
