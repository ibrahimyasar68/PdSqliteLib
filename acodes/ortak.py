## Admin (Library) ve Guest panellerinde ortak olan sekmeler ##
# Giriş (çıkış ve kullanıcı adı), Kitap Listesi, Filtre ve İstatistik sekmeleri.
# İki panelin .ui dosyasında bu sekmelerdeki nesne adları aynı olduğu için kod tek yerde tutulur.

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QVBoxLayout
from database.dbframe import kitap_ara, rapor
from acodes.grafikler import GrafikPaneli
from acodes.filtre_paneli import FiltrePaneli
from acodes import tema
from acodes.yerlesim import liste_sayfasi
from acodes.tablo import KolonSecici, tablo_ayarla, tablo_basliklari, tabloya_yaz  # noqa: F401  (library.py de buradan alır)
from acodes.disa_aktar import disa_aktar, sag_tik_menusu
from acodes.kullanici_yonetimi import SifreDegistir, panel_butonu

LISTE_KOLONLARI = [(70,"Kayıt No"),(200,"Adı"),(160,"Yazarı"),(120,"Çeviren"),(90,"Türü"),
                   (160,"Yayınevi"),(50,"Yılı"),(55,"Sayfa"),(120,"ISBN"),(55,"Kopya"),(60,"Raf")]

# Tab 5 istatistikleri: (tablo no, veritabanı kolonu, başlık, gösterilecek en fazla satır)
ISTATISTIKLER = [(1,'Turu','Yayın Türü',35), (2,'Yazari','Yazar',40),
                 (3,'Yayinevi','Yayınevi',35), (4,'Yili','Basım Yılı',35)]


class OrtakSekmeler:
    """Kullanan sınıfta self.QtLibrary (arayüz) ve self.dur_msj tanımlı olmalıdır."""

    def ortak_sekmeleri_kur(self):
        ui=self.QtLibrary

        ###  Tab_1  ###
        # Çıkış butonu oturumu kapatıp giriş ekranına döner (programdan çıkış giriş ekranındadır)
        ui.pushButton_1_cikis.setText("Oturumu Kapat")
        ui.pushButton_1_cikis.setToolTip("Oturumu kapatıp giriş ekranına dön")
        ui.pushButton_1_cikis.clicked.connect(self.oturumu_kapat)

        ###  Tab_2  ###
        self.create_form_tab2()
        self.arama_kutusu_kur()
        # Liste sekmeye gelince kendiliğinden dolar ve yazdıkça süzülür; Listele butonuna gerek kalmadı
        ui.pushButton_2_listele.hide()
        ui.tabWidget.currentChanged.connect(self.liste_sekmesi_acildi)
        ui.pushButton_2_temizle.clicked.connect(self.temizle)

        ###  Tab_4: dört ayrı filtre sekmesi yerine tek panel  ###
        ui.gridLayout_3.removeWidget(ui.tabWidget_4)
        ui.tabWidget_4.setParent(None)   # hemen ağaçtan çıksın (ikon, arama vb. eski bileşenleri görmesin)
        ui.tabWidget_4.deleteLater()
        self.filtre=FiltrePaneli(mesaj=lambda metin: self.QtLibrary.statusbar.showMessage(metin,self.dur_msj))
        ui.gridLayout_3.addWidget(self.filtre,0,0)

        ###  Tab_5  ###
        # Grafikler: eski sabit resmin yerine her yenilemede çizilen grafikler
        ui.widget.hide()
        self.grafikler=GrafikPaneli(ui.tab_5_2)
        ui.gridLayout_6.addWidget(self.grafikler,0,0)
        self.create_tab_5()

        ###  Tablolar: başlığa tıklayınca sıralama, hücreler salt okunur, boşken yönlendirici mesaj  ###
        tablo_ayarla(ui.tableWidget_2, bos_metin="Aramanıza uyan kitap yok.")
        self.cizelgeleri_kartla()

        ###  Dışa aktarma: ana tablolarda buton, tüm tablolarda sağ tık menüsü  ###
        self.aktar_liste=self.aktar_butonu(ui.tableWidget_2,"Kitap Listesi",ui.pushButton_2_temizle,(40,480,100,60))
        self.filtre.btn_aktar.clicked.connect(lambda: disa_aktar(self,self.filtre.tablo,"Filtre"))
        sag_tik_menusu(self,self.filtre.tablo,"Filtre")
        for no,_,baslik,_ in ISTATISTIKLER:
            sag_tik_menusu(self,getattr(ui,f"tableWidget_5_1_{no}"),f"İstatistik - {baslik}")

        ###  Kitap Listesi esnek yerleşim: solda butonlar, üstte arama, tablo pencereyle büyür  ###
        ust=QHBoxLayout()
        self.arama.setMinimumSize(320,36)
        self.arama.setMaximumWidth(620)
        ust.addWidget(self.arama,1)
        ust.addWidget(self.arama_sonuc)
        ust.addStretch()
        self.liste_kolonlari=KolonSecici(ui.tableWidget_2,"kitap_listesi")
        self.liste_kolonlari.buton.setMinimumHeight(36)
        ust.addWidget(self.liste_kolonlari.buton)
        liste_sayfasi(ui.tab_2,[ui.pushButton_2_temizle,self.aktar_liste],ui.tableWidget_2,ust,
                      uyari=self.liste_kolonlari.soru)

    def aktar_butonu(self,tablo,ad,ornek,konum):
        ###  Örnek butonla aynı stilde "Dışa Aktar" butonu ve tabloya sağ tık menüsü  ###
        buton=panel_butonu(ornek,"Dışa Aktar",f"{ornek.objectName()}_aktar")
        buton.setParent(ornek.parentWidget())
        buton.setGeometry(*konum)
        buton.setToolTip(f"{ad} tablosunu Excel veya CSV olarak kaydet")
        buton.clicked.connect(lambda: disa_aktar(self,tablo,ad))
        buton.show()
        sag_tik_menusu(self,tablo,ad)
        return buton

    ##################################
    #####   Tab_1 Fonksiyonlar   #####
    ##################################

    def oturumu_kapat(self):
        ###  Açık alt pencereleri kapat, giriş ekranına haber ver, paneli kapat  ###
        if hasattr(self,"user"):
            self.user.close()
        self.oturum_kapandi.emit()   # giriş ekranı önce görünür olur, böylece program kapanmaz
        self.close()

    def sifremi_degistir(self):
        SifreDegistir(self.aktif_kullanici, eski_sor=True, parent=self).exec_()

    def user_name(self,name):
        self.aktif_kullanici=name
        if hasattr(self,"ana_sayfa"):
            self.ana_sayfa.karsila(name,self.ROL)
        if hasattr(self,"yan_menu"):
            self.yan_menu.kullanici(name,self.ROL)
        self.setWindowTitle(f"{self.PENCERE_BASLIGI} - {name}")
        self.QtLibrary.label_log_on.setText(name)

    ##################################
    #####   Tab_2 Fonksiyonlar   #####
    ##################################

    def create_form_tab2(self):
        self.QtLibrary.tableWidget_2.setColumnCount(len(LISTE_KOLONLARI))
        self.QtLibrary.tableWidget_2.setRowCount(0)
        tablo_basliklari(self.QtLibrary.tableWidget_2, LISTE_KOLONLARI)

    def arama_kutusu_kur(self):
        ###  Tablonun üstüne arama kutusu (tablo biraz aşağı kaydırılır)  ###
        ui=self.QtLibrary
        ui.tableWidget_2.setGeometry(160,55,1160,545)
        self.arama=QLineEdit(ui.tab_2)
        self.arama.setGeometry(160,10,520,36)
        self.arama.setPlaceholderText("Ara: kitap adı, yazar, çevirmen, tür, yayınevi, yıl, ISBN, raf, not...")
        self.arama.setClearButtonEnabled(True)
        self.arama.setStyleSheet('font-size: 17px; border-radius: 6px; padding: 2px 8px;')
        self.arama_sonuc=QLabel(ui.tab_2)
        self.arama_sonuc.setGeometry(700,10,400,36)
        self.arama_sonuc.setStyleSheet(f'font-size: 16px; font-weight: bold; color: {tema.VURGU_KOYU};')
        self.arama.textChanged.connect(self.listele)

    def listele(self):
        sorgu=self.arama.text().strip()
        kitaplar=kitap_ara(sorgu)
        tabloya_yaz(self.QtLibrary.tableWidget_2, kitaplar)
        self.arama_sonuc.setText(f"{len(kitaplar)} kitap bulundu" if sorgu else f"Toplam {len(kitaplar)} kitap")

    def liste_sekmesi_acildi(self):
        if self.QtLibrary.tabWidget.currentWidget() is self.QtLibrary.tab_2:
            self.listele()   # her gelişte güncel liste (başka sekmede eklenen/silinen kitaplar dahil)

    def temizle(self):
        ###  Aramayı temizle: tüm kitaplar listelenir  ###
        self.arama.clear()

    ##################################
    #####   Tab_5 Fonksiyonlar   #####
    ##################################

    def cizelgeleri_kartla(self):
        ###  Dört çizelge: başlıklı beyaz kartlar; ad kolonu kalan yeri alır, sayılar sığar, yatay kaydırma yok  ###
        ui=self.QtLibrary
        for etiket in (ui.label_25,ui.label_56,ui.label_58,ui.label_59):
            etiket.hide()
        basliklar={1:"Türlere Göre",2:"Yazarlara Göre",3:"Yayınevlerine Göre",4:"Basım Yıllarına Göre"}
        self.cizelge_kartlari=[]
        for no,*_ in ISTATISTIKLER:
            tablo=getattr(ui,f"tableWidget_5_1_{no}")
            tablo_ayarla(tablo)
            tablo.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            ui.gridLayout_5.removeWidget(tablo)
            kart=QGroupBox(basliklar[no])
            ic=QVBoxLayout(kart)
            ic.setContentsMargins(0,0,0,0)
            ic.addWidget(tablo)
            self.cizelge_kartlari.append(kart)
        ui.gridLayout_5.setHorizontalSpacing(14)
        ui.gridLayout_5.setVerticalSpacing(14)
        self.cizelgeleri_diz()
        ui.tab_5_1.installEventFilter(self)

    def cizelgeleri_diz(self):
        ###  Geniş pencerede dört çizelge yan yana, dar pencerede (ör. menü açıkken) 2x2  ###
        sutun=4 if self.QtLibrary.tab_5_1.width()>=1500 else 2
        if getattr(self,"cizelge_sutun",None)==sutun:
            return
        self.cizelge_sutun=sutun
        for i,kart in enumerate(self.cizelge_kartlari):
            self.QtLibrary.gridLayout_5.removeWidget(kart)
            self.QtLibrary.gridLayout_5.addWidget(kart,i//sutun,i%sutun)

    def eventFilter(self,nesne,olay):
        if olay.type()==QEvent.Resize and nesne is self.QtLibrary.tab_5_1:
            self.cizelgeleri_diz()
        return super().eventFilter(nesne,olay)

    def create_tab_5(self):
        for no,kolon,baslik,adet in ISTATISTIKLER:
            tablo=getattr(self.QtLibrary,f"tableWidget_5_1_{no}")
            tablo_basliklari(tablo,[(225,baslik),(50,"Adet")])
            baslik_cubugu=tablo.horizontalHeader()
            baslik_cubugu.setStretchLastSection(False)
            baslik_cubugu.setSectionResizeMode(0,QHeaderView.Stretch)
            baslik_cubugu.setSectionResizeMode(1,QHeaderView.ResizeToContents)
            kayit=rapor(kolon,adet)
            if kolon=='Yili':
                kayit=kayit.sort_index()
            tabloya_yaz(tablo, list(zip(kayit.index,kayit.values)))
        if hasattr(self,"grafikler"):
            self.grafikler.yenile()
