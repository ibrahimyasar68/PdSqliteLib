## Panel iskeleti: yönetici (Library) ve üye (Guest) panellerinin ortak çatısı ##
# Solda kenar menüsü, sağda menüden seçilen sayfa. Her panel sayfalarını Sayfa listesi olarak verir
# (sayfalari_kur); menü düğmeleri, ikonlar, Ctrl+1..9 kısayolları ve hızlı aramadaki bölümler bu listeden üretilir.
# Kitap Listesi, Filtre ve İstatistik sayfaları iki panelde ortaktır ve burada kurulur.

from dataclasses import dataclass
from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QPushButton, QStatusBar, QTabWidget, QWidget

from acodes import arka_plan, bildirim, ikonlar, kisayollar, tema
from acodes.disa_aktar import disa_aktar, sag_tik_menusu
from acodes.filtre_paneli import FiltrePaneli
from acodes.istatistik import Istatistik
from acodes.kisayollar import kisayol, metin as kisayol_metni
from acodes.kitap_listesi import KitapListesi
from acodes.komut_paleti import KomutPaleti, eslesir
from acodes.kullanici_yonetimi import SifreDegistir
from acodes.yan_menu import YanMenu, alt_sekmeli_sayfa
from database.kitaplar import kitap_ara, kitap_durumlari
from database.metin import katla


@dataclass
class Sayfa:
    anahtar: str                                # ikonlar.SEKME_IKONLARI anahtarı
    baslik: str                                 # menüdeki ad
    bilesen: QWidget
    acilinca: Optional[Callable[[], None]] = None   # sayfa her açıldığında (ör. güncel listeyi göster)


class Panel(QMainWindow):
    oturum_kapandi = Signal()
    PENCERE_BASLIGI = ""
    ROL = ""

    def __init__(self):
        super().__init__()
        self.aktif_kullanici=None
        self.dur_msj=2000
        self.alt_sekmeler={}            # {menü sayfası: alt sayfaların QTabWidget'ı}
        self.resize(1518,744)
        self.setMinimumSize(1300,720)
        self.setStatusBar(QStatusBar())
        self.bildirim=bildirim.baglan(self,self.statusBar())   # mesajlar kısa süreli bildirim olarak

        # Çıkış butonu oturumu kapatıp giriş ekranına döner (programdan çıkış giriş ekranındadır); menüye taşınır
        self.btn_cikis=QPushButton("Oturumu Kapat",objectName="oturum_kapat")
        self.btn_cikis.setToolTip("Oturumu kapatıp giriş ekranına dön")
        self.btn_cikis.clicked.connect(self.oturumu_kapat)

        ###  Ortak sayfalar ve panele özgü sayfalar  ###
        self.liste=KitapListesi()
        self.filtre=FiltrePaneli(mesaj=lambda metin,tur=None: self.bildirim.mesaj(metin,tur,self.dur_msj))
        self.filtre.btn_aktar.clicked.connect(lambda: disa_aktar(self,self.filtre.tablo,"Filtre"))
        sag_tik_menusu(self,self.filtre.tablo,"Filtre")
        self.istatistik=Istatistik()
        self.alt_sekmeler[self.istatistik]=self.istatistik.sekmeler
        self.sayfalar=self.sayfalari_kur()

        ###  Orta alan: solda menü, sağda sayfalar (sekme çubuğu gizli, menü seçer)  ###
        self.sekmeler=QTabWidget(objectName="sayfalar")
        self.sekmeler.setStyleSheet("QTabWidget#sayfalar::pane { border: none; }")
        for sayfa in self.sayfalar:
            # Kendi sınıfı olan sayfalar da (KitapListesi, Istatistik ...) temadaki sayfa zeminini çizsin
            sayfa.bilesen.setAttribute(Qt.WA_StyledBackground,True)
            self.sekmeler.addTab(sayfa.bilesen,sayfa.baslik)
        self.sayfalar[0].bilesen.setObjectName("ana_sayfa")   # arka plan fotoğrafı bu sayfada görünür
        orta=QWidget(objectName="orta_alan")
        self.setCentralWidget(orta)
        self.yan_menu=YanMenu(self.sekmeler,{s.bilesen: s.anahtar for s in self.sayfalar},self.btn_cikis)
        yatay=QHBoxLayout(orta)
        yatay.setContentsMargins(15,15,15,15)
        yatay.setSpacing(12)
        yatay.addWidget(self.yan_menu)
        yatay.addWidget(self.sekmeler,1)
        tema.uygula(self)
        self.arka_plan=arka_plan.uygula(self)       # yaprak fotoğrafı Giriş sayfasının zemininde
        ikonlar.sekmelere_uygula(self.sekmeler,{s.bilesen: s.anahtar for s in self.sayfalar})
        self.sekmeler.currentChanged.connect(self._sayfa_acildi)

        ###  Kısayollar: Ctrl+1..9 menü, Ctrl+F arama, Ctrl+K hızlı arama  ###
        kisayollar.panele_kur(self,self.sekmeler,self.liste,self.liste.arama)
        self.palet=KomutPaleti(self.komut_kaynagi,self)
        kisayol("Ctrl+K",self,self.palet.ac)
        self.yan_menu.btn_ara.clicked.connect(self.palet.ac)
        self.yan_menu.btn_ara.setToolTip(f"Kitap, üye veya bölüm arayın ({kisayol_metni('Ctrl+K')})")
        ikonlar.butonlara_uygula(self)

    def sayfalari_kur(self):
        """Menü sırasıyla [Sayfa]; ilki Giriş (ana sayfa). Alt sayfalı sayfalar için alt_sekmeli() kullanılır."""
        raise NotImplementedError

    def alt_sekmeli(self,baslik,alt_sayfalar):
        """[(ad, bileşen)]: üstte anahtarla seçilen alt sayfalardan bir menü sayfası."""
        sayfa,sekmeler=alt_sekmeli_sayfa(baslik,alt_sayfalar)
        self.alt_sekmeler[sayfa]=sekmeler
        return sayfa

    def ac(self,sayfa,alt=None):
        """Menü sayfasını (ve varsa alt sayfasını) açar."""
        self.sekmeler.setCurrentWidget(sayfa)
        if alt is not None:
            self.alt_sekmeler[sayfa].setCurrentWidget(alt)

    def _sayfa_acildi(self,i):
        acilinca=self.sayfalar[i].acilinca
        if acilinca:
            acilinca()

    def sayfa_adi(self,bilesen,ad):
        ###  Menüdeki adı değiştirir; "(N gecikmiş)" eki menüde kırmızı rozet olur  ###
        self.sekmeler.setTabText(self.sekmeler.indexOf(bilesen),ad)
        self.yan_menu.yenile()

    ##################################
    #####   Hızlı arama (Ctrl+K)   #####
    ##################################

    def komut_kaynagi(self,metin):
        gruplar=[("Bölümler",[k for k in self.bolum_komutlari() if eslesir(metin,k[0])]),
                 ("İşlemler",[k[:4] for k in self.islem_komutlari() if eslesir(metin,k[0],k[1],k[4])])]
        if len(katla(metin).strip())>=2:      # tek harfle yüzlerce kitap listelenmesin
            gruplar.append(("Kitaplar",self.kitap_komutlari(metin)))
            gruplar+=self.ek_arama_gruplari(metin)
        return gruplar

    def bolum_komutlari(self):
        komutlar=[]
        for i,sayfa in enumerate(self.sayfalar):
            ad=self.yan_menu.ogeler[i][0].ad
            kisa=kisayol_metni(f"Ctrl+{i+1}") if i<9 else ""
            ikon=ikonlar.SEKME_IKONLARI[sayfa.anahtar]
            komutlar.append((ad,kisa,ikon,lambda s=sayfa.bilesen: self.ac(s)))
        return komutlar

    def islem_komutlari(self):
        """[(ad, açıklama, ikon, işlev, aramada eşleşecek ek kelimeler)] — panele göre (Library / Guest) genişler."""
        return [("Grafikler","İstatistik","grafik",lambda: self.ac(self.istatistik,self.istatistik.sekmeler.widget(1)),"grafik çizelge"),
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
        self.ac(self.liste)
        self.liste.arama.setText(adi)

    ##################################
    #####   Oturum   #####
    ##################################

    def oturumu_kapat(self):
        ###  Açık alt pencereleri kapat, giriş ekranına haber ver, paneli kapat  ###
        if hasattr(self,"user"):
            self.user.close()
        self.oturum_kapandi.emit()   # giriş ekranı önce görünür olur, böylece program kapanmaz
        self.close()

    def sifremi_degistir(self):
        SifreDegistir(self.aktif_kullanici, eski_sor=True, parent=self).exec()

    def user_name(self,name):
        self.aktif_kullanici=name
        self.ana_sayfa.karsila(name,self.ROL)
        self.yan_menu.kullanici(name,self.ROL)
        self.setWindowTitle(f"{self.PENCERE_BASLIGI} - {name}")

    def tum_kitaplari_goster(self):
        self.ac(self.liste)
        self.liste.listele()
