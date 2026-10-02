## Panellerin arka planı: Giriş sekmesindeki yaprak fotoğrafı ##
# Fotoğraf pencereyi kaplayacak şekilde ölçeklenip ortalanır (taşan kenarlar kırpılır). Sekme sayfaları
# yarı saydam olduğu için fotoğraf içeriğin arkasından hafifçe görünür; tablolar, kartlar ve formlar
# okunaklı kalsın diye beyaz kalır. Giriş sekmesinde sayfa perdesi yoktur, fotoğraf tam görünür.

from PyQt5.QtCore import QEvent, QObject, QRect, Qt
from PyQt5.QtGui import QPainter, QPixmap

from acodes import tema

RESIM = ":/pic/autumn.jpg"      # kaynak dosyası (media_rc) panellerin .ui formlarıyla yüklenir
SAYFA_SAYDAMLIK = 0.62          # sekme sayfalarının örtücülüğü (0: fotoğraf tam görünür, 1: hiç görünmez)
SAYFA_SAYDAMLIK_KOYU = 0.80     # koyu temada yazılar okunaklı kalsın diye fotoğraf daha az görünür

# Perde ana sekmelerin sayfalarına verilir (iç içe sekmelerde tekrar etmez); Giriş sayfası (tab_1) perdesizdir
def stil():
    return f"""
#centralwidget {{ background: transparent; }}
QTabWidget::pane {{ background: transparent; }}
QStackedWidget > QWidget {{ background: transparent; }}
QTabWidget#tabWidget > QStackedWidget > QWidget {{ background-color: rgba({tema.SAYFA_RGB}, {SAYFA_SAYDAMLIK_KOYU if tema.KOYU_MU else SAYFA_SAYDAMLIK}); }}
QTabWidget#tabWidget > QStackedWidget > QWidget#tab_1 {{ background: transparent; }}
"""


class ArkaPlan(QObject):
    def __init__(self, pencere):
        super().__init__(pencere)
        self.pencere = pencere
        self.bilesen = pencere.centralWidget()
        self.resim = QPixmap(RESIM)
        self.olcekli = None
        self.gosterildi = False
        self.bilesen.installEventFilter(self)
        pencere.installEventFilter(self)

    def eventFilter(self, nesne, olay):
        if nesne is self.pencere:
            if olay.type() == QEvent.Show and not self.gosterildi:
                # .ui sayfaları sekmelere yerleşmeden önce biçimlendirildiği için "sekme sayfası" kuralları
                # ilk açılışta eşleşmez; pencere ilk gösterildiğinde stil bir kez yeniden uygulanır
                self.gosterildi = True
                self.pencere.setStyleSheet(self.pencere.styleSheet())
            return False
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
    """Panelin orta bileşenine fotoğrafı çizer, sayfaları yarı saydam yapar (Giriş sayfası perdesiz)."""
    pencere.setStyleSheet(pencere.styleSheet() + stil())
    return ArkaPlan(pencere)
