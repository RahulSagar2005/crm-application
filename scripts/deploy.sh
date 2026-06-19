#!/usr/bin/env bash
# deploy.sh — Build CRM services and push to registry (Railway / Docker Hub)
# Usage: IMAGE_TAG=v1.0.0 bash scripts/deploy.sh
# Requires: Docker, Railway CLI (optional), and access to your target registry.

set -euo pipefail

: "${IMAGE_TAG:=$(git rev-parse --short HEAD 2>/dev/null || echo latest)}"

echo "[deploy] Building backend image (tag: $IMAGE_TAG)..."
docker build -t crm-backend:"$IMAGE_TAG" -f backend/Dockerfile backend/

echo "[deploy] Building channel-stub image (tag: $IMAGE_TAG)..."
if [ -f "channel-stub/Dockerfile" ]; then
  docker build -t crm-channel-stub:"$IMAGE_TAG" -f channel-stub/Dockerfile channel-stub/
fi

echo "[deploy] Building frontend image (tag: $IMAGE_TAG)..."
if [ -f "frontend/Dockerfile" ]; then
  docker build -t crm-frontend:"$IMAGE_TAG" -f frontend/Dockerfile frontend/
fi

echo "[deploy] Images built. Push to registry via:"
echo "        docker push <registry>/crm-backend:$IMAGE_TAG"
echo "        docker push <registry>/crm-channel-stub:$IMAGE_TAG"
echo "        docker push <registry>/crm-frontend:$IMAGE_TAG"

if command -v railway >/dev/null 2>&1; then
  echo "[deploy] Railway CLI detected — triggering Railway deploy..."
  railway up --service backend || echo "[deploy] Railway backend deploy skipped/failed"
else
  echo "[deploy] Railway CLI not installed — manual push required"
fi