# Proje Planı — youtube-shorts-automation

> Kurgudan ([kurgu.md](kurgu.md)) ve gerçek geçmişten (320 commit, 66 üretim döngüsü, 1261 Actions çalışması) çıkarıldı. Tarihler commit/state kayıtlarından doğrulandı.
> Son güncelleme: 2026-11-22. Maddelerin işaretli takibi: [../todo.md](../todo.md).

## Neredeyiz? (2026-11-22)

- **Faz 0–3 ve 5 tamam**, sistem üretimde ve otopilotta çalışıyor: 39 döngü `done` (YouTube'a yükleme çağrısı başarılı), son başarı 2026-11-22 07:31 UTC ("The Zip Code That Does Not Exist — 00000").
- **Faz 4 (TikTok) iptal**; 2026-11-22 kararıyla tamamen kapsam dışı, kalıntılar temizlenecek.
- **Faz 6 (dokümantasyon/yönetişim) bugün tamamlandı.**
- **Sıradaki: Faz 7 (güvenlik temizliği)** — kullanıcı onayı ve kullanıcının kendi hesaplarında yapacağı adımlar gerekiyor.
- Anlık bot durumu: döngü `20261122-1535` **pending** (5 konu Telegram'da, 2026-11-22 15:35 UTC başladı). Yerel klon remote'un 18 commit gerisinde (sadece state commit'leri).

## Fazlar

### Faz 0 — Kurulum (2026-08-04) ✅
Repo oluşturma, secret'lar, Telegram botu, YouTube OAuth, ilk dosyalar (`5ec33c0`, `188fc58`), klasör yapısı düzeltme (`23893c9`).

### Faz 1 — MVP: Telegram seçimli + onaylı YouTube hattı (2026-08-04) ✅
5 konu → seçim → video → onay/redo → YouTube private + publishAt 20:00. İlk başarılı yükleme 2026-08-04 19:06 UTC ("Honey never spoils").

### Faz 2 — Akış sağlamlaştırma (2026-08-04 → 2026-08-07) ✅
- `error` durumunun günü kilitlememesi (`a8f9868`/`b780b37`, `823c59d`)
- Manuel tetiklemenin her zaman çalışması, sonra her durumu sıfırlaması (`8d4d1d4`, `a857c96`, `f02e09c`)
- Hashtag seçim adımı (`b7adc58`, `2ab4b85`, `707dc8e`)
- Onayda Telegram'dan indirme yerine yeniden üretim (20 MB getFile sınırı) (`6d63a8d`)
- `#Shorts` otomatik ekleme (`6e489f0`)
- İçerik dili kuralı (`ce07d1d`)
- Cron 10 dk → 5 dk, ofsetli dakikalar; pip/apt cache; otomatik tetik 16:30 (`21f43b9`, `c2eecad`, `75a061a`, `66c2123`)

### Faz 3 — Video kalitesi ve etkileşim (2026-08-07 → 2026-08-29) ✅
- Hedef boyutlu bitrate (Telegram 50 MB) (`a2af89d`)
- Kanca metni + subscribe butonu + CTA (`e247efe`, `52e3177`, `8a4bf62`) → sonra sadeleştirme: kanca metni kaldırıldı, küçük pop-in buton + dokunma halkası, altyazı MarginV=170 (`e80e68a`, `bc4cdfe`, `6255979`)
- Viral script kuralları (kanca, 65–85 kelime, merak açığı, twist) (`1390818`, `a72e13a`)

### Faz 4 — TikTok denemesi (2026-08-11 → 2026-08-29) ❌ İptal
TikTok'a geçiş (Türkçe içerik, SELF_ONLY), OAuth ve 401 init teşhis araçları. Bu dönemdeki 11 döngüden 10'u `error`, 1'i yarım kaldı; hiçbiri yayınlanmadı. 2026-08-29'da YouTube + İngilizceye dönüldü. 2026-11-22: TikTok tamamen kapsam dışı.

### Faz 5 — Kararlı işletim (2026-08-29 → sürüyor) ✅ (işletimde)
- YouTube refresh token yenileme (Actions üzerinden, `052021d`, `0d03d4a`; run 2026-08-29 15:45 UTC)
- edge-tts 7.2.8 → 7.3.1 (Microsoft servis değişikliği sonrası seslendirme hataları) (`bf20af7`, 2026-10-15)
- 2026-08-29'dan bugüne 27 döngü `done`, 7 döngü `error` (2'si 08-29'daki geçiş/token yenileme sırasında).

### Faz 6 — Dokümantasyon ve yönetişim (2026-11-22) ✅
CLAUDE.md talimatları, kurgu, plan, changelog, lessons, todo, hafıza dosyaları, işlem günlüğü, kararlar, roadmap, üretim geçmişi.

### Faz 7 — Güvenlik temizliği (sıradaki, onay bekliyor) ⏳
1. TikTok uygulamasını TikTok Developer Portal'dan sil / client secret'ı yenile (public commit `45370f4`'te açık).
2. `yt_oauth_exchange` run 33261095531 ve `tiktok_oauth_exchange` 4 run'ının loglarını kontrol et, token görünüyorsa logları sil; YouTube refresh token'ı iptal edip yenile.
3. TIKTOK_* GitHub secret'larını sil.
4. Repo'da GitHub Secret scanning + Push protection'ı aç.
5. OAuth exchange script'inin token'ı loga basmasını engelle (`::add-mask::`) ya da yerel `setup_oauth.py` yolunu standart yap.

### Faz 8 — TikTok kaldırma + kod temizliği (kısmen tamam) 🟡
✅ 2026-11-22: `src/tiktok_*.py` (4) ve `.github/workflows/tiktok_*.yml` (3) silindi. Kalan (onay bekliyor): `telegram_bot.download_review_video` (kullanılmıyor), README'yi güncel yapılandırmaya eşitleme (16:30, 5 dk, hashtag adımı).

### Faz 9 — Güvenilirlik iyileştirmeleri (öneri, onay bekliyor) ⏳
- YouTube `video_id` ve yükleme zamanını state'e yazmak (yayın doğrulaması).
- Tekrarlayan konuları önlemek (normalize edilmiş anahtar + tüm geçmiş).
- Yoklama güvenilirliği (dış tetikleyici → `workflow_dispatch`/`repository_dispatch`, ya da Telegram webhook köprüsü) — maliyet/karmaşıklık değerlendirmesiyle.
- Telegram offset'ini işleme sonrası kaydetmek.
- Onaylanan videonun birebir yüklenmesi (ör. üretilen mp4'ü Actions artifact/release olarak saklayıp yükleme anında indirmek).

### Faz 10 — Büyüme/analitik (opsiyonel) 💤
YouTube Analytics API ile izlenme/tutma oranı geri bildirimi → prompt iyileştirme; yayın saati deneyleri. Kapsam ve maliyet kullanıcıyla netleşmeden başlanmaz.

## Kritik yol
Faz 7 (güvenlik) → Faz 8 (temizlik) → Faz 9'dan "video_id kaydı" ve "YouTube'da gerçekten public mi?" doğrulaması. Bunlar bitmeden yeni özellik eklenmez.
