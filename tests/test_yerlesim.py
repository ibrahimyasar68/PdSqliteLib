## Esnek yerleşim testleri: sayfalar pencere büyüyünce genişler ##
import pytest

from acodes.guest import Guest
from acodes.library import Library


def genislikler(panel, bilesenler, en, boy):
    panel.resize(en, boy)
    panel.show()
    from PySide6.QtWidgets import QApplication
    QApplication.processEvents()
    return [b.width() for b in bilesenler]


@pytest.fixture
def lib(app, uyarilar):
    return Library()


def test_kitap_listesi_tablosu_buyur(lib):
    q = lib
    q.sekmeler.setCurrentWidget(q.liste)
    kucuk, = genislikler(lib, [q.liste.tablo], 1100, 700)
    buyuk, = genislikler(lib, [q.liste.tablo], 1700, 950)
    assert q.liste.layout() is not None and buyuk >= kucuk + 300


def test_odunc_ekrani_tablosu_buyur(lib):
    q = lib
    q.sekmeler.setCurrentWidget(q.verme)
    kucuk, = genislikler(lib, [lib.odunc.tablo], 1100, 700)
    buyuk, = genislikler(lib, [lib.odunc.tablo], 1700, 950)
    assert buyuk >= kucuk + 200


def test_guest_kitap_listesi_de_esnek(app):
    g = Guest()
    assert g.liste.layout() is not None


def test_odunc_ekraninda_liste_ustte_kartlar_altta(lib):
    q = lib
    o = lib.odunc
    q.sekmeler.setCurrentWidget(q.verme)
    genislikler(lib, [], 1280, 760)
    ver = o.btn_ver.parentWidget()
    iade = o.btn_iade.parentWidget()
    tablo_alt = o.tablo.mapTo(o, o.tablo.rect().bottomLeft()).y()
    assert ver.mapTo(o, ver.rect().topLeft()).y() > tablo_alt                  # kartlar listenin altında
    assert ver.mapTo(o, ver.rect().topLeft()).y() == iade.mapTo(o, iade.rect().topLeft()).y()   # yan yana
    assert o.tablo.width() > o.width() - 60                                   # liste tam genişlikte
    assert not o.tablo.isColumnHidden(3)                                      # telefon da görünür
    assert o.tablo.horizontalScrollBar().maximum() == 0                       # yatay kaydırma yok


def test_kitap_kayitta_liste_ustte_form_altta(lib):
    q = lib
    k = lib.kitaplar
    q.sekmeler.setCurrentWidget(q.kayit)
    genislikler(lib, [], 1280, 760)
    tablo_alt = k.tablo.mapTo(k, k.tablo.rect().bottomLeft()).y()
    kutu = k.alan["Adi"].parentWidget()
    assert kutu.mapTo(k, kutu.rect().topLeft()).y() > tablo_alt                # form listenin altında
    assert kutu.mapTo(k, kutu.rect().topLeft()).y() == k.ek.mapTo(k, k.ek.rect().topLeft()).y()   # kartlar yan yana
    assert k.tablo.width() > k.width() - 60                                    # liste tam genişlikte
    assert k.tablo.horizontalScrollBar().maximum() == 0
    k.kolonlar.denetle()
    assert not k.kolonlar.soru.isVisible()                                     # liste sığıyor, soru çıkmaz
