#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Ping health endpoint:"
if ! curl -fsS http://localhost:8000/health | jq .; then
  curl -fsS http://127.0.0.1:8000/health | jq . || true
fi

echo
echo "Recent healthcheck attempts:"
docker inspect $(docker ps --filter name=api -q) --format '{{json .State.Health.Log}}' | jq '.[-5:]' || true

echo
docker ps --filter name=api
