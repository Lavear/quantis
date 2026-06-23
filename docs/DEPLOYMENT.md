# Deployment

## Environment variables (backend)
| Var | Purpose |
|-----|---------|
| `DATABASE_URL` | Postgres connection string |
| `JWT_SECRET` | **Set a long random value in production** |
| `JWT_ALGORITHM` | default HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | token lifetime (default 1440) |
| `RF_MODEL_PATH` | path to the trained Random Forest artifact |

## Production checklist
- [ ] Replace `JWT_SECRET` with a 32+ byte random secret (`openssl rand -hex 32`).
- [ ] Restrict CORS `allow_origins` to your real frontend domain (currently `*`).
- [ ] Put the API behind HTTPS (reverse proxy: Caddy / Nginx / cloud LB).
- [ ] Run the DB as a managed service; keep `pgdata` volume backed up.
- [ ] Pre-train `rf_model.joblib` in CI and bake it into the backend image.
- [ ] Move Monte Carlo to a worker (Celery/RQ) if you expect concurrent heavy runs.
- [ ] Set `uvicorn`/gunicorn worker count to match CPU; the engine is CPU-bound.

## Build & run images
```bash
docker compose build
docker compose up -d
docker compose logs -f backend
```

## Scaling notes
- The API is stateless (JWT), so scale `backend` replicas horizontally behind a load balancer.
- Postgres is the single source of truth; use read replicas only if dashboard reads dominate.
- Frontend builds to static assets (`npm run build`) and can be served from any CDN;
  point `VITE_API_URL` at the public API origin.
