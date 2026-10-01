## Veritabanı yedekleme ##
# Yedekler veritabanının yanındaki "yedekler" klasörüne alınır:
#   geliştirme:  data/yedekler/
#   .app / .exe: ~/Library/Application Support/PdSqliteLib/yedekler/  (Windows: %APPDATA%\PdSqliteLib\yedekler)
# Otomatik yedek günde bir kez alınır, son OTOMATIK_SAKLA tanesi tutulur.
# SQLite'ın yedekleme özelliği kullanıldığı için program açıkken de tutarlı kopya alınır.

import datetime
import glob
import os
import sqlite3

from database.dbbase import DB_YOLU, baglantı
from database.sema import GEREKLI_TABLOLAR, sema_olustur, tablolar

OTOMATIK_SAKLA = 10
OTOMATIK_ONEK = "DBL_Kayit_"      # otomatik yedekler: DBL_Kayit_20260929_101500.db
# Riskli işlemlerden önce alınan güvenlik yedekleri: her türden son GUVENLIK_SAKLA tanesi tutulur
GUVENLIK_SAKLA = 10
GUVENLIK_ONEKLERI = ("duzeltme_oncesi_", "geri_yukleme_oncesi_")


def yedek_klasoru():
    klasor = os.path.join(os.path.dirname(os.path.abspath(DB_YOLU)), "yedekler")
    os.makedirs(klasor, exist_ok=True)
    return klasor


def _zaman():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def yedek_al(hedef=None):
    """Veritabanının kopyasını hedef dosyaya yazar ve dosya yolunu döndürür."""
    if hedef is None:
        hedef = os.path.join(yedek_klasoru(), f"{OTOMATIK_ONEK}{_zaman()}.db")
    if os.path.exists(hedef):
        os.remove(hedef)
    kopya = sqlite3.connect(hedef)
    try:
        baglantı.backup(kopya)
    finally:
        kopya.close()
    return hedef


def guvenlik_yedegi_al(onek):
    """Riskli bir işlemden önce yedek alır (ör. duzeltme_oncesi_...), aynı türün eskilerini temizler."""
    yol = yedek_al(os.path.join(yedek_klasoru(), f"{onek}{_zaman()}.db"))
    guvenlik_yedeklerini_temizle()
    return yol


def guvenlik_yedeklerini_temizle():
    """Her güvenlik yedeği türünden en yeni GUVENLIK_SAKLA tanesi kalır; silinen dosya sayısını döndürür."""
    silinen = 0
    for onek in GUVENLIK_ONEKLERI:
        yedekler = sorted(glob.glob(os.path.join(yedek_klasoru(), f"{onek}[0-9]*.db")))
        for eski in yedekler[:-GUVENLIK_SAKLA]:
            os.remove(eski)
            silinen += 1
    return silinen


def otomatik_yedekler():
    """Otomatik yedekler, eskiden yeniye sıralı."""
    return sorted(glob.glob(os.path.join(yedek_klasoru(), f"{OTOMATIK_ONEK}[0-9]*.db")))


def son_otomatik_yedek():
    """Son otomatik yedeğin tarihi (datetime) veya None."""
    yedekler = otomatik_yedekler()
    if not yedekler:
        return None
    try:
        return datetime.datetime.strptime(os.path.basename(yedekler[-1])[len(OTOMATIK_ONEK):-3], "%Y%m%d_%H%M%S")
    except ValueError:
        return None


def otomatik_yedek():
    """Bugün otomatik yedek alınmadıysa alır, eski otomatik yedekleri temizler.
    Alınan yedeğin yolunu, gerek yoksa None döndürür."""
    bugun = datetime.date.today().strftime("%Y%m%d")
    if any(os.path.basename(y).startswith(f"{OTOMATIK_ONEK}{bugun}") for y in otomatik_yedekler()):
        return None
    yol = yedek_al()
    for eski in otomatik_yedekler()[:-OTOMATIK_SAKLA]:
        os.remove(eski)
    guvenlik_yedeklerini_temizle()      # önceki sürümlerden birikmiş olanlar da temizlenir
    return yol


def yedek_hatasi(yol):
    """Dosya geri yüklenebilir bir yedek değilse nedenini, uygunsa None döndürür."""
    if not os.path.isfile(yol):
        return "Dosya bulunamadı."
    try:
        kaynak = sqlite3.connect(f"file:{yol}?mode=ro", uri=True)
        try:
            eksik = GEREKLI_TABLOLAR - tablolar(kaynak)
            if eksik:
                return f"Bu dosya PdSqliteLib veritabanı değil (eksik tablolar: {', '.join(sorted(eksik))})."
            if kaynak.execute("SELECT COUNT(*) FROM users WHERE yetki='admin'").fetchone()[0] == 0:
                return "Yedekte admin kullanıcı yok; geri yüklenirse kimse yönetici olarak giriş yapamaz."
        finally:
            kaynak.close()
    except sqlite3.DatabaseError:
        return "Dosya okunamadı veya bir SQLite veritabanı değil."
    return None


def geri_yukle(yol):
    """Yedeği mevcut veritabanının yerine yükler. Önce mevcut halin yedeğini alır ve onun yolunu döndürür."""
    hata = yedek_hatasi(yol)
    if hata:
        raise ValueError(hata)
    onceki = guvenlik_yedegi_al("geri_yukleme_oncesi_")
    kaynak = sqlite3.connect(f"file:{yol}?mode=ro", uri=True)
    try:
        kaynak.backup(baglantı)
    finally:
        kaynak.close()
    sema_olustur(baglantı)   # eski bir yedekte sonradan eklenen tablolar yoksa oluştur
    return onceki
