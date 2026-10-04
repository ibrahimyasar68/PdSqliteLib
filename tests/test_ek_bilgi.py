## ISBN, kopya sayısı, raf yeri ve notlar testleri ##
import sqlite3
from dataclasses import replace

import pytest

from servis.dogrulama import isbn_gecerli, isbn_normal
from acodes.guest import Guest
from acodes.library import Library
from database.kitaplar import kitap_ara, kitap_bul, kitap_ekle, kitap_guncelle
from database.modeller import Kitap
from database.odunc import kopya_durumu, uyede_mi
from database.sema import sema_olustur


@pytest.mark.parametrize("isbn,gecerli", [
    ("978-0-306-40615-7", True), ("9780306406157", True),
    ("0-306-40615-2", True), ("080442957X", True), ("0 8044 2957 x", True),
    ("978-0-306-40615-8", False), ("0-306-40615-3", False), ("12345", False), ("abc", False),
])
def test_isbn_gecerli(isbn, gecerli):
    assert isbn_gecerli(isbn) is gecerli


def test_isbn_normal():
    assert isbn_normal(" 978-0-306 40615-7 ") == "9780306406157"
    assert isbn_normal("080442957x") == "080442957X"


def test_eski_veritabani_otomatik_guncellenir(tmp_path):
    b = sqlite3.connect(tmp_path / "eski.db")
    b.execute("CREATE TABLE kayitlistesi (Id INTEGER PRIMARY KEY, Adi TEXT, Yazari TEXT, Ceviren TEXT,"
              " Turu TEXT, Yayinevi TEXT, Yili TEXT, Sayfa TEXT)")
    b.execute("INSERT INTO kayitlistesi (Adi) VALUES ('Eski Kitap')")
    b.commit()
    sema_olustur(b)
    kolonlar = [s[1] for s in b.execute("PRAGMA table_info(kayitlistesi)")]
    assert kolonlar[-4:] == ["ISBN", "Kopya", "Raf", "Notlar"]
    assert b.execute("SELECT Kopya FROM kayitlistesi").fetchone()[0] == 1   # mevcut kitaplar 1 kopya
    sema_olustur(b)                                                          # ikinci kez sorun çıkarmaz
    b.close()


def test_ekle_ve_degistir(db):
    kitap_ekle(Kitap("Kısa"))
    kisa = db.execute("SELECT ISBN, Kopya, Raf, Notlar FROM kayitlistesi WHERE Adi='Kısa'").fetchone()
    assert kisa == ("", 1, "", "")
    kitap_id = kitap_ekle(Kitap("Tam", isbn="9780306406157", kopya=3, raf="B-2", notlar="İmzalı"))
    tam = kitap_bul(kitap_id)
    assert (tam.isbn, tam.kopya, tam.raf, tam.notlar) == ("9780306406157", 3, "B-2", "İmzalı")
    kitap_guncelle(replace(tam, isbn="", kopya=2, raf="C-1", notlar=""))
    assert kitap_bul(kitap_id) == Kitap("Tam", kopya=2, raf="C-1", id=kitap_id)


def test_aramada_isbn_raf_ve_notlar(db):
    kitap_ekle(Kitap("Tam", isbn="9780306406157", raf="B-2", notlar="Dedemden kalma"))
    assert len(kitap_ara("978-0-306")) == 1          # tireli yazılsa da bulur
    assert len(kitap_ara("b-2")) == 1
    assert len(kitap_ara("dedemden")) == 1
    kitap_ekle(Kitap("Bulantı", "Jean-Paul SARTRE"))
    assert len(kitap_ara("jean-paul")) == 1 and len(kitap_ara("jeanpaul")) == 1
    assert len(kitap_ara("tahir")[0]) == 11          # liste satırı 11 kolon (notlar hariç)


def test_kopya_durumu(db):
    db.execute("UPDATE kayitlistesi SET Kopya=2 WHERE Id=1")
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES ('3','1','2026-01-01','10:00','out','','')")
    db.commit()
    assert kopya_durumu(1) == (2, 1) and kopya_durumu(2) == (1, 0)
    assert uyede_mi(3, 1) and not uyede_mi(4, 1)


# --- Arayüz ---

@pytest.fixture
def lib(app, uyarilar):
    return Library()


@pytest.mark.parametrize("panel", [Library, Guest])
def test_kitap_listesinde_yeni_kolonlar(app, uyarilar, db, panel):
    db.execute("UPDATE kayitlistesi SET ISBN='9780306406157', Kopya=2, Raf='A-1' WHERE Id=1")
    db.commit()
    p = panel()
    t = p.liste.tablo
    p.liste.arama.setText("yol ayrımı")
    basliklar = [t.horizontalHeaderItem(c).text() for c in range(t.columnCount())]
    assert basliklar[-4:] == ["ISBN", "Kopya", "Raf", "Durum"]
    assert [t.item(0, c).text() for c in (8, 9, 10, 11)] == ["9780306406157", "2", "A-1", "Rafta"]


def test_durum_yazisi():
    from database.kitaplar import durum_yazi
    assert durum_yazi(1, 0) == ("Rafta", "rafta")
    assert durum_yazi(1, 1) == ("Ödünçte", "yok")
    assert durum_yazi(3, 1) == ("2/3 kopya rafta", "kismen")
    assert durum_yazi(2, 2) == ("2 kopyanın hepsi ödünçte", "yok")


@pytest.mark.parametrize("panel", [Library, Guest])
def test_listelerde_durum_kolonu_renkli(app, uyarilar, db, panel):
    from acodes import tema
    db.execute("UPDATE kayitlistesi SET Kopya=2 WHERE Id=1")
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES ('3','1','2026-01-01','10:00 ','out','','')")
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES ('3','6','2026-01-01','10:00 ','out','','')")
    db.commit()
    p = panel()
    t = p.liste.tablo
    p.liste.listele()
    durum = {t.item(r, 1).text(): t.item(r, 11) for r in range(t.rowCount())}
    assert durum["Yol Ayrımı"].text() == "1/2 kopya rafta" and durum["Satranç"].text() == "Ödünçte"
    assert durum["Denemeler"].text() == "Rafta"
    assert durum["Satranç"].foreground().color().name() == tema.TEHLIKE.lower()
    p.filtre.ekle("Yazari", "Stefan ZWEIG")                       # Filtre sonuçlarında da var
    assert p.filtre.tablo.item(0, 8).text() == "Ödünçte"
