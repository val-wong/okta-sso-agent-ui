import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

OKTA_DOMAIN = os.getenv("OKTA_DOMAIN", "").rstrip("/")
API_TOKEN = os.getenv("OKTA_API_TOKEN")

if not OKTA_DOMAIN or not API_TOKEN:
    print("❌ Missing OKTA_DOMAIN or OKTA_API_TOKEN in .env")
    exit(1)

url = f"{OKTA_DOMAIN}/api/v1/apps"
headers = {
    "Authorization": f"SSWS {API_TOKEN}",
    "Accept": "application/json"
}
params = {
    "limit": 200
}

def scan_apps():
    print("🔍 Scanning Okta apps...\n")
    page = 1

    while True:
        print(f"📄 Fetching page {page}...\n")
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"❌ Error fetching apps: {response.status_code} - {response.text}")
            break

        apps = response.json()
        if not apps:
            print("✅ No more apps found.")
            break

        for app in apps:
            name = app.get("label", "Unnamed App")
            app_id = app.get("id", "unknown")
            sign_on_mode = app.get("signOnMode", "unknown")
            features = app.get("features", [])

            print(f"🔹 {name}")
            print(f"    - ID: {app_id}")
            print(f"    - Sign-On Mode: {sign_on_mode}")
            print(f"    - Features: {features}\n")

        # Okta uses link headers for pagination — we stop if no next link
        if "link" in response.headers:
            link_header = response.headers["link"]
            if 'rel="next"' not in link_header:
                break
        else:
            break

        page += 1

if __name__ == "__main__":
    scan_apps()
