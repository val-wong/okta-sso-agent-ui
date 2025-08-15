#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker inspect $(docker ps --filter name=api -q) --format '{{json .State.Health.Log}}' | jq '.[-5:]'
