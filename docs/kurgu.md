# Proje Kurgusu — youtube-shorts-automation ("interesthings")

> Bu belge projeyi baştan sona anlatır. Okuyan kişi başka kaynağa bakmadan sistemin ne olduğunu, nasıl çalıştığını, nasıl kurulduğunu, nasıl kullanıldığını ve nereye bağlandığını anlayabilmelidir.
> Son doğrulama: 2026-11-22 (kod: `0d34b2c` / remote `521ee6b`). Kapsam: **yalnızca YouTube**. TikTok kapsam dışıdır (karar: 2026-11-22, bkz. [hafiza/kararlar.md](hafiza/kararlar.md)).

---

## 1. Ne yapar?

İngilizce "ilginç bilgi / şaşırtıcı gerçek" temalı **YouTube Shorts** videolarını uçtan uca otomatik üretir ve yükler:

1. Claude (Anthropic API) ile 5 aday konu + her biri için seslendirme metni (script), başlık, açıklama, 10 hashtag adayı ve Pexels arama kelimeleri üretir.
2. Adayları **Telegram botu** üzerinden kanal sahibine sunar; sahibi bir konu seçer.
3. Seçilen konu için 10 hashtag adayı sunar; sahibi 5 tanesini seçer.
4. Videoyu üretir: edge-tts seslendirme → Pexels dikey stok klipler → faster-whisper altyazı → ffmpeg montaj (1080x1920, altyazı yakma, "SUBSCRIBE" buton animasyonu, kapanış CTA metni).
5. Videoyu Telegram'a **onaya** gönderir ("Onayla, yayinla" / "Begenmedim, tekrar uret").
6. Onaylanırsa videoyu (yeniden üretip) **YouTube'a private + zamanlanmış yayın** (`publishAt`) olarak yükler; YouTube videoyu her gün **20:00 İstanbul** saatinde herkese açar.
7. Sahibi hiç yanıt vermezse her adım **20 saat** sonra kendiliğinden ilerler (otopilot).

Her şey **GitHub Actions** üzerinde çalışır; kişisel bilgisayarın açık olması gerekmez.

## 2. Ne işe yarar? (amaç)

- Kanal sahibinin günde birkaç dokunuşla (konu seç → hashtag seç → onayla) düzenli Shorts yayınlaması.
- Hiç dokunulmasa bile yayın akışının durmaması (fallback).
- Neredeyse sıfır maliyet: ücretli tek bileşen Claude API çağrısıdır (döngü başına 1 çağrı). Diğerleri (Telegram, edge-tts, Pexels, faster-whisper, GitHub Actions public repo, YouTube Data API) ücretsizdir.

## 3. Mimari

```
                 ┌────────────────────────── GitHub (public repo: ufukkcan/youtube-shorts-automation) ─────────────────────────┐
                 │                                                                                                              │
  cron (5 dk)    │  .github/workflows/check_and_produce.yml  (ubuntu-latest, Python 3.12, ffmpeg, fonts-dejavu-core)           │
  ─────────────► │     └─ python src/check_and_produce.py   ◄── state/*.json (repo içinde, her çalışmada commit+push)           │
                 │            │                                                                                                 │
                 └────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────┘
                              │
     ┌────────────────────────┼───────────────────────────────┬───────────────────────┬──────────────────────┐
     ▼                        ▼                               ▼                       ▼                      ▼
 Telegram Bot API        Anthropic API                   Pexels API            Microsoft Edge TTS       YouTube Data API v3
 (getUpdates/send*)      (claude-sonnet-4-6)             (videos/search)       (edge-tts paketi)        (videos.insert, OAuth refresh token)
  ▲   kanal sahibi
  └── Telegram istemcisi
```

**Durum (state) yönetimi:** Sunucu/veritabanı yok. Tüm kalıcı durum repo içindeki `state/` klasöründeki JSON dosyalarıdır; her Actions çalışmasının son adımı bunları `shorts-bot` kimliğiyle commit edip push eder (`State guncellendi (secim/uretim)` commit'leri bunlardır).

**Tetikleme modeli:** Sürekli çalışan bir süreç yok. Workflow 5 dakikada bir planlanmıştır (`2,7,12,...,57 * * * *`) ve her çalışmada Telegram'dan yeni güncellemeleri **short-poll** ile çeker, duruma göre bir adım ilerletir, biter. `concurrency: check-and-produce` ile aynı anda tek çalışma olur.

> **Ölçülen gerçek:** GitHub zamanlanmış çalışmaların çoğunu düşürüyor. 2026-08-04 → 2026-11-22 arasında 1261 çalışma var (≈11/gün, beklenen 288/gün). Yani gerçek yoklama aralığı ortalama ≈2 saattir. Telegram tıklamalarına tepki saatler sürebilir. (Kaynak: GitHub API, 2026-11-22.)

## 4. Durum makinesi (state machine)

`state/pending_topics.json` içindeki `status` alanı:

```
             "video uret" (her durumda, force reset)                         AUTO_TRIGGER_TIME (16:30 İst.) ve
        ┌──────────────────────────────────────────────┐                     bugün döngü başlamamış ya da son durum "error"
        │                                              ▼                                     │
   (yok/done/error) ──────────────────────────────► pending ◄──────────────────────────────────┘
                                                      │  konu seçildi  /  20 saat → 1. konu otomatik
                                                      ▼
                                             selecting_hashtags
                                                      │  5 hashtag seçildi  /  20 saat → eksikler sırayla tamamlanır
                                                      │  (video üretilir, Telegram'a onaya gönderilir)
                                                      ▼
                                   ┌──────────── reviewing ◄─────────┐
                                   │                 │                │ "tekrar uret" (attempts < 5) → yeniden üret
                                   │                 └────────────────┘
                                   │ "onayla" / 20 saat timeout / 5. redo'da otomatik onay
                                   ▼
                        video yeniden üretilir → YouTube'a yüklenir → done
   Herhangi bir üretim/yükleme istisnası → error (Telegram'a hata mesajı, workflow "failure")
```

Kurallar (kod: [src/check_and_produce.py](../src/check_and_produce.py)):
- `video uret` / `video üret` / `uret` / `üret` / `/uret` / `/video` / `/generate` mesajı **her zaman** mevcut durumu sıfırlar ve yeni 5 konu üretir (`suggest_topics.run(force=True)`), aktif döngü olsa bile.
- Otomatik tetikleme günde 1 kez: `trigger_date == bugün` ise tekrar başlamaz; ancak son durum `error` ise aynı gün yeniden başlar.
- `FALLBACK_HOURS=20` her aşama için ayrı sayılır (`created_at`, `hashtag_started_at`, `review_started_at`). Hiç dokunulmazsa bir döngü ≈3×20 saat + yoklama gecikmesi ≈ **2,5–3 gün** sürer. Bu yüzden otopilotta yayın sıklığı ≈ 3 günde 1 videodur (ölçülen, bkz. [hafiza/uretim-gecmisi.md](hafiza/uretim-gecmisi.md)).
- Onaylanan video Telegram'dan geri indirilmez (Bot API `getFile` indirme sınırı 20 MB); aynı içerikle **yeniden üretilip** yüklenir. Seslendirme/altyazı aynı olur, Pexels sonuçları değişirse klipler farklı olabilir.

### 4.1 `state/pending_topics.json` şeması

| Alan | Ne zaman yazılır | Açıklama |
|---|---|---|
| `batch_id` | pending | UTC `YYYYMMDD-HHMM`; Telegram callback'lerinde anahtar |
| `trigger_date` | pending | İstanbul tarihi `YYYY-MM-DD`; günde-1-otomatik kuralı |
| `message_id` | pending, reviewing | Konu mesajı id'si; reviewing'de video mesajı id'si ile ezilir |
| `created_at` | pending | UTC ISO; konu seçimi fallback başlangıcı |
| `status` | her adım | `pending` / `selecting_hashtags` / `reviewing` / `done` / `error` (geçmişte TikTok döneminde `approved_pending_publish` de vardı) |
| `candidates` | pending | 5 aday (şema 4.2) |
| `candidate` | selecting_hashtags | Seçilen aday (hashtag sonrası `video_description` ezilir) |
| `hashtag_options` | selecting_hashtags | Temizlenmiş ≤10 hashtag |
| `hashtag_message_id` | selecting_hashtags | Hashtag mesajı id'si |
| `selected_hashtags` | selecting_hashtags | Seçilen indeksler |
| `hashtag_started_at` | selecting_hashtags | UTC ISO |
| `video_file_id` | reviewing | Telegram file_id (kullanılmıyor, bilgi amaçlı) |
| `review_started_at` | reviewing | UTC ISO |
| `attempts` | reviewing | Üretim deneme sayısı (1'den başlar) |

> Eksik: YouTube `video_id` state'e **yazılmıyor**; sadece Telegram'a "Video yayinlandi: https://youtube.com/shorts/<id>" mesajı gider. (todo'da)

### 4.2 Aday (candidate) şeması — Claude çıktısı

`topic` (dahili başlık), `teaser` (Telegram'da gösterilen 1 cümle), `video_title` (<60 karakter), `video_description` (yedek; hashtag seçiminden sonra `topic + "\n\n" + #h1 … #h5` ile ezilir), `tags` (tam 10: 6–7 konuya özel + 3–4 jenerik: shorts, viral, trending, facts, didyouknow), `script` (65–85 kelime, tek paragraf, şok edici kanca ile başlar), `visual_keywords` (3–5 İngilizce Pexels arama ifadesi).

### 4.3 Diğer state dosyaları

- `state/topics_used.json` → `{"topics": [...]}`; gösterilen tüm aday başlıkları (seçilmese de) eklenir, son **300** tutulur, Claude'a son **60** tanesi "tekrar etme" diye verilir.
- `state/telegram_offset.json` → `{"offset": N}`; bir sonraki `getUpdates` offset'i. Güncellemeler **işlenmeden önce** kaydedilir.

## 5. Üretim hattı (bir video nasıl yapılır)

| Adım | Dosya | Teknoloji | Ayrıntı |
|---|---|---|---|
| 1/4 Seslendirme | [src/generate_voice.py](../src/generate_voice.py) | edge-tts 7.3.1 | Ses `TTS_VOICE=en-US-AriaNeural`, hız `TTS_RATE=+5%`; süre `ffprobe` ile ölçülür |
| 2/4 Görseller | [src/fetch_visuals.py](../src/fetch_visuals.py) | Pexels Videos API | Her anahtar kelime için `orientation=portrait`, ilk dikey dosyanın en genişi; toplam süre ses süresini geçene kadar (kelimeler en fazla 3 tur) |
| 3/4 Altyazı | [src/generate_captions.py](../src/generate_captions.py) | faster-whisper 1.0.3, model `small`, CPU int8 | Kelime zaman damgalı, 3 kelimelik SRT parçaları |
| 4/4 Montaj | [src/assemble_video.py](../src/assemble_video.py) | ffmpeg (libx264, aac, libass) | Klipler 1080x1920/30fps normalize → concat → altyazı yak (Arial 16, MarginV=170) → 1,2 sn'de `follow_button.png` pop-in (260 px) + `tap_ring.png` dokunma halkası → son 3 sn "SUBSCRIBE" kutulu metin → bitrate hedefi 30 MB (700–5000 kbps), ses 128 kbps |
| Yükleme | [src/pipeline.py](../src/pipeline.py) → [src/upload_youtube.py](../src/upload_youtube.py) | google-api-python-client | Açıklamaya `#Shorts` yoksa eklenir; `categoryId=24`, `selfDeclaredMadeForKids=false`, `privacyStatus=private` + `publishAt=sonraki 20:00 İst. (UTC)`; resumable upload |

## 6. Kullanılan teknolojiler

| Alan | Teknoloji / sürüm |
|---|---|
| Dil | Python 3.12 (Actions `setup-python@v5`) |
| Çalışma ortamı | GitHub Actions `ubuntu-latest`, apt: `ffmpeg`, `fonts-dejavu-core`; pip cache + apt cache |
| LLM | Anthropic Python SDK `anthropic==0.40.0`, model `claude-sonnet-4-6`, `max_tokens=4000` |
| TTS | `edge-tts==7.3.1` (Microsoft Edge okuma servisi, anahtar gerektirmez) |
| Stok video | Pexels Videos API (`requests==2.32.3`) |
| ASR / altyazı | `faster-whisper==1.0.3` (ilk çalıştırmada model indirir) |
| Video | ffmpeg (concat demuxer, subtitles/libass, drawtext, overlay, scale eval=frame) |
| YouTube | `google-api-python-client==2.149.0`, `google-auth==2.35.0`, `google-auth-oauthlib==1.2.1` (yalnız yerel token kurulumu için) |
| Mesajlaşma | Telegram Bot API (doğrudan HTTP, kütüphane yok) |
| Durum | Repo içi JSON + git commit/push |

## 7. Entegrasyonlar ve nasıl bağlanır

Secret değerleri hiçbir dosyada yazılmaz. Hepsi **GitHub → repo → Settings → Secrets and variables → Actions** altında saklanır. Ayrıntılı liste: [hafiza/03-entegrasyonlar-kimlik.md](hafiza/03-entegrasyonlar-kimlik.md).

### 7.1 Telegram
1. Telegram'da `@BotFather` → `/newbot` → bot token → secret `TELEGRAM_BOT_TOKEN`.
2. Bota herhangi bir mesaj at; tarayıcıda `https://api.telegram.org/bot<TOKEN>/getUpdates` → `chat.id` → secret `TELEGRAM_CHAT_ID`.
3. Bot yalnızca bu chat id'den gelen mesaj/tıklamaları işler. Webhook **kurulmamalı** (getUpdates ile çakışır).
4. Sınırlar: `sendVideo` 50 MB; `getFile` indirme 20 MB; Telegram onaylanmamış update'leri en fazla 24 saat tutar.

### 7.2 Anthropic (Claude)
- https://console.anthropic.com/settings/keys → secret `ANTHROPIC_API_KEY`. Döngü başına 1 çağrı (`generate_script._call_claude`).

### 7.3 Pexels
- https://www.pexels.com/api/ → secret `PEXELS_API_KEY`. `Authorization: <key>` başlığı ile `https://api.pexels.com/videos/search`.

### 7.4 YouTube Data API v3 (OAuth)
1. Google Cloud Console → proje → **YouTube Data API v3** etkin → OAuth consent screen → OAuth client ID.
2. Refresh token alma — iki yol var:
   - **Yerel:** client tipi *Desktop app*, `client_secret.json`'ı repo köküne koy (gitignore'da), `pip install google-auth-oauthlib`, `python setup_oauth.py` → çıktıdaki `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
   - **Actions üzerinden (2026-08-29'da kullanıldı):** client'ın redirect URI'si `https://ufukkcan.github.io/tiktok-legal-pages/callback.html` olmalı; tarayıcıda yetkilendirme linkini aç, callback sayfasındaki `code`'u kopyala, Actions → *YouTube OAuth code exchange* → Run workflow → `code`. Script refresh token'ı **loga basar** (güvenlik riski, bkz. lessons L15) → secret `YT_REFRESH_TOKEN`.
3. Scope: `https://www.googleapis.com/auth/youtube.upload`.
4. Dikkat: Google, denetlenmemiş (unverified) API projelerinden `videos.insert` ile yüklenen videoları *private*'a kilitleyebilir; videoların gerçekten yayına girdiği YouTube Studio'dan doğrulanmalı (todo: doğrulanmadı). Consent screen "Testing" modundaysa refresh token 7 günde düşer (bu projede 08-29'dan beri düşmediği için muhtemelen "In production"; doğrulanmadı).
5. Kota: `videos.insert` yüksek maliyetlidir; güncel birim maliyeti ve günlük kota Google Cloud Console → APIs → YouTube Data API v3 → Quotas'tan doğrulanmalı.

### 7.5 GitHub
- Repo: `https://github.com/ufukkcan/youtube-shorts-automation` (**public**, default branch `main`, oluşturma 2026-08-04).
- Workflow'un state push edebilmesi için varsayılan `GITHUB_TOKEN` yazma izni gerekir (çalışıyor: bot 253 commit atmış).
- Public repo olduğu için Actions dakikaları ücretsiz; ancak **commit geçmişi ve Actions logları herkese açıktır** (bkz. lessons L14–L15).

### 7.6 GitHub Pages (OAuth callback)
- `https://ufukkcan.github.io/tiktok-legal-pages/callback.html` — ayrı public repo `ufukkcan/tiktok-legal-pages` (Pages açık). Adı TikTok olsa da **YouTube OAuth redirect URI'si de burayı kullanıyor**; TikTok temizliğinde bu repo silinmemelidir.

## 8. Workflow'lar

| Dosya | Tetik | Görev | Durum |
|---|---|---|---|
| `check_and_produce.yml` | cron `2,7,12,...,57 * * * *` + elle | Ana motor (tek iş: kur → `check_and_produce.py` → state commit/push, `if: always()`) | Aktif, çalışıyor |
| `suggest_topics.yml` | Sadece elle | 5 konuyu zorla üret (yedek). Hiç çalıştırılmadı (0 run). Not: bunun yerine Telegram'dan "video uret" yeterli | Aktif, kullanılmıyor |
| `yt_oauth_exchange.yml` | Elle (`code` girdisi) | YouTube auth code → refresh token (loga basar) | 1 run (2026-08-29) |
| ~~`tiktok_*.yml` (3 adet)~~ | — | TikTok denemesi kalıntısı | 2026-11-22'de silindi (eski run kayıtları GitHub'da duruyor) |

## 9. Yapılandırma (check_and_produce.yml `env`)

| Değişken | Mevcut değer | Kod varsayılanı | Anlamı |
|---|---|---|---|
| `PRIVACY_STATUS` | `public` | `public` | `PUBLISH_TIME_ISTANBUL=off` ise kullanılan görünürlük |
| `CONTENT_LANGUAGE` | `en` | `en` | İçerik dili (`tr` mümkün); whisper dili de bu |
| `TTS_VOICE` | `en-US-AriaNeural` | aynı | edge-tts sesi |
| `TTS_RATE` | (yok) | `+5%` | Konuşma hızı |
| `AUTO_TRIGGER_TIME` | `16:30` | `20:00` | Manuel tetik yoksa döngünün başlayacağı İstanbul saati (string karşılaştırma `HH:MM`) |
| `PUBLISH_TIME_ISTANBUL` | `20:00` | `20:00` | YouTube `publishAt` saati; `off` = hemen yayın |
| `FALLBACK_HOURS` | `20` | `20` | Yanıtsız adımın otomatik ilerleme süresi; `0` = kapalı |
| `MAX_REDO_ATTEMPTS` | `5` | `5` | Bu sayıya ulaşan "tekrar uret" otomatik onaya döner |

Kod içi sabitler: `N_CANDIDATES=5`, `N_HASHTAGS_TO_PICK=5`, hashtag adayı ≤10, `topics_used` 300/60, video `TARGET_MAX_MB=30`, whisper `small`, `WORDS_PER_CHUNK=3`.

## 10. Nasıl kullanılır (günlük)

Telegram'da bot ile:
1. İstersen **`video uret`** yaz (ya da `/uret`, `/video`, `/generate`). Yazmazsan 16:30 İstanbul'dan sonraki ilk çalışmada kendiliğinden başlar.
2. Gelen 5 teaser'dan birinin numarasına bas.
3. Gelen 10 hashtag'ten 5'ine bas (tekrar basmak seçimi kaldırır; 5'e ulaşınca üretim başlar).
4. Video gelince **Onayla, yayinla** ya da **Begenmedim, tekrar uret**.
5. Onaydan sonra "Video yayinlandi: https://youtube.com/shorts/<id>" mesajı gelir; video YouTube'da 20:00 İstanbul'da açılır.

Beklentiler: Her tıklamanın işlenmesi bir sonraki Actions çalışmasını bekler (ölçülen ortalama ≈2 saat, bazen daha uzun). Bot tıklamaya Telegram'da anında "secildi" yanıtı veremez; yanıt işlendiğinde gelir.

Takılırsa: `video uret` yazmak her durumu sıfırlar. State dosyasını elle silmek gerekmez.

## 11. Yerel çalıştırma / test

Bu iş istasyonunda ffmpeg yok (2026-11-22). Tam yerel test için ffmpeg + Python 3.12 + `pip install -r requirements.txt` gerekir. Ortam değişkenleri PowerShell'de `$env:ANTHROPIC_API_KEY="..."` şeklinde verilir (değerler dosyaya yazılmaz). `src` içinden:
- `python generate_script.py` → 5 aday JSON (state/topics_used.json'a yazar!)
- `python generate_voice.py "metin" voice.mp3`
- `python fetch_visuals.py "ocean,ship" 30`
- `python generate_captions.py voice.mp3 out.srt en`
- `python assemble_video.py clip1.mp4,clip2.mp4 voice.mp3 out.srt final.mp4 30`
- `python main.py` → **onaysız tam otomatik üret+yükle** (dikkat: gerçek YouTube'a yükler).

Yerel testler `state/` dosyalarını değiştirir; canlı bot ile çakışmaması için commit etmeden geri al (`git checkout -- state/`).

## 12. Sınırlar ve bilinen riskler (özet)

- GitHub cron güvenilmez (≈11 çalışma/gün).
- Otopilotta ≈3 günde 1 video; 2026-10-18'den beri bota hiç etkileşim gelmemiş (Telegram offset değişmedi).
- Tekrarlayan konular (ör. Cleopatra's Needle 5 kez, Baader-Meinhof 3 kez aday olarak seçildi).
- Onaylanan video ile yüklenen video birebir aynı olmayabilir (yeniden üretim).
- YouTube video id'si saklanmıyor; yayın doğrulaması yok.
- Güvenlik: public repo geçmişinde TikTok client secret (`45370f4`), Actions loglarında OAuth refresh token çıktıları.
Ayrıntı ve çözümler: [lessons.md](lessons.md), [../todo.md](../todo.md).
