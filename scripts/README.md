# Project-level scripts

Bash utility scripts for common development tasks.

| Script | Purpose |
| --- | --- |
| `setup.sh` | Bootstrap a fresh dev environment: venv, deps, Postgres + Redis, migrations, seed data, tests |
| `db_healthcheck.sh` | Verify Postgres and Redis are reachable before starting the app |
| `run_local.sh` | Start the full CRM stack locally (backend, channel-stub, Celery worker, frontend) |
| `deploy.sh` | Build Docker images for all services and push to the target registry |

## Usage

```bash
# First-time setup
bash scripts/setup.sh

# Verify dependencies before running
bash scripts/db_healthcheck.sh

# Run the whole stack locally
bash scripts/run_local.sh

# Deploy
IMAGE_TAG=v1.0.0 bash scripts/deploy.sh
```

## Requirements

- Bash 4+
- Docker + docker-compose
- Python 3.10+
- Node.js 18+ (for the frontend)