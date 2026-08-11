"""
TikTok Content Posting API uzerinden video yukler.
Resmi dokumantasyon: https://developers.tiktok.com/doc/content-posting-api-get-started

ONEMLI: Yeni olusturulan TikTok uygulamalari once "denetlenmemis" (unaudited)
statusunde olur. Bu durumda TikTok, guvenlik geregi yuklenen videolari
SADECE SANA OZEL (private/SELF_ONLY) yapabilir -- herkese acik paylasim icin
TikTok'un uygulamani incelemesi (audit) gerekiyor. Bu kisitlama koddan degil
TikTok'un kendi politikasindan kaynaklanir.
"""
import os
import time

import requests

CLIENT_KEY = os.environ["TIKTOK_CLIENT_KEY"]
CLIENT_SECRET = os.environ["TIKTOK_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["TIKTOK_REFRESH_TOKEN"]
# Uygulama henuz TikTok tarafindan onaylanmadiysa "SELF_ONLY" kullan (guvenli
# varsayilan). Onaylandiktan sonra "PUBLIC_TO_EVERYONE" yapabilirsin.
PRIVACY_LEVEL = os.environ.get("TIKTOK_PRIVACY_LEVEL", "SELF_ONLY")

TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"


def _get_access_token() -> str:
    """Refresh token ile yeni bir access token alir (access token'lar ~24 saat
    gecerli, bu yuzden her calistirmada yeniden alinir)."""
    resp = requests.post(
        TOKEN_URL,
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
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"TikTok access token alinamadi: {data}")
    return data["access_token"]


def upload_video(video_path: str, title: str) -> str:
    """Videoyu yukler. title: TikTok'ta videonun altinda gorunecek aciklama
    (hashtag'ler dahil tek metin -- TikTok'ta YouTube'daki gibi ayri
    baslik/aciklama alani yok). Donus: publish_id."""
    access_token = _get_access_token()
    video_size = os.path.getsize(video_path)

    init_resp = requests.post(
        INIT_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={
            "post_info": {
                "title": title[:2200],
                "privacy_level": PRIVACY_LEVEL,
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": video_size,
                "total_chunk_count": 1,
            },
        },
        timeout=30,
    )
    init_resp.raise_for_status()
    init_data = init_resp.json()
    if init_data.get("error", {}).get("code") not in (None, "ok"):
        raise RuntimeError(f"TikTok init hatasi: {init_data}")

    publish_id = init_data["data"]["publish_id"]
    upload_url = init_data["data"]["upload_url"]

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    put_resp = requests.put(
        upload_url,
        headers={
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
        },
        data=video_bytes,
        timeout=180,
    )
    put_resp.raise_for_status()

    _wait_for_publish(access_token, publish_id)
    return publish_id


def _wait_for_publish(access_token: str, publish_id: str, timeout_seconds: int = 120) -> None:
    """Yukleme sonrasi TikTok'un videoyu isleyip yayinlamasini bekler."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        resp = requests.post(
            STATUS_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8",
            },
            json={"publish_id": publish_id},
            timeout=20,
        )
        resp.raise_for_status()
        status = resp.json().get("data", {}).get("status")
        print(f"   TikTok durumu: {status}")
        if status in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"):
            return
        if status == "FAILED":
            raise RuntimeError(f"TikTok yayin hatasi: {resp.json()}")
        time.sleep(5)
    print("   Uyari: TikTok durumu zaman asimina ugradi, ama yukleme muhtemelen basarili -- uygulamandan kontrol et.")


if __name__ == "__main__":
    import sys
    pid = upload_video(sys.argv[1], sys.argv[2])
    print("Yuklendi, publish_id:", pid)
