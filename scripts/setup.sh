#!/usr/bin/env bash
# setup.sh — Bootstrap the local dev environment for crm-application
# Usage: bash scripts/setup.sh

set -euo pipefail

echo "[setup] Creating virtual environment at .venv..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "[setup] Upgrading pip..."
pip install --upgrade pip wheel setuptools

echo "[setup] Installing project requirements..."
if [ -f "backend/requirements.txt" ]; then
  pip install -r backend/requirements.txt
elif [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
fi

if [ -f "requirements-dev.txt" ]; then
  echo "[setup] Installing dev requirements (pytest, httpx)..."
  pip install -r requirements-dev.txt
fi

echo "[setup] Starting Postgres + Redis via docker-compose..."
if command -v docker >/dev/null 2>&1 && [ -f "docker-compose.yml" ]; then
  docker-compose up -d postgres redis
  echo "[setup] Waiting 5s for services to be ready..."
  sleep 5
else
  echo "[setup] docker/docker-compose not available — ensure Postgres + Redis are running manually"
fi

echo "[setup] Running database migrations..."
if command -v alembic >/dev/null 2>&1; then
  cd backend && alembic upgrade head && cd ..
else
  echo "[setup] alembic not installed — skipping migrations"
fi

echo "[setup] Seeding database..."
if [ -f "seed_data/generate_seed.py" ]; then
  python seed_data/generate_seed.py || echo "[setup] Seed script failed — see output"
else
  echo "[setup] seed_data/generate_seed.py not found — skipping seed"
fi

echo "[setup] Running test suite..."
pytest -q || echo "[setup] Tests failed — see output above"

echo "[setup] Done. Activate with: source .venv/bin/activate"