terraform {
  required_providers {
    okta = {
      source  = "okta/okta"
      version = ">= 4.7.0"
    }
  }
}
provider "okta" {}


resource "okta_app_saml" "app_zoom_saml" {
  label                    = "Zoom SAML"
  sso_url                  = "https://zoom.us/"
  recipient                = "https://zoom.us/"
  destination              = "https://zoom.us/"
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
MIIDtDCCApygAwIBAgIGAZhpjENRMA0GCSqGSIb3DQEBCwUAMIGaMQswCQYDVQQGEwJVUzETMBEG
A1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNjbzENMAsGA1UECgwET2t0YTEU
MBIGA1UECwwLU1NPUHJvdmlkZXIxGzAZBgNVBAMMEmludGVncmF0b3ItMTA2NzgwMjEcMBoGCSqG
SIb3DQEJARYNaW5mb0Bva3RhLmNvbTAeFw0yNTA4MDIwNjQ5NTZaFw0zNTA4MDIwNjUwNTZaMIGa
MQswCQYDVQQGEwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNj
bzENMAsGA1UECgwET2t0YTEUMBIGA1UECwwLU1NPUHJvdmlkZXIxGzAZBgNVBAMMEmludGVncmF0
b3ItMTA2NzgwMjEcMBoGCSqGSIb3DQEJARYNaW5mb0Bva3RhLmNvbTCCASIwDQYJKoZIhvcNAQEB
BQADggEPADCCAQoCggEBAL+iHMBdrkRY9EgXlfonsZI95te61jMM5QiCX8nBBplZOcohbekKRRrQ
J5VryLgj8wm5AXpun4IKYVvF7rwP8c6v2nHTar76ymQeUS3nMwKtpffkUlQ7M7R/oiKEwTnU+5cs
xowOaOysEtj65EeBtV6mtVFBzMyxW63dzapKr7AvD+5UMiqyYWPehPs9AuPVUDUuHhnQHNq+TnIO
Z1JgtBSv7e4uUawO6A+Y9Maw0asyYTlwyC16OhITejA0pihBxqDRvr+eMKdJH7DEGUpNIJU1XkBR
hvCGOjxAmYIVAfNLcuG5Pdhj4pe/qJ19GuL8W1N/skk5hgRnqYykCyQaBU0CAwEAATANBgkqhkiG
9w0BAQsFAAOCAQEAM4dKDWtN6IEVRMEYBe7Vj6rqnPBy8JW+9gtO/XjZauApQ4IwQnZ+wVLWSSRn
YF66sZXCnCEZ4ZQQijX+5E8iXNvI/kdyqKmm3j0sI7mF3e5pB+727Cgx1cPqt1EArLNrjhs09ZYZ
2YgAEH42zAPz8KG9hKxdd3EJqUh/tYQjXOwCtj6dnrPYjKbT8d5amqF3Odi5S+jUzh0i03x21z5U
A8LaasXLzBCSxtFG3QX0MABG/uzcCPJjdz9JrF1Lm9bn5185qPgYz+Te+3M+Hio/3Qtp5FvyZJqX
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