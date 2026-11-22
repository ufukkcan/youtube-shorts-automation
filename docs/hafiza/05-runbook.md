# 05 — Runbook (hazır komutlar ve senaryolar)

> Ortam: Windows PowerShell 5.1, çalışma dizini proje kökü. Bash aracını kullanma (fork hatası, L21).
> 🔒 = okuma dışı/dış sisteme etki eder → komut + gerekçe + etki sun, kullanıcı onayını bekle.

## 1. Oturum başı senkron (okuma)
```powershell
# Remote'u getir (yerel dosyalara dokunmaz)
git fetch origin
# Yerel ne kadar geride/ileride
git status -sb
# Remote'taki son 5 commit
git log origin/main -5 --format="%h %ad %an | %s" --date=iso
```
Yerel geride ve yerelde değişiklik yoksa güncelle (yalnız yerel klasör):
```powershell
git pull --ff-only
```

## 2. Botun anlık durumu (okuma)
```powershell
# Aktif döngünün özeti (remote'taki son hali)
$j = (git show origin/main:state/pending_topics.json) -join "`n" | ConvertFrom-Json; [pscustomobject]@{batch=$j.batch_id; trigger=$j.trigger_date; status=$j.status; created=$j.created_at; hashtag_started=$j.hashtag_started_at; review_started=$j.review_started_at; attempts=$j.attempts; topic=$j.candidate.topic} | Format-List
# Bekleyen 5 konunun teaser'ları
$j.candidates | ForEach-Object { $_.topic }
# Telegram offset en son ne zaman değişti (kullanıcı etkileşiminin son izi)
git log origin/main -1 --format="%ad" --date=iso -- state/telegram_offset.json
```

## 3. Actions sağlığı (okuma, anonim API 60/saat)
```powershell
$h = @{ 'User-Agent' = 'docs-audit-client'; 'Accept' = 'application/vnd.github+json' }
$base = "https://api.github.com/repos/ufukkcan/youtube-shorts-automation/actions"
# Son 10 çalışma
(Invoke-RestMethod -Headers $h -Uri "$base/workflows/check_and_produce.yml/runs?per_page=10").workflow_runs | ForEach-Object { "$($_.id) | $($_.created_at) | $($_.event) | $($_.conclusion)" }
# Başarısızlar
(Invoke-RestMethod -Headers $h -Uri "$base/workflows/check_and_produce.yml/runs?per_page=20&status=failure").workflow_runs | ForEach-Object { "$($_.id) | $($_.created_at)" }
# Bir run'da hangi adım düştü (RUN_ID değiştir)
(Invoke-RestMethod -Headers $h -Uri "$base/runs/RUN_ID/jobs").jobs.steps | Where-Object conclusion -eq 'failure' | Select-Object name
# Kalan limit
(Invoke-RestMethod -Headers $h -Uri "https://api.github.com/rate_limit").rate
```
Log içeriği API'den anonim indirilemez → tarayıcı: `https://github.com/ufukkcan/youtube-shorts-automation/actions/runs/RUN_ID` (kullanıcı bakar ve hata satırını paylaşır).

## 4. Üretim geçmişi tablosunu yeniden üret (okuma)
`docs/hafiza/uretim-gecmisi.md`'deki tablo şu komutla üretildi; yeni satırlar için çalıştır, çıktıyı tabloya ekle:
```powershell
$commits = git log --reverse --format="%h|%ad" --date=format:"%Y-%m-%d %H:%M" origin/main -- state/pending_topics.json; $b=[ordered]@{}
foreach ($c in $commits) { $h,$d=$c.Split('|'); $raw=git show "${h}:state/pending_topics.json" 2>$null; if(-not $raw){continue}; $j=($raw -join "`n")|ConvertFrom-Json; $id=$j.batch_id
  if(-not $b.Contains($id)){$b[$id]=[ordered]@{start=$d;trig=$j.trigger_date;status='';topic='';att='';end=$d;path=@()}}; $e=$b[$id]
  if($e.path.Count -eq 0 -or $e.path[-1] -ne $j.status){$e.path+=$j.status}; $e.status=$j.status; $e.end=$d; if($j.candidate){$e.topic=$j.candidate.topic}; if($j.attempts){$e.att=$j.attempts} }
$i=0; foreach($k in $b.Keys){$i++; $e=$b[$k]; "| $i | $k | $($e.trig) | $($e.start) | $($e.end) | $($e.status) | $($e.att) | $(($e.path) -join ' > ') | $($e.topic) |"}
```

## 5. Kod değişikliği öncesi kontrol (yerel)
```powershell
# Sözdizimi
python -m py_compile (Get-ChildItem src/*.py).FullName
# Değişiklik büyüklüğü (beklenmeyen silme var mı? L1)
git diff --stat
# Secret deseni taraması (değer basmadan sadece dosya:satır)
git diff | Select-String -Pattern '(sk-ant-|AIza|ya29\.|1//0|client_secret\s*=\s*"[^"B])' | ForEach-Object { "$($_.LineNumber)" }
```

## 6. Senaryolar

### 6.1 "Video gelmiyor / bot cevap vermiyor"
1. §1 + §2: status ve zamanlar. `created_at`/`*_started_at` + 20 saat geçmediyse beklemek normal.
2. §3: son run zamanı. Son run birkaç saatten eskiyse GitHub cron gecikmesi (L4). 🔒 Elle tetik: Actions → *Check Telegram selection and produce* → Run workflow.
3. Son run failure ise hangi adım (§3) → log satırını kullanıcıdan iste.

### 6.2 Üretim adımında hata (`selecting_hashtags → error` ya da `reviewing → error`)
- ~1 dk'da düşüyorsa önce edge-tts (L5): `pip index versions edge-tts` (yerel) → yeni sürüm varsa `requirements.txt` güncelle (🔒 push).
- `HTTP 413` / boyut → bitrate (L7).
- `invalid_grant` → YouTube refresh token (L16, §6.4).
- `quotaExceeded` → YouTube kotası; ertesi gün (Pasifik gece yarısı) sıfırlanır.
- Kurtarma: Telegram'dan `video uret` (yeni döngü) ya da 16:30 sonrası otomatik tetik (`error` aynı gün yeniden tetiklenir).

### 6.3 Döngü takıldı
Telegram'a `video uret` yaz. State dosyasını elle silme (L8).

### 6.4 YouTube refresh token yenileme 🔒 (kullanıcı yapar)
Yerel (tercih — token loga düşmez): `client_secret.json` (Desktop app) kökte → `pip install google-auth-oauthlib` → `python setup_oauth.py` → çıktıdaki 3 değeri GitHub Secrets'a gir → `client_secret.json`'ı sil. Ardından 1 elle run ile doğrula.

### 6.5 Yapılandırma değiştirme 🔒
`.github/workflows/check_and_produce.yml` env bloğu (42–56). Aynı commit'te README + `docs/kurgu.md` §9 güncelle (L18). `changelog.md` + `kararlar.md`'ye yaz.

## 7. Kullanıcının Telegram komutları
- `video uret` / `video üret` / `uret` / `üret` / `/uret` / `/video` / `/generate` → yeni 5 konu (her durumu sıfırlar).
- Butonlar: konu numarası → hashtag numaraları (5 adet, toggle) → "Onayla, yayinla" / "Begenmedim, tekrar uret".
