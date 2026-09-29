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
    Sayfa    TEXT,
    ISBN     TEXT,
    Kopya    INTEGER DEFAULT 1,
    Raf      TEXT,
    Notlar   TEXT
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
CREATE TABLE IF NOT EXISTS duzeltme_yoksay (
    kolon TEXT,
    imza  TEXT
);
"""

GEREKLI_TABLOLAR = {"kayitlistesi", "users", "follow"}


# Sonradan eklenen kolonlar: eski veritabanları ve yedekler açılışta bunlarla güncellenir
EK_KOLONLAR = {"kayitlistesi": [("ISBN", "TEXT"), ("Kopya", "INTEGER DEFAULT 1"), ("Raf", "TEXT"), ("Notlar", "TEXT")]}


def sema_olustur(baglanti):
    baglanti.executescript(SEMA)
    for tablo, kolonlar in EK_KOLONLAR.items():
        mevcut = {satir[1] for satir in baglanti.execute(f"PRAGMA table_info({tablo})")}
        for ad, tip in kolonlar:
            if ad not in mevcut:
                baglanti.execute(f"ALTER TABLE {tablo} ADD COLUMN {ad} {tip}")
    baglanti.commit()


def tablolar(baglanti):
    return {satir[0] for satir in baglanti.execute("SELECT name FROM sqlite_master WHERE type='table'")}
