"""
TANI ARACI -- video/init endpoint'ini FARKLI govde (body) varyasyonlariyla
dener, hangisinin 401 yerine 200 dondugunu görmek icin. Gercek dosya
gerektirmez (init asamasi sadece boyut bilgisi ister, gercek yukleme ayri).
"""
import os

import requests

CLIENT_KEY = os.environ["TIKTOK_CLIENT_KEY"]
CLIENT_SECRET = os.environ["TIKTOK_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["TIKTOK_REFRESH_TOKEN"]

FAKE_SIZE = 5_000_000  # sahte 5MB, gercek dosya gerekmiyor bu testte


def get_access_token() -> str:
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
    resp.raise_for_status()
    return resp.json()["access_token"]


def try_init(label: str, body: dict, access_token: str) -> None:
    resp = requests.post(
        "https://open.tiktokapis.com/v2/post/publish/video/init/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json=body,
        timeout=30,
    )
    print(f"\n=== Deneme: {label} ===")
    print("Govde:", body)
    print("HTTP durum kodu:", resp.status_code)
    print("Yanit:", resp.text[:500])


def main() -> None:
    token = get_access_token()
    print("Access token alindi, uzunluk:", len(token))

    source_info = {
        "source": "FILE_UPLOAD",
        "video_size": FAKE_SIZE,
        "chunk_size": FAKE_SIZE,
        "total_chunk_count": 1,
    }

    try_init(
        "A) post_info + privacy_level=SELF_ONLY",
        {
            "post_info": {
                "title": "test",
                "privacy_level": "SELF_ONLY",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
            },
            "source_info": source_info,
        },
        token,
    )

    try_init(
        "B) SADECE source_info (post_info yok)",
        {"source_info": source_info},
        token,
    )

    try_init(
        "C) post_info (privacy_level olmadan) + source_info",
        {
            "post_info": {"title": "test"},
            "source_info": source_info,
        },
        token,
    )


if __name__ == "__main__":
    main()
