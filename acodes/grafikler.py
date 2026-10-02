## İstatistik > Grafikler alt sekmesi ##
# Grafikler veritabanından her yenilemede yeniden çizilir (eskiden sabit bir resim gösteriliyordu).
# Ek kütüphane gerektirmemek için Qt'nin kendi çizim araçları (QPainter) kullanılır.

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QGridLayout, QWidget

from acodes import tema
from database.dbframe import rapor, yil_dagilimi

RENKLER = [QColor(c) for c in ("#4e79a7", "#f28e2b", "#59a14f", "#e15759", "#76b7b2",
                                "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac")]
PASTA_DILIM = 7        # en büyük 7 tür, gerisi "Diğer"
CUBUK_SAYISI = 10


class Grafik(QWidget):
    """Başlıklı, beyaz zeminli grafik kutusu. Alt sınıflar ciz() metodunu yazar."""

    def __init__(self, baslik, parent=None):
        super().__init__(parent)
        self.baslik = baslik
        self.veri = []          # [(etiket, değer), ...]
        self.setMinimumSize(300, 220)

    def veri_ver(self, veri):
        self.veri = [(str(e) if str(e).strip() else "(belirtilmemiş)", int(d)) for e, d in veri if int(d) > 0]
        self.update()

    def paintEvent(self, olay):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        kutu = QRectF(self.rect()).adjusted(4, 4, -4, -4)
        p.setPen(QPen(QColor(tema.KENAR)))
        p.setBrush(QColor(tema.KART))
        p.drawRoundedRect(kutu, 8, 8)
        p.setPen(QColor(tema.METIN))
        p.setFont(tema.yazi_tipi(17, kalin=True))
        p.drawText(kutu.adjusted(12, 8, -12, 0), Qt.AlignLeft | Qt.AlignTop, self.baslik)
        alan = kutu.adjusted(14, 38, -14, -12)
        p.setFont(tema.yazi_tipi(14))
        if not self.veri:
            p.setPen(QColor(tema.SOLUK))
            p.drawText(alan, Qt.AlignCenter, "Gösterilecek veri yok")
        else:
            self.ciz(p, alan)
        p.end()


class PastaGrafik(Grafik):
    def ciz(self, p, alan):
        toplam = sum(d for _, d in self.veri)
        cap = min(alan.height(), alan.width() * 0.5)
        daire = QRectF(alan.left(), alan.top() + (alan.height() - cap) / 2, cap, cap)
        aci = 90 * 16
        for i, (_, deger) in enumerate(self.veri):
            dilim = -round(deger / toplam * 360 * 16)
            p.setPen(QPen(QColor(tema.KART), 1.5))
            p.setBrush(RENKLER[i % len(RENKLER)])
            p.drawPie(daire, aci, dilim)
            aci += dilim
        # Açıklama: renk, etiket, adet ve yüzde
        satir = min(22, alan.height() / max(1, len(self.veri)))
        x = daire.right() + 20
        y = alan.top() + (alan.height() - satir * len(self.veri)) / 2
        for i, (etiket, deger) in enumerate(self.veri):
            p.setPen(Qt.NoPen)
            p.setBrush(RENKLER[i % len(RENKLER)])
            p.drawRoundedRect(QRectF(x, y + satir * i + 4, 12, 12), 2, 2)
            p.setPen(QColor(tema.METIN))
            p.drawText(QRectF(x + 20, y + satir * i, alan.right() - x - 20, satir),
                       Qt.AlignLeft | Qt.AlignVCenter, f"{etiket}  {deger}  (%{deger / toplam * 100:.1f})")


class YatayCubukGrafik(Grafik):
    def ciz(self, p, alan):
        en_buyuk = max(d for _, d in self.veri)
        etiket_eni = min(alan.width() * 0.4, 210)
        satir = alan.height() / len(self.veri)
        cubuk_alani = alan.width() - etiket_eni - 40
        for i, (etiket, deger) in enumerate(self.veri):
            y = alan.top() + satir * i
            p.setPen(QColor(tema.METIN))
            metin = p.fontMetrics().elidedText(etiket, Qt.ElideRight, int(etiket_eni - 8))
            p.drawText(QRectF(alan.left(), y, etiket_eni - 8, satir), Qt.AlignRight | Qt.AlignVCenter, metin)
            en = max(2, cubuk_alani * deger / en_buyuk)
            p.setPen(Qt.NoPen)
            p.setBrush(RENKLER[0])
            p.drawRoundedRect(QRectF(alan.left() + etiket_eni, y + satir * 0.18, en, satir * 0.64), 3, 3)
            p.setPen(QColor(tema.METIN))
            p.drawText(QRectF(alan.left() + etiket_eni + en + 6, y, 40, satir), Qt.AlignLeft | Qt.AlignVCenter, str(deger))


class DikeyCubukGrafik(Grafik):
    def ciz(self, p, alan):
        en_buyuk = max(d for _, d in self.veri)
        alt = alan.bottom() - 22          # etiketler için yer
        ust = alan.top() + 18             # değerler için yer
        sutun = alan.width() / len(self.veri)
        for i, (etiket, deger) in enumerate(self.veri):
            x = alan.left() + sutun * i
            boy = max(2, (alt - ust) * deger / en_buyuk)
            p.setPen(Qt.NoPen)
            p.setBrush(RENKLER[2])
            p.drawRoundedRect(QRectF(x + sutun * 0.15, alt - boy, sutun * 0.7, boy), 3, 3)
            p.setPen(QColor(tema.METIN))
            p.drawText(QRectF(x, alt - boy - 18, sutun, 18), Qt.AlignCenter, str(deger))
            p.drawText(QRectF(x, alt + 2, sutun, 20), Qt.AlignCenter, etiket)


def tur_dagilimi():
    veri = list(rapor('Turu', 1000).items())
    if len(veri) > PASTA_DILIM + 1:
        veri = veri[:PASTA_DILIM] + [("Diğer", sum(d for _, d in veri[PASTA_DILIM:]))]
    return veri


class GrafikPaneli(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.turler = PastaGrafik("Türlere Göre Dağılım")
        self.yazarlar = YatayCubukGrafik(f"En Çok Kitabı Olan {CUBUK_SAYISI} Yazar")
        self.yayinevleri = YatayCubukGrafik(f"En Çok Kitabı Olan {CUBUK_SAYISI} Yayınevi")
        self.yillar = DikeyCubukGrafik("Basım Yıllarına Göre (on yıllık)")
        duzen = QGridLayout(self)
        duzen.setContentsMargins(0, 0, 0, 0)
        duzen.addWidget(self.turler, 0, 0)
        duzen.addWidget(self.yazarlar, 0, 1)
        duzen.addWidget(self.yillar, 1, 0)
        duzen.addWidget(self.yayinevleri, 1, 1)

    def yenile(self):
        self.turler.veri_ver(tur_dagilimi())
        for grafik, kolon in ((self.yazarlar, 'Yazari'), (self.yayinevleri, 'Yayinevi')):
            grafik.veri_ver(rapor(kolon, CUBUK_SAYISI, bos_dahil=False).items())
        self.yillar.veri_ver(yil_dagilimi())
