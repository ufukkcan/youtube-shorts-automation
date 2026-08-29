"""
TEK SEFERLIK YARDIMCI -- tarayicidan alinan yetkilendirme kodunu (code)
Google'a gonderip YouTube refresh_token'i log ciktisina yazdirir.
Bilgisayarda Python calistirmaya gerek kalmadan, GitHub Actions uzerinden.
"""
import os

import requests

CLIENT_ID = os.environ["YT_CLIENT_ID"]
CLIENT_SECRET = os.environ["YT_CLIENT_SECRET"]
CODE = os.environ["YT_AUTH_CODE"]
REDIRECT_URI = "https://ufukkcan.github.io/tiktok-legal-pages/callback.html"


def main() -> None:
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": CODE,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        },
        timeout=20,
    )
    print("HTTP durum kodu:", resp.status_code)
    data = resp.json()
    print("Tam yanit:", data)

    if "refresh_token" in data:
        print("\n=== BU DEGERI GITHUB SECRETS'A YT_REFRESH_TOKEN OLARAK EKLE ===")
        print(data["refresh_token"])
    else:
        print("\nrefresh_token gelmedi -- yukaridaki yaniti kontrol et.")


if __name__ == "__main__":
    main()
