## İstatistik sayfası: Çizelgeler (tür, yazar, yayınevi, basım yılı) ve Grafikler ##

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QGridLayout, QGroupBox, QHeaderView, QTableWidget, QVBoxLayout, QWidget

from acodes.disa_aktar import sag_tik_menusu
from acodes.grafikler import GrafikPaneli
from acodes.olaylar import olaylar
from acodes.tablo import OranCubugu, tablo_ayarla, tablo_basliklari, tabloya_yaz
from acodes.yan_menu import alt_sekmeli_sayfa
from database.istatistik import rapor

# (veritabanı kolonu, tablo başlığı, kart başlığı, gösterilecek en fazla satır)
ISTATISTIKLER = [('Turu','Yayın Türü',"Türlere göre",35), ('Yazari','Yazar',"Yazarlara göre",40),
                 ('Yayinevi','Yayınevi',"Yayınevlerine göre",35), ('Yili','Basım Yılı',"Basım yıllarına göre",35)]


class Istatistik(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Çizelgeler: başlıklı kartlar; ad kolonu kalan yeri alır, sayılar sığar, yatay kaydırma yok
        self.cizelgeler=QWidget()
        self.izgara=QGridLayout(self.cizelgeler)
        self.izgara.setHorizontalSpacing(14)
        self.izgara.setVerticalSpacing(14)
        self.tablolar=[]
        self.kartlar=[]
        for _,baslik,kart_basligi,_ in ISTATISTIKLER:
            tablo=QTableWidget(0,2)
            tablo_ayarla(tablo)
            tablo.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            sag_tik_menusu(self,tablo,f"İstatistik - {baslik}")
            kart=QGroupBox(kart_basligi)
            ic=QVBoxLayout(kart)
            ic.setContentsMargins(0,0,0,0)
            ic.addWidget(tablo)
            self.tablolar.append(tablo)
            self.kartlar.append(kart)
        self.sutun=None
        self.cizelgeleri_diz()
        self.cizelgeler.installEventFilter(self)

        # Grafikler: her yenilemede veritabanından çizilir
        grafik_sayfasi=QWidget()
        g=QGridLayout(grafik_sayfasi)
        g.setContentsMargins(5,5,5,5)
        g.setSpacing(5)
        self.grafikler=GrafikPaneli(grafik_sayfasi)
        g.addWidget(self.grafikler,0,0)

        sayfa,self.sekmeler=alt_sekmeli_sayfa("İstatistik",[("Çizelgeler",self.cizelgeler),("Grafikler",grafik_sayfasi)])
        duzen=QVBoxLayout(self)
        duzen.setContentsMargins(0,0,0,0)
        duzen.addWidget(sayfa)
        self.yenile()
        olaylar.kitaplar.connect(self.yenile)

    def cizelgeleri_diz(self):
        ###  Geniş pencerede dört çizelge yan yana, dar pencerede (ör. menü açıkken) 2x2  ###
        sutun=4 if self.cizelgeler.width()>=1500 else 2
        if self.sutun==sutun:
            return
        self.sutun=sutun
        for i,kart in enumerate(self.kartlar):
            self.izgara.removeWidget(kart)
            self.izgara.addWidget(kart,i//sutun,i%sutun)

    def eventFilter(self,nesne,olay):
        if olay.type()==QEvent.Resize and nesne is self.cizelgeler:
            self.cizelgeleri_diz()
        return super().eventFilter(nesne,olay)

    def yenile(self):
        for tablo,(kolon,baslik,_,adet) in zip(self.tablolar,ISTATISTIKLER):
            tablo_basliklari(tablo,[(225,baslik),(50,"Adet")])
            baslik_cubugu=tablo.horizontalHeader()
            baslik_cubugu.setStretchLastSection(False)
            baslik_cubugu.setSectionResizeMode(0,QHeaderView.Stretch)
            baslik_cubugu.setSectionResizeMode(1,QHeaderView.Fixed)
            tablo.setColumnWidth(1,170)                          # Adet: oran çubuğu ve sayı
            if not isinstance(tablo.itemDelegateForColumn(1),OranCubugu):
                tablo.setItemDelegateForColumn(1,OranCubugu(tablo))
            kayit=list(rapor(kolon,adet).items())
            if kolon=='Yili':
                kayit.sort(key=lambda k: (not str(k[0]).isdigit(), str(k[0])))   # yıllar sırayla, belirtilmemiş en sonda
            tabloya_yaz(tablo,kayit)
            for r in range(tablo.rowCount()):
                tablo.item(r,0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)   # yıllar da adlar gibi sola yaslı
            tablo.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.grafikler.yenile()
