## Kısa süre görünen bildirimler ##
# Panellerde durum çubuğuna yazılan her mesaj, pencerenin sağ altında yumuşakça beliren ve birkaç saniye sonra
# solarak kaybolan bir kartta gösterilir: kart zemini, solda türüne göre renkli çizgi ve ikon.
# Kodun mesaj yazdığı yerler (showMessage) değişmeden kalır.
# Geri alınabilen işlemlerde (kitap silme, iade alma) kutunun sağında "Geri Al" butonu çıkar ve kutu daha uzun kalır;
# altındaki ince çubuk kalan süreyi gösterir, fare kutunun üstündeyken süre durur.
# Bildirimin türü (başarı / uyarı / bilgi) mesaj(metin, tur) ile açıkça verilir; verilmezse metinden tahmin edilir.

from PyQt5.QtCore import QEvent, QObject, QPropertyAnimation, Qt, QTimer, QVariantAnimation
from PyQt5.QtWidgets import QFrame, QGraphicsOpacityEffect, QLabel, QPushButton

from acodes import hareket, ikonlar, tema

KENAR_BOSLUK = 24           # pencerenin sağ ve alt kenarından uzaklık
EN_FAZLA_EN = 440
SIMGE = 20
SIMGELER = {"basari": "kontrol", "uyari": "uyari", "bilgi": "bilgi"}
UYARI_KELIMELERI = ("yanlış", "geçmiş", "silinemez", "bulunamadı", "eksik", "gecikti", "olamaz",
                    "seçim yapınız", "seçiniz", "yok!", "yetkiniz")
BASARI_KELIMELERI = ("kaydedildi", "güncellendi", "silindi", "eklendi", "listelendi", "görüntülendi",
                     "temizlendi", "yazıldı", "teslim tarihi", "alındı", "getirildi", "kopyalandı")
EYLEMLI_SURE_MS = 8000      # "Geri Al" gibi bir buton varsa kullanıcıya düşünecek zaman kalsın
CUBUK_BOY = 3               # kalan süre çubuğu
TURLER = ("basari", "uyari", "bilgi")


def tur_bul(metin):
    """Türü verilmeyen mesajlar için metinden tahmin (eski çağrılar ve doğrudan durum çubuğuna yazılanlar)."""
    kucuk = metin.replace("İ", "i").replace("I", "ı").lower()
    if metin.rstrip().endswith("!") or any(k in kucuk for k in UYARI_KELIMELERI):
        return "uyari"
    if any(k in kucuk for k in BASARI_KELIMELERI):
        return "basari"
    return "bilgi"


def renk(tur):
    """Bildirimin vurgu rengi (soldaki çizgi ve ikon); tema değişince güncel paletten okunur."""
    return {"basari": tema.BASARI, "uyari": tema.TEHLIKE, "bilgi": tema.VURGU}[tur]


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
        self.kutu.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.kutu.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.kutu.hide()
        # Belirip solarak gelir ve gider. Kutuyu kaydıran bir animasyon denendi; çizim stili değişirken (tema geçişi)
        # süreci çökertiyordu, saydamlık animasyonu ise güvenli.
        self.saydamlik = QGraphicsOpacityEffect(self.kutu)
        self.kutu.setGraphicsEffect(self.saydamlik)
        self.animasyon = QPropertyAnimation(self.saydamlik, b"opacity", self)
        self.animasyon.finished.connect(self._animasyon_bitti)
        self.simge = QLabel(self.kutu)
        self.simge.setFixedSize(SIMGE, SIMGE)
        self.simge.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.zamanlayici = QTimer(self)
        self.zamanlayici.setSingleShot(True)
        self.zamanlayici.timeout.connect(self.kaybol)
        self.kalan_ms = None            # fare üstündeyken durdurulan sürenin kalanı
        # Kalan süre çubuğu: yalnızca eylemli bildirimlerde, kutunun altında soldan sağa kısalır
        self.cubuk = QFrame(self.kutu, objectName="bildirim_cubuk")
        self.cubuk.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.cubuk.hide()
        self.cubuk_animasyonu = QVariantAnimation(self)
        self.cubuk_animasyonu.setStartValue(1.0)
        self.cubuk_animasyonu.setEndValue(0.0)
        self.cubuk_animasyonu.valueChanged.connect(self._cubugu_ciz)
        self.tur = None
        self._siradaki_tur = None
        self.durum_cubugu = None
        self.eylem = QPushButton(self.kutu, objectName="bildirim_eylem")
        self.eylem.setCursor(Qt.PointingHandCursor)
        self.eylem.setStyleSheet(f"QPushButton#bildirim_eylem {{ background: transparent; color: {tema.VURGU_YAZI};"
                                 f" font-size: {tema.YAZI.metin}px; font-weight: {tema.YARI_KALIN};"
                                 f" border: 1px solid {tema.KENAR_IKINCIL}; border-radius: {tema.KOSE.kucuk}px;"
                                 f" padding: 4px 12px; }}"
                                 f" QPushButton#bildirim_eylem:hover {{ background: {tema.YUZEY}; }}")
        self.eylem.clicked.connect(self._eylem_tiklandi)
        self.eylem.hide()
        self.eylem_islevi = None
        pencere.installEventFilter(self)
        self.kutu.installEventFilter(self)

    def mesaj(self, metin, tur=None, sure=None):
        """Mesajı türüyle gösterir: tur "basari", "uyari" veya "bilgi" (None ise metinden tahmin edilir).
        Durum çubuğuna da yazılır (kodun geri kalanı ve testler oradan okur)."""
        assert tur is None or tur in TURLER, tur
        self._siradaki_tur = tur
        try:
            if self.durum_cubugu is not None:
                self.durum_cubugu.showMessage(metin, sure or sure_ms(metin))
            else:
                self.goster(metin)
        finally:
            self._siradaki_tur = None

    def goster(self, metin, eylem=None):
        """eylem: (buton yazısı, işlev), ör. ("Geri Al", geri_al). Buton yalnızca bu bildirim görünürken çalışır."""
        if not metin:
            return
        self.tur = self._siradaki_tur or tur_bul(metin)
        self.kutu.setText(metin)
        self.eylem_islevi = eylem[1] if eylem else None
        if eylem:
            self.eylem.setText(eylem[0])
            self.eylem.adjustSize()
        self.eylem.setVisible(bool(eylem))
        self.kutu.setAttribute(Qt.WA_TransparentForMouseEvents, not eylem)
        sag = self.eylem.width() + 30 if eylem else 18
        alt = 12 + CUBUK_BOY + 8 if eylem else 12          # eylemli kutuda altta süre çubuğuna yer
        # Seçicili kural: kutunun ikonu ve butonu bu çerçeveyi devralmasın
        self.kutu.setStyleSheet(f"QLabel#bildirim {{ background-color: {tema.KART}; color: {tema.METIN};"
                                f" font-size: {tema.YAZI.metin}px; font-weight: {tema.ORTA};"
                                f" padding: 12px {sag}px {alt}px {SIMGE + 28}px; border: 1px solid {tema.KENAR_IKINCIL};"
                                f" border-left: 4px solid {renk(self.tur)}; border-radius: {tema.KOSE.orta}px; }}")
        self.simge.setPixmap(ikonlar.ikon(SIMGELER[self.tur], renk(self.tur)).pixmap(SIMGE, SIMGE))
        sure = max(sure_ms(metin), EYLEMLI_SURE_MS) if eylem else sure_ms(metin)
        self.kalan_ms = None
        self.cubuk.setStyleSheet(f"QFrame#bildirim_cubuk {{ background-color: {renk(self.tur)};"
                                 f" border-radius: {CUBUK_BOY // 2}px; }}")
        self.cubuk.setVisible(bool(eylem))
        self.cubuk_animasyonu.stop()
        self._yerlestir()
        self.kutu.raise_()
        self.kutu.show()
        self._solma(self.saydamlik.opacity() if self.animasyon.state() else 0.0, 1.0, tema.SURE.orta)
        self.zamanlayici.start(sure)
        if eylem:
            self.cubuk_animasyonu.setDuration(sure)
            self.cubuk_animasyonu.start()

    def eylemli(self, metin, eylem_adi, islev, tur="basari"):
        """Mesajı durum çubuğuna da yazar (kodun geri kalanı gibi) ve bildirimde eylem butonuyla gösterir."""
        self._siradaki_tur = tur
        try:
            if self.durum_cubugu is not None:
                self.durum_cubugu.showMessage(metin, EYLEMLI_SURE_MS)
            self.goster(metin, (eylem_adi, islev))
        finally:
            self._siradaki_tur = None

    def _cubugu_ciz(self, oran=None):
        """Kalan süre çubuğu: kutunun alt kenarında, iç boşluk payıyla; genişliği kalan süreyle orantılı."""
        oran = self.cubuk_animasyonu.currentValue() if oran is None else oran
        if oran is None:
            oran = 1.0
        sol, sag = 12, 12
        tam = max(0, self.kutu.width() - sol - sag)
        self.cubuk.setGeometry(sol, self.kutu.height() - CUBUK_BOY - 7, max(CUBUK_BOY, round(tam * oran)), CUBUK_BOY)

    def _durdur(self):
        """Fare eylemli kutunun üstüne gelince süre (ve çubuk) durur: kullanıcı karar verirken kaybolmasın."""
        if self.zamanlayici.isActive() and self.cubuk.isVisibleTo(self.kutu):
            self.kalan_ms = self.zamanlayici.remainingTime()
            self.zamanlayici.stop()
            self.cubuk_animasyonu.pause()

    def _surdur(self):
        if self.kalan_ms is not None:
            self.zamanlayici.start(max(1500, self.kalan_ms))
            self.kalan_ms = None
            self.cubuk_animasyonu.resume()

    def _eylem_tiklandi(self):
        islev, self.eylem_islevi = self.eylem_islevi, None
        self.eylem.hide()
        self.cubuk.hide()
        self.cubuk_animasyonu.stop()
        self.kaybol()
        if islev:
            islev()

    def kaybol(self):
        self.kalan_ms = None
        self._solma(self.saydamlik.opacity(), 0.0, tema.SURE.uzun)

    def _solma(self, baslangic, bitis, sure):
        self.animasyon.stop()
        if not hareket.izinli():            # "Hareketi azalt": hemen görünür / kaybolur
            self.saydamlik.setOpacity(bitis)
            self.animasyon.setEndValue(bitis)
            self._animasyon_bitti()
            return
        self.animasyon.setDuration(sure)
        self.animasyon.setStartValue(baslangic)
        self.animasyon.setEndValue(bitis)
        self.animasyon.start()

    def _animasyon_bitti(self):
        if self.animasyon.endValue() == 0.0:
            self.kutu.hide()
            self.cubuk_animasyonu.stop()

    def _yerlestir(self):
        """Kartı ölçüp sağ alttaki yerine koyar."""
        # Genişlik metne göre: kısa mesaj küçük kart, uzun mesaj en fazla EN_FAZLA_EN (gerekirse alt satıra geçer)
        sinir = min(EN_FAZLA_EN, self.pencere.width() - 2 * KENAR_BOSLUK)
        self.kutu.setMinimumWidth(0)
        self.kutu.setMaximumWidth(16777215)
        ek = self.eylem.width() + 30 if self.eylem.isVisibleTo(self.kutu) else 0
        en = max(260, min(sinir, self.kutu.fontMetrics().horizontalAdvance(self.kutu.text()) + SIMGE + 70 + ek))
        self.kutu.setFixedWidth(en)
        self.kutu.adjustSize()
        if ek:
            self.eylem.move(en - self.eylem.width() - 12, (self.kutu.height() - self.eylem.height()) // 2)
        self.simge.move(18, (self.kutu.height() - SIMGE) // 2)
        self._cubugu_ciz()
        self.kutu.move(self.pencere.width() - en - KENAR_BOSLUK, self.pencere.height() - self.kutu.height() - KENAR_BOSLUK)

    def eventFilter(self, nesne, olay):
        if nesne is self.kutu:
            if olay.type() == QEvent.Enter:
                self._durdur()
            elif olay.type() == QEvent.Leave:
                self._surdur()
        elif olay.type() == QEvent.Resize and self.kutu.isVisible():
            self._yerlestir()
        return False


def baglan(pencere, durum_cubugu):
    """Durum çubuğuna yazılan mesajları bildirim olarak gösterir ve durum çubuğunu gizler."""
    bildirim = Bildirim(pencere)
    bildirim.durum_cubugu = durum_cubugu
    durum_cubugu.messageChanged.connect(bildirim.goster)
    durum_cubugu.hide()
    return bildirim
