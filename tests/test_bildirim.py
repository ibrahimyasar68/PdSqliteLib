## Kısa süreli bildirimler testleri ##
import datetime

import pytest
from PyQt5.QtTest import QTest

from acodes import bildirim
from acodes.guest import Guest
from acodes.library import Library


@pytest.mark.parametrize("metin,tur", [
    ("'Yeni Kitap' kaydedildi", "basari"), ("Yol Ayrımı güncellendi.", "basari"),
    ("İşlem kaydedildi. Teslim tarihi: 14.10.2026", "basari"),
    ("Seçim yapınız", "uyari"), ("Temizlenecek Veri Yok!", "uyari"),
    ("Teslim süresi (15 gün) geçmiş 2 kitap var.", "uyari"),
    ("Müsait kopya: 1 / 2", "bilgi"),
])
def test_tur_bul(metin, tur):
    assert bildirim.tur_bul(metin) == tur


def test_sure():
    assert bildirim.sure_ms("Tamam") == 2500
    assert bildirim.sure_ms("x" * 500) == 7000


@pytest.fixture
def lib(app, uyarilar):
    l = Library()
    l.resize(1200, 700)
    return l


def test_durum_cubugu_gizli_mesaj_bildirimde(lib):
    assert lib.QtLibrary.statusbar.isHidden()
    lib.QtLibrary.statusbar.showMessage("'Deneme' kaydedildi", 2000)
    kutu = lib.bildirim.kutu
    assert not kutu.isHidden() and kutu.text() == "'Deneme' kaydedildi" and lib.bildirim.tur == "basari"
    assert kutu.y() + kutu.height() <= lib.height()                     # pencerenin içinde, altta
    assert lib.QtLibrary.statusbar.currentMessage() == "'Deneme' kaydedildi"


def test_bildirim_kaybolur(lib):
    lib.QtLibrary.statusbar.showMessage("Seçim yapınız")
    lib.bildirim.kaybol()
    QTest.qWait(600)                                                    # solma animasyonu
    assert lib.bildirim.kutu.isHidden()


def test_bos_mesaj_gostermez(lib):
    lib.bildirim.kutu.hide()
    lib.QtLibrary.statusbar.clearMessage()
    assert lib.bildirim.kutu.isHidden()


def test_gercek_islemde_bildirim(lib):
    lib.kitaplar.alan["Adi"].setText("bildirim kitabı")
    lib.kitaplar.kaydet()
    assert lib.bildirim.kutu.text() == "'Bildirim Kitabı' kaydedildi" and lib.bildirim.tur == "basari"
    lib.find_item_6_1_1()                                                # seçim yapılmadan Bul
    assert lib.bildirim.kutu.text() == "Seçim yapınız" and lib.bildirim.tur == "uyari"


def test_geciken_kitap_acilista_uyari(app, uyarilar, db):
    eski = str(datetime.date.today() - datetime.timedelta(days=30))
    db.execute("INSERT INTO follow VALUES ('3','1',?,'10:00','out','','')", (eski,))
    db.commit()
    l = Library()
    assert "geçmiş 1 kitap" in l.bildirim.kutu.text() and l.bildirim.tur == "uyari"


def test_guest_panelinde_de_bildirim(app):
    g = Guest()
    assert g.QtLibrary.statusbar.isHidden()
    g.QtLibrary.statusbar.showMessage("Liste görüntülendi.")
    assert g.bildirim.kutu.text() == "Liste görüntülendi."
