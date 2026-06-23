import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";

const fields: [string, string, string][] = [
  ["name", "Full name", "text"],
  ["age", "Age", "number"],
  ["salary", "Annual salary (₹)", "number"],
  ["monthly_expenses", "Monthly expenses (₹)", "number"],
  ["savings", "Savings (₹)", "number"],
  ["investments", "Investments (₹)", "number"],
  ["debt", "Outstanding debt (₹)", "number"],
  ["assets", "Other assets (₹)", "number"],
  ["financial_goal", "Target wealth goal (₹)", "number"],
];

export default function Onboard() {
  const nav = useNavigate();
  const [f, setF] = useState<Record<string, any>>({ risk_appetite: "moderate" });

  async function save() {
    const payload: any = { ...f };
    fields.forEach(([k, , t]) => { if (t === "number") payload[k] = Number(payload[k] || 0); });
    await api.saveProfile(payload);
    nav("/");
  }

  return (
    <div className="wrap">
      <div className="topbar"><div className="brand">Quant<span>is</span></div></div>
      <div className="panel" style={{ maxWidth: 720, margin: "0 auto" }}>
        <h2 style={{ marginTop: 0 }}>Build your digital twin</h2>
        <p className="label">We model your full financial ecosystem from these inputs.</p>
        <div className="grid" style={{ gridTemplateColumns: "1fr 1fr", gap: 14, marginTop: 14 }}>
          {fields.map(([k, label, t]) => (
            <div key={k}>
              <div className="label">{label}</div>
              <input className="input" type={t}
                onChange={(e) => setF({ ...f, [k]: e.target.value })} />
            </div>
          ))}
          <div>
            <div className="label">Risk appetite</div>
            <select className="input" onChange={(e) => setF({ ...f, risk_appetite: e.target.value })}>
              <option value="conservative">Conservative</option>
              <option value="moderate" selected>Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>
        </div>
        <button className="btn" style={{ marginTop: 20 }} onClick={save}>Generate twin →</button>
      </div>
    </div>
  );
}
