# Quantis

**AI-Powered Financial Digital Twin for Wealth Forecasting, Risk Simulation, and Financial Decision Support.**

Quantis builds a *digital twin* of a user's financial life — income, expenses, savings, investments, debt, assets, and goals — and simulates how that life evolves under economic and personal shocks. Unlike a budgeting app that records the past, Quantis projects many possible futures.

---

## What's in this repo

```
quantis/
├── backend/        FastAPI + SQLAlchemy + the financial engine
│   └── app/
│       ├── api/        routes + auth dependencies
│       ├── core/       config, JWT + password hashing
│       ├── db/         SQLAlchemy session
│       ├── models/     ORM tables
│       ├── schemas/    Pydantic request/response models
│       └── services/   finance.py, explain.py, ml_forecast.py  ← the math
├── frontend/       React + TypeScript + Vite + Recharts dashboard
├── database/       PostgreSQL schema.sql
├── dataset/        10,000-user synthetic generator + users.csv
├── scripts/        train_model.py (Random Forest forecaster)
├── docker/         (compose lives at repo root)
├── docs/           architecture, install, deployment
└── docker-compose.yml
```

---

## The engine (services/finance.py)

Everything is plain, testable Python over a single `Profile` dataclass.

**QFHS — Quantis Financial Health Score** (0–100):

```
QFHS = 0.25·S + 0.20·L + 0.20·D + 0.20·I + 0.15·R
```

| Component | Meaning | Full-marks threshold |
|-----------|---------|----------------------|
| S | Savings rate | ≥ 20% of income |
| L | Liquidity | ≥ 6 months of expenses in savings |
| D | Debt management | debt-to-income → 0 |
| I | Investment efficiency | ≥ 40% of net worth invested |
| R | Risk resilience | ≥ 12 months survivable |

Bands: 0–40 Poor · 41–60 Fair · 61–80 Good · 81–100 Excellent.

**Risk resilience** — `(savings + ½·investments) / monthly_expenses` = months you survive with zero income.

**Scenario engine** — job loss, inflation shock (+15%), market crash (−30%), medical emergency, promotion (+20%), investment boom (+30%). Each returns future wealth, QFHS, category, and months of survival.

**Monte Carlo** — 1,000 paths over N years with stochastic salary growth, inflation, market returns, and 1%/month emergency shocks. Returns mean/median/P10/P90 wealth, probability of reaching the target, probability of distress, and a 30-bin histogram.

**Forecast** — deterministic compound growth **vs** a Random Forest trained on the synthetic population (`services/ml_forecast.py`). The `/forecast` endpoint returns both so you can compare.

**Explainability (services/explain.py)** — because QFHS is a linear additive model, each component's Shapley value is exact in closed form: `wᵢ·(componentᵢ − 50)`. No sampling needed, and it produces human-readable "why your score moved" sentences plus a recommendation list keyed off the weakest components.

---

## Quickstart (Docker)

```bash
git clone <your-repo> quantis && cd quantis
docker compose up --build
```

- API → http://localhost:8000  (interactive docs at `/docs`)
- Frontend → http://localhost:5173
- Postgres → localhost:5432 (`quantis` / `quantis`)

Schema auto-loads on first boot; tables are also created by SQLAlchemy at startup.

### Train the Random Forest (optional but recommended)

```bash
python scripts/train_model.py     # generates dataset if missing, writes rf_model.joblib
```

Without a trained model the `/forecast` endpoint still works — it just returns `random_forest: null` and you rely on the compound model.

---

## API

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/register` | – | Create account, returns JWT |
| POST | `/login` | – | OAuth2 password form, returns JWT |
| POST | `/profile` | ✓ | Create/update financial profile |
| GET | `/dashboard` | ✓ | KPIs + QFHS |
| POST | `/calculate-qfhs` | ✓ | Score breakdown |
| POST | `/simulate-scenario` | ✓ | One scenario or `{"scenario":"all"}` |
| POST | `/monte-carlo` | ✓ | 1,000-path simulation |
| POST | `/forecast` | ✓ | Compound vs Random Forest |
| GET | `/recommendations` | ✓ | Recommendations + SHAP explanations |

All protected routes expect `Authorization: Bearer <token>`.

---

## Local dev without Docker

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://quantis:quantis@localhost:5432/quantis"
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev      # proxies /api → backend
```

See `docs/INSTALL.md` and `docs/DEPLOYMENT.md` for details.

---

## Notes & honest limitations

- Synthetic data and the RF target are **illustrative**, not calibrated to real returns. Treat all projections as a modelling exercise, not investment advice.
- `JWT_SECRET` defaults to a placeholder — set a real one in production.
- Monte Carlo runs synchronously; for heavy concurrent load, move it to a task queue.
- This is a strong foundation covering all 9 modules end-to-end, intended to be extended (e.g. snapshot history charts, per-scenario persistence UI, real market data).
