"""
Telegram Bot API ile dogrudan HTTP istekleri uzerinden konusur (ek kutuphane gerekmez).
Sadece TELEGRAM_CHAT_ID ile eslesen mesaj/tiklamalari isler, boylece baskasi
botu bulup mudahale edemez.
"""
import json
import os

import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_topic_options(candidates: list[dict], batch_id: str) -> int:
    """5 konuyu numarali liste + tiklanabilir butonlarla gonderir. Mesaj id'sini dondurur."""
    lines = [f"Bugunun shorts konulari ({batch_id}):\n"]
    for i, c in enumerate(candidates, start=1):
        lines.append(f"{i}) {c['teaser']}")
    text = "\n".join(lines)

    buttons = [
        {"text": str(i), "callback_data": f"select:{batch_id}:{i - 1}"}
        for i in range(1, len(candidates) + 1)
    ]

    resp = requests.post(
        f"{API_BASE}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "reply_markup": {"inline_keyboard": [buttons]},
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()["result"]["message_id"]


def edit_message(message_id: int, text: str) -> None:
    requests.post(
        f"{API_BASE}/editMessageText",
        json={"chat_id": CHAT_ID, "message_id": message_id, "text": text},
        timeout=20,
    )


def send_message(text: str) -> None:
    requests.post(f"{API_BASE}/sendMessage", json={"chat_id": CHAT_ID, "text": text}, timeout=20)


def answer_callback_query(callback_query_id: str, text: str = "") -> None:
    requests.post(
        f"{API_BASE}/answerCallbackQuery",
        json={"callback_query_id": callback_query_id, "text": text},
        timeout=20,
    )


def get_updates(offset: int | None) -> list[dict]:
    """Son kontrolden bu yana gelen yeni update'leri ceker (short poll, timeout=5s)."""
    params = {"timeout": 5}
    if offset is not None:
        params["offset"] = offset
    resp = requests.get(f"{API_BASE}/getUpdates", params=params, timeout=15)
    resp.raise_for_status()
    return resp.json().get("result", [])


def send_video_for_review(video_path: str, content: dict, batch_id: str) -> tuple[int, str]:
    """Uretilen videoyu Telegram'a yukleyip Onayla/Tekrar uret butonlariyla gonderir.
    (message_id, telegram_file_id) dondurur. file_id sayesinde onay gelene kadar
    videoyu tekrar indirmemize gerek kalmaz -- Telegram gecici depomuz gibi calisir."""
    caption = f"Onayina sunuluyor: {content['topic']}\n\n{content['video_title']}"[:1024]
    buttons = {
        "inline_keyboard": [[
            {"text": "Onayla, yayinla", "callback_data": f"review:{batch_id}:approve"},
            {"text": "Begenmedim, tekrar uret", "callback_data": f"review:{batch_id}:redo"},
        ]]
    }
    with open(video_path, "rb") as f:
        resp = requests.post(
            f"{API_BASE}/sendVideo",
            data={
                "chat_id": CHAT_ID,
                "caption": caption,
                "supports_streaming": "true",
                "reply_markup": json.dumps(buttons),
            },
            files={"video": f},
            timeout=180,
        )
    resp.raise_for_status()
    result = resp.json()["result"]
    return result["message_id"], result["video"]["file_id"]


def download_review_video(file_id: str, dest_path: str) -> None:
    """Daha once Telegram'a gonderilmis videoyu file_id ile geri indirir
    (onaylanan videoyu tekrar uretmeden dogrudan YouTube'a yuklemek icin)."""
    resp = requests.get(f"{API_BASE}/getFile", params={"file_id": file_id}, timeout=20)
    resp.raise_for_status()
    file_path = resp.json()["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    with requests.get(file_url, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as out:
            for chunk in r.iter_content(chunk_size=1 << 16):
                out.write(chunk)


def find_review_decision(updates: list[dict], batch_id: str) -> str | None:
    """'review:{batch_id}:approve' veya '...:redo' callback'ini arar, bulursa
    'approve' / 'redo' dondurur ve kullaniciya kisa bir onay gosterir."""
    for update in updates:
        callback = update.get("callback_query")
        if not callback:
            continue
        if str(callback["message"]["chat"]["id"]) != str(CHAT_ID):
            continue
        prefix = f"review:{batch_id}:"
        data = callback.get("data", "")
        if not data.startswith(prefix):
            continue
        decision = data[len(prefix):]
        feedback = "Yukleniyor..." if decision == "approve" else "Yeniden uretiliyor..."
        answer_callback_query(callback["id"], text=feedback)
        return decision
    return None


def find_manual_trigger(updates: list[dict]) -> bool:
    """Kullanicinin bota duz metin olarak 'video uret' (veya /uret, /video)
    yazip yazmadigina bakar. Boylece gunun herhangi bir saatinde, otomatik
    saati beklemeden surece manuel baslatabilir."""
    trigger_phrases = {"video uret", "video üret", "uret", "üret", "/uret", "/video", "/generate"}
    for update in updates:
        message = update.get("message")
        if not message:
            continue
        if str(message.get("chat", {}).get("id")) != str(CHAT_ID):
            continue
        text = message.get("text", "").strip().lower()
        if text in trigger_phrases:
            return True
    return False


def send_hashtag_options(hashtags: list[str], batch_id: str) -> int:
    """Konuyla ilgili hashtag adaylarini, secilebilir (tiklandikca isaretlenen)
    butonlarla gonderir. Mesaj id'sini dondurur."""
    text = _hashtag_message_text(hashtags, selected_indices=[])
    resp = requests.post(
        f"{API_BASE}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "reply_markup": {"inline_keyboard": _hashtag_keyboard(hashtags, batch_id, [])},
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()["result"]["message_id"]


def update_hashtag_message(message_id: int, hashtags: list[str], selected_indices: list[int], batch_id: str) -> None:
    """Secim degistikce mesaji (metin + isaretli butonlar) gunceller."""
    requests.post(
        f"{API_BASE}/editMessageText",
        json={
            "chat_id": CHAT_ID,
            "message_id": message_id,
            "text": _hashtag_message_text(hashtags, selected_indices),
            "reply_markup": {"inline_keyboard": _hashtag_keyboard(hashtags, batch_id, selected_indices)},
        },
        timeout=20,
    )


def _hashtag_message_text(hashtags: list[str], selected_indices: list[int]) -> str:
    lines = [f"Bu konuyla ilgili 5 hashtag sec ({len(selected_indices)}/5 secildi):\n"]
    for i, tag in enumerate(hashtags):
        mark = "[secildi] " if i in selected_indices else ""
        lines.append(f"{mark}{i + 1}) #{tag}")
    return "\n".join(lines)


def _hashtag_keyboard(hashtags: list[str], batch_id: str, selected_indices: list[int]) -> list[list[dict]]:
    rows = []
    for i in range(0, len(hashtags), 2):
        row = []
        for j in (i, i + 1):
            if j < len(hashtags):
                label = f"{'v ' if j in selected_indices else ''}{j + 1}"
                row.append({"text": label, "callback_data": f"htag:{batch_id}:{j}"})
        rows.append(row)
    return rows


def find_hashtag_toggles(updates: list[dict], batch_id: str) -> list[int]:
    """Bu batch_id icin gelen TUM hashtag tiklamalarini SIRAYLA dondurur.
    Yoklama araligi birkac dakika oldugu icin kullanici arka arkaya birden
    fazla hashtag'e tiklamis olabilir -- hepsini sirayla isleriz, tek tek
    degil (yoksa aradaki tiklamalari kaybederiz)."""
    indices = []
    prefix = f"htag:{batch_id}:"
    for update in updates:
        callback = update.get("callback_query")
        if not callback:
            continue
        if str(callback["message"]["chat"]["id"]) != str(CHAT_ID):
            continue
        data = callback.get("data", "")
        if not data.startswith(prefix):
            continue
        indices.append(int(data[len(prefix):]))
        answer_callback_query(callback["id"])
    return indices


def find_selection(updates: list[dict], batch_id: str) -> int | None:
    """Bu batch_id icin, dogru chat_id'den gelen bir buton tiklamasi var mi bakar.
    Varsa secilen indexi (0-4) dondurur, callback'i yanitlar."""
    for update in updates:
        callback = update.get("callback_query")
        if not callback:
            continue
        if str(callback["message"]["chat"]["id"]) != str(CHAT_ID):
            continue
        data = callback.get("data", "")
        if not data.startswith(f"select:{batch_id}:"):
            continue
        index = int(data.rsplit(":", 1)[1])
        answer_callback_query(callback["id"], text=f"{index + 1} secildi, uretim basliyor...")
        return index
    return None
