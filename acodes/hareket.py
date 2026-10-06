## Kısa geçiş animasyonları ##
# Sayfa değişince yeni sayfa hafifçe belirir, kenar menüsü daralıp açılırken genişliği yumuşakça değişir,
# tema değişince eski görünüm solarak kaybolur, kaydedilen / ödünç verilen satır kısa süre parlayıp söner.
# Ayrıca: yanlış girişte kart sallanır, hatalı alanın çerçevesi kırmızıdan söner, seçili menü / segment vurgusu
# kayarak gider, sayılar sayarak gelir, gecikme rozeti bir kez nabız gibi atar. Alt bölüm değişince yeni bölüm
# seçilen yönden kayarak gelir, kılavuz konuları yükseklikleri değişerek açılıp kapanır.
# Süreler tema.SURE ölçeğinden gelir. Animasyonlar yalnızca pencere ekrandayken çalışır.
# ANIMASYON = False testlerde kapatır; AZALT kullanıcının "Hareketi azalt" tercihidir (Ayarlar > Görünüm).

from PySide6.QtCore import (QEasingCurve, QEvent, QObject, QPersistentModelIndex, QPoint, QPropertyAnimation, QRect,
                          QSequentialAnimationGroup, Qt, QTimer, QVariantAnimation)
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect, QLabel, QWidget

from acodes import tema

ANIMASYON = True
AZALT = False
TERCIH = "gorunum/hareketi_azalt"
SINIRSIZ = 16777215          # Qt'nin en büyük bileşen boyutu (QWIDGETSIZE_MAX)


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


def kayarak_belir(sayfa, yon, kayma=16):
    """Sayfa yon tarafından (1: sağdan, -1: soldan) birkaç piksel kayarak ve belirerek gelir (alt bölüm anahtarı:
    içerik, seçili zeminin kaydığı yöne akar). Bitince sayfa yerine döner, efekt kaldırılır."""
    if not yon or not acik_mi(sayfa) or sayfa.graphicsEffect() is not None:
        return None
    yer = sayfa.pos()
    efekt = QGraphicsOpacityEffect(sayfa)
    efekt.setOpacity(0.0)
    sayfa.setGraphicsEffect(efekt)
    animasyon = QVariantAnimation(efekt)
    animasyon.setDuration(tema.SURE.orta)
    animasyon.setStartValue(0.0)
    animasyon.setEndValue(1.0)
    animasyon.setEasingCurve(QEasingCurve.OutCubic)

    def adim(t):
        efekt.setOpacity(t)
        sayfa.move(yer.x() + round(yon * kayma * (1 - t)), yer.y())

    def bitti():
        sayfa.move(yer)
        if sayfa.graphicsEffect() is efekt:
            sayfa.setGraphicsEffect(None)

    animasyon.valueChanged.connect(adim)
    animasyon.finished.connect(bitti)
    adim(0.0)
    animasyon.start()
    return animasyon


def yukseklikle_goster(bilesen, goster):
    """Bileşen yüksekliği sıfırdan açılarak görünür veya kapanarak gizlenir (kılavuz konuları). Altındakiler
    birden zıplamaz, yumuşakça yer değiştirir. Animasyon kapalıysa hemen gösterilir / gizlenir."""
    eski = getattr(bilesen, "_yukseklik_animasyonu", None)
    if eski is not None:
        eski.stop()
        bilesen._yukseklik_animasyonu = None
    kap = bilesen.parentWidget()
    if not acik_mi(kap):
        bilesen.setMaximumHeight(SINIRSIZ)
        bilesen.setVisible(goster)
        return None
    if goster:
        bas = bilesen.height() if bilesen.isVisible() else 0
        bilesen.setMaximumHeight(bas)
        bilesen.show()
        if kap.layout() is not None:
            kap.layout().activate()         # gizliyken bilinmeyen genişlik yerleşsin (yükseklik ona bağlı)
        en = bilesen.width()
        hedef = bilesen.heightForWidth(en) if bilesen.hasHeightForWidth() else -1
        hedef = hedef if hedef > 0 else bilesen.sizeHint().height()
    else:
        if bilesen.isHidden():
            return None
        bas, hedef = bilesen.height(), 0
    if bas == hedef:
        bilesen.setMaximumHeight(SINIRSIZ)
        bilesen.setVisible(goster)
        return None
    animasyon = QVariantAnimation(bilesen)
    animasyon.setDuration(tema.SURE.orta)
    animasyon.setStartValue(bas)
    animasyon.setEndValue(hedef)
    animasyon.setEasingCurve(QEasingCurve.OutCubic)
    animasyon.valueChanged.connect(bilesen.setMaximumHeight)

    def bitti():
        bilesen._yukseklik_animasyonu = None
        bilesen.setMaximumHeight(SINIRSIZ)      # pencere daralınca yazı yeniden kırılabilsin
        bilesen.setVisible(goster)

    animasyon.finished.connect(bitti)
    bilesen._yukseklik_animasyonu = animasyon
    animasyon.start()
    return animasyon


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
    onceki = getattr(bilesen, "_genislik_bitince", None)
    if onceki is not None:          # yarıda kalan isteğin bitince işi iptal
        animasyon.finished.disconnect(onceki)
        bilesen._genislik_bitince = None
    if not acik_mi(bilesen) or bilesen.width() == hedef:
        bilesen.setFixedWidth(hedef)
        if bitince:
            bitince()
        return
    animasyon.setStartValue(bilesen.width())
    animasyon.setEndValue(hedef)
    if bitince:
        animasyon.finished.connect(bitince)
        bilesen._genislik_bitince = bitince
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


def salla(bilesen):
    """Yanlış girişte bileşeni yatayda kısa süre sallar (sönen titreşim), sonra yerine bırakır."""
    if not acik_mi(bilesen) or getattr(bilesen, "_salla", None) is not None:
        return None
    yer = bilesen.pos()
    animasyon = QVariantAnimation(bilesen)
    animasyon.setDuration(tema.SURE.uzun)
    animasyon.setStartValue(0.0)
    animasyon.setEndValue(1.0)

    def adim(t):
        import math
        bilesen.move(yer.x() + round(8 * (1 - t) * math.sin(t * math.pi * 6)), yer.y())

    def bitti():
        bilesen.move(yer)
        bilesen._salla = None

    animasyon.valueChanged.connect(adim)
    animasyon.finished.connect(bitti)
    bilesen._salla = animasyon
    animasyon.start()
    return animasyon


def pencere_belir(pencere):
    """Üst düzey pencereyi saydamdan görünüre getirir (girişten panele geçiş)."""
    if not acik_mi(pencere):
        return None
    animasyon = QPropertyAnimation(pencere, b"windowOpacity", pencere)
    animasyon.setDuration(tema.SURE.orta)
    animasyon.setStartValue(0.0)
    animasyon.setEndValue(1.0)
    animasyon.setEasingCurve(QEasingCurve.OutCubic)
    animasyon.finished.connect(lambda: pencere.setWindowOpacity(1.0))
    pencere.setWindowOpacity(0.0)
    animasyon.start()
    return animasyon


def acilir_pencere_belir(pencere, kayma=8):
    """Açılır pencere (hızlı arama) birkaç piksel aşağıdan kayarak ve belirerek gelir."""
    if not acik_mi(pencere):
        return None
    hedef = pencere.pos()
    konum = QPropertyAnimation(pencere, b"pos", pencere)
    konum.setDuration(tema.SURE.kisa)
    konum.setStartValue(hedef + QPoint(0, kayma))
    konum.setEndValue(hedef)
    konum.setEasingCurve(QEasingCurve.OutCubic)
    saydam = pencere_belir(pencere)
    if saydam is not None:
        saydam.setDuration(tema.SURE.kisa)
    pencere.move(hedef + QPoint(0, kayma))
    konum.start()
    return konum


def hata_vurgula(alan):
    """Hatalı alanın çerçevesi tehlike renginde belirir, kısa süre kalır ve normale söner.
    Animasyon kapalıyken çerçeve kısa süre kırmızı kalıp normale döner (hata yine görünsün)."""
    eski = getattr(alan, "_hata_animasyonu", None)
    if eski is not None:
        eski.stop()
    stil = getattr(alan, "_ozgun_stil", None)
    if stil is None:
        stil = alan._ozgun_stil = alan.styleSheet()

    def boya(renk):
        alan.setStyleSheet(stil + f"\n{type(alan).__name__} {{ border-color: {renk.name().upper()}; }}")

    def bitti():
        alan.setStyleSheet(stil)
        alan._hata_animasyonu = None

    if not izinli():
        boya(QColor(tema.TEHLIKE))
        QTimer.singleShot(tema.SURE.parlama * 2, alan, bitti)     # alan bu arada silinirse çağrılmaz
        return None
    animasyon = QVariantAnimation(alan)
    animasyon.setDuration(tema.SURE.parlama * 2)
    animasyon.setStartValue(QColor(tema.TEHLIKE))
    animasyon.setKeyValueAt(0.5, QColor(tema.TEHLIKE))          # yarı süre kırmızı kalır
    animasyon.setEndValue(QColor(tema.KENAR_GIRDI))
    animasyon.valueChanged.connect(boya)
    animasyon.finished.connect(bitti)
    alan._hata_animasyonu = animasyon
    boya(QColor(tema.TEHLIKE))
    animasyon.start()
    return animasyon


def nabiz(bilesen, tekrar=2):
    """Bileşen dikkat çekmek için birkaç kez soluklaşıp geri gelir (sürekli değil); bitince efekt kalkar."""
    if not acik_mi(bilesen) or bilesen.graphicsEffect() is not None:
        return None
    efekt = QGraphicsOpacityEffect(bilesen)
    bilesen.setGraphicsEffect(efekt)
    grup = QSequentialAnimationGroup(efekt)
    for _ in range(tekrar):
        for bas, son in ((1.0, 0.3), (0.3, 1.0)):
            a = QPropertyAnimation(efekt, b"opacity")
            a.setDuration(tema.SURE.uzun)
            a.setStartValue(bas)
            a.setEndValue(son)
            a.setEasingCurve(QEasingCurve.InOutSine)
            grup.addAnimation(a)
    grup.finished.connect(lambda: bilesen.graphicsEffect() is efekt and bilesen.setGraphicsEffect(None))
    grup.start()
    return grup


def say(etiket, hedef, bicim=str):
    """Etiketteki sayı 0'dan hedefe sayarak gelir; animasyon kapalıysa hemen yazılır."""
    eski = getattr(etiket, "_sayac", None)
    if eski is not None:
        eski.stop()
        etiket._sayac = None
    if not acik_mi(etiket) or not isinstance(hedef, int) or hedef <= 0:
        etiket.setText(bicim(hedef))
        return None
    animasyon = QVariantAnimation(etiket)
    animasyon.setDuration(tema.SURE.sayac)
    animasyon.setStartValue(0)
    animasyon.setEndValue(hedef)
    animasyon.setEasingCurve(QEasingCurve.OutCubic)
    animasyon.valueChanged.connect(lambda d: etiket.setText(bicim(int(d))))
    def bitti():
        etiket.setText(bicim(hedef))
        etiket._sayac = None

    animasyon.finished.connect(bitti)
    etiket._sayac = animasyon
    etiket.setText(bicim(0))
    animasyon.start()
    return animasyon


class KayanVurgu(QObject):
    """Buton grubunda seçili olanın arkasındaki vurgu: seçim değişince yeni butonun altına kayarak gider.
    Butonlar yer / boyut değiştirince (menü daralırken) vurgu animasyonsuz izler. Vurgunun görünümü kabın stil
    sayfasında nesne adıyla verilir; seçili butonun kendi zemini saydam olmalıdır."""

    def __init__(self, kap, grup, ad):
        super().__init__(kap)
        self.kap = kap
        self.grup = grup
        self.cerceve = QFrame(kap, objectName=ad)
        self.cerceve.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.cerceve.lower()
        self.cerceve.hide()
        self.animasyon = QPropertyAnimation(self.cerceve, b"geometry", self)
        self.animasyon.setDuration(tema.SURE.orta)
        self.animasyon.setEasingCurve(QEasingCurve.OutCubic)
        grup.buttonToggled.connect(lambda buton, secili: secili and self.hedefle(True))
        kap.installEventFilter(self)
        for buton in grup.buttons():
            buton.installEventFilter(self)

    def hedef(self):
        buton = self.grup.checkedButton()
        if buton is None or not buton.isVisibleTo(self.kap):
            return None
        return QRect(buton.mapTo(self.kap, QPoint()), buton.size())

    def hedefle(self, animasyonlu=False):
        alan = self.hedef()
        if alan is None:
            self.cerceve.hide()
            return
        if animasyonlu and acik_mi(self.kap) and self.cerceve.isVisible() and self.cerceve.geometry() != alan:
            self.animasyon.stop()
            self.animasyon.setStartValue(self.cerceve.geometry())
            self.animasyon.setEndValue(alan)
            self.animasyon.start()
        else:
            self.animasyon.stop()
            self.cerceve.setGeometry(alan)
        self.cerceve.show()
        self.cerceve.lower()

    def eventFilter(self, nesne, olay):
        if olay.type() in (QEvent.Resize, QEvent.Move, QEvent.Show, QEvent.LayoutRequest):
            if self.animasyon.state() != QPropertyAnimation.Running:
                self.hedefle()
        return False
