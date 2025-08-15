#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

cat > compose.override.yaml <<'YAML'
services:
  api:
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app
    volumes:
      - ./backend:/app
    environment:
      - PYTHONUNBUFFERED=1
      - VERSION=v0.1.0
      - PYTHONPATH=/app
YAML

echo "Wrote compose.override.yaml (dev hot-reload)."
echo "Start/reload with: docker compose up -d; watch: docker compose logs -f"
