#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

FILE="backend/main.py"
if [[ ! -f "$FILE" ]]; then
  echo "ERROR: $FILE not found. Are you in the right repo root?" >&2
  exit 1
fi

if ! grep -q '@app.get("/")' "$FILE"; then
  cat >> "$FILE" <<'PY'
@app.get("/")
async def root():
    return {"message": "Okta SSO Agent up"}
PY
  echo "Added root route to $FILE"
else
  echo "Root route already present in $FILE"
fi

if [[ -f compose.override.yaml ]]; then
  echo "compose.override.yaml present; Uvicorn --reload should hot-reload automatically."
else
  echo "Rebuilding container to pick up code changes..."
  docker compose build --no-cache
  docker compose up -d
fi

curl -s http://localhost:8000/ | jq . || true
