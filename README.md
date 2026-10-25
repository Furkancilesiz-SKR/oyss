# OYSS Rehberi (9-12. sınıf, 2026-2027 1. dönem)

> **Uyarı.** Bu sayfa bağımsız bir bilgilendirme sayfasıdır, Millî Eğitim Bakanlığı’nın resmî sitesi değildir ve sınav işlemleri bu sayfadan yapılmaz. Sınav işlemleri için [eba.gov.tr](https://www.eba.gov.tr) esastır.

## Bu nedir?

Ortak Yazılı Sınav Sistemi (OYSS) için hazırlanmış bir rehber sitesi. Sınıfını (9, 10, 11, 12), dersi ve yazılıyı seçersin; her senaryoda hangi öğrenme çıktısından kaç açık uçlu soru geleceğini kart kart ya da yan yana karşılaştırma tablosunda görürsün. Veri, ÖDSGM’nin 10 Eylül 2026 tarihli konu-soru dağılım tablolarından alındı.

Bilmen gerekenler:

- **12. sınıf OYSS kapsamında değil** (OYSS Uygulama Kılavuzu). 12. sınıf sekmesindeki tablolar ÖDSGM’nin 12. sınıf sayfalarıdır; okulunun ortak yazılısında kullanılıp kullanılmadığını öğretmenine sor.
- **11. sınıf İngilizce** OYSS dışında, bu yüzden listede yok.
- **Ülke geneli yazılılar** (9. sınıf Matematik 2. yazılı: 6 Ocak 2027; 10. sınıf Türk Dili ve Edebiyatı 1. yazılı: 12 Kasım 2026) için tablo henüz yayımlanmadı; sınav öncesi kılavuzla yayımlanacak.
- **Örnek soru yok.** MEB/ÖDSGM 2026-2027 OYSS için örnek soru yayımlamadı; soru havuzu yalnız öğretmenlere, sınavdan 4 gün önce açılıyor. Sayfada uydurma soru yok.
- Resmî tabloda "Toplam" satırı yok; toplamlar satırlardan hesaplandı (yalnız 11. sınıf Türk Dili ve Edebiyatı 2. yazılıda etiketsiz bir toplam satırı var ve hesapla aynı çıkıyor).

## Dosyalar

| Yol | Ne |
| --- | --- |
| `oyss-rehber.html` | **Tek dosya sürüm.** CSS, JS, veri ve three.js içinde. Çift tıkla her tarayıcıda açılır, internet gerekmez. |
| `site/` | Aynı site, ayrı dosyalarla (yayınlamak için bunu yükle). `index.html`, `stil.css`, `uygulama.js`, `sahne.js` (3B başlık), `veri.js` (bütün veri), `vendor/` (three.js, lisansıyla). `vendor/three.classic.min.js`, `araclar/paketle.py`'nin `three.module.min.js`'den ürettiği klasik (file:// altında da çalışan) kopyadır. |
| `kontrol.py` | Veriyi denetler; hatasızsa "TAMAM" yazar. |
| `kaynaklar.md` | Resmî dosya adresleri (xlsx/PDF'ler pakete konmadı). |

## Nasıl açılır?

- En kolayı: `oyss-rehber.html` dosyasına çift tıkla.
- `site/index.html` dosyasına da çift tıklayabilirsin; 3B başlık dahil çalışır.

### Yerelde sunucuyla (isteğe bağlı)

Önce `site/` klasörünün içine gir, sonra sun:

```bash
cd site
python3 -m http.server 8000      # sonra tarayıcıda http://localhost:8000
```

Ya da (Node.js kuruluysa) `site/`'in bir üst klasöründen:

```bash
npx serve site
```

## Yayınlama (bu klasörden yapılmadı; yapacaksan)

Yayınlanacak klasör `site/`. Tek dosya yeterliyse `oyss-rehber.html`'i `index.html` adıyla yükle.

**GitHub Pages**

```bash
cd site
git init -b main && git add . && git commit -m "OYSS rehberi"
gh repo create oyss-rehber --public --source=. --push
gh api -X POST repos/<kullanici>/oyss-rehber/pages -f 'source[branch]=main' -f 'source[path]=/'
# adres: https://<kullanici>.github.io/oyss-rehber/
```

**Netlify Drop** (komutsuz): https://app.netlify.com/drop adresine `site/` klasörünü sürükle. Komutla:

```bash
npx netlify-cli deploy --dir=site --prod
```

**Vercel**

```bash
cd site
npx vercel --prod        # ilk seferde giriş ister; "Output directory" sorusuna . yaz
```

## Veri nasıl güncellenir? (ÖDSGM yeni tablo yayımlarsa)

Depo kökünde (`oyss/`), sırayla:

1. Yeni xlsx dosyalarını `veri/pdf/<sınıf>/` altına indir (adresler `kaynaklar.md`'de).
2. Sınıfın üretici betiğini çalıştır; JSON'u yeniden yazar:
   - 9: `python3 -I veri/araclar/s9/s9_uret.py`
   - 10: önce `python3 -I veri/araclar/uret_sinif10.py` (`veri/sinif-10.json`), sonra `python3 -I veri/araclar/s10_bos_satirlar.py` (`veri/sinif-10-tam-satirlar.json`: hiçbir senaryoda soru gelmeyen satırları da içerir; `birlestir.py` bunu ister, sırayı bozma)
   - 11: `python3 -I veri/araclar/uret11.py`
   - 12: `python3 -I veri/araclar/s12/yaz.py`
3. Tarih bilgisi değiştiyse `veri/araclar/birlestir.py` içindeki `OKUL_TARIH` ve `ULKE_TARIH` tablolarını güncelle.
4. Birleştir: `python3 -I veri/araclar/birlestir.py` → `site/veri.js` (kendi kontrolleri başarısızsa hata verip durur).
5. Paketle (depo kökünden, `araclar/paketle.py`; `teslim/` değil `oyss/araclar/`): `python3 -I araclar/paketle.py` → `teslim/site/`, `teslim/oyss-rehber.html`, `teslim/kaynaklar.md`.
6. Denetle: `python3 -I teslim/kontrol.py`.

Örnek soru yayımlanırsa ilgili sınıfın JSON'undaki `ornek_sorular` listesine şu alanlarla ekle; site otomatik gösterir: `ders_id`, `yazili`, `kod`, `soru`, `cevap_anahtari`, `gorsel_var`, `kaynak_url`, `sayfa` ve (önceki sistemden geliyorsa) `eski_sistem: true` (kartta "eski sistem" rozeti çıkar).

## Kontrol komutu

```bash
python3 -I teslim/kontrol.py          # depo kökünden
python3 kontrol.py                    # teslim klasörünün içinden
```

Çıktı `TAMAM` ya da hata listesi. Kontrol edilenler: sınıf başına ders sayısı (9:9, 10:10, 11:9, 12:9), her senaryoda satır toplamı = toplam, boş alan, her dersin kaynak adresi, bilinen iki ülke geneli tarih.

## Kullanılan diller ve araçlar

| Ne | Sürüm |
| --- | --- |
| HTML, CSS, JavaScript (kütüphanesiz, sistem fontları) | tarayıcıda çalışır |
| [three.js](https://threejs.org) (3B başlık sahnesi, MIT lisansı: `site/vendor/three.LICENSE`) | 0.170.0 |
| Python (yalnız standart kütüphane; birleştirme, paketleme, kontrol) | 3.14 ile denendi |
| Node.js (yalnız `npx serve` ve Lighthouse ölçümü için, isteğe bağlı) | 26 |

Sayfa hiçbir dış adrese istek atmaz (font, CDN yok). WebGL yoksa ya da cihaz "hareketi azalt" modundaysa 3B sahne hiç yüklenmez, sayfa aynen çalışır. Açık/koyu tema cihaz ayarını izler.

## Kaynaklar

Tam liste `kaynaklar.md`'de. Başlıcaları:

- [ÖDSGM 1. dönem konu soru dağılım tabloları 2026-2027](https://odsgm.meb.gov.tr/www/1donem-konu-soru-dagilim-tablolari-2026-2027/icerik/1724)
- [MEB duyurusu, 10 Eylül 2026](https://www.meb.gov.tr/birinci-donem-ortak-yazili-sinavlarinin-konu-soru-dagilim-tablolari-yayimlandi/haber/41870/tr)
- [OYSS Uygulama Kılavuzu](https://www.meb.gov.tr/meb_iys_dosyalar/2026_10/6ad703eb1bb29010473792_Ortak_Yazili_Sinav_Sistemi_OYSS_Uygulama_Kilavuzu.pdf)
- [Okul Geneli OYSS Uygulama Takvimi](https://www.meb.gov.tr/meb_iys_dosyalar/2026_10/6ad703df743f8654049216_Okul_Geneli_Ortak_Yazili_Sinav_Sistemi_Uygulama_Takvimi.pdf)
- [Ülke Geneli Ortak Yazılı Sınav Takvimi](https://odsgm.meb.gov.tr/meb_iys_dosyalar/2026_09/6aa2d6b17db57454479127_Ulke_Geneli_Ortak_Yaz%C4%B1l%C4%B1_S%C4%B1nav_Takvimi.pdf)

Sınavdan önce senaryo seçerken sayıları her zaman resmî dosyalarla karşılaştır.
