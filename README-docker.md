# Okta SSO Agent — Docker

## Local
cp .env.example .env
# Fill in OKTA_ORG_URL and OKTA_API_TOKEN
make run
open http://localhost:8000

## Logs
make logs

## Stop
make stop

## Build a tagged image
make build TAG=0.1.0 REGISTRY=ghcr.io/<user>/

## Push
make push TAG=0.1.0 REGISTRY=ghcr.io/<user>/