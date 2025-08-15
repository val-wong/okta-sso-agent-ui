#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

: "${OWNER:?Set OWNER}"
: "${REPO:=okta-sso-agent-ui}"
: "${VERSION:?Set VERSION (e.g., v0.1.2)}"
PORT="${PORT:-9001}"

docker pull ghcr.io/$OWNER/$REPO:$VERSION
echo "Running on host port $PORT -> container 8000"
docker run --rm --name agent-$VERSION -p ${PORT}:8000 ghcr.io/$OWNER/$REPO:$VERSION
