"""
TAM OTOMATIK mod (Telegram secimi OLMADAN, tek adim).
Telegram'dan konu secmek istiyorsan bunun yerine suggest_topics.py +
check_and_produce.py ikilisini kullan (bkz. README).
"""
from generate_script import generate_daily_content
from pipeline import produce_and_upload


def run() -> None:
    print("Konu ve script uretiliyor...")
    content = generate_daily_content()
    print(f"Konu: {content['topic']}")
    produce_and_upload(content)


if __name__ == "__main__":
    run()
