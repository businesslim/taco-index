# TACO Index Production Deployment Design

**Goal:** Deploy the TACO Index service publicly using Railway (backend) + Vercel (frontend), connected to GitHub for automated CI/CD.

**Architecture:** FastAPI backend runs on Railway with managed PostgreSQL and Redis plugins. Next.js frontend is deployed on Vercel. Both platforms watch the GitHub repo (`businesslim/taco-index`) and auto-deploy on push to `main`.

**Tech Stack:** Railway (PaaS), Vercel, GitHub Actions (none needed — platform CI), nixpacks (Railway build), Vercel build system

---

## Infrastructure

```
GitHub (businesslim/taco-index)
       │
       ├─── Railway (backend service)
       │     ├── FastAPI via uvicorn          ← railway.toml already configured
       │     ├── PostgreSQL plugin            ← DATABASE_URL auto-injected
       │     └── Redis plugin                 ← REDIS_URL auto-injected
       │
       └─── Vercel (frontend service)
             └── Next.js 14 App Router        ← root dir: frontend/
```

## Environment Variables

### Railway (backend)
| Variable | Value |
|---|---|
| `ANTHROPIC_API_KEY` | `sk-ant-...` |
| `CORS_ORIGINS` | `https://<project>.vercel.app` |
| `POLL_INTERVAL_MINUTES` | `15` |
| `DATABASE_URL` | auto-injected by PostgreSQL plugin |
| `REDIS_URL` | auto-injected by Redis plugin |

### Vercel (frontend)
| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<project>.railway.app` |

## Deployment Steps

### Phase 1: Railway (backend)
1. Create Railway project at railway.app
2. Add PostgreSQL plugin → `DATABASE_URL` auto-configured
3. Add Redis plugin → `REDIS_URL` auto-configured
4. Set env vars: `ANTHROPIC_API_KEY`, `CORS_ORIGINS=https://placeholder.vercel.app`, `POLL_INTERVAL_MINUTES=15`
5. Connect GitHub repo (`businesslim/taco-index`), set root directory to `backend/`
6. Deploy — Railway uses `railway.toml` (nixpacks builder, uvicorn start command)
7. Open Railway Shell → run `alembic upgrade head` (one-time migration)
8. Note the Railway public URL (e.g., `https://taco-index-production.railway.app`)

### Phase 2: Vercel (frontend)
1. Create Vercel project at vercel.com, connect GitHub repo
2. Set root directory to `frontend/`
3. Set env var: `NEXT_PUBLIC_API_URL=https://<railway-url>`
4. Deploy
5. Note the Vercel public URL (e.g., `https://taco-index.vercel.app`)

### Phase 3: Wire up CORS
1. Go back to Railway → update `CORS_ORIGINS` to the actual Vercel URL
2. Redeploy (or Railway picks it up automatically on env change)

## Key Constraints

- `backend/.env` is gitignored — secrets never reach GitHub
- Alembic migrations must be run manually after the first deploy via Railway Shell; subsequent schema changes also require this
- The APScheduler background job (15-min polling) runs inside the same FastAPI process — Railway keeps it alive 24/7
- No Dockerfile needed — nixpacks auto-detects Python from `requirements.txt`

## Future: Custom Domain
When a domain is purchased:
1. Railway: Settings → Custom Domain → add `api.yourdomain.com`
2. Vercel: Settings → Domains → add `yourdomain.com`
3. Update Railway `CORS_ORIGINS` and Vercel `NEXT_PUBLIC_API_URL` accordingly
