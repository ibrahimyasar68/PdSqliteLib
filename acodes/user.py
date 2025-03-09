# from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from bforms.user_py import Ui_MainWindow
from database.dbframe import df_user_list
from database.dbbase import user_ekle
from bforms.onay import onay


class User(QMainWindow):
    def __init__(self):
        super().__init__()
        self.QtUser = Ui_MainWindow()
        self.QtUser.setupUi(self)
        self.dur_msj=2000
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.cmb_yetki()
        self.QtUser.pushButton_cikis.clicked.connect(self.user_exit)
        self.QtUser.pushButton_kaydet.clicked.connect(self.save_user)

    def user_exit(self):
        self.close()

    def save_user(self):
        kayit=[]
        if (self.QtUser.lineEdit_kullanici_adi.text()) in df_user_list('kullanici'):
            self.QtUser.statusbar.showMessage("Kullanıcı adı kullanılmaktadır. Lütfen yeni bir kayıt deneyin",self.dur_msj)
            self.QtUser.lineEdit_kullanici_adi.clear()
        else:
            kayit.append(self.QtUser.lineEdit_kullanici_adi.text())
        if (self.QtUser.lineEdit_sifre.text()) in df_user_list('sifre'):
            self.QtUser.statusbar.showMessage("Girilen şifre kullamınmaktadır. lütfen yeni bir şifre belirletiniz", self.dur_msj)
            self.QtUser.lineEdit_sifre.clear()
        else:
            kayit.append(self.QtUser.lineEdit_sifre.text())
        kayit.append(self.QtUser.lineEdit_adi_soyadi.text())
        kayit.append(self.QtUser.lineEdit_telefon.text())
        kayit.append(self.QtUser.lineEdit_mail.text())
        if self.QtUser.comboBox_yetki.currentText()=="Yetki Seçin...":
            self.QtUser.statusbar.showMessage("Yetki Seçin",self.dur_msj)
        else:
            kayit.append(self.QtUser.comboBox_yetki.currentText())
        print(kayit)


    def cmb_yetki(self):
        cmb=["Yetki Seçin...","admin","guest"]
        self.QtUser.comboBox_yetki.addItems(cmb)
        
# Uygulamanın sürekli çalışması
if __name__=="__main__":
    app=QApplication([])
    pencere = User()
    pencere.show()
    app.exec_()

# # Uygulamanın sürekli çalışması
# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = Ui_MainWindow()
#     ui.setupUi(MainWindow)
#     MainWindow.showMaximized()
#     sys.exit(app.exec_())    