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

This project is configured for **Railway** via a single multi-service `railway.json`
at the repo root. The file declares four services that Railway will create
together when you link the repo.

### One-time setup

1. Sign in at [railway.app](https://railway.app) with your GitHub account.
2. **New Project → Deploy from GitHub repo** → pick `crm-application`.
3. Railway reads `railway.json` and creates four services:
   `backend`, `celery-worker`, `channel-stub`, `frontend`.

### Add databases (Postgres + Redis)

4. In the project, click **+ New → Database → PostgreSQL**. After it
   provisions, right-click it → **Variables** and copy the `DATABASE_URL`.
5. Click **+ New → Database → Redis**. Copy `REDIS_URL` and `REDIS_PRIVATE_URL`.

> The Postgres plugin exposes `DATABASE_URL` (sync, `postgresql://…`); the
> backend needs the async driver, so for the backend service set
> `DATABASE_URL=postgresql+asyncpg://…` (same host/user/pass/db, just
> the scheme prefix and driver).

### Wire env vars on the four services

For **`backend`**:

```
DATABASE_URL=postgresql+asyncpg://<from step 4>
REDIS_URL=redis://<from step 5>
GROQ_API_KEY=<your key>
CORS_ORIGINS=https://<frontend-domain>.up.railway.app
```

The backend's other vars (`CHANNEL_STUB_URL`, `CRM_BASE_URL`) are auto-set
by the steps below once those services have public URLs.

For **`channel-stub`**: none required.

For **`celery-worker`**: same vars as `backend`.

For **`frontend`**:

```
VITE_API_URL=https://<backend-domain>.up.railway.app
```

> `VITE_API_URL` is a **build-time** variable. If you change it later you
> must trigger a redeploy of the frontend service so the new value gets
> baked into the JS bundle.

### Cross-service URLs (the order matters)

6. Deploy everything once. After `channel-stub` and `backend` get public
   URLs, go to **`channel-stub` → Variables** and add `PORT=8001` (Railway
   default is fine; the stub's startCommand reads `$PORT`).
7. Copy the **`channel-stub`** public URL. On the **`backend`** service,
   set `CHANNEL_STUB_URL=<that-url>` and `CRM_BASE_URL=<backend-public-url>`.
8. Copy the **`backend`** public URL. On the **`frontend`** service, set
   `VITE_API_URL=<that-url>` and **redeploy** the frontend so the new
   value is baked into the bundle.
9. Copy the **`frontend`** public URL. Back on **`backend`**, update
   `CORS_ORIGINS` to include it, then redeploy the backend.

### Domain (optional)

10. On the `frontend` service → **Settings → Networking → Generate Domain**
    or attach a custom one. The included nginx config already serves the
    Vite build with an SPA rewrite (`try_files` → `index.html`).

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
