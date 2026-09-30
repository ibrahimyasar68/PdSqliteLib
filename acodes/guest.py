from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from bforms.guest_py import Ui_MainWindow
from acodes.ortak import OrtakSekmeler
from acodes.kitaplarim import Kitaplarim
from acodes.ayarlar import Ayarlar
from database.dbframe import kullanici_bilgisi


## Guest paneli: Giriş, Kitap Listesi, Filtre ve İstatistik sekmeleri (salt okunur)
class Guest(OrtakSekmeler, QMainWindow):
    oturum_kapandi = pyqtSignal()
    PENCERE_BASLIGI = "Yaşar Kütüphanesi - Üye Paneli"

    def __init__(self):
        super().__init__()
        self.QtLibrary = Ui_MainWindow()
        self.QtLibrary.setupUi(self)
        self.QtLibrary.tabWidget.setCurrentIndex(0)
        self.dur_msj=2000
        self.aktif_kullanici=None
        self.ortak_sekmeleri_kur()

        ###  Kitaplarım: üyenin elindeki ve daha önce aldığı kitaplar  ###
        self.kitaplarim=Kitaplarim()
        self.QtLibrary.tabWidget.addTab(self.kitaplarim,"Kitaplarım")

        ###  Ayarlar: hesap bilgileri ve şifre değiştirme  ###
        self.ayarlar=Ayarlar([("Hesabım", [("Şifremi Değiştir", self.sifremi_degistir, "Kendi şifrenizi değiştirin")],
                               self.hesap_bilgisi)])
        self.QtLibrary.tabWidget.addTab(self.ayarlar,"Ayarlar")
        self.QtLibrary.tabWidget.currentChanged.connect(self.sekme_degisti)

    def user_name(self,name):
        super().user_name(name)
        self.ayarlar.yenile()
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
