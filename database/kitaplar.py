## Kitaplar (kayitlistesi tablosu): kayıt, arama, filtre ##

from database.baglanti import baglantı, islem
from database.metin import katla, tr_sirala
from database.modeller import Kitap

# Sorguya adı yazılabilecek kolonlar (değerler her zaman ? ile verilir)
KITAP_KOLON = {'Id','Adi','Yazari','Ceviren','Turu','Yayinevi','Yili','Sayfa','ISBN','Kopya','Raf','Notlar'}

def kolon(ad, izinli):
    if ad not in izinli:
        raise ValueError(f"Geçersiz kolon: {ad}")
    return ad

# Kitap Listesi tablosunun kolonları (Notlar listede gösterilmez ama aramada kullanılır)
LISTE_SQL = "SELECT Id, Adi, Yazari, Ceviren, Turu, Yayinevi, Yili, Sayfa, ISBN, Kopya, Raf FROM kayitlistesi"
TEMEL_KOLONLAR = "Id, Adi, Yazari, Ceviren, Turu, Yayinevi, Yili, Sayfa"
TUM_KOLONLAR = TEMEL_KOLONLAR + ", ISBN, Kopya, Raf, Notlar"

## Ad, yazar, çevirmen, tür, yayınevi, yıl, ISBN, raf ve notlarda geçen kelimelerin hepsini içeren kitaplar
def kitap_ara(sorgu):
    kelimeler=katla(sorgu.replace("-","")).split()
    sonuc=[]
    for satir in baglantı.execute(LISTE_SQL.replace(" FROM", ", Notlar FROM")):
        # Tireler iki tarafta da yok sayılır: "978-0-306" ISBN'i, "b-2" raf yerini, "jean-paul" adı bulur
        metin=katla(" ".join(str(x or "") for x in satir[1:7]+satir[8:9]+satir[10:12])).replace("-","")
        if all(k in metin for k in kelimeler):
            sonuc.append(satir[:11])
    return sonuc

## Filtre açılır listeleri ve öneriler için bir kolondaki farklı değerler (boşlar hariç), Türk alfabesine göre
def farkli_degerler(ad):
    k=kolon(ad,KITAP_KOLON)
    satirlar=baglantı.execute(f"SELECT DISTINCT {k} FROM kayitlistesi WHERE {k} IS NOT NULL AND {k}<>''").fetchall()
    return sorted((str(s[0]) for s in satirlar), key=tr_sirala)

## Açılır listeler için (id, adı, yayınevi, yılı) listesi
def secim_listesi():
    return baglantı.execute("SELECT Id, Adi, Yayinevi, Yili FROM kayitlistesi ORDER BY Adi, Yili").fetchall()

## Filtre: kosullar = {kolon: [seçilen değerler] veya "aranan metin"}.
## Liste verilirse değerlerden biri ("veya"), metin verilirse kitap listesindeki arama gibi yazılan kelimelerin
## hepsi (büyük/küçük harf ve Türkçe karakter farksız) aranır. Farklı kolonların hepsi ("ve") tutmalı.
_TEMEL_SIRA = {ad: i for i, ad in enumerate(TEMEL_KOLONLAR.split(", "))}

def _kosullari_hazirla(kosullar):
    hazir=[]
    for ad,kosul in kosullar.items():
        i=_TEMEL_SIRA[kolon(ad,set(_TEMEL_SIRA))]
        if isinstance(kosul,str):
            if katla(kosul).split():
                hazir.append((ad,i,False,katla(kosul).split()))
        elif kosul:
            hazir.append((ad,i,True,{str(d) for d in kosul}))
    return hazir

def _uyar(satir,hazir,haric=None):
    for ad,i,secim,deger in hazir:
        if ad==haric:
            continue
        metin="" if satir[i] is None else str(satir[i])
        if secim:
            if metin not in deger:
                return False
        elif not all(k in katla(metin) for k in deger):
            return False
    return True

## Koşullara uyan kitaplar (koşul yoksa boş liste), kitap adına göre sıralı
def kitap_filtrele(kosullar):
    hazir=_kosullari_hazirla(kosullar)
    if not hazir:
        return []
    satirlar=[s for s in baglantı.execute(f"SELECT {TEMEL_KOLONLAR} FROM kayitlistesi") if _uyar(s,hazir)]
    return sorted(satirlar, key=lambda s: (tr_sirala(s[1] or ""), s[0]))

## Her kolon için seçilebilecek değerler: o kolon hariç diğer koşullara uyan kitaplarda geçenler.
## Ör. türe "şiir" yazılınca yazar listesinde sadece şiir kitabı olan yazarlar kalır.
def filtre_secenekleri(kosullar, kolonlar):
    hazir=_kosullari_hazirla(kosullar)
    satirlar=baglantı.execute(f"SELECT {TEMEL_KOLONLAR} FROM kayitlistesi").fetchall()
    secenekler={}
    for ad in kolonlar:
        i=_TEMEL_SIRA[kolon(ad,set(_TEMEL_SIRA))]
        degerler={str(s[i]) for s in satirlar if s[i] not in (None,"") and _uyar(s,hazir,haric=ad)}
        secenekler[ad]=sorted(degerler,key=tr_sirala)
    return secenekler

## Ana sayfa: son eklenen kitaplar (Id, Adi, Yazari)
def son_eklenenler(adet=10):
    return baglantı.execute("SELECT Id, Adi, Yazari FROM kayitlistesi ORDER BY Id DESC LIMIT ?",(adet,)).fetchall()

## Kitap listelerindeki "Durum" kolonu: her kitap için (yazı, tür); tür "rafta", "kismen" veya "yok"
def kitap_durumlari(kitap_idler):
    kopyalar=dict(baglantı.execute("SELECT Id, COALESCE(Kopya,1) FROM kayitlistesi"))
    disarida={}
    for b,sayi in baglantı.execute("SELECT bookId, COUNT(*) FROM follow WHERE status='out' GROUP BY bookId"):
        disarida[b]=sayi
    return [durum_yazi(kopyalar.get(i,1),disarida.get(i,0)) for i in kitap_idler]

def durum_yazi(kopya, disarida):
    if disarida<=0:
        return ("Rafta","rafta")
    if disarida>=kopya:
        return ("Ödünçte","yok") if kopya==1 else (f"{kopya} kopyanın hepsi ödünçte","yok")
    return (f"{kopya-disarida}/{kopya} kopya rafta","kismen")

######################
###  Kayıt         ####
######################

_YAZ_KOLONLARI = ", ".join(Kitap.KOLONLAR)

## Kitabın tüm bilgileri (yoksa None)
def kitap_bul(id):
    kayit=baglantı.execute(f"SELECT {TUM_KOLONLAR} FROM kayitlistesi WHERE Id=?",(id,)).fetchone()
    return Kitap.satirdan(kayit) if kayit else None

## Yeni kitap; numarası (Id) döner
def kitap_ekle(kitap):
    with islem():
        return baglantı.execute(f"INSERT INTO kayitlistesi ({_YAZ_KOLONLARI}) VALUES ({','.join('?'*len(Kitap.KOLONLAR))})",
                                kitap.degerler()).lastrowid

## Kitabın tüm bilgilerini günceller (kitap.id ile)
def kitap_guncelle(kitap):
    atama=", ".join(f"{k}=?" for k in Kitap.KOLONLAR)
    with islem():
        baglantı.execute(f"UPDATE kayitlistesi SET {atama} WHERE Id=?", (*kitap.degerler(), kitap.id))

def kitap_sil(id):
    with islem():
        baglantı.execute("DELETE FROM kayitlistesi WHERE Id=?",(id,))

## Silinen kitabı aynı numarayla geri getirme ("Geri Al"); ödünç geçmişi numarayla bağlı kalır
def kitap_geri_ekle(kitap):
    with islem():
        baglantı.execute(f"INSERT INTO kayitlistesi (Id, {_YAZ_KOLONLARI}) VALUES ({','.join('?'*(len(Kitap.KOLONLAR)+1))})",
                         (kitap.id, *kitap.degerler()))
