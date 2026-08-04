"""
Sik araliklarla calisir (cron, or. her 5-10 dakikada bir). DORT asamali surec:

  asama 0 "aktif dongu yok" -> Telegram'a "video uret" yazildi mi, ya da
                         AUTO_TRIGGER_TIME saatine gelindi mi? Ikisinden biri
                         olduysa yeni bir 5-konu dongusu baslatir.
  asama 1 "pending"            -> Telegram'da 5 konudan biri secildi mi?
                         Secildiyse konuyla ilgili 10 hashtag onerisi gonderir
                         -> durum "selecting_hashtags" olur.
  asama 2 "selecting_hashtags" -> Kullanici 5 hashtag secti mi? Secildiyse
                         videoyu URETIR (henuz YUKLEMEZ) ve onaya Telegram'a
                         gonderir -> durum "reviewing" olur.
  asama 3 "reviewing"          -> Kullanici "Onayla" dedi mi, "Tekrar uret" mi
                         dedi? Onayladiysa videoyu YENIDEN URETIP YouTube'a
                         yukler -> durum "done" (Telegram'in getFile ile dosya
                         indirme siniri 20MB oldugu icin -- shorts videolarimiz
                         genelde bunu astigindan -- oradan geri indirmek yerine
                         ayni icerikle tekrar uretip yuklemek daha guvenilir).
                         Begenmediyse videoyu YENIDEN URETIR, tekrar onaya
                         sunar -> "reviewing" durumunda kalir (dongu).

Kullanici hic yanit vermezse FALLBACK_HOURS sonra ilgili adim otomatik
ilerletilir, boylece gunluk yayin sonsuza kadar beklemede kalmaz.
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
    edit_message,
    find_hashtag_toggles,
    find_manual_trigger,
    find_review_decision,
    find_selection,
    get_updates,
    send_hashtag_options,
    send_message,
    send_video_for_review,
    update_hashtag_message,
)

PENDING_FILE = Path(__file__).resolve().parent.parent / "state" / "pending_topics.json"
OFFSET_FILE = Path(__file__).resolve().parent.parent / "state" / "telegram_offset.json"
FALLBACK_HOURS = float(os.environ.get("FALLBACK_HOURS", "20"))
MAX_REDO_ATTEMPTS = int(os.environ.get("MAX_REDO_ATTEMPTS", "5"))
N_HASHTAGS_TO_PICK = 5
# Manuel "video uret" gelmezse gunun dongusu bu Istanbul saatinde kendiliginden baslar.
AUTO_TRIGGER_TIME = os.environ.get("AUTO_TRIGGER_TIME", "20:00")
ISTANBUL = ZoneInfo("Europe/Istanbul")


def run() -> None:
    updates = _fetch_updates()
    pending = _load_json(PENDING_FILE)
    today = datetime.now(ISTANBUL).date().isoformat()

    active_cycle = bool(pending) and pending.get("status") in ("pending", "selecting_hashtags", "reviewing")

    if active_cycle:
        status = pending["status"]
        if status == "pending":
            _handle_topic_selection(pending, updates)
        elif status == "selecting_hashtags":
            _handle_hashtag_selection(pending, updates)
        else:
            _handle_review_decision(pending, updates)
        return

    # Su an aktif bir dongu yok (hic olmadi / "done" / "error"). Manuel "video uret"
    # HER ZAMAN yeni bir dongu baslatabilir -- bugun zaten bir video yayinlanmis
    # olsa bile, kullanici acikca isterse ikinci bir video da uretilebilir.
    # Otomatik saat tetiklemesi ise gunde sadece BIR kez calisir (onceki deneme
    # hata vermediyse), boylece kullanici hic dokunmasa bile gun tekrar tekrar
    # tetiklenip durmaz.
    manual = find_manual_trigger(updates)
    started_today = bool(pending) and pending.get("trigger_date") == today
    auto_should_fire = not started_today or pending.get("status") == "error"

    if manual:
        send_message("Alindi! Yeni bir konu listesi hazirlaniyor...")
        print("Manuel tetikleme alindi, yeni dongu baslatiliyor (force).")
        suggest_topics.run(force=True)
    elif auto_should_fire and datetime.now(ISTANBUL).strftime("%H:%M") >= AUTO_TRIGGER_TIME:
        print(f"Otomatik tetikleme saati geldi ({AUTO_TRIGGER_TIME}), yeni dongu baslatiliyor.")
        suggest_topics.run(force=False)
    else:
        print(f"Bugun icin henuz yeni bir tetikleme yok (manuel istek yok, otomatik saat {AUTO_TRIGGER_TIME} henuz gelmedi ya da bugun zaten calisti).")


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

    _start_hashtag_selection(pending, chosen)


def _start_hashtag_selection(pending: dict, chosen: dict) -> None:
    hashtag_options = _clean_hashtag_candidates(chosen.get("tags", []))
    message_id = send_hashtag_options(hashtag_options, pending["batch_id"])

    pending["status"] = "selecting_hashtags"
    pending["candidate"] = chosen
    pending["hashtag_options"] = hashtag_options
    pending["hashtag_message_id"] = message_id
    pending["selected_hashtags"] = []
    pending["hashtag_started_at"] = datetime.now(timezone.utc).isoformat()
    _save_json(PENDING_FILE, pending)


def _clean_hashtag_candidates(tags: list[str]) -> list[str]:
    """Etiketleri hashtag'e uygun (bosluksuz, alfanumerik) hale getirir,
    tekrarlari eler, en fazla 10 tane birakir."""
    cleaned = []
    seen = set()
    for tag in tags:
        word = "".join(ch for ch in str(tag) if ch.isalnum())
        if word and word.lower() not in seen:
            cleaned.append(word)
            seen.add(word.lower())
    return cleaned[:10]


def _handle_hashtag_selection(pending: dict, updates: list[dict]) -> None:
    toggles = find_hashtag_toggles(updates, pending["batch_id"])
    selected = pending.get("selected_hashtags", [])

    for index in toggles:
        if index in selected:
            selected.remove(index)
        else:
            selected.append(index)
        if len(selected) >= N_HASHTAGS_TO_PICK:
            break

    timed_out = (
        len(selected) < N_HASHTAGS_TO_PICK
        and _hours_since(pending["hashtag_started_at"]) >= FALLBACK_HOURS > 0
    )
    if timed_out:
        # yanit gelmedi, eksik kalanlari listeden sirayla tamamla
        for i in range(len(pending["hashtag_options"])):
            if len(selected) >= N_HASHTAGS_TO_PICK:
                break
            if i not in selected:
                selected.append(i)

    pending["selected_hashtags"] = selected

    if len(selected) >= N_HASHTAGS_TO_PICK:
        hashtag_options = pending["hashtag_options"]
        chosen_tags = [hashtag_options[i] for i in selected[:N_HASHTAGS_TO_PICK]]
        chosen = pending["candidate"]
        chosen["video_description"] = chosen["topic"] + "\n\n" + " ".join(f"#{t}" for t in chosen_tags)

        edit_message(
            pending["hashtag_message_id"],
            "Hashtag secimi tamamlandi: " + " ".join(f"#{t}" for t in chosen_tags),
        )

        try:
            _produce_and_send_for_review(pending, chosen, attempt_note="Video uretiliyor...")
        except Exception as exc:
            send_message(f"Video uretiminde hata olustu: {exc}\nTekrar denemek icin 'video uret' yazabilirsin.")
            pending["status"] = "error"
            _save_json(PENDING_FILE, pending)
            raise
    else:
        update_hashtag_message(
            pending["hashtag_message_id"], pending["hashtag_options"], selected, pending["batch_id"]
        )
        _save_json(PENDING_FILE, pending)


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
    """Onaylanan videoyu YUKLER. Not: Telegram Bot API'nin getFile ile dosya
    INDIRME siniri 20MB (gonderme siniri 50MB'dir) -- shorts videolarimiz
    genelde bunu asiyor, bu yuzden Telegram'dan geri indirmek yerine ayni
    icerikle (ayni script + ayni gorsel anahtar kelimeleri) videoyu YENIDEN
    URETIP oyle yukluyoruz. TTS ve Pexels aramasi ayni girdiyle pratikte ayni
    (ya da neredeyse ayni) sonucu verdigi icin bu, kullanicinin onayladigi
    videoyla is farkli olmaz."""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            video_path = produce_video(chosen, Path(tmp))
            video_id = upload_video(video_path, chosen)
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
