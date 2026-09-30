## Esnek yerleşim ##
# .ui dosyalarındaki sayfalar sabit piksel konumlarıyla çizilmiş; pencere büyüyünce sol üstte küçük kalıyorlardı.
# Buradaki kalıplar mevcut bileşenleri yerleşim düzenlerine (layout) alır: tablolar ve alanlar pencereyle büyür.

from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtWidgets import QFormLayout, QGroupBox, QHBoxLayout, QLayout, QLineEdit, QVBoxLayout

SINIRSIZ = 16777215


def buton_boyutu(buton, en=(110, 170), boy=40):
    buton.setMinimumSize(en[0], boy)
    buton.setMaximumSize(en[1], boy)


def liste_sayfasi(sayfa, butonlar, tablo, ust=None):
    """Solda alt alta butonlar, sağda (isteğe bağlı üst satır ve) pencereyle büyüyen tablo."""
    duzen = QHBoxLayout(sayfa)
    duzen.setContentsMargins(14, 12, 14, 12)
    duzen.setSpacing(14)
    sol = QVBoxLayout()
    sol.setSpacing(10)
    if ust is not None:
        sol.addSpacing(52)            # butonlar tablonun hizasından başlasın
    for buton in butonlar:
        buton_boyutu(buton, (120, 160))
        sol.addWidget(buton)
    sol.addStretch()
    sag = QVBoxLayout()
    sag.setSpacing(10)
    if ust is not None:
        sag.addLayout(ust)
    sag.addWidget(tablo, 1)
    duzen.addLayout(sol)
    duzen.addLayout(sag, 1)
    return duzen


def form_kutusu(baslik, secici, butonlar, form_bileseni, eski_baslik=None):
    """Başlıklı kart: üstte seçim kutusu ve butonlar, altında etiket-alan formu (alanlar genişler)."""
    kutu = QGroupBox(baslik)
    dikey = QVBoxLayout(kutu)
    dikey.setSpacing(12)
    satir = QHBoxLayout()
    secici.setMinimumWidth(200)
    secici.setMaximumWidth(SINIRSIZ)
    satir.addWidget(secici, 1)
    for buton in butonlar:
        buton_boyutu(buton, (100, 130), 36)
        satir.addWidget(buton)
    dikey.addLayout(satir)
    form_bileseni.setParent(kutu)
    form = form_bileseni.layout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setContentsMargins(0, 6, 0, 0)
    form.setVerticalSpacing(10)
    for alan in form_bileseni.findChildren(QLineEdit):
        alan.setMinimumSize(0, 30)
        alan.setMaximumSize(SINIRSIZ, SINIRSIZ)
    dikey.addWidget(form_bileseni)
    dikey.addStretch()
    if eski_baslik is not None:
        eski_baslik.hide()            # başlık artık kartın üstünde
    return kutu


def islem_sayfasi(sayfa, kutular, ana_buton):
    """Yan yana kartlar ve sağ altta ana işlem butonu (ör. Ödünç Ver)."""
    duzen = QVBoxLayout(sayfa)
    duzen.setContentsMargins(14, 12, 14, 12)
    duzen.setSpacing(12)
    satir = QHBoxLayout()
    satir.setSpacing(14)
    for kutu in kutular:
        satir.addWidget(kutu, 1)
    duzen.addLayout(satir, 1)
    alt = QHBoxLayout()
    alt.addStretch()
    buton_boyutu(ana_buton, (180, 240), 46)
    alt.addWidget(ana_buton)
    duzen.addLayout(alt)
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
