Okta SSO Agent — UI & API

A full-stack developer tool for scanning Okta apps, inspecting SAML/SCIM configuration, and generating Terraform configuration automatically.
Built with FastAPI (backend) and React + Vite (frontend), with optional Docker Compose for local development.

📦 Requirements

Docker Desktop (recommended for quick start)

OR:

Python 3.10+

Node.js 18+

curl and jq (for quick API checks)

Okta Developer tenant + API token with app read access

⚙️ Environment Variables
Backend (backend/.env)
OKTA_ORG_URL=https://<your-okta-org>.okta.com
OKTA_API_TOKEN=REDACTED

Frontend (okta-sso-agent-ui/.env)
VITE_API_BASE=http://localhost:8000

🚀 Quick Start with Docker Compose

From the project root:

cp backend/.env.example backend/.env
cp okta-sso-agent-ui/.env.example okta-sso-agent-ui/.env

docker compose up -d --build


Health check:

curl -s http://localhost:8000/health


UI: http://localhost:5173

🖥 Manual Development
Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Frontend
cd okta-sso-agent-ui
npm install
cp .env.example .env
npm run dev

📂 Repository Structure
okta-sso-agent/
  backend/
    main.py
    requirements.txt
    .env.example
    Dockerfile
  okta-sso-agent-ui/
    src/
    vite.config.ts
    .env.example
    Dockerfile
  docker-compose.yml

🔌 API Endpoints

GET /health → { "ok": true }

GET /apps → List Okta apps

GET /apps/{app_id} → App details JSON

GET /apps/{app_id}/saml → SAML config (ACS URL, Entity, etc.)

POST /generate/terraform → Generate Terraform config

🖱 UI Features

Search/filter Okta apps

View SAML endpoints at a glance

Generate minimal Terraform snippets

Copy/paste directly into your terraform directory

🛠 Typical Workflow

Search for an Okta app in the UI

Inspect its SAML configuration

Generate Terraform snippet from the UI

Add to your Terraform repo and run:

terraform init
terraform plan
terraform apply

🔒 Security Notes

Never commit .env files or API tokens to GitHub

Use read-only Okta API tokens when possible

Limit CORS origins in main.py to trusted domains
