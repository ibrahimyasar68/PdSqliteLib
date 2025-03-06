from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
# from PyQt5 import QtWidgets
from bforms.login_py import Ui_MainWindow
from acodes.library import Library
from database.dbframe import df_user_list, df_passw_list


class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.QtLogin = Ui_MainWindow()
        self.QtLogin.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)   
        self.library=Library()
       

        self.QtLogin.pushButton_giris.clicked.connect(self.giris)
  



    def giris(self):

        # ad=str(f"{self.QtLogin.lineEdit_kullanci_adi.text()}")
        # sifre=str(f"{self.QtLogin.lineEdit_parola.text()}")
               
        # kullanıcılar=df_user_list()  
        # sifreler=df_passw_list()

        # if ad=="" or sifre=="":
        #     self.QtMainEkran.statusBar.showMessage("Kullanıcı adı ve parola bilgilerini giriniz!")
        # else:
        #     if (ad not in kullanıcılar) and (sifre not in sifreler): 
        #         self.QtMainEkran.statusBar.showMessage("Kullanıcı adı ve parola yanlış!")
        #     else:           
        #         if (ad not in kullanıcılar) :
        #             self.QtMainEkran.statusBar.showMessage("Kullanıcı adı yanlış!")
        #         else:            
        #             if (sifre not in sifreler):
        #                 self.QtMainEkran.statusBar.showMessage("Şifre yanlış!")
        #             else: 
                        self.library.showFullScreen()                   
        #                 self.library.QtLibEkran.tabWidget.setEnabled(True)
        #                 self.library.QtLibEkran.verticalLayout.setEnabled(True)  
        #                 self.library.QtLibEkran.centralwidget.setEnabled(True)
        #                 # self.siyah.showFullScreen()     
                        self.close()                 


        
     
   


# Uygulamanın sürekli çalışması
if __name__=="__main__":
    app=QApplication([])
    pencere = Login()
    pencere.show()
    app.exec_()
    