# 03 — Entegrasyonlar ve kimlik bilgileri (değer YOK, sadece ad/yer)

> Kural: Secret değeri (token, key, secret, refresh token) hiçbir dosyaya yazılmaz. Burada yalnızca adı, saklandığı yer, kullanan kod, nasıl yenileneceği bulunur.
> Saklama yeri (hepsi): GitHub → `ufukkcan/youtube-shorts-automation` → Settings → Secrets and variables → Actions → Repository secrets.

## Aktif secret'lar (check_and_produce.yml kullanıyor)

| Secret adı | Servis | Kullanan kod | Nasıl alınır / yenilenir | Son değişim |
|---|---|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic | `src/generate_script.py:100` | console.anthropic.com → Settings → API keys | ❔ |
| `PEXELS_API_KEY` | Pexels | `src/fetch_visuals.py:10` | pexels.com/api | ❔ |
| `TELEGRAM_BOT_TOKEN` | Telegram | `src/telegram_bot.py:11` | @BotFather → `/token` (yeniler: `/revoke`) | ❔ |
| `TELEGRAM_CHAT_ID` | Telegram | `src/telegram_bot.py:12` | `https://api.telegram.org/bot<TOKEN>/getUpdates` → `chat.id` (secret değil ama secret'ta tutuluyor) | ❔ |
| `YT_CLIENT_ID` | Google OAuth | `src/upload_youtube.py:16-24`, `yt_oauth_exchange.py` | Google Cloud Console → APIs & Services → Credentials | ❔ |
| `YT_CLIENT_SECRET` | Google OAuth | aynı | aynı | ❔ |
| `YT_REFRESH_TOKEN` | Google OAuth | `src/upload_youtube.py:19` | `python setup_oauth.py` (yerel) ya da Actions "YouTube OAuth code exchange" | 2026-08-29 (run 33261095531 sonrası, korelasyon) |

## Kapsam dışı secret'lar (silinecek)

| Secret adı | Durum |
|---|---|
| `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REFRESH_TOKEN` | tiktok_* workflow'ları 2026-11-22'de silindi; artık hiçbir yerde kullanılmıyor. CLIENT_KEY/SECRET değerleri public commit `45370f4`'te açık. Silinecek + TikTok uygulaması silinecek/secret yenilenecek (onay bekliyor). |

## Kimliksiz/ücretsiz bağımlılıklar
- edge-tts: anahtar yok (Microsoft Edge okuma servisi).
- faster-whisper: anahtar yok (model Hugging Face'ten indirilir).
- GitHub `GITHUB_TOKEN`: otomatik; state push'u bununla. Git kimliği: `shorts-bot <shorts-bot@users.noreply.github.com>`.

## Uç noktalar

| Servis | URL | Not |
|---|---|---|
| Telegram | `https://api.telegram.org/bot<TOKEN>/{getUpdates,sendMessage,editMessageText,answerCallbackQuery,sendVideo,getFile}` | short-poll `timeout=5` |
| Anthropic | SDK (`client.messages.create`) | model `claude-sonnet-4-6`, max_tokens 4000 |
| Pexels | `https://api.pexels.com/videos/search?query=..&orientation=portrait&per_page=5&size=medium` | header `Authorization` |
| Google token | `https://oauth2.googleapis.com/token` | refresh + auth code exchange |
| YouTube | `youtube.videos().insert(part="snippet,status")` | scope `youtube.upload`, categoryId 24 |
| OAuth redirect | `https://ufukkcan.github.io/tiktok-legal-pages/callback.html` | `yt_oauth_exchange.py:13` (Google client'ta kayıtlı olmalı) |
| GitHub API (okuma) | `https://api.github.com/repos/ufukkcan/youtube-shorts-automation/actions/...` | anonim 60 istek/saat |

## Telegram callback_data biçimleri
- Konu: `select:{batch_id}:{0-4}`
- Hashtag: `htag:{batch_id}:{0-9}` (toggle)
- Onay: `review:{batch_id}:approve` / `review:{batch_id}:redo`
- Manuel tetik metinleri: `video uret`, `video üret`, `uret`, `üret`, `/uret`, `/video`, `/generate` (küçük harfe çevrilip tam eşleşme)

## Yetkiler (Claude için)
- Yazma: yalnızca yerel proje klasörü.
- Okuma: git (fetch dahil), GitHub public API, dosyalar.
- Onay gerektirir: push, workflow tetikleme, secret/ayar değişikliği, Telegram'a mesaj, herhangi bir dış servise yazma.
