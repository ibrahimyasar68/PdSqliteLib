from PyQt5.QtWidgets import QApplication, QMainWindow
from bforms.guest_py import Ui_MainWindow
from acodes.ortak import OrtakSekmeler


## Guest paneli: Giriş, Kitap Listesi, Filtre ve İstatistik sekmeleri (salt okunur)
class Guest(OrtakSekmeler, QMainWindow):
    def __init__(self):
        super().__init__()
        self.QtLibrary = Ui_MainWindow()
        self.QtLibrary.setupUi(self)
        self.QtLibrary.tabWidget.setCurrentIndex(0)
        self.dur_msj=2000
        self.ortak_sekmeleri_kur()


if __name__=="__main__":
    app=QApplication([])
    pencere = Guest()
    pencere.show()
    app.exec_()
