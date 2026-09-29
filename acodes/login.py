from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from acodes.library import Library
from acodes.guest import Guest
from bforms.login_py import Ui_MainWindow
from database.dbframe import giris_kontrol


class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.QtLogin = Ui_MainWindow()
        self.QtLogin.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint) 
        self.library=Library()
        self.guest=Guest()
        self.msj_tm=2000 

        
        self.QtLogin.pushButton_giris.clicked.connect(self.giris)
        # Üye kaydı sadece giriş yapıldıktan sonra admin panelinden yapılır
        self.QtLogin.pushButton_yeni_kayit.hide()
        self.QtLogin.pushButton_cikis.clicked.connect(self.cikis)

     

    def giris(self):

        ad=str(f"{self.QtLogin.lineEdit_kullanci_adi.text()}")
        sifre=str(f"{self.QtLogin.lineEdit_parola.text()}")
               
        if ad=="" or sifre=="":
            self.QtLogin.statusbar.showMessage("Kullanıcı adı ve parola bilgilerini giriniz!",self.msj_tm)
        else:
            yetki=giris_kontrol(ad,sifre)
            if yetki is None:
                # Hangisinin yanlış olduğu söylenmez (kullanıcı adı tahminini zorlaştırır)
                self.QtLogin.statusbar.showMessage("Kullanıcı adı veya parola yanlış!", self.msj_tm)
            elif yetki=='admin':
                self.library.showFullScreen()
                self.library.user_name(ad)
                self.close()
            elif yetki=='guest':
                self.guest.showFullScreen()
                self.guest.user_name(ad)
                self.close()
            else:
                self.QtLogin.statusbar.showMessage("Yetkiniz yok!", self.msj_tm)

    def cikis(self):
        self.close()




# Uygulamanın sürekli çalışması
if __name__=="__main__":
    app=QApplication([])
    pencere = Login()
    pencere.show()
    app.exec_()
    