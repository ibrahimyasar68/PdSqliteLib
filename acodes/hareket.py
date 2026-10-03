## Kısa geçiş animasyonları ##
# Sayfa değişince yeni sayfa hafifçe belirir, kenar menüsü daralıp açılırken genişliği yumuşakça değişir,
# tema değişince eski görünüm solarak kaybolur, kaydedilen / ödünç verilen satır kısa süre parlayıp söner.
# Süreler tema.SURE ölçeğinden gelir. Animasyonlar yalnızca pencere ekrandayken çalışır.
# ANIMASYON = False testlerde kapatır; AZALT kullanıcının "Hareketi azalt" tercihidir (Ayarlar > Görünüm).

from PyQt5.QtCore import QEasingCurve, QPersistentModelIndex, QPropertyAnimation, Qt, QVariantAnimation
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QLabel, QWidget

from acodes import tema

ANIMASYON = True
AZALT = False
TERCIH = "gorunum/hareketi_azalt"


def izinli():
    return ANIMASYON and not AZALT


def acik_mi(bilesen):
    return izinli() and bilesen is not None and bilesen.isVisible()


def belir(sayfa):
    """Sayfayı saydamdan görünüre getirir; bitince efekt kaldırılır (çizim yükü kalmasın)."""
    if not acik_mi(sayfa) or sayfa.graphicsEffect() is not None:
        return
    efekt = QGraphicsOpacityEffect(sayfa)
    efekt.setOpacity(0.0)
    sayfa.setGraphicsEffect(efekt)
    animasyon = QPropertyAnimation(efekt, b"opacity", efekt)
    animasyon.setDuration(tema.SURE.kisa)
    animasyon.setStartValue(0.0)
    animasyon.setEndValue(1.0)
    animasyon.setEasingCurve(QEasingCurve.OutCubic)
    animasyon.finished.connect(lambda: sayfa.graphicsEffect() is efekt and sayfa.setGraphicsEffect(None))
    animasyon.start()


def genislige_kay(bilesen, hedef, bitince=None):
    """Bileşenin sabit genişliğini hedefe yumuşakça getirir; animasyon kapalıysa hemen ayarlar.
    Her bileşenin tek animasyonu vardır: yarıda yeni bir istek gelirse eskisi (ve bitince işi) iptal olur."""
    animasyon = getattr(bilesen, "_genislik_animasyonu", None)
    if animasyon is None:
        animasyon = QVariantAnimation(bilesen)
        animasyon.setDuration(tema.SURE.orta)
        animasyon.setEasingCurve(QEasingCurve.OutCubic)
        animasyon.valueChanged.connect(bilesen.setFixedWidth)
        bilesen._genislik_animasyonu = animasyon
    animasyon.stop()
    try:
        animasyon.finished.disconnect()
    except TypeError:               # bağlı iş yok
        pass
    if not acik_mi(bilesen) or bilesen.width() == hedef:
        bilesen.setFixedWidth(hedef)
        if bitince:
            bitince()
        return
    animasyon.setStartValue(bilesen.width())
    animasyon.setEndValue(hedef)
    if bitince:
        animasyon.finished.connect(bitince)
    animasyon.start()


def perde(pencere, goruntu):
    """Pencerenin üstüne eski görünümün resmini koyar ve solarak kaldırır (tema geçişinde yanıp sönme olmasın).
    Animasyon kapalıysa bir şey yapmaz. Perde fareyi engellemez; bitince silinir."""
    if not acik_mi(pencere) or goruntu is None or goruntu.isNull():
        return None
    etiket = QLabel(pencere, objectName="tema_perdesi")
    etiket.setAttribute(Qt.WA_TransparentForMouseEvents)
    etiket.setPixmap(goruntu)
    etiket.setGeometry(pencere.rect())
    efekt = QGraphicsOpacityEffect(etiket)
    etiket.setGraphicsEffect(efekt)
    animasyon = QPropertyAnimation(efekt, b"opacity", etiket)
    animasyon.setDuration(tema.SURE.uzun)
    animasyon.setStartValue(1.0)
    animasyon.setEndValue(0.0)
    animasyon.setEasingCurve(QEasingCurve.InOutQuad)
    animasyon.finished.connect(etiket.deleteLater)
    etiket.show()
    etiket.raise_()
    animasyon.start()
    return etiket


class _Parlama(QWidget):
    """Tablonun görünen alanında bir satırın üstüne vurgu rengini çizer; renk animasyonla söner.
    Satır sıralama ile yer değiştirse de (kalıcı indeks) üstünde kalır."""

    def __init__(self, tablo, satir):
        super().__init__(tablo.viewport())
        self.tablo = tablo
        self.indeks = QPersistentModelIndex(tablo.model().index(satir, 0))
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.guc = 1.0
        self.animasyon = QVariantAnimation(self)
        self.animasyon.setDuration(tema.SURE.parlama)
        self.animasyon.setStartValue(1.0)
        self.animasyon.setEndValue(0.0)
        self.animasyon.setEasingCurve(QEasingCurve.InQuad)
        self.animasyon.valueChanged.connect(self._ilerle)
        self.animasyon.finished.connect(self._bitti)
        self._ilerle(1.0)
        self.show()
        self.animasyon.start()

    def _ilerle(self, guc):
        self.guc = guc
        # Tablo kaydırılınca görünen alandaki çocuklar da kayar: her adımda alanın tamamını kaplar
        self.setGeometry(self.tablo.viewport().rect())
        self.update()

    def _bitti(self):
        if getattr(self.tablo, "_parlama", None) is self:
            self.tablo._parlama = None
        self.deleteLater()

    def paintEvent(self, olay):
        if not self.indeks.isValid():
            return
        satir = self.indeks.row()
        renk = QColor(tema.VURGU)
        renk.setAlphaF((0.35 if tema.KOYU_MU else 0.22) * self.guc)
        p = QPainter(self)
        p.fillRect(0, self.tablo.rowViewportPosition(satir), self.width(), self.tablo.rowHeight(satir), renk)
        p.end()


def satiri_parlat(tablo, satir):
    """Kaydedilen, ödünç verilen veya geri getirilen satırı kısa süre vurgular (değişen yer gözden kaçmasın).
    Aynı tabloda yenisi başlarsa eskisi kaldırılır."""
    if not acik_mi(tablo) or satir is None or not 0 <= satir < tablo.model().rowCount():
        return None
    eski = getattr(tablo, "_parlama", None)
    if eski is not None:
        eski.animasyon.stop()
        eski.deleteLater()
    tablo._parlama = _Parlama(tablo, satir)
    return tablo._parlama


def secili_satiri_parlat(tablo):
    satirlar = tablo.selectionModel().selectedRows() if tablo.selectionModel() else []
    return satiri_parlat(tablo, satirlar[0].row()) if satirlar else None
