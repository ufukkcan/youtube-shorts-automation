# interesthings — Telegram'dan konu seçimli + video onaylı YouTube Shorts hattı

Kanal dili: **İngilizce** (script, seslendirme, altyazı, başlık/açıklama hep İngilizce
üretilir). Bot ile aranızdaki Telegram yazışmaları Türkçe kalır — o sadece senin
kontrol panelin.

## Akış

1. **Manuel tetikleme:** Gün içinde istediğin an bota (Telegram'dan) düz metin
   olarak **"video üret"** yaz (ya da `/uret`, `/video`). Bot hemen o an 5 konu
   üretip sana gönderir — saat kaç olursa olsun beklemez.
2. **Sen tetiklemezsen:** Sistem kendiliğinden, her gün saat **20:00 İstanbul
   saatinde** (`AUTO_TRIGGER_TIME`) 5 konuyu kendisi üretip Telegram'a gönderir.
   Yani gün boyunca hiçbir şey yapmasan bile döngü mutlaka başlar.
3. Bir numaraya dokunursun.
4. Bot o konuyla **videoyu üretir ama YouTube'a yüklemez** — önce videonun kendisini
   Telegram'a "Onayla" / "Beğenmedim, tekrar üret" butonlarıyla gönderir.
5. **Onayla** dersen → video 'private' olarak yüklenir ve YouTube'un kendi
   zamanlanmış yayın özelliğiyle **her gün saat 20:00 İstanbul saatinde**
   (`PUBLISH_TIME_ISTANBUL`, ayrı bir ayar) otomatik olarak herkese açık hale gelir
   (onay saatinden bağımsız).
6. **Beğenmedim** dersen → aynı konuyla video yeniden üretilir (yeni seslendirme +
   yeni stok görsel), tekrar onayına sunulur. Bu, sen onaylayana kadar döner.
7. Güvenlik ağı: **20 saat** boyunca hiç yanıt vermezsen (ne konu seçiminde ne
   onayda), bot otomatik ilerler. Ayrıca art arda **5 kez** "tekrar üret"
   dersen bot son versiyonu otomatik onaylayıp yükler (sonsuz döngüye girmesin diye).
8. Bir gün için döngü bir kere başladıysa (manuel ya da otomatik), o gün için
   ikinci bir döngü açılmaz.

**İki farklı "20:00" var, birbirine karıştırma:**
- `AUTO_TRIGGER_TIME` = sen "video üret" demezsen, konu üretim SÜRECİNİN
  kendiliğinden BAŞLAYACAĞI saat.
- `PUBLISH_TIME_ISTANBUL` = onayladığın videonun YouTube'da CANLIYA GEÇECEĞİ saat.

İkisi de varsayılan olarak 20:00 ama tamamen bağımsız ayarlar. Not: hiç
etkileşime girmeden tam otomatik pilota bırakırsan (ne seçim ne onay yaparsan),
20:00'de başlayan süreç + 20 saatlik bekleme yüzünden o günkü yayın saatini
kaçırıp bir sonraki güne kayabilir — bu yalnızca "hiç dokunmama" senaryosunda
olur, normal kullanımda (birkaç saat içinde seçim/onay) sorun çıkarmaz.

Tüm bunlar GitHub Actions üzerinde, bilgisayarın kapalıyken bile çalışır.

## Maliyet
Claude API çağrıları (konu üretimi + her "tekrar üret" başka bir seslendirme/görsel
çekme turu demek, dolayısıyla çok tekrar üretme istemek biraz daha API kullanımı
demek — yine de günde birkaç kuruş - birkaç lira aralığında kalır). Geri kalanı
(Telegram, edge-tts, Pexels, faster-whisper, GitHub Actions, YouTube API) ücretsiz.

## Kurulum (tek seferlik)

### 1. Repoyu kendi GitHub hesabına al

### 2. Telegram bot oluştur
1. **@BotFather**'a `/newbot` yaz, bot adını belirle, **token**'ı al (`TELEGRAM_BOT_TOKEN`)
2. Botuna bir mesaj at (örn. "merhaba")
3. Tarayıcıda `https://api.telegram.org/bot<TOKEN>/getUpdates` adresine git,
   dönen JSON'daki `"chat":{"id": ...}` değeri senin `TELEGRAM_CHAT_ID`'n

### 3. API anahtarları
- **Anthropic**: https://console.anthropic.com/settings/keys
- **Pexels**: https://www.pexels.com/api/

### 4. YouTube OAuth izni (kendi bilgisayarında, tek seferlik)
1. https://console.cloud.google.com → yeni proje → **YouTube Data API v3**'ü etkinleştir
2. **OAuth client ID** oluştur (Desktop app), `client_secret.json` olarak indir
3. `pip install google-auth-oauthlib` → `python setup_oauth.py`
4. Kanalın bağlı olduğu Google hesabıyla tarayıcıda giriş yap
5. Çıkan `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` değerlerini not al

> Bunu Claude senin adına yapamaz — kendi Google hesabınla onay vermen gerekiyor.

### 5. GitHub Secrets ekle
**Settings > Secrets and variables > Actions**:
- `ANTHROPIC_API_KEY`, `PEXELS_API_KEY`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`

### 6. İlk testi yap
Telegram'da bota **"video üret"** yaz → 5 konu gelmeli (ilk denemede Actions
sekmesinden **Check Telegram selection and produce**'u elle çalıştırman gerekir,
sonrasında zaten 10 dakikada bir otomatik çalışıyor). Birini seç, video Telegram'a
düşünce onayla veya tekrar üret de.

İlk denemelerde `check_and_produce.yml` içindeki `PRIVACY_STATUS`'u `"private"`
yaparsan, videoyu gerçekten yayına almadan kanalında test edebilirsin.

## Workflow'lar

| Dosya | Ne zaman | Görevi |
|---|---|---|
| `check_and_produce.yml` | Her 10 dakikada bir | **Ana motor.** Manuel "video üret" mesajını veya otomatik saati kontrol eder, döngüyü başlatır; konu seçimi → video üretir → onaya sunar; onaylanınca yükler; reddedilirse yeniden üretir |
| `suggest_topics.yml` | Sadece elle (`workflow_dispatch`) | Test/yedek amaçlı — Actions sekmesinden elle bir döngü zorlamak istersen |

Not: bekleyen bir iş yoksa (ve ne manuel istek ne otomatik saat gelmediyse)
`check_and_produce.yml` saniyeler içinde biter, Actions kotasını neredeyse hiç harcamaz.

## Telegram video boyutu hakkında
Bot API ile video gönderiminde ~50 MB sınırı var. 30-45 saniyelik bir shorts
(1080x1920, standart bitrate) tipik olarak 5-15 MB civarında olur, bu yüzden
sorun yaşamazsın. Çok daha uzun videolara geçersen bu sınırı aşabilirsin.

## Zamanlanmış yayın (20:00 İstanbul)
`PUBLISH_TIME_ISTANBUL` (varsayılan `"20:00"`) ayarı sayesinde onayladığın video
hemen değil, YouTube'un kendi zamanlanmış yayın mekanizmasıyla her gün tam o
saatte otomatik olarak herkese açık olur. Sen videoyu sabah da onaylasan, gece
onaylasan fark etmez — YouTube kanalında "Scheduled" (zamanlanmış) olarak durur,
saat gelince kendiliğinden yayına girer. Kapatmak istersen bu değeri `"off"` yap;
o zaman video onaylanır onaylanmaz hemen (`PRIVACY_STATUS` neyse o şekilde) yayınlanır.

**Neden 20:00 İstanbul?** ABD (Doğu/Batı yakası) ve Avrupa'nın aktif kullanım
saatlerine en dengeli denk gelen aralıklardan biri — ABD öğle/erken öğleden
sonrasına, Avrupa'nın akşama yaklaştığı saate denk düşüyor. Tam "prime time"
her iki kıtada birden yakalanamıyor (saat farkı çok büyük) ama bu saat ikisini
de ölü saatlerden kurtarıyor.

## Etiketler ve "Keşfet"e düşme
Sistem zaten her video için konuya özel, otomatik üretilmiş etiketler ve
hashtag'ler ekliyor — bunlar generic ("shorts", "viral" gibi) değil, o günün
konusuna göre Claude'un ürettiği spesifik kelimeler (`src/generate_script.py`
içindeki `tags` alanı → YouTube'un `snippet.tags`'ine gidiyor; `video_description`
alanının sonuna da 5-8 ilgili hashtag ekleniyor).

Bunu söylemem gerekiyor: etiket/hashtag'ler **Keşfet'e düşmeyi garanti etmez**.
YouTube'un Shorts algoritması asıl olarak izlenme süresi (videoyu sonuna kadar
izleme oranı), ilk 1-2 saniyedeki tutma oranı ve etkileşime (beğeni/yorum/paylaşım)
bakıyor — etiketler bu sinyallerin üstüne "doğru kitleye gösterme" için yardımcı
oluyor, ama zayıf bir video etiketle öne çıkmıyor. Script'teki güçlü "kanca"
(ilk cümle) ve konunun gerçekten merak uyandırıcı olması, etiketten çok daha
belirleyici.

## Özelleştirme
- **Dil**: `CONTENT_LANGUAGE=tr` yapıp `TTS_VOICE`'u da `tr-TR-EmelNeural` gibi
  bir Türkçe sese çevirirsen tekrar Türkçe içeriğe dönebilirsin.
- **Ses**: `check_and_produce.yml` içindeki `TTS_VOICE` (tüm liste: `edge-tts --list-voices`)
- **Konu/script üslubu**: `src/generate_script.py` → `SYSTEM_PROMPT`
- **Altyazı görünümü**: `src/assemble_video.py` → `subtitle_style`
- **Bekleme süresi**: `FALLBACK_HOURS` (0 = otomatik ilerlemeyi tamamen kapat)
- **Max tekrar-üret denemesi**: `MAX_REDO_ATTEMPTS`
- **Otomatik başlama saati**: `AUTO_TRIGGER_TIME` (manuel tetiklenmezse döngü ne zaman kendiliğinden başlasın)
- **Yayın saati**: `PUBLISH_TIME_ISTANBUL` (`"off"` = zamanlamayı kapat, onaylanır onaylanmaz hemen yayınla)

## Tam otomatik moda dönmek istersen
`src/main.py` hâlâ duruyor — konu seçimi ve onay adımlarını atlayıp direkt
üretip yüklemek istersen `python main.py` çalıştıran ayrı, basit bir workflow kurman yeterli.

## Yerel test
```
export TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=...
export ANTHROPIC_API_KEY=... PEXELS_API_KEY=...
cd src
python suggest_topics.py       # 5 konuyu uretir, Telegram'a gonderir
python check_and_produce.py    # secim/onay var mi kontrol eder, varsa ilerletir
```
