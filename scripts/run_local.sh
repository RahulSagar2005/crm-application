#!/usr/bin/env bash
# run_local.sh — Bring up the entire CRM stack locally (backend, channel-stub, celery worker, frontend)
# Usage: bash scripts/run_local.sh
# Requires: docker-compose, and ports 5432, 6379, 8000, 8001, 5173 to be free.

set -euo pipefail

echo "[local] Starting Postgres + Redis..."
docker-compose up -d postgres redis

echo "[local] Waiting for services to be ready..."
sleep 5

echo "[local] Running migrations..."
if [ -f "backend/alembic.ini" ]; then
  (cd backend && alembic upgrade head)
fi

echo "[local] Starting backend on :8000..."
(cd backend && uvicorn main:app --reload --port 8000) &
BACKEND_PID=$!

echo "[local] Starting channel-stub on :8001..."
if [ -f "channel-stub/main.py" ]; then
  (cd channel-stub && uvicorn main:app --reload --port 8001) &
  CHANNEL_PID=$!
fi

echo "[local] Starting Celery worker..."
(cd backend && celery -A celery_app worker --loglevel=info) &
CELERY_PID=$!

echo "[local] Starting frontend on :5173..."
if [ -f "frontend/package.json" ]; then
  (cd frontend && npm run dev) &
  FRONTEND_PID=$!
fi

echo "[local] Stack started. PIDs: backend=$BACKEND_PID celery=$CELERY_PID frontend=${FRONTEND_PID:-n/a}"
echo "[local] Press Ctrl+C to stop all services."

trap 'echo "[local] Stopping..."; kill $BACKEND_PID ${CHANNEL_PID:-} $CELERY_PID ${FRONTEND_PID:-} 2>/dev/null; docker-compose stop postgres redis; exit' INT TERM

wait