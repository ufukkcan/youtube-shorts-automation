"""
Script metnini edge-tts (ucretsiz, Microsoft Edge okuma motoru) ile seslendirir.
Turkce icin: tr-TR-EmelNeural (kadin) veya tr-TR-AhmetNeural (erkek)
Ingilizce icin: en-US-AriaNeural, en-US-GuyNeural gibi secenekler var.
Tum ses listesi icin: edge-tts --list-voices
"""
import asyncio
import os
import subprocess

import edge_tts

VOICE = os.environ.get("TTS_VOICE", "en-US-AriaNeural")
RATE = os.environ.get("TTS_RATE", "+5%")  # shorts icin biraz hizli anlatim daha akici durur


async def _synthesize(text: str, output_path: str) -> None:
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(output_path)


def generate_voice(text: str, output_path: str) -> float:
    """Sesi uretir ve saniye cinsinden suresini dondurur."""
    asyncio.run(_synthesize(text, output_path))
    return _get_duration(output_path)


def _get_duration(path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


if __name__ == "__main__":
    import sys
    duration = generate_voice(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "voice.mp3")
    print(f"Ses uretildi, sure: {duration:.1f}s")
