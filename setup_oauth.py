"""
BU BETIGI SADECE BIR KEZ, KENDI BILGISAYARINDA calistir.
Amaci: YouTube kanalina yukleme izni veren bir "refresh token" uretmek.
Bu islem senin kendi Google hesabinla tarayicida giris yapmani gerektirir,
bu yuzden Claude bunu senin adina yapamaz.

Kullanim:
1) https://console.cloud.google.com adresinde bir proje olustur
2) "YouTube Data API v3"u etkinlestir
3) "OAuth client ID" olustur (Application type: Desktop app)
4) Indirdigin client_secret.json dosyasini bu klasore koy
5) pip install google-auth-oauthlib
6) python setup_oauth.py
7) Tarayici acilacak, kendi YouTube kanalinin baglantili oldugu hesapla giris yap
8) Terminalde cikan CLIENT_ID / CLIENT_SECRET / REFRESH_TOKEN degerlerini
   GitHub reponun Settings > Secrets and variables > Actions kismina ekle
"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    credentials = flow.run_local_server(port=0)

    print("\n--- Bu degerleri GitHub Secrets'a ekle ---")
    print(f"YT_CLIENT_ID={credentials.client_id}")
    print(f"YT_CLIENT_SECRET={credentials.client_secret}")
    print(f"YT_REFRESH_TOKEN={credentials.refresh_token}")


if __name__ == "__main__":
    main()
