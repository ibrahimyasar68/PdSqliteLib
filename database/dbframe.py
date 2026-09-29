import pandas as pd
from database.dbbase import baglantı, sifre_dogrula, sifre_guncelle

# Sorguya adı yazılabilecek kolonlar (değerler her zaman ? ile verilir)
KITAP_KOLON = {'Id','Adi','Yazari','Ceviren','Turu','Yayinevi','Yili','Sayfa'}
USER_KOLON = {'id','kullanici','adi_soyadi','telefon','mail','yetki'}

def kolon(ad, izinli):
    if ad not in izinli:
        raise ValueError(f"Geçersiz kolon: {ad}")
    return ad

######################
###  Book Table   ####
######################

def df_all_list():
    return baglantı.execute("SELECT * FROM kayitlistesi").fetchall()

## Filtre açılır listeleri için bir kolondaki farklı değerler (boşlar hariç)
def df_sort_list(sort):
    k=kolon(sort,KITAP_KOLON)
    satirlar=baglantı.execute(f"SELECT DISTINCT {k} FROM kayitlistesi WHERE {k} IS NOT NULL AND {k}<>''").fetchall()
    return sorted(str(s[0]) for s in satirlar)

## Açılır listeler için (id, adı, yayınevi, yılı) listesi
def df_book_id_list():
    return baglantı.execute("SELECT Id, Adi, Yayinevi, Yili FROM kayitlistesi ORDER BY Adi, Yili").fetchall()

## Filtre sonuçları: kolonu verilen değere eşit kitaplar
def df_srt_fltr(sort,name):
    return baglantı.execute(f"SELECT * FROM kayitlistesi WHERE {kolon(sort,KITAP_KOLON)}=?",(name,)).fetchall()

## İstatistik: kolondaki her değer için kitap sayısı (en çok olan cnt tanesi)
def rapor(sor,cnt):
    dfbook=pd.read_sql_query("SELECT * FROM kayitlistesi",baglantı)
    snc=dfbook.groupby(sor)['Yili'].count().sort_values().tail(cnt)[::-1]
    return snc

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

def df_book_find_by_id(id):
    return list(baglantı.execute("SELECT * FROM kayitlistesi WHERE Id=?",(id,)).fetchone())

## Kitap vermede tablo döküm listesi
def df_work_table_book():
    kayit=baglantı.execute("""SELECT COALESCE(k.Adi,'(silinmiş kitap)'), COALESCE(k.Yazari,''), COALESCE(k.Turu,''),
                                     COALESCE(u.adi_soyadi,'(silinmiş üye)'), COALESCE(u.telefon,''), COALESCE(u.mail,''), f.outdate
                              FROM follow f
                              LEFT JOIN kayitlistesi k ON k.Id=f.bookId
                              LEFT JOIN users u ON u.id=f.userId
                              WHERE f.status='out'""").fetchall()
    return [list(satir) for satir in kayit]

