#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

: "${OWNER:?Set OWNER}"
: "${REPO:=okta-sso-agent-ui}"
: "${VERSION:?Set VERSION (e.g., v0.1.2)}"

# Run on a random free host port
CID=$(docker run -d -p 0:8000 ghcr.io/$OWNER/$REPO:$VERSION)
PORT=$(docker port "$CID" 8000/tcp | sed 's/.*:\([0-9][0-9]*\)$//')
echo "Container $CID listening on host port $PORT"
curl -s "http://localhost:$PORT/health" | jq . || true
