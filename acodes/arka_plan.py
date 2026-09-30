## Panellerin arka planı: giriş ekranındaki şelale fotoğrafı ##
# Fotoğraf pencereyi kaplayacak şekilde ölçeklenip ortalanır (taşan kenarlar kırpılır). Sekme sayfaları
# yarı saydam olduğu için fotoğraf içeriğin arkasından hafifçe görünür; tablolar, kartlar ve formlar
# okunaklı kalsın diye beyaz kalır.

from PyQt5.QtCore import QEvent, QObject, QRect, Qt
from PyQt5.QtGui import QPainter, QPixmap

RESIM = ":/pic/login.jpeg"      # kaynak dosyası (media_rc) panellerin .ui formlarıyla yüklenir
SAYFA_SAYDAMLIK = 0.62          # sekme sayfalarının örtücülüğü (0: fotoğraf tam görünür, 1: hiç görünmez)

STIL = f"""
#centralwidget {{ background: transparent; }}
QTabWidget::pane {{ background-color: rgba(247, 248, 251, {SAYFA_SAYDAMLIK}); }}
QTabWidget QTabWidget::pane {{ background: transparent; }}
QStackedWidget > QWidget {{ background: transparent; }}
"""


class ArkaPlan(QObject):
    def __init__(self, bilesen):
        super().__init__(bilesen)
        self.bilesen = bilesen
        self.resim = QPixmap(RESIM)
        self.olcekli = None
        bilesen.installEventFilter(self)

    def eventFilter(self, nesne, olay):
        if olay.type() == QEvent.Paint and not self.resim.isNull():
            boyut = self.bilesen.size()
            if self.olcekli is None or self.olcekli[0] != boyut:
                resim = self.resim.scaled(boyut, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.olcekli = (boyut, resim)
            resim = self.olcekli[1]
            kaynak = QRect((resim.width() - boyut.width()) // 2, (resim.height() - boyut.height()) // 2,
                           boyut.width(), boyut.height())
            QPainter(self.bilesen).drawPixmap(self.bilesen.rect(), resim, kaynak)
            return True
        return False


def uygula(pencere):
    """Panelin orta bileşenine fotoğrafı çizer, sayfaları yarı saydam yapar."""
    pencere.setStyleSheet(pencere.styleSheet() + STIL)
    return ArkaPlan(pencere.centralWidget())
