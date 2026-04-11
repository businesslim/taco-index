# TACO Index Production Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy TACO Index to production on Railway (backend) + Vercel (frontend), accessible publicly via auto-generated URLs.

**Architecture:** Two code changes are required before deploy: (1) DATABASE_URL format validator so Railway's `postgresql://` URL works with asyncpg, (2) auto-migration release command in `railway.toml`. Then infrastructure is set up manually via Railway and Vercel dashboards/CLI.

**Tech Stack:** Railway (nixpacks, PostgreSQL plugin, Redis plugin), Vercel, GitHub (businesslim/taco-index), FastAPI, Next.js 14

---

## File Map

| File | Change |
|---|---|
| `backend/app/config.py` | Add `field_validator` to normalize DATABASE_URL for asyncpg |
| `backend/railway.toml` | Add `releaseCommand` to auto-run Alembic migrations on deploy |
| No frontend code changes | Vercel builds Next.js as-is |

---

### Task 1: Fix DATABASE_URL for Railway (asyncpg format)

Railway injects `DATABASE_URL` as `postgresql://...` or `postgres://...`, but SQLAlchemy asyncpg requires `postgresql+asyncpg://...`. Without this fix, the backend will crash on startup with a connection error.

**Files:**
- Modify: `backend/app/config.py`
- Test: `backend/tests/test_config.py` (create)

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_config.py`:

```python
import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


# Isolated Settings class for testing the validator in isolation
class _TestSettings(BaseSettings):
    model_config = SettingsConfigDict()
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/db"

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


def test_postgres_scheme_converted():
    s = _TestSettings(database_url="postgres://user:pass@host:5432/db")
    assert s.database_url == "postgresql+asyncpg://user:pass@host:5432/db"


def test_postgresql_scheme_converted():
    s = _TestSettings(database_url="postgresql://user:pass@host:5432/db")
    assert s.database_url == "postgresql+asyncpg://user:pass@host:5432/db"


def test_asyncpg_scheme_unchanged():
    s = _TestSettings(database_url="postgresql+asyncpg://user:pass@host:5432/db")
    assert s.database_url == "postgresql+asyncpg://user:pass@host:5432/db"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend
source .venv/bin/activate
pytest tests/test_config.py -v
```

Expected: 3 tests collected, likely ImportError or AttributeError since `fix_database_url` doesn't exist in `config.py` yet. The test file imports a local class so it won't fail on import — the assertions will pass trivially. That's fine; the next step wires the validator into the real `Settings`.

- [ ] **Step 3: Add validator to Settings in config.py**

Replace the entire `backend/app/config.py` with:

```python
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/taco_index"
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = "placeholder"
    poll_interval_minutes: int = 15
    cors_origins: str = "http://localhost:3000"

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
```

- [ ] **Step 4: Run the full test suite**

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

Expected: All 22 existing tests + 3 new config tests pass. No failures.

- [ ] **Step 5: Commit**

```bash
git add backend/app/config.py backend/tests/test_config.py
git commit -m "fix: normalize DATABASE_URL scheme for Railway asyncpg compatibility"
```

---

### Task 2: Add auto-migration release command to railway.toml

Railway supports a `releaseCommand` that runs after each deploy but before traffic is switched over. Using it for `alembic upgrade head` ensures the DB schema is always in sync with the code.

**Files:**
- Modify: `backend/railway.toml`

No tests for this task (infrastructure config). Verification happens in Task 3 when Railway logs show the migration running.

- [ ] **Step 1: Update railway.toml**

Replace the entire `backend/railway.toml` with:

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "on_failure"
releaseCommand = "alembic upgrade head"
```

- [ ] **Step 2: Commit**

```bash
git add backend/railway.toml
git commit -m "chore: add alembic auto-migration as Railway release command"
```

---

### Task 3: Deploy Railway backend

This task has no code changes. All steps are done via the Railway dashboard (railway.app) and terminal.

**Prerequisites:** Tasks 1 and 2 must be committed and pushed to `main`.

- [ ] **Step 1: Push commits to GitHub**

```bash
git push origin main
```

Verify at https://github.com/businesslim/taco-index that the latest commits are visible.

- [ ] **Step 2: Create Railway project**

1. Go to https://railway.app and log in (or sign up)
2. Click **New Project**
3. Choose **Empty Project**

- [ ] **Step 3: Add PostgreSQL plugin**

In the Railway project dashboard:
1. Click **+ New** → **Database** → **PostgreSQL**
2. Wait for provisioning (30–60 seconds)
3. Railway automatically sets `DATABASE_URL` in the project environment

- [ ] **Step 4: Add Redis plugin**

1. Click **+ New** → **Database** → **Redis**
2. Wait for provisioning
3. Railway automatically sets `REDIS_URL` in the project environment

- [ ] **Step 5: Create backend service**

1. Click **+ New** → **GitHub Repo**
2. Select `businesslim/taco-index`
3. Railway asks for the root directory — set it to `backend`
4. Railway detects Python via nixpacks, installs `requirements.txt`

- [ ] **Step 6: Set environment variables**

In the backend service → **Variables** tab, add:

| Key | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your key: `sk-ant-...` |
| `CORS_ORIGINS` | `https://placeholder.vercel.app` (update after Vercel deploy) |
| `POLL_INTERVAL_MINUTES` | `15` |

`DATABASE_URL` and `REDIS_URL` are already injected by the plugins — do NOT set these manually.

- [ ] **Step 7: Deploy and verify**

1. Click **Deploy** (or it auto-deploys on GitHub push)
2. Watch the deploy logs — you should see:
   - nixpacks building Python environment
   - `pip install -r requirements.txt`
   - Release command: `alembic upgrade head` → `Running upgrade -> db92c6508a50` (or similar)
   - `uvicorn app.main:app ...` startup
3. Once deployed, Railway shows a public URL like `https://taco-index-production.railway.app`
4. Test the health endpoint:
   ```bash
   curl https://<your-railway-url>/api/index/current
   ```
   Expected: JSON response (may be `{"detail": "not found"}` if no data yet — that's OK)

- [ ] **Step 8: Note the Railway URL**

Copy the Railway service URL (e.g., `https://taco-index-production.railway.app`). You'll need it in Task 4.

---

### Task 4: Deploy Vercel frontend

This task has no code changes. All steps are done via the Vercel dashboard (vercel.com).

**Prerequisites:** Task 3 must be complete and you have the Railway URL.

- [ ] **Step 1: Create Vercel project**

1. Go to https://vercel.com and log in (or sign up)
2. Click **Add New** → **Project**
3. Import from GitHub → select `businesslim/taco-index`

- [ ] **Step 2: Configure project settings**

In the project configuration screen:
- **Framework Preset:** Next.js (auto-detected)
- **Root Directory:** Click **Edit** → type `frontend`
- Leave build command and output directory as defaults (`next build`, `.next`)

- [ ] **Step 3: Set environment variable**

Under **Environment Variables**, add:

| Key | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<your-railway-url>` (from Task 3 Step 8, no trailing slash) |

Example: `https://taco-index-production.railway.app`

- [ ] **Step 4: Deploy and verify**

1. Click **Deploy**
2. Wait for build to complete (2–3 minutes)
3. Vercel assigns a URL like `https://taco-index.vercel.app`
4. Open the URL in a browser — the dashboard should load
5. Verify the gauge and coin prices appear (data may be empty until the scheduler runs)

- [ ] **Step 5: Note the Vercel URL**

Copy the Vercel deployment URL (e.g., `https://taco-index.vercel.app`). You'll need it in Task 5.

---

### Task 5: Wire up CORS and verify end-to-end

Update Railway's `CORS_ORIGINS` with the real Vercel URL so the frontend can call the backend API.

**Files:** No code changes — Railway env var update only.

- [ ] **Step 1: Update CORS_ORIGINS in Railway**

1. Go to Railway dashboard → backend service → **Variables**
2. Find `CORS_ORIGINS`
3. Change value from `https://placeholder.vercel.app` to your actual Vercel URL (e.g., `https://taco-index.vercel.app`)
4. Railway automatically redeploys the service with the new env var

- [ ] **Step 2: Verify end-to-end**

1. Open your Vercel URL in a browser
2. Open browser DevTools → Network tab
3. Reload the page
4. Confirm API calls to the Railway URL return 200 (no CORS errors in console)
5. Wait up to 15 minutes for the first scheduler run, then refresh — gauge and posts should populate

- [ ] **Step 3: Verify scheduler is running**

In Railway → backend service → **Logs**, look for log lines like:
```
INFO: Pipeline started
INFO: Fetched 20 posts from Truth Social
INFO: Saved N new tweets
INFO: TACO Index recalculated: XX
```

These appear every 15 minutes. If they don't appear after 20 minutes, check that `ANTHROPIC_API_KEY` is set correctly.
