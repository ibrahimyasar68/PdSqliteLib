from collections import Counter

from database.dbbase import baglantı, sifre_dogrula, sifre_guncelle

# Sorguya adı yazılabilecek kolonlar (değerler her zaman ? ile verilir)
KITAP_KOLON = {'Id','Adi','Yazari','Ceviren','Turu','Yayinevi','Yili','Sayfa','ISBN','Kopya','Raf','Notlar'}
USER_KOLON = {'id','kullanici','adi_soyadi','telefon','mail','yetki'}

def kolon(ad, izinli):
    if ad not in izinli:
        raise ValueError(f"Geçersiz kolon: {ad}")
    return ad

######################
###  Book Table   ####
######################

# Kitap Listesi tablosunun kolonları (Notlar listede gösterilmez ama aramada kullanılır)
LISTE_SQL = "SELECT Id, Adi, Yazari, Ceviren, Turu, Yayinevi, Yili, Sayfa, ISBN, Kopya, Raf FROM kayitlistesi"
TEMEL_KOLONLAR = "Id, Adi, Yazari, Ceviren, Turu, Yayinevi, Yili, Sayfa"
TUM_KOLONLAR = TEMEL_KOLONLAR + ", ISBN, Kopya, Raf, Notlar"

## Arama: büyük/küçük harf ve Türkçe karakter farkı gözetilmez ("sahin" -> "Şahin")
_KATLAMA = str.maketrans("ÇĞIİÖŞÜÂÎÛçğıöşüâîû", "cgiiosuaiucgiosuaiu")

def katla(metin):
    return str(metin or "").translate(_KATLAMA).lower()

## Türk alfabesine göre sıralama anahtarı (Ç, Ğ, İ, Ö, Ş, Ü kendi yerlerinde; büyük/küçük harf farksız)
_ALFABE = "abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_SIRA = {h: i for i, h in enumerate(_ALFABE)}

def tr_sirala(metin):
    metin=str(metin or "").replace("I","ı").replace("İ","i").lower().translate(str.maketrans("âîû","aiu"))
    return [1000+_SIRA[h] if h in _SIRA else ord(h) for h in metin]

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

## Filtre açılır listeleri için bir kolondaki farklı değerler (boşlar hariç)
def df_sort_list(sort):
    k=kolon(sort,KITAP_KOLON)
    satirlar=baglantı.execute(f"SELECT DISTINCT {k} FROM kayitlistesi WHERE {k} IS NOT NULL AND {k}<>''").fetchall()
    return sorted((str(s[0]) for s in satirlar), key=tr_sirala)

## Açılır listeler için (id, adı, yayınevi, yılı) listesi
def df_book_id_list():
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

## Ana sayfa: son eklenen kitaplar (Id, Adi, Yazari)
def son_eklenenler(adet=10):
    return baglantı.execute("SELECT Id, Adi, Yazari FROM kayitlistesi ORDER BY Id DESC LIMIT ?",(adet,)).fetchall()

## Ayarlar > Hesabım için kullanıcının bilgileri: (kullanici, adi_soyadi, telefon, mail, yetki)
def kullanici_bilgisi(kullanici):
    return baglantı.execute("SELECT kullanici, adi_soyadi, telefon, mail, yetki FROM users WHERE kullanici=?",
                            (kullanici,)).fetchone()

######################
###  User Table   ####
######################

## Kitap verme ekranı için (id, adı soyadı, kullanıcı adı) listesi
def df_user_id_list():
    return baglantı.execute("SELECT id, adi_soyadi, kullanici FROM users ORDER BY adi_soyadi").fetchall()

## Kullanıcının tüm bilgileri (yoksa None)
def df_user_find_by_id(id):
    kayit=baglantı.execute("SELECT * FROM users WHERE id=?",(id,)).fetchone()
    return list(kayit) if kayit else None

## Bu kolonda bu değere sahip kullanıcı var mı?
def df_user_query(a,b):
    return baglantı.execute(f"SELECT COUNT(*) FROM users WHERE {kolon(a,USER_KOLON)}=?",(b,)).fetchone()[0]>0

## Kullanıcı yönetimi ekranı için tüm kullanıcılar (şifre hariç)
def df_user_all():
    return baglantı.execute("SELECT id, kullanici, adi_soyadi, telefon, mail, yetki FROM users ORDER BY kullanici").fetchall()

def admin_sayisi():
    return baglantı.execute("SELECT COUNT(*) FROM users WHERE yetki='admin'").fetchone()[0]

## Kullanıcının elinde iade edilmemiş kitap sayısı
def kullanici_odunc_sayisi(id):
    return baglantı.execute("SELECT COUNT(*) FROM follow WHERE userId=? AND status='out'",(str(id),)).fetchone()[0]

## Giriş kontrolü: doğruysa yetkiyi, yanlışsa None döndürür
def giris_kontrol(name,paw):
    kayit=baglantı.execute("SELECT sifre, yetki FROM users WHERE kullanici=?",(name,)).fetchone()
    if kayit is None or not sifre_dogrula(paw,kayit[0]):
        return None
    if not kayit[0].startswith("pbkdf2$"):
        sifre_guncelle(name,paw)  # Eski düz metin şifreyi hash'e çevir
    return kayit[1]

######################
###  Work Table   ####
######################

## Kitap şu an ödünçte mi?
def kitap_oduncte(book_id):
    return baglantı.execute("SELECT COUNT(*) FROM follow WHERE bookId=? AND status='out'",(str(book_id),)).fetchone()[0]>0

## Kitabın tüm bilgileri: Id, Adi, Yazari, Ceviren, Turu, Yayinevi, Yili, Sayfa, ISBN, Kopya, Raf, Notlar (yoksa None)
def df_book_find_by_id(id):
    kayit=baglantı.execute(f"SELECT {TUM_KOLONLAR} FROM kayitlistesi WHERE Id=?",(id,)).fetchone()
    return list(kayit) if kayit else None

## Kitabın kaç kopyası var, kaçı dışarıda
def kopya_durumu(book_id):
    kopya=baglantı.execute("SELECT COALESCE(Kopya,1) FROM kayitlistesi WHERE Id=?",(book_id,)).fetchone()
    disarida=baglantı.execute("SELECT COUNT(*) FROM follow WHERE bookId=? AND status='out'",(str(book_id),)).fetchone()[0]
    return (kopya[0] if kopya else 0), disarida

## Kitap listelerindeki "Durum" kolonu: her kitap için (yazı, tür); tür "rafta", "kismen" veya "yok"
def kitap_durumlari(kitap_idler):
    kopyalar=dict(baglantı.execute("SELECT Id, COALESCE(Kopya,1) FROM kayitlistesi"))
    disarida={}
    for (b,) in baglantı.execute("SELECT bookId FROM follow WHERE status='out'"):
        if str(b).isdigit():
            disarida[int(b)]=disarida.get(int(b),0)+1
    return [durum_yazi(kopyalar.get(i,1),disarida.get(i,0)) for i in kitap_idler]

def durum_yazi(kopya, disarida):
    if disarida<=0:
        return ("Rafta","rafta")
    if disarida>=kopya:
        return ("Ödünçte","yok") if kopya==1 else (f"{kopya} kopyanın hepsi ödünçte","yok")
    return (f"{kopya-disarida}/{kopya} kopya rafta","kismen")

## Üyede bu kitabın iade edilmemiş bir kopyası var mı?
def uyede_mi(user_id, book_id):
    return baglantı.execute("SELECT COUNT(*) FROM follow WHERE userId=? AND bookId=? AND status='out'",
                            (str(user_id),str(book_id))).fetchone()[0]>0

## Kitap vermede tablo döküm listesi
def df_work_table_book():
    kayit=baglantı.execute("""SELECT COALESCE(k.Adi,'(silinmiş kitap)'), COALESCE(k.Yazari,''), COALESCE(k.Turu,''),
                                     COALESCE(u.adi_soyadi,'(silinmiş üye)'), COALESCE(u.telefon,''), COALESCE(u.mail,''), f.outdate,
                                     f.userId, f.bookId
                              FROM follow f
                              LEFT JOIN kayitlistesi k ON k.Id=f.bookId
                              LEFT JOIN users u ON u.id=f.userId
                              WHERE f.status='out' ORDER BY f.outdate, f.rowid""").fetchall()
    return [list(satir) for satir in kayit]

