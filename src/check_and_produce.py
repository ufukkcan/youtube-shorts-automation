"""
Sik araliklarla calisir (cron, or. her 10 dakikada bir). UC asamali surec:

  asama 0 "bugun icin dongu yok" -> Telegram'a "video uret" yazildi mi, ya da
                         AUTO_TRIGGER_TIME saatine gelindi mi? Ikisinden biri
                         olduysa yeni bir 5-konu dongusu baslatir.
  asama 1 "pending"   -> Telegram'da 5 konudan biri secildi mi? Secildiyse
                         videoyu URETIR (henuz YUKLEMEZ) ve onaya Telegram'a
                         gonderir -> durum "reviewing" olur.
  asama 2 "reviewing" -> Kullanici "Onayla" dedi mi, "Tekrar uret" mi dedi?
                         Onayladiysa YouTube'a yukler -> durum "done".
                         Begenmediyse videoyu YENIDEN URETIR, tekrar onaya
                         sunar -> "reviewing" durumunda kalir (dongu).

Kullanici hic yanit vermezse FALLBACK_HOURS sonra ilgili adim otomatik
ilerletilir (secim icin ilk konu, onay icin mevcut video), boylece gunluk
yayin sonsuza kadar beklemede kalmaz.
"""
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import suggest_topics
from pipeline import produce_video, upload_video
from telegram_bot import (
    download_review_video,
    edit_message,
    find_manual_trigger,
    find_review_decision,
    find_selection,
    get_updates,
    send_message,
    send_video_for_review,
)

PENDING_FILE = Path(__file__).resolve().parent.parent / "state" / "pending_topics.json"
OFFSET_FILE = Path(__file__).resolve().parent.parent / "state" / "telegram_offset.json"
FALLBACK_HOURS = float(os.environ.get("FALLBACK_HOURS", "20"))
MAX_REDO_ATTEMPTS = int(os.environ.get("MAX_REDO_ATTEMPTS", "5"))
# Manuel "video uret" gelmezse gunun dongusu bu Istanbul saatinde kendiliginden baslar.
AUTO_TRIGGER_TIME = os.environ.get("AUTO_TRIGGER_TIME", "20:00")
ISTANBUL = ZoneInfo("Europe/Istanbul")


def run() -> None:
    updates = _fetch_updates()
    pending = _load_json(PENDING_FILE)
    today = datetime.now(ISTANBUL).date().isoformat()

    started_today = bool(pending) and pending.get("trigger_date") == today
    # "error" durumunda kalan bir dongu, bugun icin bile olsa yeniden tetiklenebilir
    # (manuel "video uret" veya otomatik saatle) -- boylece gecici bir hata
    # (ag sorunu, kutuphane hatasi vb.) gunu tamamen kilitlemez.
    needs_new_cycle = (not started_today) or (pending.get("status") == "error")

    if needs_new_cycle:
        _handle_idle(updates, pending)
        return

    if pending["status"] == "pending":
        _handle_topic_selection(pending, updates)
    elif pending["status"] == "reviewing":
        _handle_review_decision(pending, updates)
    else:
        print(f"Bugun ({today}) icin dongu zaten tamamlandi (durum: {pending['status']}).")


def _handle_idle(updates: list[dict], pending: dict | None) -> None:
    manual = find_manual_trigger(updates)
    now_hhmm = datetime.now(ISTANBUL).strftime("%H:%M")
    auto_time_reached = now_hhmm >= AUTO_TRIGGER_TIME

    if manual:
        send_message("Alindi! Bugunun konulari hazirlaniyor...")
        print("Manuel tetikleme alindi, yeni dongu baslatiliyor.")
        suggest_topics.run()
    elif auto_time_reached:
        print(f"Otomatik tetikleme saati geldi ({AUTO_TRIGGER_TIME}), yeni dongu baslatiliyor.")
        suggest_topics.run()
    else:
        print(f"Bugun icin henuz tetikleme yok (manuel istek yok, otomatik saat {AUTO_TRIGGER_TIME} henuz gelmedi).")


def _handle_topic_selection(pending: dict, updates: list[dict]) -> None:
    selected_index = find_selection(updates, pending["batch_id"])
    auto_selected = False

    if selected_index is None and _hours_since(pending["created_at"]) >= FALLBACK_HOURS > 0:
        selected_index = 0
        auto_selected = True

    if selected_index is None:
        print("Henuz konu secimi yok.")
        return

    chosen = pending["candidates"][selected_index]
    print(f"Secilen konu: {chosen['topic']} (otomatik: {auto_selected})")
    note = " [yanit gelmedigi icin otomatik secildi]" if auto_selected else ""
    edit_message(pending["message_id"], f"Secildi: {selected_index + 1}) {chosen['topic']}{note}")

    try:
        _produce_and_send_for_review(pending, chosen, attempt_note="Ilk versiyon uretiliyor...")
    except Exception as exc:
        send_message(f"Video uretiminde hata olustu: {exc}\nTekrar denemek icin 'video uret' yazabilirsin.")
        pending["status"] = "error"
        _save_json(PENDING_FILE, pending)
        raise


def _handle_review_decision(pending: dict, updates: list[dict]) -> None:
    decision = find_review_decision(updates, pending["batch_id"])
    timed_out = decision is None and _hours_since(pending["review_started_at"]) >= FALLBACK_HOURS > 0

    if decision is None and not timed_out:
        print("Henuz onay/tekrar-uret karari yok.")
        return

    chosen = pending["candidate"]

    if decision == "redo" and pending["attempts"] >= MAX_REDO_ATTEMPTS:
        send_message(
            f"Maksimum tekrar deneme sayisina ({MAX_REDO_ATTEMPTS}) ulasildi, "
            f"son uretilen versiyon otomatik onaylanip yukleniyor."
        )
        decision = "approve"

    if decision == "approve" or timed_out:
        if timed_out:
            send_message("Yanit gelmedigi icin mevcut video otomatik onaylanip yukleniyor.")
        _download_and_upload(pending, chosen)
        return

    if decision == "redo":
        print(f"Video begenilmedi, yeniden uretiliyor... (deneme {pending['attempts'] + 1})")
        try:
            _produce_and_send_for_review(
                pending, chosen, attempt_note="Yeni versiyon uretiliyor...", is_redo=True
            )
        except Exception as exc:
            send_message(f"Yeniden uretimde hata olustu: {exc}\nTekrar denemek icin 'video uret' yazabilirsin.")
            pending["status"] = "error"
            _save_json(PENDING_FILE, pending)
            raise


def _produce_and_send_for_review(pending: dict, chosen: dict, attempt_note: str, is_redo: bool = False) -> None:
    send_message(attempt_note)
    with tempfile.TemporaryDirectory() as tmp:
        video_path = produce_video(chosen, Path(tmp))
        message_id, file_id = send_video_for_review(video_path, chosen, pending["batch_id"])

    pending["status"] = "reviewing"
    pending["candidate"] = chosen
    pending["video_file_id"] = file_id
    pending["message_id"] = message_id
    pending["review_started_at"] = datetime.now(timezone.utc).isoformat()
    pending["attempts"] = pending.get("attempts", 0) + 1 if is_redo else 1
    _save_json(PENDING_FILE, pending)


def _download_and_upload(pending: dict, chosen: dict) -> None:
    try:
        with tempfile.TemporaryDirectory() as tmp:
            local_path = str(Path(tmp) / "approved.mp4")
            download_review_video(pending["video_file_id"], local_path)
            video_id = upload_video(local_path, chosen)
        send_message(f"Video yayinlandi: https://youtube.com/shorts/{video_id}")
        pending["status"] = "done"
    except Exception as exc:
        send_message(f"Yukleme sirasinda hata olustu: {exc}")
        pending["status"] = "error"
        raise
    finally:
        _save_json(PENDING_FILE, pending)


def _fetch_updates() -> list[dict]:
    offset = _load_json(OFFSET_FILE).get("offset")
    updates = get_updates(offset)
    if updates:
        _save_json(OFFSET_FILE, {"offset": updates[-1]["update_id"] + 1})
    return updates


def _hours_since(iso_timestamp: str) -> float:
    then = datetime.fromisoformat(iso_timestamp)
    return (datetime.now(timezone.utc) - then).total_seconds() / 3600


def _load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run()
