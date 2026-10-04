## Ödünç takibi testleri: teslim tarihi, gecikme, dışarıdaki kitaplar ve geçmiş ##
import datetime

import pytest

from acodes.library import Library
from PyQt5.QtGui import QColor
from acodes import tema
from database import odunc

BUGUN = datetime.date.today()
G = datetime.date(2026, 1, 1)


def gun_once(n):
    return str(BUGUN - datetime.timedelta(days=n))


def odunc_ekle(db, user_id, book_id, verilis, durum="out", iade=""):
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES (?,?,?,?,?,?,?)",
               (str(user_id), str(book_id), verilis, "10:00 ", durum, iade, "11:00 " if iade else ""))
    db.commit()


# --- Tarih hesapları (sabit tarihlerle) ---

def test_teslim_tarihi():
    assert odunc.ODUNC_SURESI_GUN == 15
    assert odunc.teslim_tarihi("2026-01-01") == datetime.date(2026, 1, 16)
    assert odunc.teslim_tarihi("") is None and odunc.teslim_tarihi(None) is None


@pytest.mark.parametrize("iade,bugun,gecikme", [
    (None, datetime.date(2026, 1, 16), 0),     # son gün: gecikme yok
    (None, datetime.date(2026, 1, 20), 4),
    ("2026-01-10", datetime.date(2026, 3, 1), 0),   # zamanında iade
    ("2026-01-25", datetime.date(2026, 3, 1), 9),   # geç iade
])
def test_gecikme_gunu(iade, bugun, gecikme):
    assert odunc.gecikme_gunu("2026-01-01", iade, bugun=bugun) == gecikme


def test_gun_sayisi():
    assert odunc.gun_sayisi("2026-01-01", bugun=datetime.date(2026, 1, 11)) == 10
    assert odunc.gun_sayisi("2026-01-01", "2026-01-04") == 3
    assert odunc.gun_sayisi("hatalı") is None


def test_tarih_yazi():
    assert odunc.tarih_yazi("2026-01-05") == "05.01.2026"
    assert odunc.tarih_yazi(datetime.date(2026, 9, 29)) == "29.09.2026"
    assert odunc.tarih_yazi("") == ""


def test_geciken_sayisi(db):
    odunc_ekle(db, 3, 1, gun_once(20))                                   # gecikmiş
    odunc_ekle(db, 3, 2, gun_once(3))                                    # süresi var
    odunc_ekle(db, 4, 3, gun_once(40), "in", gun_once(10))               # geç iade edilmiş (sayılmaz)
    assert odunc.geciken_sayisi() == 1


def test_odunc_gecmisi_filtreleri(db):
    odunc_ekle(db, 3, 1, "2025-01-01", "in", "2025-01-10")
    odunc_ekle(db, 3, 2, "2025-02-01")
    odunc_ekle(db, 4, 1, "2025-03-01")
    assert [s[2] for s in odunc.odunc_gecmisi()] == ["2025-03-01", "2025-02-01", "2025-01-01"]
    assert len(odunc.odunc_gecmisi(user_id=3)) == 2
    assert len(odunc.odunc_gecmisi(book_id=1)) == 2
    assert len(odunc.odunc_gecmisi(user_id=3, book_id=1)) == 1
    assert [u[0] for u in odunc.odunc_alan_uyeler()] == [3, 4]


# --- Arayüz ---

@pytest.fixture
def lib(app, uyarilar):
    return Library()


def sekme_adi(lib):
    q = lib.QtLibrary
    return q.tabWidget.tabText(q.tabWidget.indexOf(q.tab_6))


def test_sekme_adinda_gecikme_sayisi(app, uyarilar, db):
    odunc_ekle(db, 4, 2, gun_once(20))
    lib = Library()
    assert sekme_adi(lib) == "Kitap Verme (1 gecikmiş)"
    lib.odunc.tablo.selectRow(0)
    lib.odunc.iade_al()
    assert sekme_adi(lib) == "Kitap Verme"


def test_gecmis_sekmesi(lib, db):
    odunc_ekle(db, 3, 1, "2025-01-01", "in", "2025-01-25")
    odunc_ekle(db, 3, 2, gun_once(20))
    odunc_ekle(db, 4, 3, gun_once(2))
    g = lib.gecmis
    g.yenile()
    q = lib.QtLibrary
    assert q.tabWidget_6.tabText(q.tabWidget_6.indexOf(g)) == "Ödünç Geçmişi"
    assert g.tablo.rowCount() == 3 and g.ozet.text() == "3 kayıt, 2 dışarıda"
    durumlar = [g.tablo.item(r, 6).text() for r in range(3)]
    assert durumlar == ["Dışarıda", "Gecikmiş (5 gün)", "İade edildi (9 gün geç)"]
    assert g.tablo.item(1, 0).background().color() == QColor(tema.GECIKME_ARKA)

    g.durum.setCurrentText("Gecikmiş")
    assert g.tablo.rowCount() == 1
    g.durum.setCurrentText("İade edildi")
    assert g.tablo.rowCount() == 1 and g.tablo.item(0, 4).text() == "25.01.2025"
    g.durum.setCurrentText("Tümü")
    g.uye.setCurrentIndex(g.uye.findData(3))
    assert g.tablo.rowCount() == 2
    g.yenile()                                   # yenilemede seçim korunur
    assert g.uye.currentData() == 3 and g.tablo.rowCount() == 2
    g.uye.setCurrentIndex(0)
    g.kitap.setCurrentIndex(g.kitap.findData(3))
    assert g.tablo.rowCount() == 1


def test_silinmis_kitap_gecmiste_gorunur(lib, db):
    odunc_ekle(db, 3, 999, "2025-01-01", "in", "2025-01-05")
    lib.gecmis.yenile()
    assert lib.gecmis.tablo.item(0, 0).text() == "(silinmiş kitap)"
