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

### NEON DATABASE SETUP

1. Go to [neon.tech](https://neon.tech) → New Project → copy `DATABASE_URL`
2. Format: `postgresql+asyncpg://user:pass@host/dbname`
3. Run: `cd backend && alembic upgrade head`

### UPSTASH REDIS SETUP

1. Go to [upstash.com](https://upstash.com) → Create Database → Redis
2. Copy `REDIS_URL` (starts with `rediss://`)

### RENDER DEPLOYMENT (Backend)

1. New Web Service → Connect GitHub repo
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add all env vars from `.env.example`
6. Note the public URL (e.g. `https://xeno-crm.onrender.com`)

### RENDER DEPLOYMENT (Celery Worker)

1. New Background Worker → same repo
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `celery -A app.tasks.celery_app worker --loglevel=info`
5. Same env vars as backend

### RENDER DEPLOYMENT (Channel Stub)

1. New Web Service → same repo
2. Root Directory: `channel-stub`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Note the URL → set as `CHANNEL_STUB_URL` in backend env vars

### VERCEL DEPLOYMENT (Frontend)

1. Import GitHub repo in [Vercel](https://vercel.com)
2. Root Directory: `frontend`
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Add env var: `VITE_API_URL=https://your-backend.onrender.com`
6. Deploy

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
