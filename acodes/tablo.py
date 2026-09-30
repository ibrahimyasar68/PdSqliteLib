## Tablo yardımcıları: doldurma, sıralama ve satır vurgulama ##

import re

from PyQt5.QtCore import QEvent, QObject, Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QTableWidgetItem

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
        if self.anahtar[0] == 0:          # sayılar sağa yaslı
            self.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def __lt__(self, diger):
        if isinstance(diger, SiraliHucre):
            return self.anahtar < diger.anahtar
        return super().__lt__(diger)


class BosDurum(QObject):
    """Tabloda gösterilecek bir şey yokken ortasında yönlendirici bir mesaj gösterir."""

    def __init__(self, tablo, metin):
        super().__init__(tablo)
        self.tablo = tablo
        self.etiket = QLabel(metin, tablo.viewport())
        self.etiket.setObjectName("bos_durum")
        self.etiket.setAlignment(Qt.AlignCenter)
        self.etiket.setWordWrap(True)
        self.etiket.setStyleSheet("color: #8A94A6; font-size: 15px; background: transparent;")
        self.etiket.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.bekliyor = False
        model = tablo.model()
        for sinyal in (model.rowsInserted, model.rowsRemoved, model.modelReset, model.layoutChanged, model.dataChanged):
            sinyal.connect(self.guncelle_sonra)
        tablo.viewport().installEventFilter(self)
        self.guncelle()

    def guncelle_sonra(self, *_):
        # Tablo doldurulurken her hücre için değil, doldurma bitince bir kez kontrol edilir
        if not self.bekliyor:
            self.bekliyor = True
            QTimer.singleShot(0, self.guncelle)

    def bos_mu(self):
        for r in range(self.tablo.rowCount()):
            for c in range(self.tablo.columnCount()):
                hucre = self.tablo.item(r, c)
                if hucre is not None and hucre.text():
                    return False
        return True

    def guncelle(self):
        self.bekliyor = False
        self.etiket.setVisible(self.bos_mu())
        self.etiket.setGeometry(self.tablo.viewport().rect().adjusted(20, 20, -20, -20))

    def eventFilter(self, nesne, olay):
        if olay.type() == QEvent.Resize:
            self.etiket.setGeometry(self.tablo.viewport().rect().adjusted(20, 20, -20, -20))
        return False


def tablo_ayarla(tablo, siralama=True, bos_metin=None):
    """Hücreler düzenlenemez, tıklanınca satır seçilir, başlığa tıklanınca sıralanır.
    İlk açılışta veri geldiği sırada gösterilir (sıralama göstergesi yok).
    Satırlar sırayla renklenir, satır numarası kolonu gizlenir; bos_metin verilirse boş tabloda gösterilir."""
    tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
    tablo.setAlternatingRowColors(True)
    tablo.setMouseTracking(True)
    tablo.verticalHeader().setVisible(False)
    tablo.verticalHeader().setDefaultSectionSize(26)
    tablo.horizontalHeader().setStretchLastSection(True)
    tablo.horizontalHeader().setHighlightSections(False)
    if bos_metin:
        tablo.bos_durum = BosDurum(tablo, bos_metin)
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
    # "İçeriğe göre genişlik" kolonları her hücrede baştan ölçülür (737 kitapta ~18 sn);
    # doldururken sabitlenir, bitince bir kez ölçülür
    baslik=tablo.horizontalHeader()
    kipler=[baslik.sectionResizeMode(c) for c in range(tablo.columnCount())]
    for c,kip in enumerate(kipler):
        if kip==QHeaderView.ResizeToContents:
            baslik.setSectionResizeMode(c,QHeaderView.Interactive)
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
    for c,kip in enumerate(kipler):
        if kip==QHeaderView.ResizeToContents:
            baslik.setSectionResizeMode(c,kip)
    tablo.setSortingEnabled(siralama)


def satir_verisi(tablo, satir):
    """tabloya_yaz(veri=...) ile saklanan bilgi; boş satırda None."""
    hucre=tablo.item(satir,0)
    return hucre.data(Qt.UserRole) if hucre else None
