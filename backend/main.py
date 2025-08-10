# backend/main.py
from pathlib import Path
import os, re, logging
from typing import Optional, List, Dict, Any, Literal

import httpx
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# ── env ────────────────────────────────────────────────────────────────────────
ENV_PATH = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=ENV_PATH)

OKTA_ORG_URL = os.getenv("OKTA_ORG_URL", "").rstrip("/")
OKTA_API_TOKEN = os.getenv("OKTA_API_TOKEN", "")

logger = logging.getLogger("uvicorn.error")

# ── app & CORS ────────────────────────────────────────────────────────────────
app = FastAPI(title="Okta SSO Agent API")
origins = [f"http://localhost:{p}" for p in range(5173, 5180)]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── models ────────────────────────────────────────────────────────────────────
class SaveFileInput(BaseModel):
    filename: str
    content: str

TemplateType = Literal["saml_only", "zoom_saml_only"]

class GenerateTfInput(BaseModel):
    template: TemplateType = Field(default="saml_only")
    app_label: str
    sso_acs_url: Optional[str] = None
    sso_entity_id: Optional[str] = None
    idp_x509_cert: Optional[str] = None
    zoom_account_id: Optional[str] = None  # optional relay state

# ── helpers ───────────────────────────────────────────────────────────────────
def _assert_okta_config():
    if not OKTA_ORG_URL or not OKTA_API_TOKEN:
        raise HTTPException(500, detail="OKTA_ORG_URL or OKTA_API_TOKEN not set")

def _okta_headers() -> Dict[str, str]:
    return {
        "Authorization": f"SSWS {OKTA_API_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def _parse_link_after(link_header: Optional[str]) -> Optional[str]:
    if not link_header:
        return None
    m = re.search(r'<[^>]*\bafter=([^&>]+)[^>]*>; *rel="next"', link_header)
    return m.group(1) if m else None

async def _okta_get(client: httpx.AsyncClient, path: str, params: Dict[str, Any] | None = None):
    url = f"{OKTA_ORG_URL}{path}"
    try:
        r = await client.get(url, headers=_okta_headers(), params=params, timeout=30.0)
    except httpx.HTTPError as e:
        logger.error(f"httpx error GET {url}: {e}")
        raise HTTPException(502, detail=f"httpx error: {e}")
    if r.status_code >= 400:
        logger.error(f"Okta error {r.status_code} {url} {params}: {r.text}")
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r

def _tf_header() -> str:
    return (
        'terraform {\n'
        '  required_providers {\n'
        '    okta = {\n'
        '      source  = "okta/okta"\n'
        '      version = ">= 4.7.0"\n'
        '    }\n'
        '  }\n'
        '}\n'
        'provider "okta" {}\n'
    )

def _sanitize(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", s).lower()

def _tf_saml(label: str, acs: str, entity: str, pem_cert: str, *,
             nameid_email: bool, relay_state: Optional[str], res_name: str) -> str:
    # Correct brace count (double) and formats
    if nameid_email:
        nameid_tpl = "{{user.email}}"
        nameid_fmt = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    else:
        nameid_tpl = "{{user.userName}}"
        nameid_fmt = "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"

    pem_block = f"""<<-PEM
{pem_cert.strip()}
PEM"""
    rs = relay_state or ""

    # v5.x: attribute_statements must be blocks, not a map
    return f'''
resource "okta_app_saml" "{res_name}" {{
  label                    = "{label}"
  sso_url                  = "{acs}"
  recipient                = "{acs}"
  destination              = "{acs}"
  audience                 = "{entity}"
  default_relay_state      = "{rs}"

  response_signed          = true
  assertion_signed         = true
  signature_algorithm      = "RSA_SHA256"
  digest_algorithm         = "SHA256"
  honor_force_authn        = false

  subject_name_id_template = "{nameid_tpl}"
  subject_name_id_format   = "{nameid_fmt}"

  single_logout_issuer     = "{entity}"
  single_logout_url        = ""
  single_logout_certificate = {pem_block}

  attribute_statements {{
    name   = "Email"
    values = ["user.email"]
  }}

  attribute_statements {{
    name   = "FirstName"
    values = ["user.firstName"]
  }}

  attribute_statements {{
    name   = "LastName"
    values = ["user.lastName"]
  }}
}}
'''.strip()

# ── routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/config")
async def get_config():
    masked = (OKTA_ORG_URL[:32] + "...") if OKTA_ORG_URL else ""
    raw_env = {
        "OKTA_ORG_URL": OKTA_ORG_URL,
        "OKTA_API_TOKEN_present": bool(OKTA_API_TOKEN),
        "env_path": str(ENV_PATH),
    }
    return {
        "org_url": masked,
        "used_org_url": masked,
        "has_token": bool(OKTA_API_TOKEN),
        "raw_env": raw_env,
        "cors": [f"http://localhost:{p}" for p in range(5173, 5180)],
    }

@app.get("/apps/scan")
async def scan_apps(limit: int = 200):
    _assert_okta_config()
    results: List[Dict[str, Any]] = []
    after: Optional[str] = None
    params: Dict[str, Any] = {"limit": limit}
    async with httpx.AsyncClient() as client:
        while True:
            if after:
                params["after"] = after
            r = await _okta_get(client, "/api/v1/apps", params=params)
            items = r.json()
            # summarize
            for x in items:
                features = x.get("features") or []
                has_prov = any(f in features for f in [
                    "PUSH_NEW_USERS","PUSH_PROFILE_UPDATES","PUSH_PASSWORD_UPDATES",
                    "REACTIVATE_DEPROVISIONED_USERS","IMPORT_NEW_USERS"
                ])
                name = x.get("name") or ""
                inferred_scim = has_prov or ("scim" in name.lower())
                results.append({
                    "id": x.get("id"),
                    "name": name,
                    "label": x.get("label"),
                    "status": x.get("status"),
                    "signOnMode": x.get("signOnMode"),
                    "features": features,
                    "inferred_provisioning": has_prov,
                    "inferred_scim": inferred_scim,
                })
            after = _parse_link_after(r.headers.get("link"))
            if not after or not items:
                break
    return {"count": len(results), "apps": results}

@app.get("/apps/{id}")
async def get_app(id: str):
    _assert_okta_config()
    async with httpx.AsyncClient() as client:
        r = await _okta_get(client, f"/api/v1/apps/{id}")
        return r.json()

@app.get("/apps/{id}/sso/saml/metadata")
async def get_app_metadata(id: str):
    _assert_okta_config()
    url = f"{OKTA_ORG_URL}/api/v1/apps/{id}/sso/saml/metadata"
    async with httpx.AsyncClient() as client:
        r = await client.get(
            url,
            headers={"Authorization": f"SSWS {OKTA_API_TOKEN}", "Accept": "application/xml"},
            timeout=30.0,
        )
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.text

@app.get("/apps/{id}/saml/cert")
async def get_saml_cert(id: str):
    _assert_okta_config()
    url = f"{OKTA_ORG_URL}/api/v1/apps/{id}/sso/saml/metadata"
    async with httpx.AsyncClient() as client:
        r = await client.get(
            url,
            headers={"Authorization": f"SSWS {OKTA_API_TOKEN}", "Accept": "application/xml"},
            timeout=30.0,
        )
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    xml = r.text
    m = re.search(r"<(?:ds:)?X509Certificate>([^<]+)</(?:ds:)?X509Certificate>", xml, re.S)
    if not m:
        return {"pem": None, "note": "No X509Certificate found in metadata"}
    b64 = m.group(1).strip().replace("\n", "")
    wrapped = "\n".join(b64[i:i+64] for i in range(0, len(b64), 64))
    pem = f"-----BEGIN CERTIFICATE-----\n{wrapped}\n-----END CERTIFICATE-----\n"
    return {"pem": pem}

@app.post("/tf/generate")
async def tf_generate(payload: GenerateTfInput):
    # Only SAML-only flows here
    if payload.template in ("saml_only", "zoom_saml_only"):
        if not payload.app_label:
            raise HTTPException(400, detail="Missing app_label")
        if not payload.idp_x509_cert:
            raise HTTPException(400, detail="Missing idp_x509_cert")

        # Zoom specifics enforced here
        if payload.template == "zoom_saml_only":
            if not payload.sso_acs_url:
                payload.sso_acs_url = "https://zoom.us/saml/SSO"
            payload.sso_entity_id = "https://zoom.us"
            nameid_email = True
            relay_state = payload.zoom_account_id
        else:
            nameid_email = False
            relay_state = None

        for f in ("sso_acs_url", "sso_entity_id"):
            if not getattr(payload, f):
                raise HTTPException(400, detail=f"Missing {f}")

        # Guard against audience accidentally being an Okta app ID
        if re.match(r"^0o[a-zA-Z0-9]+$", payload.sso_entity_id):
            if payload.template == "zoom_saml_only":
                payload.sso_entity_id = "https://zoom.us"
            else:
                raise HTTPException(400, detail="sso_entity_id looks like an Okta app ID; use the SP Entity ID URL")

        parts = [_tf_header()]
        res_name = f"app_{_sanitize(payload.app_label)}"
        parts.append(
            _tf_saml(
                label=payload.app_label,
                acs=payload.sso_acs_url,
                entity=payload.sso_entity_id,
                pem_cert=payload.idp_x509_cert,
                nameid_email=nameid_email,
                relay_state=relay_state,
                res_name=res_name,
            )
        )
        filename = f"{_sanitize(payload.app_label)}.tf"
        content = "\n\n".join(parts).strip()
        return {"filename": filename, "content": content}

    raise HTTPException(400, detail=f"Unsupported template: {payload.template}")

@app.post("/files/tf")
async def save_tf_file(input: SaveFileInput = Body(...)):
    if not input.filename.endswith(".tf"):
        raise HTTPException(400, detail="filename must end with .tf")
    target = Path.cwd() / input.filename
    target.write_text(input.content, encoding="utf-8")
    return {"saved": True, "path": str(target)}

# Back-compat for older UI
@app.post("/tf/zoom")
async def tf_zoom_bridge(payload: GenerateTfInput):
    payload.template = "zoom_saml_only"
    return await tf_generate(payload)
