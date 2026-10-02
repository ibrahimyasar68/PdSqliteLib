## Klavye kısayolları: tuşa basılmış gibi denenir ##
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from acodes.guest import Guest
from acodes.library import Library


def ac(pencere):
    pencere.show()
    QApplication.setActiveWindow(pencere)       # ekransız testte pencere kendiliğinden etkin olmaz
    return pencere


def bas(pencere, tus):
    dizi = QKeySequence(tus)
    QTest.keyClick(pencere, Qt.Key(dizi[0] & ~Qt.KeyboardModifierMask), Qt.KeyboardModifiers(dizi[0] & Qt.KeyboardModifierMask))


@pytest.fixture
def lib(app, uyarilar):
    p = ac(Library())
    yield p
    p.close()


def test_ctrl_rakam_menu_bolumleri(lib):
    sekmeler = lib.QtLibrary.tabWidget
    bas(lib, "Ctrl+2")
    assert sekmeler.currentWidget() is lib.QtLibrary.tab_2
    bas(lib, "Ctrl+7")
    assert sekmeler.currentWidget() is lib.ayarlar
    bas(lib, "Ctrl+1")
    assert sekmeler.currentIndex() == 0


def test_ctrl_f_acik_sayfanin_aramasina_gider(lib):
    q = lib.QtLibrary
    q.tabWidget.setCurrentWidget(q.tab_6)
    bas(lib, QKeySequence.Find)
    assert lib.focusWidget() is lib.odunc.arama
    q.tabWidget.setCurrentWidget(q.tab_4)
    bas(lib, QKeySequence.Find)
    assert lib.focusWidget() is lib.filtre.combo["Turu"]           # yazılabilir liste odağı kendisi alır
    q.tabWidget.setCurrentWidget(lib.ayarlar)                     # aramasız sayfa: Kitap Listesi'ne gider
    bas(lib, QKeySequence.Find)
    assert q.tabWidget.currentWidget() is q.tab_2 and lib.focusWidget() is lib.arama


def test_kitap_kayit_kisayollari(lib, db):
    q = lib.QtLibrary
    k = lib.kitaplar
    lib.kitap_duzenle(6)
    k.alan["Adi"].setText("DEĞİŞTİ")
    bas(lib, "Esc")                                               # vazgeç: değişiklik geri alınır
    assert k.alan["Adi"].text() == "Satranç"
    bas(lib, QKeySequence.New)
    assert k.kitap_id is None and k.alan["Adi"].text() == ""
    k.alan["Adi"].setText("Kısayolla Eklenen")
    bas(lib, QKeySequence.Save)
    assert db.execute("SELECT COUNT(*) FROM kayitlistesi WHERE Adi='Kısayolla Eklenen'").fetchone()[0] == 1
    assert "(" in k.btn_kaydet.toolTip()                          # ipucunda kısayol yazar
    q.tabWidget.setCurrentWidget(q.tab_2)                         # başka sayfadayken çalışmaz
    k.alan["Adi"].setText("X")
    bas(lib, QKeySequence.Save)
    assert db.execute("SELECT COUNT(*) FROM kayitlistesi WHERE Adi='X'").fetchone()[0] == 0


def test_uye_panelinde_kisayollar(app, uyarilar):
    g = ac(Guest())
    bas(g, "Ctrl+5")
    assert g.QtLibrary.tabWidget.currentWidget() is g.kitaplarim
    bas(g, QKeySequence.Find)
    assert g.QtLibrary.tabWidget.currentWidget() is g.QtLibrary.tab_2 and g.focusWidget() is g.arama
    g.close()
