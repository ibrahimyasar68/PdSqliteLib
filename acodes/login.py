from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from acodes.library import Library
from acodes.guest import Guest
from bforms.login_py import Ui_MainWindow
from database.dbframe import df_user_list,authority,df_pasw_query_by_name


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
  



    def giris(self):

        ad=str(f"{self.QtLogin.lineEdit_kullanci_adi.text()}")
        sifre=str(f"{self.QtLogin.lineEdit_parola.text()}")
               
        kullanicilar=df_user_list('kullanici')  
        sifreler=df_user_list('sifre')

        if ad=="" or sifre=="":
            self.QtLogin.statusbar.showMessage("Kullanıcı adı ve parola bilgilerini giriniz!",self.msj_tm)
           
        else:
            if (ad not in kullanicilar) and (sifre not in sifreler): 
                self.QtLogin.statusbar.showMessage("Kullanıcı adı ve parola yanlış!", self.msj_tm)
            else:           
                if (ad not in kullanicilar):
                    self.QtLogin.statusbar.showMessage("Kullanıcı adı yanlış!", self.msj_tm)
                else:            
                    if df_pasw_query_by_name(ad,sifre):
                        self.QtLogin.statusbar.showMessage("Şifre yanlış!", self.msj_tm)
                    else:
                        if authority(ad)=='admin':                                            
                            self.library.showFullScreen()    
                            self.close()
                        elif authority(ad)=='guest': 
                            self.guest.showFullScreen()
                            self.close()
                        else:
                            self.QtLogin.statusbar.showMessage("Yetkiniz yok!", self.msj_tm)
     
   


# Uygulamanın sürekli çalışması
if __name__=="__main__":
    app=QApplication([])
    pencere = Login()
    pencere.show()
    app.exec_()
    