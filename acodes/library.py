from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox
from bforms.library_py import Ui_MainWindow
from acodes.onay import onay
from acodes.user import User
from acodes.kullanici_yonetimi import KullaniciYonetimi
from acodes.ayarlar import Ayarlar, klasoru_ac
from acodes import kilavuz
from acodes import tema
from acodes.odunc_gecmisi import OduncGecmisi
from acodes.veri_duzeltme import VeriDuzeltme
from acodes.kitap_ekrani import KitapEkrani
from acodes.odunc_ekrani import OduncEkrani
from acodes.disa_aktar import disa_aktar, sag_tik_menusu
from acodes.ana_sayfa import AnaSayfa, ana_sayfayi_yerlestir
from acodes import arka_plan, bildirim, ikonlar, kisayollar
from acodes.yan_menu import YanMenu, menuyu_yerlestir, segmente_cevir
from acodes.ortak import OrtakSekmeler
from acodes.tablo import satir_verisi
from database.dbframe import df_book_find_by_id, genel_ozet, son_eklenenler
from database.yedek import geri_yukle, otomatik_yedekler, son_otomatik_yedek, yedek_al, yedek_hatasi, yedek_klasoru
from database.dbbase import DB_YOLU
from database.odunc import (ODUNC_SURESI_GUN, gecikme_gunu, geciken_sayisi, kalan_gun_yazi, tarih_yazi,
                            teslim_tarihi, yaklasan_teslimler)
from PyQt5.QtCore import pyqtSignal
import os
import datetime


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
        self.arka_plan=arka_plan.uygula(self)   # yaprak fotoğrafı tüm panelin zemininde
        self.bildirim=bildirim.baglan(self,self.QtLibrary.statusbar)   # mesajlar kısa süreli bildirim olarak
        self.user=User(self)
        self.user.kaydedildi.connect(self.kullanici_eklendi)
        self.QtLibrary.tabWidget.setCurrentIndex(0)

        ###  Property  #########
        self.dur_msj=2000
        self.aktif_kullanici=None

        ###  Tab_1, 2, 4, 5 (Guest ile ortak)  #########
        self.ortak_sekmeleri_kur()

        ###  Kitap Verme: ödünç verme, iade alma ve dışarıdaki kitaplar tek ekranda  ###
        ui=self.QtLibrary
        self.odunc=OduncEkrani(mesaj=lambda metin: self.QtLibrary.statusbar.showMessage(metin,8000),
                               degisti=self.yenile)
        ui.tabWidget_6.addTab(self.odunc,"Ödünç ve İade")
        self.odunc.btn_aktar.clicked.connect(lambda: disa_aktar(self,self.odunc.tablo,"Dışarıdaki Kitaplar"))
        sag_tik_menusu(self,self.odunc.tablo,"Dışarıdaki Kitaplar")
        self.gecmis=OduncGecmisi()
        self.QtLibrary.tabWidget_6.addTab(self.gecmis,"Ödünç Geçmişi")
        self.QtLibrary.tabWidget_6.currentChanged.connect(self.odunc_sekmesi_degisti)
        self.gecikme_bildir()

        ###  Ayarlar sekmesi: kullanıcılar, yedekleme ve kütüphane bilgileri  ###
        self.ayarlar=Ayarlar([
            ("Kullanıcılar", [
                ("Yeni Kullanıcı Ekle", self.user.ac, "Yeni üye veya yönetici kaydı"),
                ("Kullanıcı Yönetimi", self.kullanici_yonetimi, "Kullanıcıları düzenleme, şifre sıfırlama, silme"),
                ("Şifremi Değiştir", self.sifremi_degistir, "Kendi şifrenizi değiştirin")], None),
            ("Yedekleme", [
                ("Yedek Al", self.yedek_al_ekrani, "Veritabanının kopyasını istediğiniz yere kaydedin"),
                ("Yedekten Geri Yükle", self.geri_yukle_ekrani, "Önceki bir yedeğe dönün"),
                ("Yedek Klasörünü Aç", lambda: klasoru_ac(yedek_klasoru()), "Otomatik yedeklerin bulunduğu klasör")],
                self.yedek_bilgisi),
            ("Kütüphane Bilgileri", [], self.kutuphane_bilgisi),
        ], kilavuz=kilavuz.YONETICI)
        self.QtLibrary.tabWidget.addTab(self.ayarlar,"Ayarlar")

        ###  Ana sayfa özet panosu  ###
        self.ana_sayfa=AnaSayfa(
            kartlar=[("kitap","Kitap",tema.VURGU),("disarida","Dışarıda",tema.BILGI),
                     ("geciken","Geciken",tema.TEHLIKE),("uye","Üye",tema.YESIL)],
            listeler=[("yaklasan","Teslimi yaklaşan ve geciken kitaplar",["Kitap","Üye","Teslim Tarihi","Durum"],
                       "Önümüzdeki 3 gün içinde teslim edilecek\nveya teslim süresi geçmiş kitap yok."),
                      ("son","Son eklenen kitaplar",["Adı","Yazarı","Kayıt No"],"Henüz kitap eklenmemiş.")])
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

        ###  Kitap Kayıt: ekleme / düzenleme / silme tek ekranda; Veri Düzeltme sadece açıkken yenilenir  ###
        ui=self.QtLibrary
        self.kitaplar=KitapEkrani(mesaj=lambda metin: self.QtLibrary.statusbar.showMessage(metin,self.dur_msj),
                                  degisti=self.yenile)
        ui.tabWidget_3.addTab(self.kitaplar,"Kitaplar")
        self.duzeltme=VeriDuzeltme(kitap_duzenle=self.kitap_duzenle, degisti=self.yenile)
        self.QtLibrary.tabWidget_3.addTab(self.duzeltme,"Veri Düzeltme")
        self.QtLibrary.tabWidget_3.currentChanged.connect(self.kayit_sekmesi_degisti)

        ###  Çift tıklama: kitap satırı Kitap Kayıt ekranında açılır  ###
        ui=self.QtLibrary
        for tablo in (ui.tableWidget_2,self.filtre.tablo):
            tablo.setToolTip("Kitabı düzenlemek için satıra çift tıklayın")
            tablo.cellDoubleClicked.connect(lambda satir,_,t=tablo: self.tablodan_kitap_duzenle(t,satir))

        # Sekme değişince listeler güncellensin (ör. Tab 1'den eklenen yeni üye)
        self.QtLibrary.tabWidget.currentChanged.connect(self.yenile)

        ###  İkonlar  ###
        ikonlar.butonlara_uygula(self)
        sayfalar={ui.tab_1:"tab_1",ui.tab_2:"tab_2",ui.tab_3:"tab_3",ui.tab_4:"tab_4",
                  ui.tab_5:"tab_5",ui.tab_6:"tab_6",self.ayarlar:"ayarlar"}
        ikonlar.sekmelere_uygula(ui.tabWidget,sayfalar)

        ###  Sol kenar menüsü (sekme çubuğu yerine) ve alt sekmeler yerine üstte anahtar  ###
        self.yan_menu=YanMenu(ui.tabWidget,sayfalar,ui.pushButton_1_cikis)
        menuyu_yerlestir(self,self.yan_menu)
        kisayollar.panele_kur(self,ui.tabWidget,ui.tab_2,self.arama)   # Ctrl+1..9 menü, Ctrl+F arama
        for alt_sekmeler in (ui.tabWidget_3,ui.tabWidget_5,ui.tabWidget_6):
            segmente_cevir(alt_sekmeler)

    def yenile(self):
        ###  Kayıt/üye/ödünç değişikliklerinden sonra listeleri ve istatistikleri güncelleme  ###
        self.kitaplar.yenile()
        self.filtre.yenile()
        self.create_tab_5()
        self.odunc.yenile()
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
        k["geciken"].ayarla(gecikmis,"teslim süresi geçmiş",renk=None if gecikmis else tema.SOLUK)
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
        self.QtLibrary.tabWidget_6.setCurrentWidget(self.odunc)

    def gecikme_bildir(self):
        ###  Teslim süresi geçen kitap varsa Kitap Verme sekmesinin adında göster  ###
        sayi=geciken_sayisi()
        sekme=self.QtLibrary.tabWidget.indexOf(self.QtLibrary.tab_6)
        self.QtLibrary.tabWidget.setTabText(sekme, f"Kitap Verme ({sayi} gecikmiş)" if sayi else "Kitap Verme")
        if hasattr(self,"yan_menu"):
            self.yan_menu.yenile()
        if sayi:
            self.QtLibrary.statusbar.showMessage(
                f"Teslim süresi ({ODUNC_SURESI_GUN} gün) geçmiş {sayi} kitap var. Kitap Verme > Ödünç ve İade", 10000)
        return sayi

    def kayit_sekmesi_degisti(self):
        if self.QtLibrary.tabWidget_3.currentWidget() is self.duzeltme:
            self.duzeltme.yenile()

    def odunc_sekmesi_degisti(self):
        ###  Dışarıdaki kitaplar ve geçmiş sekmesi açılınca güncel hali göster  ###
        sayfa=self.QtLibrary.tabWidget_6.currentWidget()
        if sayfa is self.odunc:
            self.odunc.yenile()
        elif sayfa is self.gecmis:
            self.gecmis.yenile()

    def tablodan_kitap_duzenle(self,tablo,satir):
        hucre=tablo.item(satir,0)   # ilk kolon: kitap numarası (Id)
        if hucre and hucre.text().isdigit():
            self.kitap_duzenle(int(hucre.text()))

    def kitap_duzenle(self,kitap_id):
        ###  Kitap Kayıt > Kitaplar ekranını bu kitapla aç  ###
        q=self.QtLibrary
        q.tabWidget.setCurrentWidget(q.tab_3)
        q.tabWidget_3.setCurrentWidget(self.kitaplar)
        if df_book_find_by_id(kitap_id) is None:
            q.statusbar.showMessage("Kitap bulunamadı (silinmiş olabilir).",self.dur_msj)
            return
        self.kitaplar.sec(kitap_id)

    def iade_ekrani(self,user_id,book_id):
        ###  Kitap Verme > Ödünç ve İade ekranını bu ödünç seçili olarak aç  ###
        self.disaridakileri_goster()
        self.odunc.sec(user_id,book_id)

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

    def kullanici_eklendi(self,kullanici):
        ###  Yeni kullanıcı kaydından sonra: listeler (ödünç verme, bilgiler) yenilenir, aynı menüde kalınır  ###
        self.yenile()
        self.QtLibrary.statusbar.showMessage(f"'{kullanici}' kullanıcısı kaydedildi.",self.dur_msj*2)

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
        QMessageBox.information(self,"Bilgi",f"Yedek geri yüklendi.\n\nÖnceki hal şuraya yedeklendi:\n{onceki}")
