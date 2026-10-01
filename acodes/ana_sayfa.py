## Ana sayfa özet panosu ##
# Üstte başlık şeridi (panelin arka plan fotoğrafı üzerinde), altında tıklanabilir özet kartları ve iki kısa liste.
# Yönetici ve üye panelleri aynı bileşeni farklı kartlar/listelerle kurar.

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QFrame, QGraphicsDropShadowEffect, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
                             QLabel, QTableWidget, QVBoxLayout, QWidget)

from acodes import tema
from acodes.tablo import tablo_ayarla, tabloya_yaz

STIL = f"""
#ana_sayfa {{ background: transparent; }}
#ana_baslik {{ background: transparent; }}
#hosgeldin {{ color: #FDBA74; font-family: "{tema.BASLIK_YAZISI}"; font-size: 84px; font-weight: normal;
               font-style: normal; }}
#karsilama {{ color: white; font-size: 19px; font-weight: bold; }}
#kart {{ background-color: {tema.KART}; border: 1px solid {tema.KENAR}; border-radius: 10px; }}
#kart:hover {{ border-color: {tema.VURGU}; }}
#kart_sayi {{ font-size: 30px; font-weight: bold; color: {tema.METIN}; }}
#kart_baslik {{ font-size: 16px; font-weight: bold; color: #334155; }}
#kart_alt {{ font-size: 14px; color: {tema.IKINCIL_METIN}; }}
QGroupBox {{ font-weight: bold; }}
#ana_sayfa QTableWidget, #ana_sayfa QHeaderView {{ color: {tema.METIN}; }}
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
    def __init__(self, kartlar, listeler, parent=None):
        """kartlar: [(anahtar, başlık, renk)]; listeler: [(anahtar, başlık, kolonlar, boş metin)].
        Kütüphane adı ve Oturumu Kapat sol kenar menüsündedir; burada karşılama yazısı kalır."""
        super().__init__(parent)
        self.setObjectName("ana_sayfa")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(STIL)

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
        self.karsilama.setText(f"{kullanici}  ·  {rol}")


def ana_sayfayi_yerlestir(ui, ana_sayfa):
    """.ui'daki eski ana sayfa içeriğini (resim, başlık, buton kutusu) gizleyip panoyu sekmeye yerleştirir."""
    for eski in (ui.label, ui.label_32, ui.label_log_on, ui.verticalLayoutWidget):
        eski.hide()
    duzen = QVBoxLayout(ui.tab_1)
    duzen.setContentsMargins(0, 0, 0, 0)
    duzen.addWidget(ana_sayfa)
