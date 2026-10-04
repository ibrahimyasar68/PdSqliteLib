## Kullanıcı arayüzü tercihleri (menü açık/kapalı, gizlenen kolonlar) ##
# Veritabanının yanındaki tercihler.ini dosyasında tutulur: program her açılışta hatırlar;
# testler ve geçici veritabanıyla açılan kopyalar gerçek tercihlere dokunmaz.

import os

from PySide6.QtCore import QSettings

from database.baglanti import DB_YOLU


def _dosya():
    return QSettings(os.path.join(os.path.dirname(os.path.abspath(DB_YOLU)), "tercihler.ini"), QSettings.IniFormat)


def oku(anahtar, varsayilan=None):
    deger = _dosya().value(anahtar)
    return varsayilan if deger is None else deger


def yaz(anahtar, deger):
    t = _dosya()
    t.setValue(anahtar, deger)
    t.sync()


def mantiksal(anahtar, varsayilan=False):
    return str(oku(anahtar, "1" if varsayilan else "0")) in ("1", "true", "True")


def sayi_listesi(anahtar):
    metin = str(oku(anahtar, "") or "")
    return [int(p) for p in metin.split(",") if p.strip().isdigit()]
