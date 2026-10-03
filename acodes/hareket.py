## Kısa geçiş animasyonları ##
# Sayfa değişince yeni sayfa hafifçe belirir, kenar menüsü daralıp açılırken genişliği yumuşakça değişir.
# Animasyonlar yalnızca pencere ekrandayken çalışır; testlerde ANIMASYON = False ile kapatılır (sonuç hemen görünür).

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QVariantAnimation
from PyQt5.QtWidgets import QGraphicsOpacityEffect

ANIMASYON = True
SAYFA_MS = 140
GENISLIK_MS = 180


def acik_mi(bilesen):
    return ANIMASYON and bilesen is not None and bilesen.isVisible()


def belir(sayfa):
    """Sayfayı saydamdan görünüre getirir; bitince efekt kaldırılır (çizim yükü kalmasın)."""
    if not acik_mi(sayfa) or sayfa.graphicsEffect() is not None:
        return
    efekt = QGraphicsOpacityEffect(sayfa)
    efekt.setOpacity(0.0)
    sayfa.setGraphicsEffect(efekt)
    animasyon = QPropertyAnimation(efekt, b"opacity", efekt)
    animasyon.setDuration(SAYFA_MS)
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
        animasyon.setDuration(GENISLIK_MS)
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
