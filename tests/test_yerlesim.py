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


def test_odunc_sayfasi_alanlari_genisler(lib):
    q = lib.QtLibrary
    q.tabWidget.setCurrentWidget(q.tab_6)
    q.tabWidget_6.setCurrentWidget(q.tab_6_1)
    kucuk = genislikler(lib, [q.lineEdit_6_1_adi, q.lineEdit_6_1_kullanici], 1100, 700)
    buyuk = genislikler(lib, [q.lineEdit_6_1_adi, q.lineEdit_6_1_kullanici], 1700, 950)
    assert all(b > k + 150 for k, b in zip(kucuk, buyuk))
    assert q.label_47.isHidden()                                     # başlık artık kartın üstünde


def test_diger_sayfalar_duzende(lib):
    q = lib.QtLibrary
    for sayfa in (q.tab_6_1, q.tab_6_2, q.tab_6_3):
        assert sayfa.layout() is not None
    assert q.pushButton_3_3_Sil_2.isHidden()


def test_guest_kitap_listesi_de_esnek(app):
    g = Guest()
    assert g.QtLibrary.tab_2.layout() is not None
