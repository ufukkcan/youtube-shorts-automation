"""
Google OAuth refresh token kullanarak (interaktif giris GEREKMEDEN)
YouTube'a video yukler. Refresh token'i BIR KEZ, kendi bilgisayarinda
(README'deki setup_oauth.py betigiyle) uretip GitHub Secrets'a eklersin.
Sonrasinda bu script hep o refresh token ile calisir.
"""
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _get_credentials() -> Credentials:
    return Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )


def upload_short(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    privacy_status: str = "public",
    publish_at: str | None = None,
) -> str:
    """Videoyu yukler, video id'sini dondurur.
    publish_at verilirse (ISO8601 UTC, ornek '2026-08-05T17:00:00Z'), video
    'private' olarak yuklenir ve YouTube o saat geldiginde otomatik olarak
    'public' yapar -- gercek zamanlanmis yayin budur."""
    youtube = build("youtube", "v3", credentials=_get_credentials())

    status = {
        "privacyStatus": "private" if publish_at else privacy_status,
        "selfDeclaredMadeForKids": False,
    }
    if publish_at:
        status["publishAt"] = publish_at

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:30],
            "categoryId": "24",  # Entertainment
        },
        "status": status,
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Yukleniyor: %{int(status.progress() * 100)}")

    video_id = response["id"]
    print(f"Yuklendi: https://youtube.com/shorts/{video_id}")
    return video_id


if __name__ == "__main__":
    import sys
    upload_short(
        video_path=sys.argv[1],
        title=sys.argv[2],
        description=sys.argv[3],
        tags=sys.argv[4].split(","),
    )
