"""
Konu+script hazir oldugunda calisan uretim adimlari.
produce_video(): sadece videoyu uretir, YOUTUBE'A YUKLEMEZ (once Telegram'da
onaya sunulacak). upload_video(): onaylanmis videoyu YouTube'a yukler.
produce_and_upload(): TAM OTOMATIK mod icin ikisini art arda calistiran
geriye-donuk-uyumlu kisayol (main.py bunu kullanir).
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from assemble_video import assemble
from fetch_visuals import fetch_clips
from generate_captions import generate_srt
from generate_voice import generate_voice
from upload_youtube import upload_short

LANGUAGE = os.environ.get("CONTENT_LANGUAGE", "en")
PRIVACY_STATUS = os.environ.get("PRIVACY_STATUS", "public")
PUBLISH_TIME_ISTANBUL = os.environ.get("PUBLISH_TIME_ISTANBUL", "20:00")
ISTANBUL = ZoneInfo("Europe/Istanbul")


def _next_publish_at_utc(hhmm: str) -> str:
    hour, minute = (int(part) for part in hhmm.split(":"))
    now_ist = datetime.now(ISTANBUL)
    target_ist = now_ist.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target_ist <= now_ist:
        target_ist += timedelta(days=1)
    return target_ist.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_hook(script: str) -> str:
    script = script.strip()
    for sep in (". ", "! ", "? "):
        idx = script.find(sep)
        if idx != -1:
            return script[: idx + 1].strip()
    return script[:60].strip()


def produce_video(content: dict, work_dir: Path) -> str:
    work_dir = Path(work_dir)

    print("1/4 Seslendirme yapiliyor...")
    audio_path = work_dir / "voice.mp3"
    duration = generate_voice(content["script"], str(audio_path))
    print(f"   Ses suresi: {duration:.1f}s")

    print("2/4 Gorseller cekiliyor...")
    clips_dir = work_dir / "clips"
    clip_paths = fetch_clips(content["visual_keywords"], str(clips_dir), duration)
    print(f"   {len(clip_paths)} klip indirildi")

    print("3/4 Altyazi cikariliyor...")
    srt_path = work_dir / "captions.srt"
    generate_srt(str(audio_path), str(srt_path), language=LANGUAGE)

    print("4/4 Video montajlaniyor...")
    output_path = work_dir / "final.mp4"
    hook_text = _extract_hook(content["script"])
    assemble(clip_paths, str(audio_path), str(srt_path), str(output_path), duration, hook_text=hook_text)
    return str(output_path)


def upload_video(video_path: str, content: dict) -> str:
    publish_at = None
    if PUBLISH_TIME_ISTANBUL and PUBLISH_TIME_ISTANBUL.lower() != "off":
        publish_at = _next_publish_at_utc(PUBLISH_TIME_ISTANBUL)
        print(f"   Zamanlanmis yayin: {publish_at} (UTC) / Istanbul {PUBLISH_TIME_ISTANBUL}")

    description = content["video_description"]
    if "#shorts" not in description.lower():
        description = description.rstrip() + "\n\n#Shorts"

    return upload_short(
        video_path=video_path,
        title=content["video_title"],
        description=description,
        tags=content["tags"],
        privacy_status=PRIVACY_STATUS,
        publish_at=publish_at,
    )


def produce_and_upload(content: dict) -> str:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        video_path = produce_video(content, Path(tmp))
        video_id = upload_video(video_path, content)
        print(f"Tamamlandi: https://youtube.com/shorts/{video_id}")
        return video_id
