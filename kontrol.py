#!/usr/bin/env python3
"""OYSS rehberi veri tutarlılık denetimi.  Kullanım:  python3 kontrol.py [veri.js yolu]
Varsayılan: bu dosyanın yanındaki site/veri.js.  Hatasız ise 'TAMAM', değilse hata listesi + çıkış kodu 1."""
import datetime, hashlib, json, os, sys

yol = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site', 'veri.js')
hatalar = []
def h(m): hatalar.append(m)

s = open(yol, encoding='utf8').read()
bas = 'window.OYSS = '
if not s.startswith(bas): sys.exit('veri.js beklenen biçimde değil')
d = json.loads(s[len(bas):s.rindex(';')])

BEKLENEN = {9: 9, 10: 10, 11: 9, 12: 9}
bos = lambda v: v is None or (isinstance(v, str) and not v.strip())
siniflar = {x['sinif']: x for x in d['siniflar']}
if sorted(siniflar) != [9, 10, 11, 12]: h(f'sınıflar 9-12 olmalı: {sorted(siniflar)}')
if bos(d.get('uyari')) or 'resmî sitesi değildir' not in d['uyari']: h('uyarı metni yok')
for n, ders_say in BEKLENEN.items():
    sn = siniflar.get(n)
    if not sn: continue
    if len(sn['dersler']) != ders_say: h(f'{n}. sınıf ders sayısı {len(sn["dersler"])}, beklenen {ders_say}')
    if bos(sn.get('kaynaklar')): h(f'{n}. sınıf kaynak listesi boş')
    if n == 12 and 'OYSS kapsamında değil' not in (sn.get('uyari') or ''): h('12. sınıf uyarısı yok')
    if n == 11 and [k['id'] for k in sn.get('kapsam_disi', [])] != ['ingilizce']: h('11. sınıf İngilizce kapsam dışı notu yok')
    idler = [x['id'] for x in sn['dersler']]
    if len(set(idler)) != len(idler): h(f'{n}. sınıf ders id tekrarı')
    for x in sn['dersler']:
        ad = f'{n}/{x["id"]}'
        if bos(x.get('ad')): h(f'{ad}: ders adı boş')
        if bos(x.get('kaynak_url')) or not x['kaynak_url'].startswith('https://'): h(f'{ad}: kaynak URL yok')
        if len(x['yazililar']) != 2: h(f'{ad}: yazılı sayısı {len(x["yazililar"])}')
        for y in x['yazililar']:
            yad = f'{ad}/{y["ad"]}'
            if y['tur'] == 'ulke_geneli':
                if bos(y.get('tarih')): h(f'{yad}: ülke geneli tarih yok')
                if y['satirlar']: h(f'{yad}: ülke geneli ama satır var')
                continue
            if y['tur'] != 'senaryo': h(f'{yad}: bilinmeyen tür'); continue
            sc = y['senaryo_sayisi']
            if not sc or len(y['toplam']) != sc: h(f'{yad}: senaryo sayısı/toplam uzunluğu tutmuyor')
            if y['toplam_kaynak'] not in ('hesap', 'kaynak'): h(f'{yad}: toplam_kaynak geçersiz')
            if not y['satirlar']: h(f'{yad}: satır yok')
            for i in range(sc):
                t = sum(r['c'][i] for r in y['satirlar'])
                if t != y['toplam'][i]: h(f'{yad}: senaryo {i + 1} satır toplamı {t} != toplam {y["toplam"][i]}')
                if y['toplam'][i] <= 0: h(f'{yad}: senaryo {i + 1} toplamı 0')
            for r in y['satirlar']:
                if len(r['c']) != sc: h(f'{yad}: {r.get("kod")} c uzunluğu')
                if bos(r.get('metin')): h(f'{yad}: {r.get("kod")} metin boş')
                if bos(r.get('ust')) and n != 12: h(f'{yad}: {r.get("kod")} ünite/tema boş')
                if any(v < 0 for v in r['c']): h(f'{yad}: negatif sayı')
                if bool(r.get('bos')) != all(v == 0 for v in r['c']): h(f'{yad}: {r.get("kod")} bos işareti yanlış')
            if y['ad'] == '1. yazılı' and n in (9, 10, 11) and bos(y.get('takvim_gunu')): h(f'{yad}: takvim günü yok')
# (b) 11. sınıfta İngilizce ders olarak bulunmamalı
if 11 in siniflar and any(x['id'] == 'ingilizce' for x in siniflar[11]['dersler']): h('11. sınıf dersleri arasında ingilizce var (OYSS uygulanmaz)')
# (a) takvim günleri: sabit beklenen liste + haftanın günü hesapla doğrulanır
OKUL = {'biyoloji': '3 Kasım 2026', 'kimya': '4 Kasım 2026', 'tarih': '4 Kasım 2026', 'matematik': '5 Kasım 2026',
        'fizik': '6 Kasım 2026', 'felsefe': '6 Kasım 2026', 'cografya': '10 Kasım 2026',
        'turk-dili-ve-edebiyati': '11 Kasım 2026', 'din-kulturu': '11 Kasım 2026', 'ingilizce': '13 Kasım 2026'}
AYLAR = {'Ocak': 1, 'Şubat': 2, 'Mart': 3, 'Nisan': 4, 'Mayıs': 5, 'Haziran': 6, 'Temmuz': 7, 'Ağustos': 8, 'Eylül': 9, 'Ekim': 10, 'Kasım': 11, 'Aralık': 12}
GUNLER = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
def gun_dogru(t, yer):
    try:
        g, ay, yil, gun = t.split()
        gercek = GUNLER[datetime.date(int(yil), AYLAR[ay], int(g)).weekday()]
    except Exception:
        h(f'{yer}: tarih ayrıştırılamadı: {t!r}'); return
    if gercek != gun: h(f'{yer}: "{t}" yanlış, o gün {gercek}')
for n in (9, 10, 11):
    if n not in siniflar: continue
    for x in siniflar[n]['dersler']:
        for y in x['yazililar']:
            if y['tur'] == 'senaryo' and y['ad'] == '1. yazılı':
                t = y.get('takvim_gunu') or ''
                bek = OKUL.get(x['id'])
                if not t.startswith((bek or '?') + ' '): h(f'{n}/{x["id"]}: takvim günü {t!r}, beklenen {bek}')
                gun_dogru(t, f'{n}/{x["id"]}/takvim')
            elif y.get('takvim_gunu'): h(f'{n}/{x["id"]}/{y["ad"]}: beklenmeyen takvim günü')
for sn in siniflar.values():
    for x in sn['dersler']:
        for y in x['yazililar']:
            if y.get('tarih'): gun_dogru(y['tarih'], f'{sn["sinif"]}/{x["id"]}/tarih')
# (c) satır içeriği (ust, kod, konu, metin, c) parmak izi: birlestir.py kaynak JSON'dan hesaplayıp gömdü; burada veri.js satırlarından yeniden hesaplanır
for sn in siniflar.values():
    for x in sn['dersler']:
        for y in x['yazililar']:
            if y['tur'] != 'senaryo': continue
            ham = json.dumps([[r.get('ust'), r.get('kod'), r.get('konu'), r.get('metin'), list(r['c'])] for r in y['satirlar']], ensure_ascii=False, separators=(',', ':'))
            if hashlib.sha256(ham.encode('utf8')).hexdigest() != y.get('parmak'):
                h(f'{sn["sinif"]}/{x["id"]}/{y["ad"]}: satır içeriği parmak iziyle uyuşmuyor (sayı, sıra, konu ya da metin değişmiş)')
# bilinen tarihler
def bul(n, did, yad):
    for x in siniflar[n]['dersler']:
        if x['id'] == did:
            return [y for y in x['yazililar'] if y['ad'] == yad][0]
if bul(9, 'matematik', '2. yazılı')['tarih'] != '6 Ocak 2027 Çarşamba': h('9 Matematik 2. yazılı tarihi yanlış')
if bul(10, 'turk-dili-ve-edebiyati', '1. yazılı')['tarih'] != '12 Kasım 2026 Perşembe': h('10 TDE 1. yazılı tarihi yanlış')
if hatalar:
    print('HATA:'); [print(' -', x) for x in hatalar]; sys.exit(1)
top = sum(len(x['yazililar']) for sn in siniflar.values() for x in sn['dersler'])
print(f'TAMAM  ({len(siniflar)} sınıf, {sum(len(sn["dersler"]) for sn in siniflar.values())} ders, {top} yazılı)')
