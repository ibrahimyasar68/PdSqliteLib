from PyQt5.QtWidgets import *
from bforms.guest_py import Ui_MainWindow
from bforms.onay import onay
from database.dbframe import *
from database.dbbase import *

class Guest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.QtLibrary = Ui_MainWindow()
        self.QtLibrary.setupUi(self)
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

        ###  Tab_1 Olaylar  #########
        self.QtLibrary.pushButton_1_cikis.clicked.connect(self.lib_exit)

        ###  Tab_2 Olaylar  #########
        self.create_form_tab2()
        self.QtLibrary.pushButton_2_listele.clicked.connect(self.listele)
        self.QtLibrary.pushButton_2_temizle.clicked.connect(self.temizle)    
        ###  Tab_3 Olaylar  #########

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
    ##################################
    #####   Tab_1 Fonksiyonlar   #####
    ##################################

    def lib_exit (self):
        self.close()

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
        tur_liste.insert(0,' Seçiniz...')
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
        yazar_liste.insert (0,' Seçiniz...')
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
    pencere = Guest()
    pencere.show()
    app.exec_()
