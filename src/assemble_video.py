"""
Stok klipleri birlestirir, 1080x1920 (9:16 shorts) formatina getirir,
ses dosyasini ekler, altyaziyi yakar ve izlenme/etkilesim icin ek katmanlar
ekler: ilk 3 saniyede buyuk "kanca" metni, video ortasinda abone-ol butonu,
son 3 saniyede paylas/takip cagrisi.
"""
import subprocess
from pathlib import Path

WIDTH, HEIGHT = 1080, 1920
TARGET_MAX_MB = 30.0
AUDIO_BITRATE_KBPS = 128

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
SUBSCRIBE_BUTTON_PATH = ASSETS_DIR / "subscribe_button.png"

HOOK_DURATION = 3.0
CTA_DURATION = 3.0
BUTTON_WIDTH = 460
CTA_TEXT = "FOLLOW FOR MORE"


def assemble(
    clip_paths: list[str],
    audio_path: str,
    srt_path: str,
    output_path: str,
    target_duration: float,
    hook_text: str | None = None,
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

    subtitle_style = (
        "FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,"
        "Alignment=2,MarginV=40"
    )

    video_kbps = _compute_video_bitrate_kbps(target_duration)

    hook_file = work_dir / "hook.txt"
    cta_file = work_dir / "cta.txt"
    hook_file.write_text(hook_text or "", encoding="utf-8")
    cta_file.write_text(CTA_TEXT, encoding="utf-8")

    btn_start = min(HOOK_DURATION, max(target_duration - CTA_DURATION - 2, 0))
    btn_end = max(target_duration - CTA_DURATION - 0.5, btn_start + 0.5)
    cta_start = max(target_duration - CTA_DURATION, 0)

    box_style = "box=1:boxcolor=black@0.55:boxborderw=18"
    filter_complex = (
        f"[0:v]subtitles={_esc(str(srt_path))}:"
        f"force_style='{subtitle_style}'[sub];"
        f"[sub]drawtext=fontfile={_esc(FONT_PATH)}:textfile={_esc(str(hook_file))}:"
        f"fontsize=58:fontcolor=white:{box_style}:line_spacing=10:"
        f"x=(w-text_w)/2:y=170:enable='lt(t,{HOOK_DURATION})'[hooked];"
        f"[hooked]drawtext=fontfile={_esc(FONT_PATH)}:textfile={_esc(str(cta_file))}:"
        f"fontsize=52:fontcolor=white:{box_style}:"
        f"x=(w-text_w)/2:y=(h-text_h)/2:enable='gte(t,{cta_start})'[cta];"
        f"[2:v]scale={BUTTON_WIDTH}:-1[btn];"
        f"[cta][btn]overlay=x=(W-w)/2:y=170:enable='between(t,{btn_start},{btn_end})'[vout]"
    )

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(silent_video),
            "-i", audio_path,
            "-loop", "1", "-i", str(SUBSCRIBE_BUTTON_PATH),
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
    return path.replace("\\", "/").replace(":", "\\:")


def _compute_video_bitrate_kbps(duration_seconds: float) -> int:
    total_kbps = (TARGET_MAX_MB * 8192) / max(duration_seconds, 1.0)
    video_kbps = total_kbps - AUDIO_BITRATE_KBPS
    return int(max(700, min(video_kbps, 5000)))


def _normalize_clips(clip_paths: list[str], work_dir: Path, target_duration: float) -> list[str]:
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
