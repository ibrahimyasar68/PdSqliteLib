from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox
from bforms.library_py import Ui_MainWindow
from bforms.onay import onay
from acodes.user import User
from acodes.kullanici_yonetimi import KullaniciYonetimi
from acodes.ayarlar import Ayarlar, klasoru_ac
from acodes import tema
from acodes.odunc_gecmisi import OduncGecmisi
from acodes.veri_duzeltme import VeriDuzeltme
from acodes.ek_bilgi import EkBilgiler
from acodes.aranabilir import aranabilir_yap, secili_veri
from acodes.ana_sayfa import AnaSayfa, ana_sayfayi_yerlestir
from acodes import bildirim, ikonlar
from acodes.yerlesim import form_kutusu, islem_sayfasi, liste_sayfasi
from acodes.ortak import OrtakSekmeler, FILTRELER, SECINIZ
from acodes.tablo import satir_verisi, tablo_ayarla, tablo_basliklari, tabloya_yaz
from database.dbframe import (df_book_id_list, df_book_find_by_id, df_user_id_list, df_user_find_by_id,
                              kitap_oduncte, kopya_durumu, uyede_mi, df_work_user_list, df_work_perbook, df_work_table_book)
from database.dbbase import ekle_kayit, degistir_kayit, sil_kayit, save_work_to_db, update_work_to_db
from database.yedek import geri_yukle, otomatik_yedekler, son_otomatik_yedek, yedek_al, yedek_hatasi, yedek_klasoru
from database.dbbase import DB_YOLU
from database.dbframe import genel_ozet
from database.odunc import (ODUNC_SURESI_GUN, gecikme_gunu, geciken_sayisi, gun_sayisi, kalan_gun_yazi,
                            odunc_verilis, tarih_yazi, teslim_tarihi, yaklasan_teslimler)
from database.dbframe import son_eklenenler
from PyQt5.QtCore import pyqtSignal
import os
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
    oturum_kapandi = pyqtSignal()
    PENCERE_BASLIGI = "Yaşar Kütüphanesi - Yönetici Paneli"
    ROL = "Yönetici"

    def __init__(self):
        super().__init__()
        self.QtLibrary = Ui_MainWindow()
        self.QtLibrary.setupUi(self)
        tema.uygula(self)   # .ui renkleri yerine tek tema
        self.bildirim=bildirim.baglan(self,self.QtLibrary.statusbar)   # mesajlar kısa süreli bildirim olarak
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
        self.aktif_kullanici=None

        ###  Tab_1, 2, 4, 5 (Guest ile ortak)  #########
        self.ortak_sekmeleri_kur()
        # Ana sayfa sade: işlem butonları Ayarlar sekmesinde, burada sadece Oturumu Kapat kalır
        self.QtLibrary.pushButton_1_yeni_kullanici.hide()

        ###  Uzun açılır listeler yazdıkça süzülür  ###
        ui=self.QtLibrary
        for cmb,ipucu in ((ui.comboBox_3_2_bul_adi,"Kitap adı yazarak arayın..."),
                          (ui.comboBox_3_3_bul_adi,"Kitap adı yazarak arayın..."),
                          (ui.comboBox_6_1_1_liste_kitap,"Kitap adı yazarak arayın..."),
                          (ui.comboBox_6_1_2_liste_kisi,"Üye adı yazarak arayın..."),
                          (ui.comboBox_6_2_1_liste_kisi,"Üye adı yazarak arayın..."),
                          (ui.comboBox_6_2_2_liste_kitap,"Kitap adı yazarak arayın...")):
            aranabilir_yap(cmb,ipucu)

        ###  Tab_3 Olaylar  #########
        # Ek bilgiler (ISBN, kopya, raf, notlar) formların yanındaki boş alana
        self.ek_3_1=EkBilgiler(self.QtLibrary.tab_3_1)
        self.ek_3_1.setGeometry(830,20,440,330)
        self.ek_3_2=EkBilgiler(self.QtLibrary.tab_3_2)
        self.ek_3_2.setGeometry(30,260,460,330)
        self.ek_3_3=EkBilgiler(self.QtLibrary.tab_3_3, salt_okunur=True)
        self.ek_3_3.setGeometry(30,260,460,330)
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

        self.gecmis=OduncGecmisi()
        self.QtLibrary.tabWidget_6.addTab(self.gecmis,"Ödünç Geçmişi")
        self.QtLibrary.tabWidget_6.currentChanged.connect(self.odunc_sekmesi_degisti)
        self.gecikme_bildir()

        ###  Ayarlar sekmesi: kullanıcılar, yedekleme ve kütüphane bilgileri  ###
        self.ayarlar=Ayarlar([
            ("Kullanıcılar", [
                ("Yeni Kullanıcı Ekle", self.user.show, "Yeni üye veya yönetici kaydı"),
                ("Kullanıcı Yönetimi", self.kullanici_yonetimi, "Kullanıcıları düzenleme, şifre sıfırlama, silme"),
                ("Şifremi Değiştir", self.sifremi_degistir, "Kendi şifrenizi değiştirin")], None),
            ("Yedekleme", [
                ("Yedek Al", self.yedek_al_ekrani, "Veritabanının kopyasını istediğiniz yere kaydedin"),
                ("Yedekten Geri Yükle", self.geri_yukle_ekrani, "Önceki bir yedeğe dönün"),
                ("Yedek Klasörünü Aç", lambda: klasoru_ac(yedek_klasoru()), "Otomatik yedeklerin bulunduğu klasör")],
                self.yedek_bilgisi),
            ("Kütüphane Bilgileri", [], self.kutuphane_bilgisi),
        ])
        self.QtLibrary.tabWidget.addTab(self.ayarlar,"Ayarlar")

        ###  Ana sayfa özet panosu  ###
        self.ana_sayfa=AnaSayfa(
            kartlar=[("kitap","Kitap",tema.VURGU),("disarida","Dışarıda","#0EA5E9"),
                     ("geciken","Geciken",tema.TEHLIKE),("uye","Üye","#16A34A")],
            listeler=[("yaklasan","Teslimi yaklaşan ve geciken kitaplar",["Kitap","Üye","Teslim Tarihi","Durum"],
                       "Önümüzdeki 3 gün içinde teslim edilecek\nveya teslim süresi geçmiş kitap yok."),
                      ("son","Son eklenen kitaplar",["Adı","Yazarı","Kayıt No"],"Henüz kitap eklenmemiş.")],
            cikis_butonu=self.QtLibrary.pushButton_1_cikis)
        ana_sayfayi_yerlestir(self.QtLibrary,self.ana_sayfa)
        k=self.ana_sayfa.kartlar
        k["kitap"].tiklanabilir(self.tum_kitaplari_goster,"Kitap listesini aç")
        k["disarida"].tiklanabilir(self.disaridakileri_goster,"Dışarıdaki kitapları aç")
        k["geciken"].tiklanabilir(self.disaridakileri_goster,"Dışarıdaki kitapları aç (gecikenler kırmızı)")
        k["uye"].tiklanabilir(lambda: self.QtLibrary.tabWidget.setCurrentWidget(self.ayarlar),"Ayarlar > Kullanıcılar")
        l=self.ana_sayfa.listeler
        l["son"].tablo.cellDoubleClicked.connect(
            lambda satir,_: self.kitap_duzenle(satir_verisi(l["son"].tablo,satir)) if satir_verisi(l["son"].tablo,satir) else None)
        l["son"].tablo.setToolTip("Kitabı düzenlemek için çift tıklayın")
        l["yaklasan"].tablo.cellDoubleClicked.connect(
            lambda satir,_: self.iade_ekrani(*satir_verisi(l["yaklasan"].tablo,satir)) if satir_verisi(l["yaklasan"].tablo,satir) else None)
        l["yaklasan"].tablo.setToolTip("İade almak için çift tıklayın")
        self.ana_sayfa_yenile()

        ###  Kitap Kayıt > Veri Düzeltme (sadece bu alt sekme açıkken yenilenir)  ###
        self.duzeltme=VeriDuzeltme(kitap_duzenle=self.kitap_duzenle, degisti=self.yenile)
        self.QtLibrary.tabWidget_3.addTab(self.duzeltme,"Veri Düzeltme")
        self.QtLibrary.tabWidget_3.currentChanged.connect(self.kayit_sekmesi_degisti)

        ###  Çift tıklama: kitap satırı düzenleme ekranını, ödünç satırı iade ekranını açar  ###
        ui=self.QtLibrary
        for tablo in [ui.tableWidget_2]+[getattr(ui,f"tableWidget_4_{no}_2") for no,_,_ in FILTRELER]:
            tablo.setToolTip("Kitabı düzenlemek için satıra çift tıklayın")
            tablo.cellDoubleClicked.connect(lambda satir,_,t=tablo: self.tablodan_kitap_duzenle(t,satir))
        tablo_ayarla(ui.tableWidget_6_2, bos_metin="Şu an dışarıda kitap yok.")
        aktar_6_3=self.aktar_butonu(ui.tableWidget_6_2,"Dışarıdaki Kitaplar",ui.pushButton_6_3_temizle,(40,470,100,60))

        ###  Kitap Verme esnek yerleşim: kitap ve üye kartları yan yana, alanlar pencereyle genişler  ###
        islem_sayfasi(ui.tab_6_1,[
            form_kutusu("Ödünç verilecek kitap",ui.comboBox_6_1_1_liste_kitap,
                        [ui.pushButton_6_1_1_bul_kitap,ui.pushButton_6_1_1_bul_kitap_temizle],ui.formLayoutWidget_11,ui.label_47),
            form_kutusu("Ödünç alacak üye",ui.comboBox_6_1_2_liste_kisi,
                        [ui.pushButton_6_1_2_bul_kisi,ui.pushButton_6_1_2_bul_kisi_temizle],ui.formLayoutWidget_17,ui.label_78)],
            ui.pushButton_6_1_islemi_kaydet)
        islem_sayfasi(ui.tab_6_2,[
            form_kutusu("İade edecek üye",ui.comboBox_6_2_1_liste_kisi,
                        [ui.pushButton_6_2_1_bul_kisi,ui.pushButton_6_2_1_bul_kisi_temizle],ui.formLayoutWidget_18,ui.label_79),
            form_kutusu("İade alınacak kitap",ui.comboBox_6_2_2_liste_kitap,
                        [ui.pushButton_6_2_2_bul_kitap,ui.pushButton_6_2_2_bul_kitap_temizle],ui.formLayoutWidget_12,ui.label_57)],
            ui.pushButton_6_2_islemi_kaydet)
        ui.pushButton_3_3_Sil_2.hide()   # .ui'da tablonun arkasında kalmış, işlevsiz eski bir kopya
        liste_sayfasi(ui.tab_6_3,[ui.pushButton_6_3_listele,ui.pushButton_6_3_temizle,aktar_6_3],ui.tableWidget_6_2)
        ui.tableWidget_6_2.setToolTip("İade almak için satıra çift tıklayın")
        ui.tableWidget_6_2.cellDoubleClicked.connect(lambda satir,_: self.tablodan_iade(satir))

        # Sekme değişince listeler güncellensin (ör. Tab 1'den eklenen yeni üye)
        self.QtLibrary.tabWidget.currentChanged.connect(self.yenile)

        ###  İkonlar  ###
        ikonlar.butonlara_uygula(self)
        ikonlar.sekmelere_uygula(ui.tabWidget,{ui.tab_1:"tab_1",ui.tab_2:"tab_2",ui.tab_3:"tab_3",ui.tab_4:"tab_4",
                                               ui.tab_5:"tab_5",ui.tab_6:"tab_6",self.ayarlar:"ayarlar"})

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
        self.gecmis.yenile()
        self.gecikme_bildir()
        self.ayarlar.yenile()
        self.ana_sayfa_yenile()

    def ana_sayfa_yenile(self):
        o=genel_ozet()
        gecikmis=geciken_sayisi()
        k=self.ana_sayfa.kartlar
        k["kitap"].ayarla(o["kitap"],f"{o['kopya']} kopya")
        k["disarida"].ayarla(o["disarida"],"şu an ödünçte")
        k["geciken"].ayarla(gecikmis,"teslim süresi geçmiş",renk=None if gecikmis else "#94A3B8")
        k["uye"].ayarla(o["uye"],f"{o['admin']} yönetici")
        yaklasan=yaklasan_teslimler()
        self.ana_sayfa.listeler["yaklasan"].doldur(
            [[kitap,uye,tarih_yazi(teslim_tarihi(verilis)),kalan_gun_yazi(verilis)] for kitap,uye,verilis,_,_ in yaklasan],
            vurgulu={i for i,(_,_,verilis,_,_) in enumerate(yaklasan) if gecikme_gunu(verilis)},
            veri=[(u,b) for *_,u,b in yaklasan])
        son=son_eklenenler()
        self.ana_sayfa.listeler["son"].doldur([[adi,yazar,id] for id,adi,yazar in son],veri=[id for id,_,_ in son])

    def tum_kitaplari_goster(self):
        self.QtLibrary.tabWidget.setCurrentWidget(self.QtLibrary.tab_2)
        self.listele()

    def disaridakileri_goster(self):
        self.QtLibrary.tabWidget.setCurrentWidget(self.QtLibrary.tab_6)
        self.QtLibrary.tabWidget_6.setCurrentWidget(self.QtLibrary.tab_6_3)

    def gecikme_bildir(self):
        ###  Teslim süresi geçen kitap varsa Kitap Verme sekmesinin adında göster  ###
        sayi=geciken_sayisi()
        sekme=self.QtLibrary.tabWidget.indexOf(self.QtLibrary.tab_6)
        self.QtLibrary.tabWidget.setTabText(sekme, f"Kitap Verme ({sayi} gecikmiş)" if sayi else "Kitap Verme")
        if sayi:
            self.QtLibrary.statusbar.showMessage(
                f"Teslim süresi ({ODUNC_SURESI_GUN} gün) geçmiş {sayi} kitap var. Kitap Verme > Dışarıdaki Kitaplar", 10000)
        return sayi

    def kayit_sekmesi_degisti(self):
        if self.QtLibrary.tabWidget_3.currentWidget() is self.duzeltme:
            self.duzeltme.yenile()

    def odunc_sekmesi_degisti(self):
        ###  Dışarıdaki kitaplar ve geçmiş sekmesi açılınca güncel hali göster  ###
        sayfa=self.QtLibrary.tabWidget_6.currentWidget()
        if sayfa is self.QtLibrary.tab_6_3:
            self.listele_6()
        elif sayfa is self.gecmis:
            self.gecmis.yenile()

    def tablodan_kitap_duzenle(self,tablo,satir):
        hucre=tablo.item(satir,0)   # ilk kolon: kitap numarası (Id)
        if hucre and hucre.text().isdigit():
            self.kitap_duzenle(int(hucre.text()))

    def kitap_duzenle(self,kitap_id):
        ###  Kitap Kayıt > Kayıt Düzenleme ekranını bu kitapla aç  ###
        q=self.QtLibrary
        q.tabWidget.setCurrentWidget(q.tab_3)
        q.tabWidget_3.setCurrentWidget(q.tab_3_2)
        i=q.comboBox_3_2_bul_adi.findData(kitap_id)
        if i<0:
            q.statusbar.showMessage("Kitap bulunamadı (silinmiş olabilir).",self.dur_msj)
            return
        q.comboBox_3_2_bul_adi.setCurrentIndex(i)
        self.find_item_3_2()

    def tablodan_iade(self,satir):
        idler=satir_verisi(self.QtLibrary.tableWidget_6_2,satir)
        if idler:
            self.iade_ekrani(*idler)

    def iade_ekrani(self,user_id,book_id):
        ###  Kitap Verme > Alma Kaydı ekranını bu üye ve kitap seçili olarak aç  ###
        q=self.QtLibrary
        q.tabWidget_6.setCurrentWidget(q.tab_6_2)
        self.clear_form_6_2_1()
        sayi=lambda x: int(x) if str(x).isdigit() else -1
        i=q.comboBox_6_2_1_liste_kisi.findData(sayi(user_id))
        if i<0:
            q.statusbar.showMessage("Bu ödüncü alan üye silinmiş; iade ekranından seçilemez.",self.dur_msj)
            return
        q.comboBox_6_2_1_liste_kisi.setCurrentIndex(i)
        self.find_user_6_2_1()
        j=q.comboBox_6_2_2_liste_kitap.findData(sayi(book_id))
        if j<0:
            q.statusbar.showMessage("Bu kitap silinmiş; iade ekranından seçilemez.",self.dur_msj)
            return
        q.comboBox_6_2_2_liste_kitap.setCurrentIndex(j)
        self.find_item_6_2_2()

    ##################################
    #####   Tab_1 Fonksiyonlar   #####
    ##################################

    def yedek_bilgisi(self):
        son=son_otomatik_yedek()
        return [("Son otomatik yedek", son.strftime("%d.%m.%Y %H:%M") if son else "Henüz alınmadı"),
                ("Saklanan otomatik yedek", f"{len(otomatik_yedekler())} (en fazla 10, günde bir)"),
                ("Yedek klasörü", yedek_klasoru())]

    def kutuphane_bilgisi(self):
        o=genel_ozet()
        return [("Kitap", f"{o['kitap']} kayıt, {o['kopya']} kopya"),
                ("Kullanıcı", f"{o['uye']} üye, {o['admin']} yönetici"),
                ("Ödünç", f"{o['disarida']} kitap dışarıda, toplam {o['odunc']} işlem"),
                ("Veritabanı", os.path.normpath(DB_YOLU))]

    def kullanici_yonetimi(self):
        KullaniciYonetimi(self.aktif_kullanici, self).exec_()
        self.yenile()

    def yedek_al_ekrani(self):
        varsayilan=os.path.join(yedek_klasoru(), f"DBL_Kayit_yedek_{datetime.date.today():%Y%m%d}.db")
        yol,_=QFileDialog.getSaveFileName(self,"Yedek Al",varsayilan,"Veritabanı (*.db)")
        if not yol:
            return
        try:
            yedek_al(yol)
        except Exception as hata:
            QMessageBox.warning(self,"Uyarı!",f"Yedek alınamadı:\n{hata}")
            return
        QMessageBox.information(self,"Bilgi",f"Yedek alındı:\n{yol}")

    def geri_yukle_ekrani(self):
        yol,_=QFileDialog.getOpenFileName(self,"Yedekten Geri Yükle",yedek_klasoru(),"Veritabanı (*.db)")
        if not yol:
            return
        hata=yedek_hatasi(yol)
        if hata:
            QMessageBox.warning(self,"Uyarı!",hata)
            return
        cvb=onay(f"Mevcut tüm kayıtlar bu yedektekilerle değiştirilecek:\n{os.path.basename(yol)}\n\n"
                 "Mevcut halin yedeği önce otomatik olarak alınacak. Devam edilsin mi?")
        if cvb!=QMessageBox.Yes:
            return
        onceki=geri_yukle(yol)
        self.yenile()
        self.clear_form_6_2_1()
        QMessageBox.information(self,"Bilgi",f"Yedek geri yüklendi.\n\nÖnceki hal şuraya yedeklendi:\n{onceki}")

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
        kayit.extend(self.ek_3_1.degerler())
        if (self.QtLibrary.lineEdit_3_1_adi.text())=="":
            self.QtLibrary.statusbar.showMessage("Kayıt oluşturun",self.dur_msj)
        elif self.ek_3_1.hata():
            QMessageBox.warning(self,"Uyarı!",self.ek_3_1.hata())
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
        self.ek_3_1.temizle()

### Tablo 2 İşlemleri  ###

    def list_items_3_2 (self):
        kitap_listesi(self.QtLibrary.comboBox_3_2_bul_adi)

    def find_item_3_2(self):
        id=secili_veri(self.QtLibrary.comboBox_3_2_bul_adi)
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
        self.ek_3_2.doldur(*degisecek[8:12])
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
        kayit.extend(self.ek_3_2.degerler())
        disarida=kopya_durumu(kayit[0])[1] if kayit[0] else 0
        if self.ek_3_2.hata():
            QMessageBox.warning(self,"Uyarı!",self.ek_3_2.hata())
        elif kayit[9]<disarida:
            QMessageBox.warning(self,"Uyarı!",f"Bu kitabın {disarida} kopyası şu an üyelerde. "
                                              f"Kopya sayısı {disarida}'den az olamaz.")
        elif len(self.QtLibrary.lineEdit_3_2_adi.text())!=0:
            cvb=onay("Kayıt değiştirilsin mi?")
            if cvb==QMessageBox.Yes:
                degistir_kayit(kayit)
                self.QtLibrary.statusbar.showMessage(f"'{kayit[1]}' güncellendi.",self.dur_msj)
                self.clear_form_3_2()
                self.yenile()
        else:
            self.QtLibrary.statusbar.showMessage("Kitap adı boş olamaz. Kontrol edin.",self.dur_msj)

    def clear_form_3_2(self):
        self.QtLibrary.lineEdit_3_2_id.clear()
        self.QtLibrary.lineEdit_3_2_ceviren.clear()
        self.QtLibrary.lineEdit_3_2_yazari.clear()
        self.QtLibrary.lineEdit_3_2_adi.clear()
        self.QtLibrary.lineEdit_3_2_turu.clear()
        self.QtLibrary.lineEdit_3_2_yayinevi.clear()
        self.QtLibrary.lineEdit_3_2_yili.clear()
        self.QtLibrary.lineEdit_3_2_sayfa.clear()
        self.ek_3_2.temizle()
        self.QtLibrary.pushButton_3_2_deg_kaydet.setEnabled(False)
        self.QtLibrary.pushButton_3_2_iptal.setEnabled(False)
        self.QtLibrary.comboBox_3_2_bul_adi.setCurrentIndex(0)

### Tablo 3 İşlemleri  ###

    def list_items_3_3 (self):
        kitap_listesi(self.QtLibrary.comboBox_3_3_bul_adi)

    def find_item_3_3(self):
        id=secili_veri(self.QtLibrary.comboBox_3_3_bul_adi)
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
        self.ek_3_3.doldur(*silinecek[8:12])
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
        self.ek_3_3.temizle()
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
        id=secili_veri(self.QtLibrary.comboBox_6_1_1_liste_kitap)
        if id is None:
            self.QtLibrary.statusbar.showMessage("Seçim yapınız",self.dur_msj)
            return
        kopya,disarida=kopya_durumu(id)
        if disarida>=kopya:
            QMessageBox.information(self,"Uyarı!","Bu kitap başka bir üyededir!" if kopya==1 else
                                    f"Bu kitabın {kopya} kopyasının hepsi üyelerde!")
        else:
            self.show_items_6_1_1(df_book_find_by_id(id))
            if kopya>1:
                self.QtLibrary.statusbar.showMessage(f"Müsait kopya: {kopya-disarida} / {kopya}",8000)

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
        id=secili_veri(self.QtLibrary.comboBox_6_1_2_liste_kisi)
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
        if self.flag_book and self.flag_user and uyede_mi(self.kisi_6_1,self.QtLibrary.lineEdit_6_1_id.text()):
            QMessageBox.information(self,"Uyarı!","Bu kitabın bir kopyası zaten bu üyede. Önce iade alın.")
        elif self.flag_book and self.flag_user:
            cvb=onay("İşlemi kaydetmek istiyor musunuz?")
            if cvb==QMessageBox.Yes:
                tdy=datetime.datetime.today()
                kayit=[str(self.kisi_6_1),
                        self.QtLibrary.lineEdit_6_1_id.text(),
                        tdy.date(), datetime.datetime.strftime(tdy, '%X '),"out","",""]
                save_work_to_db(kayit)
                self.QtLibrary.statusbar.showMessage(
                    f"İşlem kaydedildi. Teslim tarihi: {tarih_yazi(teslim_tarihi(tdy.date()))}",8000)
                self.clear_form_6_1_1()
                self.clear_form_6_1_2()
                self.clear_form_6_2_1()  # İade listesi yeni kaydı göstersin
                self.gecikme_bildir()
        else:
            self.QtLibrary.statusbar.showMessage("Kayıtta eksik var. Kontrol edin.",self.dur_msj)

### Tablo 2 İşlemleri  ###

    def list_user_6_2_1 (self):
        self.QtLibrary.comboBox_6_2_1_liste_kisi.clear()
        self.QtLibrary.comboBox_6_2_1_liste_kisi.addItem(SECINIZ)
        for id,adi,kullanici in df_work_user_list():
            self.QtLibrary.comboBox_6_2_1_liste_kisi.addItem(f"{adi} ({kullanici})",id)

    def find_user_6_2_1(self):
        id=secili_veri(self.QtLibrary.comboBox_6_2_1_liste_kisi)
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
        kitap_id=secili_veri(self.QtLibrary.comboBox_6_2_2_liste_kitap)
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
        verilis=odunc_verilis(self.kisi_6_2,kayit[0])
        bilgi=f"Veriliş: {tarih_yazi(verilis)}, teslim: {tarih_yazi(teslim_tarihi(verilis))}"
        gecikme=gecikme_gunu(verilis)
        self.QtLibrary.statusbar.showMessage(f"{bilgi} ({gecikme} gün gecikti)" if gecikme else bilgi, 10000)

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
                self.gecikme_bildir()
        else:
            self.QtLibrary.statusbar.showMessage("Kayıtta eksik var. Kontrol edin.",self.dur_msj)

### Tablo 3 İşlemleri  ###

    def create_form_tab_6(self):
        self.QtLibrary.tableWidget_6_2.setColumnCount(9)
        self.QtLibrary.tableWidget_6_2.setRowCount(1)
        tablo_basliklari(self.QtLibrary.tableWidget_6_2,
                         [(190,"Kitap Adı"),(160,"Yazarı"),(90,"Türü"),(160,"Alan Kişi"),(110,"Telefon"),
                          (160,"Mail"),(95,"Aldığı Tarih"),(95,"Teslim Tarihi"),(45,"Gün")])

    def listele_6(self):
        ###  En eski ödünç en üstte; teslim süresi geçenler kırmızı  ###
        satirlar,idler,gecikenler=[],[],set()
        for r,(kitap,yazar,tur,kisi,telefon,mail,verilis,user_id,book_id) in enumerate(df_work_table_book()):
            gun=gun_sayisi(verilis)
            satirlar.append([kitap,yazar,tur,kisi,telefon,mail,tarih_yazi(verilis),
                             tarih_yazi(teslim_tarihi(verilis)),"" if gun is None else gun])
            idler.append((user_id,book_id))
            if gecikme_gunu(verilis):
                gecikenler.add(r)
        tabloya_yaz(self.QtLibrary.tableWidget_6_2, satirlar, vurgulu=gecikenler, veri=idler)
        gecikmis=len(gecikenler)
        mesaj=f"Dışarıda {len(satirlar)} kitap var"
        self.QtLibrary.statusbar.showMessage(f"{mesaj}, {gecikmis} tanesinin teslim süresi geçmiş." if gecikmis else mesaj+".",self.dur_msj)

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
