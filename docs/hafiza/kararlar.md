# Kararlar

> Biçim: **Tarih · Karar · Gerekçe · Alternatif · Kaynak**. Kararı değiştiren yeni karar eskisini "yerini aldı: #N" diye işaretler. 2026-11-22 öncesi kararlar commit'lerden geriye dönük çıkarıldı; gerekçeler kod yorumlarından alındı.

| # | Tarih | Karar | Gerekçe | Durum | Kaynak |
|---|---|---|---|---|---|
| K1 | 2026-08-04 | Kanal içeriği İngilizce, bot yazışmaları Türkçe | Daha geniş izleyici; Telegram sadece kontrol paneli | Geçerli (K11 ile kısa süre TR oldu, K13 ile geri) | README, `5ec33c0` |
| K2 | 2026-08-04 | Altyapı: GitHub Actions + repo içi JSON state, sunucu yok | Bilgisayar kapalıyken çalışsın, sıfır maliyet | Geçerli | README |
| K3 | 2026-08-04 | İnsan onaylı akış: konu seçimi + video onayı, 20 saat fallback, 5 redo sınırı | Kalite kontrolü ama yayının durmaması | Geçerli | `188fc58` |
| K4 | 2026-08-04 | YouTube native zamanlanmış yayın: private + publishAt 20:00 İstanbul | ABD ve Avrupa aktif saatlerine en dengeli denk gelen saat (README gerekçesi) | Geçerli | README, pipeline |
| K5 | 2026-08-04 | Otomatik tetik 20:00 → 16:30 İstanbul; cron 10 → 5 dk | Yayın saatinden önce seçim/onay için zaman kalsın | Geçerli | `21f43b9` |
| K6 | 2026-08-04 | `error` günü kilitlemez; aynı gün yeniden tetiklenebilir | Geçici hatalar yayını öldürmesin | Geçerli | `a8f9868`/`b780b37`, `823c59d` |
| K7 | 2026-08-04 | Hashtag seçimi: 10 adaydan kullanıcı 5 seçer; açıklama = topic + 5 hashtag | Keşfete düşmeye yardımcı, kullanıcı kontrolü | Geçerli | `707dc8e` |
| K8 | 2026-08-04 | Onaylanan video Telegram'dan indirilmez, yeniden üretilir | Bot API getFile 20 MB sınırı | Geçerli (riskli, todo) | `6d63a8d` |
| K9 | 2026-08-07 | "video uret" her durumda state'i sıfırlar | Tıkanan döngüleri elle dosya silmeden kurtarmak | Geçerli | `f02e09c` |
| K10 | 2026-08-07 | Süreye göre bitrate, hedef 30 MB | Telegram 50 MB gönderme sınırı | Geçerli | `a2af89d` |
| K11 | 2026-08-11 | TikTok'a geçiş, Türkçe içerik, kendi zamanlayıcımız | — | Yerini aldı: K13 | `2cac377`, `0daf578` |
| K12 | 2026-08-11 | Script prompt'u "viral Shorts" kurallarına göre (ilk 3 sn kanca, 65–85 kelime, merak açığı, twist) | Tamamlama oranı algoritmanın ana sinyali | Geçerli | `1390818` |
| K13 | 2026-08-29 | YouTube + İngilizceye geri dönüş | TikTok denetimsiz uygulama: SELF_ONLY/401, 0 yayın | Geçerli | `bc4cdfe`, `5806828` |
| K14 | 2026-08-29 | Ekrandaki büyük kanca metni kaldırıldı; küçük pop-in Subscribe + dokunma halkası; CTA "SUBSCRIBE"; altyazı MarginV=170 | Altyazı/YouTube arayüzü ile çakışmama, sade görünüm | Geçerli | `e80e68a` |
| K15 | 2026-08-29 | YouTube refresh token'ı Actions üzerinden (callback sayfası + exchange workflow) alma | Yerel Python/tarayıcı akışı kullanılamadı (yorum: "bilgisayarda Python calistiramayan/engellenen durumlar") | Geçerli ama riskli (token loga düşer) | `052021d` |
| K16 | 2026-11-22 | **TikTok tamamen kapsam dışı**; sadece YouTube. TikTok dosyaları kaldırılabilir | Kullanıcı kararı | Geçerli; TikTok dosyaları kullanıcı onayıyla 2026-11-22'de silindi | Kullanıcı mesajı |
| K17 | 2026-11-22 | `ufukkcan/tiktok-legal-pages` reposu silinmez | YouTube OAuth redirect URI'si onun `callback.html`'ini kullanıyor | Geçerli (kullanıcı onayı bekleniyor) | `yt_oauth_exchange.py:13` |
| K18 | 2026-11-22 | Doküman yapısı: `CLAUDE.md` + `todo.md` kökte, `docs/` (kurgu, plan, changelog, lessons), `docs/hafiza/` (01–05 + günlük, kararlar, roadmap, üretim geçmişi) | Kullanıcının istediği yerler (docs/changelog.md, docs/lessons.md, todo.md) + oturum başı hızlı bağlam | Geçerli | Bu oturum |
