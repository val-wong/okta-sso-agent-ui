#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

: "${VERSION:?Set VERSION (e.g., export VERSION=v0.1.2)}"

git tag "$VERSION"
git push origin "$VERSION"
echo "Pushed git tag $VERSION (triggers the CI workflow)"
