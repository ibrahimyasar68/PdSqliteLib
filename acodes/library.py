from PyQt5.QtWidgets import *
from bforms.library_py import Ui_MainWindow
from acodes.user import User
from database.dbframe import *
from bforms.onay import onay
from database.dbbase import *

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
        self.list_items_3_3()  
        self.QtLibrary.pushButton_3_3_bul.clicked.connect(self.find_item_3_3)    
        self.QtLibrary.pushButton_3_3_Sil.clicked.connect(self.delete_item_3_3)     

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
        self.create_tab_5_1()

    ##################################
    #####   Tab_1 Fonksiyonlar   #####
    ##################################

    def lib_exit (self):
        self.close()

    def new_user(self):
        self.user.show()
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
        id=(df_count_items())+1      
        kayit=[]
        kayit.append(id)        
        kayit.append(self.QtLibrary.lineEdit_3_1_adi.text())
        kayit.append(self.QtLibrary.lineEdit_3_1_yazari.text())   
        kayit.append(self.QtLibrary.lineEdit_3_1_ceviren.text())
        kayit.append(self.QtLibrary.lineEdit_3_1_turu.text())
        kayit.append(self.QtLibrary.lineEdit_3_1_yayinevi.text())
        kayit.append(self.QtLibrary.lineEdit_3_1_yili.text())
        kayit.append(self.QtLibrary.lineEdit_3_1_sayfa.text())

        if (self.QtLibrary.lineEdit_3_1_adi.text())=="":
            self.QtLibrary.statusbar.showMessage("Kayıt oluşturun",self.dur_msj) 
        else:          
            cvb=onay(f"{(self.QtLibrary.lineEdit_3_1_adi.text())} kaydedilsin mi?")
            if cvb==QMessageBox.Yes:        
                # ekle_kayit(kayit)
                print(kayit)
                self.QtLibrary.statusbar.showMessage(f"'{(self.QtLibrary.lineEdit_3_1_adi.text())}' kaydedildi",self.dur_msj)
            else:pass  
    def clear_form_3_1(self):
        self.QtLibrary.lineEdit_3_1_adi.clear()
        self.QtLibrary.lineEdit_3_1_yazari.clear()
        self.QtLibrary.lineEdit_3_1_ceviren.clear()
        self.QtLibrary.lineEdit_3_1_turu.clear()    
        self.QtLibrary.lineEdit_3_1_yayinevi.clear()
        self.QtLibrary.lineEdit_3_1_yili.clear()

### Tablo 2 İşlemleri  ###
    def list_items_3_2 (self):
        cmb=(df_sort_list('Adi'))
        cmb[0]=(' Seçiniz...')
        self.QtLibrary.comboBox_3_2_bul_adi.addItems(cmb)

    def find_item_3_2(self):
        txt=self.QtLibrary.comboBox_3_2_bul_adi.currentText()
        if txt==(' Seçiniz...'):
            self.QtLibrary.statusbar.showMessage("Seçim yapınız",self.dur_msj)
        else:
            sayi,kyt=df_find_by_sort('Adi',txt)
            if sayi==0: 
                self.QtLibrary.statusbar.showMessage(f"'{txt}' kaydı bulunamadı",self.dur_msj)
            else:
                if sayi>1:
                    cvb=onay(f"'{txt}' adında {sayi} kayıt bulundu.\nİlk kayıt gösterilsin mi?")
                    if cvb==QMessageBox.No:
                        self.QtLibrary.statusbar.showMessage("Yeniden kayıt girin")
                    else:
                        self.show_items_3_2(kyt)    
                else:
                    self.show_items_3_2(kyt)  

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
        self.QtLibrary.comboBox_3_2_bul_adi.setCurrentIndex(0) 
        
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
            

    def update_item_3_2(self):
        kayit=[]
        kayit.append(self.QtLibrary.lineEdit_3_2_id.text())       
        kayit.append(self.QtLibrary.lineEdit_3_2_adi.text())
        kayit.append(self.QtLibrary.lineEdit_3_2_yazari.text())      
        kayit.append(self.QtLibrary.lineEdit_3_2_ceviren.text())
        kayit.append(self.QtLibrary.lineEdit_3_2_turu.text())
        kayit.append(self.QtLibrary.lineEdit_3_2_yayinevi.text())
        kayit.append(self.QtLibrary.lineEdit_3_2_yili.text())
        kayit.append(self.QtLibrary.lineEdit_3_2_sayfa.text())
        if len(self.QtLibrary.lineEdit_3_2_adi.text())!=0:
            cvb=onay("Kayıt değiştirilsin mi?")
            if cvb==QMessageBox.Yes:
                # degistir_kayit(kayit)
                print(kayit)
                self.QtLibrary.statusbar.showMessage(f"'{kayit[1]}' güncellendi.",self.dur_msj)
                self.clear_form_3_2()               
            else:pass
        else:
            self.QtLibrary.statusbar.showMessage("Kayıtta değişiklik yapılmadı.Kontrol edin",self.dur_msj)

### Tablo 3 İşlemleri  ###

    def list_items_3_3 (self):
        cmb=(df_sort_list('Adi'))
        cmb[0]=(' Seçiniz...')
        self.QtLibrary.comboBox_3_3_bul_adi.addItems(cmb)

    def find_item_3_3(self):
        txt=self.QtLibrary.comboBox_3_3_bul_adi.currentText()
        if txt==(' Seçiniz...'):
            self.QtLibrary.statusbar.showMessage("Seçim yapınız",self.dur_msj)
        else:
            sayi,kyt=df_find_by_sort('Adi',txt)
            if sayi==0: 
                self.QtLibrary.statusbar.showMessage(f"'{txt}' kaydı bulunamadı",self.dur_msj)
            else:
                if sayi>1:
                    cvb=onay(f"'{txt}' adında {sayi} kayıt bulundu.\nİlk kayıt gösterilsin mi?")
                    if cvb==QMessageBox.No:
                        self.QtLibrary.statusbar.showMessage("Yeniden kayıt girin")
                    else:
                        self.show_items_3_3(kyt)    
                else:
                    self.show_items_3_3(kyt)  

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
        self.QtLibrary.comboBox_3_3_bul_adi.setCurrentIndex(0) 
        
    def show_items_3_3(self,kyt):
        degisecek=kyt 
        self.QtLibrary.lineEdit_3_3_id.setText(str(degisecek[0]))    
        self.QtLibrary.lineEdit_3_3_adi.setText(degisecek[1])
        self.QtLibrary.lineEdit_3_3_yazari.setText(degisecek[2])
        self.QtLibrary.lineEdit_3_3_ceviren.setText(degisecek[3])
        self.QtLibrary.lineEdit_3_3_turu.setText(degisecek[4])
        self.QtLibrary.lineEdit_3_3_yayinevi.setText(degisecek[5])
        self.QtLibrary.lineEdit_3_3_yili.setText(degisecek[6])
        self.QtLibrary.lineEdit_3_3_sayfa.setText(degisecek[7])
        self.QtLibrary.statusbar.showMessage(f"{self.QtLibrary.comboBox_3_3_bul_adi.currentText()} bilgileri yazıldı.",self.dur_msj)
        self.QtLibrary.pushButton_3_3_Sil.setEnabled(True)
            
    def delete_item_3_3(self):
        cvb=onay("Kayıt silinsin mi?")
        if cvb==QMessageBox.Yes:
            # sil_adi(kayit)
            print(self.QtLibrary.lineEdit_3_3_adi.text())            
            self.QtLibrary.statusbar.showMessage(f"{self.QtLibrary.comboBox_3_3_bul_adi.currentText()} silindi",self.dur_msj)
            self.clear_form_3_3()
        else:pass

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
        tur_liste[0]=(' Seçiniz...')
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
            else:pass            
        else:
            self.QtLibrary.statusbar.showMessage("Temizlenecek Veri Yok!",self.dur_msj)

### Tablo 2 İşlemleri  ###

    def list_author_4_2(self):
        ###  DB'den Yazar Listesini alma  ###
        yazar_liste=df_sort_list('Yazari')
        yazar_liste[0]=(' Seçiniz...')
        cmb=yazar_liste 
        self.QtLibrary.comboBox_4_2_turu.addItems(cmb)

        #####  Liste  genişliği ve adı ayarlama  #######
        self.QtLibrary.tableWidget_4_2_1.setColumnWidth(0,200)
        self.QtLibrary.tableWidget_4_2_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Tür"))
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
                self.QtLibrary.tableWidget_4_2_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Tür"))
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
            else:pass            
        else:
            self.QtLibrary.statusbar.showMessage("Temizlenecek Veri Yok!",self.dur_msj)


### Tablo 3 İşlemleri  ###

    def list_publish_4_3(self):        
        ###  DB'den Yayınevi Listesini alma  ###       
        yayin_liste=df_sort_list('Yayinevi')
        yayin_liste[0]=(' Seçiniz...')
        cmb=yayin_liste 
        self.QtLibrary.comboBox_4_3_turu.addItems(cmb)

        #####  Liste  genişliği ve adı ayarlama  #######
        self.QtLibrary.tableWidget_4_3_1.setColumnWidth(0,200)
        self.QtLibrary.tableWidget_4_3_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Tür"))
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
                self.QtLibrary.tableWidget_4_3_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Tür"))
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
            else:pass            
        else:
            self.QtLibrary.statusbar.showMessage("Temizlenecek Veri Yok!",self.dur_msj)


### Tablo 4 İşlemleri  ###

    def list_year_4_4(self):
        ###  DB'den Yıl Listesini alma  ###
        yil_liste=df_sort_list('Yili')
        yil_liste[0]=(' Seçiniz...')
        cmb=yil_liste 
        self.QtLibrary.comboBox_4_4_turu.addItems(cmb)

        #####  Liste  genişliği ve adı ayarlama  #######
        self.QtLibrary.tableWidget_4_4_1.setColumnWidth(0,200)
        self.QtLibrary.tableWidget_4_4_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Tür"))
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
                self.QtLibrary.tableWidget_4_4_1.setHorizontalHeaderItem(0,QTableWidgetItem("Seçilen Tür"))
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
            else:pass            
        else:
            self.QtLibrary.statusbar.showMessage("Temizlenecek Veri Yok!",self.dur_msj)

    ##################################
    #####   Tab_5 Fonksiyonlar   #####
    ##################################

    def create_tab_5_1(self):        
        self.table_5_1_1()
        self.table_5_1_2()
        self.table_5_1_3()
        self.table_5_1_4()

    def table_5_1_1(self):       
        kolonbilgi=[(225,"Yayın Türü"),(50,"Adet")]
        for ind,dgr in enumerate(kolonbilgi):
                self.QtLibrary.tableWidget_5_1_1.setColumnWidth(ind,dgr[0])
                self.QtLibrary.tableWidget_5_1_1.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        self.QtLibrary.tableWidget_5_1_1.setRowCount(self.cnt2)
        kayit=rapor('Turu',self.cnt2) 
        for i in range(self.cnt2):                 
            self.QtLibrary.tableWidget_5_1_1.setItem(i,0,QTableWidgetItem(kayit.index[i]))          
            self.QtLibrary.tableWidget_5_1_1.setItem(i,1,QTableWidgetItem(str(kayit.values[i])))
       

    def table_5_1_2(self): 
        kolonbilgi=[(225,"Yazar"),(50,"Adet")]
        for ind,dgr in enumerate(kolonbilgi):
                self.QtLibrary.tableWidget_5_1_2.setColumnWidth(ind,dgr[0])
                self.QtLibrary.tableWidget_5_1_2.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        self.QtLibrary.tableWidget_5_1_2.setRowCount(self.cnt3)
        kayit=rapor('Yazari',self.cnt3) 
        for i in range(self.cnt3):                 
            self.QtLibrary.tableWidget_5_1_2.setItem(i,0,QTableWidgetItem(kayit.index[i]))          
            self.QtLibrary.tableWidget_5_1_2.setItem(i,1,QTableWidgetItem(str(kayit.values[i])))
    
    def table_5_1_3(self):       
        kolonbilgi=[(225,"Yayınevi"),(50,"Adet")]
        for ind,dgr in enumerate(kolonbilgi):
                self.QtLibrary.tableWidget_5_1_3.setColumnWidth(ind,dgr[0])
                self.QtLibrary.tableWidget_5_1_3.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        self.QtLibrary.tableWidget_5_1_3.setRowCount(self.cnt2)
        kayit=rapor('Yayinevi',self.cnt2) 
        for i in range(self.cnt2):                 
            self.QtLibrary.tableWidget_5_1_3.setItem(i,0,QTableWidgetItem(kayit.index[i]))          
            self.QtLibrary.tableWidget_5_1_3.setItem(i,1,QTableWidgetItem(str(kayit.values[i])))

    def table_5_1_4(self):       
        kolonbilgi=[(225,"Basım Yılı"),(50,"Adet")]
        for ind,dgr in enumerate(kolonbilgi):
                self.QtLibrary.tableWidget_5_1_4.setColumnWidth(ind,dgr[0])
                self.QtLibrary.tableWidget_5_1_4.setHorizontalHeaderItem(ind,QTableWidgetItem(dgr[1]))
        self.QtLibrary.tableWidget_5_1_4.setRowCount(self.cnt2)
        kayit1=rapor('Yili',self.cnt2)
        kayit=kayit1.sort_index()
        for i in range(self.cnt2):                 
            self.QtLibrary.tableWidget_5_1_4.setItem(i,0,QTableWidgetItem(kayit.index[i]))          
            self.QtLibrary.tableWidget_5_1_4.setItem(i,1,QTableWidgetItem(str(kayit.values[i])))


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
