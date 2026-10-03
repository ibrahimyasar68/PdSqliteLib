from types import SimpleNamespace
from PyQt5.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit, QListView, QMainWindow, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from acodes import ikonlar, tema
from database.dbframe import df_user_query
from database.dbbase import user_ekle
from acodes.onay import onay
import re

SIFRE_EN_AZ = 6


def telefon_gecerli(tel):
    return re.fullmatch(r"\d{10}", tel) is not None


def mail_gecerli(mail):
    return re.fullmatch(r"[\w.+-]+@[\w-]+(\.[\w-]+)*\.[a-zA-Z]{2,}", mail) is not None


def sifre_hatasi(sifre, tekrar=None):
    """Şifre kurallara uymuyorsa hata mesajını, uyuyorsa None döndürür."""
    if len(sifre) < SIFRE_EN_AZ:
        return f"Şifre en az {SIFRE_EN_AZ} karakter olmalıdır!"
    if tekrar is not None and sifre != tekrar:
        return "Şifreler birbiriyle aynı değil!"
    return None


class User(QMainWindow):
    kaydedildi = pyqtSignal(str)      # kullanıcı adı: panel listeleri yeniler ve bildirim gösterir

    def __init__(self, parent=None):
        super().__init__(parent)
        if parent is not None:
            # Panelin üzerinde, ona bağlı pencere: kapanınca kalınan menüye dönülür (Mac'te tam ekran/büyütülmüş
            # panelden ayrı bir masaüstü alanına geçip siyah ekranda kalmıyordu)
            self.setWindowFlags(Qt.Dialog)
            self.setWindowModality(Qt.WindowModal)
        self.dur_msj=3000
        self.setWindowTitle("Yaşar Kütüphanesi - Yeni Kullanıcı")
        self.tasarim()

        self.cmb_yetki()

        self.QtUser.lineEdit_kullanici_adi.editingFinished.connect(self.chk_kullanici_adi)
        self.QtUser.lineEdit_sifre.editingFinished.connect(self.chk_sifre)
        self.QtUser.lineEdit_adi_soyadi.editingFinished.connect(self.chk_adi_soyadi)
        self.QtUser.lineEdit_telefon.editingFinished.connect(self.chk_telefon)
        self.QtUser.lineEdit_mail.editingFinished.connect(self.chk_mail)

        self.QtUser.pushButton_cikis.clicked.connect(self.user_exit)
        self.QtUser.pushButton_kaydet.clicked.connect(self.save_user)
        self.QtUser.pushButton_temizle.clicked.connect(self.clear_form)

    def tasarim(self):
        ###  Temadaki sade form: başlık, etiketli alanlar, kart içinde mesaj, sağ altta butonlar  ###
        # Alanlar self.QtUser altında toplanır (diğer pencerelerdeki ui nesnesi gibi)
        ui=self.QtUser=SimpleNamespace(
            lineEdit_kullanici_adi=QLineEdit(), lineEdit_sifre=QLineEdit(), lineEdit_adi_soyadi=QLineEdit(),
            lineEdit_telefon=QLineEdit(), lineEdit_mail=QLineEdit(), comboBox_yetki=QComboBox(),
            pushButton_cikis=QPushButton(objectName="pushButton_cikis"),
            pushButton_temizle=QPushButton(objectName="pushButton_temizle"),
            pushButton_kaydet=QPushButton(objectName="pushButton_kaydet"))
        ui.lineEdit_sifre.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        alanlar=[(ui.lineEdit_kullanici_adi,"Kullanıcı adı *","ör. ayse"),
                 (ui.lineEdit_sifre,"Şifre *",f"En az {SIFRE_EN_AZ} karakter"),
                 (ui.lineEdit_adi_soyadi,"Adı soyadı *","ör. Ayşe Yılmaz"),
                 (ui.lineEdit_telefon,"Telefon","10 hane, ör. 5321234567"),
                 (ui.lineEdit_mail,"E-posta","ör. ayse@ornek.com"),
                 (ui.comboBox_yetki,"Yetki *",None)]
        kart=QWidget(objectName="kullanici_karti")
        duzen=QVBoxLayout(kart)
        duzen.setContentsMargins(36,30,36,26)
        duzen.setSpacing(4)
        duzen.addWidget(QLabel("Yeni Kullanıcı",objectName="form_baslik"))
        alt=QLabel("Üye (guest) veya yönetici (admin) kaydı oluşturun. * işaretli alanlar zorunludur.",
                   objectName="form_alt")
        alt.setWordWrap(True)
        duzen.addWidget(alt)
        duzen.addSpacing(14)
        for alan,etiket,ipucu in alanlar:
            alan.setFixedHeight(38)
            if ipucu:
                alan.setPlaceholderText(ipucu)
            duzen.addWidget(QLabel(etiket,objectName="form_etiket"))
            duzen.addWidget(alan)
            duzen.addSpacing(8)
        ui.comboBox_yetki.setView(QListView())    # Mac'in yerel listesi seçenekleri kesiyordu
        self.mesaj=QLabel("",objectName="form_mesaj")
        self.mesaj.setWordWrap(True)
        self._mesaj_sayaci=QTimer(self,singleShot=True,timeout=self.mesaj.clear)
        duzen.addWidget(self.mesaj)
        duzen.addStretch()
        butonlar=QHBoxLayout()
        butonlar.addStretch()
        for buton,metin,rol in ((ui.pushButton_cikis,"Kapat","ikincil"),(ui.pushButton_temizle,"Temizle","ikincil"),
                                (ui.pushButton_kaydet,"Kaydet",None)):
            buton.setText(metin)
            buton.setMinimumSize(110,40)
            buton.setMaximumSize(160,40)
            buton.setCursor(Qt.PointingHandCursor)
            if rol:
                buton.setProperty("rol",rol)
            butonlar.addWidget(buton)
        duzen.addLayout(butonlar)
        self.setCentralWidget(kart)
        ikonlar.butonlara_uygula(self)
        self.setFixedSize(520,700)                # Mac: tam ekran panelin üstünde ekrana yayılmasın
        self.setStyleSheet(tema.qss()+f"""
#kullanici_karti {{ background-color: {tema.KART}; }}
#form_baslik {{ font-size: {tema.YAZI.buyuk}px; font-weight: {tema.YARI_KALIN}; color: {tema.METIN}; }}
#form_alt {{ color: {tema.IKINCIL_METIN}; }}
#form_etiket {{ font-weight: {tema.ORTA}; color: {tema.ETIKET}; }}
#form_mesaj {{ color: {tema.TEHLIKE}; }}
QLineEdit, QComboBox {{ font-size: {tema.YAZI.metin}px; padding: 4px 10px; border-radius: {tema.KOSE.kucuk}px; }}
""")

    def mesaj_goster(self,metin,sure):
        ###  Formun içinde kısa süre görünen mesaj  ###
        self.mesaj.setText(metin)
        self._mesaj_sayaci.start(sure)

    def ac(self):
        ###  Panelin ortasında, önde açılır  ###
        panel=self.parentWidget()
        if panel is not None:
            merkez=panel.frameGeometry().center()
            self.move(merkez.x()-self.width()//2, max(panel.frameGeometry().top()+20, merkez.y()-self.height()//2))
        self.show()
        self.raise_()
        self.activateWindow()

    def user_exit(self):
        self.clear_form()
        self.close()

    def closeEvent(self,olay):
        super().closeEvent(olay)
        panel=self.parentWidget()
        if panel is not None:                    # odak panele döner
            panel.raise_()
            panel.activateWindow()

    def chk_kullanici_adi(self):
        if df_user_query('kullanici',self.QtUser.lineEdit_kullanici_adi.text()):
            self.QtUser.lineEdit_kullanici_adi.clear()
            QMessageBox.information(self,"Uyarı!","Kullanıcı adı kullanılmaktadır!")
            self.mesaj_goster("Kullanıcı adı kullanılmaktadır. Lütfen yeni bir kayıt deneyin",self.dur_msj)

    def chk_sifre(self):
        if  not (self.QtUser.lineEdit_kullanici_adi.text()):
            QMessageBox.information(self,"Uyarı!","Önce kullanıcı adı girilmelidir!")
            self.QtUser.lineEdit_sifre.clear()
        elif self.QtUser.lineEdit_sifre.text():
            # Kısa şifre Kaydet'e basmadan, formun içinde bildirilir
            self.mesaj_goster(sifre_hatasi(self.QtUser.lineEdit_sifre.text()) or "",self.dur_msj*2)

    def chk_adi_soyadi(self):
        if not self.QtUser.lineEdit_sifre.text():
            QMessageBox.information(self,"Uyarı!","Önce kullanıcı adı ve şifre girilmelidir")
            self.QtUser.lineEdit_adi_soyadi.clear()
        else:
            if df_user_query('adi_soyadi',self.QtUser.lineEdit_adi_soyadi.text()):
                cvb=onay('Bu adda bir kullanıcı var. Devam etmek İstiyor musun?')
                if cvb==QMessageBox.No:
                    self.mesaj_goster("Lütfen yeni bir isim giriniz",self.dur_msj)
                    self.QtUser.lineEdit_adi_soyadi.clear()

    # Telefon ve e-posta isteğe bağlı: boş bırakılırsa uyarı verilmez
    def chk_telefon(self):
        telefon=self.QtUser.lineEdit_telefon.text().strip()
        if telefon and not telefon_gecerli(telefon):
            QMessageBox.information(self,"Uyarı!","Uygun telefon numarası girilmedi. Kontrol edin!")
            self.QtUser.lineEdit_telefon.clear()

    def chk_mail(self):
        mail=self.QtUser.lineEdit_mail.text().strip()
        if mail and not mail_gecerli(mail):
            QMessageBox.information(self,"Uyarı!","Uygun mail adresi girilmedi. Kontrol edin!")
            self.QtUser.lineEdit_mail.clear()

    def save_user(self):
        if self.QtUser.comboBox_yetki.currentText()=="Yetki Seçin...":
            QMessageBox.information(self,"Uyarı!","Kayıt oluşturmak için yetki seçimini belirtin!")
            self.QtUser.comboBox_yetki.setCurrentIndex(0)
        else:
            if not self.QtUser.lineEdit_kullanici_adi.text() or not self.QtUser.lineEdit_sifre.text() or not self.QtUser.lineEdit_adi_soyadi.text():
                QMessageBox.information(self,"Uyarı!","Kullanıcı Adı, Şifre ve Adı Soyadı boş olamaz!")
            elif sifre_hatasi(self.QtUser.lineEdit_sifre.text()):
                QMessageBox.information(self,"Uyarı!",sifre_hatasi(self.QtUser.lineEdit_sifre.text()))
            elif self.QtUser.lineEdit_telefon.text().strip() and not telefon_gecerli(self.QtUser.lineEdit_telefon.text().strip()):
                QMessageBox.information(self,"Uyarı!","Uygun telefon numarası girilmedi. Kontrol edin!")
            elif self.QtUser.lineEdit_mail.text().strip() and not mail_gecerli(self.QtUser.lineEdit_mail.text().strip()):
                QMessageBox.information(self,"Uyarı!","Uygun mail adresi girilmedi. Kontrol edin!")
            else:
                kayit=[]
                kayit.append(self.QtUser.lineEdit_kullanici_adi.text())
                kayit.append(self.QtUser.lineEdit_sifre.text())
                kayit.append(self.QtUser.lineEdit_adi_soyadi.text())
                kayit.append(self.QtUser.lineEdit_telefon.text().strip())
                kayit.append(self.QtUser.lineEdit_mail.text().strip())
                kayit.append(self.QtUser.comboBox_yetki.currentText())
                cvb=onay(f"{kayit[0]} kaydı yapılsın mı?",self)
                if cvb==QMessageBox.Yes:
                    user_ekle(kayit)
                    self.clear_form()
                    self.close()                     # form kapanır, kalınan menüye dönülür
                    self.kaydedildi.emit(kayit[0])

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
