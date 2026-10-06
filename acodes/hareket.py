## Kısa geçiş animasyonları ##
# Sayfa değişince yeni sayfa hafifçe belirir, kenar menüsü daralıp açılırken genişliği yumuşakça değişir,
# tema değişince eski görünüm solarak kaybolur, kaydedilen / ödünç verilen satır kısa süre parlayıp söner.
# Ayrıca: yanlış girişte kart sallanır, hatalı alanın çerçevesi kırmızıdan söner, seçili menü / segment vurgusu
# kayarak gider, sayılar sayarak gelir, gecikme rozeti bir kez nabız gibi atar. Alt bölüm değişince yeni bölüm
# seçilen yönden kayarak gelir, kılavuz konuları yükseklikleri değişerek açılıp kapanır. Kartlar ve giriş formu
# sırayla gelir, filtre etiketleri açılarak eklenip daralarak gider, sonuç sayıları akarak değişir. Butonların
# üstüne gelince renk kısa bir geçişle değişir, odaklanan yazı alanının çevresinde yumuşak bir ışık belirir.
# Süreler tema.SURE ölçeğinden gelir. Animasyonlar yalnızca pencere ekrandayken çalışır.
# ANIMASYON = False testlerde kapatır; AZALT kullanıcının "Hareketi azalt" tercihidir (Ayarlar > Görünüm).

import re

from PySide6.QtCore import (QEasingCurve, QEvent, QObject, QPersistentModelIndex, QPoint, QPropertyAnimation, QRect,
                          QRectF, QSequentialAnimationGroup, Qt, QTimer, QVariantAnimation)
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect, QLabel, QWidget

from acodes import tema

ANIMASYON = True
AZALT = False
TERCIH = "gorunum/hareketi_azalt"
SINIRSIZ = 16777215          # Qt'nin en büyük bileşen boyutu (QWIDGETSIZE_MAX)


def izinli():
    return ANIMASYON and not AZALT


def acik_mi(bilesen):
    return izinli() and bilesen is not None and bilesen.isVisible()


def belir(sayfa):
    """Sayfayı saydamdan görünüre getirir; bitince efekt kaldırılır (çizim yükü kalmasın)."""
    if not acik_mi(sayfa) or sayfa.graphicsEffect() is not None:
        return
    efekt = QGraphicsOpacityEffect(sayfa)
    efekt.setOpacity(0.0)
    sayfa.setGraphicsEffect(efekt)
    animasyon = QPropertyAnimation(efekt, b"opacity", efekt)
    animasyon.setDuration(tema.SURE.kisa)
    animasyon.setStartValue(0.0)
    animasyon.setEndValue(1.0)
    animasyon.setEasingCurve(QEasingCurve.OutCubic)
    animasyon.finished.connect(lambda: sayfa.graphicsEffect() is efekt and sayfa.setGraphicsEffect(None))
    animasyon.start()


def kayarak_belir(sayfa, yon, kayma=16, dikey=False, sure=None, bitince=None):
    """Sayfa yon tarafından (1: sağdan / alttan, -1: soldan / üstten) birkaç piksel kayarak ve belirerek gelir
    (alt bölüm anahtarı: içerik, seçili zeminin kaydığı yöne akar; menü: aşağıdaki bölüm aşağıdan gelir).
    Bitince sayfa yerine döner, efekt kaldırılır."""
    if not yon or not acik_mi(sayfa) or sayfa.graphicsEffect() is not None:
        return None
    yer = sayfa.pos()
    efekt = QGraphicsOpacityEffect(sayfa)
    efekt.setOpacity(0.0)
    sayfa.setGraphicsEffect(efekt)
    animasyon = QVariantAnimation(efekt)
    animasyon.setDuration(sure or tema.SURE.orta)
    animasyon.setStartValue(0.0)
    animasyon.setEndValue(1.0)
    animasyon.setEasingCurve(QEasingCurve.OutCubic)

    isik = getattr(sayfa, "_odak_isigi", None)       # odaklı alanın ışığı alanla birlikte belirsin

    def adim(t):
        efekt.setOpacity(t)
        kay = round(yon * kayma * (1 - t))
        sayfa.move(yer.x(), yer.y() + kay) if dikey else sayfa.move(yer.x() + kay, yer.y())
        if isik is not None and isik.isVisible():
            isik.yerles()
            isik.update()

    def bitti():
        sayfa.move(yer)
        if sayfa.graphicsEffect() is efekt:
            sayfa.setGraphicsEffect(None)
        if bitince:
            bitince()

    animasyon.valueChanged.connect(adim)
    animasyon.finished.connect(bitti)
    adim(0.0)
    animasyon.start()
    return animasyon


def yukseklikle_goster(bilesen, goster):
    """Bileşen yüksekliği sıfırdan açılarak görünür veya kapanarak gizlenir (kılavuz konuları). Altındakiler
    birden zıplamaz, yumuşakça yer değiştirir. Animasyon kapalıysa hemen gösterilir / gizlenir."""
    eski = getattr(bilesen, "_yukseklik_animasyonu", None)
    if eski is not None:
        eski.stop()
        bilesen._yukseklik_animasyonu = None
    kap = bilesen.parentWidget()
    if not acik_mi(kap):
        bilesen.setMaximumHeight(SINIRSIZ)
        bilesen.setVisible(goster)
        return None
    if goster:
        bas = bilesen.height() if bilesen.isVisible() else 0
        bilesen.setMaximumHeight(bas)
        bilesen.show()
        if kap.layout() is not None:
            kap.layout().activate()         # gizliyken bilinmeyen genişlik yerleşsin (yükseklik ona bağlı)
        en = bilesen.width()
        hedef = bilesen.heightForWidth(en) if bilesen.hasHeightForWidth() else -1
        hedef = hedef if hedef > 0 else bilesen.sizeHint().height()
    else:
        if bilesen.isHidden():
            return None
        bas, hedef = bilesen.height(), 0
    if bas == hedef:
        bilesen.setMaximumHeight(SINIRSIZ)
        bilesen.setVisible(goster)
        return None
    animasyon = QVariantAnimation(bilesen)
    animasyon.setDuration(tema.SURE.orta)
    animasyon.setStartValue(bas)
    animasyon.setEndValue(hedef)
    animasyon.setEasingCurve(QEasingCurve.OutCubic)
    animasyon.valueChanged.connect(bilesen.setMaximumHeight)

    def bitti():
        bilesen._yukseklik_animasyonu = None
        bilesen.setMaximumHeight(SINIRSIZ)      # pencere daralınca yazı yeniden kırılabilsin
        bilesen.setVisible(goster)

    animasyon.finished.connect(bitti)
    bilesen._yukseklik_animasyonu = animasyon
    animasyon.start()
    return animasyon


def genislige_kay(bilesen, hedef, bitince=None):
    """Bileşenin sabit genişliğini hedefe yumuşakça getirir; animasyon kapalıysa hemen ayarlar.
    Her bileşenin tek animasyonu vardır: yarıda yeni bir istek gelirse eskisi (ve bitince işi) iptal olur."""
    animasyon = getattr(bilesen, "_genislik_animasyonu", None)
    if animasyon is None:
        animasyon = QVariantAnimation(bilesen)
        animasyon.setDuration(tema.SURE.orta)
        animasyon.setEasingCurve(QEasingCurve.OutCubic)
        animasyon.valueChanged.connect(bilesen.setFixedWidth)
        bilesen._genislik_animasyonu = animasyon
    animasyon.stop()
    onceki = getattr(bilesen, "_genislik_bitince", None)
    if onceki is not None:          # yarıda kalan isteğin bitince işi iptal
        animasyon.finished.disconnect(onceki)
        bilesen._genislik_bitince = None
    if not acik_mi(bilesen) or bilesen.width() == hedef:
        bilesen.setFixedWidth(hedef)
        if bitince:
            bitince()
        return
    animasyon.setStartValue(bilesen.width())
    animasyon.setEndValue(hedef)
    if bitince:
        animasyon.finished.connect(bitince)
        bilesen._genislik_bitince = bitince
    animasyon.start()


def perde(pencere, goruntu):
    """Pencerenin üstüne eski görünümün resmini koyar ve solarak kaldırır (tema geçişinde yanıp sönme olmasın).
    Animasyon kapalıysa bir şey yapmaz. Perde fareyi engellemez; bitince silinir."""
    if not acik_mi(pencere) or goruntu is None or goruntu.isNull():
        return None
    etiket = QLabel(pencere, objectName="tema_perdesi")
    etiket.setAttribute(Qt.WA_TransparentForMouseEvents)
    etiket.setPixmap(goruntu)
    etiket.setGeometry(pencere.rect())
    efekt = QGraphicsOpacityEffect(etiket)
    etiket.setGraphicsEffect(efekt)
    animasyon = QPropertyAnimation(efekt, b"opacity", etiket)
    animasyon.setDuration(tema.SURE.uzun)
    animasyon.setStartValue(1.0)
    animasyon.setEndValue(0.0)
    animasyon.setEasingCurve(QEasingCurve.InOutQuad)
    animasyon.finished.connect(etiket.deleteLater)
    etiket.show()
    etiket.raise_()
    animasyon.start()
    return etiket


class _Parlama(QWidget):
    """Tablonun görünen alanında bir satırın üstüne vurgu rengini çizer; renk animasyonla söner.
    Satır sıralama ile yer değiştirse de (kalıcı indeks) üstünde kalır."""

    def __init__(self, tablo, satir):
        super().__init__(tablo.viewport())
        self.tablo = tablo
        self.indeks = QPersistentModelIndex(tablo.model().index(satir, 0))
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.guc = 1.0
        self.animasyon = QVariantAnimation(self)
        self.animasyon.setDuration(tema.SURE.parlama)
        self.animasyon.setStartValue(1.0)
        self.animasyon.setEndValue(0.0)
        self.animasyon.setEasingCurve(QEasingCurve.InQuad)
        self.animasyon.valueChanged.connect(self._ilerle)
        self.animasyon.finished.connect(self._bitti)
        self._ilerle(1.0)
        self.show()
        self.animasyon.start()

    def _ilerle(self, guc):
        self.guc = guc
        # Tablo kaydırılınca görünen alandaki çocuklar da kayar: her adımda alanın tamamını kaplar
        self.setGeometry(self.tablo.viewport().rect())
        self.update()

    def _bitti(self):
        if getattr(self.tablo, "_parlama", None) is self:
            self.tablo._parlama = None
        self.deleteLater()

    def paintEvent(self, olay):
        if not self.indeks.isValid():
            return
        satir = self.indeks.row()
        renk = QColor(tema.VURGU)
        renk.setAlphaF((0.35 if tema.KOYU_MU else 0.22) * self.guc)
        p = QPainter(self)
        p.fillRect(0, self.tablo.rowViewportPosition(satir), self.width(), self.tablo.rowHeight(satir), renk)
        p.end()


def satiri_parlat(tablo, satir):
    """Kaydedilen, ödünç verilen veya geri getirilen satırı kısa süre vurgular (değişen yer gözden kaçmasın).
    Aynı tabloda yenisi başlarsa eskisi kaldırılır."""
    if not acik_mi(tablo) or satir is None or not 0 <= satir < tablo.model().rowCount():
        return None
    eski = getattr(tablo, "_parlama", None)
    if eski is not None:
        eski.animasyon.stop()
        eski.deleteLater()
    tablo._parlama = _Parlama(tablo, satir)
    return tablo._parlama


def secili_satiri_parlat(tablo):
    satirlar = tablo.selectionModel().selectedRows() if tablo.selectionModel() else []
    return satiri_parlat(tablo, satirlar[0].row()) if satirlar else None


def salla(bilesen):
    """Yanlış girişte bileşeni yatayda kısa süre sallar (sönen titreşim), sonra yerine bırakır."""
    if not acik_mi(bilesen) or getattr(bilesen, "_salla", None) is not None:
        return None
    yer = bilesen.pos()
    animasyon = QVariantAnimation(bilesen)
    animasyon.setDuration(tema.SURE.uzun)
    animasyon.setStartValue(0.0)
    animasyon.setEndValue(1.0)

    def adim(t):
        import math
        bilesen.move(yer.x() + round(8 * (1 - t) * math.sin(t * math.pi * 6)), yer.y())

    def bitti():
        bilesen.move(yer)
        bilesen._salla = None

    animasyon.valueChanged.connect(adim)
    animasyon.finished.connect(bitti)
    bilesen._salla = animasyon
    animasyon.start()
    return animasyon


def pencere_belir(pencere):
    """Üst düzey pencereyi saydamdan görünüre getirir (girişten panele geçiş)."""
    if not acik_mi(pencere):
        return None
    animasyon = QPropertyAnimation(pencere, b"windowOpacity", pencere)
    animasyon.setDuration(tema.SURE.orta)
    animasyon.setStartValue(0.0)
    animasyon.setEndValue(1.0)
    animasyon.setEasingCurve(QEasingCurve.OutCubic)
    animasyon.finished.connect(lambda: pencere.setWindowOpacity(1.0))
    pencere.setWindowOpacity(0.0)
    animasyon.start()
    return animasyon


def acilir_pencere_belir(pencere, kayma=8):
    """Açılır pencere (hızlı arama) birkaç piksel aşağıdan kayarak ve belirerek gelir."""
    if not acik_mi(pencere):
        return None
    hedef = pencere.pos()
    konum = QPropertyAnimation(pencere, b"pos", pencere)
    konum.setDuration(tema.SURE.kisa)
    konum.setStartValue(hedef + QPoint(0, kayma))
    konum.setEndValue(hedef)
    konum.setEasingCurve(QEasingCurve.OutCubic)
    saydam = pencere_belir(pencere)
    if saydam is not None:
        saydam.setDuration(tema.SURE.kisa)
    pencere.move(hedef + QPoint(0, kayma))
    konum.start()
    return konum


def hata_vurgula(alan):
    """Hatalı alanın çerçevesi tehlike renginde belirir, kısa süre kalır ve normale söner.
    Animasyon kapalıyken çerçeve kısa süre kırmızı kalıp normale döner (hata yine görünsün)."""
    eski = getattr(alan, "_hata_animasyonu", None)
    if eski is not None:
        eski.stop()
    stil = getattr(alan, "_ozgun_stil", None)
    if stil is None:
        stil = alan._ozgun_stil = alan.styleSheet()

    def boya(renk):
        alan.setStyleSheet(stil + f"\n{type(alan).__name__} {{ border-color: {renk.name().upper()}; }}")

    def bitti():
        alan.setStyleSheet(stil)
        alan._hata_animasyonu = None

    if not izinli():
        boya(QColor(tema.TEHLIKE))
        QTimer.singleShot(tema.SURE.parlama * 2, alan, bitti)     # alan bu arada silinirse çağrılmaz
        return None
    animasyon = QVariantAnimation(alan)
    animasyon.setDuration(tema.SURE.parlama * 2)
    animasyon.setStartValue(QColor(tema.TEHLIKE))
    animasyon.setKeyValueAt(0.5, QColor(tema.TEHLIKE))          # yarı süre kırmızı kalır
    animasyon.setEndValue(QColor(tema.KENAR_GIRDI))
    animasyon.valueChanged.connect(boya)
    animasyon.finished.connect(bitti)
    alan._hata_animasyonu = animasyon
    boya(QColor(tema.TEHLIKE))
    animasyon.start()
    return animasyon


def nabiz(bilesen, tekrar=2):
    """Bileşen dikkat çekmek için birkaç kez soluklaşıp geri gelir (sürekli değil); bitince efekt kalkar."""
    if not acik_mi(bilesen) or bilesen.graphicsEffect() is not None:
        return None
    efekt = QGraphicsOpacityEffect(bilesen)
    bilesen.setGraphicsEffect(efekt)
    grup = QSequentialAnimationGroup(efekt)
    for _ in range(tekrar):
        for bas, son in ((1.0, 0.3), (0.3, 1.0)):
            a = QPropertyAnimation(efekt, b"opacity")
            a.setDuration(tema.SURE.uzun)
            a.setStartValue(bas)
            a.setEndValue(son)
            a.setEasingCurve(QEasingCurve.InOutSine)
            grup.addAnimation(a)
    grup.finished.connect(lambda: bilesen.graphicsEffect() is efekt and bilesen.setGraphicsEffect(None))
    grup.start()
    return grup


def say(etiket, hedef, bicim=str, baslangic=0, sure=None):
    """Etiketteki sayı baslangic'tan (0) hedefe sayarak gelir; animasyon kapalıysa hemen yazılır."""
    eski = getattr(etiket, "_sayac", None)
    if eski is not None:
        eski.stop()
        etiket._sayac = None
    if (not acik_mi(etiket) or not isinstance(hedef, int) or hedef == baslangic
            or (baslangic == 0 and hedef <= 0)):
        etiket.setText(bicim(hedef))
        return None
    animasyon = QVariantAnimation(etiket)
    animasyon.setDuration(sure or tema.SURE.sayac)
    animasyon.setStartValue(baslangic)
    animasyon.setEndValue(hedef)
    animasyon.setEasingCurve(QEasingCurve.OutCubic)
    animasyon.valueChanged.connect(lambda d: etiket.setText(bicim(int(d))))
    def bitti():
        etiket.setText(bicim(hedef))
        etiket._sayac = None

    animasyon.finished.connect(bitti)
    etiket._sayac = animasyon
    etiket.setText(bicim(baslangic))
    animasyon.start()
    return animasyon


_SAYI = re.compile(r"\d+")


def sayi_yaz(etiket, metin):
    """Sonuç sayısı gibi etiketlerde sayı eski değerinden yenisine akarak değişir ("12 kitap bulundu" →
    "3 kitap bulundu"). Metnin kalıbı değişirse ("Toplam 8 kitap" → "2 kitap bulundu") hemen yazılır."""
    onceki = getattr(etiket, "_sayi_hedefi", None) or etiket.text()
    etiket._sayi_hedefi = metin
    yeni, eski = _SAYI.search(metin), _SAYI.search(onceki)
    if (yeni is None or eski is None
            or (metin[:yeni.start()], metin[yeni.end():]) != (onceki[:eski.start()], onceki[eski.end():])):
        say(etiket, None, lambda _: metin)                  # süren sayımı durdurup metni yazar
        return None
    on, son = metin[:yeni.start()], metin[yeni.end():]
    return say(etiket, int(yeni.group()), lambda n: f"{on}{n}{son}", baslangic=int(eski.group()),
               sure=tema.SURE.uzun)


def sirayla_belir(bilesenler, kayma=10, bitince=None):
    """Bileşenler sırayla (tema.SURE.adim arayla) birkaç piksel aşağıdan kayarak ve belirerek gelir
    (ana sayfa kartları, giriş formu). Kendi efekti olan bileşen atlanır. bitince(bileşen): her biri yerine
    oturunca (atlananlar için hemen) çağrılır, ör. kaldırılan gölge efekti geri kurulsun."""
    baslayan = []
    for i, bilesen in enumerate(bilesenler):
        if not acik_mi(bilesen) or bilesen.graphicsEffect() is not None:
            if bitince:
                bitince(bilesen)
            continue
        efekt = QGraphicsOpacityEffect(bilesen)
        efekt.setOpacity(0.0)                   # sırası gelene kadar görünmez
        bilesen.setGraphicsEffect(efekt)
        baslayan.append(bilesen)

        def baslat(b=bilesen, e=efekt):
            if b.graphicsEffect() is not e:
                return
            b.setGraphicsEffect(None)           # kayarak_belir kendi efektini kurar
            if kayarak_belir(b, 1, kayma, dikey=True, bitince=bitince and (lambda: bitince(b))) is None and bitince:
                bitince(b)
        QTimer.singleShot(i * tema.SURE.adim, bilesen, baslat)
    return baslayan


def genisleyerek_ekle(bilesen):
    """Yeni eklenen küçük öğe (filtre etiketi) sıfır genişlikten açılarak ve belirerek gelir; yanındakiler
    birden kaymaz. Animasyon kapalıysa hemen görünür."""
    if not izinli():
        return None
    hedef = bilesen.sizeHint().width()
    efekt = QGraphicsOpacityEffect(bilesen)
    efekt.setOpacity(0.0)
    bilesen.setGraphicsEffect(efekt)
    bilesen.setMaximumWidth(0)
    animasyon = QVariantAnimation(bilesen)
    animasyon.setDuration(tema.SURE.orta)
    animasyon.setStartValue(0.0)
    animasyon.setEndValue(1.0)
    animasyon.setEasingCurve(QEasingCurve.OutBack)       # hafifçe taşıp yerine oturur

    def adim(t):
        bilesen.setMaximumWidth(max(0, round(hedef * t)))
        efekt.setOpacity(max(0.0, min(1.0, t)))

    def bitti():
        bilesen.setMaximumWidth(SINIRSIZ)
        if bilesen.graphicsEffect() is efekt:
            bilesen.setGraphicsEffect(None)

    animasyon.valueChanged.connect(adim)
    animasyon.finished.connect(bitti)
    animasyon.start()
    return animasyon


def daralarak_sil(bilesen, bitince=None):
    """Kaldırılan küçük öğe daralıp solarak gider, sonra silinir. Animasyon kapalıysa hemen silinir.
    bitince: öğe yerleşimden çıktıktan sonra çağrılır (ör. kap boş kaldıysa gizlensin)."""
    def sil():
        duzen = bilesen.parentWidget().layout() if bilesen.parentWidget() else None
        if duzen is not None:
            duzen.removeWidget(bilesen)
        bilesen.hide()
        bilesen.deleteLater()
        if bitince:
            bitince()

    if not acik_mi(bilesen):
        sil()
        return None
    bilesen.setEnabled(False)                   # giderken bir daha tıklanmasın
    efekt = bilesen.graphicsEffect() or QGraphicsOpacityEffect(bilesen)
    bilesen.setGraphicsEffect(efekt)
    bas = bilesen.width()
    animasyon = QVariantAnimation(bilesen)
    animasyon.setDuration(tema.SURE.kisa)
    animasyon.setStartValue(1.0)
    animasyon.setEndValue(0.0)
    animasyon.setEasingCurve(QEasingCurve.InCubic)

    def adim(t):
        bilesen.setMaximumWidth(round(bas * t))
        if isinstance(efekt, QGraphicsOpacityEffect):
            efekt.setOpacity(t)

    animasyon.valueChanged.connect(adim)
    animasyon.finished.connect(sil)
    animasyon.start()
    return animasyon


class KayanVurgu(QObject):
    """Buton grubunda seçili olanın arkasındaki vurgu: seçim değişince yeni butonun altına kayarak gider.
    Butonlar yer / boyut değiştirince (menü daralırken) vurgu animasyonsuz izler. Vurgunun görünümü kabın stil
    sayfasında nesne adıyla verilir; seçili butonun kendi zemini saydam olmalıdır."""

    def __init__(self, kap, grup, ad):
        super().__init__(kap)
        self.kap = kap
        self.grup = grup
        self.cerceve = QFrame(kap, objectName=ad)
        self.cerceve.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.cerceve.lower()
        self.cerceve.hide()
        self.animasyon = QPropertyAnimation(self.cerceve, b"geometry", self)
        self.animasyon.setDuration(tema.SURE.orta)
        self.animasyon.setEasingCurve(QEasingCurve.OutCubic)
        grup.buttonToggled.connect(lambda buton, secili: secili and self.hedefle(True))
        kap.installEventFilter(self)
        for buton in grup.buttons():
            buton.installEventFilter(self)

    def hedef(self):
        buton = self.grup.checkedButton()
        if buton is None or not buton.isVisibleTo(self.kap):
            return None
        return QRect(buton.mapTo(self.kap, QPoint()), buton.size())

    def hedefle(self, animasyonlu=False):
        alan = self.hedef()
        if alan is None:
            self.cerceve.hide()
            return
        if animasyonlu and acik_mi(self.kap) and self.cerceve.isVisible() and self.cerceve.geometry() != alan:
            self.animasyon.stop()
            self.animasyon.setStartValue(self.cerceve.geometry())
            self.animasyon.setEndValue(alan)
            self.animasyon.start()
        else:
            self.animasyon.stop()
            self.cerceve.setGeometry(alan)
        self.cerceve.show()
        self.cerceve.lower()

    def eventFilter(self, nesne, olay):
        if olay.type() in (QEvent.Resize, QEvent.Move, QEvent.Show, QEvent.LayoutRequest):
            if self.animasyon.state() != QPropertyAnimation.Running:
                self.hedefle()
        return False


# --- Üstüne gelme ve odak: renkler bir anda değil kısa bir geçişle değişir ---

# Kendi özel görünümü olan butonlar (segment, etiket, menü araçları, zeminsiz Sil ...): QSS'teki gibi anında
OZEL_BUTONLAR = {"segment_ogesi", "filtre_etiketi", "kilavuz_konu", "daralt", "menu_ara", "oturum_kapat",
                 "pushButton_cikis"}


def _karisim(a, b, t):
    return QColor.fromRgbF(a.redF() + (b.redF() - a.redF()) * t, a.greenF() + (b.greenF() - a.greenF()) * t,
                           a.blueF() + (b.blueF() - a.blueF()) * t, a.alphaF() + (b.alphaF() - a.alphaF()) * t)


def uzerinde_renkleri(buton):
    """Butonun (normal, üstüne gelinmiş) renkleri {QSS özelliği: QColor}; QSS'teki :hover kurallarının aynısı.
    Özel görünümlü, devre dışı veya seçili butonlarda None (geçiş yapılmaz)."""
    if (not buton.isEnabled() or buton.styleSheet() or (buton.isCheckable() and buton.isChecked())
            or buton.objectName() in OZEL_BUTONLAR or buton.objectName() in tema.TEHLIKELI_BUTONLAR
            or buton.property("tehlikeli")):
        return None
    if buton.objectName() == "menu_ogesi":
        return ({"background-color": QColor(255, 255, 255, 0), "color": QColor(tema.MENU_OGE)},
                {"background-color": QColor(255, 255, 255, 20), "color": QColor(Qt.white)})
    if buton.property("rol") == "ikincil":
        return ({"background-color": QColor(tema.KART), "border-color": QColor(tema.KENAR_IKINCIL)},
                {"background-color": QColor(tema.YUZEY), "border-color": QColor(tema.SOLUK)})
    return ({"background-color": QColor(tema.VURGU)}, {"background-color": QColor(tema.VURGU_KOYU)})


def _qss_rengi(renk):
    return f"rgba({renk.red()}, {renk.green()}, {renk.blue()}, {renk.alphaF():.3f})"


class UzerindeGecisi(QObject):
    """Butonların üstüne gelince / çıkınca zemin rengi tema.SURE.kisa içinde değişir. Geçiş sürerken buton
    kendi stil sayfasıyla boyanır; bitince stil sayfası eski haline döner ve QSS'teki aynı renk devralır."""

    def gecis(self, buton):
        animasyon = buton.findChild(QVariantAnimation, "uzerinde_gecisi")
        if animasyon is None:
            animasyon = QVariantAnimation(buton, objectName="uzerinde_gecisi")
            animasyon.setDuration(tema.SURE.kisa)
            animasyon.setEasingCurve(QEasingCurve.OutCubic)
            animasyon.valueChanged.connect(lambda t: self._boya(buton, animasyon, t))
            animasyon.finished.connect(lambda: self.birak(buton))
        return animasyon

    def _boya(self, buton, animasyon, t):
        renkler = animasyon.property("renkler")
        if renkler is None:
            return
        normal, uzerinde = renkler
        kural = "; ".join(f"{oz}: {_qss_rengi(_karisim(normal[oz], uzerinde[oz], t))}" for oz in normal)
        buton.setStyleSheet(f"QPushButton {{ {kural}; }}")
        animasyon.setProperty("guc", t)

    def birak(self, buton):
        """Geçişi bitirir; buton yeniden yalnızca QSS ile boyanır."""
        animasyon = buton.findChild(QVariantAnimation, "uzerinde_gecisi")
        if animasyon is None or animasyon.property("renkler") is None:
            return
        animasyon.stop()
        animasyon.setProperty("renkler", None)
        buton.setStyleSheet("")

    def eventFilter(self, buton, olay):
        tur = olay.type()
        if tur in (QEvent.Enter, QEvent.Leave):
            self._git(buton, 1.0 if tur == QEvent.Enter else 0.0)
        elif tur in (QEvent.MouseButtonPress, QEvent.EnabledChange, QEvent.Hide):
            self.birak(buton)               # basılı / devre dışı rengini QSS versin
        return False

    def _git(self, buton, hedef):
        animasyon = self.gecis(buton)
        suruyor = animasyon.property("renkler") is not None
        renkler = animasyon.property("renkler") if suruyor else uzerinde_renkleri(buton)
        if renkler is None or not acik_mi(buton):
            self.birak(buton)
            return
        bas = animasyon.property("guc") if suruyor else 1.0 - hedef
        animasyon.stop()
        animasyon.setProperty("renkler", renkler)
        animasyon.setStartValue(float(bas))
        animasyon.setEndValue(hedef)
        self._boya(buton, animasyon, float(bas))
        animasyon.start()


class OdakIsigi(QWidget):
    """Odaklanan yazı alanının çevresinde vurgu renginde yumuşak bir ışık; odakla belirir, odak gidince söner.
    Alanın kardeşi olarak altına yerleşir (alan kendi zeminini üstüne çizer); alanla birlikte kayar."""
    PAY = 4

    def __init__(self, alan):
        super().__init__(alan.parentWidget())
        self.alan = alan
        self.guc = 0.0
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.animasyon = QVariantAnimation(self)
        self.animasyon.setDuration(tema.SURE.kisa)
        self.animasyon.setEasingCurve(QEasingCurve.OutCubic)
        self.animasyon.valueChanged.connect(self._ilerle)
        self.animasyon.finished.connect(lambda: self.guc <= 0 and self.hide())
        self.hide()

    def yerles(self):
        self.setGeometry(self.alan.geometry().adjusted(-self.PAY, -self.PAY, self.PAY, self.PAY))
        self.stackUnder(self.alan)

    def git(self, hedef):
        self.animasyon.stop()
        if hedef > 0 and self.alan.isVisible():
            self.yerles()
            self.show()
        if not acik_mi(self.alan) or not self.isVisible():
            self._ilerle(hedef)
            if hedef <= 0:
                self.hide()
            return
        self.animasyon.setStartValue(self.guc)
        self.animasyon.setEndValue(float(hedef))
        self.animasyon.start()

    def _ilerle(self, guc):
        self.guc = guc
        self.update()

    def paintEvent(self, olay):
        efekt = self.alan.graphicsEffect()       # alan belirirken ışık da onunla birlikte belirir
        guc = self.guc * (efekt.opacity() if isinstance(efekt, QGraphicsOpacityEffect) else 1.0)
        if guc <= 0:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        alan = QRectF(self.rect())
        for pay, saydamlik in ((0, 0.12), (2, 0.24)):     # dışta soluk, içte koyu: yumuşak kenar
            renk = QColor(tema.VURGU)
            renk.setAlphaF(saydamlik * guc)
            p.setBrush(renk)
            yaricap = tema.KOSE.kucuk + self.PAY - pay
            p.drawRoundedRect(alan.adjusted(pay, pay, -pay, -pay), yaricap, yaricap)
        p.end()


class _OdakIzleyici(QObject):
    def eventFilter(self, alan, olay):
        tur = olay.type()
        if tur in (QEvent.FocusIn, QEvent.FocusOut):
            hedef = alan.parentWidget() if _ic_alan_mi(alan) else alan
            isik = getattr(hedef, "_odak_isigi", None)
            if isik is None and tur == QEvent.FocusIn and izinli():
                isik = hedef._odak_isigi = OdakIsigi(hedef)
            if isik is not None:
                isik.git(1.0 if tur == QEvent.FocusIn else 0.0)
        elif tur in (QEvent.Move, QEvent.Resize) and getattr(alan, "_odak_isigi", None) is not None:
            if alan._odak_isigi.isVisible():
                alan._odak_isigi.yerles()
        elif tur == QEvent.Hide and getattr(alan, "_odak_isigi", None) is not None:
            alan._odak_isigi.git(0.0)
        return False


def _ic_alan_mi(alan):
    """Açılır liste ve sayı kutusunun içindeki yazı alanı: ışık dıştaki kutunun çevresinde yanar."""
    from PySide6.QtWidgets import QAbstractSpinBox, QComboBox
    return isinstance(alan.parentWidget(), (QComboBox, QAbstractSpinBox))


def etkilesimleri_kur(kok):
    """Kökteki butonlara yumuşak üstüne gelme, yazı alanlarına odak ışığı kurar (panel, giriş ekranı, onay).
    Sonradan eklenen bileşenler için yeniden çağrılabilir; aynı bileşene iki kez kurulmaz."""
    from PySide6.QtWidgets import QAbstractSpinBox, QComboBox, QLineEdit, QPlainTextEdit, QPushButton
    uzerinde = kok.findChild(UzerindeGecisi, "uzerinde_izleyici")
    if uzerinde is None:
        uzerinde = UzerindeGecisi(kok)
        uzerinde.setObjectName("uzerinde_izleyici")
    odak = kok.findChild(_OdakIzleyici, "odak_izleyici")
    if odak is None:
        odak = _OdakIzleyici(kok)
        odak.setObjectName("odak_izleyici")
    for buton in kok.findChildren(QPushButton):
        if not buton.property("yumusak"):
            buton.setProperty("yumusak", True)
            buton.installEventFilter(uzerinde)
    for tur in (QLineEdit, QPlainTextEdit, QComboBox, QAbstractSpinBox):
        for alan in kok.findChildren(tur):
            if not alan.property("odak_isikli"):
                alan.setProperty("odak_isikli", True)
                alan.installEventFilter(odak)
