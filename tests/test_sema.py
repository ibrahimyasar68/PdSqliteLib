## Şema göçleri (database/sema.py) testleri ##
import sqlite3

import pytest

from database import sema
from database.baglanti import goc_oncesi_yedek
from database.yedek import yedek_hatasi

ESKI_FOLLOW = ("CREATE TABLE follow (userId TEXT, bookId TEXT, outdate TEXT, outtime TEXT, status TEXT,"
               " indate TEXT, intime TEXT)")


@pytest.fixture
def eski(tmp_path):
    """Sürüm 0 (göç öncesi) veritabanı: follow'da id'ler metin, ödünç numarası yok."""
    b = sqlite3.connect(tmp_path / "eski.db")
    b.execute(ESKI_FOLLOW)
    b.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, kullanici TEXT UNIQUE, sifre TEXT, adi_soyadi TEXT,"
              " telefon TEXT, mail TEXT, yetki TEXT)")
    b.execute("INSERT INTO users VALUES (1, 'admin', 'x', 'Yönetici', '', '', 'admin')")
    b.executemany("INSERT INTO follow VALUES (?,?,?,?,?,?,?)", [
        ("3", "1", "2025-01-01", "10:00 ", "in", "2025-01-10", "11:00 "),
        ("3", "1", "2026-01-01", "10:00 ", "out", "", ""),
        ("4", "eski", "2026-01-02", "10:00 ", "out", "", ""),      # sayıya çevrilemeyen eski değer
    ])
    b.execute("DELETE FROM follow WHERE rowid=1")                  # numaralarda boşluk: 2 ve 3 kalır
    b.commit()
    yield b
    b.close()


def test_eski_veritabani_kayipsiz_tasinir(eski):
    sema.sema_olustur(eski)
    assert sema.surum(eski) == sema.SURUM
    satirlar = eski.execute("SELECT id, userId, bookId, status FROM follow ORDER BY id").fetchall()
    assert satirlar == [(2, 3, 1, "out"), (3, 4, "eski", "out")]       # numaralar (rowid) korunur
    assert eski.execute("SELECT typeof(userId), typeof(bookId) FROM follow WHERE id=2").fetchone() == ("integer", "integer")
    indeksler = {s[0] for s in eski.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='follow'")}
    assert {"follow_kitap", "follow_uye", "follow_durum"} <= indeksler
    assert eski.execute("PRAGMA integrity_check").fetchone() == ("ok",)


def test_goc_iki_kez_calisinca_bir_sey_degismez(eski):
    sema.sema_olustur(eski)
    once = eski.execute("SELECT * FROM follow ORDER BY id").fetchall()
    sema.sema_olustur(eski)
    assert eski.execute("SELECT * FROM follow ORDER BY id").fetchall() == once


def test_bos_veritabani_son_surumle_kurulur(tmp_path):
    b = sqlite3.connect(tmp_path / "yeni.db")
    sema.sema_olustur(b)
    assert sema.surum(b) == sema.SURUM
    assert "id" in [s[1] for s in b.execute("PRAGMA table_info(follow)")]
    b.close()


def test_yarim_kalan_adim_geri_alinir(eski, monkeypatch):
    monkeypatch.setattr(sema, "GOCLER", sema.GOCLER + [("bozuk", ["CREATE TABLE gecici (a)", "BU SQL DEĞİL"])])
    monkeypatch.setattr(sema, "SURUM", len(sema.GOCLER))
    with pytest.raises(sqlite3.OperationalError):
        sema.sema_olustur(eski)
    assert sema.surum(eski) == sema.SURUM - 1                    # önceki adımlar uygulandı, bozuk adım hiç
    assert "gecici" not in sema.tablolar(eski)


def test_programdan_yeni_veritabani_reddedilir(eski, tmp_path):
    eski.execute(f"PRAGMA user_version = {sema.SURUM + 1}")
    eski.commit()
    with pytest.raises(RuntimeError, match="programdan yeni"):
        sema.sema_olustur(eski)
    assert "daha yeni bir sürümüyle" in yedek_hatasi(str(tmp_path / "eski.db"))


def test_gocten_once_yedek_alinir(eski, tmp_path):
    yol = goc_oncesi_yedek(eski, str(tmp_path / "eski.db"))
    assert "goc_oncesi_v0_" in yol
    yedek = sqlite3.connect(yol)
    assert sema.surum(yedek) == 0 and yedek.execute("SELECT COUNT(*) FROM follow").fetchone()[0] == 2
    yedek.close()
    sema.sema_olustur(eski)
    assert goc_oncesi_yedek(eski, str(tmp_path / "eski.db")) is None     # güncel veritabanında yedek alınmaz
