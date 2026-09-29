from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from bforms.library_py import Ui_MainWindow
from bforms.onay import onay
from acodes.user import User
from acodes.ortak import OrtakSekmeler, FILTRELER, SECINIZ, tablo_basliklari, tabloya_yaz
from database.dbframe import (df_book_id_list, df_book_find_by_id, df_user_id_list, df_user_find_by_id,
                              kitap_oduncte, df_work_user_list, df_work_perbook, df_work_table_book)
from database.dbbase import ekle_kayit, degistir_kayit, sil_kayit, save_work_to_db, update_work_to_db
import datetime


def buyuk_harf(metin):
    """Her kelimenin ilk harfini büyütür, gerisine dokunmaz (Türkçe i/İ uyumlu).
    str.title() "Anne'nin" -> "Anne'Nin", "TAHİR" -> "Tahi̇r" yaptığı için kullanılmıyor."""
    kelimeler=[]
    for k in metin.split(" "):
        if k:
            ilk=k[0]
            k=("İ" if ilk=="i" else "I" if ilk=="ı" else ilk.upper())+k[1:]
        kelimeler.append(k)
    return " ".join(kelimeler)


def kitap_listesi(cmb):
    """Açılır listeyi kitap id'leriyle doldurur. Aynı adlı kitaplara yayınevi ve yıl eklenir."""
    kitaplar=df_book_id_list()
    adlar=[adi for _,adi,_,_ in kitaplar]
    cmb.addItem(SECINIZ)
    for id,adi,yayinevi,yili in kitaplar:
        cmb.addItem(f"{adi} ({yayinevi}, {yili})" if adlar.count(adi)>1 else adi, id)


## Admin paneli: ortak sekmelere ek olarak Kitap Kayıt ve Kitap Verme sekmeleri
class Library(OrtakSekmeler, QMainWindow):
    def __init__(self):
        super().__init__()
        self.QtLibrary = Ui_MainWindow()
        self.QtLibrary.setupUi(self)
        self.user=User()
        self.QtLibrary.tabWidget.setCurrentIndex(0)

        ###  Property  #########
        self.dur_msj=2000
        self.flag_book=False
        self.flag_user=False
        self.flag_book2=False
        self.flag_user2=False
        self.kisi_6_1=None
        self.kisi_6_2=None

        ###  Tab_1, 2, 4, 5 (Guest ile ortak)  #########
        self.ortak_sekmeleri_kur()
        self.QtLibrary.pushButton_1_yeni_kullanici.clicked.connect(self.user.show)

        ###  Tab_3 Olaylar  #########
        self.QtLibrary.pushButton_3_1_kaydet.clicked.connect(self.save_book)
        self.QtLibrary.pushButton_3_1_temizle.clicked.connect(self.clear_form_3_1)
        self.list_items_3_2()
        self.QtLibrary.pushButton_3_2_bul.clicked.connect(self.find_item_3_2)
        self.QtLibrary.pushButton_3_2_deg_kaydet.clicked.connect(self.update_item_3_2)
        self.QtLibrary.pushButton_3_2_iptal.clicked.connect(self.clear_form_3_2)
        self.list_items_3_3()
        self.QtLibrary.pushButton_3_3_bul.clicked.connect(self.find_item_3_3)
        self.QtLibrary.pushButton_3_3_Sil.clicked.connect(self.delete_item_3_3)
        self.QtLibrary.pushButton_3_3_iptal.clicked.connect(self.clear_form_3_3)

        ###  Tab_6 Olaylar  #########
        self.list_items_6_1_1()
        self.QtLibrary.pushButton_6_1_1_bul_kitap.clicked.connect(self.find_item_6_1_1)
        self.QtLibrary.pushButton_6_1_1_bul_kitap_temizle.clicked.connect(self.clear_form_6_1_1)
        self.list_user_6_1_2 ()
        self.QtLibrary.pushButton_6_1_2_bul_kisi.clicked.connect(self.find_user_6_1_2)
        self.QtLibrary.pushButton_6_1_2_bul_kisi_temizle.clicked.connect(self.clear_form_6_1_2)
        self.QtLibrary.pushButton_6_1_islemi_kaydet.clicked.connect(self.save_work)

        self.list_user_6_2_1()
        self.QtLibrary.pushButton_6_2_1_bul_kisi.clicked.connect(self.find_user_6_2_1)
        self.QtLibrary.pushButton_6_2_1_bul_kisi_temizle.clicked.connect(self.clear_form_6_2_1)

        self.QtLibrary.pushButton_6_2_2_bul_kitap.clicked.connect(self.find_item_6_2_2)
        self.QtLibrary.pushButton_6_2_2_bul_kitap_temizle.clicked.connect(self.clear_form_6_2_2)
        self.QtLibrary.pushButton_6_2_islemi_kaydet.clicked.connect(self.save_work2)

        self.create_form_tab_6()
        self.QtLibrary.pushButton_6_3_listele.clicked.connect(self.listele_6)
        self.QtLibrary.pushButton_6_3_temizle.clicked.connect(self.temizle_6)

        # Sekme değişince listeler güncellensin (ör. Tab 1'den eklenen yeni üye)
        self.QtLibrary.tabWidget.currentChanged.connect(self.yenile)

    def yenile(self):
        ###  Kayıt/üye değişikliklerinden sonra açılır listeleri ve istatistikleri güncelleme  ###
        for cmb in (self.QtLibrary.comboBox_3_2_bul_adi, self.QtLibrary.comboBox_3_3_bul_adi,
                    self.QtLibrary.comboBox_6_1_1_liste_kitap, self.QtLibrary.comboBox_6_1_2_liste_kisi):
            cmb.clear()
        self.list_items_3_2()
        self.list_items_3_3()
        for no,kolon,_ in FILTRELER:
            self.filtre_combo_doldur(no,kolon)
        self.create_tab_5()
        self.list_items_6_1_1()
        self.list_user_6_1_2()

    ##################################
    #####   Tab_3 Fonksiyonlar   #####
    ##################################

### Tablo 1 İşlemleri  ###

    def save_book(self):
        kayit=[]
        kayit.append(buyuk_harf(self.QtLibrary.lineEdit_3_1_adi.text()))
        kayit.append(buyuk_harf(self.QtLibrary.lineEdit_3_1_yazari.text()))
        kayit.append(buyuk_harf(self.QtLibrary.lineEdit_3_1_ceviren.text()))
        kayit.append(buyuk_harf(self.QtLibrary.lineEdit_3_1_turu.text()))
        kayit.append(buyuk_harf(self.QtLibrary.lineEdit_3_1_yayinevi.text()))
        kayit.append(self.QtLibrary.lineEdit_3_1_yili.text())
        kayit.append(self.QtLibrary.lineEdit_3_1_sayfa.text())
        if (self.QtLibrary.lineEdit_3_1_adi.text())=="":
            self.QtLibrary.statusbar.showMessage("Kayıt oluşturun",self.dur_msj)
        else:
            cvb=onay(f"{(self.QtLibrary.lineEdit_3_1_adi.text())} kaydedilsin mi?")
            if cvb==QMessageBox.Yes:
                ekle_kayit(kayit)
                self.QtLibrary.statusbar.showMessage(f"'{kayit[0]}' kaydedildi",self.dur_msj)
                self.clear_form_3_1()
                self.yenile()

    def clear_form_3_1(self):
        self.QtLibrary.lineEdit_3_1_adi.clear()
        self.QtLibrary.lineEdit_3_1_yazari.clear()
        self.QtLibrary.lineEdit_3_1_ceviren.clear()
        self.QtLibrary.lineEdit_3_1_turu.clear()
        self.QtLibrary.lineEdit_3_1_yayinevi.clear()
        self.QtLibrary.lineEdit_3_1_yili.clear()
        self.QtLibrary.lineEdit_3_1_sayfa.clear()

### Tablo 2 İşlemleri  ###

    def list_items_3_2 (self):
        kitap_listesi(self.QtLibrary.comboBox_3_2_bul_adi)

    def find_item_3_2(self):
        id=self.QtLibrary.comboBox_3_2_bul_adi.currentData()
        if id is None:
            self.QtLibrary.statusbar.showMessage("Seçim yapınız",self.dur_msj)
        else:
            self.show_items_3_2(df_book_find_by_id(id))

    def show_items_3_2(self,kyt):
        degisecek=kyt
        self.QtLibrary.lineEdit_3_2_id.setText(str(degisecek[0]))
        self.QtLibrary.lineEdit_3_2_adi.setText(degisecek[1])
        self.QtLibrary.lineEdit_3_2_yazari.setText(degisecek[2])
        self.QtLibrary.lineEdit_3_2_ceviren.setText(degisecek[3])
        self.QtLibrary.lineEdit_3_2_turu.setText(degisecek[4])
        self.QtLibrary.lineEdit_3_2_yayinevi.setText(degisecek[5])
        self.QtLibrary.lineEdit_3_2_yili.setText(degisecek[6])
        self.QtLibrary.lineEdit_3_2_sayfa.setText(degisecek[7])
        self.QtLibrary.statusbar.showMessage(f"{self.QtLibrary.comboBox_3_2_bul_adi.currentText()} bilgileri yazıldı.",self.dur_msj)
        self.QtLibrary.pushButton_3_2_deg_kaydet.setEnabled(True)
        self.QtLibrary.pushButton_3_2_iptal.setEnabled(True)

    def update_item_3_2(self):
        kayit=[]
        kayit.append(self.QtLibrary.lineEdit_3_2_id.text())
        kayit.append(buyuk_harf(self.QtLibrary.lineEdit_3_2_adi.text()))
        kayit.append(buyuk_harf(self.QtLibrary.lineEdit_3_2_yazari.text()))
        kayit.append(buyuk_harf(self.QtLibrary.lineEdit_3_2_ceviren.text()))
        kayit.append(buyuk_harf(self.QtLibrary.lineEdit_3_2_turu.text()))
        kayit.append(buyuk_harf(self.QtLibrary.lineEdit_3_2_yayinevi.text()))
        kayit.append(self.QtLibrary.lineEdit_3_2_yili.text())
        kayit.append(self.QtLibrary.lineEdit_3_2_sayfa.text())
        if len(self.QtLibrary.lineEdit_3_2_adi.text())!=0:
            cvb=onay("Kayıt değiştirilsin mi?")
            if cvb==QMessageBox.Yes:
                degistir_kayit(kayit)
                self.QtLibrary.statusbar.showMessage(f"'{kayit[1]}' güncellendi.",self.dur_msj)
                self.clear_form_3_2()
                self.yenile()
        else:
            self.QtLibrary.statusbar.showMessage("Kayıtta değişiklik yapılmadı.Kontrol edin",self.dur_msj)

    def clear_form_3_2(self):
        self.QtLibrary.lineEdit_3_2_id.clear()
        self.QtLibrary.lineEdit_3_2_ceviren.clear()
        self.QtLibrary.lineEdit_3_2_yazari.clear()
        self.QtLibrary.lineEdit_3_2_adi.clear()
        self.QtLibrary.lineEdit_3_2_turu.clear()
        self.QtLibrary.lineEdit_3_2_yayinevi.clear()
        self.QtLibrary.lineEdit_3_2_yili.clear()
        self.QtLibrary.lineEdit_3_2_sayfa.clear()
        self.QtLibrary.pushButton_3_2_deg_kaydet.setEnabled(False)
        self.QtLibrary.pushButton_3_2_iptal.setEnabled(False)
        self.QtLibrary.comboBox_3_2_bul_adi.setCurrentIndex(0)

### Tablo 3 İşlemleri  ###

    def list_items_3_3 (self):
        kitap_listesi(self.QtLibrary.comboBox_3_3_bul_adi)

    def find_item_3_3(self):
        id=self.QtLibrary.comboBox_3_3_bul_adi.currentData()
        if id is None:
            self.QtLibrary.statusbar.showMessage("Seçim yapınız",self.dur_msj)
        else:
            self.show_items_3_3(df_book_find_by_id(id))

    def show_items_3_3(self,kyt):
        silinecek=kyt
        self.QtLibrary.lineEdit_3_3_id.setText(str(silinecek[0]))
        self.QtLibrary.lineEdit_3_3_adi.setText(silinecek[1])
        self.QtLibrary.lineEdit_3_3_yazari.setText(silinecek[2])
        self.QtLibrary.lineEdit_3_3_ceviren.setText(silinecek[3])
        self.QtLibrary.lineEdit_3_3_turu.setText(silinecek[4])
        self.QtLibrary.lineEdit_3_3_yayinevi.setText(silinecek[5])
        self.QtLibrary.lineEdit_3_3_yili.setText(silinecek[6])
        self.QtLibrary.lineEdit_3_3_sayfa.setText(silinecek[7])
        self.QtLibrary.statusbar.showMessage(f"{self.QtLibrary.comboBox_3_3_bul_adi.currentText()} bilgileri yazıldı.",self.dur_msj)
        self.QtLibrary.pushButton_3_3_Sil.setEnabled(True)
        self.QtLibrary.pushButton_3_3_iptal.setEnabled(True)

    def delete_item_3_3(self):
        if kitap_oduncte(self.QtLibrary.lineEdit_3_3_id.text()):
            QMessageBox.information(self,"Uyarı!","Bu kitap ödünçte. İade alınmadan silinemez!")
            return
        cvb=onay("Kayıt silinsin mi?")
        if cvb==QMessageBox.Yes:
            sil_kayit(int(self.QtLibrary.lineEdit_3_3_id.text()))
            self.QtLibrary.statusbar.showMessage(f"{self.QtLibrary.lineEdit_3_3_adi.text()} silindi",self.dur_msj)
            self.clear_form_3_3()
            self.yenile()

    def clear_form_3_3(self):
        self.QtLibrary.lineEdit_3_3_id.clear()
        self.QtLibrary.lineEdit_3_3_adi.clear()
        self.QtLibrary.lineEdit_3_3_yazari.clear()
        self.QtLibrary.lineEdit_3_3_ceviren.clear()
        self.QtLibrary.lineEdit_3_3_turu.clear()
        self.QtLibrary.lineEdit_3_3_yayinevi.clear()
        self.QtLibrary.lineEdit_3_3_yili.clear()
        self.QtLibrary.lineEdit_3_3_sayfa.clear()
        self.QtLibrary.pushButton_3_3_Sil.setEnabled(False)
        self.QtLibrary.pushButton_3_3_iptal.setEnabled(False)
        self.QtLibrary.comboBox_3_3_bul_adi.setCurrentIndex(0)

    ##################################
    #####   Tab_6 Fonksiyonlar   #####
    ##################################

### Tablo 1 İşlemleri  ###

    def list_items_6_1_1 (self):
        kitap_listesi(self.QtLibrary.comboBox_6_1_1_liste_kitap)

    def find_item_6_1_1(self):
        id=self.QtLibrary.comboBox_6_1_1_liste_kitap.currentData()
        if id is None:
            self.QtLibrary.statusbar.showMessage("Seçim yapınız",self.dur_msj)
        elif kitap_oduncte(id):
            QMessageBox.information(self,"Uyarı!","Bu kitap başka bir üyededir!")
        else:
            self.show_items_6_1_1(df_book_find_by_id(id))

    def show_items_6_1_1(self,kyt):
        kayit=kyt
        self.QtLibrary.lineEdit_6_1_id.setText(str(kayit[0]))
        self.QtLibrary.lineEdit_6_1_adi.setText(kayit[1])
        self.QtLibrary.lineEdit_6_1_yazari.setText(kayit[2])
        self.QtLibrary.lineEdit_6_1_ceviren.setText(kayit[3])
        self.QtLibrary.lineEdit_6_1_turu.setText(kayit[4])
        self.QtLibrary.lineEdit_6_1_yayinevi.setText(kayit[5])
        self.QtLibrary.lineEdit_6_1_yili.setText(kayit[6])
        self.QtLibrary.lineEdit_6_1_sayfa.setText(kayit[7])
        self.flag_book=True
        self.check_bottom()
        self.QtLibrary.pushButton_6_1_1_bul_kitap_temizle.setEnabled(True)
        self.QtLibrary.statusbar.showMessage(f"{self.QtLibrary.comboBox_6_1_1_liste_kitap.currentText()} bilgileri yazıldı.",self.dur_msj)

    def clear_form_6_1_1(self):
        self.QtLibrary.lineEdit_6_1_id.clear()
        self.QtLibrary.lineEdit_6_1_ceviren.clear()
        self.QtLibrary.lineEdit_6_1_yazari.clear()
        self.QtLibrary.lineEdit_6_1_adi.clear()
        self.QtLibrary.lineEdit_6_1_turu.clear()
        self.QtLibrary.lineEdit_6_1_yayinevi.clear()
        self.QtLibrary.lineEdit_6_1_yili.clear()
        self.QtLibrary.lineEdit_6_1_sayfa.clear()
        self.flag_book=False
        self.QtLibrary.pushButton_6_1_islemi_kaydet.setEnabled(False)
        self.QtLibrary.pushButton_6_1_1_bul_kitap_temizle.setEnabled(False)
        self.QtLibrary.comboBox_6_1_1_liste_kitap.setCurrentIndex(0)

    def list_user_6_1_2 (self):
        # Aynı isimde iki üye olabileceği için her satırda kullanıcı id'si saklanır
        self.QtLibrary.comboBox_6_1_2_liste_kisi.addItem(SECINIZ)
        for id,adi,kullanici in df_user_id_list():
            self.QtLibrary.comboBox_6_1_2_liste_kisi.addItem(f"{adi} ({kullanici})",id)

    def find_user_6_1_2(self):
        id=self.QtLibrary.comboBox_6_1_2_liste_kisi.currentData()
        if id is None:
            self.QtLibrary.statusbar.showMessage("Seçim yapınız",self.dur_msj)
        else:
            kyt=df_user_find_by_id(id)
            self.show_user_6_1_2(kyt)

    def show_user_6_1_2(self,kyt):
        kayit=kyt
        self.kisi_6_1=kayit[0]
        self.QtLibrary.lineEdit_6_1_kullanici.setText(kayit[1])
        self.QtLibrary.lineEdit_6_1_adi_soyadi.setText(kayit[3])
        self.QtLibrary.lineEdit_6_1_telefon.setText(kayit[4])
        self.QtLibrary.lineEdit_6_1_mail.setText(kayit[5])
        self.QtLibrary.lineEdit_6_1_yetki.setText(kayit[6])
        self.flag_user=True
        self.check_bottom()
        self.QtLibrary.pushButton_6_1_2_bul_kisi_temizle.setEnabled(True)
        self.QtLibrary.statusbar.showMessage(f"{self.QtLibrary.comboBox_6_1_2_liste_kisi.currentText()} bilgileri yazıldı.",self.dur_msj)

    def clear_form_6_1_2(self):
        self.QtLibrary.lineEdit_6_1_kullanici.clear()
        self.QtLibrary.lineEdit_6_1_adi_soyadi.clear()
        self.QtLibrary.lineEdit_6_1_telefon.clear()
        self.QtLibrary.lineEdit_6_1_mail.clear()
        self.QtLibrary.lineEdit_6_1_yetki.clear()
        self.kisi_6_1=None
        self.flag_user=False
        self.QtLibrary.pushButton_6_1_islemi_kaydet.setEnabled(False)
        self.QtLibrary.pushButton_6_1_2_bul_kisi_temizle.setEnabled(False)
        self.QtLibrary.comboBox_6_1_2_liste_kisi.setCurrentIndex(0)

    def check_bottom(self):
        self.QtLibrary.pushButton_6_1_islemi_kaydet.setEnabled(self.flag_book and self.flag_user)

    def save_work(self):
        if self.flag_book and self.flag_user:
            cvb=onay("İşlemi kaydetmek istiyor musunuz?")
            if cvb==QMessageBox.Yes:
                tdy=datetime.datetime.today()
                kayit=[str(self.kisi_6_1),
                        self.QtLibrary.lineEdit_6_1_id.text(),
                        tdy.date(), datetime.datetime.strftime(tdy, '%X '),"out","",""]
                save_work_to_db(kayit)
                self.QtLibrary.statusbar.showMessage("İşlem kaydedildi.",self.dur_msj)
                self.clear_form_6_1_1()
                self.clear_form_6_1_2()
                self.clear_form_6_2_1()  # İade listesi yeni kaydı göstersin
        else:
            self.QtLibrary.statusbar.showMessage("Kayıtta eksik var. Kontrol edin.",self.dur_msj)

### Tablo 2 İşlemleri  ###

    def list_user_6_2_1 (self):
        self.QtLibrary.comboBox_6_2_1_liste_kisi.clear()
        self.QtLibrary.comboBox_6_2_1_liste_kisi.addItem(SECINIZ)
        for id,adi,kullanici in df_work_user_list():
            self.QtLibrary.comboBox_6_2_1_liste_kisi.addItem(f"{adi} ({kullanici})",id)

    def find_user_6_2_1(self):
        id=self.QtLibrary.comboBox_6_2_1_liste_kisi.currentData()
        if id is None:
            self.QtLibrary.statusbar.showMessage("Seçim yapınız",self.dur_msj)
        else:
            kyt=df_user_find_by_id(id)
            self.show_user_6_2_1(kyt)
            self.QtLibrary.comboBox_6_2_2_liste_kitap.clear()
            self.QtLibrary.comboBox_6_2_2_liste_kitap.addItem(SECINIZ)
            for kitap_id,adi in df_work_perbook(id):
                self.QtLibrary.comboBox_6_2_2_liste_kitap.addItem(adi,kitap_id)
            self.QtLibrary.comboBox_6_2_2_liste_kitap.setEnabled(True)
            self.QtLibrary.pushButton_6_2_2_bul_kitap.setEnabled(True)

    def show_user_6_2_1(self,kyt):
        kayit=kyt
        self.kisi_6_2=kayit[0]
        self.QtLibrary.lineEdit_6_2_kullanici.setText(kayit[1])
        self.QtLibrary.lineEdit_6_2_adi_soyadi.setText(kayit[3])
        self.QtLibrary.lineEdit_6_2_telefon.setText(kayit[4])
        self.QtLibrary.lineEdit_6_2_mail.setText(kayit[5])
        self.QtLibrary.lineEdit_6_2_yetki.setText(kayit[6])
        self.flag_user2=True
        self.check_bottom2()
        self.QtLibrary.pushButton_6_2_1_bul_kisi_temizle.setEnabled(True)
        self.QtLibrary.statusbar.showMessage(f"{self.QtLibrary.comboBox_6_2_1_liste_kisi.currentText()} bilgileri yazıldı.",self.dur_msj)

    def clear_form_6_2_1(self):
        self.QtLibrary.lineEdit_6_2_kullanici.clear()
        self.QtLibrary.lineEdit_6_2_adi_soyadi.clear()
        self.QtLibrary.lineEdit_6_2_telefon.clear()
        self.QtLibrary.lineEdit_6_2_mail.clear()
        self.QtLibrary.lineEdit_6_2_yetki.clear()
        self.kisi_6_2=None
        self.flag_user2=False
        self.QtLibrary.pushButton_6_2_islemi_kaydet.setEnabled(False)
        self.QtLibrary.pushButton_6_2_1_bul_kisi_temizle.setEnabled(False)
        self.list_user_6_2_1()
        self.QtLibrary.comboBox_6_2_2_liste_kitap.setEnabled(False)
        self.QtLibrary.comboBox_6_2_2_liste_kitap.clear()
        self.QtLibrary.pushButton_6_2_2_bul_kitap.setEnabled(False)
        self.clear_form_6_2_2()

    def find_item_6_2_2(self):
        kitap_id=self.QtLibrary.comboBox_6_2_2_liste_kitap.currentData()
        if kitap_id is None:
            self.QtLibrary.statusbar.showMessage("Seçim yapınız",self.dur_msj)
        else:
            self.show_items_6_2_2(df_book_find_by_id(kitap_id))

    def show_items_6_2_2(self,kyt):
        kayit=kyt
        self.QtLibrary.lineEdit_6_2_id.setText(str(kayit[0]))
        self.QtLibrary.lineEdit_6_2_adi.setText(kayit[1])
        self.QtLibrary.lineEdit_6_2_yazari.setText(kayit[2])
        self.QtLibrary.lineEdit_6_2_ceviren.setText(kayit[3])
        self.QtLibrary.lineEdit_6_2_turu.setText(kayit[4])
        self.QtLibrary.lineEdit_6_2_yayinevi.setText(kayit[5])
        self.QtLibrary.lineEdit_6_2_yili.setText(kayit[6])
        self.QtLibrary.lineEdit_6_2_sayfa.setText(kayit[7])
        self.flag_book2=True
        self.check_bottom2()
        self.QtLibrary.pushButton_6_2_2_bul_kitap_temizle.setEnabled(True)
        self.QtLibrary.statusbar.showMessage(f"{self.QtLibrary.comboBox_6_2_2_liste_kitap.currentText()} bilgileri yazıldı.",self.dur_msj)

    def clear_form_6_2_2(self):
        self.QtLibrary.lineEdit_6_2_id.clear()
        self.QtLibrary.lineEdit_6_2_ceviren.clear()
        self.QtLibrary.lineEdit_6_2_yazari.clear()
        self.QtLibrary.lineEdit_6_2_adi.clear()
        self.QtLibrary.lineEdit_6_2_turu.clear()
        self.QtLibrary.lineEdit_6_2_yayinevi.clear()
        self.QtLibrary.lineEdit_6_2_yili.clear()
        self.QtLibrary.lineEdit_6_2_sayfa.clear()
        self.flag_book2=False
        self.QtLibrary.pushButton_6_2_islemi_kaydet.setEnabled(False)
        self.QtLibrary.pushButton_6_2_2_bul_kitap_temizle.setEnabled(False)
        self.QtLibrary.comboBox_6_2_2_liste_kitap.setCurrentIndex(0)

    def check_bottom2(self):
        self.QtLibrary.pushButton_6_2_islemi_kaydet.setEnabled(self.flag_book2 and self.flag_user2)

    def save_work2(self):
        if self.flag_book2 and self.flag_user2:
            cvb=onay("İşlemi kaydetmek istiyor musunuz?")
            if cvb==QMessageBox.Yes:
                tdy=datetime.datetime.today()
                kayit=[str(self.kisi_6_2),
                        self.QtLibrary.lineEdit_6_2_id.text(),"","","in",
                        tdy.date(), datetime.datetime.strftime(tdy, '%X ')]
                update_work_to_db(kayit)
                self.QtLibrary.statusbar.showMessage("İşlem kaydedildi.",self.dur_msj)
                self.clear_form_6_2_1()
        else:
            self.QtLibrary.statusbar.showMessage("Kayıtta eksik var. Kontrol edin.",self.dur_msj)

### Tablo 3 İşlemleri  ###

    def create_form_tab_6(self):
        self.QtLibrary.tableWidget_6_2.setRowCount(1)
        tablo_basliklari(self.QtLibrary.tableWidget_6_2,
                         [(220,"Kitap Adı"),(220,"Yazarı"),(100,"Turu"),(170,"Alan Kişi"),
                          (120,"Telefon"),(180,"Mail"),(100,"Aldığı Tarih")])

    def listele_6(self):
        tabloya_yaz(self.QtLibrary.tableWidget_6_2, df_work_table_book())
        self.QtLibrary.statusbar.showMessage("Liste görüntülendi.",self.dur_msj)

    def temizle_6(self):
        self.QtLibrary.tableWidget_6_2.clear()
        self.create_form_tab_6()
        self.QtLibrary.statusbar.showMessage("Liste temizlendi.",self.dur_msj)

# Uygulamanın sürekli çalışması
if __name__=="__main__":
    app=QApplication([])
    pencere = Library()
    pencere.show()
    app.exec_()
