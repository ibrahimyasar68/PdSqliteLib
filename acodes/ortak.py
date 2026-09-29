## Admin (Library) ve Guest panellerinde ortak olan sekmeler ##
# Giriş (çıkış ve kullanıcı adı), Kitap Listesi, Filtre ve İstatistik sekmeleri.
# İki panelin .ui dosyasında bu sekmelerdeki nesne adları aynı olduğu için kod tek yerde tutulur.

from PyQt5.QtWidgets import QLabel, QLineEdit, QMessageBox, QTableWidgetItem
from bforms.onay import onay
from database.dbframe import df_sort_list, df_srt_fltr, kitap_ara, rapor
from acodes.grafikler import GrafikPaneli

SECINIZ = ' Seçiniz...'

LISTE_KOLONLARI = [(60,"Sıra No"),(200,"Adı"),(200,"Yazarı"),(150,"Çeviren"),
                   (150,"Turu"),(200,"Yayınevi"),(60,"Yılı"),(60,"Sayfa")]
FILTRE_KOLONLARI = [(50,"Sıra No"),(190,"Adı"),(190,"Yazarı"),(130,"Çeviren"),
                    (130,"Turu"),(165,"Yayınevi"),(40,"Yılı"),(40,"Sayfa")]

# Tab 4 filtreleri: (sıra no, veritabanı kolonu, seçim tablosu başlığı)
FILTRELER = [(1,'Turu','Seçilen Tür'), (2,'Yazari','Seçilen Yazar'),
             (3,'Yayinevi','Seçilen Yayınevi'), (4,'Yili','Seçilen Yıl')]

# Tab 5 istatistikleri: (tablo no, veritabanı kolonu, başlık, gösterilecek en fazla satır)
ISTATISTIKLER = [(1,'Turu','Yayın Türü',35), (2,'Yazari','Yazar',40),
                 (3,'Yayinevi','Yayınevi',35), (4,'Yili','Basım Yılı',35)]


def tablo_basliklari(tablo, kolonlar):
    for i,(genislik,baslik) in enumerate(kolonlar):
        tablo.setColumnWidth(i,genislik)
        tablo.setHorizontalHeaderItem(i,QTableWidgetItem(baslik))


def tabloya_yaz(tablo, satirlar):
    tablo.setRowCount(len(satirlar))
    for r,satir in enumerate(satirlar):
        for c,deger in enumerate(satir):
            tablo.setItem(r,c,QTableWidgetItem(str(deger)))


class OrtakSekmeler:
    """Kullanan sınıfta self.QtLibrary (arayüz) ve self.dur_msj tanımlı olmalıdır."""

    def ortak_sekmeleri_kur(self):
        ui=self.QtLibrary

        ###  Tab_1  ###
        ui.pushButton_1_cikis.clicked.connect(self.close)

        ###  Tab_2  ###
        self.create_form_tab2()
        self.arama_kutusu_kur()
        ui.pushButton_2_listele.clicked.connect(self.listele)
        ui.pushButton_2_temizle.clicked.connect(self.temizle)

        ###  Tab_4  ###
        self.filtre_secimleri={no:[] for no,_,_ in FILTRELER}
        for no,kolon,baslik in FILTRELER:
            self.filtre_kur(no,kolon,baslik)
            self.filtre_combo(no).currentTextChanged.connect(lambda _,no=no: self.filtre_ekle(no))
            getattr(ui,f"pushButton_4_{no}_listele").clicked.connect(lambda _,no=no,kolon=kolon: self.filtre_listele(no,kolon))
            getattr(ui,f"pushButton_4_{no}_temizle").clicked.connect(lambda _,no=no,baslik=baslik: self.filtre_temizle(no,baslik))

        ###  Tab_5  ###
        # Grafikler: eski sabit resmin yerine her yenilemede çizilen grafikler
        ui.widget.hide()
        self.grafikler=GrafikPaneli(ui.tab_5_2)
        ui.gridLayout_6.addWidget(self.grafikler,0,0)
        self.create_tab_5()

    ##################################
    #####   Tab_1 Fonksiyonlar   #####
    ##################################

    def user_name(self,name):
        self.aktif_kullanici=name
        self.QtLibrary.label_log_on.setText(name)

    ##################################
    #####   Tab_2 Fonksiyonlar   #####
    ##################################

    def create_form_tab2(self):
        self.QtLibrary.tableWidget_2.setRowCount(1)
        tablo_basliklari(self.QtLibrary.tableWidget_2, LISTE_KOLONLARI)

    def arama_kutusu_kur(self):
        ###  Tablonun üstüne arama kutusu (tablo biraz aşağı kaydırılır)  ###
        ui=self.QtLibrary
        ui.tableWidget_2.setGeometry(160,55,1160,545)
        self.arama=QLineEdit(ui.tab_2)
        self.arama.setGeometry(160,10,520,36)
        self.arama.setPlaceholderText("Ara: kitap adı, yazar, çevirmen, tür, yayınevi, yıl...")
        self.arama.setClearButtonEnabled(True)
        self.arama.setStyleSheet('font: 12pt "Verdana"; color: black; background-color: white;'
                                 ' border: 1px solid gray; border-radius: 6px; padding: 2px 6px;')
        self.arama_sonuc=QLabel(ui.tab_2)
        self.arama_sonuc.setGeometry(700,10,400,36)
        self.arama_sonuc.setStyleSheet('font: bold 12pt "Verdana"; color: rgb(0, 60, 0);')
        self.arama.textChanged.connect(self.listele)

    def listele(self):
        sorgu=self.arama.text().strip()
        kitaplar=kitap_ara(sorgu)
        tabloya_yaz(self.QtLibrary.tableWidget_2, kitaplar)
        self.arama_sonuc.setText(f"{len(kitaplar)} kitap bulundu" if sorgu else f"Toplam {len(kitaplar)} kitap")

    def temizle(self):
        self.arama.blockSignals(True)  # Temizlerken liste yeniden doldurulmasın
        self.arama.clear()
        self.arama.blockSignals(False)
        self.arama_sonuc.clear()
        self.QtLibrary.tableWidget_2.clear()
        self.create_form_tab2()
        self.QtLibrary.statusbar.showMessage("Liste temizlendi.",self.dur_msj)

    ##################################
    #####   Tab_4 Fonksiyonlar   #####
    ##################################

    def filtre_combo(self,no):
        return getattr(self.QtLibrary,f"comboBox_4_{no}_turu")

    def filtre_combo_doldur(self,no,kolon):
        cmb=self.filtre_combo(no)
        cmb.blockSignals(True)  # Doldururken seçim listesine otomatik ekleme yapılmasın
        cmb.clear()
        cmb.addItems([SECINIZ]+df_sort_list(kolon))
        cmb.blockSignals(False)

    def filtre_kur(self,no,kolon,baslik):
        ui=self.QtLibrary
        self.filtre_combo_doldur(no,kolon)
        secim=getattr(ui,f"tableWidget_4_{no}_1")
        secim.setColumnWidth(0,200)
        secim.setHorizontalHeaderItem(0,QTableWidgetItem(baslik))
        secim.setRowCount(1)
        sonuc=getattr(ui,f"tableWidget_4_{no}_2")
        tablo_basliklari(sonuc,FILTRE_KOLONLARI)
        sonuc.setRowCount(1)

    def filtre_ekle(self,no):
        secimler=self.filtre_secimleri[no]
        deger=self.filtre_combo(no).currentText()
        if deger not in (SECINIZ,'') and deger not in secimler:
            secimler.append(deger)
            secimler.sort()
            self.QtLibrary.statusbar.showMessage(f"Listeye ' {deger} ' eklendi",self.dur_msj)
        tabloya_yaz(getattr(self.QtLibrary,f"tableWidget_4_{no}_1"), [[s] for s in secimler])

    def filtre_listele(self,no,kolon):
        ui=self.QtLibrary
        secimler=self.filtre_secimleri[no]
        if secimler:
            satirlar=[]
            for deger in secimler:
                satirlar+=df_srt_fltr(kolon,deger)
            tabloya_yaz(getattr(ui,f"tableWidget_4_{no}_2"), satirlar)
            ui.statusbar.showMessage("Sonuçlar listelendi",self.dur_msj)
        else:
            ui.statusbar.showMessage("Listelenecek seçim yapınız!",self.dur_msj)
        getattr(ui,f"pushButton_4_{no}_temizle").setEnabled(True)

    def filtre_temizle(self,no,baslik):
        ui=self.QtLibrary
        secimler=self.filtre_secimleri[no]
        if not secimler:
            ui.statusbar.showMessage("Temizlenecek Veri Yok!",self.dur_msj)
            return
        if onay('Kayıtları silmek istiyor musunuz?')!=QMessageBox.Yes:
            return
        secimler.clear()
        self.filtre_combo(no).setCurrentIndex(0)
        secim=getattr(ui,f"tableWidget_4_{no}_1")
        secim.clear()
        secim.setHorizontalHeaderItem(0,QTableWidgetItem(baslik))
        secim.setRowCount(1)
        getattr(ui,f"pushButton_4_{no}_temizle").setEnabled(False)
        sonuc=getattr(ui,f"tableWidget_4_{no}_2")
        sonuc.clear()
        sonuc.setRowCount(1)
        tablo_basliklari(sonuc,FILTRE_KOLONLARI)
        ui.statusbar.showMessage("Veriler temizlendi",self.dur_msj)

    ##################################
    #####   Tab_5 Fonksiyonlar   #####
    ##################################

    def create_tab_5(self):
        for no,kolon,baslik,adet in ISTATISTIKLER:
            tablo=getattr(self.QtLibrary,f"tableWidget_5_1_{no}")
            tablo_basliklari(tablo,[(225,baslik),(50,"Adet")])
            kayit=rapor(kolon,adet)
            if kolon=='Yili':
                kayit=kayit.sort_index()
            tabloya_yaz(tablo, list(zip(kayit.index,kayit.values)))
        if hasattr(self,"grafikler"):
            self.grafikler.yenile()
