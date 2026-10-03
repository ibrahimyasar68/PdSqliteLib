## Panellerdeki "Ayarlar" sekmesi ##
# Ana sayfadaki işlem butonları (kullanıcılar, yedekleme, şifre) burada gruplanır; ana sayfa sade kalır.
# Her bölüm: başlık, butonlar [(metin, işlev, ipucu)] ve isteğe bağlı bilgi satırları.

import os

from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices
from acodes import hareket, tema, tercihler
from acodes.kilavuz import Kilavuz
from PyQt5.QtWidgets import (QApplication, QButtonGroup, QDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QSizePolicy, QToolTip, QVBoxLayout, QWidget)

def stil():
    return f"""
#ayarlar_ic {{ background: transparent; }}
QGroupBox {{ font-size: {tema.YAZI.alt_baslik}px; font-weight: {tema.YARI_KALIN}; border-radius: {tema.KOSE.orta}px; padding: 48px 14px 14px 14px; }}
QLabel {{ color: {tema.IKINCIL_METIN}; }}
QLabel[rol="deger"] {{ color: {tema.METIN}; }}
QPushButton {{ padding: 9px 16px; min-width: 150px; }}
"""


IPUCU_UYE = ("İpucu: Ctrl+K (Mac'te ⌘K) her yerden hızlı arama açar: kitap adı veya gitmek istediğiniz bölümü "
             "yazıp Enter'a basın.")
IPUCU_YONETICI = ("İpucu: Ctrl+K (Mac'te ⌘K) her yerden hızlı arama açar: kitap, üye veya yapılacak işi yazıp "
                  "Enter'a basın. Listelerde bir kitaba sağ tıklayarak düzenleyebilir, ödünç verebilir, iade "
                  "alabilir veya ödünç geçmişini görebilirsiniz.")


class TamDeger(QLabel):
    """Bilgi değeri ekranda tam yazılır; uzun klasör yolları sığmazsa "/" işaretlerinden alt satıra geçer.
    Tıklanınca değer panoya kopyalanır (ör. yolu Finder'daki "Klasöre Git" kutusuna yapıştırmak için)."""

    def __init__(self, metin, parent=None):
        super().__init__(parent)
        self.tam = metin
        self.setProperty("rol", "deger")
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Kopyalamak için tıklayın")
        # Görünmez kırılma noktası: kelime aralığı olmayan uzun yollar da satıra sığar (kopyalanan metinde yoktur)
        self.setText(metin.replace("/", "/\u200b").replace("\\", "\\\u200b"))

    def mousePressEvent(self, olay):
        QApplication.clipboard().setText(self.tam)
        QToolTip.showText(olay.globalPos(), "Panoya kopyalandı", self)


class Bolum(QGroupBox):
    def __init__(self, baslik, butonlar=(), bilgiler=None, parent=None):
        """butonlar: [(metin, işlev, ipucu)] — ilki bölümün asıl işlemidir (dolu mavi), diğerleri ikincil (çerçeveli).
        bilgiler: [(etiket, değer)] döndüren fonksiyon (yenilenebilir)."""
        super().__init__(baslik, parent)
        self.bilgi_kaynagi = bilgiler
        self.butonlar = {}
        duzen = QVBoxLayout(self)
        if butonlar:
            satir = QHBoxLayout()
            for i, (metin, islev, ipucu) in enumerate(butonlar):
                b = QPushButton(metin)
                if i > 0:
                    b.setProperty("rol", "ikincil")
                b.setCursor(Qt.PointingHandCursor)
                b.setToolTip(ipucu)
                b.clicked.connect(islev)
                satir.addWidget(b)
                self.butonlar[metin] = b
            satir.addStretch()
            duzen.addLayout(satir)
        self.form = QFormLayout()
        # macOS'un varsayılanı (alanlar önerilen boyutta, form ortalı) değerleri sıfır genişlikte bırakıyordu:
        # her sistemde değerler kalan genişliği alır, form sola yaslanır
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
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
            self.form.addRow(f"{etiket}:", TamDeger(kisa_yol(str(deger))))


class GorunumBolumu(QGroupBox):
    """Açık / koyu / sistemle aynı görünüm seçimi. Seçim değişince degisti(görünüm) yayınlanır.
    "Hareketi azalt" geçiş animasyonlarını kapatır (hemen uygulanır, panel yeniden kurulmaz)."""
    degisti = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__("Görünüm", parent)
        duzen = QVBoxLayout(self)
        satir = QHBoxLayout()
        self.grup = QButtonGroup(self)
        self.butonlar = {}
        for anahtar, ad in tema.GORUNUMLER.items():
            b = QPushButton(ad, checkable=True)
            b.setCursor(Qt.PointingHandCursor)
            b.setProperty("rol", "ikincil")
            b.setChecked(anahtar == tema.GORUNUM)
            b.clicked.connect(lambda _, a=anahtar: self.sec(a))
            self.grup.addButton(b)
            satir.addWidget(b)
            self.butonlar[anahtar] = b
        satir.addStretch()
        duzen.addLayout(satir)
        aciklama = QLabel("“Sistemle aynı” bilgisayarın açık/koyu görünümünü izler. Tercih hatırlanır.")
        aciklama.setWordWrap(True)
        duzen.addWidget(aciklama)
        # Onay kutusu yerine basılı kalan düğme: macOS stili sarmalandığında (tema._sabit_aralikli) onay kutusu
        # çizilirken program çöküyordu; görünüm düğmeleriyle de aynı biçimde durur
        self.hareket = QPushButton("Hareketi azalt", checkable=True)
        self.hareket.setProperty("rol", "ikincil")
        self.hareket.setToolTip("Sayfa geçişleri, menü, bildirim ve tema geçişindeki animasyonlar kapanır; "
                                "değişiklikler hemen görünür.")
        self.hareket.setCursor(Qt.PointingHandCursor)
        self.hareket.setChecked(hareket.AZALT)
        self.hareket.toggled.connect(self.hareket_degisti)
        alt = QHBoxLayout()
        alt.addWidget(self.hareket)
        alt.addSpacing(8)
        alt.addWidget(QLabel("Geçiş animasyonlarını kapatır; değişiklikler hemen görünür."))
        alt.addStretch()
        duzen.addLayout(alt)

    def hareket_degisti(self, azalt):
        hareket.AZALT = azalt
        tercihler.yaz(hareket.TERCIH, "1" if azalt else "0")

    def sec(self, gorunum):
        if gorunum != tema.GORUNUM:
            tercihler.yaz("gorunum/tema", gorunum)
            self.degisti.emit(gorunum)


class KilavuzPenceresi(QDialog):
    """Kullanma Kılavuzu ayrı pencerede: Ayarlar sayfası kısa kalır."""

    def __init__(self, konular, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kullanma Kılavuzu")
        self.resize(820, 680)
        self.kilavuz = Kilavuz(konular)
        kaydirma = QScrollArea()
        kaydirma.setWidgetResizable(True)
        kaydirma.setFrameShape(QScrollArea.NoFrame)
        kaydirma.setWidget(self.kilavuz)
        kapat = QPushButton("Kapat")
        kapat.setProperty("rol", "ikincil")
        kapat.setMinimumSize(110, 36)
        kapat.clicked.connect(self.close)
        duzen = QVBoxLayout(self)
        duzen.addWidget(kaydirma, 1)
        duzen.addWidget(kapat, 0, Qt.AlignRight)


class Ayarlar(QScrollArea):
    """bolumler: [(başlık, butonlar, bilgiler)] — ortalanmış tek sütunda alt alta gösterilir.
    kilavuz: Yardım bölümündeki butonla açılan Kullanma Kılavuzu konuları [(başlık, metin)]."""

    def __init__(self, bolumler, kilavuz=None, ipucu=IPUCU_UYE, parent=None):
        """Bölümlerin altında Görünüm seçimi, en altta Yardım (kısayollar ve Kullanma Kılavuzu) gösterilir."""
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        ic = QWidget()
        ic.setObjectName("ayarlar_ic")
        ic.setStyleSheet(stil())
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
        self.gorunum = GorunumBolumu()
        dikey.addWidget(self.gorunum)
        self.kilavuz_penceresi = KilavuzPenceresi(kilavuz, self) if kilavuz else None
        self.kilavuz = self.kilavuz_penceresi.kilavuz if kilavuz else None
        if kilavuz:
            yardim = Bolum("Yardım", [("Kullanma Kılavuzu", self.kilavuzu_ac,
                                       "Her bölümün nasıl kullanıldığını anlatan kılavuzu açın")])
            ipucu_yazisi = QLabel(ipucu)
            ipucu_yazisi.setWordWrap(True)
            yardim.layout().addWidget(ipucu_yazisi)
            dikey.addWidget(yardim)
            self.yardim = yardim
        dikey.addStretch()
        yatay = QHBoxLayout(ic)
        yatay.setContentsMargins(30, 10, 30, 10)
        yatay.addStretch()
        yatay.addWidget(sutun, 3)
        yatay.addStretch()

    def kilavuzu_ac(self):
        self.kilavuz_penceresi.show()
        self.kilavuz_penceresi.raise_()
        self.kilavuz_penceresi.activateWindow()

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
