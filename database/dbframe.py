import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from database.dbbase import DB_YOLU, sifre_dogrula, sifre_guncelle

baglantı= sqlite3.connect(DB_YOLU)

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

def df_count_items():
    dfbook=pd.read_sql_query("SELECT * FROM kayitlistesi",baglantı)
    sayi=len(dfbook['Id'])
    return sayi

def df_all_list():
    dfbook=pd.read_sql_query("SELECT * FROM kayitlistesi",baglantı)
    snc=[]
    for i in range(df_count_items()):
        snc.append((dfbook.iloc[i]).values)
    return snc

def df_sort_list(sort):
    dfbook=pd.read_sql_query("SELECT * FROM kayitlistesi",baglantı)
    snc=list(dfbook[sort].unique())
    snc.sort()
    return snc

## Açılır listeler için (id, adı, yayınevi, yılı) listesi
def df_book_id_list():
    return baglantı.execute("SELECT Id, Adi, Yayinevi, Yili FROM kayitlistesi ORDER BY Adi, Yili").fetchall()

def df_srt_fltr(sort,name):
    snc=pd.read_sql_query(f"SELECT * FROM kayitlistesi WHERE {kolon(sort,KITAP_KOLON)}=?",baglantı,params=(name,))
    sn=[]
    for i in range(len(snc)):
        sn.append(([*(snc.iloc[i])]))
    return len(snc),sn

def rapor(sor,cnt): ###İstatistik için####
    dfbook=pd.read_sql_query("SELECT * FROM kayitlistesi",baglantı)
    snc=dfbook.groupby(sor)['Yili'].count().sort_values().tail(cnt)[::-1]
    return snc

def piegraf():
    liste=rapor('Turu',15)
    names=liste.index[::]
    val=liste.values[::]
    valint=list(float(i) for i in val)
    myexplode=[]
    for i in range(len(valint)):
        myexplode.append(0.05)
    figure=plt.figure()
    axes=figure.add_axes([0,0,1,1])
    axes.pie(valint,labels=names, shadow=True, explode=myexplode, autopct="%1.1f%%")
    plt.show()

######################
###  User Table   ####
######################

def df_user_list(key):
    dfuser=pd.read_sql_query("SELECT * FROM users",baglantı)
    snc=list(dfuser[key])
    return snc

## Kitap verme ekranı için (id, adı soyadı, kullanıcı adı) listesi
def df_user_id_list():
    return baglantı.execute("SELECT id, adi_soyadi, kullanici FROM users ORDER BY adi_soyadi").fetchall()

def df_user_find_by_id(id):
    return list(baglantı.execute("SELECT * FROM users WHERE id=?",(id,)).fetchone())

def df_user_query(a,b):
    sayi=baglantı.execute(f"SELECT COUNT(*) FROM users WHERE {kolon(a,USER_KOLON)}=?",(b,)).fetchone()[0]
    if sayi==0:
        return False
    elif sayi==1:
        return True
    else:
        return None

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


if __name__ == "__main__":

    # piegraf()

    # x=piegraf()
    # x.show()
    pass
