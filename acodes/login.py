from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
import sys
from acodes.library import Library
from acodes.guest import Guest
from bforms.login_py import Ui_MainWindow
from database.dbframe import giris_kontrol


def panel_goster(panel):
    # Mac'te tam ekran ayrı bir masaüstü alanı açar, pencere küçültülemez; büyütülmüş pencere kullanılır
    if sys.platform=="darwin":
        panel.showMaximized()
    else:
        panel.showFullScreen()


class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.QtLogin = Ui_MainWindow()
        self.QtLogin.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(260,20,800,700)
        self.setWindowTitle("Yaşar Kütüphanesi - Giriş")
        self.library=None  # Paneller giriş yapılınca oluşturulur
        self.guest=None
        self.msj_tm=2000

        self.QtLogin.pushButton_giris.clicked.connect(self.giris)
        self.QtLogin.lineEdit_parola.returnPressed.connect(self.giris)
        # Üye kaydı sadece giriş yapıldıktan sonra admin panelinden yapılır
        self.QtLogin.pushButton_yeni_kayit.hide()
        self.QtLogin.pushButton_cikis.clicked.connect(self.close)

    def giris(self):
        ad=self.QtLogin.lineEdit_kullanci_adi.text()
        sifre=self.QtLogin.lineEdit_parola.text()

        if ad=="" or sifre=="":
            self.QtLogin.statusbar.showMessage("Kullanıcı adı ve parola bilgilerini giriniz!",self.msj_tm)
        else:
            yetki=giris_kontrol(ad,sifre)
            if yetki is None:
                # Hangisinin yanlış olduğu söylenmez (kullanıcı adı tahminini zorlaştırır)
                self.QtLogin.statusbar.showMessage("Kullanıcı adı veya parola yanlış!", self.msj_tm)
            elif yetki in ('admin','guest'):
                # Her oturumda panel sıfırdan oluşturulur; önceki kullanıcıdan bir şey kalmaz
                panel=Library() if yetki=='admin' else Guest()
                if yetki=='admin':
                    self.library=panel
                else:
                    self.guest=panel
                panel.user_name(ad)
                panel.oturum_kapandi.connect(self.giris_ekranina_don)
                panel_goster(panel)
                self.hide()
            else:
                self.QtLogin.statusbar.showMessage("Yetkiniz yok!", self.msj_tm)

    def giris_ekranina_don(self):
        for panel in (self.library,self.guest):
            if panel is not None:
                panel.deleteLater()
        self.library=None
        self.guest=None
        self.QtLogin.lineEdit_kullanci_adi.clear()
        self.QtLogin.lineEdit_parola.clear()
        self.show()
        self.raise_()
        self.activateWindow()
        self.QtLogin.lineEdit_kullanci_adi.setFocus()
        self.QtLogin.statusbar.showMessage("Oturum kapatıldı.", self.msj_tm)


# Uygulamanın sürekli çalışması
if __name__=="__main__":
    app=QApplication([])
    pencere = Login()
    pencere.show()
    app.exec_()
