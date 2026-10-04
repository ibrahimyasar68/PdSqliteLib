## Veritabanı bağlantısı ##
# Veritabanı dosyasının yeri ve uygulamanın kullandığı tek bağlantı.
# Kitap, kullanıcı ve ödünç işlemleri kitaplar.py, kullanicilar.py ve odunc.py'dedir.

import os
import shutil
import sqlite3
import sys

from database.sema import sema_olustur

def db_yolu():
    """Geliştirmede proje içindeki data/ klasörü kullanılır.
    Paketlenmiş uygulamada (.app / .exe) veritabanı kullanıcı klasöründe tutulur;
    ilk açılışta paketle gelen veritabanı oraya kopyalanır.
    PDSQLITE_DB ortam değişkeni verilirse o dosya kullanılır (testler için)."""
    if os.environ.get("PDSQLITE_DB"):
        return os.environ["PDSQLITE_DB"]
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


# Uygulama tek bir bağlantı kullanır.
# Yazma işlemleri "with baglantı:" bloğundadır: blok bitince kaydedilir, hata olursa hiçbiri yazılmaz.
os.makedirs(os.path.dirname(os.path.abspath(DB_YOLU)), exist_ok=True)
baglantı = sqlite3.connect(DB_YOLU)
sema_olustur(baglantı)  # Eksik tablo varsa oluşturulur
