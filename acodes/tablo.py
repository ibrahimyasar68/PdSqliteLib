## Tablo yardımcıları: doldurma, sıralama ve satır vurgulama ##

import re

from PySide6.QtCore import QEvent, QObject, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHeaderView, QLabel, QPushButton, QStyle,
                             QStyledItemDelegate, QStyleOptionViewItem, QTableWidgetItem, QToolTip, QVBoxLayout, QWidget)

from acodes import hareket, tema
from database.kitaplar import kitap_durumlari
from database.metin import tr_sirala

SATIR_BOY = 38          # tablo satır yüksekliği (piksel)
_TARIH = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
_SAYI = re.compile(r"-?\d+")


def siralama_anahtari(deger):
    """Sayılar sayı olarak, gg.aa.yyyy tarih olarak, metinler Türk alfabesine göre sıralanır; boşlar en sonda."""
    metin = str(deger).strip()
    if not metin:
        return (3,)
    if _SAYI.fullmatch(metin):
        return (0, int(metin))
    tarih = _TARIH.fullmatch(metin)
    if tarih:
        gun, ay, yil = tarih.groups()
        return (1, (int(yil), int(ay), int(gun)))
    return (2, tr_sirala(metin))


class SiraliHucre(QTableWidgetItem):
    def __init__(self, deger):
        super().__init__("" if deger is None else str(deger))
        self.anahtar = siralama_anahtari(self.text())
        if self.anahtar[0] == 0:          # sayılar sağa yaslı
            self.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def __lt__(self, diger):
        if isinstance(diger, SiraliHucre):
            return self.anahtar < diger.anahtar
        return super().__lt__(diger)


class BosDurum(QObject):
    """Tabloda gösterilecek bir şey yokken ortasında simge, yönlendirici bir mesaj ve (varsa) bir eylem butonu.
    eylem: (buton yazısı, işlev), ör. ("Aramayı Temizle", arama.clear)."""

    def __init__(self, tablo, metin, simge="kitap", eylem=None):
        super().__init__(tablo)
        from acodes import ikonlar
        self.tablo = tablo
        self.kap = QWidget(tablo.viewport())
        self.kap.setObjectName("bos_durum")
        self.kap.setStyleSheet("#bos_durum { background: transparent; }")
        dikey = QVBoxLayout(self.kap)
        dikey.setSpacing(10)
        dikey.addStretch()
        self.simge = QLabel()
        self.simge.setPixmap(ikonlar.ikon(simge, tema.BOS_METIN).pixmap(44, 44))
        self.simge.setAlignment(Qt.AlignCenter)
        self.simge.setStyleSheet("background: transparent;")
        self.etiket = QLabel(metin)
        self.etiket.setAlignment(Qt.AlignCenter)
        self.etiket.setWordWrap(True)
        self.etiket.setStyleSheet(f"color: {tema.BOS_METIN}; font-size: {tema.YAZI.alt_baslik}px; background: transparent;")
        dikey.addWidget(self.simge)
        dikey.addWidget(self.etiket)
        self.buton = None
        if eylem:
            self.buton = QPushButton(eylem[0])
            self.buton.setProperty("rol", "ikincil")
            self.buton.setCursor(Qt.PointingHandCursor)
            self.buton.setMinimumHeight(36)
            self.buton.clicked.connect(eylem[1])
            dikey.addWidget(self.buton, 0, Qt.AlignHCenter)
        dikey.addStretch()
        self.bekliyor = False
        model = tablo.model()
        for sinyal in (model.rowsInserted, model.rowsRemoved, model.modelReset, model.layoutChanged, model.dataChanged):
            sinyal.connect(self.guncelle_sonra)
        tablo.viewport().installEventFilter(self)
        self.guncelle()

    def guncelle_sonra(self, *_):
        # Tablo doldurulurken her hücre için değil, doldurma bitince bir kez kontrol edilir
        if not self.bekliyor:
            self.bekliyor = True
            QTimer.singleShot(0, self, self.guncelle)      # tablo silinirse çağrılmaz (bağlam: self)

    def bos_mu(self):
        for r in range(self.tablo.rowCount()):
            for c in range(self.tablo.columnCount()):
                hucre = self.tablo.item(r, c)
                if hucre is not None and hucre.text():
                    return False
        return True

    def guncelle(self):
        self.bekliyor = False
        bos = self.bos_mu()
        yeni_bos = bos and self.kap.isHidden()
        self.kap.setGeometry(self.tablo.viewport().rect().adjusted(20, 20, -20, -20))
        for parca in (self.kap, self.etiket):
            parca.setVisible(bos)
        if yeni_bos:            # boş durum birden çıkmaz: hafifçe aşağıdan kayarak belirir
            hareket.kayarak_belir(self.kap, 1, kayma=6, dikey=True, sure=tema.SURE.orta)

    def eventFilter(self, nesne, olay):
        if olay.type() == QEvent.Resize:
            self.kap.setGeometry(self.tablo.viewport().rect().adjusted(20, 20, -20, -20))
        return False


def _zemin_ciz(temsilci, ressam, secenek, indeks):
    """Hücrenin zeminini (seçili, üstüne gelinen, sıra sıra renkli satır) yazısız çizer."""
    zemin = QStyleOptionViewItem(secenek)
    temsilci.initStyleOption(zemin, indeks)
    zemin.text = ""
    bilesen = zemin.widget
    (bilesen.style() if bilesen else QApplication.style()).drawControl(QStyle.CE_ItemViewItem, zemin, ressam, bilesen)


def _rozet_yazisi(secenek):
    yazi = QFont(secenek.font)
    yazi.setPixelSize(tema.YAZI.ince)
    yazi.setBold(True)
    return yazi


class DurumRozeti(QStyledItemDelegate):
    """Durum kolonu ("Ödünçte", "1/2 kopya rafta"): yazı kendi renginin açık tonundaki yuvarlak rozette.
    Olağan durum ("Rafta") her satırda rozet olup dikkati dağıtmasın diye yalnızca küçük bir nokta olarak çizilir;
    hücrenin metni (arama, sıralama, dışa aktarma için) değişmez."""
    SESSIZ = "Rafta"

    def paint(self, ressam, secenek, indeks):
        metin = indeks.data() or ""
        firca = indeks.data(Qt.ForegroundRole)
        if not metin or firca is None:
            return super().paint(ressam, secenek, indeks)
        _zemin_ciz(self, ressam, secenek, indeks)
        renk = QColor(firca.color())
        if metin == self.SESSIZ:
            alan = secenek.rect
            ressam.save()
            ressam.setRenderHint(QPainter.Antialiasing)
            ressam.setPen(Qt.NoPen)
            ressam.setBrush(renk)
            ressam.drawEllipse(QRectF(alan.x() + 10, alan.center().y() - 3.5 + 0.5, 7, 7))
            ressam.restore()
            return
        yazi = _rozet_yazisi(secenek)
        olcu = QFontMetrics(yazi)
        alan = secenek.rect
        boy = olcu.height() + 6
        en = min(olcu.horizontalAdvance(metin) + 20, alan.width() - 10)
        kutu = QRectF(alan.x() + 6, alan.center().y() - boy / 2 + 0.5, en, boy)
        zemin = QColor(renk)
        zemin.setAlphaF(0.24 if tema.KOYU_MU else 0.13)
        ressam.save()
        ressam.setRenderHint(QPainter.Antialiasing)
        ressam.setPen(Qt.NoPen)
        ressam.setBrush(zemin)
        ressam.drawRoundedRect(kutu, boy / 2, boy / 2)
        ressam.setPen(renk)
        ressam.setFont(yazi)
        ressam.drawText(kutu, Qt.AlignCenter, olcu.elidedText(metin, Qt.ElideRight, int(kutu.width()) - 12))
        ressam.restore()

    def helpEvent(self, olay, gorunum, secenek, indeks):
        if olay.type() == QEvent.ToolTip and indeks.data() == self.SESSIZ:
            QToolTip.showText(olay.globalPos(), self.SESSIZ, gorunum)     # nokta yazısız çizildiği için adı ipucunda
            return True
        return super().helpEvent(olay, gorunum, secenek, indeks)

    def sizeHint(self, secenek, indeks):
        boyut = super().sizeHint(secenek, indeks)
        en = QFontMetrics(_rozet_yazisi(secenek)).horizontalAdvance(indeks.data() or "") + 34
        return QSize(max(boyut.width(), en), boyut.height())


class OranCubugu(QStyledItemDelegate):
    """Sayı hücresinde değerin kolondaki en büyük değere oranı kadar yatay çubuk; sayı çubuğun sağında.
    İstatistik çizelgelerinde dağılım grafik sekmesine geçmeden görünür."""
    SAYI_EN = 46

    def paint(self, ressam, secenek, indeks):
        metin = indeks.data() or ""
        if not str(metin).isdigit():
            return super().paint(ressam, secenek, indeks)
        _zemin_ciz(self, ressam, secenek, indeks)
        model = indeks.model()
        degerler = [model.index(r, indeks.column()).data() for r in range(model.rowCount())]
        en_buyuk = max([int(d) for d in degerler if str(d).isdigit()] + [1])
        alan = secenek.rect.adjusted(8, 0, -8, 0)
        iz = QRectF(alan.x(), alan.center().y() - 4, max(0, alan.width() - self.SAYI_EN), 8)
        ressam.save()
        ressam.setRenderHint(QPainter.Antialiasing)
        ressam.setPen(Qt.NoPen)
        ressam.setBrush(QColor(tema.YUZEY_2))
        ressam.drawRoundedRect(iz, 4, 4)
        dolu = QRectF(iz)
        dolu.setWidth(max(8.0, iz.width() * int(metin) / en_buyuk))
        ressam.setBrush(QColor(tema.VURGU))
        ressam.drawRoundedRect(dolu, 4, 4)
        ressam.setPen(QColor(tema.METIN))
        ressam.setFont(secenek.font)
        ressam.drawText(alan, Qt.AlignRight | Qt.AlignVCenter, str(metin))
        ressam.restore()


def tablo_ayarla(tablo, siralama=True, bos_metin=None, sira_no=True, bos_simge="kitap", bos_eylem=None):
    """Hücreler düzenlenemez, tıklanınca satır seçilir, başlığa tıklanınca sıralanır.
    İlk açılışta veri geldiği sırada gösterilir (sıralama göstergesi yok).
    Satırlar ince çizgiyle ayrılır; bos_metin verilirse boş tabloda gösterilir.
    sira_no: solda 1'den başlayan sıra numarası (kayıt numarasından bağımsız; sıralama değişince de
    ekrandaki sıraya göre numaralanır, son numara listedeki kayıt sayısını gösterir)."""
    tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
    tablo.setAlternatingRowColors(False)      # satırlar ince çizgiyle ayrılır (sıra sıra renk yok)
    tablo.setShowGrid(False)
    tablo.setMouseTracking(True)
    tablo.setWordWrap(False)              # uzun metin satır yüksekliğini bozmadan "..." ile kısalır
    tablo.verticalHeader().setVisible(sira_no)
    tablo.verticalHeader().setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)
    tablo.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
    tablo.verticalHeader().setHighlightSections(True)    # seçili satırın sıra numarasında vurgu çizgisi
    tablo.verticalHeader().setDefaultSectionSize(SATIR_BOY)
    tablo.horizontalHeader().setStretchLastSection(True)
    tablo.horizontalHeader().setHighlightSections(False)
    # Başlık, kolonun hücreleriyle aynı hizada: metinler solda (sayı kolonlarını tabloya_yaz sağa alır)
    tablo.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    if bos_metin:
        tablo.bos_durum = BosDurum(tablo, bos_metin, bos_simge, bos_eylem)
    if siralama:
        tablo.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        tablo.setSortingEnabled(True)


def tablo_basliklari(tablo, kolonlar):
    for i,(genislik,baslik) in enumerate(kolonlar):
        tablo.setColumnWidth(i,genislik)
        tablo.setHorizontalHeaderItem(i,QTableWidgetItem(baslik))


def tabloya_yaz(tablo, satirlar, vurgulu=(), veri=None, renkler=None):
    """satirlar: yazılacak değerler. vurgulu: kırmızı gösterilecek satırların sırası.
    veri: her satır için ilk hücrede saklanacak ek bilgi (ör. id'ler), sıralamada satırla birlikte taşınır.
    renkler: {(satır, kolon): yazı rengi} (ör. Durum kolonu)."""
    siralama=tablo.isSortingEnabled()
    tablo.setSortingEnabled(False)   # doldururken satırlar yer değiştirmesin
    # "İçeriğe göre genişlik" kolonları her hücrede baştan ölçülür (737 kitapta ~18 sn);
    # doldururken sabitlenir, bitince bir kez ölçülür
    baslik=tablo.horizontalHeader()
    kipler=[baslik.sectionResizeMode(c) for c in range(tablo.columnCount())]
    for c,kip in enumerate(kipler):
        if kip==QHeaderView.ResizeToContents:
            baslik.setSectionResizeMode(c,QHeaderView.Interactive)
    tablo.setRowCount(len(satirlar))
    for r,satir in enumerate(satirlar):
        for c,deger in enumerate(satir):
            hucre=SiraliHucre(deger)
            if r in vurgulu:
                hucre.setBackground(QColor(tema.GECIKME_ARKA))     # ör. teslim süresi geçmiş ödünçler
                hucre.setForeground(QColor(tema.GECIKME_YAZI))
            if renkler and (r,c) in renkler:
                hucre.setForeground(QColor(renkler[r,c]))
            if c==0 and veri is not None:
                hucre.setData(Qt.UserRole, veri[r])
            tablo.setItem(r,c,hucre)
    for c,kip in enumerate(kipler):
        if kip==QHeaderView.ResizeToContents:
            baslik.setSectionResizeMode(c,kip)
    basliklari_hizala(tablo,satirlar)
    tablo.setSortingEnabled(siralama)
    # Yeni içerikle kolonlar çizimden önce yerleşsin (ertelenince liste bir kare eski genişliklerle görünüyordu)
    if hasattr(tablo,"kolon_secici"):
        tablo.kolon_secici.denetle()
    elif hasattr(tablo,"orantili"):
        tablo.orantili.dagit()


def basliklari_hizala(tablo, satirlar):
    """Boş olmayan değerlerinin çoğu (%80) sayı olan kolonların başlığı, sayılar gibi sağa yaslanır; diğerleri solda.
    (Basım yılında "1985-1990" gibi tek tük metinler başlığı sola kaydırmasın.)"""
    for c in range(tablo.columnCount()):
        degerler=[str(s[c]).strip() for s in satirlar if c<len(s) and s[c] is not None and str(s[c]).strip()]
        sayi=bool(degerler) and sum(1 for d in degerler if _SAYI.fullmatch(d))>=0.8*len(degerler)
        hucre=tablo.horizontalHeaderItem(c)
        if hucre is None:
            continue
        hucre.setTextAlignment((Qt.AlignRight if sayi else Qt.AlignLeft) | Qt.AlignVCenter)


def durum_ekle(satirlar):
    """Kitap satırlarının (ilk değer kitap numarası) sonuna "Durum" kolonunu ekler: Rafta / Ödünçte / 1/2 kopya rafta.
    tabloya_yaz için (satırlar, renkler) döndürür."""
    durumlar = kitap_durumlari([s[0] for s in satirlar])
    renk = {"rafta": tema.BASARI, "kismen": tema.UYARI, "yok": tema.TEHLIKE}
    yeni = [list(s) + [yazi] for s, (yazi, _) in zip(satirlar, durumlar)]
    return yeni, {(r, len(s) - 1): renk[tur] for r, (s, (_, tur)) in enumerate(zip(yeni, durumlar))}


class OrantiliKolonlar(QObject):
    """Uzun metinli kolonlar (ör. Adı 3, Yazarı 2, Yayınevi 2) kalan genişliği ağırlıklarına göre paylaşır;
    diğer kolonlar içeriğe göre daralır. Qt'nin "Stretch" kipi her kolona eşit pay verdiği için kitap adı
    tür kolonu kadar dar kalıyordu."""
    EN_AZ = 70

    def __init__(self, tablo, agirliklar):
        super().__init__(tablo)
        self.tablo, self.agirliklar = tablo, agirliklar
        self.bekliyor = False
        baslik = tablo.horizontalHeader()
        baslik.setStretchLastSection(False)
        for kolon in range(tablo.columnCount()):
            baslik.setSectionResizeMode(kolon, QHeaderView.Fixed if kolon in agirliklar else QHeaderView.ResizeToContents)
        model = tablo.model()
        for sinyal in (model.rowsInserted, model.modelReset, model.layoutChanged):
            sinyal.connect(self.dagit_sonra)
        baslik.sectionResized.connect(self._kolon_boyutlandi)
        tablo.viewport().installEventFilter(self)

    def _kolon_boyutlandi(self, kolon, eski, yeni):
        if kolon not in self.agirliklar:      # içeriğe göre kolon değişti (ör. liste doldu): pay yeniden hesaplanır
            self.dagit_sonra()

    def dagit_sonra(self, *_):
        if not self.bekliyor:
            self.bekliyor = True
            QTimer.singleShot(0, self, self.dagit)

    def dagit(self):
        self.bekliyor = False
        if getattr(self, "dagitiyor", False):     # genişlik değişimi kaydırma çubuğunu açıp kapatırsa iç içe çağrılır
            return
        self.dagitiyor = True
        try:
            self._dagit()
        finally:
            self.dagitiyor = False

    def _dagit(self):
        gorunen = [c for c in range(self.tablo.columnCount()) if not self.tablo.isColumnHidden(c)]
        oranli = [c for c in gorunen if c in self.agirliklar]
        if not oranli:
            return
        diger = sum(self.tablo.columnWidth(c) for c in gorunen if c not in self.agirliklar)
        kalan = self.tablo.viewport().width() - diger
        toplam = sum(self.agirliklar[c] for c in oranli)
        for i, c in enumerate(oranli):
            en = max(self.EN_AZ, int(kalan * self.agirliklar[c] / toplam))
            if i == len(oranli) - 1 and kalan > self.EN_AZ * len(oranli):   # yuvarlama artığı son kolona
                en = max(self.EN_AZ, kalan - sum(self.tablo.columnWidth(k) for k in oranli[:-1]))
            self.tablo.setColumnWidth(c, en)

    def eventFilter(self, nesne, olay):
        # Ertelenirse bir kare eski genişliklerle çiziliyor (yatay kaydırma çubuğu bir an görünüp kayboluyordu)
        if olay.type() in (QEvent.Resize, QEvent.Show):
            self.dagit()
        return False


def durum_rozeti_kur(tablo, kolon=None):
    """Durum kolonunu (varsayılan: son kolon) renkli rozet olarak çizer."""
    tablo.setItemDelegateForColumn(tablo.columnCount() - 1 if kolon is None else kolon, DurumRozeti(tablo))


def satir_verisi(tablo, satir):
    """tabloya_yaz(veri=...) ile saklanan bilgi; boş satırda None."""
    hucre=tablo.item(satir,0)
    return hucre.data(Qt.UserRole) if hucre else None


class KolonSecici(QObject):
    """Kitap listelerinde gösterilecek kolonların seçimi (seçim hatırlanır).
    "Kolonlar" butonu ve kolon başlığına sağ tık aynı seçim listesini açar. Liste pencereye sığmazsa önce
    tamamen boş kolonlar, sonra otomatik (öncelik sırasıyla) kolonlar kendiliğinden gizlenir; pencere büyüyünce
    geri gelir (bu gizleme kaydedilmez). Yine de sığmazsa tablonun üstünde hangi kolonları gizlemek istediği
    sorulur ("Bir daha sorma" ile kapatılabilir)."""
    MAKUL_EN = 160          # kısa kolonlarda beklenen en fazla genişlik (uzun değerler "..." ile kısalabilir)
    PAY_EN = 80             # oranlı (uzun metinli) kolonlarda ağırlık başına beklenen genişlik (Adı 3 → 240 px)
    GERI_PAY = 24           # gizlenen kolon ancak bu kadar boş yer de kalıyorsa geri gelir (sınırda gidip gelmesin)

    def __init__(self, tablo, anahtar, zorunlu=(1,), varsayilan_gizli=(), otomatik=(), parent=None):
        """zorunlu: gizlenemeyen kolonlar (kitap adı). varsayilan_gizli: kullanıcı henüz seçim yapmadıysa gizli
        kolonlar (ör. sıra numarasıyla aynı işi gören Kayıt No). otomatik: liste sığmazsa kendiliğinden
        gizlenecek kolonlar, önce gizlenecek olan başta."""
        super().__init__(parent or tablo)
        from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
        from acodes import tercihler
        self.tablo, self.anahtar, self.zorunlu = tablo, anahtar, set(zorunlu)
        self.otomatik = [c for c in otomatik if c not in self.zorunlu]
        self.oto_gizli = set()        # sığmadığı için kendiliğinden gizlenenler (kaydedilmez)
        self.baslik_olcu = {}         # kolon başlıklarının görünürken ölçülen genişliği (gizliyken Qt 0 verir)
        self.istenen = set()          # kullanıcının bu oturumda açıkça gösterdiği kolonlar (kendiliğinden gizlenmez)
        self.denetleniyor = False
        tablo.kolon_secici = self     # tabloya_yaz doldurduktan sonra çizimden önce denetletir
        self.tercihler = tercihler
        self.buton = QPushButton("Kolonlar")
        self.buton.setProperty("rol", "ikincil")
        self.buton.setToolTip("Listede gösterilecek kolonları seçin")
        self.buton.clicked.connect(lambda: self.menu().exec(self.buton.mapToGlobal(self.buton.rect().bottomLeft())))
        baslik = tablo.horizontalHeader()
        baslik.setContextMenuPolicy(Qt.CustomContextMenu)
        baslik.customContextMenuRequested.connect(lambda konum: self.menu().exec(baslik.mapToGlobal(konum)))

        self.soru = QFrame(objectName="kolon_sorusu")
        self.soru.setStyleSheet(f"#kolon_sorusu {{ background-color: {tema.UYARI_ARKA}; border: 1px solid {tema.UYARI_KENAR};"
                                f" border-radius: {tema.KOSE.orta}px; }} #kolon_sorusu QLabel {{ color: {tema.UYARI_METIN}; }}")
        satir = QHBoxLayout(self.soru)
        satir.setContentsMargins(12, 6, 8, 6)
        satir.addWidget(QLabel("Liste pencereye sığmıyor. Hangi kolonların gizleneceğini seçmek ister misiniz?"), 1)
        self.btn_sec = QPushButton("Kolonları Seç")
        self.btn_sec.clicked.connect(lambda: self.menu().exec(self.btn_sec.mapToGlobal(self.btn_sec.rect().bottomLeft())))
        self.btn_sorma = QPushButton("Bir daha sorma")
        self.btn_sorma.setProperty("rol", "ikincil")
        self.btn_sorma.clicked.connect(self.sorma)
        satir.addWidget(self.btn_sec)
        satir.addWidget(self.btn_sorma)
        self.soru.hide()

        kayitli = tercihler.oku(f"kolonlar/{anahtar}") is not None
        for kolon in tercihler.sayi_listesi(f"kolonlar/{anahtar}") if kayitli else varsayilan_gizli:
            if kolon not in self.zorunlu and kolon < tablo.columnCount():
                tablo.setColumnHidden(kolon, True)
        self.bekliyor = False
        tablo.viewport().installEventFilter(self)
        model = tablo.model()
        for sinyal in (model.rowsInserted, model.modelReset, model.layoutChanged):
            sinyal.connect(self.denetle_sonra)

    def menu(self):
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self.tablo)
        for c in range(self.tablo.columnCount()):
            baslik = self.tablo.horizontalHeaderItem(c)
            ad = baslik.text() if baslik else str(c + 1)
            eylem = menu.addAction(ad + (" (yer yok)" if c in self.oto_gizli else ""))
            eylem.setCheckable(True)
            eylem.setChecked(not self.tablo.isColumnHidden(c))
            eylem.setEnabled(c not in self.zorunlu)
            eylem.toggled.connect(lambda gorunsun, c=c: self.goster(c, gorunsun))
        menu.addSeparator()
        menu.addAction("Tüm kolonları göster", self.hepsini_goster)
        return menu

    def gizli(self):
        """Kullanıcının gizlediği kolonlar (yer olmadığı için kendiliğinden gizlenenler hariç)."""
        return [c for c in range(self.tablo.columnCount()) if self.tablo.isColumnHidden(c) and c not in self.oto_gizli]

    def goster(self, kolon, gorunsun):
        if kolon in self.zorunlu:
            return
        self.oto_gizli.discard(kolon)
        (self.istenen.add if gorunsun else self.istenen.discard)(kolon)
        self.tablo.setColumnHidden(kolon, not gorunsun)
        if hasattr(self.tablo, "orantili"):
            self.tablo.orantili.dagit_sonra()
        self.tercihler.yaz(f"kolonlar/{self.anahtar}", ",".join(map(str, self.gizli())))
        self.denetle_sonra()

    def hepsini_goster(self):
        for c in self.gizli() + sorted(self.oto_gizli):
            self.goster(c, True)

    def sorma(self):
        self.tercihler.yaz(f"kolonlar/{self.anahtar}_sorma", "1")
        self.soru.hide()

    # --- Sığma hesabı: gerçek kolon genişlikleri yerine içeriklerden hesaplanır (gizleyip denemeye gerek kalmaz)

    def _agirliklar(self):
        """Kalan yeri paylaşan uzun metinli kolonlar ve ağırlıkları (Qt'nin Stretch kolonları 2 sayılır)."""
        orantili = getattr(self.tablo, "orantili", None)
        if orantili is not None:
            return orantili.agirliklar
        baslik = self.tablo.horizontalHeader()
        return {c: 2 for c in range(self.tablo.columnCount()) if baslik.sectionResizeMode(c) == QHeaderView.Stretch}

    def _baslik_eni(self, c):
        """Başlığın gereken genişliği. Qt gizli kolonda 0 verir: kolon gizlenince "artık sığıyor" sanılıp geri
        açılıyor, açılınca sığmayıp yeniden gizleniyordu (liste titriyordu). Görünürken ölçülen değer saklanır;
        hiç görünmemiş kolonda yazının genişliğinden tahmin edilir."""
        baslik = self.tablo.horizontalHeader()
        if not self.tablo.isColumnHidden(c):
            olcu = baslik.sectionSizeHint(c)
            if olcu > 0:
                self.baslik_olcu[c] = olcu
        if c not in self.baslik_olcu:
            hucre = self.tablo.horizontalHeaderItem(c)
            return QFontMetrics(baslik.font()).horizontalAdvance(hucre.text() if hucre else "") + 40
        return self.baslik_olcu[c]

    def _ihtiyac(self, kolonlar):
        agirlik = self._agirliklar()
        toplam = 0
        for c in kolonlar:
            if c in agirlik:
                toplam += self.PAY_EN * agirlik[c]
            else:
                toplam += min(self.MAKUL_EN, max(self._baslik_eni(c), self.tablo.sizeHintForColumn(c)))
        return toplam

    def _bos_kolon(self, c):
        return all(not (self.tablo.item(r, c) and self.tablo.item(r, c).text().strip())
                   for r in range(self.tablo.rowCount()))

    def sigmiyor(self, kolonlar=None):
        """Görünen kolonların (verilmezse şu an görünenler) makul genişlikleri tablonun genişliğini aşıyor mu?
        Kendiliğinden gizlenmiş bir kolonun geri gelmesi için GERI_PAY kadar fazladan yer gerekir."""
        if self.tablo.rowCount() == 0 or not self.tablo.isVisible():
            return False
        if kolonlar is None:
            kolonlar = [c for c in range(self.tablo.columnCount()) if not self.tablo.isColumnHidden(c)]
        pay = self.GERI_PAY if self.oto_gizli & set(kolonlar) else 0
        return self._ihtiyac(kolonlar) + pay > self.tablo.viewport().width()

    def yerlestir(self):
        """Sığmıyorsa boş, sonra öncelikli kolonları kendiliğinden gizler; yer açılınca geri getirir."""
        if self.tablo.rowCount() == 0 or not self.tablo.isVisible():
            return
        gorunen = [c for c in range(self.tablo.columnCount())
                   if not self.tablo.isColumnHidden(c) or c in self.oto_gizli]
        adaylar = [c for c in gorunen if c not in self.zorunlu and c not in self.istenen and self._bos_kolon(c)]
        adaylar += [c for c in self.otomatik if c in gorunen and c not in self.istenen and c not in adaylar]
        gizlenecek = set()
        for c in adaylar:
            if not self.sigmiyor([k for k in gorunen if k not in gizlenecek]):
                break
            gizlenecek.add(c)
        if gizlenecek == self.oto_gizli:
            return
        for c in self.oto_gizli - gizlenecek:
            self.tablo.setColumnHidden(c, False)
        for c in gizlenecek - self.oto_gizli:
            self.tablo.setColumnHidden(c, True)
        self.oto_gizli = gizlenecek
        if hasattr(self.tablo, "orantili"):
            self.tablo.orantili.dagit()       # kalan kolonlar aynı karede yeni genişliğini alır

    def denetle_sonra(self, *_):
        if not self.bekliyor:
            self.bekliyor = True
            QTimer.singleShot(0, self, self.denetle)

    def denetle(self):
        self.bekliyor = False
        if self.denetleniyor:                 # kolon gizlemek tabloyu yeniden boyutlandırırsa iç içe çağrılır
            return
        self.denetleniyor = True
        try:
            self._denetle()
        finally:
            self.denetleniyor = False

    def _denetle(self):
        self.yerlestir()
        sor = not self.tercihler.mantiksal(f"kolonlar/{self.anahtar}_sorma") and self.sigmiyor()
        self.soru.setVisible(sor)

    def eventFilter(self, nesne, olay):
        # Ertelenirse önce sığmayan liste çizilir, sonra kolon gizlenir: bir kare titrer
        if olay.type() in (QEvent.Resize, QEvent.Show):
            self.denetle()
        return False
