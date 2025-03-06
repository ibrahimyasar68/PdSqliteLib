#Veritabanı İşlemleri#
import sqlite3


baglantı = sqlite3.connect("C:\\Database\\DBL_Kayit.db")
islem=baglantı.cursor()
baglantı.commit()


#Kayıt ekleme (ActifLibrary)
def ekle_kayit(kayit):
    ekle="Insert Into kayitlistesi (id, adi, yazari, ceviren, turu, yayinevi, yili, sayfa) values (?,?,?,?,?,?,?,?)"
    islem.execute(ekle,((kayit[0]),(kayit[1]),(kayit[2]),(kayit[3]),(kayit[4]),(kayit[5]),(kayit[6]),(kayit[7])))
    baglantı.commit()


# Kayıt değiştirme  (ActifLibrary)
def degistir_kayit(kayit):
    dgsm =(f"Update kayitlistesi Set adi='{kayit[1]}', yazari='{kayit[2]}', ceviren='{kayit[3]}', turu='{kayit[4]}', yayinevi='{kayit[5]}', yili='{kayit[6]}', sayfa='{kayit[7]}' where id='{kayit[0]}'")
    islem.execute(dgsm)
    baglantı.commit()


#isme göre kayıt silme (ActifLibrary)  
def sil_adi(adi):
    sorgu=("Delete From kayitlistesi where adi=?")
    islem.execute(sorgu,(adi,))
    baglantı.commit() 


# kullanıcı ekleme (users)
def user_ekle(user):
    ekle="Insert Into users ( kullanıcı_adı, sifre, adi, soyadi, telefon, mail, sehir) values (?,?,?,?,?,?,?)"
    islem.execute(ekle,((user[0]),(user[1]),(user[2]),(user[3]),(user[4]),(user[5]),(user[6])))
    baglantı.commit()


if __name__=="__main__": 
    pass
 