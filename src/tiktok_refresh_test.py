"""
TANI ARACI -- sadece refresh_token ile access_token alma adimini izole test
eder, gercek yukleme yapmaz. Sorunu tam olarak nerede oldugunu gormek icin.
"""
import os

import requests

CLIENT_KEY = os.environ["TIKTOK_CLIENT_KEY"]
CLIENT_SECRET = os.environ["TIKTOK_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["TIKTOK_REFRESH_TOKEN"]

print("CLIENT_KEY uzunlugu:", len(CLIENT_KEY), "ilk/son 3 karakter:", CLIENT_KEY[:3], CLIENT_KEY[-3:])
print("CLIENT_SECRET uzunlugu:", len(CLIENT_SECRET))
print("REFRESH_TOKEN uzunlugu:", len(REFRESH_TOKEN), "ilk/son 5 karakter:", REFRESH_TOKEN[:5], REFRESH_TOKEN[-5:])

resp = requests.post(
    "https://open.tiktokapis.com/v2/oauth/token/",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    },
    timeout=20,
)
print("\nHTTP durum kodu:", resp.status_code)
print("Tam yanit:", resp.json())
