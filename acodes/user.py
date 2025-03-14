# from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from bforms.user_py import Ui_MainWindow
from database.dbframe import df_user_list,df_user_query
from database.dbbase import user_ekle
from bforms.onay import onay
import re


class User(QMainWindow):
    def __init__(self):
        super().__init__()
        self.QtUser = Ui_MainWindow()
        self.QtUser.setupUi(self)
        self.dur_msj=3000
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.cmb_yetki()



        self.QtUser.lineEdit_kullanici_adi.editingFinished.connect(self.chk_kullanici_adi)
        self.QtUser.lineEdit_sifre.editingFinished.connect(self.chk_sifre)
        self.QtUser.lineEdit_adi_soyadi.editingFinished.connect(self.chk_adi_soyadi)
        self.QtUser.lineEdit_telefon.editingFinished.connect(self.chk_telefon)
        self.QtUser.lineEdit_mail.editingFinished.connect(self.chk_mail)

        self.QtUser.pushButton_cikis.clicked.connect(self.user_exit)
        self.QtUser.pushButton_kaydet.clicked.connect(self.save_user)

    def user_exit(self):
        self.clear_form()
        self.close()

    def chk_kullanici_adi(self):
        if df_user_query('kullanici',self.QtUser.lineEdit_kullanici_adi.text()):
            self.QtUser.lineEdit_kullanici_adi.clear()
            QMessageBox.information(self,"Uyarı!","Kullanıcı adı kullanılmaktadır!")
            self.QtUser.statusbar.showMessage("Kullanıcı adı kullanılmaktadır. Lütfen yeni bir kayıt deneyin",self.dur_msj) 
        else:pass

    def chk_sifre(self):
        if df_user_query('sifre',self.QtUser.lineEdit_sifre.text()):
            QMessageBox.information(self,"Uyarı!","Şifre kullanılmaktadır!")
            self.QtUser.statusbar.showMessage("Şifre kullanılmaktadır. Lütfen yeni bir şifre deneyin",self.dur_msj)   
            self.QtUser.lineEdit_sifre.clear()
        else:pass   

    def chk_adi_soyadi(self):
        if df_user_query('adi_soyadi',self.QtUser.lineEdit_adi_soyadi.text()):
            cvb=onay('Bu adda bir kullanıcı var. Devam etmek İstiyor musun?')
            if cvb==QMessageBox.No:
                self.QtUser.statusbar.showMessage("Lütfen yeni bir isim giriniz",self.dur_msj)   
                self.QtUser.lineEdit_adi_soyadi.clear()
            else:pass
        else:pass      

    def chk_telefon(self):
        txt=(self.QtUser.lineEdit_telefon.text())
        if not txt.isdigit():
            QMessageBox.information(self,"Uyarı!", "Telefon numarası olarak rakam girin!")
        elif len(txt) != 10:
            QMessageBox.information(self,"Uyarı!", "Telefon numarası eksik. Kontrol edin!")
        else:
            pass

    def chk_mail(self):
        mail=self.QtUser.lineEdit_mail.text()
        if '@' not in  mail:
            QMessageBox.information(self,"Uyarı!","Uygun mail adresi girilmedi.Kontrol edin!")
        else:
            if len((mail.split("@")[1]))==0:
                QMessageBox.information(self,"Uyarı!","Mail domain kısmını kontrol edin!")
            else:
                snc=((((mail.split("@"))[1]).split(".")))
                if  len(snc)==0 or  len(snc)>2:
                    QMessageBox.information(self,"Uyarı!","Mail domain kısmını kontrol edin!")
                else:
                    pass

    def save_user(self):
        kayit=[]      
        kayit.append(self.QtUser.lineEdit_kullanici_adi.text())       
        kayit.append(self.QtUser.lineEdit_sifre.text())
        kayit.append(self.QtUser.lineEdit_adi_soyadi.text())
        kayit.append(self.QtUser.lineEdit_telefon.text())
        kayit.append(self.QtUser.lineEdit_mail.text())
        if self.QtUser.comboBox_yetki.currentText()=="Yetki Seçin...":
            self.QtUser.statusbar.showMessage("Yetki Seçin",self.dur_msj)
        else:
            kayit.append(self.QtUser.comboBox_yetki.currentText())
        cvb=onay(f"{kayit[0]} kaydı yapılsın mı?")
        if cvb==QMessageBox.Yes:   
            print(kayit)
            self.clear_form()
        else:pass

    def cmb_yetki(self):
        cmb=["Yetki Seçin...","admin","guest"]
        self.QtUser.comboBox_yetki.addItems(cmb)

    def clear_form(self):
        self.QtUser.lineEdit_kullanici_adi.clear()       
        self.QtUser.lineEdit_sifre.clear()
        self.QtUser.lineEdit_adi_soyadi.clear()
        self.QtUser.lineEdit_telefon.clear()
        self.QtUser.lineEdit_mail.clear()
        self.QtUser.comboBox_yetki.setCurrentIndex(0)

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