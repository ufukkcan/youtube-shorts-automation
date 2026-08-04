"""
Yeni bir gunluk uretim dongusu baslatir: 5 aday konu uretir, Telegram'a gonderir,
kullanicinin secimini bekleyecek sekilde state/pending_topics.json'a kaydeder.
Secim/onay islemlerini check_and_produce.py yapar.

Bu dosya artik KENDI cron'uyla degil, check_and_produce.py'nin her 10 dakikada
bir calisan dongusu tarafindan (manuel tetikleme veya otomatik saat gelince)
cagrilir -- run() ayni gun icinde birden fazla kez cagrilsa bile GUVENLIDIR,
"trigger_date" alani sayesinde bugun icin zaten baslatilmissa hicbir sey yapmaz.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from generate_script import generate_topic_candidates
from telegram_bot import send_topic_options

PENDING_FILE = Path(__file__).resolve().parent.parent / "state" / "pending_topics.json"
N_CANDIDATES = 5
ISTANBUL = ZoneInfo("Europe/Istanbul")


def run() -> None:
    existing = _load_pending()
    today = datetime.now(ISTANBUL).date().isoformat()

    if existing and existing.get("trigger_date") == today:
        print(f"Bugun ({today}) icin zaten bir dongu baslatilmis, atlaniyor:", existing["batch_id"])
        return

    candidates = generate_topic_candidates(n=N_CANDIDATES)
    batch_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")

    message_id = send_topic_options(candidates, batch_id)

    PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
    PENDING_FILE.write_text(
        json.dumps(
            {
                "batch_id": batch_id,
                "trigger_date": today,
                "message_id": message_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "pending",
                "candidates": candidates,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"5 konu Telegram'a gonderildi. batch_id={batch_id}")


def _load_pending() -> dict | None:
    if PENDING_FILE.exists():
        return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    return None


if __name__ == "__main__":
    run()
