# TODO — youtube-shorts-automation

> Tüm yapılan ve yapılacak işler. `[x]` yalnızca kanıtla doğrulandıysa (commit / state geçmişi / Actions API). Doğrulama 2026-11-22'de yapıldı.
> 🔒 = dış sisteme yazar / kullanıcının hesabında yapılır → komut + gerekçe + etki sunulur, onay beklenir.
> Faz açıklamaları: [docs/proje-plani.md](docs/proje-plani.md).

## Faz 0 — Kurulum
- [x] Repo, README, requirements, setup_oauth.py, .gitignore — kanıt `5ec33c0`
- [x] Kaynak kodlar + 2 workflow, `src/` ve `.github/workflows/` yapısı — `188fc58`, `23893c9`
- [x] Secret'lar (Anthropic, Pexels, Telegram, YouTube) tanımlı — kanıt: döngüler bu servislerle `done` oluyor (son: 2026-11-22 07:31 UTC)
- [x] Telegram botu çalışıyor — kanıt: offset ilerlemiş (son 2026-10-18), konu mesajları gönderiliyor (döngü #66 pending)

## Faz 1 — MVP
- [x] Konu üretimi (Claude) + Telegram seçimi + video üretimi + onay/redo + YouTube private/publishAt — kanıt: ilk `done` #2 2026-08-04 19:06 UTC
- [x] Redo akışı ve sayaç — kanıt: #9 attempts=3 ile `done` (2026-08-07)

## Faz 2 — Akış sağlamlaştırma
- [x] `error` günü kilitlemez — `a8f9868`/`b780b37`, `823c59d`
- [x] Manuel tetik `force`, sonra her durumu sıfırlama — `8d4d1d4`, `a857c96`, `f02e09c`
- [x] Hashtag seçim aşaması — `2ab4b85`, `707dc8e`; kanıt: `selecting_hashtags` geçişleri #4'ten itibaren
- [x] Onayda yeniden üretip yükleme (20 MB getFile) — `6d63a8d`; kanıt: #5 done
- [x] `#Shorts` ekleme — `6e489f0`
- [x] Dil kuralı — `ce07d1d`
- [x] Cron 5 dk ofsetli, pip/apt cache, AUTO_TRIGGER 16:30 — `21f43b9`, `c2eecad`, `75a061a`, `66c2123`

## Faz 3 — Video kalitesi
- [x] Hedef boyutlu bitrate — `a2af89d`; kanıt: sonraki döngüler Telegram'a gönderilebildi
- [x] Subscribe pop-in + dokunma halkası + SUBSCRIBE CTA + MarginV 170 — `e80e68a`, `0e75857`, `6255979`
- [x] Viral script kuralları — `1390818`, `a72e13a`
- [x] DejaVu font kurulumu — `8a4bf62`

## Faz 4 — TikTok (iptal)
- [x] TikTok denendi ve bırakıldı; YouTube'a dönüldü — `bc4cdfe`, `5806828`; kanıt: #34 done 2026-08-29 16:06
- [x] Karar: TikTok tamamen kapsam dışı (kullanıcı, 2026-11-22) — kararlar K16

## Faz 5 — Kararlı işletim
- [x] YouTube refresh token yenilendi — run 33261095531; kanıt: #34 done
- [x] edge-tts 7.3.1 — `bf20af7`; kanıt: #54 done 14 dk içinde, sonrasında edge-tts kaynaklı hata yok
- [x] Sistem çalışıyor — kanıt: #65 done 2026-11-22 07:31 UTC, #66 pending 15:35 UTC

## Faz 6 — Dokümantasyon ve yönetişim (2026-11-22)
- [x] `docs/kurgu.md` — proje kurgusu
- [x] `docs/proje-plani.md` — fazlar, neredeyiz
- [x] `docs/changelog.md` — geriye dönük
- [x] `docs/lessons.md` — 25 ders
- [x] `todo.md` — bu dosya
- [x] `CLAUDE.md` — talimatlar + oturum başı listesi
- [x] `docs/hafiza/01–05`, `uretim-gecmisi.md`, `islem-gunlugu.md`, `kararlar.md`, `roadmap.md`
- [x] Claude kalıcı hafızasına kullanıcı profili + proje işaretçisi
- [x] `git pull --ff-only` (0d34b2c → 521ee6b) + dokümanlar commit + push (kullanıcı onayı 2026-11-22) — kanıt: İnceleme

## Faz 7 — Güvenlik temizliği (SIRADAKİ, onay bekliyor)
- [ ] 🔒 TikTok Developer Portal'da uygulamayı sil ya da client secret'ı yenile (public `45370f4`'te açık) — kullanıcı yapar
- [ ] 🔒 Actions run 33261095531 (yt_oauth_exchange) logunu tarayıcıda aç: refresh token düz metin görünüyor mu? Görünüyorsa: run logunu sil + Google hesabı → Güvenlik → üçüncü taraf erişimden uygulama erişimini kaldır → `setup_oauth.py` ile yeni token → `YT_REFRESH_TOKEN` güncelle → 1 elle run ile doğrula
- [ ] 🔒 tiktok_oauth_exchange run loglarını (31495693681, 31495884213, 31496255429, 31800716091) sil
- [ ] 🔒 GitHub Secrets'tan `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REFRESH_TOKEN` sil
- [ ] 🔒 Repo Settings → Code security → Secret scanning + Push protection aç
- [ ] `yt_oauth_exchange.py` token'ı loga basmasın (`::add-mask::`) ya da workflow'u kaldırıp yalnız yerel `setup_oauth.py` — karar kullanıcıda

## Faz 8 — TikTok kaldırma ve temizlik (onay bekliyor)
- [x] Sil: `src/tiktok_upload.py`, `src/tiktok_oauth_exchange.py`, `src/tiktok_refresh_test.py`, `src/tiktok_init_test.py` (kullanıcı onayı 2026-11-22)
- [x] Sil: `.github/workflows/tiktok_oauth_exchange.yml`, `tiktok_refresh_test.yml`, `tiktok_init_test.yml`
- [ ] Sil: `telegram_bot.download_review_video` (kullanılmıyor), `assets/subscribe_button.png` (kullanılmıyor)
- [ ] `ufukkcan/tiktok-legal-pages` reposunu SİLME (YouTube OAuth callback) — kullanıcıya teyit ettir
- [ ] README'yi güncelle: AUTO_TRIGGER 16:30, cron 5 dk (gerçekte ≈2 saat), hashtag adımı, gerçek akış süreleri
- [x] Silme sonrası `python -m py_compile` (exit 0) ve `git grep -i tiktok` (kodda yalnız `yt_oauth_exchange.py:13` callback URL'si — kasıtlı)
- [ ] Silme sonrası ilk zamanlanmış `check_and_produce` run'ının yeşil olduğunu doğrula (silinen dosyaları import eden kod yoktu; risk düşük)

## Faz 9 — Güvenilirlik (öneri, her biri ayrı onay)
- [ ] YouTube'da 39 videonun görünürlüğünü doğrula (YouTube Studio) — kullanıcı bakar; "Private (locked)" varsa API audit gerekir
- [ ] YouTube `video_id` + yükleme zamanını `pending_topics.json`'a yaz
- [ ] Konu tekrarını önle (normalize anahtar, tüm geçmiş)
- [ ] Telegram offset'ini işleme sonrası kaydet
- [ ] Onaylanan videonun birebir yüklenmesi (artifact sakla) — maliyet/karmaşıklık değerlendir
- [ ] Yoklama gecikmesi: dış tetikleyici ya da webhook köprüsü — değerlendir
- [ ] Otopilot sıklığı: FALLBACK_HOURS'u düşürmek (ör. 6) ister misin? — karar kullanıcıda
- [ ] Bilinmeyen hataların logları: 33665069160, 34754285697, 43633352748 (kullanıcı tarayıcıdan hata satırını paylaşır)
- [ ] Bilinmeyenler: bot kullanıcı adı, kanal id, GCP proje/consent/audit/kota → `docs/hafiza/02-sistemler-durum.md`'ye işle

## Faz 10 — Büyüme (opsiyonel)
- [ ] YouTube Analytics geri bildirimi, yayın saati deneyi, kelime vurgulu altyazı — bkz. roadmap

---

## İnceleme

### 2026-11-22 — TikTok dosyaları silindi, pull + commit + push
- Sonuç: 4 Python + 3 workflow dosyası silindi; dokümanlar eklendi; tek commit olarak `main`'e push edildi.
- Kanıt: `git pull --ff-only` 0d34b2c → 521ee6b (yalnız state); `py_compile` exit 0; kodda kalan tek "tiktok" geçişi YouTube OAuth callback URL'si. Push sonucu ve commit hash'i: `docs/hafiza/islem-gunlugu.md`.
- Açık: silme sonrası ilk Actions run'ının yeşil olduğunun doğrulanması.

### 2026-11-22 — Faz 6 dokümantasyon
- Sonuç: 15 doküman oluşturuldu; kod ve dış sistemlerde değişiklik yok.
- Kanıt/yöntem: 320 commit'ten kullanıcıya ait 67 commit'in diff'leri tek tek okundu; `state/pending_topics.json`'un tüm commit'lerinden 66 döngünün geçiş geçmişi çıkarıldı (39 done / 20 error / 7 yarım); GitHub API: repo public, 1261 run, 30 failure (17'si state error'larıyla eşleştirildi), 21 cancelled; Telegram offset son değişim 2026-10-18.
- Doğrulanamayanlar: failure loglarının içeriği (anonim API izin vermiyor), YouTube'daki gerçek görünürlük, GCP ayarları. İlgili maddeler Faz 7/9'da.
