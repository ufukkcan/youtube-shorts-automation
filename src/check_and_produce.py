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
