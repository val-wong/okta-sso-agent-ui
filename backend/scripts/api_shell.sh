#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

CID="$(docker ps --filter name=api -q)"
if [[ -z "$CID" ]]; then
  echo "No running API container found. Start with: docker compose up -d" >&2
  exit 1
fi
docker exec -it "$CID" sh
