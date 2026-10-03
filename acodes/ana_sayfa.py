## Ana sayfa özet panosu ##
# Üstte başlık şeridi (panelin arka plan fotoğrafı üzerinde), altında tıklanabilir özet kartları ve iki kısa liste.
# Yönetici ve üye panelleri aynı bileşeni farklı kartlar/listelerle kurar.

from PyQt5.QtCore import QEasingCurve, Qt, QVariantAnimation, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QFrame, QGraphicsDropShadowEffect, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                             QLabel, QTableWidget, QVBoxLayout, QWidget)

from acodes import hareket, ikonlar, tema
from acodes.tablo import tablo_ayarla, tabloya_yaz

def stil():
    return f"""
#ana_sayfa {{ background: transparent; }}
#ana_baslik {{ background: transparent; }}
#hosgeldin {{ color: white; font-size: {tema.YAZI.karsilama}px; font-weight: {tema.YARI_KALIN}; }}
#karsilama {{ color: rgba(255, 255, 255, 0.88); font-size: {tema.YAZI.alt_baslik}px; font-weight: {tema.ORTA}; }}
#kart {{ background-color: {tema.KART}; border: 1px solid {tema.KENAR}; border-radius: {tema.KOSE.orta}px; }}
#kart:hover {{ border-color: {tema.VURGU}; }}
#kart_baslik {{ font-size: {tema.YAZI.ince}px; font-weight: {tema.ORTA}; color: {tema.IKINCIL_METIN}; }}
#kart_sayi {{ font-size: {tema.YAZI.gosterge}px; font-weight: {tema.YARI_KALIN}; color: {tema.METIN}; }}
#kart_alt {{ font-size: {tema.YAZI.ince}px; color: {tema.IKINCIL_METIN}; }}
QGroupBox {{ font-weight: {tema.YARI_KALIN}; }}
#ana_sayfa QTableWidget, #ana_sayfa QHeaderView {{ color: {tema.METIN}; }}
"""


class Kart(QFrame):
    """Üstte başlık, büyük sayı ve açıklama; sağ üstte rengin açık tonunda yuvarlak zeminli ikon.
    Tıklanabilir kartlar üstüne gelince gölgesi yumuşakça büyüyerek öne çıkar. Sayı ilk görünüşte 0'dan sayarak gelir."""
    tiklandi = pyqtSignal()
    IKON_EN = 44

    def __init__(self, baslik, renk, ikon="kitap", parent=None):
        super().__init__(parent)
        self.setObjectName("kart")
        self.renk = renk
        self.ikon_adi = ikon
        self.baslik = QLabel(baslik, objectName="kart_baslik")
        self.sayi = QLabel("-", objectName="kart_sayi")
        self.alt = QLabel("", objectName="kart_alt")
        self.ikon = QLabel(objectName="kart_ikon")
        self.ikon.setFixedSize(self.IKON_EN, self.IKON_EN)
        self.ikon.setAlignment(Qt.AlignCenter)
        metin = QVBoxLayout()
        metin.setSpacing(2)
        for w in (self.baslik, self.sayi, self.alt):
            metin.addWidget(w)
        duzen = QHBoxLayout(self)
        duzen.setContentsMargins(16, 14, 16, 14)
        duzen.addLayout(metin, 1)
        duzen.addWidget(self.ikon, 0, Qt.AlignTop)
        self.setMinimumHeight(105)
        self.golge = QGraphicsDropShadowEffect(self)
        self.golge.setBlurRadius(22)
        self.golge.setOffset(0, 4)
        self.golge.setColor(QColor(0, 0, 0, 90 if tema.KOYU_MU else 40))
        self.golge.setEnabled(False)
        self.setGraphicsEffect(self.golge)
        self.golge_guc = 0.0
        self.golge_animasyonu = QVariantAnimation(self)
        self.golge_animasyonu.setDuration(tema.SURE.kisa)
        self.golge_animasyonu.setEasingCurve(QEasingCurve.OutCubic)
        self.golge_animasyonu.valueChanged.connect(self._golge_ciz)
        self.golge_animasyonu.finished.connect(lambda: self.golge.setEnabled(self.golge_guc > 0))
        self.hedef = None
        self.sayildi = False
        self._renklendir(renk)

    def _renklendir(self, renk):
        zemin = QColor(renk)
        zemin.setAlphaF(0.24 if tema.KOYU_MU else 0.12)
        self.ikon.setStyleSheet(f"background-color: rgba({zemin.red()}, {zemin.green()}, {zemin.blue()}, "
                                f"{zemin.alphaF():.2f}); border-radius: {self.IKON_EN // 2}px;")
        self.ikon.setPixmap(ikonlar.ikon(self.ikon_adi, renk).pixmap(22, 22))
        self.ikon.renk = renk

    def ayarla(self, sayi, alt="", renk=None):
        self.hedef = sayi
        self.alt.setText(alt)
        self._renklendir(renk or self.renk)
        if not self.sayildi and self.isVisible():
            self._say()
            return
        sayac = getattr(self.sayi, "_sayac", None)
        if sayac is not None:
            if sayac.endValue() == sayi:                  # zaten bu sayıya doğru sayıyor
                return
            sayac.stop()
            self.sayi._sayac = None
        self.sayi.setText(str(sayi))

    def mousePressEvent(self, olay):
        if olay.button() == Qt.LeftButton:
            self.tiklandi.emit()

    def _say(self):
        self.sayildi = True
        hareket.say(self.sayi, self.hedef)

    def showEvent(self, olay):
        super().showEvent(olay)
        if not self.sayildi and self.hedef is not None:
            self._say()

    def _golge_ciz(self, guc):
        self.golge_guc = guc
        self.golge.setBlurRadius(22 * guc)
        self.golge.setOffset(0, 4 * guc)
        self.golge.setColor(QColor(0, 0, 0, round((90 if tema.KOYU_MU else 40) * guc)))

    def _golgeye_git(self, hedef):
        if not hareket.acik_mi(self):
            self._golge_ciz(hedef)
            self.golge.setEnabled(hedef > 0)
            return
        self.golge.setEnabled(True)
        self.golge_animasyonu.stop()
        self.golge_animasyonu.setStartValue(self.golge_guc)
        self.golge_animasyonu.setEndValue(float(hedef))
        self.golge_animasyonu.start()

    def enterEvent(self, olay):
        if self.toolTip() != "":                          # yalnızca tıklanabilir kartlar
            self._golgeye_git(1.0)
        super().enterEvent(olay)

    def leaveEvent(self, olay):
        self._golgeye_git(0.0)
        super().leaveEvent(olay)

    def tiklanabilir(self, islev, ipucu):
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(ipucu)
        self.tiklandi.connect(islev)


class Liste(QGroupBox):
    def __init__(self, baslik, kolonlar, bos_metin, parent=None):
        super().__init__(baslik, parent)
        self.tablo = QTableWidget(0, len(kolonlar))
        self.tablo.setHorizontalHeaderLabels(kolonlar)
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tablo.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tablo_ayarla(self.tablo, bos_metin=bos_metin)
        QVBoxLayout(self).addWidget(self.tablo)

    def doldur(self, satirlar, vurgulu=(), veri=None):
        tabloya_yaz(self.tablo, satirlar, vurgulu=vurgulu, veri=veri)


class AnaSayfa(QWidget):
    def __init__(self, kartlar, listeler, parent=None):
        """kartlar: [(anahtar, başlık, renk, ikon)]; listeler: [(anahtar, başlık, kolonlar, boş metin)].
        Kütüphane adı ve Oturumu Kapat sol kenar menüsündedir; burada karşılama yazısı kalır."""
        super().__init__(parent)
        self.setObjectName("ana_sayfa")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(stil())

        # Başlık şeridi: ortada "Hoş geldiniz", altında kullanıcı adı · yetki (fotoğrafın üzerinde)
        baslik = QFrame(objectName="ana_baslik")
        baslik.setFixedHeight(150)
        self.hosgeldin = QLabel("Hoş geldiniz", objectName="hosgeldin")
        self.karsilama = QLabel("", objectName="karsilama")
        yazi = QVBoxLayout()
        yazi.setSpacing(2)
        yazi.addStretch()
        for etiket in (self.hosgeldin, self.karsilama):
            etiket.setAlignment(Qt.AlignCenter)
            golge = QGraphicsDropShadowEffect(etiket)     # fotoğraf üzerinde okunaklı olsun
            golge.setBlurRadius(14)
            golge.setOffset(0, 2)
            golge.setColor(QColor(0, 0, 0, 200))
            etiket.setGraphicsEffect(golge)
            yazi.addWidget(etiket)
        yazi.addStretch()
        serit = QHBoxLayout(baslik)
        serit.setContentsMargins(28, 6, 28, 6)
        serit.addLayout(yazi, 1)

        self.kartlar = {}
        kart_satiri = QHBoxLayout()
        kart_satiri.setSpacing(14)
        for anahtar, ad, renk, ikon in kartlar:
            self.kartlar[anahtar] = Kart(ad, renk, ikon)
            kart_satiri.addWidget(self.kartlar[anahtar])

        self.listeler = {}
        alt = QGridLayout()
        alt.setHorizontalSpacing(14)
        for i, (anahtar, ad, kolonlar, bos) in enumerate(listeler):
            self.listeler[anahtar] = Liste(ad, kolonlar, bos)
            alt.addWidget(self.listeler[anahtar], 0, i)

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(16, 14, 16, 14)
        duzen.setSpacing(14)
        duzen.addWidget(baslik)
        duzen.addLayout(kart_satiri)
        duzen.addLayout(alt, 1)

    def karsila(self, kullanici, rol):
        self.karsilama.setText(f"{kullanici}  ·  {rol}")


def ana_sayfayi_yerlestir(ui, ana_sayfa):
    """Panoyu ana sayfa sekmesine yerleştirir."""
    duzen = QVBoxLayout(ui.tab_1)
    duzen.setContentsMargins(0, 0, 0, 0)
    duzen.addWidget(ana_sayfa)
