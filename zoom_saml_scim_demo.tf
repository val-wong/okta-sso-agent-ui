terraform {
  required_providers {
    okta = {
      source  = "okta/okta"
      version = ">= 4.7.0"
    }
  }
}
provider "okta" {}


resource "okta_app_saml" "app_zoom_saml_scim_demo" {
  label                    = "Zoom SAML SCIM Demo"
  sso_url                  = "https://zoom.us/saml/SSO"
  recipient                = "https://zoom.us/saml/SSO"
  destination              = "https://zoom.us/saml/SSO"
  audience                 = "https://zoom.us"
  default_relay_state      = ""

  response_signed          = true
  assertion_signed         = true
  signature_algorithm      = "RSA_SHA256"
  digest_algorithm         = "SHA256"
  honor_force_authn        = false

  subject_name_id_template = "{{user.email}}"
  subject_name_id_format   = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"

  single_logout_issuer     = "https://zoom.us"
  single_logout_url        = ""
  single_logout_certificate = <<-PEM
-----BEGIN CERTIFICATE-----
MIIDtDCCApygAwIBAgIGAZhpjENRMA0GCSqGSIb3DQEBCwUAMIGaMQswCQYDVQQG
EwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNj
bzENMAsGA1UECgwET2t0YTEUMBIGA1UECwwLU1NPUHJvdmlkZXIxGzAZBgNVBAMM
EmludGVncmF0b3ItMTA2NzgwMjEcMBoGCSqGSIb3DQEJARYNaW5mb0Bva3RhLmNv
bTAeFw0yNTA4MDIwNjQ5NTZaFw0zNTA4MDIwNjUwNTZaMIGaMQswCQYDVQQGEwJV
UzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNjbzEN
MAsGA1UECgwET2t0YTEUMBIGA1UECwwLU1NPUHJvdmlkZXIxGzAZBgNVBAMMEmlu
dGVncmF0b3ItMTA2NzgwMjEcMBoGCSqGSIb3DQEJARYNaW5mb0Bva3RhLmNvbTCC
ASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAL+iHMBdrkRY9EgXlfonsZI9
5te61jMM5QiCX8nBBplZOcohbekKRRrQJ5VryLgj8wm5AXpun4IKYVvF7rwP8c6v
2nHTar76ymQeUS3nMwKtpffkUlQ7M7R/oiKEwTnU+5csxowOaOysEtj65EeBtV6m
tVFBzMyxW63dzapKr7AvD+5UMiqyYWPehPs9AuPVUDUuHhnQHNq+TnIOZ1JgtBSv
7e4uUawO6A+Y9Maw0asyYTlwyC16OhITejA0pihBxqDRvr+eMKdJH7DEGUpNIJU1
XkBRhvCGOjxAmYIVAfNLcuG5Pdhj4pe/qJ19GuL8W1N/skk5hgRnqYykCyQaBU0C
AwEAATANBgkqhkiG9w0BAQsFAAOCAQEAM4dKDWtN6IEVRMEYBe7Vj6rqnPBy8JW+
9gtO/XjZauApQ4IwQnZ+wVLWSSRnYF66sZXCnCEZ4ZQQijX+5E8iXNvI/kdyqKmm
3j0sI7mF3e5pB+727Cgx1cPqt1EArLNrjhs09ZYZ2YgAEH42zAPz8KG9hKxdd3EJ
qUh/tYQjXOwCtj6dnrPYjKbT8d5amqF3Odi5S+jUzh0i03x21z5UA8LaasXLzBCS
xtFG3QX0MABG/uzcCPJjdz9JrF1Lm9bn5185qPgYz+Te+3M+Hio/3Qtp5FvyZJqX
iRHphGldQihVGL2iBip+iDwJedNQmq/0gEuzXIVZPSEd+sKUYTnDMw==
-----END CERTIFICATE-----
PEM

  attribute_statements {
    name   = "Email"
    values = ["user.email"]
  }

  attribute_statements {
    name   = "FirstName"
    values = ["user.firstName"]
  }

  attribute_statements {
    name   = "LastName"
    values = ["user.lastName"]
  }
}