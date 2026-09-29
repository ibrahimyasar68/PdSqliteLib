from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from bforms.guest_py import Ui_MainWindow
from acodes.ortak import OrtakSekmeler
from acodes.kullanici_yonetimi import SifreDegistir, panel_butonu
from acodes.kitaplarim import Kitaplarim


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

        ###  Tab_1: kendi şifresini değiştirme  ###
        ornek=self.QtLibrary.pushButton_1_cikis
        self.btn_sifre=panel_butonu(ornek,"Şifremi Değiştir","pushButton_1_sifre")
        self.QtLibrary.verticalLayout.insertWidget(0,self.btn_sifre)
        self.btn_sifre.clicked.connect(self.sifremi_degistir)

        ###  Kitaplarım: üyenin elindeki ve daha önce aldığı kitaplar  ###
        self.kitaplarim=Kitaplarim()
        self.QtLibrary.tabWidget.addTab(self.kitaplarim,"Kitaplarım")
        self.QtLibrary.tabWidget.currentChanged.connect(self.sekme_degisti)

    def user_name(self,name):
        super().user_name(name)
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

    def sifremi_degistir(self):
        SifreDegistir(self.aktif_kullanici, eski_sor=True, parent=self).exec_()


if __name__=="__main__":
    app=QApplication([])
    pencere = Guest()
    pencere.show()
    app.exec_()
