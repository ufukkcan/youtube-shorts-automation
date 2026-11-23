"""
Konuyla eslesen ucretsiz stok videolari Pexels API uzerinden indirir.
Ucretsiz Pexels API anahtari: https://www.pexels.com/api/ adresinden aliniyor.
"""
import os
from pathlib import Path

import requests

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
SEARCH_URL = "https://api.pexels.com/videos/search"


MIN_CLIPS = 4          # hizli kurgu (her ~2.5 sn'de goruntu degisimi) icin en az bu kadar farkli klip
MAX_FILE_WIDTH = 1080  # cikti 1080 genislikte; daha buyuk (4K) dosya indirmek sadece sureyi uzatir


def fetch_clips(keywords: list[str], out_dir: str, min_total_seconds: float) -> list[str]:
    """Anahtar kelimeleri sirayla dolasarak FARKLI dikey klipler indirir.
    Hem toplam sure min_total_seconds'i gecene hem de en az MIN_CLIPS klip
    olana kadar devam eder. Ayni Pexels videosu iki kez indirilmez (onceden
    ayni anahtar kelime ikinci turda ayni videoyu donduruyordu)."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    downloaded_paths = []
    used_ids: set = set()
    total_duration = 0.0
    keyword_index = 0

    while keyword_index < len(keywords) * 3:
        if total_duration >= min_total_seconds and len(downloaded_paths) >= MIN_CLIPS:
            break
        keyword = keywords[keyword_index % len(keywords)]
        clip = _search_one_clip(keyword, exclude_ids=used_ids)
        if clip is not None:
            dest = os.path.join(out_dir, f"clip_{len(downloaded_paths):02d}.mp4")
            _download(clip["url"], dest)
            downloaded_paths.append(dest)
            used_ids.add(clip["id"])
            total_duration += clip["duration"]
        keyword_index += 1

    if not downloaded_paths:
        raise RuntimeError("Hicbir stok video bulunamadi, anahtar kelimeleri kontrol et.")
    return downloaded_paths


def _search_one_clip(keyword: str, exclude_ids: set) -> dict | None:
    resp = requests.get(
        SEARCH_URL,
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": keyword, "orientation": "portrait", "per_page": 5, "size": "medium"},
        timeout=20,
    )
    resp.raise_for_status()
    results = resp.json().get("videos", [])
    for video in results:
        if video.get("id") in exclude_ids:
            continue
        portrait = [f for f in video["video_files"] if f.get("width", 0) < f.get("height", 1)]
        if not portrait:
            continue
        # 1080 genislige kadar olan en buyuk dosya; yoksa en kucuk buyuk dosya
        fitting = [f for f in portrait if f.get("width", 0) <= MAX_FILE_WIDTH]
        chosen = (
            max(fitting, key=lambda f: f.get("width", 0)) if fitting
            else min(portrait, key=lambda f: f.get("width", 0))
        )
        return {"id": video.get("id"), "url": chosen["link"], "duration": video.get("duration", 6)}
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
