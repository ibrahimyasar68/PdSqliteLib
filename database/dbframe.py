import pandas as pd
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

def df_all_list():
    return baglantı.execute(LISTE_SQL).fetchall()

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

## Filtre sonuçları: kolonu verilen değere eşit kitaplar
def df_srt_fltr(sort,name):
    return baglantı.execute(f"SELECT {TEMEL_KOLONLAR} FROM kayitlistesi WHERE {kolon(sort,KITAP_KOLON)}=?",(name,)).fetchall()

## İstatistik: kolondaki her değer için kitap sayısı (en çok olan cnt tanesi)
def rapor(sor,cnt):
    dfbook=pd.read_sql_query("SELECT * FROM kayitlistesi",baglantı)
    snc=dfbook.groupby(sor)['Yili'].count().sort_values().tail(cnt)[::-1]
    return snc

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

def df_user_find_by_id(id):
    return list(baglantı.execute("SELECT * FROM users WHERE id=?",(id,)).fetchone())

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

## İade ekranı için kitap alan kullanıcıların (id, adı soyadı, kullanıcı adı) listesi
def df_work_user_list():
    return baglantı.execute("""SELECT DISTINCT u.id, u.adi_soyadi, u.kullanici FROM follow f
                               JOIN users u ON u.id=f.userId
                               WHERE f.status='out' ORDER BY u.adi_soyadi""").fetchall()

## Kullanıcıdaki kitapların (id, adı) listesi
def df_work_perbook(id):
    return baglantı.execute("""SELECT k.Id, k.Adi FROM follow f
                               JOIN kayitlistesi k ON k.Id=f.bookId
                               WHERE f.status='out' AND f.userId=? ORDER BY k.Adi""",(str(id),)).fetchall()

## Kitabın tüm bilgileri: Id, Adi, Yazari, Ceviren, Turu, Yayinevi, Yili, Sayfa, ISBN, Kopya, Raf, Notlar
def df_book_find_by_id(id):
    return list(baglantı.execute(f"SELECT {TUM_KOLONLAR} FROM kayitlistesi WHERE Id=?",(id,)).fetchone())

## Kitabın kaç kopyası var, kaçı dışarıda
def kopya_durumu(book_id):
    kopya=baglantı.execute("SELECT COALESCE(Kopya,1) FROM kayitlistesi WHERE Id=?",(book_id,)).fetchone()
    disarida=baglantı.execute("SELECT COUNT(*) FROM follow WHERE bookId=? AND status='out'",(str(book_id),)).fetchone()[0]
    return (kopya[0] if kopya else 0), disarida

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

