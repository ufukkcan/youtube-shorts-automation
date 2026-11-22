# Lessons — hatalar, sorunlar, çözümler ve kurallar

> Oturum başında oku. Her düzeltmeden sonra yeni madde ekle: **Örüntü → Kök neden → Çözüm → Kural**.
> Kanıt seviyesi: **[Kanıtlı]** commit/log/API ile doğrulandı · **[Korelasyon]** zaman/sıra uyumu var, log yok · **[Bilinmiyor]** neden doğrulanamadı.
> Secret değerleri yazılmaz; yalnızca commit/run referansı.

## A. Güvenlik

### L14 — Secret koda gömüldü (public repo) [Kanıtlı]
- Örüntü: `45370f4` (2026-08-11) `src/setup_tiktok_oauth.py` içine TikTok CLIENT_KEY ve CLIENT_SECRET düz metin yazıldı; dosya `8602d0f` (2026-08-31) ile silindi ama **git geçmişinde duruyor**. Repo public (2026-11-22 API ile doğrulandı).
- Kök neden: "yerel çalıştır" script'i placeholder doldurularak GitHub web editöründen commit edildi.
- Çözüm (bekliyor): TikTok uygulamasını sil/secret'ı yenile. Geçmişi yeniden yazmak (filter-repo) tek başına yetmez; secret iptal edilmeli.
- Kural: Secret yalnızca GitHub Secrets'ta. Koda/dosyaya asla. Commit öncesi `git diff` içinde anahtar desenleri ara; repo'da GitHub Secret scanning + Push protection açık olmalı.

### L15 — OAuth exchange workflow'ları token'ı loga basıyor [Kanıtlı: kod / Bilinmiyor: log içeriği]
- Örüntü: `yt_oauth_exchange.py` ve `tiktok_oauth_exchange.py` `print("Tam yanit:", data)` ve `print(data["refresh_token"])` yapıyor. Yeni alınan token henüz secret olmadığı için GitHub maskelemez. Public repoda Actions logları herkese açık. Çalışan run'lar: YT 33261095531 (2026-08-29), TikTok 31495693681, 31495884213, 31496255429, 31800716091.
- Çözüm (bekliyor): Logları kontrol et → görünüyorsa run loglarını sil, YouTube refresh token'ı Google hesabından iptal edip yenile. Script'te `print(f"::add-mask::{token}")` kullan ya da token'ı loga hiç yazma (yerel `setup_oauth.py` yolu).
- Kural: Hiçbir script token/secret basmaz; teşhis çıktısında yalnızca uzunluk ve HTTP kodu. (`tiktok_refresh_test.py` de secret'ların ilk/son karakterlerini basıyor — kaldırılacak.)

## B. Değişiklik yönetimi (GitHub web editörü)

### L1 — Web editörü yapıştırmasıyla dosya kesildi [Kanıtlı]
- `a8f9868` check_and_produce.py'den 122 satır silindi; 1 dk sonra `b780b37` geri koydu. `2e24200` yml'de sadece env bloğu kaldı; 3 dk sonra `5806828`.
- Kural: Her düzenlemeden sonra commit diff istatistiğine bak (beklenmedik "-100 satır" = hata). Mümkünse yerelde düzenle, `git diff --stat` ile kontrol et, sonra push.

### L2 — YAML yarım kaldı, state push adımı kayboldu [Kanıtlı]
- `c2eecad` son adım `- name: State'i` satırında kesildi → 4 dk boyunca state commit edilemedi; `75a061a` düzeltti.
- Kural: Workflow değişikliğinden sonra bir `workflow_dispatch` çalıştırıp "State kaydet" adımının yeşil olduğunu doğrula.

### L3 — Girinti hatası canlıya gitti [Kanıtlı]
- `dcf0d97` `_produce_and_upload` çağrısı fazla girintili (IndentationError); `8313727` 3 dk sonra düzeltti.
- Kural: Python değişikliği push etmeden önce `python -m py_compile src/*.py`.

### L11 — Asset, onu kullanan koddan sonra geldi [Korelasyon]
- `e80e68a` (18:03 +03) `tap_ring.png`'yi referans aldı; dosya `6255979` (18:21 +03) ile geldi. Arada 15:13 UTC döngüsü üretimde `error`.
- Kural: Kod ve kullandığı asset aynı commit'te (ya da asset önce).

### L12 — Binary dosya yanlış yere / boş yüklendi [Kanıtlı]
- `subscribe_button.png` önce kök dizine, sonra 1 baytlık placeholder `assets/`'e, sonra gerçek dosya. (`74622a2` → `d25a89d` → `c0a4952` → `c3fad0c`)
- Kural: Binary dosyalarda commit sonrası boyutu kontrol et (`git show --stat`).

### L8 — State elle silinerek "reset" yapıldı [Kanıtlı]
- `c4134f3`, `4c75f2a`, `d743c37` `state/pending_topics.json` silindi. Kalıcı çözüm `f02e09c`: "video uret" her durumu sıfırlar.
- Kural: Takılan döngü için Telegram'dan `video uret` yaz; state dosyasını elle silme/düzenleme (bot her çalışmada push ettiği için çakışma çıkar).

### L18 — README güncel değil [Kanıtlı]
- README: otomatik tetik 20:00, cron 10 dk, hashtag adımı yok. Gerçek: 16:30, 5 dk (ofsetli), hashtag adımı var.
- Kural: Yapılandırma değişikliği = README + docs/kurgu.md aynı commit'te.

## C. Dış servis sınırları

### L5 — edge-tts, Microsoft servis değişikliğiyle kırılıyor [Korelasyon, iki kez]
- 2026-08-04: 6.1.19 ile ilk 3 run başarısız → 7.2.8 (`ea489b5`) sonrası başarı. 2026-10-12 ve 10-15: üretim adımı ~1 dk'da düştü → 7.3.1 (`bf20af7`) sonrası başarı.
- Kural: Üretim "1/4 Seslendirme" adımında düşüyorsa ilk iş `pip index versions edge-tts` ile son sürüme bak ve yükselt. Sürüm sabit kalsın (`==`), ama periyodik kontrol et.

### L6 — Telegram getFile 20 MB indirme sınırı [Kanıtlı: kod yorumu + sıra]
- Onaylanan video Telegram'dan geri indirilemedi (2026-08-04 19:47 UTC `reviewing → error`). `6d63a8d` ile yeniden üretip yükleme.
- Yan etki: Yüklenen video onaylanandan farklı olabilir (Pexels sonuçları değişebilir). Kalıcı çözüm todo'da.

### L7 — Telegram sendVideo 50 MB sınırı [Korelasyon]
- 2026-08-07 05:54 ve 06:04 UTC üretim/gönderim hataları; `a2af89d` bitrate hedeflemesinden (30 MB) sonra düzeldi.
- Kural: Çıktı boyutunu süreye göre bitrate ile sınırla; CRF tek başına boyut garantisi vermez.

### L13 — Platform API'si denetim istiyor (TikTok) [Kanıtlı: kod + 10 error]
- Denetlenmemiş TikTok uygulaması yalnız SELF_ONLY; `video/init` 401; 11 döngüde 0 yayın. YouTube'a dönüldü; 2026-11-22 TikTok kapsam dışı.
- Kural: Yeni platform entegrasyonundan önce API'nin denetim/onay şartlarını ve gerçek bir test yüklemesini doğrula; canlı akışı değiştirmeden ayrı dalda dene.

### L16 — YouTube yüklemesi dönüşte başarısız oldu, token yenilendi [Bilinmiyor]
- 2026-08-29 15:32 UTC `reviewing → error` (YouTube'a dönüş sonrası ilk yükleme). 15:45 UTC `yt_oauth_exchange` ile yeni refresh token alındı; 16:06 döngüsü `done`. Önceki token'ın neden geçersiz olduğu log olmadan doğrulanamadı.
- Kural: Yükleme `invalid_grant` verirse refresh token'ı yenile; consent screen "Testing" ise 7 günde bir düşer → "In production" yap.

### L19 — YouTube'a yüklenen videonun gerçekten public olduğu doğrulanmadı [Bilinmiyor]
- `done` = `videos.insert` id döndürdü. Google, denetlenmemiş API projelerinden yüklenenleri private'a kilitleyebilir. video_id state'te yok.
- Kural: "Yüklendi" ≠ "yayında". YouTube Studio'dan doğrula; video_id'yi state'e yaz.

## D. Zamanlama ve akış

### L4 — GitHub cron güvenilmez [Kanıtlı: API]
- 5 dk cron → 110 günde 1261 run (≈11/gün). `c942941` cron'u "yenilemek" için boş commit atılmıştı (tetiklenmiyor şüphesi). 2026-11-22 döngüsü 16:30 hedefine göre ≈2 saat geç başladı.
- Kural: Zamanlanmış GitHub Actions'a dakika hassasiyetiyle güvenme. Tepki süresi kritikse dış tetikleyici (repository_dispatch) ya da webhook değerlendir.

### L20 — Otopilot yayın sıklığını 3 güne düşürüyor [Kanıtlı: state geçmişi]
- 2026-10-18'den beri Telegram offset değişmedi (hiç etkileşim yok). Her aşama 20 saat bekliyor → döngü ≈2,5–3 gün.
- Kural: Günlük yayın hedefleniyorsa ya etkileşim gerekir ya da FALLBACK_HOURS düşürülmeli (karar kullanıcıda).

### L17 — Tekrarlayan konular [Kanıtlı: state geçmişi]
- Seçilen konular: Cleopatra's Needle 5 kez (#4, #5, #9, #18, #20), Baader-Meinhof 3 kez (#36, #49, #63), Honey 2, Antikythera 2, Lobsters 2. Claude'a yalnız son 60 başlık gidiyor ve başlıklar her seferinde farklı yazılıyor (tam eşleşme yok).
- Kural: Tekrar kontrolü serbest metin başlıkla yapılmaz; normalize anahtar (ör. ana varlık adı) + tüm geçmiş.

### L9 — Türkçe prompt çıktı dilini etkiledi [Kanıtlı: commit]
- `ce07d1d` DİL KURALI eklendi; tags dili `1390818`'de netleştirildi.
- Kural: Talimat dili ≠ çıktı dili ise bunu sistem ve kullanıcı mesajında ayrı ayrı açıkça yaz.

### L10 — Altyazı konumu deneme-yanılma [Kanıtlı: commit]
- MarginV 140 → 40 → 170; libass MarginV'yi PlayResY'ye göre ölçekliyor, küçük değişiklik büyük kayma.
- Kural: Görsel değişikliği canlıya vermeden önce `PRIVACY_STATUS`/test ile bir örnek üretip Telegram'da bak.

## E. Bu oturumda (2026-11-22, Claude) öğrenilenler

### L21 — Bash aracı bu makinede çalışmıyor [Kanıtlı]
- Git Bash `fork: Resource temporarily unavailable` / `0xC0000142`. Kural: Bu iş istasyonunda PowerShell aracını kullan.

### L22 — Yerel klon geride olabilir [Kanıtlı]
- Yerel `main` remote'un 18 commit gerisindeydi (bot her gün push ediyor). Kural: Durum analizi `git fetch` + `origin/main` üzerinden yapılır; yerel `state/` dosyasına güvenme.

### L23 — GitHub anonim API limiti 60/saat [Kanıtlı]
- 30 run'ın job sorgusunda 12'den sonra 403. Kural: `gh` CLI (kurulu değil) ya da token ile çağır; anonimde sorguları önce sayısını hesapla, toplu sorgudan kaçın.

### L24 — PowerShell 5.1 git stderr'i hata gibi gösterir [Kanıtlı]
- `git fetch` başarılı olduğu halde `NativeCommandError` görünüyor. Kural: Sonucu çıktı içeriği/`git status` ile doğrula, kırmızı yazıya göre değil.

### L25 — Masaüstü Desktop Commander MCP bağlanamadı [Kanıtlı]
- Bu proje iç ağ gerektirmiyor; yerel komutlar PowerShell aracıyla yeterli.
