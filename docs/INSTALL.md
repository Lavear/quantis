# Installation

## Prerequisites
- Docker + Docker Compose, **or**
- Python 3.12, Node 20, PostgreSQL 16 for manual setup.

## Option A — Docker (recommended)
```bash
docker compose up --build
```
First boot loads `database/schema.sql` and starts all three services.
- API: http://localhost:8000/docs
- Web: http://localhost:5173

## Option B — Manual

### 1. Database
```bash
createdb quantis
psql quantis < database/schema.sql
```

### 2. Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit JWT_SECRET + DATABASE_URL
uvicorn app.main:app --reload --port 8000
```

### 3. Dataset + model (optional)
```bash
cd dataset && python generate_dataset.py      # writes users.csv (10k rows)
cd ..      && python scripts/train_model.py   # writes backend/app/services/rf_model.joblib
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Verifying
```bash
curl -X POST localhost:8000/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@quantis.app","password":"demo12345"}'
```
A JWT in the response means everything is wired correctly.
