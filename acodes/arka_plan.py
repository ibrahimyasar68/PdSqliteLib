## Panellerin arka planı: Giriş sekmesindeki yaprak fotoğrafı ##
# Fotoğraf yalnızca Giriş (ana sayfa) sekmesinde, pencereyi kaplayacak şekilde ölçeklenip ortalanarak çizilir
# (taşan kenarlar kırpılır). Diğer sekmelerde düz tema zemini kalır: tablolar ve formlar sade bir yüzeyde durur.
# Giriş sekmesine gelinince / çıkılınca fotoğraf düz zeminle yumuşakça yer değiştirir (birden kaybolmaz).

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QRect, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QTabWidget

from acodes import hareket, tema
import bforms.media_rc  # noqa: F401  (Qt kaynakları: arka plan fotoğrafı)

RESIM = ":/pic/autumn.jpg"      # Qt kaynak dosyasında (bforms/media_rc.py, yukarıda yüklenir)

# Ana sekmelerin sayfaları düz zeminlidir (iç içe sekmelerde tekrar etmez); Giriş sayfası (ana_sayfa) saydamdır
def stil():
    return f"""
#orta_alan {{ background: transparent; }}
QTabWidget::pane {{ background: transparent; }}
QStackedWidget > QWidget {{ background: transparent; }}
QTabWidget#sayfalar > QStackedWidget > QWidget {{ background-color: {tema.SAYFA}; border-radius: {tema.KOSE.buyuk}px; }}
QTabWidget#sayfalar > QStackedWidget > QWidget#ana_sayfa {{ background: transparent; }}
"""


class ArkaPlan(QObject):
    """Giriş sekmesinde panelin orta bileşenine fotoğrafı çizer; diğer sayfalar düz zeminlidir.
    Sayfa zeminlerinin stili (stil()) panelin stil sayfasındadır."""

    def __init__(self, pencere):
        super().__init__(pencere)
        self.pencere = pencere
        self.bilesen = pencere.centralWidget()
        self.sekmeler = pencere.findChild(QTabWidget, "sayfalar")
        self.resim = QPixmap(RESIM)
        self.olcekli = None
        self.gorunurluk = 1.0 if self.fotograf_gorunur() else 0.0     # fotoğrafın saydamlığı (geçişte arada)
        self.gecis = QVariantAnimation(self)
        self.gecis.setDuration(tema.SURE.orta)
        self.gecis.setEasingCurve(QEasingCurve.InOutQuad)
        self.gecis.valueChanged.connect(self._ilerle)
        self.bilesen.installEventFilter(self)
        self.sekmeler.currentChanged.connect(lambda _: self.gec())

    def fotograf_gorunur(self):
        return self.sekmeler.currentWidget() is self.sekmeler.widget(0)

    def gec(self):
        """Fotoğrafı açık sayfaya göre gösterir / gizler; animasyon kapalıysa hemen."""
        hedef = 1.0 if self.fotograf_gorunur() else 0.0
        self.gecis.stop()
        if hareket.acik_mi(self.bilesen) and self.gorunurluk != hedef:
            self.gecis.setStartValue(self.gorunurluk)
            self.gecis.setEndValue(hedef)
            self.gecis.start()
        else:
            self._ilerle(hedef)

    def _ilerle(self, deger):
        self.gorunurluk = deger
        self.bilesen.update()

    def eventFilter(self, nesne, olay):
        if olay.type() != QEvent.Paint:
            return False
        p = QPainter(self.bilesen)
        if self.resim.isNull() or self.gorunurluk <= 0:
            p.fillRect(self.bilesen.rect(), QColor(tema.ZEMIN))
            return True
        if self.gorunurluk < 1:
            p.fillRect(self.bilesen.rect(), QColor(tema.ZEMIN))
            p.setOpacity(self.gorunurluk)
        boyut = self.bilesen.size()
        if self.olcekli is None or self.olcekli[0] != boyut:
            resim = self.resim.scaled(boyut, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.olcekli = (boyut, resim)
        resim = self.olcekli[1]
        kaynak = QRect((resim.width() - boyut.width()) // 2, (resim.height() - boyut.height()) // 2,
                       boyut.width(), boyut.height())
        p.drawPixmap(self.bilesen.rect(), resim, kaynak)
        return True

