"""
ONIZLEME -- canli akisa dokunmadan (state dosyalari, Telegram offset'i, YouTube)
tek bir ornek video uretir ve Telegram'a sadece bilgi amacli gonderir.
Format degisikliklerini canliya almadan once gormek icin; .github/workflows/
preview.yml elle tetikler, hicbir sey commit edilmez, YouTube'a yukleme yapilmaz.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path

import requests

from generate_script import _call_claude  # topics_used.json'a YAZMAZ
from pipeline import produce_video
from telegram_bot import API_BASE, CHAT_ID


def main() -> None:
    candidate = _call_claude(1)[0]
    print(json.dumps(candidate, ensure_ascii=False, indent=2))

    with tempfile.TemporaryDirectory() as tmp:
        video_path = produce_video(candidate, Path(tmp))
        duration = _duration(video_path)
        size_mb = os.path.getsize(video_path) / (1024 * 1024)
        words = len(candidate["script"].split())
        print(f"Onizleme videosu: {duration:.1f} sn, {size_mb:.1f} MB, {words} kelime")

        caption = (
            f"ONIZLEME (YouTube'a yuklenmeyecek)\n"
            f"{candidate['video_title']}\n"
            f"{duration:.1f} sn | {words} kelime | {size_mb:.1f} MB\n\n"
            f"{candidate['script']}"
        )[:1024]
        with open(video_path, "rb") as f:
            resp = requests.post(
                f"{API_BASE}/sendVideo",
                data={"chat_id": CHAT_ID, "caption": caption, "supports_streaming": "true"},
                files={"video": f},
                timeout=180,
            )
        resp.raise_for_status()
    print("Onizleme Telegram'a gonderildi.")


def _duration(path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


if __name__ == "__main__":
    main()
