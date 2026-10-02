## Kısa süre görünen bildirimler ##
# Panellerde durum çubuğuna yazılan her mesaj, pencerenin alt ortasında yumuşakça beliren ve birkaç saniye
# sonra kaybolan bir kutuda gösterilir. Kodun mesaj yazdığı yerler (showMessage) değişmeden kalır.
# Geri alınabilen işlemlerde (kitap silme, iade alma) kutunun sağında "Geri Al" butonu çıkar ve kutu daha uzun kalır.

from PyQt5.QtCore import QEvent, QObject, QPropertyAnimation, Qt, QTimer
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QLabel, QPushButton

from acodes import tema

ALT_BOSLUK = 80
RENKLER = {"basari": "#15803D", "uyari": tema.TEHLIKE, "bilgi": "#1F2937"}
UYARI_KELIMELERI = ("yanlış", "geçmiş", "silinemez", "bulunamadı", "eksik", "gecikti", "olamaz",
                    "seçim yapınız", "seçiniz", "yok!", "yetkiniz")
BASARI_KELIMELERI = ("kaydedildi", "güncellendi", "silindi", "eklendi", "listelendi", "görüntülendi",
                     "temizlendi", "yazıldı", "teslim tarihi", "alındı", "getirildi", "kopyalandı")
EYLEMLI_SURE_MS = 8000      # "Geri Al" gibi bir buton varsa kullanıcıya düşünecek zaman kalsın


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
        self.durum_cubugu = None
        self.eylem = QPushButton(self.kutu, objectName="bildirim_eylem")
        self.eylem.setCursor(Qt.PointingHandCursor)
        self.eylem.setStyleSheet("QPushButton#bildirim_eylem { background: transparent; color: white; font-size: 15px;"
                                 " font-weight: bold; border: 1px solid rgba(255,255,255,0.75); border-radius: 7px;"
                                 " padding: 4px 12px; }"
                                 " QPushButton#bildirim_eylem:hover { background: rgba(255,255,255,0.18); }")
        self.eylem.clicked.connect(self._eylem_tiklandi)
        self.eylem.hide()
        self.eylem_islevi = None
        pencere.installEventFilter(self)

    def goster(self, metin, eylem=None):
        """eylem: (buton yazısı, işlev), ör. ("Geri Al", geri_al). Buton yalnızca bu bildirim görünürken çalışır."""
        if not metin:
            return
        self.tur = tur_bul(metin)
        self.kutu.setText(metin)
        self.eylem_islevi = eylem[1] if eylem else None
        if eylem:
            self.eylem.setText(eylem[0])
            self.eylem.adjustSize()
        self.eylem.setVisible(bool(eylem))
        self.kutu.setAttribute(Qt.WA_TransparentForMouseEvents, not eylem)
        sag = self.eylem.width() + 30 if eylem else 18
        self.kutu.setStyleSheet(f"background-color: {RENKLER[self.tur]}; color: white; font-size: 16px;"
                                f" font-weight: bold; padding: 10px {sag}px 10px 18px; border-radius: 10px;")
        self._yerlestir()
        self.kutu.raise_()
        self.kutu.show()
        self._solma(self.saydamlik.opacity() if self.animasyon.state() else 0.0, 1.0, 180)
        self.zamanlayici.start(max(sure_ms(metin), EYLEMLI_SURE_MS) if eylem else sure_ms(metin))

    def eylemli(self, metin, eylem_adi, islev):
        """Mesajı durum çubuğuna da yazar (kodun geri kalanı gibi) ve bildirimde eylem butonuyla gösterir."""
        if self.durum_cubugu is not None:
            self.durum_cubugu.showMessage(metin, EYLEMLI_SURE_MS)
        self.goster(metin, (eylem_adi, islev))

    def _eylem_tiklandi(self):
        islev, self.eylem_islevi = self.eylem_islevi, None
        self.eylem.hide()
        self.kaybol()
        if islev:
            islev()

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
        ek = self.eylem.width() + 30 if self.eylem.isVisibleTo(self.kutu) else 0
        en = max(220, min(sinir, self.kutu.fontMetrics().horizontalAdvance(self.kutu.text()) + 60 + ek))
        self.kutu.setFixedWidth(en)
        self.kutu.adjustSize()
        if ek:
            self.eylem.move(en - self.eylem.width() - 12, (self.kutu.height() - self.eylem.height()) // 2)
        # Alt kenardan biraz yukarıda: sekmelerin alt çubuğunu (ör. Kayıt Ekleme / Düzenleme) örtmesin
        self.kutu.move((self.pencere.width() - en) // 2, self.pencere.height() - self.kutu.height() - ALT_BOSLUK)

    def eventFilter(self, nesne, olay):
        if olay.type() == QEvent.Resize and self.kutu.isVisible():
            self._yerlestir()
        return False


def baglan(pencere, durum_cubugu):
    """Durum çubuğuna yazılan mesajları bildirim olarak gösterir ve durum çubuğunu gizler."""
    bildirim = Bildirim(pencere)
    bildirim.durum_cubugu = durum_cubugu
    durum_cubugu.messageChanged.connect(bildirim.goster)
    durum_cubugu.hide()
    return bildirim
