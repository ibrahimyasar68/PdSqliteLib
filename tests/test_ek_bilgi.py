## ISBN, kopya sayısı, raf yeri ve notlar testleri ##
import sqlite3

import pytest

from acodes.ek_bilgi import isbn_gecerli, isbn_normal
from acodes.guest import Guest
from acodes.library import Library
from database.dbbase import degistir_kayit, ekle_kayit
from database.dbframe import df_book_find_by_id, kitap_ara, kopya_durumu, uyede_mi
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
    ekle_kayit(["Kısa", "", "", "", "", "", ""])
    kisa = db.execute("SELECT ISBN, Kopya, Raf, Notlar FROM kayitlistesi WHERE Adi='Kısa'").fetchone()
    assert kisa == ("", 1, "", "")
    ekle_kayit(["Tam", "", "", "", "", "", "", "9780306406157", 3, "B-2", "İmzalı"])
    kitap_id = db.execute("SELECT Id FROM kayitlistesi WHERE Adi='Tam'").fetchone()[0]
    assert df_book_find_by_id(kitap_id)[8:] == ["9780306406157", 3, "B-2", "İmzalı"]
    degistir_kayit([kitap_id, "Tam", "", "", "", "", "", ""])                   # ek bilgilere dokunmaz
    assert df_book_find_by_id(kitap_id)[9] == 3
    degistir_kayit([kitap_id, "Tam", "", "", "", "", "", "", "", 2, "C-1", ""])
    assert df_book_find_by_id(kitap_id)[8:] == ["", 2, "C-1", ""]


def test_aramada_isbn_raf_ve_notlar(db):
    ekle_kayit(["Tam", "", "", "", "", "", "", "9780306406157", 1, "B-2", "Dedemden kalma"])
    assert len(kitap_ara("978-0-306")) == 1          # tireli yazılsa da bulur
    assert len(kitap_ara("b-2")) == 1
    assert len(kitap_ara("dedemden")) == 1
    ekle_kayit(["Bulantı", "Jean-Paul SARTRE", "", "", "", "", ""])
    assert len(kitap_ara("jean-paul")) == 1 and len(kitap_ara("jeanpaul")) == 1
    assert len(kitap_ara("tahir")[0]) == 11          # liste satırı 11 kolon (notlar hariç)


def test_kopya_durumu(db):
    db.execute("UPDATE kayitlistesi SET Kopya=2 WHERE Id=1")
    db.execute("INSERT INTO follow VALUES ('3','1','2026-01-01','10:00','out','','')")
    db.commit()
    assert kopya_durumu(1) == (2, 1) and kopya_durumu(2) == (1, 0)
    assert uyede_mi(3, 1) and not uyede_mi(4, 1)


# --- Arayüz ---

@pytest.fixture
def lib(app, uyarilar):
    return Library()


def test_kayit_eklerken_ek_bilgiler(lib, db, uyarilar):
    q = lib.QtLibrary
    q.lineEdit_3_1_adi.setText("yeni kitap")
    lib.ek_3_1.isbn.setText("978-0-306-40615-8")      # hatalı kontrol basamağı
    lib.save_book()
    assert "ISBN geçerli değil" in uyarilar[-1]
    assert db.execute("SELECT COUNT(*) FROM kayitlistesi WHERE Adi='Yeni Kitap'").fetchone()[0] == 0
    lib.ek_3_1.isbn.setText("978-0-306-40615-7")
    lib.ek_3_1.kopya.setValue(3)
    lib.ek_3_1.raf.setText("  A-3 ")
    lib.ek_3_1.notlar.setPlainText("Bağış")
    lib.save_book()
    assert db.execute("SELECT ISBN, Kopya, Raf, Notlar FROM kayitlistesi WHERE Adi='Yeni Kitap'").fetchone() == \
        ("9780306406157", 3, "A-3", "Bağış")
    assert lib.ek_3_1.degerler() == ("", 1, "", "")    # form temizlendi


def test_duzenlemede_ek_bilgiler(lib, db, uyarilar):
    db.execute("UPDATE kayitlistesi SET Kopya=3, Raf='A-1' WHERE Id=1")
    db.executemany("INSERT INTO follow VALUES (?,'1','2026-01-01','10:00','out','','')", [("3",), ("4",)])
    db.commit()
    lib.kitap_duzenle(1)
    assert lib.ek_3_2.kopya.value() == 3 and lib.ek_3_2.raf.text() == "A-1"
    lib.ek_3_2.kopya.setValue(1)                        # 2 kopya dışarıdayken 1'e düşürülemez
    lib.update_item_3_2()
    assert "2 kopyası şu an üyelerde" in uyarilar[-1]
    lib.ek_3_2.kopya.setValue(2)
    lib.ek_3_2.raf.setText("C-9")
    lib.update_item_3_2()
    assert db.execute("SELECT Kopya, Raf FROM kayitlistesi WHERE Id=1").fetchone() == (2, "C-9")


def test_silme_ekraninda_ek_bilgiler_salt_okunur(lib, db):
    db.execute("UPDATE kayitlistesi SET Raf='D-4' WHERE Id=6")
    db.commit()
    lib.QtLibrary.comboBox_3_3_bul_adi.setCurrentText("Satranç")
    lib.find_item_3_3()
    assert lib.ek_3_3.raf.text() == "D-4" and lib.ek_3_3.raf.isReadOnly()


def odunc_ver(lib, kitap, user_id):
    q = lib.QtLibrary
    q.comboBox_6_1_1_liste_kitap.setCurrentText(kitap)
    lib.find_item_6_1_1()
    q.comboBox_6_1_2_liste_kisi.setCurrentIndex(q.comboBox_6_1_2_liste_kisi.findData(user_id))
    lib.find_user_6_1_2()
    lib.save_work()


def test_cok_kopyali_kitap_birden_fazla_uyeye(lib, db, uyarilar):
    db.execute("UPDATE kayitlistesi SET Kopya=2 WHERE Id=6")
    db.commit()
    odunc_ver(lib, "Satranç", 3)
    lib.QtLibrary.comboBox_6_1_1_liste_kitap.setCurrentText("Satranç")
    lib.find_item_6_1_1()
    assert lib.QtLibrary.statusbar.currentMessage() == "Müsait kopya: 1 / 2"
    odunc_ver(lib, "Satranç", 4)
    assert kopya_durumu(6) == (2, 2)
    lib.QtLibrary.comboBox_6_1_1_liste_kitap.setCurrentText("Satranç")
    lib.find_item_6_1_1()
    assert uyarilar[-1] == "Bu kitabın 2 kopyasının hepsi üyelerde!"


def test_ayni_uyeye_ikinci_kopya_verilmez(lib, db, uyarilar):
    db.execute("UPDATE kayitlistesi SET Kopya=3 WHERE Id=6")
    db.commit()
    odunc_ver(lib, "Satranç", 3)
    odunc_ver(lib, "Satranç", 3)
    assert uyarilar[-1] == "Bu kitabın bir kopyası zaten bu üyede. Önce iade alın."
    assert kopya_durumu(6) == (3, 1)


@pytest.mark.parametrize("panel", [Library, Guest])
def test_kitap_listesinde_yeni_kolonlar(app, uyarilar, db, panel):
    db.execute("UPDATE kayitlistesi SET ISBN='9780306406157', Kopya=2, Raf='A-1' WHERE Id=1")
    db.commit()
    p = panel()
    t = p.QtLibrary.tableWidget_2
    p.arama.setText("yol ayrımı")
    basliklar = [t.horizontalHeaderItem(c).text() for c in range(t.columnCount())]
    assert basliklar[-3:] == ["ISBN", "Kopya", "Raf"]
    assert [t.item(0, c).text() for c in (8, 9, 10)] == ["9780306406157", "2", "A-1"]
