"""
Konu+script hazir oldugunda calisan uretim adimlari.
produce_video(): sadece videoyu uretir, TIKTOK'A YUKLEMEZ (once Telegram'da
onaya sunulacak). upload_video(): onaylanmis videoyu TikTok'a yukler.
produce_and_upload(): TAM OTOMATIK mod icin ikisini art arda calistiran
geriye-donuk-uyumlu kisayol (main.py bunu kullanir).

NOT: TikTok'un Content Posting API'sinde YouTube'daki gibi native bir
"belirli saatte yayinla" ozelligi bulunmuyor (ya da en azindan dogrulayamadim).
Bu yuzden PUBLISH_TIME_ISTANBUL ozelligini KENDI KODUMUZLA koruyoruz:
onay geldiginde hemen yuklemek yerine, check_and_produce.py o saat gelene
kadar bekleyip, o an videoyu (yeniden uretip) TikTok'a yukluyor.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import tiktok_upload
from assemble_video import assemble
from fetch_visuals import fetch_clips
from generate_captions import generate_srt
from generate_voice import generate_voice

LANGUAGE = os.environ.get("CONTENT_LANGUAGE", "en")
ISTANBUL = ZoneInfo("Europe/Istanbul")


def next_publish_at_utc(hhmm: str) -> str:
    """'20:00' gibi bir Istanbul saatini alir, bir sonraki gelecek
    zamanlanmis anini (bugun gectiyse yarin) UTC ISO8601 olarak dondurur."""
    hour, minute = (int(part) for part in hhmm.split(":"))
    now_ist = datetime.now(ISTANBUL)
    target_ist = now_ist.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target_ist <= now_ist:
        target_ist += timedelta(days=1)
    return target_ist.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_hook(script: str) -> str:
    """Scriptin ilk cumlesini (kanca) cikarir, ilk 3 saniyede ekranda
    buyuk metin olarak gosterilecek."""
    script = script.strip()
    for sep in (". ", "! ", "? "):
        idx = script.find(sep)
        if idx != -1:
            return script[: idx + 1].strip()
    return script[:60].strip()


def produce_video(content: dict, work_dir: Path) -> str:
    """content: generate_script.py'nin urettigi tek bir aday sozlugu.
    work_dir: cagiran tarafindan yonetilen (ve temizlenen) bir klasor.
    Donus: uretilen mp4'un yolu (work_dir icinde)."""
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
    """Onaylanmis videoyu TikTok'a yukler, publish_id dondurur.
    TikTok'ta YouTube'daki gibi ayri baslik/aciklama alani yok -- ikisini
    birlestirip tek bir "title" (video altinda gorunen metin) olarak gonderiyoruz."""
    title = f"{content['video_title']}\n\n{content['video_description']}".strip()
    return tiktok_upload.upload_video(video_path, title)


def produce_and_upload(content: dict) -> str:
    """TAM OTOMATIK mod icin: uret + onaysiz direkt yukle."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        video_path = produce_video(content, Path(tmp))
        publish_id = upload_video(video_path, content)
        print(f"Tamamlandi, TikTok publish_id: {publish_id}")
        return publish_id
