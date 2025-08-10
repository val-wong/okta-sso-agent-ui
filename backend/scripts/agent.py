import requests
import os
from dotenv import load_dotenv

load_dotenv()

OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
OKTA_API_TOKEN = os.getenv("OKTA_API_TOKEN")


def run_agent():
    """
    Core logic to scan Okta apps and return structured data.
    """
    if not OKTA_DOMAIN or not OKTA_API_TOKEN:
        raise ValueError("Missing OKTA_DOMAIN or OKTA_API_TOKEN in environment variables")

    url = f"{OKTA_DOMAIN}/api/v1/apps"
    headers = {
        "Authorization": f"SSWS {OKTA_API_TOKEN}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching apps from Okta: {e}")

    apps = response.json()

    results = []
    for app in apps:
        results.append({
            "id": app.get("id"),
            "name": app.get("name"),
            "label": app.get("label"),
            "status": app.get("status")
        })

    return results


if __name__ == "__main__":
    try:
        apps = run_agent()
        print(f"Found {len(apps)} apps in Okta:")
        for app in apps:
            print(f"- {app['label']} ({app['status']})")
    except Exception as e:
        print(f"Error: {e}")
