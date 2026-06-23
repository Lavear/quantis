# Quantis — System Architecture

```
                    ┌─────────────────────────────┐
                    │   React + TS + Vite (5173)   │
                    │   Recharts dashboard         │
                    │   React Query · React Router │
                    └──────────────┬──────────────┘
                                   │ JWT (Bearer)  /api → :8000
                    ┌──────────────▼──────────────┐
                    │        FastAPI (8000)        │
                    │  routes → deps (auth)        │
                    │  ┌────────────────────────┐  │
                    │  │ services/finance.py    │  │  QFHS, risk, scenarios,
                    │  │ services/explain.py    │  │  Monte Carlo, forecast,
                    │  │ services/ml_forecast.py│  │  SHAP, recommendations
                    │  └────────────────────────┘  │
                    └──────────────┬──────────────┘
                                   │ SQLAlchemy
                    ┌──────────────▼──────────────┐
                    │      PostgreSQL (5432)       │
                    │  users, financial_profiles,  │
                    │  snapshots, scenario_results,│
                    │  risk_assessments, recs,     │
                    │  simulation_runs             │
                    └──────────────────────────────┘

   dataset/generate_dataset.py ──► users.csv ──► scripts/train_model.py ──► rf_model.joblib
```

## Request lifecycle (e.g. POST /monte-carlo)
1. Frontend attaches `Authorization: Bearer <jwt>`.
2. `deps.current_user` decodes the JWT and loads the `User`.
3. Route loads the user's `FinancialProfile`, maps it to a `Profile` dataclass.
4. `services.finance.monte_carlo` runs 1,000 vectorised-per-path simulations.
5. Result is persisted to `simulation_runs` and returned as JSON.
6. Recharts renders the histogram + probabilities.

## Design choices
- **Pure-function engine.** All financial math lives in `services/` with no DB or web
  dependencies, so it's unit-testable and reusable from scripts.
- **Closed-form SHAP.** QFHS is linear and additive, so exact Shapley values are
  `wᵢ·(componentᵢ − baseline)` — no KernelExplainer sampling, instant and exact.
- **RF as a second opinion.** The Random Forest is trained on the synthetic population
  and compared against the deterministic compound model rather than replacing it.
- **Stateless auth.** JWT means the API scales horizontally with no session store.
