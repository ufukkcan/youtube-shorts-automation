# CLAUDE.md — youtube-shorts-automation

## Proje
Telegram onaylı, GitHub Actions üzerinde çalışan, İngilizce "ilginç bilgi" **YouTube Shorts** üretim ve yükleme hattı ("interesthings"). Konu üret → seçtir → hashtag seçtir → video üret → onaylat → YouTube'a zamanlanmış yükle. **Kapsam yalnızca YouTube; TikTok kapsam dışıdır.**
Proje klasörü: `C:\Users\mc061965\Documents\projeler\youtube-shorts-automation`
Repo: `https://github.com/ufukkcan/youtube-shorts-automation` (public, `main`)

## Oturum başı
1. Bu dosyayı oku ve uygula.
2. Oturum başında MUTLAKA oku:
   - `docs/hafiza/01-ozet.md` (tek sayfa bağlam)
   - `docs/hafiza/02-sistemler-durum.md` (sistemler ve anlık durum)
   - `docs/lessons.md` (hatalar ve kurallar)
   - `todo.md` (yalnızca açık `[ ]` maddeler ve İnceleme'nin son kaydı)
3. Ardından `git fetch origin` + `git status -sb` ile yerelin remote'a göre durumunu kontrol et (bot her gün state push eder; yerel geride olabilir).
4. Diğer dosyaları yalnızca gerektiğinde oku:
   - `docs/hafiza/03-entegrasyonlar-kimlik.md` — secret adları, uç noktalar, callback biçimleri
   - `docs/hafiza/04-dosya-haritasi.md` — fonksiyon/satır yerleri (dosyayı baştan okumadan önce buraya bak)
   - `docs/hafiza/05-runbook.md` — hazır komutlar ve arıza senaryoları
   - `docs/kurgu.md` — sistemin tam tasarımı
   - `docs/proje-plani.md` — fazlar ve neredeyiz
   - `docs/changelog.md`, `docs/hafiza/uretim-gecmisi.md`, `docs/hafiza/kararlar.md`, `docs/hafiza/islem-gunlugu.md`, `docs/hafiza/roadmap.md`

## Genel talimatlar
1. **Token tasarrufu:** Kısa ve net yaz; ne yaptığını/ne yapılacağını söyle, istenmedikçe detay verme. Övgü/güzelleme yok. Dosyayı baştan okumadan önce `04-dosya-haritasi.md`'den satır aralığını bul, sadece o aralığı oku. `state/topics_used.json` ve git geçmişini tamamen okuma; runbook komutlarını kullan.
2. **Varsayım yok:** Doğrulanmış/doğrulanabilir yöntemler kullan. Bilmediğin, anlamadığın, bulamadığın şeyi sor, birlikte karar verelim. Çıkarımları "korelasyon"/"doğrulanmadı" diye etiketle.
3. **Yetki:** Yazma yetkisi yalnızca proje klasöründe. GitHub (push, workflow tetikleme, secret/ayar), Telegram, YouTube/Google, Anthropic, Pexels ve diğer dış sistemlerde yalnızca okuma. Okuma dışı her işlemde **komut + gerekçe + etki** sun, onayımı bekle. `git fetch` okuma sayılır; `git pull --ff-only` yalnız yerel klasörü değiştirir (izinli); `git commit`/`git push` onay ister.
4. **Komut ortamı:** Yerel komutları PowerShell aracıyla çalıştır (Windows PowerShell 5.1). Bash aracı bu makinede fork hatası veriyor (L21). İç ağ gerekmiyor; Desktop Commander gerekmez. GitHub okuma: anonim API 60 istek/saat (L23); `gh` kurulu değil.
5. **Secret:** Secret değeri (token, API key, client secret, refresh token, auth code) hiçbir dosyaya, commit'e, loga yazılmaz. Secret adı, saklama yeri, kullanıcı adı, URL, run/commit id ve tarih yazılır. Public repoda geçmişte açık secret var (L14) — benzerini asla üretme.
6. **Ustalık yol haritası:** Çalışılan her konu için `docs/hafiza/roadmap.md`'yi güncel tut; md dosyalarındaki maddeler tamamlandıkça işaretle.
7. En iyi %1'in kullandığı az paylaşılan teknikleri, gizli kaynakları ve alışılmadık yaklaşımları dahil et (roadmap'te ⚡).
8. **Döngü engeli:** Bir sorun en fazla 3 denemede çözülmezse dur, denenenleri bildir, birlikte karar verelim.
9. **Kendini geliştirme:** Her düzeltmemden sonra `docs/lessons.md`'ye örüntüyü ve aynı hatayı önleyecek kuralı yaz. Oturum başında lessons'ı gözden geçir.
10. **Bitti demeden kanıt:** Çalıştığını kanıtlamadan tamamlandı işaretleme. Bu projede kanıt: `python -m py_compile`, ilgili Actions run'ının yeşil olması ve beklenen state geçişi (`git show origin/main:state/pending_topics.json`), gerekirse Telegram/YouTube'da kullanıcının gördüğü sonuç. Önce/sonra karşılaştır. "Kıdemli bir mühendis bunu onaylar mı?" diye sor.
11. **Dengeli zarafet:** Önemsiz olmayan değişikliklerde daha zarif bir yol var mı diye düşün. Çözüm yamalı duruyorsa doğru çözümü uygula. Basit işlerde aşırı mühendislik yapma. Sunmadan önce kendi işini sorgula.
12. **Otonom hata düzeltme:** Hata bildirildiğinde log/çıktı/state geçmişinden kök nedeni bul ve proje klasöründe düzelt; elden tutulmayı bekleme. Düzeltmenin canlıya gitmesi (push) madde 3'teki onaya tabi. Başarısız Actions run'larını önce jobs API ile hangi adımda düştüğünü bularak teşhis et; log içeriğini kullanıcıdan iste (anonim indirilemez).
13. Aşırı mühendislik yok, istenmeyen özellik yok.
14. **Tembellik yok:** Kök nedeni bul, geçici çözüm yok. Script sonucuna güvenme, her çalıştırmadan sonra çıktıyı kontrol et. Yönlendirilmedikçe örnek/kısmi veriyle değil tüm veriyle çalış. Ama hepsini birden okuma: gerekeni oku, karar için yetmezse daha fazlasını oku.
15. **Minimum etki:** Yalnızca gerekene dokun, yan etki yaratma. Canlı bot `state/` dosyalarını sürekli değiştiriyor: yerelde `state/` değişikliği commit etme, elle silme/düzenleme (L8).
16. Soru sorduğumda yalnızca düzyazı cevap ver. Komut vereceksen bağımsız komutları tek blokta, her birinin üstünde tek satır açıklamayla ver.

## Projeye özel kurallar
- Yapılandırma değişikliği (`check_and_produce.yml` env) = README + `docs/kurgu.md` §9 + changelog + kararlar aynı anda güncellenir (L18).
- Kod + kullandığı asset aynı commit'te (L11). Push öncesi `git diff --stat` ile beklenmedik silme kontrolü (L1).
- `ufukkcan/tiktok-legal-pages` reposu silinmez: YouTube OAuth redirect URI'si onun `callback.html`'ini kullanır (K17).
- Takılan döngü için çözüm Telegram'dan `video uret`; state dosyası silinmez.
- Bot dili Türkçe, içerik İngilizce (K1).

## Görev yönetimi
1. **Önce plan:** Planı `todo.md`'ye işaretlenebilir maddelerle yaz.
2. **Planı onaylat:** Uygulamaya başlamadan bana danış.
3. **İlerlemeyi işle:** Maddeleri bittikçe `[x]` + kanıt ile işaretle.
4. **Sonucu belgele:** `todo.md` → "İnceleme" bölümüne sonucu ve kanıtı yaz.
5. **Dersleri yakala:** Düzeltmelerden sonra `docs/lessons.md`'yi güncelle.
6. **Changelog:** Her geliştirme, iyileştirme, sürüm değişikliği ve önemli bulgudan sonra `docs/changelog.md`'ye ne yapıldığını ve nasıl çalıştığını yaz; commit hash, run id, secret adı, URL ve tarihi ekle (secret değeri hariç).
7. **Günlük ve kararlar:** Sistemlere yapılan her işlemi `docs/hafiza/islem-gunlugu.md`'ye, kararları `docs/hafiza/kararlar.md`'ye tarihli yaz.
8. **Durum:** Bir sistemin durumu değişince `docs/hafiza/02-sistemler-durum.md`'deki satırı ve "Son kontrol" tarihini güncelle; yeni döngü sonuçlarını gerekirse `uretim-gecmisi.md`'ye ekle (runbook §4).
9. Satır numaraları değişen kod değişikliğinden sonra `docs/hafiza/04-dosya-haritasi.md`'yi güncelle.
