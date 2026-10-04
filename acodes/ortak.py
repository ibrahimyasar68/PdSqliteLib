## Admin (Library) ve Guest panellerinde ortak olan sekmeler ##
# Giriş (çıkış ve kullanıcı adı), Kitap Listesi, Filtre ve İstatistik sekmeleri.
# İki panelin .ui dosyasında bu sekmelerdeki nesne adları aynı olduğu için kod tek yerde tutulur.

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QGroupBox, QHeaderView, QLabel, QLineEdit, QVBoxLayout
from database.dbframe import katla, kitap_ara, kitap_durumlari, rapor
from acodes.grafikler import GrafikPaneli
from acodes.filtre_paneli import FiltrePaneli
from acodes.yerlesim import baslik_satiri, liste_sayfasi
from acodes.tablo import (KolonSecici, OranCubugu, OrantiliKolonlar, durum_ekle, durum_rozeti_kur, tablo_ayarla, tablo_basliklari,
                          tabloya_yaz)
from acodes.disa_aktar import disa_aktar, sag_tik_menusu
from acodes.kisayollar import arama_kutusu_yap, kisayol, metin as kisayol_metni
from acodes.komut_paleti import KomutPaleti, eslesir
from acodes import ikonlar, tema
from acodes.kullanici_yonetimi import SifreDegistir, panel_butonu

LISTE_KOLONLARI = [(70,"Kayıt No"),(200,"Adı"),(160,"Yazarı"),(120,"Çeviren"),(90,"Türü"),
                   (160,"Yayınevi"),(50,"Yılı"),(55,"Sayfa"),(120,"ISBN"),(55,"Kopya"),(60,"Raf"),(150,"Durum")]
GENIS_KOLONLAR = {1:3,2:2,3:1.5,5:2}  # Adı, Yazarı, Çeviren, Yayınevi kalan yeri bu oranlarla paylaşır
VARSAYILAN_GIZLI = (0,8)            # Kayıt No (sıra numarası var) ve ISBN; Kolonlar'dan açılabilir
OTOMATIK_GIZLI = (10,9,3,7)         # liste sığmazsa sırayla gizlenir: Raf, Kopya, Çeviren, Sayfa

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
        # Liste sekmeye gelince kendiliğinden dolar ve yazdıkça süzülür
        ui.tabWidget.currentChanged.connect(self.liste_sekmesi_acildi)
        ui.pushButton_2_temizle.clicked.connect(self.temizle)

        ###  Tab_4: tür, yazar, yayınevi ve yıl tek panelde  ###
        self.filtre=FiltrePaneli(mesaj=lambda metin,tur=None: self.bildirim.mesaj(metin,tur,self.dur_msj))
        ui.gridLayout_3.addWidget(self.filtre,0,0)

        ###  Tab_5  ###
        # Grafikler: her yenilemede veritabanından çizilir
        self.grafikler=GrafikPaneli(ui.tab_5_2)
        ui.gridLayout_6.addWidget(self.grafikler,0,0)
        self.create_tab_5()

        ###  Tablolar: başlığa tıklayınca sıralama, hücreler salt okunur, boşken yönlendirici mesaj  ###
        tablo_ayarla(ui.tableWidget_2, bos_metin="Aramanıza uyan kitap yok.", bos_simge="ara",
                     bos_eylem=("Aramayı Temizle", self.temizle))
        durum_rozeti_kur(ui.tableWidget_2)
        ui.tableWidget_2.orantili=OrantiliKolonlar(ui.tableWidget_2, GENIS_KOLONLAR)
        self.cizelgeleri_kartla()

        ###  Dışa aktarma: ana tablolarda buton, tüm tablolarda sağ tık menüsü  ###
        self.aktar_liste=self.aktar_butonu(ui.tableWidget_2,"Kitap Listesi",ui.pushButton_2_temizle)
        self.filtre.btn_aktar.clicked.connect(lambda: disa_aktar(self,self.filtre.tablo,"Filtre"))
        sag_tik_menusu(self,self.filtre.tablo,"Filtre")
        for no,_,baslik,_ in ISTATISTIKLER:
            sag_tik_menusu(self,getattr(ui,f"tableWidget_5_1_{no}"),f"İstatistik - {baslik}")

        ###  Kitap Listesi: üstte başlık, sonuç sayısı ve butonlar; altında arama; tablo pencereyle büyür  ###
        self.liste_kolonlari=KolonSecici(ui.tableWidget_2,"kitap_listesi",varsayilan_gizli=VARSAYILAN_GIZLI,
                                         otomatik=OTOMATIK_GIZLI)
        ust=baslik_satiri("Kitap Listesi",self.arama_sonuc,
                          [ui.pushButton_2_temizle,self.aktar_liste,self.liste_kolonlari.buton])
        liste_sayfasi(ui.tab_2,ust,self.arama,ui.tableWidget_2,uyari=self.liste_kolonlari.soru)

    ##################################
    #####   Hızlı arama (Ctrl+K)   #####
    ##################################

    def hizli_arama_kur(self,sayfa_ikonlari):
        ###  Ctrl+K ve menüdeki "Hızlı ara" aynı paleti açar (yan menü ve sayfa ikonları kurulduktan sonra)  ###
        self.sayfa_ikonlari=sayfa_ikonlari
        self.palet=KomutPaleti(self.komut_kaynagi,self)
        kisayol("Ctrl+K",self,self.palet.ac)
        self.yan_menu.btn_ara.clicked.connect(self.palet.ac)
        self.yan_menu.btn_ara.setToolTip(f"Kitap, üye veya bölüm arayın ({kisayol_metni('Ctrl+K')})")

    def komut_kaynagi(self,metin):
        gruplar=[("Bölümler",[k for k in self.bolum_komutlari() if eslesir(metin,k[0])]),
                 ("İşlemler",[k[:4] for k in self.islem_komutlari() if eslesir(metin,k[0],k[1],k[4])])]
        if len(katla(metin).strip())>=2:      # tek harfle yüzlerce kitap listelenmesin
            gruplar.append(("Kitaplar",self.kitap_komutlari(metin)))
            gruplar+=self.ek_arama_gruplari(metin)
        return gruplar

    def bolum_komutlari(self):
        sekmeler=self.QtLibrary.tabWidget
        komutlar=[]
        for i in range(sekmeler.count()):
            sayfa=sekmeler.widget(i)
            ad=self.yan_menu.ogeler[i][0].ad
            kisa=kisayol_metni(f"Ctrl+{i+1}") if i<9 else ""
            ikon=ikonlar.SEKME_IKONLARI.get(self.sayfa_ikonlari.get(sayfa))
            komutlar.append((ad,kisa,ikon,lambda s=sayfa: sekmeler.setCurrentWidget(s)))
        return komutlar

    def islem_komutlari(self):
        """[(ad, açıklama, ikon, işlev, aramada eşleşecek ek kelimeler)] — panele göre (Library / Guest) genişler."""
        q=self.QtLibrary
        return [("Grafikler","İstatistik","grafik",lambda: (q.tabWidget.setCurrentWidget(q.tab_5),q.tabWidget_5.setCurrentWidget(q.tab_5_2)),"grafik çizelge"),
                ("Şifremi değiştir","Hesap","kilit",self.sifremi_degistir,"parola"),
                ("Kullanma kılavuzu","Yardım","kitap",self.ayarlar.kilavuzu_ac,"yardım nasıl"),
                ("Oturumu kapat","Giriş ekranına dön","guc",self.oturumu_kapat,"çıkış")]

    def kitap_komutlari(self,metin,adet=8):
        kitaplar=kitap_ara(metin)[:adet]
        durumlar=kitap_durumlari([k[0] for k in kitaplar])
        return [(k[1]," · ".join(str(x) for x in (k[2],k[5],k[6],durum) if x),"kitap",
                 lambda kitap_id=k[0],adi=k[1]: self.kitabi_ac(kitap_id,adi))
                for k,(durum,_) in zip(kitaplar,durumlar)]

    def ek_arama_gruplari(self,metin):
        return []

    def kitabi_ac(self,kitap_id,adi):
        ###  Hızlı aramada seçilen kitap: Kitap Listesi bu kitapla süzülmüş açılır (yönetici panelinde düzenleme)  ###
        self.QtLibrary.tabWidget.setCurrentWidget(self.QtLibrary.tab_2)
        self.arama.setText(adi)

    def aktar_butonu(self,tablo,ad,ornek):
        ###  Örnek butonla aynı stilde "Dışa Aktar" butonu ve tabloya sağ tık menüsü  ###
        buton=panel_butonu(ornek,"Dışa Aktar",f"{ornek.objectName()}_aktar")
        buton.setParent(ornek.parentWidget())
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

    ##################################
    #####   Tab_2 Fonksiyonlar   #####
    ##################################

    def create_form_tab2(self):
        tablo=self.QtLibrary.tableWidget_2
        tablo.setColumnCount(len(LISTE_KOLONLARI))
        tablo.setRowCount(0)
        tablo_basliklari(tablo, LISTE_KOLONLARI)
        tablo.horizontalHeader().setMinimumSectionSize(48)

    def arama_kutusu_kur(self):
        ###  Tablonun üstüne arama kutusu ve sonuç sayısı (yerleşimi liste_sayfasi kurar)  ###
        ui=self.QtLibrary
        self.arama=arama_kutusu_yap(QLineEdit(ui.tab_2))
        self.arama.setPlaceholderText("Ara: kitap adı, yazar, çevirmen, tür, yayınevi, yıl, ISBN, raf, not...")
        self.arama.setClearButtonEnabled(True)
        self.arama.setStyleSheet(f'font-size: {tema.YAZI.alt_baslik}px; padding: 2px 8px;')
        self.arama_sonuc=QLabel(ui.tab_2)
        self.arama.textChanged.connect(self.listele)

    def listele(self):
        sorgu=self.arama.text().strip()
        kitaplar=kitap_ara(sorgu)
        satirlar, renkler=durum_ekle(kitaplar)
        tabloya_yaz(self.QtLibrary.tableWidget_2, satirlar, renkler=renkler)
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
        basliklar={1:"Türlere göre",2:"Yazarlara göre",3:"Yayınevlerine göre",4:"Basım yıllarına göre"}
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
            baslik_cubugu.setSectionResizeMode(1,QHeaderView.Fixed)
            tablo.setColumnWidth(1,170)                          # Adet: oran çubuğu ve sayı
            if not isinstance(tablo.itemDelegateForColumn(1),OranCubugu):
                tablo.setItemDelegateForColumn(1,OranCubugu(tablo))
            kayit=list(rapor(kolon,adet).items())
            if kolon=='Yili':
                kayit.sort(key=lambda k: (not str(k[0]).isdigit(), str(k[0])))   # yıllar sırayla, belirtilmemiş en sonda
            tabloya_yaz(tablo, kayit)
            for r in range(tablo.rowCount()):
                tablo.item(r,0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)   # yıllar da adlar gibi sola yaslı
            tablo.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        if hasattr(self,"grafikler"):
            self.grafikler.yenile()
