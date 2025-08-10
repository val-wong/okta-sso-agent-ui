import argparse
from pathlib import Path
from string import Template

ZOOM_TF_TEMPLATE = Template("""terraform {
  required_providers {
    okta = {
      source  = "okta/okta"
      version = ">= 4.7.0"
    }
  }
}

provider "okta" {}

resource "okta_app_saml" "zoom" {
  label                    = "Zoom SAML"
  sso_url                  = "$ACS_URL"
  recipient                = "$ACS_URL"
  destination              = "$ACS_URL"
  audience                 = "https://zoom.us"
  response_signed          = true
  assertion_signed         = true
  signature_algorithm      = "RSA_SHA256"
  digest_algorithm         = "SHA256"
  honor_force_authn        = false
  subject_name_id_template = "$SUBJECT_TEMPLATE"
  subject_name_id_format   = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
  status                   = "ACTIVE"

  attribute_statements {
    type   = "EXPRESSION"
    name   = "Email"
    values = ["user.email"]
  }

  attribute_statements {
    type   = "EXPRESSION"
    name   = "FirstName"
    values = ["user.firstName"]
  }

  attribute_statements {
    type   = "EXPRESSION"
    name   = "LastName"
    values = ["user.lastName"]
  }
}

resource "okta_app_group_assignment" "zoom_assignment" {
  app_id   = okta_app_saml.zoom.id
  group_id = "$GROUP_ID"
}
""")

def generate_tf(acs_url: str, group_id: str):
    out = ZOOM_TF_TEMPLATE.substitute(
        ACS_URL=acs_url,
        GROUP_ID=group_id,
        SUBJECT_TEMPLATE='$${user.email}',
    )
    output_path = Path(__file__).resolve().parents[1] / "terraform" / "generated" / "zoom_saml.tf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(out, encoding="utf-8")
    print(str(output_path.resolve()))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://zoom.us/saml/SSO")
    parser.add_argument("--group", required=True)
    args = parser.parse_args()
    generate_tf(args.url, args.group)
