## Panellerin arka planı: yaprak fotoğrafı ##
import pytest
from PyQt5.QtWidgets import QApplication

from acodes import arka_plan
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


def test_diger_sayfalarda_yari_saydam_perde(app, uyarilar):
    p = Library()
    goruntu = goster(p, p.QtLibrary.tab_4)
    kenar = goruntu.pixelColor(1180, 690)          # tablonun dışında kalan sayfa zemini
    assert kenar.name() not in ("#f7f8fb", "#ffffff") and kenar.lightness() > 120   # perdeli fotoğraf
    p.close()
