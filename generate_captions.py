"""
Uretilen ses dosyasini analiz edip kelime zamanlamali .srt altyazi dosyasi cikarir.
Shorts tarzi icin altyazilari kisa (2-4 kelimelik) parcalara boler, boylece
ekranda vurgulu, hizli akan altyazi gorunumu olur.
faster-whisper tamamen ucretsiz ve yerel calisir (ilk calistirmada model indirir).
"""
from faster_whisper import WhisperModel

WORDS_PER_CHUNK = 3
MODEL_SIZE = "small"  # dogruluk/hiz dengesi icin yeterli; "base" daha hizli, "medium" daha dogru


def _format_timestamp(seconds: float) -> str:
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    millis = int((secs - int(secs)) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(secs):02d},{millis:03d}"


def generate_srt(audio_path: str, srt_path: str, language: str = "en") -> None:
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, language=language, word_timestamps=True)

    words = []
    for segment in segments:
        words.extend(segment.words)

    lines = []
    index = 1
    for chunk_start in range(0, len(words), WORDS_PER_CHUNK):
        chunk = words[chunk_start:chunk_start + WORDS_PER_CHUNK]
        if not chunk:
            continue
        text = " ".join(w.word.strip() for w in chunk)
        start = _format_timestamp(chunk[0].start)
        end = _format_timestamp(chunk[-1].end)
        lines.append(f"{index}\n{start} --> {end}\n{text}\n")
        index += 1

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    import sys
    generate_srt(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "tr")
    print("Altyazi olusturuldu:", sys.argv[2])
