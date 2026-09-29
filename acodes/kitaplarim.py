## Guest paneli > Kitaplarım sekmesi ##
# Üyenin elindeki kitaplar (teslim tarihi, kalan gün) ve daha önce aldığı kitaplar.

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QHeaderView, QLabel, QTableWidget, QVBoxLayout, QWidget

from acodes.tablo import tablo_ayarla, tabloya_yaz
from database.odunc import gecikme_gunu, gun_sayisi, kalan_gun_yazi, tarih_yazi, teslim_tarihi, uye_odunc


def tablo_olustur(basliklar):
    tablo = QTableWidget(0, len(basliklar))
    tablo.setHorizontalHeaderLabels(basliklar)
    baslik = tablo.horizontalHeader()
    baslik.setSectionResizeMode(QHeaderView.ResizeToContents)
    baslik.setSectionResizeMode(0, QHeaderView.Stretch)
    tablo_ayarla(tablo)
    return tablo


class Kitaplarim(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.kullanici = None
        self.setObjectName("tab_kitaplarim")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            #tab_kitaplarim { background-color: rgb(255, 245, 215); }
            QLabel, QTableWidget, QGroupBox { font: 11pt "Verdana"; color: black; }
            QTableWidget { background-color: white; }
            QGroupBox { font-weight: bold; }
        """)
        self.ozet = QLabel()
        self.ozet.setStyleSheet('font: bold 13pt "Verdana";')
        self.elimdeki = tablo_olustur(["Kitap", "Yazar", "Aldığım Tarih", "Teslim Tarihi", "Durum"])
        self.gecmis = tablo_olustur(["Kitap", "Yazar", "Aldığım Tarih", "İade Tarihi", "Gün"])

        kutu1 = QGroupBox("Elimdeki kitaplar")
        QVBoxLayout(kutu1).addWidget(self.elimdeki)
        kutu2 = QGroupBox("Daha önce aldığım kitaplar")
        QVBoxLayout(kutu2).addWidget(self.gecmis)
        duzen = QVBoxLayout(self)
        duzen.addWidget(self.ozet)
        duzen.addWidget(kutu1, 1)
        duzen.addWidget(kutu2, 1)

    def yukle(self, kullanici=None):
        """Kullanıcının ödünçlerini listeler; gecikmiş kitap sayısını döndürür."""
        if kullanici is not None:
            self.kullanici = kullanici
        elimdeki, eski, gecikenler = [], [], set()
        for kitap, yazar, verilis, durum, iade in uye_odunc(self.kullanici):
            if durum == "out":
                if gecikme_gunu(verilis):
                    gecikenler.add(len(elimdeki))
                elimdeki.append([kitap, yazar, tarih_yazi(verilis), tarih_yazi(teslim_tarihi(verilis)),
                                 kalan_gun_yazi(verilis)])
            else:
                gun = gun_sayisi(verilis, iade)
                eski.append([kitap, yazar, tarih_yazi(verilis), tarih_yazi(iade), "" if gun is None else gun])
        tabloya_yaz(self.elimdeki, elimdeki, vurgulu=gecikenler)
        tabloya_yaz(self.gecmis, eski)
        if not elimdeki:
            metin = "Şu an sizde ödünç kitap yok."
        else:
            metin = f"Şu an sizde {len(elimdeki)} kitap var."
            if gecikenler:
                metin += f" {len(gecikenler)} tanesinin teslim süresi geçti, lütfen iade edin."
        self.ozet.setText(metin)
        self.ozet.setStyleSheet('font: bold 13pt "Verdana"; color: %s;' % ("rgb(170, 0, 0)" if gecikenler else "black"))
        return len(gecikenler)
