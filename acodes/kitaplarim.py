## Guest paneli > Kitaplarım sekmesi ##
# Üyenin elindeki kitaplar (teslim tarihi, kalan gün) ve daha önce aldığı kitaplar.
# Durum kolonunda kalan günün yanında teslim süresinin ne kadarının geçtiğini gösteren çubuk vardır: süre
# boldayken yeşil, teslime az kalınca turuncu, gecikince kırmızı; sayfa her açıldığında dolarak gelir.

from PySide6.QtCore import QEasingCurve, QRectF, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QFontMetrics, QPainter
from PySide6.QtWidgets import (QGroupBox, QHeaderView, QLabel, QStyledItemDelegate, QTableWidget, QVBoxLayout,
                             QWidget)

from acodes import hareket, tema
from acodes.tablo import _zemin_ciz, tablo_ayarla, tabloya_yaz
from database.odunc import (ODUNC_SURESI_GUN, gecikme_gunu, gun_sayisi, kalan_gun_yazi, tarih_yazi, teslim_tarihi,
                            uye_odunc)

DURUM_KOLONU = 4
GECEN_ORAN = Qt.UserRole + 1        # Durum hücresinde: teslim süresinin geçen kısmı (0-1, gecikince 1)
CUBUK_RENGI = Qt.UserRole + 2
YAKIN_GUN = 3                       # teslime bu kadar gün (veya daha az) kalınca çubuk turuncu


def teslim_rengi(verilis):
    """Çubuğun rengi: süre boldayken yeşil, teslime YAKIN_GUN gün kalınca turuncu, gecikince kırmızı."""
    if gecikme_gunu(verilis):
        return tema.TEHLIKE
    gecen = gun_sayisi(verilis) or 0
    return tema.UYARI if ODUNC_SURESI_GUN - gecen <= YAKIN_GUN else tema.BASARI


class TeslimCubugu(QStyledItemDelegate):
    """Durum hücresi: solda kalan gün yazısı, sağda teslim süresinin geçen kısmı kadar dolu çubuk.
    ilerleme(): 0-1 arası; çubuklar sayfa açılırken bu oranda dolarak çizilir."""
    CUBUK_EN = 96

    def __init__(self, ilerleme, parent=None):
        super().__init__(parent)
        self.ilerleme = ilerleme

    def paint(self, ressam, secenek, indeks):
        oran = indeks.data(GECEN_ORAN)
        if oran is None:
            return super().paint(ressam, secenek, indeks)
        _zemin_ciz(self, ressam, secenek, indeks)
        alan = secenek.rect.adjusted(8, 0, -10, 0)
        iz = QRectF(alan.right() - self.CUBUK_EN, alan.center().y() - 3, self.CUBUK_EN, 6)
        firca = indeks.data(Qt.ForegroundRole)
        ressam.save()
        ressam.setRenderHint(QPainter.Antialiasing)
        ressam.setPen(firca.color() if firca is not None else QColor(tema.METIN))
        ressam.setFont(secenek.font)
        metin_alani = alan.adjusted(0, 0, -self.CUBUK_EN - 12, 0)
        ressam.drawText(metin_alani, Qt.AlignLeft | Qt.AlignVCenter,
                        QFontMetrics(secenek.font).elidedText(indeks.data() or "", Qt.ElideRight, metin_alani.width()))
        ressam.setPen(Qt.NoPen)
        ressam.setBrush(QColor(tema.YUZEY_2))
        ressam.drawRoundedRect(iz, 3, 3)
        dolu = QRectF(iz)
        dolu.setWidth(iz.width() * max(0.0, min(1.0, oran)) * self.ilerleme())
        if dolu.width() > 0:
            dolu.setWidth(max(6.0, dolu.width()))         # yuvarlak uçlar ezilmesin
            ressam.setBrush(QColor(indeks.data(CUBUK_RENGI) or tema.BASARI))
            ressam.drawRoundedRect(dolu, 3, 3)
        ressam.restore()

    def sizeHint(self, secenek, indeks):
        boyut = super().sizeHint(secenek, indeks)
        if indeks.data(GECEN_ORAN) is None:
            return boyut
        en = QFontMetrics(secenek.font).horizontalAdvance(indeks.data() or "") + self.CUBUK_EN + 40
        return QSize(max(boyut.width(), en), boyut.height())


def tablo_olustur(basliklar, bos_metin):
    tablo = QTableWidget(0, len(basliklar))
    tablo.setHorizontalHeaderLabels(basliklar)
    baslik = tablo.horizontalHeader()
    baslik.setSectionResizeMode(QHeaderView.ResizeToContents)
    baslik.setSectionResizeMode(0, QHeaderView.Stretch)
    tablo_ayarla(tablo, bos_metin=bos_metin)
    return tablo


class Kitaplarim(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.kullanici = None
        self.setObjectName("tab_kitaplarim")
        self.setAttribute(Qt.WA_StyledBackground, True)   # panelin yarı saydam sayfa zemini çizilsin
        self.setStyleSheet(f"QGroupBox {{ font-weight: {tema.YARI_KALIN}; }}")
        self.ozet = QLabel()
        self.ozet.setStyleSheet(f'font-size: {tema.YAZI.alt_baslik}px; font-weight: {tema.YARI_KALIN};')
        self.elimdeki = tablo_olustur(["Kitap", "Yazar", "Aldığım Tarih", "Teslim Tarihi", "Durum"],
                                      "Şu an elinizde ödünç kitap yok.")
        self.ilerleme = 1.0             # çubukların dolma oranı (sayfa açılırken 0'dan 1'e)
        self.dolma = QVariantAnimation(self)
        self.dolma.setDuration(tema.SURE.sayac)
        self.dolma.setStartValue(0.0)
        self.dolma.setEndValue(1.0)
        self.dolma.setEasingCurve(QEasingCurve.OutCubic)
        self.dolma.valueChanged.connect(self._doldur)
        self.elimdeki.setItemDelegateForColumn(DURUM_KOLONU, TeslimCubugu(lambda: self.ilerleme, self.elimdeki))
        self.gecmis = tablo_olustur(["Kitap", "Yazar", "Aldığım Tarih", "İade Tarihi", "Gün"],
                                    "Daha önce aldığınız kitap yok.")

        kutu1 = QGroupBox("Elimdeki kitaplar")
        QVBoxLayout(kutu1).addWidget(self.elimdeki)
        kutu2 = QGroupBox("Daha önce aldığım kitaplar")
        QVBoxLayout(kutu2).addWidget(self.gecmis)
        duzen = QVBoxLayout(self)
        duzen.addWidget(QLabel("Kitaplarım", objectName="sayfa_baslik"))
        duzen.addWidget(self.ozet)
        duzen.addWidget(kutu1, 1)
        duzen.addWidget(kutu2, 1)

    def yukle(self, kullanici=None):
        """Kullanıcının ödünçlerini listeler; gecikmiş kitap sayısını döndürür."""
        if kullanici is not None:
            self.kullanici = kullanici
        elimdeki, eski, gecikenler, cubuklar = [], [], set(), []
        for kitap, yazar, verilis, durum, iade in uye_odunc(self.kullanici):
            if durum == "out":
                if gecikme_gunu(verilis):
                    gecikenler.add(len(elimdeki))
                elimdeki.append([kitap, yazar, tarih_yazi(verilis), tarih_yazi(teslim_tarihi(verilis)),
                                 kalan_gun_yazi(verilis)])
                cubuklar.append((verilis, gun_sayisi(verilis) or 0))
            else:
                gun = gun_sayisi(verilis, iade)
                eski.append([kitap, yazar, tarih_yazi(verilis), tarih_yazi(iade), "" if gun is None else gun])
        tabloya_yaz(self.elimdeki, elimdeki, vurgulu=gecikenler)
        self._cubuklari_yaz(cubuklar)
        tabloya_yaz(self.gecmis, eski)
        if not elimdeki:
            metin = "Şu an sizde ödünç kitap yok."
        else:
            metin = f"Şu an sizde {len(elimdeki)} kitap var."
            if gecikenler:
                metin += f" {len(gecikenler)} tanesinin teslim süresi geçti, lütfen iade edin."
        self.ozet.setText(metin)
        self.ozet.setStyleSheet(f'font-size: {tema.YAZI.alt_baslik}px; font-weight: {tema.YARI_KALIN};'
                                f' color: {tema.TEHLIKE if gecikenler else tema.METIN};')
        if self.isVisible():
            self.canlandir()
        return len(gecikenler)

    def _cubuklari_yaz(self, cubuklar):
        # Satırlar sıralamayla yer değiştirebilir: bilgi hücrenin kendisinde taşınır
        for r, (verilis, gecen) in enumerate(cubuklar):
            hucre = self.elimdeki.item(r, DURUM_KOLONU)
            hucre.setData(GECEN_ORAN, min(1.0, gecen / ODUNC_SURESI_GUN))
            hucre.setData(CUBUK_RENGI, teslim_rengi(verilis))
            hucre.setToolTip(f"{ODUNC_SURESI_GUN} günlük sürenin {min(gecen, ODUNC_SURESI_GUN)} günü geçti")

    def canlandir(self):
        """Çubuklar boştan bugünkü hallerine dolar; animasyon kapalıysa hemen dolu çizilir."""
        self.dolma.stop()
        if hareket.acik_mi(self.elimdeki) and self.elimdeki.rowCount():
            self._doldur(0.0)           # ilk kareye kadar dolu görünüp sonra boşalmasın
            self.dolma.start()
        else:
            self._doldur(1.0)

    def _doldur(self, deger):
        self.ilerleme = deger
        self.elimdeki.viewport().update()

    def showEvent(self, olay):
        super().showEvent(olay)
        self.canlandir()
