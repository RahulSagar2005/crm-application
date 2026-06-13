# XenoCRM — AI-Native Mini CRM for BrewCo

A production-ready Mini CRM that helps marketers ingest customer data, segment audiences with AI, launch WhatsApp/SMS/Email campaigns, and track delivery analytics.

## Architecture

- **Frontend** (React + Vite + Tailwind) — port 5173
- **CRM Backend** (FastAPI + PostgreSQL + Celery) — port 8000
- **Channel Stub** (FastAPI message simulator) — port 8001

## Quick Start (Local)

### Step 1: Dependencies

```bash
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
cd ../channel-stub && pip install -r requirements.txt
```

### Step 2: Environment Files

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
cp channel-stub/.env.example channel-stub/.env
```

Edit `backend/.env` and add your `GROQ_API_KEY` (optional — fallback rules work without it).

### Step 3: Start Database + Redis

```bash
docker-compose up postgres redis -d
```

### Step 4: Database Migration

```bash
cd backend
alembic upgrade head
```

### Step 5: Start All Services

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Celery Worker:**
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 3 — Channel Stub:**
```bash
cd channel-stub
uvicorn main:app --reload --port 8001
```

**Terminal 4 — Frontend:**
```bash
cd frontend
npm run dev
```

### Step 6: Seed Data

```bash
cd backend
python seed_data/generate_seed.py
```

Open **http://localhost:5173**

---

## Deployment

This project is configured for **Railway** with one `railway.json` per
service, each placed inside the service's own directory. The `builder`
is explicitly set to `DOCKERFILE` so Railway uses the existing
Dockerfiles (it would otherwise fall back to Railpack, which can't
build this monorepo because it scans only the repo root for language
markers).

### One-time setup

1. Sign in at [railway.app](https://railway.app) with your GitHub account.
2. **New Project → Empty Project** (do NOT pick "Deploy from GitHub"
   — that auto-detects one service; we need four).
3. From inside the project, create the four services. For each one
   click **+ New → GitHub Repo** and pick `crm-application`. Railway
   will create a service whose name is the repo name — that's fine,
   we'll rename below.
4. After each service is created, open it and configure:
   - **Settings → Service Name** → rename to one of: `backend`,
     `celery-worker`, `channel-stub`, `frontend`.
   - **Settings → Root Directory** → set to the matching subdirectory
     (`backend`, `backend`, `channel-stub`, `frontend` respectively).
     The Root Directory sets the build context for the Dockerfile.
   - **Settings → Config File Path** → for the worker only, set this
     to `/backend/railway.worker.json`. The other three use the
     default `railway.json` in their Root Directory.

   The point of the worker having its own config: the `startCommand`
   differs (`celery ...` vs `uvicorn ...`), so it needs a different
   deploy block.

### Add databases (Postgres + Redis)

5. In the project, click **+ New → Database → PostgreSQL**. After it
   provisions, right-click it → **Variables** and copy `DATABASE_URL`.
6. Click **+ New → Database → Redis**. Copy `REDIS_URL`.

> Railway's Postgres plugin exposes `DATABASE_URL` as
> `postgresql://…` (sync, psycopg). The backend needs the async
> driver, so for the `backend` service set
> `DATABASE_URL=postgresql+asyncpg://…` (same host/user/pass/db, just
> the scheme prefix).

### Wire env vars on the four services

For **`backend`**:

```
DATABASE_URL=postgresql+asyncpg://<from step 5>
REDIS_URL=redis://<from step 6>
GROQ_API_KEY=<your key>
CORS_ORIGINS=https://<frontend-domain>.up.railway.app
```

For **`channel-stub`**: none required (Railway injects `PORT`).

For **`celery-worker`**: same vars as `backend`.

For **`frontend`**:

```
VITE_API_URL=https://<backend-domain>.up.railway.app
```

> `VITE_API_URL` is a **build-time** variable — it gets baked into the
> JS bundle by Vite. If you change it later you must trigger a redeploy
> of the frontend so the new value gets baked in.

### Cross-service URLs (the order matters)

7. Trigger a first deploy on every service so Railway hands out public
   URLs.
8. Copy the **`channel-stub`** public URL. On the **`backend`** service,
   set `CHANNEL_STUB_URL=<that-url>` and `CRM_BASE_URL=<backend-public-url>`,
   then redeploy backend.
9. Copy the **`backend`** public URL. On the **`frontend`** service, set
   `VITE_API_URL=<that-url>` and **redeploy** the frontend so the new
   value is baked into the bundle.
10. Copy the **`frontend`** public URL. Back on **`backend`**, update
    `CORS_ORIGINS` to include it, then redeploy the backend.

### Domain (optional)

11. On the `frontend` service → **Settings → Networking → Generate Domain**
    or attach a custom one. The included nginx config already serves
    the Vite build with an SPA rewrite (`try_files` → `index.html`).

### Local reminder

`docker compose up` still works for local dev — nothing in it changed.
Only the deploy target moved from Render to Railway.

### SEED DATA

After all services are up:

```bash
cd backend
pip install -r requirements.txt
python seed_data/generate_seed.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/customers` | List customers |
| POST | `/api/customers/upload-csv` | Bulk CSV upload |
| POST | `/api/segments/ai-suggest` | AI segment builder |
| POST | `/api/campaigns/{id}/launch` | Launch campaign |
| GET | `/api/analytics/{campaign_id}` | Campaign analytics |
| POST | `/api/receipts` | Delivery callbacks (channel stub) |

## Tech Stack

- **Frontend:** React 18, Vite, TailwindCSS, TanStack Query, Recharts
- **Backend:** FastAPI, SQLAlchemy 2.0, Alembic, Celery, Redis, Groq AI
- **Database:** PostgreSQL
- **Channel Stub:** FastAPI async delivery simulator

## License

MIT
