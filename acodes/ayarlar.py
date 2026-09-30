## Panellerdeki "Ayarlar" sekmesi ##
# Ana sayfadaki işlem butonları (kullanıcılar, yedekleme, şifre) burada gruplanır; ana sayfa sade kalır.
# Her bölüm: başlık, butonlar [(metin, işlev, ipucu)] ve isteğe bağlı bilgi satırları.

import os

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (QFormLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget)

STIL = """
#ayarlar_ic { background-color: rgb(244, 246, 250); }
QGroupBox { font: bold 13pt "Verdana"; color: rgb(40, 50, 70); background-color: white;
            border: 1px solid rgb(210, 214, 222); border-radius: 10px; margin-top: 14px; padding: 16px 12px 12px 12px; }
QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; }
QLabel { font: 11pt "Verdana"; color: rgb(40, 50, 70); background: transparent; }
QLabel[rol="deger"] { color: rgb(20, 20, 20); }
QPushButton { font: 11pt "Verdana"; color: rgb(30, 30, 30); background-color: rgb(255, 236, 140);
              border: 1px solid rgb(200, 170, 60); border-radius: 8px; padding: 9px 16px; min-width: 150px; }
QPushButton:hover { background-color: rgb(255, 224, 90); }
QPushButton:pressed { background-color: rgb(240, 200, 60); }
"""


class Bolum(QGroupBox):
    def __init__(self, baslik, butonlar=(), bilgiler=None, parent=None):
        """butonlar: [(metin, işlev, ipucu)]; bilgiler: [(etiket, değer)] döndüren fonksiyon (yenilenebilir)."""
        super().__init__(baslik, parent)
        self.bilgi_kaynagi = bilgiler
        self.butonlar = {}
        duzen = QVBoxLayout(self)
        if butonlar:
            satir = QHBoxLayout()
            for metin, islev, ipucu in butonlar:
                b = QPushButton(metin)
                b.setCursor(Qt.PointingHandCursor)
                b.setToolTip(ipucu)
                b.clicked.connect(islev)
                satir.addWidget(b)
                self.butonlar[metin] = b
            satir.addStretch()
            duzen.addLayout(satir)
        self.form = QFormLayout()
        self.form.setLabelAlignment(Qt.AlignRight)
        self.form.setHorizontalSpacing(16)
        duzen.addLayout(self.form)
        self.yenile()

    def yenile(self):
        if self.bilgi_kaynagi is None:
            return
        while self.form.rowCount():
            self.form.removeRow(0)
        for etiket, deger in self.bilgi_kaynagi():
            yazi = QLabel(kisa_yol(str(deger)))
            yazi.setProperty("rol", "deger")
            yazi.setToolTip(str(deger))
            yazi.setTextInteractionFlags(Qt.TextSelectableByMouse)   # ör. veritabanı yolu kopyalanabilsin
            self.form.addRow(f"{etiket}:", yazi)


class Ayarlar(QScrollArea):
    """bolumler: [(başlık, butonlar, bilgiler)] — ortalanmış tek sütunda alt alta gösterilir."""

    def __init__(self, bolumler, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        ic = QWidget()
        ic.setObjectName("ayarlar_ic")
        ic.setStyleSheet(STIL)
        self.setWidget(ic)
        sutun = QWidget()
        sutun.setMaximumWidth(900)
        dikey = QVBoxLayout(sutun)
        dikey.setContentsMargins(0, 10, 0, 10)
        dikey.setSpacing(12)
        self.bolumler = []
        for baslik, butonlar, bilgiler in bolumler:
            bolum = Bolum(baslik, butonlar, bilgiler)
            dikey.addWidget(bolum)
            self.bolumler.append(bolum)
        dikey.addStretch()
        yatay = QHBoxLayout(ic)
        yatay.setContentsMargins(30, 10, 30, 10)
        yatay.addStretch()
        yatay.addWidget(sutun, 3)
        yatay.addStretch()

    def yenile(self):
        for bolum in self.bolumler:
            bolum.yenile()

    def buton(self, metin):
        for bolum in self.bolumler:
            if metin in bolum.butonlar:
                return bolum.butonlar[metin]
        raise KeyError(metin)


def kisa_yol(metin):
    """Ev klasörüyle başlayan yolları ~ ile kısaltır."""
    ev = os.path.expanduser("~")
    return "~" + metin[len(ev):] if metin.startswith(ev + os.sep) else metin


def klasoru_ac(klasor):
    os.makedirs(klasor, exist_ok=True)
    QDesktopServices.openUrl(QUrl.fromLocalFile(klasor))
