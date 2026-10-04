## Esnek yerleşim ##
# .ui dosyalarındaki sayfalar sabit piksel konumlarıyla çizilmiş; pencere büyüyünce sol üstte küçük kalıyorlardı.
# Buradaki kalıplar mevcut bileşenleri yerleşim düzenlerine (layout) alır: tablolar ve alanlar pencereyle büyür.

from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLayout, QVBoxLayout

SINIRSIZ = 16777215


def baslik_satiri(baslik=None, sayac=None, butonlar=(), bilgi=None):
    """Sayfaların ortak üst satırı: solda başlık ve sonuç sayısı (ör. "Toplam 737 kitap"), sağda butonlar.
    bilgi: başlığın yanındaki ⓘ simgesinin ipucu (uzun açıklama metni yerine)."""
    satir = QHBoxLayout()
    satir.setSpacing(8)
    if baslik:
        satir.addWidget(QLabel(baslik, objectName="sayfa_baslik"))
    if bilgi:
        simge = QLabel("ⓘ")
        simge.setProperty("rol", "bilgi_simgesi")
        simge.setToolTip(bilgi)
        simge.setCursor(Qt.WhatsThisCursor)
        satir.addWidget(simge)
    if baslik or bilgi:
        satir.addSpacing(8)
    if sayac is not None:
        sayac.setProperty("rol", "sayac")
        satir.addWidget(sayac)
    satir.addStretch()
    for buton in butonlar:
        buton.setMinimumSize(0, 36)
        buton.setMaximumSize(SINIRSIZ, 36)
        satir.addWidget(buton)
    return satir


def etiketli(etiket, alan, bosluk=4):
    """Form alanı ve üstünde, sola yaslı, iki noktasız etiketi (dikey düzen). Izgaraya addLayout ile eklenir."""
    kutu = QVBoxLayout()
    kutu.setSpacing(bosluk)
    yazi = QLabel(etiket)
    yazi.setProperty("rol", "alan_etiketi")
    yazi.setBuddy(alan)
    kutu.addWidget(yazi)
    kutu.addWidget(alan)
    return kutu


def ustte_etiketli_form(form):
    """QFormLayout'ta etiketler alanların üstünde (iki noktasız, sola yaslı); formla aynı biçim."""
    from PyQt5.QtWidgets import QFormLayout
    form.setRowWrapPolicy(QFormLayout.WrapAllRows)
    form.setLabelAlignment(Qt.AlignLeft)
    form.setVerticalSpacing(10)
    return form


def liste_sayfasi(sayfa, ust, arama, tablo, uyari=None):
    """Üstte başlık satırı, altında tam genişlikte arama kutusu, (varsa) uyarı şeridi ve pencereyle büyüyen tablo."""
    duzen = QVBoxLayout(sayfa)
    duzen.setContentsMargins(14, 12, 14, 12)
    duzen.setSpacing(10)
    duzen.addLayout(ust)
    arama.setMinimumHeight(38)
    arama.setMaximumWidth(SINIRSIZ)
    duzen.addWidget(arama)
    if uyari is not None:
        duzen.addWidget(uyari)          # ör. "liste sığmıyor, kolon gizlensin mi?" sorusu
    duzen.addWidget(tablo, 1)
    return duzen


class AkisDuzeni(QLayout):
    """Bileşenleri yan yana dizer, satır dolunca alt satıra geçer (ör. seçim etiketleri)."""

    def __init__(self, parent=None, bosluk=6):
        super().__init__(parent)
        self.ogeler = []
        self.bosluk = bosluk
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, oge):
        self.ogeler.append(oge)

    def count(self):
        return len(self.ogeler)

    def itemAt(self, i):
        return self.ogeler[i] if 0 <= i < len(self.ogeler) else None

    def takeAt(self, i):
        return self.ogeler.pop(i) if 0 <= i < len(self.ogeler) else None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, en):
        return self._diz(QRect(0, 0, en, 0), sadece_olc=True)

    def setGeometry(self, alan):
        super().setGeometry(alan)
        self._diz(alan)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        boyut = QSize()
        for oge in self.ogeler:
            boyut = boyut.expandedTo(oge.minimumSize())
        return boyut

    def _diz(self, alan, sadece_olc=False):
        x, y, satir_boyu = alan.x(), alan.y(), 0
        for oge in self.ogeler:
            boyut = oge.sizeHint()
            if x + boyut.width() > alan.right() + 1 and satir_boyu > 0:
                x, y = alan.x(), y + satir_boyu + self.bosluk
                satir_boyu = 0
            if not sadece_olc:
                oge.setGeometry(QRect(QPoint(x, y), boyut))
            x += boyut.width() + self.bosluk
            satir_boyu = max(satir_boyu, boyut.height())
        return y + satir_boyu - alan.y()
