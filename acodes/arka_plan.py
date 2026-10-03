## Panellerin arka planı: Giriş sekmesindeki yaprak fotoğrafı ##
# Fotoğraf yalnızca Giriş (ana sayfa) sekmesinde, pencereyi kaplayacak şekilde ölçeklenip ortalanarak çizilir
# (taşan kenarlar kırpılır). Diğer sekmelerde düz tema zemini kalır: tablolar ve formlar sade bir yüzeyde durur.

from PyQt5.QtCore import QEvent, QObject, QRect, Qt
from PyQt5.QtGui import QColor, QPainter, QPixmap
from PyQt5.QtWidgets import QTabWidget

from acodes import tema

RESIM = ":/pic/autumn.jpg"      # kaynak dosyası (media_rc) panellerin .ui formlarıyla yüklenir

# Ana sekmelerin sayfaları düz zeminlidir (iç içe sekmelerde tekrar etmez); Giriş sayfası (tab_1) saydamdır
def stil():
    return f"""
#centralwidget {{ background: transparent; }}
QTabWidget::pane {{ background: transparent; }}
QStackedWidget > QWidget {{ background: transparent; }}
QTabWidget#tabWidget > QStackedWidget > QWidget {{ background-color: {tema.SAYFA}; border-radius: 12px; }}
QTabWidget#tabWidget > QStackedWidget > QWidget#tab_1 {{ background: transparent; }}
"""


class ArkaPlan(QObject):
    def __init__(self, pencere):
        super().__init__(pencere)
        self.pencere = pencere
        self.bilesen = pencere.centralWidget()
        self.sekmeler = pencere.findChild(QTabWidget, "tabWidget")
        self.resim = QPixmap(RESIM)
        self.olcekli = None
        self.gosterildi = False
        self.bilesen.installEventFilter(self)
        pencere.installEventFilter(self)
        self.sekmeler.currentChanged.connect(lambda _: self.bilesen.update())

    def fotograf_gorunur(self):
        return self.sekmeler.currentWidget() is self.sekmeler.widget(0)

    def eventFilter(self, nesne, olay):
        if nesne is self.pencere:
            if olay.type() == QEvent.Show and not self.gosterildi:
                # .ui sayfaları sekmelere yerleşmeden önce biçimlendirildiği için "sekme sayfası" kuralları
                # ilk açılışta eşleşmez; pencere ilk gösterildiğinde stil bir kez yeniden uygulanır
                self.gosterildi = True
                self.pencere.setStyleSheet(self.pencere.styleSheet())
            return False
        if olay.type() != QEvent.Paint:
            return False
        if self.resim.isNull() or not self.fotograf_gorunur():
            QPainter(self.bilesen).fillRect(self.bilesen.rect(), QColor(tema.ZEMIN))
            return True
        boyut = self.bilesen.size()
        if self.olcekli is None or self.olcekli[0] != boyut:
            resim = self.resim.scaled(boyut, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.olcekli = (boyut, resim)
        resim = self.olcekli[1]
        kaynak = QRect((resim.width() - boyut.width()) // 2, (resim.height() - boyut.height()) // 2,
                       boyut.width(), boyut.height())
        QPainter(self.bilesen).drawPixmap(self.bilesen.rect(), resim, kaynak)
        return True


def uygula(pencere):
    """Giriş sekmesinde panelin orta bileşenine fotoğrafı çizer; diğer sayfalar düz zeminlidir."""
    pencere.setStyleSheet(pencere.styleSheet() + stil())
    return ArkaPlan(pencere)
