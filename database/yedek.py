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
from database.sema import GEREKLI_TABLOLAR, tablolar

OTOMATIK_SAKLA = 10
OTOMATIK_ONEK = "DBL_Kayit_"      # otomatik yedekler: DBL_Kayit_20260929_101500.db


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


def otomatik_yedekler():
    """Otomatik yedekler, eskiden yeniye sıralı."""
    return sorted(glob.glob(os.path.join(yedek_klasoru(), f"{OTOMATIK_ONEK}[0-9]*.db")))


def otomatik_yedek():
    """Bugün otomatik yedek alınmadıysa alır, eski otomatik yedekleri temizler.
    Alınan yedeğin yolunu, gerek yoksa None döndürür."""
    bugun = datetime.date.today().strftime("%Y%m%d")
    if any(os.path.basename(y).startswith(f"{OTOMATIK_ONEK}{bugun}") for y in otomatik_yedekler()):
        return None
    yol = yedek_al()
    for eski in otomatik_yedekler()[:-OTOMATIK_SAKLA]:
        os.remove(eski)
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
    onceki = yedek_al(os.path.join(yedek_klasoru(), f"geri_yukleme_oncesi_{_zaman()}.db"))
    kaynak = sqlite3.connect(f"file:{yol}?mode=ro", uri=True)
    try:
        kaynak.backup(baglantı)
    finally:
        kaynak.close()
    return onceki
