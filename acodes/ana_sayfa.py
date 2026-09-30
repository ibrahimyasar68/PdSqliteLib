## Ana sayfa özet panosu ##
# Üstte kütüphanenin resmiyle başlık şeridi, altında tıklanabilir özet kartları ve iki kısa liste.
# Yönetici ve üye panelleri aynı bileşeni farklı kartlar/listelerle kurar.

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QFrame, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QTableWidget,
                             QVBoxLayout, QWidget)

from acodes import tema
from acodes.tablo import tablo_ayarla, tabloya_yaz

STIL = f"""
#ana_sayfa {{ background: transparent; }}
#ana_baslik {{ border-image: url(:/pic/autumn.jpg) 0 0 0 0 stretch stretch; border-radius: 10px; }}
#baslik_yazi {{ color: #FFE14D; font: italic 46px "Monotype Corsiva"; }}
#karsilama {{ color: white; font-size: 17px; font-weight: bold; }}
#kart {{ background-color: {tema.KART}; border: 1px solid {tema.KENAR}; border-radius: 10px; }}
#kart:hover {{ border-color: {tema.VURGU}; }}
#kart_sayi {{ font-size: 30px; font-weight: bold; color: {tema.METIN}; }}
#kart_baslik {{ font-size: 14px; font-weight: bold; color: #334155; }}
#kart_alt {{ font-size: 12px; color: {tema.IKINCIL_METIN}; }}
QGroupBox {{ font-weight: bold; }}
"""


class Kart(QFrame):
    """Büyük sayı + başlık + açıklama; tıklanınca verilen işlevi çağırır."""
    tiklandi = pyqtSignal()

    def __init__(self, baslik, renk, parent=None):
        super().__init__(parent)
        self.setObjectName("kart")
        self.renk = renk
        self.sayi = QLabel("-", objectName="kart_sayi")
        self.baslik = QLabel(baslik, objectName="kart_baslik")
        self.alt = QLabel("", objectName="kart_alt")
        cizgi = QFrame()
        cizgi.setFixedWidth(5)
        cizgi.setStyleSheet(f"background-color: {renk}; border-radius: 2px;")
        self.cizgi = cizgi
        metin = QVBoxLayout()
        metin.setSpacing(2)
        for w in (self.sayi, self.baslik, self.alt):
            metin.addWidget(w)
        duzen = QHBoxLayout(self)
        duzen.setContentsMargins(12, 12, 16, 12)
        duzen.addWidget(cizgi)
        duzen.addSpacing(8)
        duzen.addLayout(metin, 1)
        self.setMinimumHeight(105)

    def ayarla(self, sayi, alt="", renk=None):
        self.sayi.setText(str(sayi))
        self.alt.setText(alt)
        self.cizgi.setStyleSheet(f"background-color: {renk or self.renk}; border-radius: 2px;")

    def mousePressEvent(self, olay):
        if olay.button() == Qt.LeftButton:
            self.tiklandi.emit()

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
    def __init__(self, kartlar, listeler, cikis_butonu, parent=None):
        """kartlar: [(anahtar, başlık, renk)]; listeler: [(anahtar, başlık, kolonlar, boş metin)].
        cikis_butonu: .ui'daki Oturumu Kapat butonu başlık şeridine taşınır."""
        super().__init__(parent)
        self.setObjectName("ana_sayfa")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(STIL)

        baslik = QFrame(objectName="ana_baslik")
        baslik.setFixedHeight(150)
        self.karsilama = QLabel("", objectName="karsilama")
        yazi = QVBoxLayout()
        yazi.addStretch()
        yazi.addWidget(QLabel("Yaşar Kütüphanesi", objectName="baslik_yazi"))
        yazi.addWidget(self.karsilama)
        yazi.addStretch()
        serit = QHBoxLayout(baslik)
        serit.setContentsMargins(28, 10, 28, 10)
        serit.addLayout(yazi, 1)
        cikis_butonu.setParent(baslik)
        cikis_butonu.setMinimumSize(170, 44)
        cikis_butonu.setMaximumSize(220, 44)
        serit.addWidget(cikis_butonu, 0, Qt.AlignVCenter)

        self.kartlar = {}
        kart_satiri = QHBoxLayout()
        kart_satiri.setSpacing(14)
        for anahtar, ad, renk in kartlar:
            self.kartlar[anahtar] = Kart(ad, renk)
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
        self.karsilama.setText(f"Hoş geldiniz, {kullanici}  ·  {rol}")


def ana_sayfayi_yerlestir(ui, ana_sayfa):
    """.ui'daki eski ana sayfa içeriğini (resim, başlık, buton kutusu) gizleyip panoyu sekmeye yerleştirir."""
    for eski in (ui.label, ui.label_32, ui.label_log_on, ui.verticalLayoutWidget):
        eski.hide()
    duzen = QVBoxLayout(ui.tab_1)
    duzen.setContentsMargins(0, 0, 0, 0)
    duzen.addWidget(ana_sayfa)
