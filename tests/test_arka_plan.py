## Panellerin arka planı: giriş ekranındaki fotoğraf ##
import pytest
from PyQt5.QtWidgets import QApplication

from acodes.guest import Guest
from acodes.library import Library


@pytest.mark.parametrize("panel", [Library, Guest])
def test_fotograf_panelin_zemininde(app, uyarilar, panel):
    p = panel()
    assert not p.arka_plan.resim.isNull()
    p.resize(1200, 700)
    p.show()
    QApplication.processEvents()
    goruntu = p.centralWidget().grab().toImage()
    # sayfanın dışında kalan kenarda (sekme çubuğunun solu) fotoğraf görünür: düz tema zemini değil
    renkler = {goruntu.pixel(x, 5) for x in range(0, 200, 10)}
    assert len(renkler) > 3
    p.close()


def test_sayfalar_yari_saydam(app, uyarilar):
    lib = Library()
    assert "rgba(247, 248, 251" in lib.styleSheet() and "#centralwidget { background: transparent; }" in lib.styleSheet()
