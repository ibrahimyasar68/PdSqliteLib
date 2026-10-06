## Evet / Hayır onay penceresi ##
# Açık pencerenin üstünü karartır, ortasında temaya uygun bir kart çıkar: kart hafifçe büyüyerek ve belirerek
# gelir, karartma onunla birlikte koyulaşır; cevap verilince ikisi birlikte söner. Geri alınamayan işlemlerde
# (tehlikeli=True) kartın ikonu ve Evet butonu kırmızıdır, Enter yanlışlıkla onaylamasın diye Hayır seçilidir.
# Dönüş değeri QMessageBox.Yes / QMessageBox.No'dur (çağıranlar bununla karşılaştırır).

from PySide6.QtCore import QEasingCurve, QRect, QRectF, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton,
                             QVBoxLayout)

from acodes import hareket, ikonlar, tema

KART_EN = 420
KUCUK_OLCEK = 0.94          # kart bu ölçekten tam boyuta büyür


def stil():
    t, Y, K = tema, tema.YAZI, tema.KOSE
    return f"""
#onay_karti {{ background-color: {t.KART}; border: 1px solid {t.KENAR}; border-radius: {K.buyuk}px; }}
#onay_baslik {{ color: {t.METIN}; font-size: {Y.alt_baslik}px; font-weight: {t.YARI_KALIN}; }}
#onay_metin {{ color: {t.IKINCIL_METIN}; font-size: {Y.metin}px; }}
#onay_ikon {{ background-color: {t.VURGU_ACIK}; border-radius: 20px; }}
#onay_ikon[tehlikeli="true"] {{ background-color: {t.TEHLIKE_ACIK}; }}
QPushButton#onay_evet[tehlikeli="true"] {{ background-color: {t.TEHLIKE_KOYU}; }}
QPushButton#onay_evet[tehlikeli="true"]:hover {{ background-color: {t.TEHLIKE}; }}
"""


def karartma_rengi(guc=1.0):
    """Kartın arkasındaki karartma: kenar menüsünün lacivert tonu, koyu temada daha koyu."""
    renk = QColor(*(int(k) for k in tema.MENU_ZEMIN_RGB.split(",")))
    renk.setAlphaF((0.55 if tema.KOYU_MU else 0.38) * guc)
    return renk


class OnayPenceresi(QDialog):
    def __init__(self, msj, parent=None, tehlikeli=False, baslik="Onay", evet="Evet", hayir="Hayır"):
        super().__init__(parent)
        self.setWindowTitle(baslik)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setStyleSheet(stil())
        self.sonuc = QMessageBox.No
        self.guc = 1.0              # 0: kart küçük ve saydam, karartma yok; 1: tam görünür
        self.resim = None           # animasyon sürerken kartın yerine ölçeklenerek çizilen görüntüsü
        self.animasyon = QVariantAnimation(self)
        self.animasyon.setEasingCurve(QEasingCurve.OutCubic)
        self.animasyon.valueChanged.connect(self._ilerle)
        self.animasyon.finished.connect(self._animasyon_bitti)

        self.kart = QFrame(objectName="onay_karti")
        self.kart.setFixedWidth(KART_EN)
        ikon = QLabel(objectName="onay_ikon")
        ikon.setProperty("tehlikeli", tehlikeli)
        ikon.setFixedSize(40, 40)
        ikon.setAlignment(Qt.AlignCenter)
        ikon.setPixmap(ikonlar.ikon("uyari" if tehlikeli else "bilgi",
                                    tema.TEHLIKE_YAZI if tehlikeli else tema.VURGU_YAZI)
                      .pixmap(QSize(22, 22), self.devicePixelRatioF()))     # Retina ekranda da net
        self.baslik = QLabel(baslik, objectName="onay_baslik")
        self.metin = QLabel(msj, objectName="onay_metin")
        self.metin.setWordWrap(True)
        self.metin.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.btn_evet = QPushButton(evet, objectName="onay_evet")
        self.btn_evet.setProperty("tehlikeli", tehlikeli)
        self.btn_hayir = QPushButton(hayir, objectName="onay_hayir")
        self.btn_hayir.setProperty("rol", "ikincil")
        for buton, cevap in ((self.btn_evet, QMessageBox.Yes), (self.btn_hayir, QMessageBox.No)):
            buton.setCursor(Qt.PointingHandCursor)
            buton.setMinimumHeight(36)
            buton.clicked.connect(lambda _, c=cevap: self.cevapla(c))
        varsayilan = self.btn_hayir if tehlikeli else self.btn_evet
        varsayilan.setDefault(True)
        varsayilan.setFocus()

        yazi = QVBoxLayout()
        yazi.setSpacing(6)
        yazi.addWidget(self.baslik)
        yazi.addWidget(self.metin)
        ust = QHBoxLayout()
        ust.setSpacing(14)
        ust.addWidget(ikon, 0, Qt.AlignTop)
        ust.addLayout(yazi, 1)
        alt = QHBoxLayout()
        alt.addStretch()
        alt.addWidget(self.btn_hayir)
        alt.addWidget(self.btn_evet)
        duzen = QVBoxLayout(self.kart)
        duzen.setContentsMargins(22, 20, 22, 18)
        duzen.setSpacing(18)
        duzen.addLayout(ust)
        duzen.addLayout(alt)
        dis = QVBoxLayout(self)
        dis.setContentsMargins(24, 24, 24, 24)
        dis.addWidget(self.kart, 0, Qt.AlignCenter)
        hareket.etkilesimleri_kur(self)

    def yerlestir(self):
        """Açık pencerenin iç alanını kaplar (kart sığmıyorsa kartın boyuna büyür, pencerenin ortasında kalır)."""
        self.adjustSize()
        en_az = self.sizeHint()
        pencere = self.parentWidget().window() if self.parentWidget() else None
        if pencere is not None and pencere.isVisible():
            alan = pencere.geometry()
        else:
            ekran = (self.screen() or QApplication.primaryScreen()).availableGeometry()
            alan = QRect(0, 0, en_az.width(), en_az.height())
            alan.moveCenter(ekran.center())
        if alan.width() < en_az.width() or alan.height() < en_az.height():
            merkez = alan.center()
            alan.setSize(alan.size().expandedTo(en_az))
            alan.moveCenter(merkez)
        self.setGeometry(alan)

    def exec(self):
        self.yerlestir()
        return super().exec()

    def showEvent(self, olay):
        super().showEvent(olay)
        if hareket.acik_mi(self):
            self._canlandir(0.0, 1.0, tema.SURE.orta)
        else:
            self._ilerle(1.0)

    def _canlandir(self, bas, son, sure):
        self.layout().activate()
        self.resim = self.kart.grab()
        self.kart.setVisible(False)
        self.animasyon.stop()
        self.animasyon.setDuration(sure)
        self.animasyon.setStartValue(bas)
        self.animasyon.setEndValue(son)
        self._ilerle(bas)
        self.animasyon.start()

    def _ilerle(self, guc):
        self.guc = guc
        self.update()

    def _animasyon_bitti(self):
        self.resim = None
        if self.guc >= 1:
            self.kart.setVisible(True)
            (self.btn_hayir if self.btn_hayir.isDefault() else self.btn_evet).setFocus()
        else:
            super().done(self.sonuc)

    def cevapla(self, sonuc):
        if self.animasyon.state() == QVariantAnimation.Running and self.guc < 1:
            return                  # kapanırken ikinci tıklama
        self.sonuc = sonuc
        if hareket.acik_mi(self):
            self._canlandir(self.guc, 0.0, tema.SURE.kisa)
        else:
            super().done(sonuc)

    def reject(self):               # Esc: Hayır
        self.cevapla(QMessageBox.No)

    def accept(self):
        self.cevapla(QMessageBox.Yes)

    def paintEvent(self, olay):
        p = QPainter(self)
        p.fillRect(self.rect(), karartma_rengi(self.guc))
        if self.resim is None:
            return
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.setOpacity(self.guc)
        olcek = KUCUK_OLCEK + (1 - KUCUK_OLCEK) * self.guc
        hedef = QRectF(self.kart.geometry())
        merkez = hedef.center()
        hedef.setSize(hedef.size() * olcek)
        hedef.moveCenter(merkez)
        p.drawPixmap(hedef, self.resim, QRectF(self.resim.rect()))


def onay(msj, parent=None, tehlikeli=False):
    # Açık pencereye bağlı açılır: Mac'te ayrı bir masaüstü alanına geçip panelin kaybolmasını önler
    return OnayPenceresi(msj, parent or QApplication.activeWindow(), tehlikeli).exec()
