## Panellerdeki "Ayarlar" sekmesi ##
# Ana sayfadaki işlem butonları (kullanıcılar, yedekleme, şifre) burada gruplanır; ana sayfa sade kalır.
# Her bölüm: başlık, butonlar [(metin, işlev, ipucu)] ve isteğe bağlı bilgi satırları.

import os

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, QSize, Qt, QUrl, Property, Signal
from PySide6.QtGui import QColor, QDesktopServices, QPainter
from acodes import hareket, tema, tercihler
from acodes.kilavuz import Kilavuz
from acodes.yerlesim import form_duzeni
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QSizePolicy, QToolTip, QVBoxLayout, QWidget)

def stil():
    return f"""
#ayarlar_ic {{ background: transparent; }}
QGroupBox {{ font-size: {tema.YAZI.alt_baslik}px; font-weight: {tema.YARI_KALIN}; border-radius: {tema.KOSE.orta}px; padding: 48px 14px 14px 14px; }}
QLabel {{ color: {tema.IKINCIL_METIN}; }}
QLabel[rol="deger"] {{ color: {tema.METIN}; }}
#sayfa_baslik {{ color: {tema.METIN}; }}
QPushButton {{ padding: 9px 16px; min-width: 150px; }}
"""


IPUCU_UYE = ("İpucu: Ctrl+K (Mac'te ⌘K) her yerden hızlı arama açar: kitap adı veya gitmek istediğiniz bölümü "
             "yazıp Enter'a basın.")
IPUCU_YONETICI = ("İpucu: Ctrl+K (Mac'te ⌘K) her yerden hızlı arama açar: kitap, üye veya yapılacak işi yazıp "
                  "Enter'a basın. Listelerde bir kitaba sağ tıklayarak düzenleyebilir, ödünç verebilir, iade "
                  "alabilir veya ödünç geçmişini görebilirsiniz.")


class TamDeger(QLabel):
    """Bilgi değeri tek satırda; sığmazsa ortadan kısalır ("~/Library/…/PdSqliteLib/yedekler"), tamamı ipucunda.
    Klasör yollarının sağında kopyala simgesi durur. Tıklanınca değerin tamamı panoya kopyalanır (ör. yolu Finder'daki
    "Klasöre Git" kutusuna yapıştırmak için)."""
    SIMGE = 14

    def __init__(self, metin, parent=None):
        super().__init__(parent)
        self.tam = metin
        self.yol = os.sep in metin or "/" in metin
        self.setProperty("rol", "deger")
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)   # uzun yol sayfayı genişletmez
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(f"{metin}\nKopyalamak için tıklayın")
        if self.yol:
            self.setContentsMargins(0, 0, self.SIMGE + 8, 0)
        self.setText(metin)

    def resizeEvent(self, olay):
        super().resizeEvent(olay)
        en = self.contentsRect().width()
        self.setText(self.fontMetrics().elidedText(self.tam, Qt.ElideMiddle, en))

    def paintEvent(self, olay):
        super().paintEvent(olay)
        if not self.yol:
            return
        from PySide6.QtGui import QPainter
        from acodes import ikonlar
        yazi_en = self.fontMetrics().horizontalAdvance(self.text())
        x = min(yazi_en, self.contentsRect().width()) + 6
        y = (self.height() - self.SIMGE) // 2
        QPainter(self).drawPixmap(x, y, ikonlar.ikon("kopyala", tema.SOLUK).pixmap(self.SIMGE, self.SIMGE))

    def mousePressEvent(self, olay):
        QApplication.clipboard().setText(self.tam)
        QToolTip.showText(olay.globalPosition().toPoint(), "Panoya kopyalandı", self)


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
        self.form = form_duzeni(QFormLayout())    # değerler her sistemde kalan genişliği alır
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


class Anahtar(QAbstractButton):
    """Açma/kapama düğmesi: yuvarlak iz üstünde kayan topuz, sağında yazı. Onay kutusu yerine kendisi çizilir:
    macOS stili sarmalandığında (tema._sabit_aralikli) onay kutusu çizilirken program çöküyordu."""
    IZ_EN, IZ_BOY = 38, 22

    def __init__(self, metin, parent=None):
        super().__init__(parent)
        self.setText(metin)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self._konum = 0.0
        self.animasyon = QPropertyAnimation(self, b"konum", self)
        self.animasyon.setDuration(tema.SURE.kisa)
        self.animasyon.setEasingCurve(QEasingCurve.OutCubic)
        self.toggled.connect(self._kay)

    def _kay(self, acik):
        hedef = 1.0 if acik else 0.0
        self.animasyon.stop()
        if hareket.izinli() and self.isVisible():
            self.animasyon.setStartValue(self._konum)
            self.animasyon.setEndValue(hedef)
            self.animasyon.start()
        else:
            self.konum = hedef

    def _konum_al(self):
        return self._konum

    def _konum_yaz(self, deger):
        self._konum = deger
        self.update()

    konum = Property(float, _konum_al, _konum_yaz)

    def sizeHint(self):
        return QSize(self.IZ_EN + 10 + self.fontMetrics().horizontalAdvance(self.text()), max(self.IZ_BOY, 26))

    def paintEvent(self, olay):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        y = (self.height() - self.IZ_BOY) / 2
        iz = QRectF(0.5, y + 0.5, self.IZ_EN - 1, self.IZ_BOY - 1)
        kapali, acik = QColor(tema.YUZEY_2), QColor(tema.VURGU)
        renk = QColor(*(round(k + (a - k) * self._konum) for k, a in zip(kapali.getRgb()[:3], acik.getRgb()[:3])))
        p.setPen(QColor(tema.KENAR_IKINCIL) if self._konum < 0.5 else Qt.NoPen)
        p.setBrush(renk)
        p.drawRoundedRect(iz, iz.height() / 2, iz.height() / 2)
        cap = self.IZ_BOY - 6
        x = 3 + (self.IZ_EN - cap - 6) * self._konum
        p.setPen(Qt.NoPen)
        from acodes.ikonlar import BUTON_RENGI
        p.setBrush(QColor(BUTON_RENGI))                 # topuz: mavi zemin üstündeki ikonlar gibi beyaz
        p.drawEllipse(QRectF(x, y + 3, cap, cap))
        if self.hasFocus():
            p.setPen(QColor(tema.VURGU))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(iz.adjusted(-2, -2, 2, 2), self.IZ_BOY / 2 + 2, self.IZ_BOY / 2 + 2)
        p.setPen(QColor(tema.METIN))
        p.drawText(QRectF(self.IZ_EN + 10, 0, self.width() - self.IZ_EN - 10, self.height()),
                   Qt.AlignLeft | Qt.AlignVCenter, self.text())


class GorunumBolumu(QGroupBox):
    """Açık / koyu / sistemle aynı görünüm seçimi. Seçim değişince degisti(görünüm) yayınlanır.
    "Hareketi azalt" geçiş animasyonlarını kapatır (hemen uygulanır, panel yeniden kurulmaz)."""
    degisti = Signal(str)

    def __init__(self, parent=None):
        super().__init__("Görünüm", parent)
        from acodes.yan_menu import SegmentAnahtari
        duzen = QVBoxLayout(self)
        duzen.setSpacing(8)
        # Tema: alt sekmelerdeki gibi tek parça segment anahtarı (seçili zemin kayarak gider)
        anahtarlar = list(tema.GORUNUMLER)
        self.secici = SegmentAnahtari(adlar=list(tema.GORUNUMLER.values()), secili=anahtarlar.index(tema.GORUNUM))
        self.butonlar = {a: self.secici.grup.button(i) for i, a in enumerate(anahtarlar)}
        self.secici.secildi.connect(lambda i: self.sec(anahtarlar[i]))
        duzen.addWidget(self.secici, 0, Qt.AlignLeft)
        aciklama = QLabel("“Sistemle aynı” bilgisayarın açık/koyu görünümünü izler. Tercih hatırlanır.")
        aciklama.setWordWrap(True)
        duzen.addWidget(aciklama)
        duzen.addSpacing(8)
        self.hareket = Anahtar("Hareketi azalt")
        self.hareket.setToolTip("Sayfa geçişleri, menü, bildirim ve tema geçişindeki animasyonlar kapanır; "
                                "değişiklikler hemen görünür.")
        self.hareket.setChecked(hareket.AZALT)
        self.hareket.toggled.connect(self.hareket_degisti)
        duzen.addWidget(self.hareket, 0, Qt.AlignLeft)
        duzen.addWidget(QLabel("Geçiş animasyonlarını kapatır; değişiklikler hemen görünür."))

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
        dikey.addWidget(QLabel("Ayarlar", objectName="sayfa_baslik"))     # diğer sayfalardaki gibi üstte sayfa adı
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
