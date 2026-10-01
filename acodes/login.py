from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsDropShadowEffect, QLabel, QLineEdit, QMainWindow, QSizePolicy, QVBoxLayout,
                             QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import sys
from acodes.library import Library
from acodes.guest import Guest
from acodes import ikonlar, kilavuz, tema
from bforms.login_py import Ui_MainWindow
from database.dbframe import giris_kontrol


def panel_goster(panel):
    # Mac'te tam ekran ayrı bir masaüstü alanı açar, pencere küçültülemez; büyütülmüş pencere kullanılır
    if sys.platform=="darwin":
        panel.showMaximized()
    else:
        panel.showFullScreen()


# Sağ taraf: geçişli zemin yerine beyaz kart; soldaki fotoğraf ve başlık korunur
GIRIS_STILI = f"""
#label_2 {{ background-color: {tema.KART}; border-top-right-radius: 16px; border-bottom-right-radius: 16px; }}
#label_5 {{ color: white; font-family: "{tema.BASLIK_YAZISI}"; font-size: 48px; font-style: normal; }}
#giris_karti QLabel {{ color: #334155; font-size: 13px; font-weight: bold; }}
#giris_karti QLabel#giris_baslik {{ color: {tema.METIN}; font-size: 26px; font-weight: bold; }}
#giris_karti QLabel#giris_alt {{ color: {tema.IKINCIL_METIN}; font-size: 13px; font-weight: normal; }}
#giris_karti QLineEdit {{ font-size: 15px; padding: 8px 10px; border-radius: 8px; min-height: 22px; }}
#giris_karti QLabel#giris_mesaj {{ color: {tema.TEHLIKE}; font-weight: normal; }}
#giris_karti QLabel#giris_mesaj[tur="bilgi"] {{ color: #15803D; }}
#giris_karti QLabel#giris_imza {{ color: {tema.IKINCIL_METIN}; font-size: 12px; font-weight: normal; }}
#pushButton_giris {{ font-size: 16px; font-weight: bold; padding: 10px; border-radius: 8px; }}
#pushButton_cikis {{ background-color: #F1F5F9; border: 1px solid {tema.KENAR}; border-radius: 22px; }}
#pushButton_cikis:hover {{ background-color: {tema.TEHLIKE}; border-color: {tema.TEHLIKE}; }}
"""


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
        self._surukle=None
        self.tasarim()

        self.QtLogin.pushButton_giris.clicked.connect(self.giris)
        self.QtLogin.lineEdit_parola.returnPressed.connect(self.giris)
        self.QtLogin.lineEdit_kullanci_adi.returnPressed.connect(self.QtLogin.lineEdit_parola.setFocus)
        # Üye kaydı sadece giriş yapıldıktan sonra admin panelinden yapılır
        self.QtLogin.pushButton_yeni_kayit.hide()
        self.QtLogin.pushButton_cikis.setToolTip("Programdan çık")
        self.QtLogin.pushButton_cikis.clicked.connect(self.close)

    def tasarim(self):
        ###  Sağ tarafa beyaz giriş kartı: başlık, etiketli alanlar, kart içinde mesaj, tam genişlikte buton  ###
        ui=self.QtLogin
        for eski in (ui.label_2, ui.label_5, ui.formFrame, ui.label_3, ui.label_4, ui.pushButton_giris, ui.pushButton_cikis):
            eski.setStyleSheet("")
        ui.formFrame.hide()
        # Başlık fotoğrafın genişliğinde ve ortada (gömülü el yazısı .ui'daki dar kutuya sığmıyordu)
        ui.label_5.setGeometry(18,70,400,150)
        ui.label_5.setAlignment(Qt.AlignCenter)
        golge=QGraphicsDropShadowEffect(ui.label_5)
        golge.setBlurRadius(16)
        golge.setOffset(0,2)
        golge.setColor(QColor(0,0,0,180))
        ui.label_5.setGraphicsEffect(golge)
        ui.statusbar.hide()                       # mesajlar kartın içinde gösterilir

        kart=QWidget(ui.widget)
        kart.setObjectName("giris_karti")
        kart.setGeometry(460,120,320,430)
        duzen=QVBoxLayout(kart)
        duzen.setSpacing(8)
        alt=QLabel("Devam etmek için hesabınıza giriş yapın.",objectName="giris_alt")
        alt.setWordWrap(True)
        self.mesaj=QLabel("",objectName="giris_mesaj")
        self.mesaj.setWordWrap(True)
        self.mesaj.setMinimumHeight(20)
        for alan,ipucu in ((ui.lineEdit_kullanci_adi,"Kullanıcı adınız"),(ui.lineEdit_parola,"Parolanız")):
            alan.setParent(kart)
            alan.setPlaceholderText(ipucu)
            alan.setMinimumWidth(0)
            alan.setMaximumWidth(16777215)
            alan.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            alan.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        ui.lineEdit_parola.setEchoMode(QLineEdit.Password)
        ui.pushButton_giris.setParent(kart)
        ui.pushButton_giris.setMinimumSize(0,46)
        ui.pushButton_giris.setMaximumSize(16777215,46)
        ui.pushButton_giris.setCursor(Qt.PointingHandCursor)
        duzen.addWidget(QLabel("Giriş Yap",objectName="giris_baslik"))
        duzen.addWidget(alt)
        duzen.addSpacing(18)
        duzen.addWidget(QLabel("Kullanıcı adı"))
        duzen.addWidget(ui.lineEdit_kullanci_adi)
        duzen.addSpacing(6)
        duzen.addWidget(QLabel("Parola"))
        duzen.addWidget(ui.lineEdit_parola)
        duzen.addWidget(self.mesaj)
        duzen.addWidget(ui.pushButton_giris)
        duzen.addStretch()
        self.imza=QLabel(kilavuz.IMZA,objectName="giris_imza")
        self.imza.setAlignment(Qt.AlignRight)
        duzen.addWidget(self.imza)

        # Parolayı göster/gizle
        self.goster=QAction(ikonlar.ikon("goz",ikonlar.SEKME_RENGI),"Parolayı göster",ui.lineEdit_parola)
        self.goster.triggered.connect(self.parola_goster_gizle)
        ui.lineEdit_parola.addAction(self.goster,QLineEdit.TrailingPosition)

        ui.pushButton_giris.setIcon(ikonlar.ikon("ok_sag"))
        ui.pushButton_cikis.setGeometry(752,574,44,44)
        ui.pushButton_cikis.setIcon(ikonlar.ikon("guc",ikonlar.SEKME_RENGI))
        ui.pushButton_cikis.setIconSize(ui.pushButton_cikis.size()*0.45)
        ui.pushButton_cikis.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(tema.qss()+GIRIS_STILI)

    def parola_goster_gizle(self):
        alan=self.QtLogin.lineEdit_parola
        gizli=alan.echoMode()==QLineEdit.Password
        alan.setEchoMode(QLineEdit.Normal if gizli else QLineEdit.Password)
        self.goster.setIcon(ikonlar.ikon("goz_kapali" if gizli else "goz",ikonlar.SEKME_RENGI))
        self.goster.setText("Parolayı gizle" if gizli else "Parolayı göster")

    def mesaj_goster(self,metin,tur="hata"):
        self.mesaj.setText(metin)
        self.mesaj.setProperty("tur",tur)
        self.mesaj.style().unpolish(self.mesaj)   # tür değişince rengi yeniden uygula
        self.mesaj.style().polish(self.mesaj)

    # Çerçevesiz pencere fareyle sürüklenerek taşınabilir
    def mousePressEvent(self,olay):
        if olay.button()==Qt.LeftButton:
            self._surukle=olay.globalPos()-self.frameGeometry().topLeft()

    def mouseMoveEvent(self,olay):
        if self._surukle is not None and olay.buttons() & Qt.LeftButton:
            self.move(olay.globalPos()-self._surukle)

    def mouseReleaseEvent(self,olay):
        self._surukle=None

    def giris(self):
        ad=self.QtLogin.lineEdit_kullanci_adi.text()
        sifre=self.QtLogin.lineEdit_parola.text()

        if ad=="" or sifre=="":
            self.mesaj_goster("Kullanıcı adı ve parola bilgilerini giriniz!")
        else:
            yetki=giris_kontrol(ad,sifre)
            if yetki is None:
                # Hangisinin yanlış olduğu söylenmez (kullanıcı adı tahminini zorlaştırır)
                self.mesaj_goster("Kullanıcı adı veya parola yanlış!")
                self.QtLogin.lineEdit_parola.selectAll()
                self.QtLogin.lineEdit_parola.setFocus()
            elif yetki in ('admin','guest'):
                # Her oturumda panel sıfırdan oluşturulur; önceki kullanıcıdan bir şey kalmaz
                self.mesaj_goster("")
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
                self.mesaj_goster("Yetkiniz yok!")

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
        self.mesaj_goster("Oturum kapatıldı.","bilgi")


# Uygulamanın sürekli çalışması
if __name__=="__main__":
    app=QApplication([])
    pencere = Login()
    pencere.show()
    app.exec_()
