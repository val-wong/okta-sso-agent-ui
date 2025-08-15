#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  if [[ -f .env.example ]]; then
    cp .env.example .env
    echo "Copied .env.example to .env"
  else
    cat > .env <<'EOF'
OKTA_ORG_URL=
OKTA_API_TOKEN=
UI_ORIGIN=
EOF
    echo "Created .env with placeholders"
  fi
else
  echo ".env already exists"
fi

echo "Edit .env and set OKTA_ORG_URL and a short-lived OKTA_API_TOKEN before calling Okta endpoints."
