## İstatistik ve özet sayılar ##

from collections import Counter

from database.baglanti import baglantı
from database.kitaplar import KITAP_KOLON, kolon
from database.metin import tr_sirala

## İstatistik: kolondaki her değer için kitap sayısı (en çok olan cnt tanesi)
## Boş değerli kitaplar "(belirtilmemiş)" olarak sayılır (eskiden adsız bir satır olarak görünüyordu)
BELIRTILMEMIS="(belirtilmemiş)"

## En çok kitabı olan cnt değer: {değer: adet}, çoktan aza; eşit sayıda olanlar Türk alfabesine göre.
## bos_dahil=False ise boşlar atlanır.
def rapor(sor,cnt,bos_dahil=True):
    degerler=(str(d if d is not None else "").strip()
              for (d,) in baglantı.execute(f"SELECT {kolon(sor,KITAP_KOLON)} FROM kayitlistesi"))
    # Her kitap sayılır (eskiden Yılı boş olan kitaplar türe/yazara göre sayımda atlanıyordu)
    sayim=Counter(d or BELIRTILMEMIS for d in degerler if d or bos_dahil)
    sira=sorted(sayim,key=lambda d:(-sayim[d],tr_sirala(d)))[:cnt]
    return {d: sayim[d] for d in sira}

## Basım yıllarına göre on yıllık dağılım: [("1980'ler", 45), ("1990'lar", 120), ...]
_ONLUK_EK = {0:"ler", 1:"lar", 2:"ler", 3:"lar", 4:"lar", 5:"ler", 6:"lar", 7:"ler", 8:"ler", 9:"lar"}

def yil_dagilimi():
    sayilar={}
    for (yil,) in baglantı.execute("SELECT Yili FROM kayitlistesi"):
        yil=str(yil or "").strip()
        if len(yil)==4 and yil.isdigit():
            onluk=int(yil)//10*10
            sayilar[onluk]=sayilar.get(onluk,0)+1
    return [(f"{o}'{_ONLUK_EK[o//10%10]}", sayilar[o]) for o in sorted(sayilar)]

## Ayarlar > Kütüphane Bilgileri için özet sayılar
def genel_ozet():
    tek=lambda sql: baglantı.execute(sql).fetchone()[0]
    return {"kitap": tek("SELECT COUNT(*) FROM kayitlistesi"),
            "kopya": tek("SELECT COALESCE(SUM(COALESCE(Kopya,1)),0) FROM kayitlistesi"),
            "uye": tek("SELECT COUNT(*) FROM users WHERE yetki='guest'"),
            "admin": tek("SELECT COUNT(*) FROM users WHERE yetki='admin'"),
            "disarida": tek("SELECT COUNT(*) FROM follow WHERE status='out'"),
            "odunc": tek("SELECT COUNT(*) FROM follow")}
