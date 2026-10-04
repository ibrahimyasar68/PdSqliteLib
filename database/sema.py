## Veritabanı şeması ve göçler ##
# SEMA ilk sürümün (0) tablolarıdır: yoksa oluşturulur, var olan tablolara ve verilere dokunulmaz.
# Sonraki her değişiklik GOCLER listesine yeni bir adım olarak eklenir (eski adımlar değiştirilmez).
# Veritabanının hangi adımda olduğu PRAGMA user_version'da tutulur; açılışta eksik adımlar sırayla,
# her biri tek işlemde uygulanır. Yedekten geri yüklenen eski veritabanları da böyle güncellenir.

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


# Göç adımları: (açıklama, [SQL komutları]). Adım n uygulanınca user_version n olur.
GOCLER = [
    # 1: follow tablosunda id'ler sayı (eskiden metin: '3'), her ödüncün kalıcı bir numarası (id) var,
    #    sık sorgulanan kolonlarda indeks. Mevcut satırların numarası (rowid) id olarak korunur ("Geri Al" için).
    #    Yabancı anahtar bilerek yok: silinen üyenin ödünç geçmişi korunur, silinen kitap "Geri Al" ile aynı
    #    numarayla geri gelir; yabancı anahtar ya silmeyi engeller ya da geçmişi koparırdı.
    #    Kolon tiplerinin INTEGER olması '3' gibi metinleri 3'e çevirir; sayıya çevrilemeyen eski değer metin kalır.
    ("follow: sayı id'ler, ödünç numarası, indeksler", [
        """CREATE TABLE follow_yeni (
               id      INTEGER PRIMARY KEY AUTOINCREMENT,
               userId  INTEGER,
               bookId  INTEGER,
               outdate TEXT,
               outtime TEXT,
               status  TEXT,
               indate  TEXT,
               intime  TEXT
           )""",
        """INSERT INTO follow_yeni (id, userId, bookId, outdate, outtime, status, indate, intime)
           SELECT rowid, userId, bookId, outdate, outtime, status, indate, intime FROM follow""",
        "DROP TABLE follow",
        "ALTER TABLE follow_yeni RENAME TO follow",
        "CREATE INDEX follow_kitap ON follow (bookId, status)",
        "CREATE INDEX follow_uye ON follow (userId, status)",
        "CREATE INDEX follow_durum ON follow (status, outdate)",
    ]),
]

SURUM = len(GOCLER)


def surum(baglanti):
    return baglanti.execute("PRAGMA user_version").fetchone()[0]


def sema_olustur(baglanti):
    """Eksik tabloları oluşturur ve veritabanını son sürüme getirir."""
    if surum(baglanti) > SURUM:
        raise RuntimeError(f"Veritabanı bu programdan yeni (sürüm {surum(baglanti)}, program {SURUM}). "
                           "Programın güncel sürümünü kullanın.")
    baglanti.executescript(SEMA)
    for tablo, kolonlar in EK_KOLONLAR.items():
        mevcut = {satir[1] for satir in baglanti.execute(f"PRAGMA table_info({tablo})")}
        for ad, tip in kolonlar:
            if ad not in mevcut:
                baglanti.execute(f"ALTER TABLE {tablo} ADD COLUMN {ad} {tip}")
    baglanti.commit()
    for numara in range(surum(baglanti) + 1, SURUM + 1):
        _, komutlar = GOCLER[numara - 1]
        try:
            baglanti.execute("BEGIN IMMEDIATE")
            for komut in komutlar:
                baglanti.execute(komut)
            baglanti.execute(f"PRAGMA user_version = {numara}")
            baglanti.commit()
        except Exception:
            baglanti.rollback()       # yarım kalan adım hiç uygulanmamış olur; veri eski haliyle kalır
            raise


def tablolar(baglanti):
    return {satir[0] for satir in baglanti.execute("SELECT name FROM sqlite_master WHERE type='table'")}
