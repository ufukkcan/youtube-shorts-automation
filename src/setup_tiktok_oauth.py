"""
BU BETIGI SADECE BIR KEZ, KENDI BILGISAYARINDA calistir.
Amaci: TikTok hesabina video yukleme izni veren bir "refresh token" uretmek.

Kullanim:
1) https://developers.tiktok.com adresinde bir hesap ac, "Manage apps" > "Create an app"
2) Uygulamana "Content Posting API" urununu ekle (Products sekmesi)
3) Uygulama ayarlarinda "Redirect URI" olarak TAM su degeri ekle:
   http://localhost:8912/callback
4) Uygulamanin "Client Key" ve "Client Secret" degerlerini asagidaki
   CLIENT_KEY / CLIENT_SECRET satirlarina yapistir
5) pip install requests (zaten kuruluysa gerek yok)
6) python setup_tiktok_oauth.py calistir
7) Acilan tarayicida kendi TikTok hesabinla giris yap, izin ver
8) Terminalde cikan degerleri GitHub Secrets'a ekle

NOT: Uygulaman TikTok tarafindan henuz "denetlenmemis" (unaudited) durumdaysa,
sadece TikTok Geliştirici Portali'nda "Target Users" olarak eklenen hesaplar
bu akisi tamamlayabilir -- kendi hesabini oraya eklemen gerekebilir.
"""
import http.server
import urllib.parse
import webbrowser

import requests

CLIENT_KEY = "BURAYA_CLIENT_KEY_YAPISTIR"
CLIENT_SECRET = "BURAYA_CLIENT_SECRET_YAPISTIR"
REDIRECT_URI = "http://localhost:8912/callback"
SCOPE = "video.publish"
PORT = 8912

received_code: dict = {}


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if "code" in params:
            received_code["code"] = params["code"][0]
            self.wfile.write("Basarili! Bu sekmeyi kapatabilirsin, terminale don.".encode("utf-8"))
        else:
            self.wfile.write("Kod bulunamadi, izin verilmemis olabilir.".encode("utf-8"))

    def log_message(self, format, *args) -> None:  # noqa: A002 - http.server imzasi boyle
        pass  # konsolu kirletmesin


def main() -> None:
    if "BURAYA" in CLIENT_KEY or "BURAYA" in CLIENT_SECRET:
        print("Once bu dosyanin icindeki CLIENT_KEY ve CLIENT_SECRET degerlerini doldur!")
        return

    auth_url = (
        "https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={CLIENT_KEY}&scope={SCOPE}&response_type=code"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}&state=setup"
    )
    print("Tarayici aciliyor, TikTok hesabinla giris yapip izin ver...")
    print("Acilmazsa bu linki elle ac:", auth_url)
    webbrowser.open(auth_url)

    server = http.server.HTTPServer(("localhost", PORT), CallbackHandler)
    while "code" not in received_code:
        server.handle_request()

    resp = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "code": received_code["code"],
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()

    if "refresh_token" not in data:
        print("Beklenmeyen yanit, TikTok'tan gelen tam cevap:")
        print(data)
        return

    print("\n--- Bu degerleri GitHub Secrets'a ekle ---")
    print(f"TIKTOK_CLIENT_KEY={CLIENT_KEY}")
    print(f"TIKTOK_CLIENT_SECRET={CLIENT_SECRET}")
    print(f"TIKTOK_REFRESH_TOKEN={data['refresh_token']}")


if __name__ == "__main__":
    main()
