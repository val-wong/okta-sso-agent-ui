#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

: "${OWNER:?Set OWNER=your-github-username (e.g., export OWNER=val-wong)}"
: "${REPO:=okta-sso-agent-ui}"
: "${VERSION:?Set VERSION (e.g., export VERSION=v0.1.2)}"
: "${CR_PAT:?Export CR_PAT with a Classic PAT that has write:packages}"

echo "$CR_PAT" | docker login ghcr.io -u "$OWNER" --password-stdin
docker tag okta-sso-agent:local ghcr.io/$OWNER/$REPO:$VERSION

# Optional: also tag latest when pushing main builds
if [[ "${PUSH_LATEST:-0}" == "1" ]]; then
  docker tag okta-sso-agent:local ghcr.io/$OWNER/$REPO:latest
fi

docker push ghcr.io/$OWNER/$REPO:$VERSION
if [[ "${PUSH_LATEST:-0}" == "1" ]]; then
  docker push ghcr.io/$OWNER/$REPO:latest
fi

echo "Pushed ghcr.io/$OWNER/$REPO:$VERSION"
