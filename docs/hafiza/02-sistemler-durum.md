# 02 — Sistemler, makineler ve güncel durumları

> Durum değiştikçe ilgili satırı güncelle ve "Son kontrol" tarihini değiştir. Değişikliği `islem-gunlugu.md`'ye de yaz.
> Durum kodları: 🟢 çalışıyor · 🟡 çalışıyor ama risk/eksik var · 🔴 çalışmıyor · ⚪ kullanılmıyor/kapsam dışı · ❔ doğrulanmadı

## Özet tablo

| # | Sistem / makine | Rol | Durum | Son kontrol | Kanıt / not |
|---|---|---|---|---|---|
| S1 | Yerel iş istasyonu (Windows 11 Pro 10.0.26200, kullanıcı `mc061965`) | Geliştirme, dokümantasyon, okuma amaçlı kontroller | 🟡 | 2026-11-22 | Python 3.12 (`C:\Users\mc061965\AppData\Local\Programs\Python\Python312\python.exe`), git 2.55.0.windows.5, PowerShell 5.1.26100. **Yok:** ffmpeg, gh CLI. Git Bash araçta fork hatası veriyor. Desktop Commander MCP bağlanamadı. |
| S2 | Yerel git klonu | Kod kopyası | 🟢 | 2026-11-22 | `main`, pull (521ee6b) + TikTok silme ve doküman commit'i push edildi. Bot sürekli state push ettiği için çalışmaya başlamadan önce her seferinde `git fetch` gerekir. |
| S3 | GitHub repo `ufukkcan/youtube-shorts-automation` | Kod + state deposu | 🟡 | 2026-11-22 | **public**, default `main`, oluşturma 2026-08-04, son push 2026-11-22 15:35 UTC. 320 commit (253 `shorts-bot`, 67 `ufukkcan`). Geçmişte açık secret (`45370f4`). |
| S4 | GitHub Actions — `check_and_produce.yml` (id 327244759) | Ana motor | 🟢 | 2026-11-22 | active. 1261 run (2026-08-04→11-22), 30 failure, 21 cancelled, 0 timed_out. Son failure 2026-11-14 19:40 UTC. Ortalama ≈11 run/gün. |
| S5 | GitHub Actions — `suggest_topics.yml` (327244760) | Elle yedek tetik | ⚪ | 2026-11-22 | active, 0 run. |
| S6 | GitHub Actions — `yt_oauth_exchange.yml` (345399290) | YT token alma | 🟡 | 2026-11-22 | 1 run: 33261095531 (2026-08-29 15:45 UTC, success). Token'ı loga basar. |
| S7 | GitHub Actions — `tiktok_*` (331923124, 334261448, 334290580) | TikTok kalıntısı | ⚪ | 2026-11-22 | Workflow dosyaları silindi (2026-11-22). Eski run'lar/loglar GitHub'da duruyor; log temizliği todo Faz 7. |
| S8 | GitHub Pages `ufukkcan.github.io/tiktok-legal-pages` (repo `ufukkcan/tiktok-legal-pages`, public, Pages açık) | OAuth redirect `callback.html` | 🟢❔ | 2026-11-22 | YouTube OAuth redirect URI'si bunu kullanıyor → **silinmemeli**. Sayfa içeriği bu oturumda okunmadı. |
| S9 | Telegram botu | Kontrol paneli (seçim/onay) | 🟢 | 2026-11-22 | Bot adı/kullanıcı adı ve chat id secret'ta, dokümanda yok (❔ kullanıcıya sor). Son update offset 210548018; offset en son 2026-10-18 16:24 UTC değişti. |
| S10 | Anthropic API | Konu/script üretimi | 🟢 | 2026-11-22 | Model `claude-sonnet-4-6`, SDK 0.40.0. Son başarılı çağrı: döngü 20261122-1535 (pending oluştu). |
| S11 | Pexels API | Stok dikey video | 🟢 | 2026-11-22 | Son başarılı üretim 2026-11-22 (döngü 20261119-1332 done). |
| S12 | Microsoft Edge TTS (edge-tts 7.3.1) | Seslendirme | 🟢 | 2026-11-22 | 2026-10-15'ten beri sorun yok. Kırılma geçmişi: L5. |
| S13 | faster-whisper (small, Actions'ta indirilir) | Altyazı | 🟢 | 2026-11-22 | — |
| S14 | YouTube Data API v3 / Google Cloud OAuth client | Yükleme | 🟢❔ | 2026-11-22 | Son başarılı `videos.insert`: 2026-11-22 07:31 UTC civarı. Proje adı, consent screen durumu, API audit durumu, kota ❔. |
| S15 | YouTube kanalı ("interesthings") | Yayın | ❔ | — | Videoların public olup olmadığı, kanal id'si doğrulanmadı (YouTube Studio'dan bakılmalı). |
| S16 | TikTok Developer uygulaması | — | ⚪🔴 | 2026-11-22 | Kapsam dışı. Client secret public geçmişte → uygulama silinmeli / secret yenilenmeli. |

## Anlık bot durumu (güncelle)

| Alan | Değer | Kaynak |
|---|---|---|
| Aktif batch | `20261122-1535` | `git show origin/main:state/pending_topics.json` |
| Status | `pending` (5 konu Telegram'da) | aynı |
| created_at | 2026-11-22 15:35 UTC (18:35 İstanbul) | aynı |
| Fallback ile otomatik konu seçimi beklenen en erken | 2026-11-23 11:35 UTC + yoklama gecikmesi | created_at + 20 saat |
| Son done | `20261119-1332` "The Zip Code That Does Not Exist — 00000", 2026-11-22 07:31 UTC | state geçmişi |
| Son error | `20261112-2021` (Baader-Meinhof), 2026-11-14 19:44 UTC, run 43633352748, adım "Secimi kontrol et, varsa uret ve yukle" | API |
| topics_used | 300 (tavan) | state |

## Bilinmeyenler (kullanıcıya sorulacak / kullanıcının bakacağı)
1. Telegram bot kullanıcı adı.
2. YouTube kanal id'si/URL'si ve yüklenen 39 videonun görünürlüğü (Public / Scheduled / Private-locked).
3. Google Cloud proje adı, OAuth consent screen durumu (Testing / In production), API audit durumu, günlük kota.
4. Anthropic hesabının bütçe/limit ayarı.
5. Actions log saklama süresi ayarı (varsayılan 90 gün).
