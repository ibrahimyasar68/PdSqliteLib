from PyQt5.QtWidgets import *
from bforms.library_py import Ui_MainWindow
from bforms.onay import onay
from acodes.user import User
from database.dbframe import *
from database.dbbase import *
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
    cmb.addItem(' Seçiniz...')
    for id,adi,yayinevi,yili in kitaplar:
        cmb.addItem(f"{adi} ({yayinevi}, {yili})" if adlar.count(adi)>1 else adi, id)



class Library(QMainWindow):
    def __init__(self):
        super().__init__()
        self.QtLibrary = Ui_MainWindow()
        self.QtLibrary.setupUi(self)
        self.user=User()
        self.QtLibrary.tabWidget.setCurrentIndex(0)

        ###  Property  #########
        self.dur_msj=2000
        self.cnt2=35
        self.cnt3=40
        self.list41=[]
        self.list42=[]
        self.list43=[]
        self.list44=[]
        self.flag_book=False
        self.flag_user=False
        self.flag_book2=False
        self.flag_user2=False
        self.kisi_6_1=None
        self.kisi_6_2=None
        

        ###  Tab_1 Olaylar  #########
        self.QtLibrary.pushButton_1_cikis.clicked.connect(self.lib_exit)
        self.QtLibrary.pushButton_1_yeni_kullanici.clicked.connect(self.new_user)

        ###  Tab_2 Olaylar  #########
        self.create_form_tab2()
        self.QtLibrary.pushButton_2_listele.clicked.connect(self.listele)
        self.QtLibrary.pushButton_2_temizle.clicked.connect(self.temizle)

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

        ###  Tab_4 Olaylar  ######### 
        self.create_tab_4()

        self.QtLibrary.comboBox_4_1_turu.currentTextChanged.connect(self.append_list_type_4_1)
        self.QtLibrary.pushButton_4_1_listele.clicked.connect(self.show_list_type_4_1)
        self.QtLibrary.pushButton_4_1_temizle.clicked.connect(self.clear_list_type_4_1)  

        self.QtLibrary.comboBox_4_2_turu.currentTextChanged.connect(self.append_list_author_4_2)
        self.QtLibrary.pushButton_4_2_listele.clicked.connect(self.show_list_author_4_2)
        self.QtLibrary.pushButton_4_2_temizle.clicked.connect(self.clear_list_author_4_2) 

        self.QtLibrary.comboBox_4_3_turu.currentTextChanged.connect(self.append_list_publish_4_3)
        self.QtLibrary.pushButton_4_3_listele.clicked.connect(self.show_list_publish_4_3)
        self.QtLibrary.pushButton_4_3_temizle.clicked.connect(self.clear_list_publish_4_3)

        self.QtLibrary.comboBox_4_4_turu.currentTextChanged.connect(self.append_list_year_4_4)
        self.QtLibrary.pushButton_4_4_listele.clicked.connect(self.show_list_year_4_4)
        self.QtLibrary.pushButton_4_4_temizle.clicked.connect(self.clear_list_year_4_4) 

        ###  Tab_5 Olaylar  #########
        self.create_tab_5()

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
                    self.QtLibrary.comboBox_4_1_turu, self.QtLibrary.comboBox_4_2_turu,
                    self.QtLibrary.comboBox_4_3_turu, self.QtLibrary.comboBox_4_4_turu,
                    self.QtLibrary.comboBox_6_1_1_liste_kitap, self.QtLibrary.comboBox_6_1_2_liste_kisi):
            cmb.blockSignals(True)
            cmb.clear()
            cmb.blockSignals(False)
        self.list_items_3_2()
        self.list_items_3_3()
        for cmb,kolon in ((self.QtLibrary.comboBox_4_1_turu,'Turu'), (self.QtLibrary.comboBox_4_2_turu,'Yazari'),
                          (self.QtLibrary.comboBox_4_3_turu,'Yayinevi'), (self.QtLibrary.comboBox_4_4_turu,'Yili')):
            cmb.blockSignals(True)  # Seçim listesine otomatik ekleme yapılmasın
            cmb.addItems([' Seçiniz...']+df_sort_list(kolon))
            cmb.blockSignals(False)
        self.create_tab_5()
        self.list_items_6_1_1()
        self.list_user_6_1_2()

    ##################################
    #####   Tab_1 Fonksiyonlar   #####
    ##################################

    def lib_exit (self):
        self.close()

    def new_user(self):
        self.user.show()

    def user_name(self,name):
        self.QtLibrary.label_log_on.setText(name)

   
    ##################################
    #####   Tab_2 Fonksiyonlar   #####
    ##################################

    def create_form_tab2(self):
        self.QtLibrary.tableWidget_2.setRowCount(1)
                #Kolon aralıklarını ayarlama
        kolonbilgi=[(60,"Sıra No"),(200,"Adı",),(200,"Yazarı"),(150,"Çeviren"),
                        (150,"Turu"),(200,"Yayınevi"),(60,"Yılı"),(60,"Sayfa")]
        for ind,dgr in enumerate(kolonbilgi):
            self.QtLibrary.tableWidget_2.setColumnWidth(ind,dgr[0])
            self.QtLibrary.tableWidget_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))

    def listele(self):
        sayi=df_count_items()
        self.QtLibrary.tableWidget_2.setRowCount(sayi)
        islem=df_all_list()
        for id,satır in enumerate(islem): 
            for no, son in enumerate(satır):
                self.QtLibrary.tableWidget_2.setItem(id,no,QTableWidgetItem(str(son)))
        self.QtLibrary.statusbar.showMessage("Liste görüntülendi.",self.dur_msj)   

    def temizle(self):
        self.QtLibrary.tableWidget_2.clear()
        self.create_form_tab2()
        self.QtLibrary.statusbar.showMessage("Liste temizlendi.",self.dur_msj)
        
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
            else:pass  

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
            else:pass
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
        else:pass

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
    #####   Tab_4 Fonksiyonlar   #####
    ##################################

    def create_tab_4(self):
         self.list_type_4_1()
         self.list_author_4_2()
         self.list_publish_4_3()
         self.list_year_4_4()
         
### Tablo 1 İşlemleri  ###         

    def list_type_4_1(self):
        ###  DB'den Tür Listesini alma  ###        
        tur_liste=df_sort_list('Turu')
        tur_liste.insert (0,' Seçiniz...')
        cmb=tur_liste 
        self.QtLibrary.comboBox_4_1_turu.addItems(cmb)

        #####  Liste  genişliği ve adı ayarlama  #######
        self.QtLibrary.tableWidget_4_1_1.setColumnWidth(0,200)
        self.QtLibrary.tableWidget_4_1_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Tür"))
        self.QtLibrary.tableWidget_4_1_1.setRowCount(1)

        #Kolon aralıklarını ayarlama
        kolonbilgi=[(50,"Sıra No"),(190,"Adı"),(190,"Yazarı"),(130,"Çeviren"),
                        (130,"Turu"),(165,"Yayınevi"),(40,"Yılı"),(40,"Sayfa")]
        for ind,dgr in enumerate(kolonbilgi):
            self.QtLibrary.tableWidget_4_1_2.setColumnWidth(ind,dgr[0])
            self.QtLibrary.tableWidget_4_1_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        self.QtLibrary.tableWidget_4_1_2.setRowCount(1)

    def append_list_type_4_1(self):         
        tur_lst_ekle=str(self.QtLibrary.comboBox_4_1_turu.currentText())
        if tur_lst_ekle != " Seçiniz..."  and tur_lst_ekle not in self.list41:
            self.list41.append(tur_lst_ekle)
            self.QtLibrary.statusbar.showMessage(f"Listeye ' {tur_lst_ekle} ' eklendi",self.dur_msj)
        if '' in self.list41:
            self.list41.remove('') 
        self.list41.sort()
        self.QtLibrary.tableWidget_4_1_1.setRowCount(len(self.list41))
        
        for x,y in enumerate(self.list41):
            self.QtLibrary.tableWidget_4_1_1.setItem(x,0,QTableWidgetItem(str(y)))

    def show_list_type_4_1(self):
        if len(self.list41)!=0:            
            str_sy=0 ### Tablodaki satır sayısı ####
            kayit=[]
            for tur in self.list41:
                 sy,kay=df_srt_fltr('Turu',tur)
                 str_sy+=sy
                 kayit.append(kay)
            self.QtLibrary.tableWidget_4_1_2.setRowCount(str_sy)

            ####### Verileri satırlara yazma ######
            sr=-1
            for kay in (kayit):
                for kyt in kay:              
                    sr+=1
                    for no, son in enumerate(kyt):           
                        self.QtLibrary.tableWidget_4_1_2.setItem(sr,no,QTableWidgetItem(str(son)))
            self.QtLibrary.statusbar.showMessage("Sonuçlar listelendi",self.dur_msj)
        else:
            self.QtLibrary.statusbar.showMessage("Listelenecek tür seçiniz!",self.dur_msj)
        self.QtLibrary.pushButton_4_1_temizle.setEnabled(True)
    
    def clear_list_type_4_1(self):
        if len(self.list41)!=0:
            cvb=onay('Kayıtları silmek istiyor musunuz?')
            if cvb==QMessageBox.Yes:
                self.list41.clear() 
                self.QtLibrary.comboBox_4_1_turu.setCurrentIndex(0)

                self.QtLibrary.tableWidget_4_1_1.clear() 
                self.QtLibrary.pushButton_4_1_temizle.setEnabled(False)               
                self.QtLibrary.tableWidget_4_1_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Tür"))
                self.QtLibrary.tableWidget_4_1_1.setRowCount(1)

                self.QtLibrary.tableWidget_4_1_2.clear()
                self.QtLibrary.tableWidget_4_1_2.setRowCount(1)
                self.QtLibrary.statusbar.showMessage("Veriler temizlendi",self.dur_msj)
                #Kolon aralıklarını ayarlama
                kolonbilgi=[(50,"Sıra No"),(190,"Adı"),(190,"Yazarı"),(130,"Çeviren"),
                                (130,"Turu"),(165,"Yayınevi"),(40,"Yılı"),(40,"Sayfa")]
                for ind,dgr in enumerate(kolonbilgi):
                    self.QtLibrary.tableWidget_4_1_2.setColumnWidth(ind,dgr[0])
                    self.QtLibrary.tableWidget_4_1_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        else:
            self.QtLibrary.statusbar.showMessage("Temizlenecek Veri Yok!",self.dur_msj)

### Tablo 2 İşlemleri  ###

    def list_author_4_2(self):
        ###  DB'den Yazar Listesini alma  ###
        yazar_liste=df_sort_list('Yazari')
        yazar_liste.insert(0,' Seçiniz...')
        cmb=yazar_liste 
        self.QtLibrary.comboBox_4_2_turu.addItems(cmb)

        #####  Liste  genişliği ve adı ayarlama  #######
        self.QtLibrary.tableWidget_4_2_1.setColumnWidth(0,200)
        self.QtLibrary.tableWidget_4_2_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Yazar"))
        self.QtLibrary.tableWidget_4_2_1.setRowCount(1)

        #Kolon aralıklarını ayarlama
        kolonbilgi=[(50,"Sıra No"),(190,"Adı"),(190,"Yazarı"),(130,"Çeviren"),
                        (130,"Turu"),(165,"Yayınevi"),(40,"Yılı"),(40,"Sayfa")]
        for ind,dgr in enumerate(kolonbilgi):
            self.QtLibrary.tableWidget_4_2_2.setColumnWidth(ind,dgr[0])
            self.QtLibrary.tableWidget_4_2_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        self.QtLibrary.tableWidget_4_2_2.setRowCount(1)

    def append_list_author_4_2(self):         
        tur_lst_ekle=str(self.QtLibrary.comboBox_4_2_turu.currentText())
        if tur_lst_ekle != " Seçiniz..."  and tur_lst_ekle not in self.list42:
            self.list42.append(tur_lst_ekle)
            self.QtLibrary.statusbar.showMessage(f"Listeye ' {tur_lst_ekle} ' eklendi",self.dur_msj)
        if '' in self.list42:
            self.list42.remove('') 
        self.list42.sort()
        self.QtLibrary.tableWidget_4_2_1.setRowCount(len(self.list42))
        
        for x,y in enumerate(self.list42):
            self.QtLibrary.tableWidget_4_2_1.setItem(x,0,QTableWidgetItem(str(y)))

    def show_list_author_4_2(self):
        if len(self.list42)!=0:            
            str_sy=0 ### Tablodaki satır sayısı ####
            kayit=[]
            for tur in self.list42:
                 sy,kay=df_srt_fltr('Yazari',tur)
                 str_sy+=sy
                 kayit.append(kay)
            self.QtLibrary.tableWidget_4_2_2.setRowCount(str_sy)

            ####### Verileri satırlara yazma ######
            sr=-1
            for kay in (kayit):
                for kyt in kay:              
                    sr+=1
                    for no, son in enumerate(kyt):           
                        self.QtLibrary.tableWidget_4_2_2.setItem(sr,no,QTableWidgetItem(str(son)))
            self.QtLibrary.statusbar.showMessage("Sonuçlar listelendi",self.dur_msj)
        else:
            self.QtLibrary.statusbar.showMessage("Listelenecek tür seçiniz!",self.dur_msj)
        self.QtLibrary.pushButton_4_2_temizle.setEnabled(True)

    def clear_list_author_4_2(self):
        if len(self.list42)!=0:
            cvb=onay('Kayıtları silmek istiyor musunuz?')
            if cvb==QMessageBox.Yes:
                self.list42.clear() 
                self.QtLibrary.comboBox_4_2_turu.setCurrentIndex(0)

                self.QtLibrary.tableWidget_4_2_1.clear() 
                self.QtLibrary.pushButton_4_2_temizle.setEnabled(False)               
                self.QtLibrary.tableWidget_4_2_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Yazar"))
                self.QtLibrary.tableWidget_4_2_1.setRowCount(1)

                self.QtLibrary.tableWidget_4_2_2.clear()
                self.QtLibrary.tableWidget_4_2_2.setRowCount(1)
                self.QtLibrary.statusbar.showMessage("Veriler temizlendi",self.dur_msj)
                #Kolon aralıklarını ayarlama
                kolonbilgi=[(50,"Sıra No"),(190,"Adı"),(190,"Yazarı"),(130,"Çeviren"),
                                (130,"Turu"),(165,"Yayınevi"),(40,"Yılı"),(40,"Sayfa")]
                for ind,dgr in enumerate(kolonbilgi):
                    self.QtLibrary.tableWidget_4_2_2.setColumnWidth(ind,dgr[0])
                    self.QtLibrary.tableWidget_4_2_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        else:
            self.QtLibrary.statusbar.showMessage("Temizlenecek Veri Yok!",self.dur_msj)

### Tablo 3 İşlemleri  ###

    def list_publish_4_3(self):        
        ###  DB'den Yayınevi Listesini alma  ###       
        yayin_liste=df_sort_list('Yayinevi')
        yayin_liste.insert(0,' Seçiniz...')
        cmb=yayin_liste 
        self.QtLibrary.comboBox_4_3_turu.addItems(cmb)

        #####  Liste  genişliği ve adı ayarlama  #######
        self.QtLibrary.tableWidget_4_3_1.setColumnWidth(0,200)
        self.QtLibrary.tableWidget_4_3_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Yayınevi"))
        self.QtLibrary.tableWidget_4_3_1.setRowCount(1)

        #Kolon aralıklarını ayarlam3
        kolonbilgi=[(50,"Sıra No"),(190,"Adı"),(190,"Yazarı"),(130,"Çeviren"),
                        (130,"Turu"),(165,"Yayınevi"),(40,"Yılı"),(40,"Sayfa")]
        for ind,dgr in enumerate(kolonbilgi):
            self.QtLibrary.tableWidget_4_3_2.setColumnWidth(ind,dgr[0])
            self.QtLibrary.tableWidget_4_3_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        self.QtLibrary.tableWidget_4_3_2.setRowCount(1)

    def append_list_publish_4_3(self):         
        tur_lst_ekle=str(self.QtLibrary.comboBox_4_3_turu.currentText())
        if tur_lst_ekle != " Seçiniz..."  and tur_lst_ekle not in self.list43:
            self.list43.append(tur_lst_ekle)
            self.QtLibrary.statusbar.showMessage(f"Listeye ' {tur_lst_ekle} ' eklendi",self.dur_msj)
        if '' in self.list43:
            self.list43.remove('') 
        self.list43.sort()
        self.QtLibrary.tableWidget_4_3_1.setRowCount(len(self.list43))
        
        for x,y in enumerate(self.list43):
            self.QtLibrary.tableWidget_4_3_1.setItem(x,0,QTableWidgetItem(str(y)))

    def show_list_publish_4_3(self):
        if len(self.list43)!=0:            
            str_sy=0 ### Tablodaki satır sayısı ####
            kayit=[]
            for tur in self.list43:
                 sy,kay=df_srt_fltr('Yayinevi',tur)
                 str_sy+=sy
                 kayit.append(kay)
            self.QtLibrary.tableWidget_4_3_2.setRowCount(str_sy)

            ####### Verileri satırlara yazma ######
            sr=-1
            for kay in (kayit):
                for kyt in kay:              
                    sr+=1
                    for no, son in enumerate(kyt):           
                        self.QtLibrary.tableWidget_4_3_2.setItem(sr,no,QTableWidgetItem(str(son)))
            self.QtLibrary.statusbar.showMessage("Sonuçlar listelendi",self.dur_msj)
        else:
            self.QtLibrary.statusbar.showMessage("Listelenecek tür seçiniz!",self.dur_msj)
        self.QtLibrary.pushButton_4_3_temizle.setEnabled(True)

    def clear_list_publish_4_3(self):
        if len(self.list43)!=0:
            cvb=onay('Kayıtları silmek istiyor musunuz?')
            if cvb==QMessageBox.Yes:
                self.list43.clear() 
                self.QtLibrary.comboBox_4_3_turu.setCurrentIndex(0)

                self.QtLibrary.tableWidget_4_3_1.clear() 
                self.QtLibrary.pushButton_4_3_temizle.setEnabled(False)               
                self.QtLibrary.tableWidget_4_3_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Yayınevi"))
                self.QtLibrary.tableWidget_4_3_1.setRowCount(1)

                self.QtLibrary.tableWidget_4_3_2.clear()
                self.QtLibrary.tableWidget_4_3_2.setRowCount(1)
                self.QtLibrary.statusbar.showMessage("Veriler temizlendi",self.dur_msj)
                #Kolon aralıklarını ayarlama
                kolonbilgi=[(50,"Sıra No"),(190,"Adı"),(190,"Yazarı"),(130,"Çeviren"),
                                (130,"Turu"),(165,"Yayınevi"),(40,"Yılı"),(40,"Sayfa")]
                for ind,dgr in enumerate(kolonbilgi):
                    self.QtLibrary.tableWidget_4_3_2.setColumnWidth(ind,dgr[0])
                    self.QtLibrary.tableWidget_4_3_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        else:
            self.QtLibrary.statusbar.showMessage("Temizlenecek Veri Yok!",self.dur_msj)

### Tablo 4 İşlemleri  ###

    def list_year_4_4(self):
        ###  DB'den Yıl Listesini alma  ###
        yil_liste=df_sort_list('Yili')
        yil_liste.insert(0,' Seçiniz...')
        cmb=yil_liste 
        self.QtLibrary.comboBox_4_4_turu.addItems(cmb)

        #####  Liste  genişliği ve adı ayarlama  #######
        self.QtLibrary.tableWidget_4_4_1.setColumnWidth(0,200)
        self.QtLibrary.tableWidget_4_4_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Yıl"))
        self.QtLibrary.tableWidget_4_4_1.setRowCount(1)

        #Kolon aralıklarını ayarlama
        kolonbilgi=[(50,"Sıra No"),(190,"Adı"),(190,"Yazarı"),(130,"Çeviren"),
                        (130,"Turu"),(165,"Yayınevi"),(40,"Yılı"),(40,"Sayfa")]
        for ind,dgr in enumerate(kolonbilgi):
            self.QtLibrary.tableWidget_4_4_2.setColumnWidth(ind,dgr[0])
            self.QtLibrary.tableWidget_4_4_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        self.QtLibrary.tableWidget_4_4_2.setRowCount(1)

    def append_list_year_4_4(self):         
        tur_lst_ekle=str(self.QtLibrary.comboBox_4_4_turu.currentText())
        if tur_lst_ekle != " Seçiniz..."  and tur_lst_ekle not in self.list44:
            self.list44.append(tur_lst_ekle)
            self.QtLibrary.statusbar.showMessage(f"Listeye ' {tur_lst_ekle} ' eklendi",self.dur_msj)
        if '' in self.list44:
            self.list44.remove('') 
        self.list44.sort()
        self.QtLibrary.tableWidget_4_4_1.setRowCount(len(self.list44))
        
        for x,y in enumerate(self.list44):
            self.QtLibrary.tableWidget_4_4_1.setItem(x,0,QTableWidgetItem(str(y)))

    def show_list_year_4_4(self):
        if len(self.list44)!=0:            
            str_sy=0 ### Tablodaki satır sayısı ####
            kayit=[]
            for tur in self.list44:
                 sy,kay=df_srt_fltr('Yili',tur)
                 str_sy+=sy
                 kayit.append(kay)
            self.QtLibrary.tableWidget_4_4_2.setRowCount(str_sy)
            ####### Verileri satırlara yazma ######
            sr=-1
            for kay in (kayit):
                for kyt in kay:              
                    sr+=1
                    for no, son in enumerate(kyt):           
                        self.QtLibrary.tableWidget_4_4_2.setItem(sr,no,QTableWidgetItem(str(son)))
            self.QtLibrary.statusbar.showMessage("Sonuçlar listelendi",self.dur_msj)
        else:
            self.QtLibrary.statusbar.showMessage("Listelenecek tür seçiniz!",self.dur_msj)
        self.QtLibrary.pushButton_4_4_temizle.setEnabled(True)

    def clear_list_year_4_4(self):
        if len(self.list44)!=0:
            cvb=onay('Kayıtları silmek istiyor musunuz?')
            if cvb==QMessageBox.Yes:
                self.list44.clear() 
                self.QtLibrary.comboBox_4_4_turu.setCurrentIndex(0)

                self.QtLibrary.tableWidget_4_4_1.clear() 
                self.QtLibrary.pushButton_4_4_temizle.setEnabled(False)               
                self.QtLibrary.tableWidget_4_4_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Yıl"))
                self.QtLibrary.tableWidget_4_4_1.setRowCount(1)

                self.QtLibrary.tableWidget_4_4_2.clear()
                self.QtLibrary.tableWidget_4_4_2.setRowCount(1)
                self.QtLibrary.statusbar.showMessage("Veriler temizlendi",self.dur_msj)
                #Kolon aralıklarını ayarlama
                kolonbilgi=[(50,"Sıra No"),(190,"Adı"),(190,"Yazarı"),(130,"Çeviren"),
                                (130,"Turu"),(165,"Yayınevi"),(40,"Yılı"),(40,"Sayfa")]
                for ind,dgr in enumerate(kolonbilgi):
                    self.QtLibrary.tableWidget_4_4_2.setColumnWidth(ind,dgr[0])
                    self.QtLibrary.tableWidget_4_4_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        else:
            self.QtLibrary.statusbar.showMessage("Temizlenecek Veri Yok!",self.dur_msj)

    ##################################
    #####   Tab_5 Fonksiyonlar   #####
    ##################################

    def create_tab_5(self):        
        self.table_5_1_1()
        self.table_5_1_2()
        self.table_5_1_3()
        self.table_5_1_4()

    def table_5_1_1(self):       
        kolonbilgi=[(225,"Yayın Türü"),(50,"Adet")]
        for ind,dgr in enumerate(kolonbilgi):
                self.QtLibrary.tableWidget_5_1_1.setColumnWidth(ind,dgr[0])
                self.QtLibrary.tableWidget_5_1_1.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        kayit=rapor('Turu',self.cnt2) 
        self.QtLibrary.tableWidget_5_1_1.setRowCount(len(kayit))
        for i in range(len(kayit)):                 
            self.QtLibrary.tableWidget_5_1_1.setItem(i,0,QTableWidgetItem(str(kayit.index[i])))          
            self.QtLibrary.tableWidget_5_1_1.setItem(i,1,QTableWidgetItem(str(kayit.values[i])))
       
    def table_5_1_2(self): 
        kolonbilgi=[(225,"Yazar"),(50,"Adet")]
        for ind,dgr in enumerate(kolonbilgi):
                self.QtLibrary.tableWidget_5_1_2.setColumnWidth(ind,dgr[0])
                self.QtLibrary.tableWidget_5_1_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        kayit=rapor('Yazari',self.cnt3) 
        self.QtLibrary.tableWidget_5_1_2.setRowCount(len(kayit))
        for i in range(len(kayit)):                 
            self.QtLibrary.tableWidget_5_1_2.setItem(i,0,QTableWidgetItem(str(kayit.index[i])))          
            self.QtLibrary.tableWidget_5_1_2.setItem(i,1,QTableWidgetItem(str(kayit.values[i])))
    
    def table_5_1_3(self):       
        kolonbilgi=[(225,"Yayınevi"),(50,"Adet")]
        for ind,dgr in enumerate(kolonbilgi):
                self.QtLibrary.tableWidget_5_1_3.setColumnWidth(ind,dgr[0])
                self.QtLibrary.tableWidget_5_1_3.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        kayit=rapor('Yayinevi',self.cnt2) 
        self.QtLibrary.tableWidget_5_1_3.setRowCount(len(kayit))
        for i in range(len(kayit)):                 
            self.QtLibrary.tableWidget_5_1_3.setItem(i,0,QTableWidgetItem(str(kayit.index[i])))          
            self.QtLibrary.tableWidget_5_1_3.setItem(i,1,QTableWidgetItem(str(kayit.values[i])))

    def table_5_1_4(self):       
        kolonbilgi=[(225,"Basım Yılı"),(50,"Adet")]
        for ind,dgr in enumerate(kolonbilgi):
                self.QtLibrary.tableWidget_5_1_4.setColumnWidth(ind,dgr[0])
                self.QtLibrary.tableWidget_5_1_4.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        kayit1=rapor('Yili',self.cnt2)
        kayit=kayit1.sort_index()
        self.QtLibrary.tableWidget_5_1_4.setRowCount(len(kayit))
        for i in range(len(kayit)):                 
            self.QtLibrary.tableWidget_5_1_4.setItem(i,0,QTableWidgetItem(str(kayit.index[i])))          
            self.QtLibrary.tableWidget_5_1_4.setItem(i,1,QTableWidgetItem(str(kayit.values[i])))

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
        self.QtLibrary.comboBox_6_1_2_liste_kisi.addItem(' Seçiniz...')
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
        if self.flag_book and self.flag_user:
            self.QtLibrary.pushButton_6_1_islemi_kaydet.setEnabled(True)
        else:
            self.QtLibrary.pushButton_6_1_islemi_kaydet.setEnabled(False)

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
            else:pass
        else:
            self.QtLibrary.statusbar.showMessage("Kayıtta eksik var. Kontrol edin.",self.dur_msj)

### Tablo 2 İşlemleri  ###

    def list_user_6_2_1 (self):
        self.QtLibrary.comboBox_6_2_1_liste_kisi.clear()
        self.QtLibrary.comboBox_6_2_1_liste_kisi.addItem(' Seçiniz...')
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
            self.QtLibrary.comboBox_6_2_2_liste_kitap.addItem(' Seçiniz...')
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
        if self.flag_book2 and self.flag_user2:
            self.QtLibrary.pushButton_6_2_islemi_kaydet.setEnabled(True)
        else:
            self.QtLibrary.pushButton_6_2_islemi_kaydet.setEnabled(False)

    def save_work2(self):
        if self.flag_book2 and self.flag_user2:
            cvb=onay("İşlemi kaydetmek istiyor musunuz?")
            if cvb==QMessageBox.Yes:
                tdy=datetime.datetime.today()
                kayit=[str(self.kisi_6_2),
                        self.QtLibrary.lineEdit_6_2_id.text(),"","","in",
                        tdy.date(), datetime.datetime.strftime(tdy, '%X ')]  
                uptate_work_to_db(kayit)
                self.QtLibrary.statusbar.showMessage("İşlem kaydedildi.",self.dur_msj)
                self.clear_form_6_2_1()
            else:pass
        else:
            self.QtLibrary.statusbar.showMessage("Kayıtta eksik var. Kontrol edin.",self.dur_msj)

### Tablo 3 İşlemleri  ###

    def create_form_tab_6(self):
        self.QtLibrary.tableWidget_6_2.setRowCount(1)
                #Kolon aralıklarını ayarlama
        kolonbilgi=[(220,"Kitap Adı",),(220,"Yazarı"),(100,"Turu"),
                        (170,"Alan Kişi"),(120,"Telefon"),(180,"Mail"),(100,"Aldığı Tarih")]
        for ind,dgr in enumerate(kolonbilgi):
            self.QtLibrary.tableWidget_6_2.setColumnWidth(ind,dgr[0])
            self.QtLibrary.tableWidget_6_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))

    def listele_6(self):
        sayi=len(df_work_table_book())       
        self.QtLibrary.tableWidget_6_2.setRowCount(sayi)
        islem=df_work_table_book()
        for id,satır in enumerate(islem): 
            for no, son in enumerate(satır):
                self.QtLibrary.tableWidget_6_2.setItem(id,no,QTableWidgetItem(str(son)))
        self.QtLibrary.statusbar.showMessage("Liste görüntülendi.",self.dur_msj)   

    def temizle_6(self):
        self.QtLibrary.tableWidget_6_2.clear()
        self.create_form_tab_6()
        self.QtLibrary.statusbar.showMessage("Liste temizlendi.",self.dur_msj)

# Uygulamanın sürekli çalışması
# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = Ui_MainWindow()
#     ui.setupUi(MainWindow)
#     MainWindow.show()
#     sys.exit(app.exec_())

# Uygulamanın sürekli çalışması
if __name__=="__main__":
    app=QApplication([])
    pencere = Library()
    pencere.show()
    app.exec_()
