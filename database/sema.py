## Veritabanı şeması ##
# Tablolar yoksa oluşturulur; var olan tablolara ve verilere dokunulmaz.

SEMA = """
CREATE TABLE IF NOT EXISTS kayitlistesi (
    Id       INTEGER PRIMARY KEY AUTOINCREMENT,
    Adi      TEXT,
    Yazari   TEXT,
    Ceviren  TEXT,
    Turu     TEXT,
    Yayinevi TEXT,
    Yili     TEXT,
    Sayfa    TEXT
);
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    kullanici  TEXT UNIQUE,
    sifre      TEXT,
    adi_soyadi TEXT,
    telefon    TEXT,
    mail       TEXT,
    yetki      TEXT
);
CREATE TABLE IF NOT EXISTS follow (
    userId  TEXT,
    bookId  TEXT,
    outdate TEXT,
    outtime TEXT,
    status  TEXT,
    indate  TEXT,
    intime  TEXT
);
"""

GEREKLI_TABLOLAR = {"kayitlistesi", "users", "follow"}


def sema_olustur(baglanti):
    baglanti.executescript(SEMA)
    baglanti.commit()


def tablolar(baglanti):
    return {satir[0] for satir in baglanti.execute("SELECT name FROM sqlite_master WHERE type='table'")}
