## Esnek yerleşim testleri: sayfalar pencere büyüyünce genişler ##
import pytest

from acodes.guest import Guest
from acodes.library import Library


def genislikler(panel, bilesenler, en, boy):
    panel.resize(en, boy)
    panel.show()
    from PyQt5.QtWidgets import QApplication
    QApplication.processEvents()
    return [b.width() for b in bilesenler]


@pytest.fixture
def lib(app, uyarilar):
    return Library()


def test_kitap_listesi_tablosu_buyur(lib):
    q = lib.QtLibrary
    q.tabWidget.setCurrentWidget(q.tab_2)
    kucuk, = genislikler(lib, [q.tableWidget_2], 1100, 700)
    buyuk, = genislikler(lib, [q.tableWidget_2], 1700, 950)
    assert q.tab_2.layout() is not None and buyuk >= kucuk + 300


def test_odunc_ekrani_tablosu_buyur(lib):
    q = lib.QtLibrary
    q.tabWidget.setCurrentWidget(q.tab_6)
    kucuk, = genislikler(lib, [lib.odunc.tablo], 1100, 700)
    buyuk, = genislikler(lib, [lib.odunc.tablo], 1700, 950)
    assert buyuk >= kucuk + 200


def test_guest_kitap_listesi_de_esnek(app):
    g = Guest()
    assert g.QtLibrary.tab_2.layout() is not None


def test_odunc_ekraninda_liste_ustte_kartlar_altta(lib):
    q = lib.QtLibrary
    o = lib.odunc
    q.tabWidget.setCurrentWidget(q.tab_6)
    genislikler(lib, [], 1280, 760)
    ver = o.btn_ver.parentWidget()
    iade = o.btn_iade.parentWidget()
    tablo_alt = o.tablo.mapTo(o, o.tablo.rect().bottomLeft()).y()
    assert ver.mapTo(o, ver.rect().topLeft()).y() > tablo_alt                  # kartlar listenin altında
    assert ver.mapTo(o, ver.rect().topLeft()).y() == iade.mapTo(o, iade.rect().topLeft()).y()   # yan yana
    assert o.tablo.width() > o.width() - 60                                   # liste tam genişlikte
    assert not o.tablo.isColumnHidden(3)                                      # telefon da görünür
    assert o.tablo.horizontalScrollBar().maximum() == 0                       # yatay kaydırma yok
