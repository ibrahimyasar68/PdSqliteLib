## Tablo yardımcıları: doldurma, sıralama ve satır vurgulama ##

import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem

from database.dbframe import tr_sirala

VURGU_ARKA = QColor(255, 205, 205)    # ör. teslim süresi geçmiş ödünçler
VURGU_YAZI = QColor(150, 0, 0)
_TARIH = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
_SAYI = re.compile(r"-?\d+")


def siralama_anahtari(deger):
    """Sayılar sayı olarak, gg.aa.yyyy tarih olarak, metinler Türk alfabesine göre sıralanır; boşlar en sonda."""
    metin = str(deger).strip()
    if not metin:
        return (3,)
    if _SAYI.fullmatch(metin):
        return (0, int(metin))
    tarih = _TARIH.fullmatch(metin)
    if tarih:
        gun, ay, yil = tarih.groups()
        return (1, (int(yil), int(ay), int(gun)))
    return (2, tr_sirala(metin))


class SiraliHucre(QTableWidgetItem):
    def __init__(self, deger):
        super().__init__("" if deger is None else str(deger))
        self.anahtar = siralama_anahtari(self.text())

    def __lt__(self, diger):
        if isinstance(diger, SiraliHucre):
            return self.anahtar < diger.anahtar
        return super().__lt__(diger)


def tablo_ayarla(tablo, siralama=True):
    """Hücreler düzenlenemez, tıklanınca satır seçilir, başlığa tıklanınca sıralanır.
    İlk açılışta veri geldiği sırada gösterilir (sıralama göstergesi yok)."""
    tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
    if siralama:
        tablo.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        tablo.setSortingEnabled(True)


def tablo_basliklari(tablo, kolonlar):
    for i,(genislik,baslik) in enumerate(kolonlar):
        tablo.setColumnWidth(i,genislik)
        tablo.setHorizontalHeaderItem(i,QTableWidgetItem(baslik))


def tabloya_yaz(tablo, satirlar, vurgulu=(), veri=None):
    """satirlar: yazılacak değerler. vurgulu: kırmızı gösterilecek satırların sırası.
    veri: her satır için ilk hücrede saklanacak ek bilgi (ör. id'ler), sıralamada satırla birlikte taşınır."""
    siralama=tablo.isSortingEnabled()
    tablo.setSortingEnabled(False)   # doldururken satırlar yer değiştirmesin
    tablo.setRowCount(len(satirlar))
    for r,satir in enumerate(satirlar):
        for c,deger in enumerate(satir):
            hucre=SiraliHucre(deger)
            if r in vurgulu:
                hucre.setBackground(VURGU_ARKA)
                hucre.setForeground(VURGU_YAZI)
            if c==0 and veri is not None:
                hucre.setData(Qt.UserRole, veri[r])
            tablo.setItem(r,c,hucre)
    tablo.setSortingEnabled(siralama)


def satir_verisi(tablo, satir):
    """tabloya_yaz(veri=...) ile saklanan bilgi; boş satırda None."""
    hucre=tablo.item(satir,0)
    return hucre.data(Qt.UserRole) if hucre else None
