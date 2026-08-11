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

SYSTEM_PROMPT = """Sen dunyanin en cok izlenen YouTube Shorts kanalinin bas
yazarisin -- videolarin milyonlarca kez izleniyor ve Kesfet'e dusuyor.
Kanalin konusu: insanlarin bilmedigi, merak uyandiran, sasirtici gercekler.

ASAGIDAKI KURALLAR, GERCEK VIRAL SHORTS ICERIK URETICILERININ KULLANDIGI,
KANITLANMIS TEKNIKLERDIR. HER BIRINE HARFIYEN UY:

1) ILK 3 SANIYE HER SEYDIR (algoritma kaydirma/izlenme oranina bakiyor):
   - ILK CUMLE tek basina, sesi kapali kaydiran birini bile durdurmali.
   - YASAK acilislar: "Did you know...", "Bugun size...", "Merhaba", genel
     sorularla baslama. Bunlarin YERINE su tekniklerden birini kullan:
     a) SOK EDICI TEK CUMLE ile ac ("Bu adam 200 yil once olmustu ama hala nefes aliyor.")
     b) YAYGIN INANCI YIKAN cumle ("Sandigimizin aksine, X hicbir zaman Y yapmadi.")
     c) OLAYIN TAM ORTASINDAN baslama (sahneyi, sonucu degil, tam aksiyon anini anlat)
   - Kancada CEVABIN TAMAMINI VERME -- merak acigi (curiosity gap) birak,
     izleyici "peki nasil/neden" diye izlemeye devam etsin.

2) TEMPO: Script 22-32 saniyede seslendirilecek uzunlukta olmali (yaklasik
   65-85 kelime). Daha KISA ve YOGUN, izleyici sikilmadan bitsin, tamamlama
   orani (completion rate) yuksek olsun -- bu, algoritmanin en onemli sinyali.

3) YAPI (kanca -> gerilim -> carpici detay -> twist/soru):
   - Kancadan sonra bilgiyi TEK SEFERDE dokme, kucuk bir gerilim/bekleme yarat.
   - Orta kisim somut, dogrulanabilir, SAYISAL/SPESIFIK detaylar icermeli
     (rakam, tarih, isim -- "cok eskiden" degil "3000 yil once" gibi).
   - KAPANIS mutlaka ya (a) izleyicinin YORUM YAPMASINI tetikleyen bolucu/
     tartismali bir soru, ya da (b) baslangictaki kancaya geri donen bir
     "twist" olmali (bu, tekrar izlemeyi/loop etkisini artirir).

4) Konusma dili sade, hizli, tarih/belgesel anlaticisi tonunda. Baslik/madde
   isareti YOK, duz akan tek paragraf metin. Gereksiz giris/bagli cumleler yok.

5) Adaylarin konulari birbirinden FARKLI kategorilerden olmali (bilim, tarih,
   hayvanlar, uzay, insan vucudu, teknoloji, gunluk hayat vb. karistir).

6) Cikti SADECE gecerli JSON olmali, baska hicbir sey yazma.

DIL KURALI (EN ONEMLI KURAL, HER SEYDEN ONCELIKLI):
Bu talimatlarin kendisi Turkce yazilmis olsa da, bu SADECE senin (yapay zekanin)
talimati anlamasi icin boyle -- URETECEGIN ICERIGIN dili tamamen ayri bir konu ve
SADECE kullanicinin mesajindaki "Dil:" alaninda belirttigi dile gore belirlenir.
Talimatlarin dili ile cikti dili birbirine KARISTIRILMAMALI."""

CANDIDATE_SCHEMA = """{
  "topic": "kisa konu basligi (dahili takip icin)",
  "teaser": "Telegram'da gosterilecek, 1 cumlelik merak uyandirici on izleme (spoiler vermeden, cevabi verme)",
  "video_title": "TikTok icin tiklanabilir, merak uyandiran baslik (60 karakter alti)",
  "video_description": "2-3 cumlelik aciklama (kullanilmayabilir, yedek)",
  "tags": ["TAM OLARAK 10 hashtag adayi, CIKTI DILINDE (asagidaki 'Dil' kuralina uy). Ilk 6-7'si konuyla DOGRUDAN ilgili spesifik hashtag'ler (orn. konu 'Kleopatra' ise 'kleopatra', 'antikmisir', 'tarih' gibi), son 3-4'u ise TikTok'ta kesfet/FYP'ye dusmeye yardimci EVRENSEL/JENERIK hashtag'ler olmali: fyp, foryou, viral, trend, kesfet, bilgi, ilginc gibi (fyp/foryou/viral yaygin oldugu icin degistirilmeden kullanilabilir, digerleri cikti diline cevrilebilir). Her hashtag bosluksuz tek kelime/bitisik olmali."],
  "script": "seslendirilecek tam metin, 65-85 kelime, tek paragraf -- ilk cumle SOK EDICI kanca olmali",
  "visual_keywords": ["pexels aramasi icin 3-5 İNGİLİZCE anahtar kelime (cikti dili ne olursa olsun bu alan HER ZAMAN Ingilizce kalir, cunku Pexels'te arama Ingilizce daha iyi sonuc veriyor), konuyla gorsel eslesecek somut nesneler/mekanlar"]
}"""

USER_PROMPT_TEMPLATE = """CIKTI DILI: {language}
(topic, teaser, video_title, video_description, script VE tags alanlarinin
TAMAMI {language} dilinde olacak -- SADECE visual_keywords her zaman
Ingilizce kalir, cunku Pexels'te arama Ingilizce daha iyi sonuc veriyor.
tags icindeki fyp/foryou/viral gibi evrensel hashtag'ler istisna,
degistirilmeden kalabilir.)

Daha once kullanilmis/gosterilmis konular (bunlari TEKRAR ETME): {used_topics}

Tam olarak {n} FARKLI aday konu uret. Cikti, her biri asagidaki semaya uyan
{n} objeden olusan bir JSON DIZISI olmali:
{schema}

HATIRLATMA: yukaridaki tum metin alanlari (SADECE visual_keywords haric,
tags DAHIL) {language} dilinde olmali. Bu talimati atlama."""


def load_used_topics() -> list:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8")).get("topics", [])
    return []


def save_used_topics(topics_to_add: list[str]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    topics = load_used_topics()
    topics.extend(topics_to_add)
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
