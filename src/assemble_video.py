"""
Stok klipleri birlestirir, 1080x1920 (9:16 shorts) formatina getirir,
ses dosyasini ekler ve altyaziyi video uzerine yakar.
"""
import subprocess
from pathlib import Path

WIDTH, HEIGHT = 1080, 1920


def assemble(clip_paths: list[str], audio_path: str, srt_path: str, output_path: str, target_duration: float) -> None:
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

    # Altyazi stili: alt-orta hizalanmis, okunakli, shorts icin buyuk font
    subtitle_style = (
        "FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,"
        "Alignment=2,MarginV=140"
    )

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(silent_video), "-i", audio_path,
            "-vf", f"subtitles={srt_path}:force_style='{subtitle_style}'",
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", str(output_path),
        ],
        check=True, capture_output=True,
    )


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
