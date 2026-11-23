# Changelog

> Geçmişe dönük olarak commit diff'leri, state geçmişi ve GitHub Actions API kayıtlarından çıkarıldı (2026-11-22). Saatler: commit'ler yazarın saat diliminde (ufukkcan = +03:00 İstanbul), state/Actions kayıtları UTC.
> Biçim: tarih → ne yapıldı → nasıl çalışıyor → kanıt (commit/run). Secret değerleri yazılmaz.
> Otomatik `State guncellendi (secim/uretim)` commit'leri (253 adet, `shorts-bot`) burada listelenmez; üretim sonuçları için [hafiza/uretim-gecmisi.md](hafiza/uretim-gecmisi.md).

---

## 2026-11-23 — Format v2: kısa video, kanca yazısı, hızlı kurgu, günlük yayın (henüz canlıda değil)
- Neden: Studio 28 gün verisi — ort. izlenme 12 sn (≈%36), 1.841 görüntülemede 0 abone, otopilotta 3 günde 1 video (`data/analiz-2026-11-22-studio-28gun.md`). Hedef: YPP (todo Faz 11).
- `src/generate_script.py`: script 65–85 → **40–55 kelime** (15–20 sn); kanca ≤12 kelime; kapanış soru yerine **döngü** (son cümle ilk cümleye bağlanır).
- `src/pipeline.py`: `_extract_hook` geri geldi; script'in ilk cümlesi montaja `hook_text` olarak gider.
- `src/assemble_video.py`: ilk **2,5 sn kanca yazısı** (DejaVu Bold 64 px, 20 karakterde satır kaydırma, `expansion=none`, y=560 — buton y=170 ve altyazıyla çakışmaz); görüntü **her 2,5 sn'de değişir** (klipler parça parça sırayla, kısa klip `-stream_loop` ile dolar, toplam süre hedefin altına düşmez); `_probe_duration` eklendi.
- `src/fetch_visuals.py`: en az **4 farklı klip**; aynı Pexels videosu tekrar indirilmez (eski hata: ikinci turda aynı video); ≤1080 genişlikte dosya tercih edilir (4K indirme yok).
- `.github/workflows/check_and_produce.yml`: `FALLBACK_HOURS` **20 → 6** (dokunulmasa da günde 1 video). README §Akış 7 ve `docs/kurgu.md` §1/§4/§5/§9 güncellendi.
- Yeni: `src/preview.py` + `.github/workflows/preview.yml` — elle tetiklenen, canlı akışa dokunmayan önizleme (1 aday → video → Telegram "ONIZLEME"; state/offset/YouTube yok, `permissions: contents: read`).
- Doğrulama (yerel, ffmpeg'siz): `py_compile` temiz; sahte modüllerle mantık testi — 18,4 sn → 8 parça/20 sn, kısa klip döngüsü, 1080 seçimi, id hariç tutma, filtre zinciri metni doğru. Gerçek video doğrulaması önizleme run'ı ile yapılacak.

## 2026-11-22 — TikTok kalıntıları silindi
- Silindi: `src/tiktok_upload.py`, `src/tiktok_oauth_exchange.py`, `src/tiktok_refresh_test.py`, `src/tiktok_init_test.py`, `.github/workflows/tiktok_oauth_exchange.yml`, `tiktok_refresh_test.yml`, `tiktok_init_test.yml`.
- Neden: Karar K16 (TikTok kapsam dışı). Hiçbir aktif kod bu dosyaları import etmiyordu; ana akış etkilenmez.
- Kalan: `src/yt_oauth_exchange.py:13` redirect URI `ufukkcan.github.io/tiktok-legal-pages/callback.html` (YouTube OAuth için gerekli, K17). GitHub'daki `TIKTOK_*` secret'ları artık hiçbir workflow tarafından kullanılmıyor; silinmeleri kullanıcıda (todo Faz 7).
- Workflow'lar silindiği için Actions arayüzünden kalkar; eski run'lar ve logları (token içerebilir) GitHub'da kalır.

## 2026-11-22 — Dokümantasyon ve yönetişim
- Eklendi: `CLAUDE.md`, `todo.md`, `docs/kurgu.md`, `docs/proje-plani.md`, `docs/changelog.md`, `docs/lessons.md`, `docs/hafiza/*` (özet, sistemler/durum, entegrasyonlar, dosya haritası, runbook, üretim geçmişi, işlem günlüğü, kararlar, roadmap).
- Karar: TikTok kapsam dışı (kullanıcı). Kalıntıların silinmesi onaya bağlandı.
- Önemli bulgular (yalnızca okuma ile): repo **public**; TikTok client secret commit `45370f4` geçmişinde açık; Actions'ta 1261 çalışma/110 gün (≈11/gün); Telegram offset 2026-10-18'den beri değişmemiş (bot otopilotta); 66 döngü: 39 done / 20 error / 7 yarım.
- Kod değişikliği yok.

## 2026-10-15 — edge-tts 7.2.8 → 7.3.1 (`bf20af7`, 21:51 +03)
- Neden: 2026-10-12 17:02 UTC ve 2026-10-15 15:44 UTC çalışmaları "Secimi kontrol et, varsa uret ve yukle" adımında ~1 dakikada başarısız oldu; iki döngü `selecting_hashtags → error` (üretimin ilk adımı seslendirme). Sürüm yükseltildikten sonraki ilk döngü (20261015-1850) 14 dakikada `done`.
- Nasıl: yalnızca `requirements.txt`.

## 2026-08-31 — Yerel TikTok OAuth script'i silindi (`8602d0f`)
- `src/setup_tiktok_oauth.py` kaldırıldı (içinde gömülü client key/secret vardı; geçmişte duruyor, bkz. lessons L14).

## 2026-08-29 — YouTube'a geri dönüş + video görünümü yenilemesi
- `bc4cdfe` pipeline: TikTok yükleyici çıkarıldı, `upload_youtube.upload_short` geri; `PRIVACY_STATUS`, `PUBLISH_TIME_ISTANBUL` (YouTube native `publishAt`) geri; ekranda kanca metni (`_extract_hook`) kaldırıldı.
- `8499cab`, `dcf0d97`, `8313727` check_and_produce: `approved_pending_publish` aşaması ve kendi zamanlayıcımız kaldırıldı; onayda doğrudan yeniden üret + YouTube'a yükle. (`dcf0d97` girinti hatası getirdi, `8313727` 3 dk sonra düzeltti — lessons L3.)
- `a72e13a` generate_script: başlık/hashtag kuralları YouTube'a göre (jenerikler: shorts, viral, trending, facts, didyouknow).
- `e80e68a` assemble_video: büyük kanca metni kaldırıldı; 260 px `follow_button.png` 1,2 sn'de pop-in (0.5x→1.15x→1.0x), ardından `tap_ring.png` dokunma halkası; CTA metni "FOLLOW FOR MORE" → "SUBSCRIBE"; altyazı `MarginV=170`.
- `0e75857` `assets/follow_button.png`, `6255979` `assets/tap_ring.png` eklendi (tap_ring kodu referans aldıktan 18 dk sonra geldi → 15:13 UTC döngüsü hata, lessons L11).
- `2e24200` yml yanlışlıkla kesildi (sadece env bloğu kaldı), `5806828` 3 dk sonra tam haliyle yeniden yazıldı: YouTube secret'ları, `CONTENT_LANGUAGE=en`, `TTS_VOICE=en-US-AriaNeural`, `PUBLISH_TIME_ISTANBUL=20:00`, `AUTO_TRIGGER_TIME=16:30`.
- `052021d` + `0d03d4a` `yt_oauth_exchange.py/.yml`: auth code → refresh token, Actions üzerinden. Run 33261095531 (15:45 UTC) başarılı; sonraki döngü 20260829-1548 16:06 UTC'de `done` (YouTube'a dönüşün ilk başarılı yüklemesi).

## 2026-08-14 — TikTok teşhis araçları ve OAuth tekrar (kapsam dışı, tarihçe)
- `f9243fd`/`733a9b0` refresh token testi, `18b2cb6`/`1acdf6e` `video/init` gövde varyasyon testi (401 araştırması), `d81c40d`/`cef0858` PKCE'li OAuth exchange geri eklendi.
- `d370d71` `PUBLISH_TIME_ISTANBUL=off`.
- O gün 3 elle tetiklenen döngü onaydan sonra `error` (TikTok yükleme).

## 2026-08-11 — TikTok'a geçiş (kapsam dışı, tarihçe)
- `3ffdd1b` içerik Türkçe (`tr`, `tr-TR-EmelNeural`), `2cac377` YT secret'ları yerine TIKTOK_* secret'ları.
- `11a8e5a` `tiktok_upload.py` (Content Posting API, FILE_UPLOAD, SELF_ONLY), `85ea2ca`/`45370f4` yerel OAuth script'i (**`45370f4` client key/secret'ı koda gömdü**), `a77192c` pipeline TikTok'a, `0daf578` `approved_pending_publish` + kendi zamanlanmış yayın beklemesi.
- `12233db`/`2b4efca` Actions OAuth exchange eklendi, `baa8746`/`c0e0455` 10 dk sonra silindi.
- `1390818` script prompt'u "viral" kurallarla yeniden yazıldı (ilk 3 sn kanca, yasak açılışlar, 65–85 kelime, merak açığı, twist/soru kapanış, 10 hashtag).

## 2026-08-09 — Etkileşim katmanları
- `74622a2`/`d25a89d`/`c0a4952`/`c3fad0c` `assets/subscribe_button.png` (önce yanlış klasöre, sonra 1 baytlık placeholder, sonra gerçek dosya).
- `e247efe` assemble: ilk 3 sn büyük kanca metni (DejaVuSans-Bold), video ortasında 460 px abone butonu, son 3 sn "FOLLOW FOR MORE"; filter_complex'e geçiş; altyazı MarginV 140→40.
- `52e3177` pipeline: script'in ilk cümlesi kanca metni olarak.
- `8a4bf62` yml: `fonts-dejavu-core` kurulumu.

## 2026-08-07 — Dosya boyutu kontrolü ve manuel reset
- `a2af89d` assemble: sabit CRF yerine süreye göre bitrate (hedef 30 MB, video 700–5000 kbps, ses 192→128 kbps). Öncesinde 05:54 ve 06:04 UTC iki döngü üretimde `error`; sonrasındaki 06:17 döngüsü `done` (zaman korelasyonu; log yok).
- `f02e09c` check_and_produce: "video uret" her durumda (aktif/tıkanmış döngü dahil) state'i sıfırlayıp yeni döngü başlatır.
- Aynı gün 7 döngü `done`, 2 döngü `error` (yoğun elle kullanım).

## 2026-08-05 — Cron zamanlaması
- `66c2123` cron `*/5` → `2,7,12,…,57` (saat başı yoğunluğundan kaçınma). `c942941` (2026-08-04 23:53) cron'u "yenilemek" için boş yorum satırı eklendi, `f02e09c` ile kaldırıldı.

## 2026-08-04 — İlk sürüm ve aynı gün iyileştirmeler
- `5ec33c0` README, requirements, setup_oauth.py, .gitignore. `188fc58` tüm kaynaklar + 2 workflow (kök dizinde). `23893c9` `src/` ve `.github/workflows/` yapısına taşındı.
- `ea489b5` edge-tts 6.1.19 → 7.2.8 (ilk denemeler 18:24–18:35 UTC elle tetiklenen 3 run başarısız; yükseltmeden sonra 18:54 döngüsü `done`).
- `a8f9868` (dosyayı yanlışlıkla 122 satır kesti) + `b780b37` (1 dk sonra geri koydu): `error` durumu günü kilitlemez; üretim hatası Telegram'a bildirilir ve state `error` olur.
- `823c59d`, `8d4d1d4`, `a857c96`: aktif döngü kavramı; manuel tetik `force=True`; otomatik tetik günde 1.
- `6e489f0` açıklamaya `#Shorts` eklenir.
- `21f43b9` cron `*/10` → `*/5`, `AUTO_TRIGGER_TIME` 20:00 → 16:30.
- `ce07d1d` DİL KURALI (Türkçe prompt'un çıktı dilini etkilememesi). `b7adc58` tags = 10–14 hashtag adayı.
- `2ab4b85` + `707dc8e` hashtag seçim aşaması (`selecting_hashtags`, 10 adaydan 5, toggle, 20 saat fallback).
- `6d63a8d` onayda Telegram `getFile` (20 MB sınırı) yerine yeniden üretip yükleme. Öncesinde 19:47 UTC döngüsü onay sonrası `error`.
- `c2eecad` pip/apt cache eklendi ama dosya "State'i" satırında kesildi → `75a061a` 4 dk sonra düzeltildi.
- `c4134f3`, `4c75f2a`, `d743c37` `state/pending_topics.json` elle silindi (takılan döngüleri sıfırlamak için).
- İlk başarılı YouTube yüklemesi: döngü 20260804-1854, 19:06 UTC, "Honey never spoils".
