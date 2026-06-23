import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar, AreaChart, Area,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";

const inr = (n: number) =>
  "₹" + Intl.NumberFormat("en-IN", { notation: "compact", maximumFractionDigits: 1 }).format(n);

const catClass = (c: string) =>
  c === "Excellent" || c === "Good" ? "good" : c === "Fair" ? "fair" : "poor";

function Kpi({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="panel">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value" style={accent ? { color: "var(--accent)" } : {}}>{value}</div>
    </div>
  );
}

const AX = { stroke: "#8b9ac0", fontSize: 12 };
const tip = { background: "#0d1426", border: "1px solid #243152", borderRadius: 8, color: "#e8edf7" };

export default function Dashboard() {
  const nav = useNavigate();
  const dash = useQuery({ queryKey: ["dash"], queryFn: api.dashboard });
  const scen = useQuery({ queryKey: ["scen"], queryFn: api.scenarios });
  const mc = useQuery({ queryKey: ["mc"], queryFn: () => api.monteCarlo(5, 1000) });
  const fc = useQuery({ queryKey: ["fc"], queryFn: () => api.forecast(0.08) });
  const rec = useQuery({ queryKey: ["rec"], queryFn: api.recommendations });

  if (dash.isLoading) return <div className="wrap">Loading your twin…</div>;
  if (dash.isError) return <div className="wrap">No profile yet. <a onClick={() => nav("/onboard")}>Set one up →</a></div>;

  const d = dash.data;
  const q = d.qfhs;
  const radar = Object.entries(q.components).map(([k, v]) => ({
    metric: { S: "Savings", L: "Liquidity", D: "Debt", I: "Investing", R: "Resilience" }[k], value: v,
  }));
  const mcBars = mc.data?.histogram.map((h: number, i: number) => ({ x: inr(mc.data.bin_edges[i]), n: h })) ?? [];

  return (
    <div className="wrap">
      <div className="topbar">
        <div className="brand">Quant<span>is</span></div>
        <button className="btn ghost" onClick={() => { api.logout(); nav("/auth"); }}>Sign out</button>
      </div>

      <div className="row2">
        <div className="panel" style={{ display: "flex", alignItems: "center", gap: 22 }}>
          <div>
            <div className="kpi-label">Financial Health Score</div>
            <div className="score-ring" style={{ color: "var(--accent)" }}>{q.score}</div>
            <span className={`pill ${catClass(q.category)}`}>{q.category}</span>
          </div>
          <ResponsiveContainer width="60%" height={150}>
            <RadarChart data={radar}>
              <PolarGrid stroke="#243152" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: "#8b9ac0", fontSize: 11 }} />
              <Radar dataKey="value" stroke="#2dd4bf" fill="#2dd4bf" fillOpacity={0.35} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="grid cards">
          <Kpi label="Net worth" value={inr(d.net_worth)} accent />
          <Kpi label="Savings" value={inr(d.savings)} />
          <Kpi label="Investments" value={inr(d.investments)} />
          <Kpi label="Debt" value={inr(d.debt)} />
          <Kpi label="Months of survival" value={`${d.months_survival}`} />
        </div>
      </div>

      <div className="section-title">Wealth forecast — compound growth</div>
      <div className="panel">
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={fc.data?.forecast ?? []}>
            <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2dd4bf" stopOpacity={0.5} />
              <stop offset="100%" stopColor="#2dd4bf" stopOpacity={0} />
            </linearGradient></defs>
            <CartesianGrid stroke="#1b2742" />
            <XAxis dataKey="year" {...AX} tickFormatter={(y) => `${y}y`} />
            <YAxis {...AX} tickFormatter={inr} />
            <Tooltip contentStyle={tip} formatter={(v: any) => inr(v)} />
            <Area dataKey="net_worth" stroke="#2dd4bf" fill="url(#g)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="row2">
        <div>
          <div className="section-title">Scenario stress tests</div>
          <div className="panel">
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={scen.data?.results ?? []}>
                <CartesianGrid stroke="#1b2742" />
                <XAxis dataKey="scenario" {...AX} angle={-20} textAnchor="end" height={60} />
                <YAxis {...AX} />
                <Tooltip contentStyle={tip} />
                <Bar dataKey="qfhs" fill="#7c6cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div>
          <div className="section-title">Monte Carlo — 1,000 simulated futures (5y)</div>
          <div className="panel">
            <div className="label" style={{ marginBottom: 8 }}>
              P(reach target) <b style={{ color: "var(--good)" }}>{((mc.data?.prob_reach_target ?? 0) * 100).toFixed(0)}%</b>
              &nbsp;·&nbsp; P(distress) <b style={{ color: "var(--bad)" }}>{((mc.data?.prob_distress ?? 0) * 100).toFixed(0)}%</b>
              &nbsp;·&nbsp; median <b>{inr(mc.data?.median_wealth ?? 0)}</b>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={mcBars}>
                <XAxis dataKey="x" {...AX} hide />
                <YAxis {...AX} />
                <Tooltip contentStyle={tip} />
                <Bar dataKey="n" fill="#2dd4bf" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="section-title">Recommendations & explainability (SHAP)</div>
      <div className="row2">
        <div className="panel">
          {(rec.data?.recommendations ?? []).map((r: any, i: number) => (
            <div key={i} className="rec">{r.text}</div>
          ))}
        </div>
        <div className="panel">
          <div className="label" style={{ marginBottom: 8 }}>Why your score is what it is</div>
          {(rec.data?.explainability.explanations ?? []).map((e: string, i: number) => (
            <div key={i} style={{ padding: "6px 0", borderBottom: "1px solid #1b2742", fontSize: 14 }}>{e}</div>
          ))}
        </div>
      </div>
    </div>
  );
}
