## Kitap Verme > Ödünç Geçmişi alt sekmesi ##
# Üye ve kitap bazında tüm ödünç kayıtları; teslim tarihi, gün sayısı ve gecikme bilgisiyle.

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QAbstractItemView, QComboBox, QHBoxLayout, QHeaderView, QLabel,
                             QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)
from database.odunc import (gecikme_gunu, gun_sayisi, odunc_alan_uyeler, odunc_gecmisi,
                            odunc_verilen_kitaplar, tarih_yazi, teslim_tarihi)

TUMU = "Tümü"
DURUMLAR = [TUMU, "Dışarıda", "Gecikmiş", "İade edildi"]
GECIKME_ARKA = QColor(255, 205, 205)
GECIKME_YAZI = QColor(150, 0, 0)


def satir_renklendir(tablo, satir, arka=GECIKME_ARKA, yazi=GECIKME_YAZI):
    for c in range(tablo.columnCount()):
        hucre = tablo.item(satir, c)
        if hucre:
            hucre.setBackground(arka)
            hucre.setForeground(yazi)


def durum_bilgisi(verilis, durum, iade):
    """(durum yazısı, gün sayısı, gecikme günü)"""
    gecikme = gecikme_gunu(verilis, iade if durum == "in" else None)
    if durum == "out":
        yazi = f"Gecikmiş ({gecikme} gün)" if gecikme else "Dışarıda"
    else:
        yazi = f"İade edildi ({gecikme} gün geç)" if gecikme else "İade edildi"
    return yazi, gun_sayisi(verilis, iade if durum == "in" else None), gecikme


class OduncGecmisi(QWidget):
    KOLONLAR = ["Kitap", "Üye", "Veriliş", "Teslim Tarihi", "İade", "Gün", "Durum"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tab_6_4")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            #tab_6_4 { background-color: rgb(255, 240, 255); }
            QLabel, QComboBox, QTableWidget { font: 11pt "Verdana"; color: black; }
            QComboBox { background-color: white; border: 1px solid gray; border-radius: 4px; padding: 3px; }
            QTableWidget { background-color: white; }
        """)
        self.uye = QComboBox()
        self.kitap = QComboBox()
        self.durum = QComboBox()
        self.durum.addItems(DURUMLAR)
        self.ozet = QLabel()
        self.tablo = QTableWidget(0, len(self.KOLONLAR))
        self.tablo.setHorizontalHeaderLabels(self.KOLONLAR)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        baslik = self.tablo.horizontalHeader()
        baslik.setSectionResizeMode(QHeaderView.ResizeToContents)
        baslik.setSectionResizeMode(0, QHeaderView.Stretch)

        filtreler = QHBoxLayout()
        for etiket, kutu in (("Üye:", self.uye), ("Kitap:", self.kitap), ("Durum:", self.durum)):
            filtreler.addWidget(QLabel(etiket))
            filtreler.addWidget(kutu, 1)
        filtreler.addWidget(self.ozet, 1)
        duzen = QVBoxLayout(self)
        duzen.addLayout(filtreler)
        duzen.addWidget(self.tablo)

        for kutu in (self.uye, self.kitap, self.durum):
            kutu.currentIndexChanged.connect(self.listele)
        self.yenile()

    def yenile(self):
        ###  Filtre listelerini güncelle (seçimler korunur) ve tabloyu yeniden doldur  ###
        for kutu, kayitlar, etiket in (
                (self.uye, odunc_alan_uyeler(), lambda k: f"{k[1]} ({k[2]})"),
                (self.kitap, odunc_verilen_kitaplar(), lambda k: f"{k[1]} ({k[2]}, {k[3]})")):
            secili = kutu.currentData()
            kutu.blockSignals(True)
            kutu.clear()
            kutu.addItem(TUMU, None)
            for kayit in kayitlar:
                kutu.addItem(etiket(kayit), kayit[0])
            kutu.setCurrentIndex(max(0, kutu.findData(secili)) if secili is not None else 0)
            kutu.blockSignals(False)
        self.listele()

    def listele(self):
        secilen_durum = self.durum.currentText()
        satirlar = []
        for kitap, uye, verilis, durum, iade in odunc_gecmisi(self.uye.currentData(), self.kitap.currentData()):
            yazi, gun, gecikme = durum_bilgisi(verilis, durum, iade)
            if (secilen_durum == "Dışarıda" and durum != "out") or \
               (secilen_durum == "Gecikmiş" and not (durum == "out" and gecikme)) or \
               (secilen_durum == "İade edildi" and durum != "in"):
                continue
            satirlar.append(([kitap, uye, tarih_yazi(verilis), tarih_yazi(teslim_tarihi(verilis)),
                              tarih_yazi(iade) if durum == "in" else "", "" if gun is None else gun, yazi],
                             durum == "out" and gecikme > 0))
        self.tablo.setRowCount(len(satirlar))
        for r, (degerler, gecikmis) in enumerate(satirlar):
            for c, deger in enumerate(degerler):
                self.tablo.setItem(r, c, QTableWidgetItem(str(deger)))
            if gecikmis:
                satir_renklendir(self.tablo, r)
        disarida = sum(1 for d, _ in satirlar if d[4] == "")
        self.ozet.setText(f"{len(satirlar)} kayıt, {disarida} dışarıda")
