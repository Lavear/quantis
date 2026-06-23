import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";

export default function Auth() {
  const nav = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("register");
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");

  async function submit() {
    setErr("");
    try {
      if (mode === "register") await api.register(email, pw);
      else await api.login(email, pw);
      nav(mode === "register" ? "/onboard" : "/");
    } catch (e: any) { setErr(e.message); }
  }

  return (
    <div className="wrap">
      <div className="auth panel">
        <div className="brand" style={{ marginBottom: 4 }}>Quant<span>is</span></div>
        <div className="label" style={{ marginBottom: 18 }}>Your financial digital twin</div>
        <div className="label">Email</div>
        <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
        <div className="label" style={{ marginTop: 12 }}>Password</div>
        <input className="input" type="password" value={pw} onChange={(e) => setPw(e.target.value)} placeholder="••••••••" />
        {err && <div className="pill poor" style={{ marginTop: 12 }}>{err}</div>}
        <button className="btn" style={{ width: "100%", marginTop: 18 }} onClick={submit}>
          {mode === "register" ? "Create account" : "Sign in"}
        </button>
        <div className="label" style={{ marginTop: 16, textAlign: "center", cursor: "pointer" }}
          onClick={() => setMode(mode === "register" ? "login" : "register")}>
          {mode === "register" ? "Have an account? Sign in" : "New here? Create an account"}
        </div>
      </div>
    </div>
  );
}
