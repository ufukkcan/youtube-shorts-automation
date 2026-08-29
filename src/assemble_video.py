"""
Stok klipleri birlestirir, 1080x1920 (9:16 shorts) formatina getirir,
ses dosyasini ekler, altyaziyi yakar ve izlenme/etkilesim icin ek katmanlar
ekler: kisa bir "Subscribe" dokunma animasyonu (kucuk, video basinda bir kez),
son 3 saniyede abone cagrisi metni.
"""
import subprocess
from pathlib import Path

WIDTH, HEIGHT = 1080, 1920
TARGET_MAX_MB = 30.0
AUDIO_BITRATE_KBPS = 128

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
FOLLOW_BUTTON_PATH = ASSETS_DIR / "follow_button.png"
TAP_RING_PATH = ASSETS_DIR / "tap_ring.png"

CTA_DURATION = 3.0              # abone cagrisi metni son kac saniye ekranda kalsin
BUTTON_WIDTH = 260              # Subscribe butonu piksel genisligi (KUCUK -- 1080 icinde)
BUTTON_START = 1.2              # video basladiktan kac saniye sonra buton belirsin
BUTTON_VISIBLE_SECONDS = 1.8    # buton kac saniye ekranda kalsin (KISA)
RING_DELAY_AFTER_BUTTON = 0.35  # buton "oturduktan" ne kadar sonra dokunma halkasi patlasin
RING_VISIBLE_SECONDS = 0.35     # dokunma halkasi ne kadar ekranda kalsin (cok kisa, ani bir "tik")
BUTTON_Y = 170                  # butonun dikey konumu (ust bolge, altyazidan uzak)
CTA_TEXT = "SUBSCRIBE"


def assemble(
    clip_paths: list[str],
    audio_path: str,
    srt_path: str,
    output_path: str,
    target_duration: float,
    hook_text: str | None = None,  # artik kullanilmiyor, geriye-donuk uyumluluk icin duruyor
) -> None:
    work_dir = Path(output_path).parent
    work_dir.mkdir(parents=True, exist_ok=True)

    concat_list_path = work_dir / "concat_list.txt"
    normalized_paths = _normalize_clips(clip_paths, work_dir, target_duration)
    concat_list_path.write_text(
        "\n".join(f"file '{Path(p).resolve()}'" for p in normalized_paths), encoding="utf-8"
    )

    silent_video = work_dir / "silent_combined.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list_path),
            "-c", "copy", str(silent_video),
        ],
        check=True, capture_output=True,
    )

    # Altyazi stili: alt bolgede ama YouTube'un kendi aciklama/kanal adi
    # alanindan (ekranin en alt ~350-400px'i) net sekilde yukarida.
    # MarginV=170 deneysel olarak dogrulandi (MarginV libass tarafindan buyuk
    # bir katsayiyla olceklendigi icin kucuk degisiklikler bile konumu ciddi
    # sekilde degistirebiliyor).
    subtitle_style = (
        "FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,"
        "Alignment=2,MarginV=170"
    )

    video_kbps = _compute_video_bitrate_kbps(target_duration)

    cta_file = work_dir / "cta.txt"
    cta_file.write_text(CTA_TEXT, encoding="utf-8")

    btn_end = min(BUTTON_START + BUTTON_VISIBLE_SECONDS, max(target_duration - CTA_DURATION - 0.5, BUTTON_START + 0.5))
    ring_start = BUTTON_START + RING_DELAY_AFTER_BUTTON
    ring_end = min(ring_start + RING_VISIBLE_SECONDS, btn_end)
    cta_start = max(target_duration - CTA_DURATION, 0)
    button_center_y = BUTTON_Y + (BUTTON_WIDTH * 110 / 420) / 2  # buton oranini koru

    box_style = "box=1:boxcolor=black@0.55:boxborderw=18"

    # Subscribe butonu icin kisa bir "pop-in" (sicrayarak buyuyup oturma) animasyonu:
    # 0.5x -> 1.15x (asiri buyume) -> 1.0x (oturma). Bir parmakla dokunulmus
    # hissi vermesi icin, oturma anindan hemen sonra kucuk bir "dokunma halkasi"
    # (tap_ring.png) aninda belirip kayboluyor.
    t_btn = f"(t-{BUTTON_START})"
    pop_scale_expr = (
        f"if(lt({t_btn}\\,0.2)\\,0.5+3.25*{t_btn}\\,"
        f"if(lt({t_btn}\\,0.35)\\,1.15-1.0*({t_btn}-0.2)\\,1))"
    )
    btn_scale_w = f"'{BUTTON_WIDTH}*({pop_scale_expr})'"

    t_ring = f"(t-{ring_start})"
    ring_scale_expr = f"'90*(0.6+1.2*{t_ring})'"

    filter_complex = (
        f"[0:v]subtitles={_esc(str(srt_path))}:"
        f"force_style='{subtitle_style}'[sub];"
        f"[sub]drawtext=fontfile={_esc(FONT_PATH)}:textfile={_esc(str(cta_file))}:"
        f"fontsize=52:fontcolor=white:{box_style}:"
        f"x=(w-text_w)/2:y=(h-text_h)/2:enable='gte(t,{cta_start})'[cta];"
        f"[2:v]scale=w={btn_scale_w}:h=-1:eval=frame[btn];"
        f"[cta][btn]overlay=x=(W-w)/2:y={BUTTON_Y}:enable='between(t,{BUTTON_START},{btn_end})'[with_btn];"
        f"[3:v]scale=w={ring_scale_expr}:h=-1:eval=frame[ring];"
        f"[with_btn][ring]overlay=x=(W/2)-w/2:y={button_center_y}-h/2:"
        f"enable='between(t,{ring_start},{ring_end})'[vout]"
    )

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(silent_video),
            "-i", audio_path,
            "-loop", "1", "-i", str(FOLLOW_BUTTON_PATH),
            "-loop", "1", "-i", str(TAP_RING_PATH),
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "medium",
            "-b:v", f"{video_kbps}k", "-maxrate", f"{int(video_kbps * 1.3)}k",
            "-bufsize", f"{int(video_kbps * 2)}k",
            "-c:a", "aac", "-b:a", f"{AUDIO_BITRATE_KBPS}k",
            "-shortest", str(output_path),
        ],
        check=True, capture_output=True,
    )


def _esc(path: str) -> str:
    """ffmpeg filter graph icinde dosya yolunu guvenli hale getirir."""
    return path.replace("\\", "/").replace(":", "\\:")


def _compute_video_bitrate_kbps(duration_seconds: float) -> int:
    """Hedef dosya boyutuna (TARGET_MAX_MB) gore video bitrate'i hesaplar,
    boylece uzun/detayli videolar bile Telegram'in 50MB sinirini asmaz."""
    total_kbps = (TARGET_MAX_MB * 8192) / max(duration_seconds, 1.0)  # 1 MB = 8192 kbit
    video_kbps = total_kbps - AUDIO_BITRATE_KBPS
    return int(max(700, min(video_kbps, 5000)))


def _normalize_clips(clip_paths: list[str], work_dir: Path, target_duration: float) -> list[str]:
    """Her klibi 1080x1920'ye scale+crop eder, sabit fps/codec'e ceker
    (concat demuxer'in calismasi icin tum kliplerin ayni format olmasi sart)."""
    normalized = []
    per_clip_duration = max(target_duration / len(clip_paths), 2.0)

    for i, clip in enumerate(clip_paths):
        dest = work_dir / f"norm_{i:02d}.mp4"
        vf = (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},fps=30"
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", clip, "-t", str(per_clip_duration),
                "-vf", vf, "-an",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                str(dest),
            ],
            check=True, capture_output=True,
        )
        normalized.append(str(dest))
    return normalized


if __name__ == "__main__":
    import sys
    assemble(
        clip_paths=sys.argv[1].split(","),
        audio_path=sys.argv[2],
        srt_path=sys.argv[3],
        output_path=sys.argv[4],
        target_duration=float(sys.argv[5]),
    )
    print("Video hazir:", sys.argv[4])
