## İstatistik > Grafikler alt sekmesi ##
# Grafikler veritabanından her yenilemede yeniden çizilir (eskiden sabit bir resim gösteriliyordu).
# Ek kütüphane gerektirmemek için Qt'nin kendi çizim araçları (QPainter) kullanılır.
# Grafik ilk görünüşte büyüyerek çizilir: çubuklar sırayla uzar, pasta dilimleri dönerek açılır. Sonraki veri
# değişikliklerinde sıfırdan çizilmez; çubuklar ve dilimler eski değerlerinden yenilerine akar.
# Üstüne gelinen dilim dışarı çıkar, çubuk koyulaşır; ipucunda değer ve yüzde yazar.

import math

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGridLayout, QToolTip, QWidget

from acodes import hareket, tema
from database.istatistik import rapor, yil_dagilimi

PASTA_DILIM = 7        # en büyük 7 tür, gerisi "Diğer"
CUBUK_SAYISI = 10
GECIKME = 0.06         # çubuklar arası başlama farkı (toplam sürenin oranı)
DISARI = 7             # üstüne gelinen pasta diliminin dışarı çıkma payı (piksel)


def renk(i):
    """Grafik serisi rengi (tema paletinden, sırayla döner)."""
    return QColor(tema.GRAFIK[i % len(tema.GRAFIK)])


class Grafik(QWidget):
    """Başlıklı, beyaz zeminli grafik kutusu. Alt sınıflar ciz() metodunu yazar."""

    def __init__(self, baslik, parent=None):
        super().__init__(parent)
        self.baslik = baslik
        self.veri = []          # [(etiket, değer), ...]
        self.setMinimumSize(300, 220)
        self.setMouseTracking(True)
        self.ilerleme = 1.0     # çizim animasyonu: 0 boş (veya eski veri), 1 tam
        self.canlandir = False  # veri değişti, görününce canlandırılsın
        self.onceki = None      # akış: {etiket: eski değer}; None ise ilk çizim (büyüyerek)
        self.cizildi = False    # en az bir kez tam çizildi (sonraki değişiklikler akarak gelir)
        self.uzerinde = None    # fare üstündeki dilim / çubuk
        self.vurgu = 0.0        # üstündeki öğenin öne çıkma gücü (0-1)
        self.parcalar = []      # son çizimde [(sıra, alan veya None)]: fare hangi öğenin üstünde
        self.animasyon = QVariantAnimation(self)
        self.animasyon.setDuration(tema.SURE.sayac)
        self.animasyon.setStartValue(0.0)
        self.animasyon.setEndValue(1.0)
        self.animasyon.setEasingCurve(QEasingCurve.OutCubic)
        self.animasyon.valueChanged.connect(self._ilerle)
        self.animasyon.finished.connect(self._bitti)
        self.vurgu_animasyonu = QVariantAnimation(self)
        self.vurgu_animasyonu.setDuration(tema.SURE.kisa)
        self.vurgu_animasyonu.setEasingCurve(QEasingCurve.OutCubic)
        self.vurgu_animasyonu.valueChanged.connect(self._vurgula)

    def veri_ver(self, veri):
        yeni = [(str(e) if str(e).strip() else "(belirtilmemiş)", int(d)) for e, d in veri if int(d) > 0]
        if yeni != self.veri:
            self.canlandir = True
            # Önceki çizim tamamlandıysa yeni değerler eskilerinden akar; yoksa grafik büyüyerek çizilir
            self.onceki = {e: self.deger_su_an(i) for i, (e, _) in enumerate(self.veri)} if self.cizildi else None
            self.uzerinde = None
        self.veri = yeni
        if self.isVisible():
            self._baslat()
        self.update()

    def _ilerle(self, deger):
        self.ilerleme = deger
        self.update()

    def _bitti(self):
        self.onceki = None
        self.cizildi = True

    def _baslat(self):
        if not self.canlandir:
            return
        self.canlandir = False
        if not hareket.acik_mi(self) or not self.veri:
            self.ilerleme = 1.0
            self._bitti()
            return
        self.ilerleme = 0.0
        self.animasyon.start()

    def showEvent(self, olay):
        super().showEvent(olay)
        self._baslat()

    def akiyor(self):
        return self.onceki is not None and self.animasyon.state() == QVariantAnimation.Running

    def deger_su_an(self, i):
        """i. öğenin çizilen değeri: akarken eski değerden yeniye ara değer (yeni öğe 0'dan başlar)."""
        etiket, deger = self.veri[i]
        if not self.akiyor():
            return deger
        eski = self.onceki.get(etiket, 0)
        return eski + (deger - eski) * self.ilerleme

    def oran(self, i):
        """i. çubuğun ilerlemesi: her çubuk bir öncekinden biraz sonra başlar, hepsi birlikte biter.
        Akarken (veri değişince) çubuklar boydan büyümez, değerleri değişir: oran 1'dir."""
        if self.onceki is not None:
            return 1.0
        n = len(self.veri)
        pay = GECIKME * max(0, n - 1)
        return max(0.0, min(1.0, (self.ilerleme * (1 + pay) - GECIKME * i)))

    def acilma(self):
        """Pasta dilimlerinin açılma oranı: ilk çizimde 0'dan 1'e, akarken hep 1."""
        return 1.0 if self.onceki is not None else self.ilerleme

    # --- Üstüne gelme

    def oge_bul(self, nokta):
        for i, alan in self.parcalar:
            if alan is not None and alan.contains(nokta):
                return i
        return None

    def ipucu(self, i):
        etiket, deger = self.veri[i]
        toplam = sum(d for _, d in self.veri) or 1
        return f"{etiket}: {deger}  (%{deger / toplam * 100:.1f})"

    def mouseMoveEvent(self, olay):
        i = self.oge_bul(olay.position())
        if i != self.uzerinde:
            self.uzerinde = i
            self.vurgu = 0.0
            self.vurgu_animasyonu.stop()
            if i is not None and hareket.acik_mi(self):
                self.vurgu_animasyonu.setStartValue(0.0)
                self.vurgu_animasyonu.setEndValue(1.0)
                self.vurgu_animasyonu.start()
            else:
                self.vurgu = 1.0
            self.update()
        if i is None:
            QToolTip.hideText()
        else:
            QToolTip.showText(olay.globalPosition().toPoint(), self.ipucu(i), self)
        super().mouseMoveEvent(olay)

    def leaveEvent(self, olay):
        self.uzerinde = None
        self.update()
        super().leaveEvent(olay)

    def _vurgula(self, guc):
        self.vurgu = guc
        self.update()

    def guc(self, i):
        """i. öğe fare üstündeyse öne çıkma gücü, değilse 0."""
        return self.vurgu if i == self.uzerinde else 0.0

    def paintEvent(self, olay):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        kutu = QRectF(self.rect()).adjusted(4, 4, -4, -4)
        p.setPen(QPen(QColor(tema.KENAR)))
        p.setBrush(QColor(tema.KART))
        p.drawRoundedRect(kutu, tema.KOSE.orta, tema.KOSE.orta)
        p.setPen(QColor(tema.METIN))
        p.setFont(tema.yazi_tipi(tema.YAZI.alt_baslik, kalin=True))
        p.drawText(kutu.adjusted(12, 8, -12, 0), Qt.AlignLeft | Qt.AlignTop, self.baslik)
        alan = kutu.adjusted(14, 38, -14, -12)
        p.setFont(tema.yazi_tipi(tema.YAZI.ince))
        self.parcalar = []
        if not self.veri:
            p.setPen(QColor(tema.SOLUK))
            p.drawText(alan, Qt.AlignCenter, "Gösterilecek veri yok")
        else:
            self.ciz(p, alan)
        p.end()


def koyulas(renk, guc):
    """Üstüne gelinen çubuk biraz koyulaşır (koyu temada açılır)."""
    return renk.lighter(round(100 + 18 * guc)) if tema.KOYU_MU else renk.darker(round(100 + 18 * guc))


class _Dilim:
    """Pasta diliminin fare için alanı: merkezden uzaklık ve açı aralığı."""

    def __init__(self, merkez, yaricap, bas, son):
        self.merkez, self.yaricap, self.bas, self.son = merkez, yaricap, bas, son

    def contains(self, nokta):
        dx, dy = nokta.x() - self.merkez.x(), self.merkez.y() - nokta.y()
        if dx * dx + dy * dy > self.yaricap * self.yaricap:
            return False
        aci = math.degrees(math.atan2(dy, dx)) % 360
        bas, son = sorted((self.bas, self.son))
        return any(bas <= a <= son for a in (aci, aci + 360, aci - 360))


class PastaGrafik(Grafik):
    def ciz(self, p, alan):
        degerler = [self.deger_su_an(i) for i in range(len(self.veri))]
        toplam = sum(degerler) or 1
        cap = min(alan.height(), alan.width() * 0.5) - 2 * DISARI
        daire = QRectF(alan.left() + DISARI, alan.top() + (alan.height() - cap) / 2, cap, cap)
        aci = 90.0
        for i, deger in enumerate(degerler):
            dilim = -deger / toplam * 360 * self.acilma()
            orta = math.radians(aci + dilim / 2)
            kay = DISARI * self.guc(i)
            yer = daire.translated(kay * math.cos(orta), -kay * math.sin(orta))
            p.setPen(QPen(QColor(tema.KART), 1.5))
            p.setBrush(renk(i))
            p.drawPie(yer, round(aci * 16), round(dilim * 16))
            self.parcalar.append((i, _Dilim(daire.center(), cap / 2, aci + dilim, aci)))
            aci += dilim
        # Açıklama: renk, etiket, adet ve yüzde (üstündeki dilimin satırı kalın)
        satir = min(22, alan.height() / max(1, len(self.veri)))
        x = daire.right() + 20 + DISARI
        y = alan.top() + (alan.height() - satir * len(self.veri)) / 2
        toplam_gercek = sum(d for _, d in self.veri)
        for i, (etiket, deger) in enumerate(self.veri):
            p.setPen(Qt.NoPen)
            p.setBrush(renk(i))
            p.drawRoundedRect(QRectF(x, y + satir * i + 4, 12, 12), 2, 2)
            p.setPen(QColor(tema.METIN))
            yazi = p.font()
            yazi.setBold(i == self.uzerinde)
            p.setFont(yazi)
            satir_alani = QRectF(x + 20, y + satir * i, alan.right() - x - 20, satir)
            p.drawText(satir_alani, Qt.AlignLeft | Qt.AlignVCenter,
                       f"{etiket}  {deger}  (%{deger / toplam_gercek * 100:.1f})")
            self.parcalar.append((i, QRectF(x, y + satir * i, alan.right() - x, satir)))   # açıklama satırı da
        yazi = p.font()
        yazi.setBold(False)
        p.setFont(yazi)


class YatayCubukGrafik(Grafik):
    def ciz(self, p, alan):
        degerler = [self.deger_su_an(i) for i in range(len(self.veri))]
        en_buyuk = max(degerler) or 1
        etiket_eni = min(alan.width() * 0.4, 210)
        satir = alan.height() / len(self.veri)
        cubuk_alani = alan.width() - etiket_eni - 40
        for i, (etiket, deger) in enumerate(self.veri):
            y = alan.top() + satir * i
            p.setPen(QColor(tema.METIN))
            metin = p.fontMetrics().elidedText(etiket, Qt.ElideRight, int(etiket_eni - 8))
            p.drawText(QRectF(alan.left(), y, etiket_eni - 8, satir), Qt.AlignRight | Qt.AlignVCenter, metin)
            en = max(2, cubuk_alani * degerler[i] / en_buyuk * self.oran(i))
            p.setPen(Qt.NoPen)
            p.setBrush(koyulas(renk(0), self.guc(i)))
            p.drawRoundedRect(QRectF(alan.left() + etiket_eni, y + satir * 0.18, en, satir * 0.64), 3, 3)
            p.setPen(QColor(tema.METIN))
            p.drawText(QRectF(alan.left() + etiket_eni + en + 6, y, 40, satir), Qt.AlignLeft | Qt.AlignVCenter,
                       str(round(degerler[i])))
            self.parcalar.append((i, QRectF(alan.left(), y, alan.width(), satir)))


class DikeyCubukGrafik(Grafik):
    def ciz(self, p, alan):
        degerler = [self.deger_su_an(i) for i in range(len(self.veri))]
        en_buyuk = max(degerler) or 1
        alt = alan.bottom() - 22          # etiketler için yer
        ust = alan.top() + 18             # değerler için yer
        sutun = alan.width() / len(self.veri)
        for i, (etiket, deger) in enumerate(self.veri):
            x = alan.left() + sutun * i
            boy = max(2, (alt - ust) * degerler[i] / en_buyuk * self.oran(i))
            p.setPen(Qt.NoPen)
            p.setBrush(koyulas(renk(2), self.guc(i)))
            p.drawRoundedRect(QRectF(x + sutun * 0.15, alt - boy, sutun * 0.7, boy), 3, 3)
            p.setPen(QColor(tema.METIN))
            p.drawText(QRectF(x, alt - boy - 18, sutun, 18), Qt.AlignCenter, str(round(degerler[i])))
            p.drawText(QRectF(x, alt + 2, sutun, 20), Qt.AlignCenter, etiket)
            self.parcalar.append((i, QRectF(x, ust - 18, sutun, alt - ust + 40)))


def tur_dagilimi():
    veri = list(rapor('Turu', 1000).items())
    if len(veri) > PASTA_DILIM + 1:
        veri = veri[:PASTA_DILIM] + [("Diğer", sum(d for _, d in veri[PASTA_DILIM:]))]
    return veri


class GrafikPaneli(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.turler = PastaGrafik("Türlere göre dağılım")
        self.yazarlar = YatayCubukGrafik(f"En çok kitabı olan {CUBUK_SAYISI} yazar")
        self.yayinevleri = YatayCubukGrafik(f"En çok kitabı olan {CUBUK_SAYISI} yayınevi")
        self.yillar = DikeyCubukGrafik("Basım yıllarına göre (on yıllık)")
        duzen = QGridLayout(self)
        duzen.setContentsMargins(0, 0, 0, 0)
        duzen.addWidget(self.turler, 0, 0)
        duzen.addWidget(self.yazarlar, 0, 1)
        duzen.addWidget(self.yillar, 1, 0)
        duzen.addWidget(self.yayinevleri, 1, 1)

    def yenile(self):
        self.turler.veri_ver(tur_dagilimi())
        for grafik, kolon in ((self.yazarlar, 'Yazari'), (self.yayinevleri, 'Yayinevi')):
            grafik.veri_ver(rapor(kolon, CUBUK_SAYISI, bos_dahil=False).items())
        self.yillar.veri_ver(yil_dagilimi())
