# Ustalık yol haritası

> Projede çalışılan her konu için dünya çapında uzmanlığa giden yol. Maddeler tamamlandıkça `[x]` + kanıt. "Az bilinen" (⚡) maddeler en iyi %1'in kullandığı, az paylaşılan teknikler/kaynaklardır. Projede uygulanmış olanlar "(projede: …)" ile işaretli.
> Kural: Bir maddeyi projeye uygulamak = kod değişikliği → önce todo + onay.

## 1. YouTube Shorts büyümesi ve algoritma
- [x] Açıklamaya `#Shorts` ekleme (projede: `pipeline.py:76`)
- [x] İlk 1–3 sn kanca, 65–85 kelime, merak açığı, twist/soru kapanışı (projede: `generate_script.py` SYSTEM_PROMPT)
- [ ] YouTube Analytics API ile video bazında "viewed vs swiped away" ve ortalama izlenme yüzdesi çekip prompt'a geri besleme
- [ ] ⚡ Döngüsel (loop) son: son cümlenin ilk cümleye bağlanması → tekrar izleme oranı; kapanış/açılış aynı görsel kare
- [ ] ⚡ Ses ölçümü: Shorts için entegre loudness ≈ -14 LUFS (`ffmpeg loudnorm` iki geçiş) — telefonda "kısık ses" kaybını önler
- [ ] ⚡ İlk karede metin: sesi kapalı izleyen için ilk kare "soru" metni (eskiden vardı, K14 ile kaldırıldı — A/B ile yeniden test)
- [ ] Yayın saati deneyi (20:00 sabit yerine analitiğe göre)
- Kaynaklar: YouTube Creator Insider kanalı, YouTube Help "Shorts discovery", Paddy Galloway vaka analizleri.

## 2. YouTube Data API, OAuth ve kota
- [x] Refresh token ile etkileşimsiz yükleme, resumable upload, `publishAt` (projede: `upload_youtube.py`)
- [ ] API projesi denetimi (audit) ve "unverified project → private kilidi" kuralını doğrula
- [ ] OAuth consent screen "In production" ve token ömrü kuralları
- [ ] ⚡ `videos.insert` sonrası `videos.list(part=status,processingDetails)` ile işleme/görünürlük doğrulaması
- [ ] ⚡ Kota tüketimini Cloud Monitoring'de alarm ile izleme
- Kaynaklar: developers.google.com/youtube/v3 (Quota calculator, Videos: insert), Google OAuth 2.0 for Installed Apps.

## 3. GitHub Actions güvenilirliği ve güvenliği
- [x] concurrency grubu, pip/apt cache, `if: always()` state push (projede: `check_and_produce.yml`)
- [ ] ⚡ Cron yerine dış zamanlayıcı → `workflow_dispatch`/`repository_dispatch` (GitHub schedule'ı yük altında düşürür; ölçülen ≈11/gün)
- [ ] ⚡ `::add-mask::` ile çalışma anında üretilen secret'ları maskeleme
- [ ] Secret scanning + push protection (public repoda ücretsiz)
- [ ] ⚡ Action'ları commit SHA ile sabitleme (supply-chain), `permissions:` en az yetki
- [ ] ⚡ `gitleaks` ile tüm geçmişi tarama; ifşa olan secret için önce iptal, sonra `git filter-repo`
- Kaynaklar: docs.github.com Actions "Events that trigger workflows → schedule" notları, "Security hardening for GitHub Actions", OpenSSF Scorecard.

## 4. ffmpeg / libass video üretimi
- [x] concat demuxer için normalize (aynı codec/fps/çözünürlük), hedef boyutlu bitrate, filter_complex overlay + `eval=frame` animasyon (projede: `assemble_video.py`)
- [ ] ⚡ ASS formatı ile kelime kelime vurgulu (karaoke `\k`) altyazı — Shorts'ta tutma oranını artıran yaygın stil; whisper kelime zamanları zaten var
- [ ] ⚡ `PlayResX/PlayResY`'yi 1080x1920 ayarlayıp MarginV'yi piksel hassasiyetinde kontrol (L10'daki ölçek sorunu)
- [ ] İki geçişli (2-pass) x264 ile sabit boyutta daha iyi kalite
- [ ] Ken Burns / hafif zoom ile statik kliplerde hareket
- Kaynaklar: ffmpeg-filters dokümanı, libass ASS spec (Aegisub belgeleri).

## 5. TTS ve ses
- [x] edge-tts ses/hız ayarı (projede)
- [ ] ⚡ SSML benzeri vurgu/duraklama (edge-tts `rate`/`pitch`, cümle bazında parçalı sentez)
- [ ] edge-tts kırılmalarına karşı yedek TTS (ör. Piper yerel model) — onaya bağlı
- Kaynak: edge-tts GitHub issues (servis değişiklikleri ilk orada görünür).

## 6. LLM ile içerik üretimi
- [x] JSON şema talimatı + kod bloğu temizleme (projede: `_call_claude`)
- [ ] ⚡ Tool use / structured output ile şema garantili JSON (parse hatalarını sıfırlar)
- [ ] ⚡ Doğruluk kontrolü: üretilen "gerçek"i ikinci bir çağrıyla iddia-kanıt listesine ayırıp riskli iddiaları elemek (yanlış bilgi = kanal riski)
- [ ] Konu tekrarını embedding/normalize anahtar ile önleme (L17)
- [ ] Prompt caching ile sabit sistem prompt maliyetini düşürme
- [ ] Model sürümünü güncel tutma (şu an `claude-sonnet-4-6`)
- Kaynak: Anthropic docs (tool use, prompt caching, prompt engineering).

## 7. Telegram Bot API
- [x] Inline keyboard, callback_data ile batch bazlı eşleme, chat_id filtresi (projede)
- [ ] ⚡ Webhook → küçük serverless köprü (Cloudflare Worker) → `repository_dispatch`: tıklamaya saniyeler içinde tepki (bugün ≈2 saat)
- [ ] Offset'i işleme sonrası kaydetme (at-least-once)
- Kaynak: core.telegram.org/bots/api.

## 8. Python işletim güvenilirliği
- [ ] Yeniden deneme (retry + backoff) dış API çağrılarında
- [ ] Hata mesajlarını Telegram'a kısaltılmış + run linkiyle gönderme
- [ ] `py_compile` + basit birim testleri (durum makinesi geçişleri) CI'da
