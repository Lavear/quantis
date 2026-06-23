"""Core financial algorithms: QFHS, risk, scenarios, Monte Carlo, forecasting."""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass, asdict

WEIGHTS = {"S": 0.25, "L": 0.20, "D": 0.20, "I": 0.20, "R": 0.15}


@dataclass
class Profile:
    age: int
    salary: float            # annual
    monthly_expenses: float
    savings: float
    investments: float
    debt: float
    assets: float


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def savings_score(p: Profile) -> float:
    monthly_income = p.salary / 12
    if monthly_income <= 0:
        return 0.0
    rate = (monthly_income - p.monthly_expenses) / monthly_income
    return _clamp(rate / 0.20 * 100)  # 20%+ savings rate -> full marks


def liquidity_score(p: Profile) -> float:
    if p.monthly_expenses <= 0:
        return 100.0
    months = p.savings / p.monthly_expenses
    return _clamp(months / 6 * 100)  # 6 months cover -> full marks


def debt_score(p: Profile) -> float:
    if p.salary <= 0:
        return 0.0 if p.debt > 0 else 100.0
    dti = p.debt / p.salary
    return _clamp((1 - dti / 0.5) * 100)  # DTI 0 -> 100, 0.5+ -> 0


def investment_score(p: Profile) -> float:
    net_worth = p.savings + p.investments + p.assets - p.debt
    if net_worth <= 0:
        return 0.0
    ratio = p.investments / net_worth
    return _clamp(ratio / 0.40 * 100)  # 40%+ invested -> full marks


def risk_resilience(p: Profile) -> float:
    """Months of survival without income."""
    if p.monthly_expenses <= 0:
        return 99.0
    liquid = p.savings + 0.5 * p.investments
    return liquid / p.monthly_expenses


def resilience_score(p: Profile) -> float:
    return _clamp(risk_resilience(p) / 12 * 100)  # 12 months -> full marks


def qfhs(p: Profile) -> dict:
    S = savings_score(p)
    L = liquidity_score(p)
    D = debt_score(p)
    I = investment_score(p)
    R = resilience_score(p)
    score = (WEIGHTS["S"] * S + WEIGHTS["L"] * L + WEIGHTS["D"] * D
             + WEIGHTS["I"] * I + WEIGHTS["R"] * R)
    if score <= 40:
        cat = "Poor"
    elif score <= 60:
        cat = "Fair"
    elif score <= 80:
        cat = "Good"
    else:
        cat = "Excellent"
    return {
        "score": round(score, 1),
        "category": cat,
        "components": {"S": round(S, 1), "L": round(L, 1), "D": round(D, 1),
                       "I": round(I, 1), "R": round(R, 1)},
        "months_survival": round(risk_resilience(p), 1),
    }


# ---------- Scenario engine ----------
def apply_scenario(p: Profile, name: str) -> Profile:
    q = Profile(**asdict(p))
    if name == "job_loss":
        q.salary = 0.0
    elif name == "inflation_shock":
        q.monthly_expenses *= 1.15
    elif name == "market_crash":
        q.investments *= 0.70
    elif name == "medical_emergency":
        loss = 0.4 * (q.savings + q.investments)
        q.savings = max(0.0, q.savings - loss)
    elif name == "promotion":
        q.salary *= 1.20
    elif name == "investment_boom":
        q.investments *= 1.30
    return q


SCENARIOS = ["job_loss", "inflation_shock", "market_crash",
             "medical_emergency", "promotion", "investment_boom"]


def simulate_scenario(p: Profile, name: str) -> dict:
    q = apply_scenario(p, name)
    h = qfhs(q)
    net_worth = q.savings + q.investments + q.assets - q.debt
    return {
        "scenario": name,
        "future_wealth": round(net_worth, 2),
        "qfhs": h["score"],
        "category": h["category"],
        "months_survival": h["months_survival"],
    }


# ---------- Monte Carlo ----------
def monte_carlo(p: Profile, years: int = 5, runs: int = 1000,
                target_wealth: float | None = None, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    months = years * 12
    net_worth0 = p.savings + p.investments + p.assets - p.debt
    target = target_wealth if target_wealth else net_worth0 * 2

    finals = np.empty(runs)
    distress = 0
    for i in range(runs):
        savings, inv, debt = p.savings, p.investments, p.debt
        salary_m, exp = p.salary / 12, p.monthly_expenses
        hit_distress = False
        for _ in range(months):
            salary_m *= (1 + rng.normal(0.005 / 12, 0.01))
            exp *= (1 + rng.normal(0.005, 0.004))
            inv *= (1 + rng.normal(0.08 / 12, 0.15 / np.sqrt(12)))
            savings += salary_m - exp
            if rng.random() < 0.01:                       # 1%/mo emergency
                savings -= 0.3 * (savings + inv)
            if debt > 0:
                debt = max(0.0, debt - 0.02 * debt)
            if savings < 0:
                hit_distress = True
                inv += savings
                savings = 0.0
        finals[i] = savings + inv + p.assets - debt
        if hit_distress:
            distress += 1

    hist, edges = np.histogram(finals, bins=30)
    return {
        "runs": runs, "years": years,
        "mean_wealth": round(float(finals.mean()), 2),
        "median_wealth": round(float(np.median(finals)), 2),
        "p10": round(float(np.percentile(finals, 10)), 2),
        "p90": round(float(np.percentile(finals, 90)), 2),
        "prob_reach_target": round(float((finals >= target).mean()), 3),
        "prob_distress": round(distress / runs, 3),
        "target_wealth": round(target, 2),
        "histogram": hist.tolist(),
        "bin_edges": [round(x, 2) for x in edges.tolist()],
    }


# ---------- Forecast ----------
def forecast_compound(p: Profile, years_list=(1, 3, 5, 10),
                      growth: float = 0.08) -> list[dict]:
    out = []
    nw = p.savings + p.investments + p.assets - p.debt
    annual_savings = max(0.0, p.salary - p.monthly_expenses * 12)
    for yr in years_list:
        fv_assets = nw * (1 + growth) ** yr
        fv_contrib = (annual_savings * (((1 + growth) ** yr - 1) / growth)
                      if growth else annual_savings * yr)
        out.append({"year": yr, "net_worth": round(fv_assets + fv_contrib, 2)})
    return out
