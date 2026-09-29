from PyQt5.QtWidgets import QApplication, QListView, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from bforms.user_py import Ui_MainWindow
from database.dbframe import df_user_query
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
        self.QtUser.label_2.setText("Y E N İ   K U L L A N I C I")
        # Mac: tam ekran panelin üstünde açılınca ekrana yayılmasın
        self.setFixedSize(900,680)
        self.move(240,20)
        # Mac'te yetki kutusu saydam kalıp koyu arka planda görünmüyordu
        self.QtUser.comboBox_yetki.setFixedSize(300,30)
        self.QtUser.comboBox_yetki.setView(QListView())  # Mac'in yerel listesi seçenekleri kesiyordu
        self.QtUser.comboBox_yetki.setStyleSheet(
            'QComboBox { font: 11pt "Verdana"; color: black; background-color: rgba(255,255,255,220);'
            ' border-radius: 6px; padding-left: 4px; }'
            'QComboBox QAbstractItemView { background-color: white; color: black;'
            ' selection-background-color: rgb(80,140,240); selection-color: white; }'
            'QComboBox QAbstractItemView::item { min-height: 26px; padding-left: 4px; }')

        self.cmb_yetki()

        self.QtUser.lineEdit_kullanici_adi.editingFinished.connect(self.chk_kullanici_adi)
        self.QtUser.lineEdit_sifre.editingFinished.connect(self.chk_sifre)
        self.QtUser.lineEdit_adi_soyadi.editingFinished.connect(self.chk_adi_soyadi)
        self.QtUser.lineEdit_telefon.editingFinished.connect(self.chk_telefon)
        self.QtUser.lineEdit_mail.editingFinished.connect(self.chk_mail)

        self.QtUser.pushButton_cikis.clicked.connect(self.user_exit)
        self.QtUser.pushButton_kaydet.clicked.connect(self.save_user)
        self.QtUser.pushButton_temizle.clicked.connect(self.clear_form)

    def user_exit(self):
        self.clear_form()
        self.close()

    def chk_kullanici_adi(self):
        if df_user_query('kullanici',self.QtUser.lineEdit_kullanici_adi.text()):
            self.QtUser.lineEdit_kullanici_adi.clear()
            QMessageBox.information(self,"Uyarı!","Kullanıcı adı kullanılmaktadır!")
            self.QtUser.statusbar.showMessage("Kullanıcı adı kullanılmaktadır. Lütfen yeni bir kayıt deneyin",self.dur_msj)

    def chk_sifre(self):
        if  not (self.QtUser.lineEdit_kullanici_adi.text()):
            QMessageBox.information(self,"Uyarı!","Önce kullanıcı adı girilmelidir!")
            self.QtUser.lineEdit_sifre.clear()

    def chk_adi_soyadi(self):
        if not self.QtUser.lineEdit_sifre.text():
            QMessageBox.information(self,"Uyarı!","Önce kullanıcı adı ve şifre girilmelidir")
            self.QtUser.lineEdit_adi_soyadi.clear()
        else:
            if df_user_query('adi_soyadi',self.QtUser.lineEdit_adi_soyadi.text()):
                cvb=onay('Bu adda bir kullanıcı var. Devam etmek İstiyor musun?')
                if cvb==QMessageBox.No:
                    self.QtUser.statusbar.showMessage("Lütfen yeni bir isim giriniz",self.dur_msj)
                    self.QtUser.lineEdit_adi_soyadi.clear()

    def chk_telefon(self):
        tel=(self.QtUser.lineEdit_telefon.text())
        pattern=r"\d{10}"
        if not re.fullmatch(pattern,tel):
            QMessageBox.information(self,"Uyarı!","Uygun telefon numarası girilmedi.Kontrol edin!")
            self.QtUser.lineEdit_telefon.clear()

    def chk_mail(self):
        mail=self.QtUser.lineEdit_mail.text()
        pattern=r"[\w.+-]+@[\w-]+(\.[\w-]+)*\.[a-zA-Z]{2,}"
        if not re.fullmatch(pattern,mail):
            QMessageBox.information(self,"Uyarı!","Uygun mail adresi girilmedi.Kontrol edin!")
            self.QtUser.lineEdit_mail.clear()

    def save_user(self):
        if self.QtUser.comboBox_yetki.currentText()=="Yetki Seçin...":
            QMessageBox.information(self,"Uyarı!","Kayıt oluşturmak için yetki seçimini belirtin!")
            self.QtUser.comboBox_yetki.setCurrentIndex(0)
        else:
            if not self.QtUser.lineEdit_kullanici_adi.text() or not self.QtUser.lineEdit_sifre.text() or not self.QtUser.lineEdit_adi_soyadi.text():
                QMessageBox.information(self,"Uyarı!","Kullanıcı Adı, Şifre ve Adı Soyadı boş olamaz!")
            else:
                kayit=[]
                kayit.append(self.QtUser.lineEdit_kullanici_adi.text())
                kayit.append(self.QtUser.lineEdit_sifre.text())
                kayit.append(self.QtUser.lineEdit_adi_soyadi.text())
                kayit.append(self.QtUser.lineEdit_telefon.text())
                kayit.append(self.QtUser.lineEdit_mail.text())
                kayit.append(self.QtUser.comboBox_yetki.currentText())
                cvb=onay(f"{kayit[0]} kaydı yapılsın mı?")
                if cvb==QMessageBox.Yes:
                    user_ekle(kayit)
                    self.clear_form()

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
