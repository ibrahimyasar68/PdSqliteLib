## Geçiş animasyonları: satır parlaması ve "Hareketi azalt" ##
import pytest
from PyQt5.QtTest import QTest

from conftest import sec
from acodes import hareket, tema, tercihler
from acodes.library import Library


@pytest.fixture
def animasyonlu(monkeypatch):
    monkeypatch.setattr(hareket, "ANIMASYON", True)
    monkeypatch.setattr(hareket, "AZALT", False)


@pytest.fixture
def lib(app, uyarilar, animasyonlu):
    l = Library()
    l.resize(1300, 800)
    l.show()
    yield l
    l.close()


def secili_satir(tablo):
    return tablo.selectionModel().selectedRows()[0].row()


def test_kaydedilen_kitap_satiri_parlar_ve_soner(lib):
    q = lib.QtLibrary
    q.tabWidget.setCurrentWidget(q.tab_3)
    q.tabWidget_3.setCurrentWidget(lib.kitaplar)
    k = lib.kitaplar
    k.yeni()
    k.alan["Adi"].setText("Parlayan Kitap")
    k.kaydet()
    parlama = k.tablo._parlama
    assert parlama is not None and parlama.indeks.row() == secili_satir(k.tablo)
    assert parlama.geometry() == k.tablo.viewport().rect()
    QTest.qWait(tema.SURE.parlama + 200)
    assert k.tablo._parlama is None                                     # bitince kendini kaldırır


def test_odunc_verilen_satir_parlar(lib):
    o = lib.odunc
    lib.disaridakileri_goster()
    sec(o.kitap, "Satranç")
    o.uye.setCurrentIndex(o.uye.findData(3))
    o.odunc_ver()
    assert o.tablo._parlama is not None and o.tablo.item(o.tablo._parlama.indeks.row(), 0).text() == "Satranç"


def test_yeni_parlama_eskisini_kaldirir(lib):
    tablo = lib.QtLibrary.tableWidget_2
    lib.QtLibrary.tabWidget.setCurrentWidget(lib.QtLibrary.tab_2)
    ilk = hareket.satiri_parlat(tablo, 0)
    ikinci = hareket.satiri_parlat(tablo, 1)
    assert ilk is not ikinci and tablo._parlama is ikinci
    assert hareket.satiri_parlat(tablo, tablo.rowCount()) is None       # olmayan satır


def test_animasyon_kapaliyken_parlama_yok(app, uyarilar):
    l = Library()
    l.show()
    assert hareket.satiri_parlat(l.QtLibrary.tableWidget_2, 0) is None  # testlerde ANIMASYON = False
    l.close()


def test_hareketi_azalt_ayari(lib, monkeypatch):
    kutu = lib.ayarlar.gorunum.hareket
    assert not kutu.isChecked()
    kutu.setChecked(True)
    assert hareket.AZALT and not hareket.izinli() and tercihler.mantiksal(hareket.TERCIH)
    sayfa = lib.QtLibrary.tab_2
    lib.QtLibrary.tabWidget.setCurrentWidget(sayfa)
    assert sayfa.graphicsEffect() is None                               # sayfa beklemeden görünür
    lib.yan_menu.btn_daralt.click()
    assert lib.yan_menu.width() == lib.yan_menu.minimumWidth()          # menü hemen daralır
    lib.yan_menu.btn_daralt.click()
    lib.QtLibrary.statusbar.showMessage("Deneme silindi")
    lib.bildirim.kaybol()
    assert lib.bildirim.kutu.isHidden()                                 # bildirim solmadan kaybolur
    kutu.setChecked(False)
    assert not hareket.AZALT and not tercihler.mantiksal(hareket.TERCIH)
