# Üretim geçmişi — tüm döngüler

> Kaynak: `state/pending_topics.json`'un `origin/main` üzerindeki tüm commit'leri (2026-11-22, `521ee6b`). Yeniden üretme komutu: [05-runbook.md](05-runbook.md) §4.
> Saatler **UTC** (bot commit saati = durum geçişinin kaydedildiği an). "done" = `videos.insert` başarılı döndü; YouTube'da public olduğu **doğrulanmadı**.
> Son durum boşsa/yalnız `pending` ise döngü yeni döngüyle ezilmiş (elle `video uret`, elle silme ya da hata sonrası) demektir.

## Özet
- Toplam 66 döngü: **39 done**, **20 error**, **7 yarım** (pending/selecting_hashtags'te ezilmiş ya da aktif).
- TikTok dönemi (#21–#31, 2026-08-11 → 08-29): 10 error + 1 yarım, 0 yayın. Kapsam dışı.
- YouTube'a dönüş sonrası (#32–#66): 27 done, 7 error, 1 aktif.
- İlk yayın: #2 (2026-08-04 19:06). Son yayın: #65 (2026-11-22 07:31). Aktif: #66 pending.
- Otopilot dönemi (≈#39'dan itibaren): adımlar arası ≈20–29 saat → döngü ≈2,5–3 gün.
- Tekrarlayan seçilmiş konular: Cleopatra's Needle (#4, #5, #9, #18, #20), Baader-Meinhof (#36, #49, #63), Honey (#2, #16), Antikythera (#17, #60), Lobsters (#6, #42).

## Hata eşleştirmesi (error döngüleri ↔ neden)
| # | Batch | Geçiş | Run (UTC) | Neden | Kanıt |
|---|---|---|---|---|---|
| 4 | 20260804-1937 | reviewing→error | — | Onaylanan videoyu Telegram getFile ile indirme (20 MB sınırı) | Korelasyon: `6d63a8d` 7 dk sonra |
| 10, 11 | 20260807-0546/0556 | selecting_hashtags→error | 31151824155, 31152387581 (dispatch) | Muhtemelen Telegram sendVideo boyut sınırı | Korelasyon: `a2af89d` sonrası düzeldi |
| 21, 22 | 20260811/0812 | approved_pending_publish→error | 31621581486, 31724142695 | TikTok yükleme | TikTok dönemi |
| 24–31 | 20260814-… / 0826 | reviewing→error | 31796963608, 31799177982, 31801466820, 31989132404, 32324909281, 32613314060, 32925073829 | TikTok yükleme (init 401) | TikTok dönemi, teşhis araçları aynı gün |
| 32 | 20260829-1509 | selecting_hashtags→error | (failure listesinde yok) | `tap_ring.png` henüz repoda yoktu | Korelasyon: asset 15:21 UTC geldi |
| 33 | 20260829-1523 | reviewing→error | 33260358601 | YouTube yükleme; token yenilendi | Korelasyon: yt_oauth_exchange 15:45 |
| 37 | 20260902-1403 | selecting_hashtags→error | 33665069160 (6 dk) | Bilinmiyor | Log okunmadı |
| 42 | 20260910-1512 | reviewing→error | 34754285697 (1 dk) | Bilinmiyor | Log okunmadı |
| 52, 53 | 20261010-1504, 20261013-1816 | selecting_hashtags→error | 38281528861, 38762962948 (1 dk) | edge-tts kırılması | Korelasyon: `bf20af7` sonrası düzeldi |
| 63 | 20261112-2021 | selecting_hashtags→error | 43633352748 (4 dk) | Bilinmiyor | Log okunmadı |
Not: State değiştirmeyen failure run'ları da var: 33825449116 (2026-09-04 01:21, 1 dk), 41253557732 (2026-10-31 23:41, 1 dk), 32771468476 (08-24), 32185019270/32182867284 (08-18), 31856027345 (08-15), 31215329758/31178120797/31153494892 (08-07), 31128270366 (08-06), 30938462473/30938757757/30939296221 (08-04). Nedenleri log okunmadan bilinmiyor.

## Tüm döngüler
| # | batch_id | trigger_date (İst.) | başlangıç (UTC) | son geçiş (UTC) | son durum | attempts | yol | seçilen konu |
|---|---|---|---|---|---|---|---|---|
| 1 | 20260804-1833 | 2026-08-04 | 2026-08-04 18:33 | 2026-08-04 18:33 | pending |  | pending |  |
| 2 | 20260804-1854 | 2026-08-04 | 2026-08-04 18:54 | 2026-08-04 19:06 | done | 1 | pending > reviewing > done | Honey never spoils |
| 3 | 20260804-1920 | 2026-08-04 | 2026-08-04 19:20 | 2026-08-04 19:20 | pending |  | pending |  |
| 4 | 20260804-1937 | 2026-08-04 | 2026-08-04 19:37 | 2026-08-04 19:47 | error | 1 | pending > selecting_hashtags > reviewing > error | Cleopatra's needle obelisk and its hidden time capsule |
| 5 | 20260804-2011 | 2026-08-04 | 2026-08-04 20:11 | 2026-08-04 20:25 | done | 1 | pending > selecting_hashtags > reviewing > done | Cleopatra's needle obelisk hidden time capsule |
| 6 | 20260804-2233 | 2026-08-05 | 2026-08-04 22:33 | 2026-08-05 05:54 | done | 1 | pending > selecting_hashtags > reviewing > done | Lobsters are biologically immortal |
| 7 | 20260805-1136 | 2026-08-05 | 2026-08-05 11:36 | 2026-08-05 11:46 | done | 1 | pending > selecting_hashtags > reviewing > done | The Voynich Manuscript unsolved mystery |
| 8 | 20260806-1342 | 2026-08-06 | 2026-08-06 13:42 | 2026-08-06 13:42 | pending |  | pending |  |
| 9 | 20260807-0456 | 2026-08-07 | 2026-08-07 04:56 | 2026-08-07 05:17 | done | 3 | pending > selecting_hashtags > reviewing > done | Cleopatra's needle obelisk hidden time capsule |
| 10 | 20260807-0546 | 2026-08-07 | 2026-08-07 05:46 | 2026-08-07 05:54 | error |  | pending > selecting_hashtags > error | The sun's light takes 100,000 years to escape the core |
| 11 | 20260807-0556 | 2026-08-07 | 2026-08-07 05:56 | 2026-08-07 06:04 | error |  | pending > selecting_hashtags > error | There is a place on Earth where two oceans meet but don't mix |
| 12 | 20260807-0617 | 2026-08-07 | 2026-08-07 06:17 | 2026-08-07 06:42 | done | 1 | pending > selecting_hashtags > reviewing > done | Vikings used sunstones to navigate |
| 13 | 20260807-1059 | 2026-08-07 | 2026-08-07 10:59 | 2026-08-07 11:45 | done | 1 | pending > selecting_hashtags > reviewing > done | Stomach growling has nothing to do with hunger |
| 14 | 20260807-1151 | 2026-08-07 | 2026-08-07 11:51 | 2026-08-07 12:03 | done | 1 | pending > selecting_hashtags > reviewing > done | There is a color the human eye cannot see — Stygian blue |
| 15 | 20260807-1206 | 2026-08-07 | 2026-08-07 12:06 | 2026-08-07 12:18 | done | 1 | pending > selecting_hashtags > reviewing > done | The Pacific Ocean is shrinking and the Atlantic is growing |
| 16 | 20260807-1222 | 2026-08-07 | 2026-08-07 12:22 | 2026-08-07 12:35 | done | 1 | pending > selecting_hashtags > reviewing > done | Honey never spoils — 3000-year-old edible honey found in Egyptian tombs |
| 17 | 20260807-1239 | 2026-08-07 | 2026-08-07 12:39 | 2026-08-07 13:11 | done | 1 | pending > selecting_hashtags > reviewing > done | The Antikythera mechanism — ancient analog computer |
| 18 | 20260808-1332 | 2026-08-08 | 2026-08-08 13:32 | 2026-08-09 09:50 | selecting_hashtags |  | pending > selecting_hashtags | Cleopatra's Needle and the hidden time capsule |
| 19 | 20260809-1013 | 2026-08-09 | 2026-08-09 10:13 | 2026-08-10 06:44 | done | 1 | pending > selecting_hashtags > reviewing > done | Cleopatra's death — the asp myth debunked |
| 20 | 20260810-1336 | 2026-08-10 | 2026-08-10 13:36 | 2026-08-11 09:42 | selecting_hashtags |  | pending > selecting_hashtags | Cleopatra's Needle and the hidden time capsule |
| 21 | 20260811-1332 | 2026-08-11 | 2026-08-11 13:32 | 2026-08-12 17:18 | error | 1 | pending > selecting_hashtags > reviewing > approved_pending_publish > error | Dünyanın en derin noktası — Mariana Çukuru hakkında bilinmeyenler |
| 22 | 20260812-1811 | 2026-08-12 | 2026-08-12 18:11 | 2026-08-13 17:11 | error | 1 | pending > selecting_hashtags > reviewing > approved_pending_publish > error | Okyanus'un karanlık bölgesi — güneş ışığının ulaşamadığı derinlik |
| 23 | 20260813-1717 | 2026-08-13 | 2026-08-13 17:17 | 2026-08-13 17:17 | pending |  | pending |  |
| 24 | 20260814-1131 | 2026-08-14 | 2026-08-14 11:31 | 2026-08-14 11:40 | error | 1 | pending > selecting_hashtags > reviewing > error | Filler Zıplayamaz |
| 25 | 20260814-1201 | 2026-08-14 | 2026-08-14 12:01 | 2026-08-14 12:14 | error | 1 | pending > selecting_hashtags > reviewing > error | Viking'lerin Kuzey Amerika'yı Keşfi |
| 26 | 20260814-1235 | 2026-08-14 | 2026-08-14 12:35 | 2026-08-14 12:45 | error | 1 | pending > selecting_hashtags > reviewing > error | Ay'da Ses Olmaması — Apollo Astronotlarının Duyduğu Titreşim |
| 27 | 20260814-1341 | 2026-08-14 | 2026-08-14 13:41 | 2026-08-17 02:52 | error | 1 | pending > selecting_hashtags > reviewing > error | Okyanus Oksijeni — Nefes Aldığımız Oksijenin Yarısı Ormandan Değil |
| 28 | 20260817-1350 | 2026-08-17 | 2026-08-17 13:50 | 2026-08-20 02:33 | error | 1 | pending > selecting_hashtags > reviewing > error | Oktopusların Üç Kalbi ve Mavi Kanı |
| 29 | 20260820-1336 | 2026-08-20 | 2026-08-20 13:36 | 2026-08-23 02:40 | error | 1 | pending > selecting_hashtags > reviewing > error | Kuzey Yıldızı'nın Sabit Olmadığı Gerçeği |
| 30 | 20260823-1350 | 2026-08-23 | 2026-08-23 13:50 | 2026-08-26 03:09 | error | 1 | pending > selecting_hashtags > reviewing > error | Ay'da Zaman Daha Yavaş Geçiyor — Relativite Etkisi |
| 31 | 20260826-1408 | 2026-08-26 | 2026-08-26 14:08 | 2026-08-29 13:27 | error | 1 | pending > selecting_hashtags > reviewing > error | Ay'da Depremler — Apollo Sismografları |
| 32 | 20260829-1509 | 2026-08-29 | 2026-08-29 15:09 | 2026-08-29 15:13 | error |  | pending > selecting_hashtags > error | A day on Venus is longer than its year |
| 33 | 20260829-1523 | 2026-08-29 | 2026-08-29 15:23 | 2026-08-29 15:32 | error | 1 | pending > selecting_hashtags > reviewing > error | The Great Wall of China is not visible from space |
| 34 | 20260829-1548 | 2026-08-29 | 2026-08-29 15:48 | 2026-08-29 16:06 | done | 1 | pending > selecting_hashtags > reviewing > done | Tardigrade survival — indestructible microscopic animal |
| 35 | 20260831-1152 | 2026-08-31 | 2026-08-31 11:52 | 2026-08-31 12:36 | done | 1 | pending > selecting_hashtags > reviewing > done | Rasputin's Impossible Death |
| 36 | 20260901-1535 | 2026-09-01 | 2026-09-01 15:35 | 2026-09-01 16:47 | done | 1 | pending > selecting_hashtags > reviewing > done | The Baader-Meinhof Phenomenon |
| 37 | 20260902-1403 | 2026-09-02 | 2026-09-02 14:03 | 2026-09-02 18:11 | error |  | pending > selecting_hashtags > error | The Eerie Silence of the WOW! Signal |
| 38 | 20260902-1813 | 2026-09-02 | 2026-09-02 18:13 | 2026-09-02 18:21 | done | 1 | pending > selecting_hashtags > reviewing > done | Trees Communicate and Warn Each Other — Wood Wide Web |
| 39 | 20260903-1342 | 2026-09-03 | 2026-09-03 13:42 | 2026-09-05 10:31 | done | 1 | pending > selecting_hashtags > reviewing > done | Castrato Singers — The Price of a Perfect Voice |
| 40 | 20260905-1330 | 2026-09-05 | 2026-09-05 13:30 | 2026-09-07 09:48 | done | 1 | pending > selecting_hashtags > reviewing > done | The Smell of Rain — Petrichor |
| 41 | 20260907-1511 | 2026-09-07 | 2026-09-07 15:11 | 2026-09-10 06:36 | done | 1 | pending > selecting_hashtags > reviewing > done | The Coldest Place in the Universe — Boomerang Nebula |
| 42 | 20260910-1512 | 2026-09-10 | 2026-09-10 15:12 | 2026-09-13 11:23 | error | 1 | pending > selecting_hashtags > reviewing > error | Lobsters Are Biologically Immortal — They Don't Age |
| 43 | 20260913-1458 | 2026-09-13 | 2026-09-13 14:58 | 2026-09-15 10:12 | done | 1 | pending > selecting_hashtags > reviewing > done | The Voronezh Alien Encounter — Soviet Government Confirmed UFO Landing |
| 44 | 20260915-1458 | 2026-09-15 | 2026-09-15 14:58 | 2026-09-18 06:28 | done | 1 | pending > selecting_hashtags > reviewing > done | The Judas Cradle — Torture Device That Was Never What You Think |
| 45 | 20260918-1507 | 2026-09-18 | 2026-09-18 15:07 | 2026-09-21 06:35 | done | 1 | pending > selecting_hashtags > reviewing > done | Coca-Cola Original Color |
| 46 | 20260921-1845 | 2026-09-21 | 2026-09-21 18:45 | 2026-09-24 11:08 | done | 1 | pending > selecting_hashtags > reviewing > done | The Great Molasses Flood of 1919 |
| 47 | 20260924-1549 | 2026-09-24 | 2026-09-24 15:49 | 2026-09-27 11:59 | done | 1 | pending > selecting_hashtags > reviewing > done | The Turk — Chess-Playing Automaton Hoax |
| 48 | 20260927-1624 | 2026-09-27 | 2026-09-27 16:24 | 2026-09-30 13:05 | done | 1 | pending > selecting_hashtags > reviewing > done | Tarrare — The Man Who Ate Everything |
| 49 | 20260930-1824 | 2026-09-30 | 2026-09-30 18:24 | 2026-10-03 13:03 | done | 1 | pending > selecting_hashtags > reviewing > done | The Baader-Meinhof Phenomenon — Why You See Things Everywhere After Learning About Them |
| 50 | 20261003-1708 | 2026-10-03 | 2026-10-03 17:08 | 2026-10-06 16:38 | done | 1 | pending > selecting_hashtags > reviewing > done | The Belmez Faces — Faces That Keep Appearing in a House Floor |
| 51 | 20261007-1343 | 2026-10-07 | 2026-10-07 13:43 | 2026-10-10 09:00 | done | 1 | pending > selecting_hashtags > reviewing > done | The Mary Celeste — Abandoned Ship Found Sailing Perfectly |
| 52 | 20261010-1504 | 2026-10-10 | 2026-10-10 15:04 | 2026-10-12 17:03 | error |  | pending > selecting_hashtags > error | The Hum — Mysterious Low Frequency Sound Heard Worldwide |
| 53 | 20261013-1816 | 2026-10-13 | 2026-10-13 18:16 | 2026-10-15 15:45 | error |  | pending > selecting_hashtags > error | The Man Who Never Slept — Fatal Familial Insomnia |
| 54 | 20261015-1850 | 2026-10-15 | 2026-10-15 18:50 | 2026-10-15 19:04 | done | 1 | pending > selecting_hashtags > reviewing > done | The Dyatlov Pass Incident |
| 55 | 20261016-1407 | 2026-10-16 | 2026-10-16 14:07 | 2026-10-18 16:24 | done | 1 | pending > selecting_hashtags > reviewing > done | The Blue Hole of Dahab — Divers' Graveyard |
| 56 | 20261018-1633 | 2026-10-18 | 2026-10-18 16:33 | 2026-10-21 15:23 | done | 1 | pending > selecting_hashtags > reviewing > done | The Radioactive Boy Scout — Teen Who Built a Nuclear Reactor in His Shed |
| 57 | 20261021-1924 | 2026-10-21 | 2026-10-21 19:24 | 2026-10-24 13:23 | done | 1 | pending > selecting_hashtags > reviewing > done | The Hiroo Onoda — Soldier Who Fought for 29 Years After WWII Ended |
| 58 | 20261024-1643 | 2026-10-24 | 2026-10-24 16:43 | 2026-10-27 12:46 | done | 1 | pending > selecting_hashtags > reviewing > done | The Cicada 13-Year and 17-Year Prime Number Emergence |
| 59 | 20261027-1847 | 2026-10-27 | 2026-10-27 18:47 | 2026-10-30 17:12 | done | 1 | pending > selecting_hashtags > reviewing > done | The Capgras Delusion — Loved Ones Replaced by Imposters |
| 60 | 20261031-1731 | 2026-10-31 | 2026-10-31 17:31 | 2026-11-03 17:20 | done | 1 | pending > selecting_hashtags > reviewing > done | The Antikythera Mechanism — Ancient Greek Computer |
| 61 | 20261104-1729 | 2026-11-04 | 2026-11-04 17:29 | 2026-11-07 19:07 | done | 1 | pending > selecting_hashtags > reviewing > done | The Gaviotas Experiment — Rainforest Grown From Scratch |
| 62 | 20261108-1455 | 2026-11-08 | 2026-11-08 14:55 | 2026-11-11 17:28 | done | 1 | pending > selecting_hashtags > reviewing > done | The Man Who Survived Two Atomic Bombs — Tsutomu Yamaguchi |
| 63 | 20261112-2021 | 2026-11-12 | 2026-11-12 20:21 | 2026-11-14 19:44 | error |  | pending > selecting_hashtags > error | The Baader-Meinhof Phenomenon — Frequency Illusion |
| 64 | 20261115-1650 | 2026-11-15 | 2026-11-15 16:50 | 2026-11-18 17:34 | done | 1 | pending > selecting_hashtags > reviewing > done | The Baychimo — Ghost Ship That Sailed Alone for 38 Years |
| 65 | 20261119-1332 | 2026-11-19 | 2026-11-19 13:32 | 2026-11-22 07:31 | done | 1 | pending > selecting_hashtags > reviewing > done | The Zip Code That Does Not Exist — 00000 |
| 66 | 20261122-1535 | 2026-11-22 | 2026-11-22 15:35 | 2026-11-22 15:35 | pending |  | pending |  |
