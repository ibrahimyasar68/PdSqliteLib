#Veritabanı İşlemleri#
import sqlite3
import os
import hashlib
import hmac
import secrets

# Veritabanı proje içindeki data/ klasöründe (Windows ve Mac için ortak)
DB_YOLU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "DBL_Kayit.db")


baglantı = sqlite3.connect(DB_YOLU)
islem=baglantı.cursor()
baglantı.commit()


#Kayıt ekleme (ActifLibrary)
def ekle_kayit(kayit):
    ekle="Insert Into kayitlistesi (adi, yazari, ceviren, turu, yayinevi, yili, sayfa) values (?,?,?,?,?,?,?)"
    islem.execute(ekle,((kayit[0]),(kayit[1]),(kayit[2]),(kayit[3]),(kayit[4]),(kayit[5]),(kayit[6])))
    baglantı.commit()


# Kayıt değiştirme  (ActifLibrary)
def degistir_kayit(kayit):
    dgsm="Update kayitlistesi Set adi=?, yazari=?, ceviren=?, turu=?, yayinevi=?, yili=?, sayfa=? where id=?"
    islem.execute(dgsm,(kayit[1],kayit[2],kayit[3],kayit[4],kayit[5],kayit[6],kayit[7],kayit[0]))
    baglantı.commit()


#isme göre kayıt silme (ActifLibrary)  
def sil_kayit(id):
    sorgu=("Delete From kayitlistesi where Id=?")
    islem.execute(sorgu,(id,))
    baglantı.commit() 


# Şifre hash'leme: "pbkdf2$tekrar$tuz$hash" biçiminde saklanır
SIFRE_TEKRAR = 200_000

def sifre_hashle(sifre):
    tuz = secrets.token_bytes(16)
    ozet = hashlib.pbkdf2_hmac("sha256", sifre.encode(), tuz, SIFRE_TEKRAR)
    return f"pbkdf2${SIFRE_TEKRAR}${tuz.hex()}${ozet.hex()}"

def sifre_dogrula(sifre, kayitli):
    if not kayitli:
        return False
    if not kayitli.startswith("pbkdf2$"):
        # Eski (düz metin) kayıtlar için
        return hmac.compare_digest(sifre, kayitli)
    _, tekrar, tuz, ozet = kayitli.split("$")
    yeni = hashlib.pbkdf2_hmac("sha256", sifre.encode(), bytes.fromhex(tuz), int(tekrar))
    return hmac.compare_digest(yeni.hex(), ozet)

def sifre_guncelle(kullanici, sifre):
    islem.execute("Update users Set sifre=? where kullanici=?", (sifre_hashle(sifre), kullanici))
    baglantı.commit()


# kullanıcı ekleme (users)
def user_ekle(user):
    ekle="Insert Into users ( kullanici, sifre, adi_soyadi, telefon, mail, yetki) values (?,?,?,?,?,?)"
    islem.execute(ekle,(user[0],sifre_hashle(user[1]),user[2],user[3],user[4],user[5]))
    baglantı.commit()


def save_work_to_db(kayit):
    baglantı = sqlite3.connect(DB_YOLU)
    islem=baglantı.cursor()
    baglantı.commit()
    ekle="Insert Into follow (userId,bookId,outdate,outtime,status,indate,intime) values (?,?,?,?,?,?,?)"
    islem.execute(ekle,((kayit[0]),(kayit[1]),(kayit[2]),(kayit[3]),(kayit[4]),(kayit[5]),(kayit[6])))
    baglantı.commit()
    baglantı.close()

def uptate_work_to_db(kayit):
    baglantı = sqlite3.connect(DB_YOLU)
    islem=baglantı.cursor()
    baglantı.commit()
    # Sadece dışarıdaki (status='out') kayıt güncellenir, geçmiş iadeler korunur
    dgsm="Update follow Set status=?, indate=?, intime=? where userId=? and bookId=? and status='out'"
    islem.execute(dgsm,(kayit[4],str(kayit[5]),kayit[6],str(kayit[0]),str(kayit[1])))
    baglantı.commit()
    baglantı.close()
    

if __name__=="__main__": 
    pass
 