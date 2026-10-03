## Panellerin arka planı: yaprak fotoğrafı ##
import pytest
from PyQt5.QtWidgets import QApplication

from acodes import arka_plan, tema
from acodes.guest import Guest
from acodes.library import Library


def goster(panel, sayfa=None):
    if sayfa is not None:
        panel.QtLibrary.tabWidget.setCurrentWidget(sayfa)
    panel.resize(1200, 700)
    panel.show()
    QApplication.processEvents()
    return panel.centralWidget().grab().toImage()


def renk(goruntu, x, y):
    return goruntu.pixelColor(x, y).name()


@pytest.mark.parametrize("panel", [Library, Guest])
def test_giris_sayfasinda_fotograf_perdesiz(app, uyarilar, panel):
    p = panel()
    assert arka_plan.RESIM == ":/pic/autumn.jpg" and not p.arka_plan.resim.isNull()
    goruntu = goster(p)                            # ilk açılış (sekme değiştirilmeden)
    # başlık şeridinde tema zemini değil, fotoğrafın kendisi görünür (koyu yaprak renkleri)
    sol = p.yan_menu.width() + 40                 # menünün sağı, karşılama yazısının üstü
    renkler = {renk(goruntu, x, 20) for x in range(sol, 1150, 40)}
    assert "#f7f8fb" not in renkler and len(renkler) > 5
    assert all(goruntu.pixelColor(x, 20).lightness() < 200 for x in range(sol, 1150, 80))
    p.close()


def test_diger_sayfalarda_duz_zemin(app, uyarilar):
    p = Library()
    goruntu = goster(p, p.QtLibrary.tab_2)
    en = goruntu.width()
    assert renk(goruntu, en - 18, 350) == tema.SAYFA.lower()       # sayfanın tablo dışında kalan kenarı
    assert renk(goruntu, en - 3, 350) == tema.ZEMIN.lower()        # sayfanın dışı: fotoğraf yok
    p.QtLibrary.tabWidget.setCurrentIndex(0)                       # Giriş'e dönünce fotoğraf yeniden çizilir
    QApplication.processEvents()
    goruntu = p.centralWidget().grab().toImage()
    assert goruntu.pixelColor(en - 3, 350).lightness() < 200
    p.close()
