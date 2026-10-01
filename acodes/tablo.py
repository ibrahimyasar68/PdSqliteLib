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
        self.etiket.setStyleSheet("color: #8A94A6; font-size: 17px; background: transparent;")
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


def tablo_ayarla(tablo, siralama=True, bos_metin=None, sira_no=True):
    """Hücreler düzenlenemez, tıklanınca satır seçilir, başlığa tıklanınca sıralanır.
    İlk açılışta veri geldiği sırada gösterilir (sıralama göstergesi yok).
    Satırlar sırayla renklenir; bos_metin verilirse boş tabloda gösterilir.
    sira_no: solda 1'den başlayan sıra numarası (kayıt numarasından bağımsız; sıralama değişince de
    ekrandaki sıraya göre numaralanır, son numara listedeki kayıt sayısını gösterir)."""
    tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
    tablo.setAlternatingRowColors(True)
    tablo.setMouseTracking(True)
    tablo.verticalHeader().setVisible(sira_no)
    tablo.verticalHeader().setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)
    tablo.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
    tablo.verticalHeader().setHighlightSections(False)
    tablo.verticalHeader().setDefaultSectionSize(30)
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


class KolonSecici(QObject):
    """Kitap listelerinde gösterilecek kolonların seçimi (seçim hatırlanır).
    "Kolonlar" butonu ve kolon başlığına sağ tık aynı seçim listesini açar. Liste pencereye sığmazsa tablonun
    üstünde kullanıcıya hangi kolonları gizlemek istediği sorulur ("Bir daha sorma" ile kapatılabilir)."""

    def __init__(self, tablo, anahtar, zorunlu=(0, 1), parent=None):
        super().__init__(parent or tablo)
        from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton
        from acodes import tercihler
        self.tablo, self.anahtar, self.zorunlu = tablo, anahtar, set(zorunlu)
        self.tercihler = tercihler
        self.buton = QPushButton("Kolonlar")
        self.buton.setProperty("rol", "ikincil")
        self.buton.setToolTip("Listede gösterilecek kolonları seçin")
        self.buton.clicked.connect(lambda: self.menu().exec_(self.buton.mapToGlobal(self.buton.rect().bottomLeft())))
        baslik = tablo.horizontalHeader()
        baslik.setContextMenuPolicy(Qt.CustomContextMenu)
        baslik.customContextMenuRequested.connect(lambda konum: self.menu().exec_(baslik.mapToGlobal(konum)))

        self.soru = QFrame(objectName="kolon_sorusu")
        self.soru.setStyleSheet("#kolon_sorusu { background-color: #FEF3C7; border: 1px solid #FCD34D; border-radius: 8px; }"
                                "#kolon_sorusu QLabel { color: #78350F; }")
        satir = QHBoxLayout(self.soru)
        satir.setContentsMargins(12, 6, 8, 6)
        satir.addWidget(QLabel("Liste pencereye sığmıyor. Hangi kolonların gizleneceğini seçmek ister misiniz?"), 1)
        self.btn_sec = QPushButton("Kolonları Seç")
        self.btn_sec.clicked.connect(lambda: self.menu().exec_(self.btn_sec.mapToGlobal(self.btn_sec.rect().bottomLeft())))
        self.btn_sorma = QPushButton("Bir daha sorma")
        self.btn_sorma.setProperty("rol", "ikincil")
        self.btn_sorma.clicked.connect(self.sorma)
        satir.addWidget(self.btn_sec)
        satir.addWidget(self.btn_sorma)
        self.soru.hide()

        for kolon in tercihler.sayi_listesi(f"kolonlar/{anahtar}"):
            if kolon not in self.zorunlu and kolon < tablo.columnCount():
                tablo.setColumnHidden(kolon, True)
        self.bekliyor = False
        tablo.viewport().installEventFilter(self)
        model = tablo.model()
        for sinyal in (model.rowsInserted, model.modelReset, model.layoutChanged):
            sinyal.connect(self.denetle_sonra)

    def menu(self):
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self.tablo)
        for c in range(self.tablo.columnCount()):
            baslik = self.tablo.horizontalHeaderItem(c)
            eylem = menu.addAction(baslik.text() if baslik else str(c + 1))
            eylem.setCheckable(True)
            eylem.setChecked(not self.tablo.isColumnHidden(c))
            eylem.setEnabled(c not in self.zorunlu)
            eylem.toggled.connect(lambda gorunsun, c=c: self.goster(c, gorunsun))
        menu.addSeparator()
        menu.addAction("Tüm kolonları göster", self.hepsini_goster)
        return menu

    def gizli(self):
        return [c for c in range(self.tablo.columnCount()) if self.tablo.isColumnHidden(c)]

    def goster(self, kolon, gorunsun):
        if kolon in self.zorunlu:
            return
        self.tablo.setColumnHidden(kolon, not gorunsun)
        self.tercihler.yaz(f"kolonlar/{self.anahtar}", ",".join(map(str, self.gizli())))
        self.denetle_sonra()

    def hepsini_goster(self):
        for c in self.gizli():
            self.goster(c, True)

    def sorma(self):
        self.tercihler.yaz(f"kolonlar/{self.anahtar}_sorma", "1")
        self.soru.hide()

    def sigmiyor(self):
        """Yatay kaydırma çıkıyorsa ya da bir kolon içeriğinin %60'ından dar kaldıysa liste sığmıyor sayılır.
        Uzun metinli kolonlarda (ör. kitap adı) en uzun değerin tamamı değil makul bir genişlik (220 px) beklenir."""
        if self.tablo.rowCount() == 0 or not self.tablo.isVisible():
            return False
        kaydirma = self.tablo.horizontalScrollBar()
        if kaydirma.isVisible() and kaydirma.maximum() > 0:
            return True
        baslik = self.tablo.horizontalHeader()
        for c in range(self.tablo.columnCount()):
            if self.tablo.isColumnHidden(c):
                continue
            icerik = min(220, max(baslik.sectionSizeHint(c), self.tablo.sizeHintForColumn(c)))
            if self.tablo.columnWidth(c) < 0.6 * icerik:
                return True
        return False

    def denetle_sonra(self, *_):
        if not self.bekliyor:
            self.bekliyor = True
            QTimer.singleShot(0, self.denetle)

    def denetle(self):
        self.bekliyor = False
        sor = not self.tercihler.mantiksal(f"kolonlar/{self.anahtar}_sorma") and self.sigmiyor()
        self.soru.setVisible(sor)

    def eventFilter(self, nesne, olay):
        if olay.type() in (QEvent.Resize, QEvent.Show):
            self.denetle_sonra()
        return False
