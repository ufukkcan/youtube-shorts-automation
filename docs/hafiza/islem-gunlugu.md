# İşlem günlüğü — sistemlere yapılan işlemler

> Her dış sistem işlemini (okuma dahil önemli olanlar, tüm yazma/tetiklemeler) tarihli yaz: **Tarih (UTC) · Kim · Sistem · İşlem · Tür (okuma/yazma) · Sonuç · Referans**. Secret değeri yazma.
> 2026-11-22 öncesi kayıtlar GitHub Actions API'deki `workflow_dispatch` (elle tetik) run'larından geriye dönük çıkarıldı; zamanlanmış (schedule) run'lar burada listelenmez.

## Geriye dönük (elle yapılan işlemler)

| Tarih (UTC) | Kim | Sistem | İşlem | Tür | Sonuç | Referans |
|---|---|---|---|---|---|---|
| 2026-08-04 17:16 | ufukkcan | GitHub | Repo oluşturuldu (public) | yazma | — | repo created_at |
| 2026-08-04 18:24–18:35 | ufukkcan | Actions check_and_produce | 3 elle tetik | yazma | failure ×3 | 30938462473, 30938757757, 30939296221 |
| 2026-08-04 18:51–19:54 | ufukkcan | GitHub | `state/pending_topics.json` elle silindi ×3 | yazma | döngü sıfırlandı | `c4134f3`, `4c75f2a`, `d743c37` |
| 2026-08-06 21:23 | ufukkcan | Actions check_and_produce | Elle tetik | yazma | failure | 31128270366 |
| 2026-08-07 05:48, 05:59 | ufukkcan | Actions check_and_produce | Elle tetik | yazma | failure ×2 | 31151824155, 31152387581 |
| 2026-08-11 13:20–13:27 | ufukkcan | Actions tiktok_oauth_exchange | 3 elle run (TikTok token) | yazma | success (token loga basıldı) | 31495693681, 31495884213, 31496255429 |
| 2026-08-13 17:07 | ufukkcan | Actions check_and_produce | Elle tetik | yazma | failure | 31724142695 |
| 2026-08-14 11:37–12:42 | ufukkcan | Actions check_and_produce | Elle tetik ×3 | yazma | failure ×3 | 31796963608, 31799177982, 31801466820 |
| 2026-08-14 11:45, 11:57 | ufukkcan | Actions tiktok_refresh_test | 2 run | okuma (TikTok token) | success | 31797522666, 31798297025 |
| 2026-08-14 12:18–12:52 | ufukkcan | Actions tiktok_init_test | 3 run | okuma | success | 31799751218, 31801998363, 31802153995 |
| 2026-08-14 12:31 | ufukkcan | Actions tiktok_oauth_exchange | 1 run | yazma | success | 31800716091 |
| 2026-08-29 15:28 | ufukkcan | Actions check_and_produce | Elle tetik | yazma | failure | 33260358601 |
| 2026-08-29 15:45 | ufukkcan | Actions yt_oauth_exchange | YouTube auth code → refresh token | yazma | success (token loga basılmış olabilir) | 33261095531 |
| 2026-08-29 ~15:45–16:00 | ufukkcan | GitHub Secrets | `YT_REFRESH_TOKEN` güncellendi (korelasyon) | yazma | sonraki döngü done | — |
| 2026-09-02 18:05 | ufukkcan | Actions check_and_produce | Elle tetik | yazma | failure | 33665069160 |
| 2026-10-18 16:24 | ufukkcan | Telegram bot | Son kullanıcı etkileşimi (offset son değişim) | — | — | `e6148f2` |

## 2026-11-22 — Claude oturumu (dokümantasyon)

| Tarih (UTC) | Kim | Sistem | İşlem | Tür | Sonuç |
|---|---|---|---|---|---|
| 2026-11-22 | Claude | Yerel repo | Dosya/geçmiş okuma, diff'ler scratchpad'e | okuma | — |
| 2026-11-22 | Claude | GitHub (git) | `git fetch origin` | okuma (yalnız remote ref'leri) | 18 yeni state commit görüldü, pull yapılmadı |
| 2026-11-22 | Claude | GitHub API (anonim) | repo, workflows, runs, jobs, tiktok-legal-pages sorguları (~45 istek) | okuma | Rate limit doldu (60/saat) |
| 2026-11-22 | Claude | Yerel proje klasörü | `CLAUDE.md`, `todo.md`, `docs/*`, `docs/hafiza/*` oluşturuldu | yazma (yalnız proje klasörü) | commit/push yapılmadı |
| 2026-11-22 | Claude | Claude hafıza klasörü | Kullanıcı profili + proje işaretçisi | yazma (yerel) | — |
