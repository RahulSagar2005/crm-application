#!/usr/bin/env bash
# db_healthcheck.sh — Quick health check for Postgres + Redis used by the CRM
# Usage: bash scripts/db_healthcheck.sh

set -euo pipefail

POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

fail=0

echo "[health] Checking Postgres at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
if command -v pg_isready >/dev/null 2>&1; then
  if pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -q; then
    echo "[health] Postgres: OK"
  else
    echo "[health] Postgres: FAIL" >&2
    fail=1
  fi
else
  echo "[health] pg_isready not installed — skipping Postgres check"
fi

echo "[health] Checking Redis at ${REDIS_HOST}:${REDIS_PORT}..."
if command -v redis-cli >/dev/null 2>&1; then
  if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping | grep -q "PONG"; then
    echo "[health] Redis: OK"
  else
    echo "[health] Redis: FAIL" >&2
    fail=1
  fi
else
  echo "[health] redis-cli not installed — skipping Redis check"
fi

if [ "$fail" -ne 0 ]; then
  echo "[health] One or more services failed" >&2
  exit 1
fi

echo "[health] All services healthy"