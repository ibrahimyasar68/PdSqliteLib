## Kısa süre görünen bildirimler ##
# Panellerde durum çubuğuna yazılan her mesaj, pencerenin alt ortasında yumuşakça beliren ve birkaç saniye
# sonra kaybolan bir kutuda gösterilir. Kodun mesaj yazdığı yerler (showMessage) değişmeden kalır.

from PyQt5.QtCore import QEvent, QObject, QPropertyAnimation, Qt, QTimer
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QLabel

from acodes import tema

ALT_BOSLUK = 80
RENKLER = {"basari": "#15803D", "uyari": tema.TEHLIKE, "bilgi": "#1F2937"}
UYARI_KELIMELERI = ("yanlış", "geçmiş", "silinemez", "bulunamadı", "eksik", "gecikti", "olamaz",
                    "seçim yapınız", "seçiniz", "yok!", "yetkiniz")
BASARI_KELIMELERI = ("kaydedildi", "güncellendi", "silindi", "eklendi", "listelendi", "görüntülendi",
                     "temizlendi", "yazıldı", "teslim tarihi", "alındı")


def tur_bul(metin):
    kucuk = metin.replace("İ", "i").replace("I", "ı").lower()
    if metin.rstrip().endswith("!") or any(k in kucuk for k in UYARI_KELIMELERI):
        return "uyari"
    if any(k in kucuk for k in BASARI_KELIMELERI):
        return "basari"
    return "bilgi"


def sure_ms(metin):
    """Okuma süresine göre: en az 2,5 sn, uzun mesajlarda en fazla 7 sn."""
    return max(2500, min(7000, 1500 + len(metin) * 45))


class Bildirim(QObject):
    def __init__(self, pencere):
        super().__init__(pencere)
        self.pencere = pencere
        self.kutu = QLabel(pencere)
        self.kutu.setObjectName("bildirim")
        self.kutu.setWordWrap(True)
        self.kutu.setAlignment(Qt.AlignCenter)
        self.kutu.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.kutu.hide()
        self.saydamlik = QGraphicsOpacityEffect(self.kutu)
        self.kutu.setGraphicsEffect(self.saydamlik)
        self.animasyon = QPropertyAnimation(self.saydamlik, b"opacity", self)
        self.animasyon.finished.connect(self._animasyon_bitti)
        self.zamanlayici = QTimer(self)
        self.zamanlayici.setSingleShot(True)
        self.zamanlayici.timeout.connect(self.kaybol)
        self.tur = None
        pencere.installEventFilter(self)

    def goster(self, metin):
        if not metin:
            return
        self.tur = tur_bul(metin)
        self.kutu.setText(metin)
        self.kutu.setStyleSheet(f"background-color: {RENKLER[self.tur]}; color: white; font-size: 16px;"
                                " font-weight: bold; padding: 10px 18px; border-radius: 10px;")
        self._yerlestir()
        self.kutu.raise_()
        self.kutu.show()
        self._solma(self.saydamlik.opacity() if self.animasyon.state() else 0.0, 1.0, 180)
        self.zamanlayici.start(sure_ms(metin))

    def kaybol(self):
        self._solma(self.saydamlik.opacity(), 0.0, 400)

    def _solma(self, baslangic, bitis, sure):
        self.animasyon.stop()
        self.animasyon.setDuration(sure)
        self.animasyon.setStartValue(baslangic)
        self.animasyon.setEndValue(bitis)
        self.animasyon.start()

    def _animasyon_bitti(self):
        if self.animasyon.endValue() == 0.0:
            self.kutu.hide()

    def _yerlestir(self):
        # Genişlik metne göre: kısa mesaj küçük kutu, uzun mesaj en fazla 620 piksel (gerekirse alt satıra geçer)
        sinir = min(620, self.pencere.width() - 80)
        self.kutu.setMinimumWidth(0)
        self.kutu.setMaximumWidth(16777215)
        en = max(220, min(sinir, self.kutu.fontMetrics().horizontalAdvance(self.kutu.text()) + 60))
        self.kutu.setFixedWidth(en)
        self.kutu.adjustSize()
        # Alt kenardan biraz yukarıda: sekmelerin alt çubuğunu (ör. Kayıt Ekleme / Düzenleme) örtmesin
        self.kutu.move((self.pencere.width() - en) // 2, self.pencere.height() - self.kutu.height() - ALT_BOSLUK)

    def eventFilter(self, nesne, olay):
        if olay.type() == QEvent.Resize and self.kutu.isVisible():
            self._yerlestir()
        return False


def baglan(pencere, durum_cubugu):
    """Durum çubuğuna yazılan mesajları bildirim olarak gösterir ve durum çubuğunu gizler."""
    bildirim = Bildirim(pencere)
    durum_cubugu.messageChanged.connect(bildirim.goster)
    durum_cubugu.hide()
    return bildirim
