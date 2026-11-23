# 01 — Tek sayfalık özet (önce bunu oku, çoğu iş için yeter)

- **Ne:** İngilizce "ilginç bilgi" YouTube Shorts kanalı ("interesthings") için Telegram onaylı otomatik üretim/yükleme hattı. Kapsam yalnızca YouTube (TikTok kapsam dışı, 2026-11-22).
- **Nerede çalışır:** GitHub Actions, public repo `ufukkcan/youtube-shorts-automation`, branch `main`. Yerel klon: `C:\Users\mc061965\Documents\projeler\youtube-shorts-automation`.
- **Ana dosya:** `src/check_and_produce.py` (durum makinesi). Workflow: `.github/workflows/check_and_produce.yml` (cron 5 dk, gerçekte ≈2 saatte bir).
- **Akış:** pending (5 konu) → selecting_hashtags (10'dan 5) → reviewing (video Telegram'da onay/redo) → done (YouTube private + publishAt 20:00 İstanbul). Her adım 6 saat (FALLBACK_HOURS) yanıtsız kalırsa kendiliğinden ilerler. `video uret` her durumu sıfırlar. Hata → `error`.
- **Üretim:** Claude `claude-sonnet-4-6` (script) → edge-tts 7.3.1 (ses) → Pexels (klip) → faster-whisper small (altyazı) → ffmpeg (1080x1920, buton animasyonu, CTA) → YouTube Data API v3.
- **State:** `state/pending_topics.json` (aktif döngü), `state/topics_used.json` (son 300 başlık), `state/telegram_offset.json`. Bot her çalışmada commit+push eder (`shorts-bot`).
- **Ayarlar (yml env):** AUTO_TRIGGER_TIME=16:30, PUBLISH_TIME_ISTANBUL=20:00, FALLBACK_HOURS=6 (2026-11-23 değişikliği; canlıya alınana kadar remote'ta 20), MAX_REDO_ATTEMPTS=5, CONTENT_LANGUAGE=en, TTS_VOICE=en-US-AriaNeural, PRIVACY_STATUS=public.
- **Durum (2026-11-22):** Çalışıyor, otopilotta (2026-10-18'den beri etkileşim yok). 66 döngü: 39 done, 20 error, 7 yarım. Son done 2026-11-22 07:31 UTC. Aktif döngü `20261122-1535` pending.
- **Açık riskler:** public geçmişte TikTok secret (`45370f4`); OAuth exchange loglarında token olabilir; video_id kaydedilmiyor; konu tekrarı; README kısmen eski. (Videoların public yayınlandığı Studio'dan doğrulandı.)
- **Kanal (Studio, 28 gün):** 18 abone, 1.841 görüntüleme, 0 yeni abone, ort. izlenme 12 sn (≈%36). Ayrıntı: `data/analiz-2026-11-22-studio-28gun.md` (gitignore, yalnız yerel).
- **Hedef:** YouTube gelirini açmak (YPP: 1.000 abone + 90 günde 10M Shorts görüntüleme + özgün içerik incelemesi).
- **Sıradaki iş:** todo.md → "Faz 11 — Gelir hedefi" (1, 2, 4 uygulanıyor; önizleme sonrası canlıya alma onayı). "Faz 7 Güvenlik" kullanıcı isteğiyle ertelendi, oturum başında hatırlat.
- **Detay gerekirse:** kurgu → `docs/kurgu.md`, dosya/fonksiyon yeri → `04-dosya-haritasi.md`, komutlar → `05-runbook.md`, geçmiş döngüler → `uretim-gecmisi.md`.
