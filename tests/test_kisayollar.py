## Klavye kısayolları: tuşa basılmış gibi denenir ##
import pytest
from PySide6.QtGui import QKeySequence
from PySide6.QtTest import QTest

from acodes.guest import Guest
from acodes.library import Library


def ac(pencere):
    pencere.show()
    pencere.windowHandle().requestActivate()    # ekransız testte pencere kendiliğinden etkin olmaz
    assert QTest.qWaitForWindowActive(pencere)
    return pencere


def bas(pencere, tus):
    dizi = QKeySequence(tus)
    QTest.keyClick(pencere, dizi[0].key(), dizi[0].keyboardModifiers())     # Qt 6: dizi öğesi QKeyCombination


@pytest.fixture
def lib(app, uyarilar):
    p = ac(Library())
    yield p
    p.close()


def test_ctrl_rakam_menu_bolumleri(lib):
    sekmeler = lib.sekmeler
    bas(lib, "Ctrl+2")
    assert sekmeler.currentWidget() is lib.liste
    bas(lib, "Ctrl+7")
    assert sekmeler.currentWidget() is lib.ayarlar
    bas(lib, "Ctrl+1")
    assert sekmeler.currentIndex() == 0


def test_ctrl_f_acik_sayfanin_aramasina_gider(lib):
    q = lib
    q.sekmeler.setCurrentWidget(q.verme)
    bas(lib, QKeySequence.Find)
    assert lib.focusWidget() is lib.odunc.arama
    q.sekmeler.setCurrentWidget(q.filtre)
    bas(lib, QKeySequence.Find)
    assert lib.focusWidget() is lib.filtre.combo["Turu"]           # yazılabilir liste odağı kendisi alır
    q.sekmeler.setCurrentWidget(lib.ayarlar)                     # aramasız sayfa: Kitap Listesi'ne gider
    bas(lib, QKeySequence.Find)
    assert q.sekmeler.currentWidget() is q.liste and lib.focusWidget() is lib.liste.arama


def test_kitap_kayit_kisayollari(lib, db):
    q = lib
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
    q.sekmeler.setCurrentWidget(q.liste)                         # başka sayfadayken çalışmaz
    k.alan["Adi"].setText("X")
    bas(lib, QKeySequence.Save)
    assert db.execute("SELECT COUNT(*) FROM kayitlistesi WHERE Adi='X'").fetchone()[0] == 0


def test_uye_panelinde_kisayollar(app, uyarilar):
    g = ac(Guest())
    bas(g, "Ctrl+5")
    assert g.sekmeler.currentWidget() is g.kitaplarim
    bas(g, QKeySequence.Find)
    assert g.sekmeler.currentWidget() is g.liste and g.focusWidget() is g.liste.arama
    g.close()
