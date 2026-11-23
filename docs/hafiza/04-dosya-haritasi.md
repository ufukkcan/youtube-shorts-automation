# 04 — Dosya haritası (dosyayı tamamen okumadan doğru satıra git)

> Satır numaraları `0d34b2c` (2026-11-22) itibarıyla. Kod değişince güncelle. Token tasarrufu: önce burada yeri bul, `Read` ile sadece o aralığı oku (`offset`/`limit`).

## Kök
| Dosya | İçerik |
|---|---|
| `CLAUDE.md` | Claude talimatları, oturum başı okuma listesi |
| `todo.md` | Tüm işler (yapıldı/yapılacak) + İnceleme |
| `README.md` | Kullanıcı kurulum rehberi (**eski**: 20:00/10 dk yazıyor) |
| `requirements.txt` | anthropic 0.40.0, edge-tts 7.3.1, faster-whisper 1.0.3, requests 2.32.3, google-api-python-client 2.149.0, google-auth 2.35.0, google-auth-oauthlib 1.2.1 |
| `setup_oauth.py` | Yerel YouTube refresh token alma (client_secret.json gerekir) |
| `.gitignore` | `__pycache__/ *.pyc .env client_secret.json test/ *.mp4 *.mp3 *.srt` |
| `assets/` | `follow_button.png` (4425 B, kullanılıyor), `tap_ring.png` (1930 B, kullanılıyor), `subscribe_button.png` (6763 B, **kullanılmıyor**) |
| `state/` | Bot durumu — elle düzenleme |

## src/check_and_produce.py (282 satır) — durum makinesi
| Satır | Öğe |
|---|---|
| 1–21 | Docstring: 4 aşama |
| 44–51 | Sabitler: PENDING_FILE, OFFSET_FILE, FALLBACK_HOURS, MAX_REDO_ATTEMPTS, N_HASHTAGS_TO_PICK=5, AUTO_TRIGGER_TIME, ISTANBUL |
| 54 | `run()` — manuel tetik (61–65), aktif döngü dağıtımı (67–77), otomatik tetik (81–88) |
| 91 | `_handle_topic_selection` — fallback: ilk konu |
| 111 | `_start_hashtag_selection` |
| 124 | `_clean_hashtag_candidates` — alfanumerik, tekrar yok, ≤10 |
| 137 | `_handle_hashtag_selection` — toggle, fallback tamamlama, açıklama = topic + hashtag'ler (166) |
| 187 | `_handle_review_decision` — redo sınırı, timeout, approve |
| 223 | `_produce_and_send_for_review` — attempts sayacı (234) |
| 238 | `_produce_and_upload` — yeniden üret + YouTube + done/error |
| 257 | `_fetch_updates` — offset işlemeden önce kaydedilir |
| 265/270/276 | `_hours_since`, `_load_json`, `_save_json` |

## src/telegram_bot.py (237)
| Satır | Öğe |
|---|---|
| 11–13 | BOT_TOKEN, CHAT_ID, API_BASE |
| 16 | `send_topic_options` (5 buton tek satır) |
| 41 / 49 / 53 | `edit_message`, `send_message`, `answer_callback_query` (hata kontrolü yok) |
| 61 | `get_updates(offset)` timeout 5 |
| 71 | `send_video_for_review` (caption ≤1024, timeout 180) |
| 99 | `download_review_video` — **kullanılmıyor** |
| 113 | `find_review_decision` |
| 133 | `find_manual_trigger` (tetik ifadeleri 137) |
| 150 / 167 | `send_hashtag_options`, `update_hashtag_message` |
| 181 / 189 | `_hashtag_message_text`, `_hashtag_keyboard` (2 sütun) |
| 201 | `find_hashtag_toggles` |
| 222 | `find_selection` |

## src/generate_script.py (137)
| Satır | Öğe |
|---|---|
| 12–13 | STATE_FILE, LANGUAGE |
| 15–60 | SYSTEM_PROMPT (viral kurallar, tempo 40–55 kelime, döngü kapanış, DİL KURALI) |
| 62–70 | CANDIDATE_SCHEMA |
| 72–86 | USER_PROMPT_TEMPLATE |
| 89 / 95 | `load_used_topics`, `save_used_topics` (son 300) |
| 103 | `_call_claude` — model (115); state'e yazmaz (preview.py bunu kullanır) |
| 126 | `generate_topic_candidates` (topics_used'a yazar) |
| 134 | `generate_daily_content` (main.py için) |

## src/pipeline.py (107)
| Satır | Öğe |
|---|---|
| 19–23 | LANGUAGE, PRIVACY_STATUS, PUBLISH_TIME_ISTANBUL |
| 26 | `next_publish_at_utc` |
| 37 | `produce_video` (4 adım; kancayı montaja verir) |
| 64 | `_extract_hook` (script'in ilk cümlesi) |
| 74 | `upload_video` (#Shorts ekleme) |
| 100 | `produce_and_upload` (tam otomatik) |

## src/assemble_video.py (217)
| Satır | Öğe |
|---|---|
| 15–36 | Boyut, SEGMENT_SECONDS=2.5, HOOK_* (süre 2.5, 64 px, 20 karakter, y=560), bitrate, font, asset yolları, buton/halka/CTA zamanlamaları |
| 39 | `assemble` — concat (57), subtitle_style (70), kanca drawtext (83–94), filter_complex (115), son ffmpeg (128) |
| 147 | `_esc` |
| 152 | `_compute_video_bitrate_kbps` |
| 160 | `_normalize_clips` — 2,5 sn parçalar, klipler sırayla, `-stream_loop` |
| 193 | `_probe_duration` (ffprobe) |

## Diğer src
| Dosya | Satır |
|---|---|
| `suggest_topics.py` (65) | `run(force)` 22, günde-1 kontrolü 30, batch_id 35, pending yazımı 40–54 |
| `generate_voice.py` (42) | VOICE 13, RATE 14, `generate_voice` 22, `_get_duration` (ffprobe) 28 |
| `fetch_visuals.py` (83) | MIN_CLIPS=4 14, MAX_FILE_WIDTH=1080 15, `fetch_clips` 18, `_search_one_clip` (id hariç tutma) 47, `_download` 72 |
| `preview.py` (60) | Önizleme: 1 aday (state'e yazmaz) → video → Telegram "ONIZLEME"; `main` 20 |
| `generate_captions.py` (47) | WORDS_PER_CHUNK 9, MODEL_SIZE 10, `generate_srt` 20 |
| `upload_youtube.py` (79) | SCOPES 13, `_get_credentials` 16, `upload_short` 27 |
| `main.py` (18) | Onaysız tam otomatik mod |
| `yt_oauth_exchange.py` (40) | REDIRECT_URI 13, token loga basılır |

## .github/workflows
| Dosya | Önemli satırlar |
|---|---|
| `check_and_produce.yml` | cron (6), concurrency (9–11), timeout 30 dk, apt cache, env (42–56), run (57), state push `if: always()` |
| `suggest_topics.yml` | sadece workflow_dispatch |
| `yt_oauth_exchange.yml` | input `code` |
| `preview.yml` | Elle; seçilen branch'in koduyla `src/preview.py`; `permissions: contents: read`, state commit yok |

TikTok dosyaları (4 `src/tiktok_*.py`, 3 `tiktok_*.yml`) 2026-11-22'de silindi; geçmişteki içerikleri için `git log --all -- src/tiktok_upload.py`.

## Okunmaması gerekenler (token israfı)
- `state/topics_used.json` (17 KB) — sayı/son kayıt için PowerShell ile `ConvertFrom-Json` kullan.
- `state/pending_topics.json` tamamı — gerekli alanları runbook komutuyla çek.
- Tüm commit geçmişi — özet `docs/changelog.md` ve `docs/hafiza/uretim-gecmisi.md`'de.
