"""
Konuyla eslesen ucretsiz stok videolari Pexels API uzerinden indirir.
Ucretsiz Pexels API anahtari: https://www.pexels.com/api/ adresinden aliniyor.
"""
import os
from pathlib import Path

import requests

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
SEARCH_URL = "https://api.pexels.com/videos/search"


def fetch_clips(keywords: list[str], out_dir: str, min_total_seconds: float) -> list[str]:
    """Her anahtar kelime icin dikey (9:16'ya yakin) bir klip indirir.
    Toplam sure min_total_seconds'i gecene kadar ek klip cekmeye devam eder."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    downloaded_paths = []
    total_duration = 0.0
    keyword_index = 0

    while total_duration < min_total_seconds and keyword_index < len(keywords) * 3:
        keyword = keywords[keyword_index % len(keywords)]
        clip = _search_one_clip(keyword, exclude_paths=downloaded_paths)
        if clip is not None:
            dest = os.path.join(out_dir, f"clip_{len(downloaded_paths):02d}.mp4")
            _download(clip["url"], dest)
            downloaded_paths.append(dest)
            total_duration += clip["duration"]
        keyword_index += 1

    if not downloaded_paths:
        raise RuntimeError("Hicbir stok video bulunamadi, anahtar kelimeleri kontrol et.")
    return downloaded_paths


def _search_one_clip(keyword: str, exclude_paths: list[str]) -> dict | None:
    resp = requests.get(
        SEARCH_URL,
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": keyword, "orientation": "portrait", "per_page": 5, "size": "medium"},
        timeout=20,
    )
    resp.raise_for_status()
    results = resp.json().get("videos", [])
    for video in results:
        # en yuksek kaliteli dikey (portrait) dosyayi sec
        files = sorted(
            (f for f in video["video_files"] if f.get("width", 0) < f.get("height", 1)),
            key=lambda f: f.get("width", 0), reverse=True,
        )
        if files:
            return {"url": files[0]["link"], "duration": video.get("duration", 6)}
    return None


def _download(url: str, dest: str) -> None:
    with requests.get(url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 16):
                f.write(chunk)


if __name__ == "__main__":
    import sys
    paths = fetch_clips(sys.argv[1].split(","), "clips", float(sys.argv[2]))
    print(paths)
