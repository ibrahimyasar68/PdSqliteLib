## Kısa süre görünen bildirimler ##
# Panellerde durum çubuğuna yazılan her mesaj, pencerenin sağ altında yumuşakça beliren ve birkaç saniye sonra
# solarak kaybolan bir kartta gösterilir: kart zemini, solda türüne göre renkli çizgi ve ikon.
# Kodun mesaj yazdığı yerler (showMessage) değişmeden kalır.
# Geri alınabilen işlemlerde (kitap silme, iade alma) kutunun sağında "Geri Al" butonu çıkar ve kutu daha uzun kalır;
# altındaki ince çubuk kalan süreyi gösterir, fare kutunun üstündeyken süre durur.
# Bildirimin türü (başarı / uyarı / bilgi) mesaj(metin, tur) ile açıkça verilir; verilmezse metinden tahmin edilir.
# Yeni mesaj gelince eylemsiz kartın yazısı değişir; "Geri Al"lı kart ise süresi bitene kadar kalır, yeni kart altına
# gelir ve eskiler yukarı kayar (en fazla UST_USTE kart).

from PySide6.QtCore import QAbstractAnimation, QEasingCurve, QEvent, QObject, QPropertyAnimation, Qt, QTimer, QVariantAnimation
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect, QLabel, QPushButton

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
UST_USTE = 3                # aynı anda görünen en fazla kart
ARALIK = 8                  # üst üste kartlar arası boşluk


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


class Kart(QObject):
    """Tek bildirim kartı: zemin, ikon, isteğe bağlı eylem butonu ve kalan süre çubuğu. Kendi süresini tutar;
    kaybolunca bitti yayınlar."""

    def __init__(self, bildirim):
        super().__init__(bildirim)
        self.bildirim = bildirim
        pencere = bildirim.pencere
        self.kutu = QLabel(pencere)
        self.kutu.setObjectName("bildirim")
        self.kutu.setWordWrap(True)
        self.kutu.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.kutu.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.kutu.hide()
        # Belirip solarak gelir ve gider. Kaydırma (üst üste dizilince) move() ile yapılır; çizim stili değişmeden
        # önce (tema geçişi) temizle() tüm animasyonları durdurur: stil değişirken süren animasyon süreci çökertiyordu.
        self.saydamlik = QGraphicsOpacityEffect(self.kutu)
        self.kutu.setGraphicsEffect(self.saydamlik)
        self.animasyon = QPropertyAnimation(self.saydamlik, b"opacity", self)
        self.animasyon.finished.connect(self._animasyon_bitti)
        self.kayma = QVariantAnimation(self)
        self.kayma.setDuration(tema.SURE.orta)
        self.kayma.setEasingCurve(QEasingCurve.OutCubic)
        self.kayma.valueChanged.connect(lambda y: self.kutu.move(self.kutu.x(), y))
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
        self.kutu.installEventFilter(self)

    def gorunur(self):
        """Ekranda mı (solarak kaybolmuyorsa)?"""
        solarak_kayboluyor = self.animasyon.state() != QAbstractAnimation.Stopped and self.animasyon.endValue() == 0.0
        return self.kutu.isVisible() and not solarak_kayboluyor

    def eylemli_mi(self):
        return self.eylem_islevi is not None

    def goster(self, metin, tur, eylem=None):
        self.tur = tur
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
                                f" border-left: 4px solid {renk(tur)}; border-radius: {tema.KOSE.orta}px; }}")
        self.simge.setPixmap(ikonlar.ikon(SIMGELER[tur], renk(tur)).pixmap(SIMGE, SIMGE))
        sure = max(sure_ms(metin), EYLEMLI_SURE_MS) if eylem else sure_ms(metin)
        self.kalan_ms = None
        self.cubuk.setStyleSheet(f"QFrame#bildirim_cubuk {{ background-color: {renk(tur)};"
                                 f" border-radius: {CUBUK_BOY // 2}px; }}")
        self.cubuk.setVisible(bool(eylem))
        self.cubuk_animasyonu.stop()
        self.boyutla()
        self.kutu.raise_()
        self.kutu.show()
        calisiyor = self.animasyon.state() != QAbstractAnimation.Stopped
        self._solma(self.saydamlik.opacity() if calisiyor else 0.0, 1.0, tema.SURE.orta)
        self.zamanlayici.start(sure)
        if eylem:
            self.cubuk_animasyonu.setDuration(sure)
            self.cubuk_animasyonu.start()

    def boyutla(self):
        """Genişlik metne göre: kısa mesaj küçük kart, uzun mesaj en fazla EN_FAZLA_EN (gerekirse alt satıra geçer)."""
        pencere = self.bildirim.pencere
        sinir = min(EN_FAZLA_EN, pencere.width() - 2 * KENAR_BOSLUK)
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

    def yerine_git(self, y, animasyonlu):
        """Kartı sağ kenara yaslı, verilen yüksekliğe koyar; üst üste dizilirken yukarı kayarak gider."""
        x = self.bildirim.pencere.width() - self.kutu.width() - KENAR_BOSLUK
        self.kayma.stop()
        if animasyonlu and hareket.izinli() and self.kutu.isVisible() and self.kutu.y() != y:
            self.kutu.move(x, self.kutu.y())
            self.kayma.setStartValue(self.kutu.y())
            self.kayma.setEndValue(y)
            self.kayma.start()
        else:
            self.kutu.move(x, y)

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
        self.zamanlayici.stop()
        self._solma(self.saydamlik.opacity(), 0.0, tema.SURE.uzun)

    def durdur(self):
        """Tüm animasyon ve süreleri durdurup kartı gizler (tema geçişinden önce)."""
        for animasyon in (self.animasyon, self.kayma, self.cubuk_animasyonu):
            animasyon.stop()
        self.zamanlayici.stop()
        self.kutu.hide()

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
            self.eylem_islevi = None
            self.bildirim._kart_bitti(self)

    def eventFilter(self, nesne, olay):
        if olay.type() == QEvent.Enter:
            self._durdur()
        elif olay.type() == QEvent.Leave:
            self._surdur()
        return False


class Bildirim(QObject):
    """Pencerenin bildirim kartları. kutu, eylem, tur gibi adlar en yeni kartı gösterir."""

    def __init__(self, pencere):
        super().__init__(pencere)
        self.pencere = pencere
        self.son = Kart(self)           # en yeni (en altta duran) kart
        self.eskiler = []               # süresi dolmamış eylemli kartlar, eskiden yeniye
        self.durum_cubugu = None
        self._siradaki_tur = None
        pencere.installEventFilter(self)

    # En yeni kartın parçaları (eski kodla ve testlerle uyum için)
    kutu = property(lambda self: self.son.kutu)
    eylem = property(lambda self: self.son.eylem)
    simge = property(lambda self: self.son.simge)
    cubuk = property(lambda self: self.son.cubuk)
    zamanlayici = property(lambda self: self.son.zamanlayici)
    tur = property(lambda self: self.son.tur)
    eylem_islevi = property(lambda self: self.son.eylem_islevi)
    kalan_ms = property(lambda self: self.son.kalan_ms)

    def kartlar(self):
        return self.eskiler + [self.son]

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
        if self.son.gorunur() and self.son.eylemli_mi():
            # Geri Al'ı olan kart süresi bitene kadar kalır: yukarı kayar, yenisi altına gelir
            self.eskiler.append(self.son)
            self.son = Kart(self)
            while len(self.eskiler) >= UST_USTE:
                self.eskiler.pop(0).kaybol()
        self.son.goster(metin, self._siradaki_tur or tur_bul(metin), eylem)
        self._diz(animasyonlu=True)

    def eylemli(self, metin, eylem_adi, islev, tur="basari"):
        """Mesajı durum çubuğuna da yazar (kodun geri kalanı gibi) ve bildirimde eylem butonuyla gösterir."""
        self._siradaki_tur = tur
        try:
            if self.durum_cubugu is not None:
                self.durum_cubugu.blockSignals(True)       # aynı mesaj önce eylemsiz kart olarak çıkmasın
                self.durum_cubugu.showMessage(metin, EYLEMLI_SURE_MS)
                self.durum_cubugu.blockSignals(False)
            self.goster(metin, (eylem_adi, islev))
        finally:
            self._siradaki_tur = None

    def kaybol(self):
        self.son.kaybol()

    def temizle(self):
        """Tüm kartları animasyonsuz kaldırır (tema geçişinden önce: stil değişirken animasyon sürmesin)."""
        for kart in self.kartlar():
            kart.durdur()
        for kart in self.eskiler:
            kart.deleteLater()
        self.eskiler = []

    def _kart_bitti(self, kart):
        if kart is not self.son:            # en yeni kart yeniden kullanılır, eskiler silinir
            if kart in self.eskiler:
                self.eskiler.remove(kart)
            kart.kutu.deleteLater()
            kart.deleteLater()
            self._diz(animasyonlu=True)

    def _diz(self, animasyonlu=False):
        """En yeni kart en altta; eskiler üstünde, aralarında ARALIK kadar boşlukla."""
        y = self.pencere.height() - KENAR_BOSLUK
        for kart in reversed(self.kartlar()):
            if kart.kutu.isHidden():          # pencere henüz açılmadıysa da yerleştirilir
                continue
            y -= kart.kutu.height()
            kart.yerine_git(y, animasyonlu and kart is not self.son)
            y -= ARALIK

    def _yerlestir(self):
        for kart in self.kartlar():
            if not kart.kutu.isHidden():
                kart.boyutla()
        self._diz()

    def eventFilter(self, nesne, olay):
        if olay.type() == QEvent.Resize and not self.son.kutu.isHidden():
            self._yerlestir()
        return False


def baglan(pencere, durum_cubugu):
    """Durum çubuğuna yazılan mesajları bildirim olarak gösterir ve durum çubuğunu gizler."""
    bildirim = Bildirim(pencere)
    bildirim.durum_cubugu = durum_cubugu
    durum_cubugu.messageChanged.connect(bildirim.goster)
    durum_cubugu.hide()
    return bildirim
