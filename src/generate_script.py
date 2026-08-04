"""
Gunluk 'ilginc bilgi' icin BIRDEN FAZLA aday konu ve script uretir.
Kullanici Telegram'dan birini secer, secilen tam icerik uretime gonderilir.
Daha once kullanilan/gosterilen konulari state/topics_used.json icinde tutar, tekrari onler.
"""
import json
import os
from pathlib import Path

from anthropic import Anthropic

STATE_FILE = Path(__file__).resolve().parent.parent / "state" / "topics_used.json"
LANGUAGE = os.environ.get("CONTENT_LANGUAGE", "en")  # "en" veya "tr"

SYSTEM_PROMPT = """Sen viral YouTube Shorts icerik yazarisin. Kanalin konusu:
insanlarin bilmedigi, merak uyandiran, sasirtici gercekler ve ilginc bilgiler.

Her aday icin kurallar:
- Script 30-45 saniyede seslendirilecek uzunlukta olmali (yaklasik 80-110 kelime).
- Ilk cumle mutlaka guclu bir "kanca" (hook) olmali, izleyiciyi ilk 2 saniyede yakalamali.
- Orta kisim carpici, somut, dogrulanabilir bir bilgi anlatmali.
- Kapanis bir soru ya da beklenmedik bir "twist" ile bitmeli (izleyici yorum yapsin diye).
- Konusma dili sade, akici, TV programi anlatici tonunda olmali. Baslik/madde isareti YOK, duz akan metin.
- Adaylarin konulari birbirinden FARKLI kategorilerden olmali (bilim, tarih, hayvanlar, uzay, insan vucudu, teknoloji, gunluk hayat vb. karistir).
- Cikti SADECE gecerli JSON olmali, baska hicbir sey yazma (aciklama, markdown, kod bloğu yok).

DIL KURALI (EN ONEMLI KURAL, HER SEYDEN ONCELIKLI):
Bu talimatlarin kendisi Turkce yazilmis olsa da, bu SADECE senin (yapay zekanin)
talimati anlamasi icin boyle -- URETECEGIN ICERIGIN dili tamamen ayri bir konu ve
SADECE kullanicinin mesajindaki "Dil:" alaninda belirttigi dile gore belirlenir.
Talimatlarin dili ile cikti dili birbirine KARISTIRILMAMALI."""

CANDIDATE_SCHEMA = """{
  "topic": "kisa konu basligi (dahili takip icin)",
  "teaser": "Telegram'da gosterilecek, 1 cumlelik merak uyandirici on izleme (spoiler vermeden)",
  "video_title": "YouTube icin tiklanabilir, merak uyandiran baslik (60 karakter alti)",
  "video_description": "2-3 cumlelik aciklama + sonunda 5-8 ilgili hashtag",
  "tags": ["etiket1", "etiket2", "..."],
  "script": "seslendirilecek tam metin, tek paragraf",
  "visual_keywords": ["pexels aramasi icin 3-5 ingilizce anahtar kelime, konuyla gorsel eslesecek somut nesneler/mekanlar"]
}"""

USER_PROMPT_TEMPLATE = """CIKTI DILI: {language}
(topic, teaser, video_title, video_description, script alanlarinin TAMAMI
{language} dilinde olacak -- tags ve visual_keywords her zaman Ingilizce kalir
cunku bunlar YouTube etiketleme ve Pexels aramasi icin kullanilir.)

Daha once kullanilmis/gosterilmis konular (bunlari TEKRAR ETME): {used_topics}

Tam olarak {n} FARKLI aday konu uret. Cikti, her biri asagidaki semaya uyan
{n} objeden olusan bir JSON DIZISI olmali:
{schema}

HATIRLATMA: yukaridaki tum metin alanlari (tags/visual_keywords haric) {language}
dilinde olmali. Bu talimati atlama."""


def load_used_topics() -> list:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8")).get("topics", [])
    return []


def save_used_topics(topics_to_add: list[str]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    topics = load_used_topics()
    topics.extend(topics_to_add)
    # son 300 konuyu tut, dosya sonsuza kadar buyumesin
    topics = topics[-300:]
    STATE_FILE.write_text(json.dumps({"topics": topics}, ensure_ascii=False, indent=2), encoding="utf-8")


def _call_claude(n: int) -> list[dict]:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    used_topics = load_used_topics()

    prompt = USER_PROMPT_TEMPLATE.format(
        language="Turkce" if LANGUAGE == "tr" else "English",
        used_topics=", ".join(used_topics[-60:]) if used_topics else "(yok, ilk video)",
        n=n,
        schema=CANDIDATE_SCHEMA,
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = "".join(block.text for block in response.content if block.type == "text").strip()
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw_text)


def generate_topic_candidates(n: int = 5) -> list[dict]:
    """n adet farkli aday konu+script uretir. Hepsi 'gosterilmis' olarak
    isaretlenir (secilmese bile), boylece yarin tekrar onerilmezler."""
    candidates = _call_claude(n)
    save_used_topics([c["topic"] for c in candidates])
    return candidates


def generate_daily_content() -> dict:
    """Geriye donuk uyumluluk: tam otomatik (secimsiz) mod icin tek konu uretir."""
    return generate_topic_candidates(n=1)[0]


if __name__ == "__main__":
    candidates = generate_topic_candidates(n=5)
    print(json.dumps(candidates, ensure_ascii=False, indent=2))
