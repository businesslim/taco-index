# TACO Index Deployment

## Backend (Railway)

1. Create new Railway project
2. Add PostgreSQL plugin → DATABASE_URL auto-configured
3. Add Redis plugin → REDIS_URL auto-configured
4. Set env var: `ANTHROPIC_API_KEY=sk-ant-...`
5. Deploy backend/ directory
6. Run migrations: `alembic upgrade head` (via Railway shell)

## Frontend (Vercel)

1. Connect GitHub repo to Vercel
2. Set root directory to `frontend/`
3. Set env var: `NEXT_PUBLIC_API_URL=https://your-backend.railway.app`
4. Deploy
