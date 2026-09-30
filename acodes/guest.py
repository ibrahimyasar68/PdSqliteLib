from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from bforms.guest_py import Ui_MainWindow
from acodes.ortak import OrtakSekmeler
from acodes.kitaplarim import Kitaplarim
from acodes.ayarlar import Ayarlar
from acodes import kilavuz
from acodes.ana_sayfa import AnaSayfa, ana_sayfayi_yerlestir
from acodes import arka_plan, bildirim, ikonlar
from database.dbframe import genel_ozet, son_eklenenler
from database.odunc import gecikme_gunu, kalan_gun_yazi, tarih_yazi, teslim_tarihi, uye_odunc
from acodes import tema
from database.dbframe import kullanici_bilgisi


## Guest paneli: Giriş, Kitap Listesi, Filtre ve İstatistik sekmeleri (salt okunur)
class Guest(OrtakSekmeler, QMainWindow):
    oturum_kapandi = pyqtSignal()
    PENCERE_BASLIGI = "Yaşar Kütüphanesi - Üye Paneli"
    ROL = "Üye"

    def __init__(self):
        super().__init__()
        self.QtLibrary = Ui_MainWindow()
        self.QtLibrary.setupUi(self)
        tema.uygula(self)   # .ui renkleri yerine tek tema
        self.arka_plan=arka_plan.uygula(self)   # yaprak fotoğrafı tüm panelin zemininde
        self.bildirim=bildirim.baglan(self,self.QtLibrary.statusbar)   # mesajlar kısa süreli bildirim olarak
        self.QtLibrary.tabWidget.setCurrentIndex(0)
        self.dur_msj=2000
        self.aktif_kullanici=None
        self.ortak_sekmeleri_kur()

        ###  Kitaplarım: üyenin elindeki ve daha önce aldığı kitaplar  ###
        self.kitaplarim=Kitaplarim()
        self.QtLibrary.tabWidget.addTab(self.kitaplarim,"Kitaplarım")

        ###  Ayarlar: hesap bilgileri ve şifre değiştirme  ###
        self.ayarlar=Ayarlar([("Hesabım", [("Şifremi Değiştir", self.sifremi_degistir, "Kendi şifrenizi değiştirin")],
                               self.hesap_bilgisi)], kilavuz=kilavuz.UYE)
        self.QtLibrary.tabWidget.addTab(self.ayarlar,"Ayarlar")

        ###  Ana sayfa özet panosu  ###
        self.ana_sayfa=AnaSayfa(
            kartlar=[("kitap","Kütüphanedeki kitap",tema.VURGU),("elimdeki","Elimdeki kitap","#0EA5E9"),
                     ("geciken","Gecikmiş",tema.TEHLIKE),("teslim","En yakın teslim","#16A34A")],
            listeler=[("elimdeki","Elimdeki kitaplar",["Kitap","Teslim Tarihi","Durum"],"Şu an elinizde ödünç kitap yok."),
                      ("son","Son eklenen kitaplar",["Adı","Yazarı"],"Henüz kitap eklenmemiş.")],
            cikis_butonu=self.QtLibrary.pushButton_1_cikis)
        ana_sayfayi_yerlestir(self.QtLibrary,self.ana_sayfa)
        k=self.ana_sayfa.kartlar
        k["kitap"].tiklanabilir(self.tum_kitaplari_goster,"Kitap listesini aç")
        for anahtar in ("elimdeki","geciken","teslim"):
            k[anahtar].tiklanabilir(lambda: self.QtLibrary.tabWidget.setCurrentWidget(self.kitaplarim),"Kitaplarım sekmesini aç")
        self.ana_sayfa_yenile()
        self.QtLibrary.tabWidget.currentChanged.connect(self.sekme_degisti)

        ###  İkonlar  ###
        ui=self.QtLibrary
        ikonlar.butonlara_uygula(self)
        ikonlar.sekmelere_uygula(ui.tabWidget,{ui.tab_1:"tab_1",ui.tab_2:"tab_2",ui.tab_4:"tab_4",ui.tab_5:"tab_5",
                                               self.kitaplarim:"kitaplarim",self.ayarlar:"ayarlar"})

    def user_name(self,name):
        super().user_name(name)
        self.ayarlar.yenile()
        self.ana_sayfa_yenile()
        if self.kitaplarim_yenile():
            self.QtLibrary.statusbar.showMessage("Teslim süresi geçmiş kitabınız var. Kitaplarım sekmesine bakın.",10000)

    def kitaplarim_yenile(self):
        sayi=self.kitaplarim.yukle(self.aktif_kullanici)
        sekme=self.QtLibrary.tabWidget.indexOf(self.kitaplarim)
        self.QtLibrary.tabWidget.setTabText(sekme, f"Kitaplarım ({sayi} gecikmiş)" if sayi else "Kitaplarım")
        return sayi

    def sekme_degisti(self):
        if self.QtLibrary.tabWidget.currentWidget() is self.kitaplarim:
            self.kitaplarim_yenile()
        elif self.QtLibrary.tabWidget.currentWidget() is self.QtLibrary.tab_1:
            self.ana_sayfa_yenile()

    def ana_sayfa_yenile(self):
        elimdeki=[(kitap,verilis) for kitap,_,verilis,durum,_ in uye_odunc(self.aktif_kullanici)
                  if durum=="out"] if self.aktif_kullanici else []
        elimdeki.sort(key=lambda e: str(teslim_tarihi(e[1]) or ""))   # teslim tarihi en yakın olan en üstte
        gecikmis={i for i,(_,verilis) in enumerate(elimdeki) if gecikme_gunu(verilis)}
        k=self.ana_sayfa.kartlar
        k["kitap"].ayarla(genel_ozet()["kitap"],"kitap listesinde aranabilir")
        k["elimdeki"].ayarla(len(elimdeki),"şu an sizde")
        k["geciken"].ayarla(len(gecikmis),"teslim süresi geçmiş" if gecikmis else "gecikmiş kitabınız yok",
                            renk=None if gecikmis else "#94A3B8")
        en_yakin=min((teslim_tarihi(v) for _,v in elimdeki if teslim_tarihi(v)),default=None)
        k["teslim"].ayarla(tarih_yazi(en_yakin) if en_yakin else "-",
                           kalan_gun_yazi(min(elimdeki,key=lambda e: teslim_tarihi(e[1]))[1]) if en_yakin else "ödünç kitabınız yok")
        self.ana_sayfa.listeler["elimdeki"].doldur(
            [[kitap,tarih_yazi(teslim_tarihi(v)),kalan_gun_yazi(v)] for kitap,v in elimdeki],vurgulu=gecikmis)
        self.ana_sayfa.listeler["son"].doldur([[adi,yazar] for _,adi,yazar in son_eklenenler()])

    def tum_kitaplari_goster(self):
        self.QtLibrary.tabWidget.setCurrentWidget(self.QtLibrary.tab_2)
        self.listele()

    def hesap_bilgisi(self):
        kayit=kullanici_bilgisi(self.aktif_kullanici) if self.aktif_kullanici else None
        if kayit is None:
            return []
        kullanici,adi_soyadi,telefon,mail,_=kayit
        return [("Kullanıcı adı",kullanici),("Adı soyadı",adi_soyadi or "-"),
                ("Telefon",telefon or "-"),("Mail",mail or "-")]


if __name__=="__main__":
    app=QApplication([])
    pencere = Guest()
    pencere.show()
    app.exec_()
