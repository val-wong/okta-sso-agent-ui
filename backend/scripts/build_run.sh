#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose build --no-cache
docker compose up -d
docker compose ps
