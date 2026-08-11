"""
GitHub Actions'tan 'workflow_dispatch' girdisiyle calistirilir -- bilgisayarda
Python calistiramayan/engellenen durumlar icin setup_tiktok_oauth.py'nin
yerel sunucu GEREKTIRMEYEN alternatifi. Tarayicidan alinan yetkilendirme
kodunu (code) TikTok'a gonderip refresh_token'i log ciktisina yazdirir.
"""
import os

import requests

CLIENT_KEY = os.environ["TIKTOK_CLIENT_KEY"]
CLIENT_SECRET = os.environ["TIKTOK_CLIENT_SECRET"]
CODE = os.environ["TIKTOK_AUTH_CODE"]
CODE_VERIFIER = os.environ["TIKTOK_CODE_VERIFIER"]
REDIRECT_URI = "https://ufukkcan.github.io/tiktok-legal-pages/callback.html"


def main() -> None:
    resp = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "code": CODE,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code_verifier": CODE_VERIFIER,
        },
        timeout=20,
    )
    print("HTTP durum kodu:", resp.status_code)
    data = resp.json()
    print("Tam yanit:", data)

    if "refresh_token" in data:
        print("\n=== BU DEGERI GITHUB SECRETS'A TIKTOK_REFRESH_TOKEN OLARAK EKLE ===")
        print(data["refresh_token"])
    else:
        print("\nrefresh_token gelmedi -- yukaridaki 'Tam yanit' kismindaki hatayi kontrol et.")


if __name__ == "__main__":
    main()
