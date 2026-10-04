## Guest > Kitaplarım sekmesi testleri ##
import datetime

import pytest

from conftest import UYE_SIFRE
from acodes.guest import Guest
from acodes.login import Login
from PySide6.QtGui import QColor
from acodes import tema
from database import odunc

BUGUN = datetime.date.today()


def gun_once(n):
    return str(BUGUN - datetime.timedelta(days=n))


def odunc_ekle(db, user_id, book_id, verilis, durum="out", iade=""):
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES (?,?,?,?,?,?,?)",
               (str(user_id), str(book_id), verilis, "10:00 ", durum, iade, ""))
    db.commit()


@pytest.mark.parametrize("gun_once_verildi,yazi", [(10, "5 gün kaldı"), (15, "Bugün teslim"), (18, "3 gün gecikti")])
def test_kalan_gun_yazi(gun_once_verildi, yazi):
    assert odunc.kalan_gun_yazi(gun_once(gun_once_verildi)) == yazi


def test_uye_odunc_sadece_o_uyenin(db):
    odunc_ekle(db, 3, 1, "2025-01-01", "in", "2025-01-05")
    odunc_ekle(db, 3, 2, gun_once(3))
    odunc_ekle(db, 4, 6, gun_once(3))
    kayitlar = odunc.uye_odunc("ayse1")
    assert [k[0] for k in kayitlar] == ["Esir Şehrin İnsanları", "Yol Ayrımı"]   # dışarıdaki önce
    assert odunc.uye_odunc("olmayan") == []


@pytest.fixture
def guest(app, db):
    odunc_ekle(db, 3, 1, "2025-01-01", "in", "2025-01-25")
    odunc_ekle(db, 3, 2, gun_once(20))       # gecikmiş
    odunc_ekle(db, 3, 6, gun_once(4))        # süresi var
    odunc_ekle(db, 4, 7, gun_once(30))       # başka üyenin
    g = Guest()
    g.user_name("ayse1")
    return g


def sekme_adi(g):
    q = g
    return q.sekmeler.tabText(q.sekmeler.indexOf(g.kitaplarim))


def test_elimdeki_ve_eski_kitaplar(guest):
    k = guest.kitaplarim
    assert k.elimdeki.rowCount() == 2 and k.gecmis.rowCount() == 1
    durumlar = {k.elimdeki.item(r, 0).text(): k.elimdeki.item(r, 4).text() for r in range(2)}
    assert durumlar == {"Esir Şehrin İnsanları": "5 gün gecikti", "Satranç": "11 gün kaldı"}
    gecikmis = next(r for r in range(2) if k.elimdeki.item(r, 0).text() == "Esir Şehrin İnsanları")
    assert k.elimdeki.item(gecikmis, 0).background().color() == QColor(tema.GECIKME_ARKA)
    assert [k.gecmis.item(0, c).text() for c in (0, 2, 3, 4)] == ["Yol Ayrımı", "01.01.2025", "25.01.2025", "24"]
    assert k.ozet.text() == "Şu an sizde 2 kitap var. 1 tanesinin teslim süresi geçti, lütfen iade edin."


def test_sekme_adi_ve_giris_uyarisi(guest):
    assert sekme_adi(guest) == "Kitaplarım (1 gecikmiş)"
    assert "Teslim süresi geçmiş kitabınız var" in guest.statusBar().currentMessage()


def test_iade_sonrasi_sekme_guncellenir(guest, db):
    db.execute("UPDATE follow SET status='in', indate=? WHERE bookId='2'", (str(BUGUN),))
    db.commit()
    guest.sekmeler.setCurrentWidget(guest.kitaplarim)
    assert sekme_adi(guest) == "Kitaplarım" and guest.kitaplarim.elimdeki.rowCount() == 1


def test_kitabi_olmayan_uye(app, db):
    g = Guest()
    g.user_name("ayse2")
    assert g.kitaplarim.ozet.text() == "Şu an sizde ödünç kitap yok." and sekme_adi(g) == "Kitaplarım"


def test_admin_panelinde_kitaplarim_yok(app, uyarilar):
    from acodes.library import Library
    q = Library()
    assert all(q.sekmeler.tabText(i) != "Kitaplarım" for i in range(q.sekmeler.count()))


def test_giris_yapan_uye_kendi_kitaplarini_gorur(app, db):
    odunc_ekle(db, 3, 6, gun_once(1))
    w = Login()
    w.QtLogin.lineEdit_kullanci_adi.setText("ayse1")
    w.QtLogin.lineEdit_parola.setText(UYE_SIFRE)
    w.giris()
    assert w.guest.kitaplarim.elimdeki.item(0, 0).text() == "Satranç"
