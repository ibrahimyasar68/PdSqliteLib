#Veritabanı İşlemleri#
import sqlite3
import os
import hashlib
import hmac
import secrets
import shutil
import sys

def db_yolu():
    """Geliştirmede proje içindeki data/ klasörü kullanılır.
    Paketlenmiş uygulamada (.app / .exe) veritabanı kullanıcı klasöründe tutulur;
    ilk açılışta paketle gelen veritabanı oraya kopyalanır."""
    if not getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "DBL_Kayit.db")
    if sys.platform == "darwin":
        klasor = os.path.expanduser("~/Library/Application Support/PdSqliteLib")
    elif sys.platform == "win32":
        klasor = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "PdSqliteLib")
    else:
        klasor = os.path.expanduser("~/.local/share/PdSqliteLib")
    yol = os.path.join(klasor, "DBL_Kayit.db")
    if not os.path.exists(yol):
        os.makedirs(klasor, exist_ok=True)
        shutil.copyfile(os.path.join(sys._MEIPASS, "data", "DBL_Kayit.db"), yol)
    return yol

DB_YOLU = db_yolu()


# Uygulama tek bir bağlantı kullanır (dbframe.py de bunu kullanır)
baglantı = sqlite3.connect(DB_YOLU)
islem=baglantı.cursor()


#Kayıt ekleme (ActifLibrary)
def ekle_kayit(kayit):
    ekle="Insert Into kayitlistesi (adi, yazari, ceviren, turu, yayinevi, yili, sayfa) values (?,?,?,?,?,?,?)"
    islem.execute(ekle,kayit[:7])
    baglantı.commit()


# Kayıt değiştirme  (ActifLibrary)
def degistir_kayit(kayit):
    dgsm="Update kayitlistesi Set adi=?, yazari=?, ceviren=?, turu=?, yayinevi=?, yili=?, sayfa=? where id=?"
    islem.execute(dgsm,(kayit[1],kayit[2],kayit[3],kayit[4],kayit[5],kayit[6],kayit[7],kayit[0]))
    baglantı.commit()


# id ile kayıt silme (ActifLibrary)
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


# Ödünç verme (follow)
def save_work_to_db(kayit):
    ekle="Insert Into follow (userId,bookId,outdate,outtime,status,indate,intime) values (?,?,?,?,?,?,?)"
    islem.execute(ekle,(kayit[0],kayit[1],str(kayit[2]),kayit[3],kayit[4],kayit[5],kayit[6]))
    baglantı.commit()

# İade alma (follow)
def update_work_to_db(kayit):
    # Sadece dışarıdaki (status='out') kayıt güncellenir, geçmiş iadeler korunur
    dgsm="Update follow Set status=?, indate=?, intime=? where userId=? and bookId=? and status='out'"
    islem.execute(dgsm,(kayit[4],str(kayit[5]),kayit[6],str(kayit[0]),str(kayit[1])))
    baglantı.commit()
