"""Module 7 (ML half): Random Forest wealth forecaster.

Trains on the synthetic dataset to predict net-worth growth multiples, then
compares against the deterministic compound-growth model. Falls back to the
compound model if no trained artifact is present.
"""
from __future__ import annotations
import os, joblib, numpy as np, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from app.services.finance import Profile, forecast_compound

MODEL_PATH = os.getenv("RF_MODEL_PATH", "app/services/rf_model.joblib")
FEATURES = ["age", "salary", "monthly_expenses", "savings",
            "investments", "debt", "assets"]


def train(csv_path: str, out: str = MODEL_PATH) -> dict:
    df = pd.read_csv(csv_path)
    df["net_worth"] = df.savings + df.investments + df.assets - df.debt
    # Synthetic target: 5y growth multiple driven by savings rate + risk.
    rate = (df.salary / 12 - df.monthly_expenses).clip(lower=0) / (df.salary / 12 + 1)
    risk_mult = df.risk_appetite.map(
        {"conservative": 0.06, "moderate": 0.09, "aggressive": 0.12}).fillna(0.08)
    y = (1 + risk_mult + 0.5 * rate) ** 5
    model = RandomForestRegressor(n_estimators=120, max_depth=12, random_state=42)
    model.fit(df[FEATURES], y)
    joblib.dump(model, out)
    return {"trained_on": len(df), "saved": out,
            "train_r2": round(float(model.score(df[FEATURES], y)), 3)}


def forecast_rf(p: Profile, years_list=(1, 3, 5, 10)) -> list[dict] | None:
    if not os.path.exists(MODEL_PATH):
        return None
    model = joblib.load(MODEL_PATH)
    x = pd.DataFrame([[getattr(p, f) for f in FEATURES]], columns=FEATURES)
    mult5 = float(model.predict(x)[0])
    annual = mult5 ** (1 / 5) - 1                  # implied annual rate
    nw = p.savings + p.investments + p.assets - p.debt
    return [{"year": y, "net_worth": round(nw * (1 + annual) ** y, 2)} for y in years_list]


def compare(p: Profile) -> dict:
    return {"compound": forecast_compound(p), "random_forest": forecast_rf(p)}
