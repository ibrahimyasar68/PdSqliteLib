from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox
import os
import datetime

from acodes import kilavuz, tema
from acodes.ana_sayfa import AnaSayfa
from acodes.ayarlar import IPUCU_YONETICI, Ayarlar, klasoru_ac
from acodes.disa_aktar import disa_aktar, sag_tik_menusu
from acodes.kitap_ekrani import KitapEkrani
from acodes.komut_paleti import eslesir
from acodes.kullanici_yonetimi import KullaniciYonetimi
from acodes.odunc_ekrani import OduncEkrani
from acodes.odunc_gecmisi import OduncGecmisi
from acodes.olaylar import olaylar
from acodes.onay import onay
from acodes.panel import Panel, Sayfa
from acodes.tablo import satir_verisi
from acodes.user import User
from acodes.veri_duzeltme import VeriDuzeltme
from database.baglanti import DB_YOLU
from database.istatistik import genel_ozet
from database.kitaplar import kitap_bul, son_eklenenler
from database.kullanicilar import secim_listesi as uye_secim_listesi
from database.odunc import (ODUNC_SURESI_GUN, disaridakiler, gecikme_gunu, geciken_sayisi, kalan_gun_yazi, kopya_durumu,
                            odunc_gecmisi, tarih_yazi, teslim_tarihi, yaklasan_teslimler)
from database.yedek import geri_yukle, otomatik_yedekler, son_otomatik_yedek, yedek_al, yedek_hatasi, yedek_klasoru


def kitap_karti_alti(kitap, kopya, disarida):
    """Ana sayfadaki Kitap kartının alt satırı: kopya sayısı yalnızca kayıt sayısından farklıysa yazılır
    (aynı sayıyı iki kez göstermesin), yanında raftaki kopya sayısı."""
    rafta = "hepsi rafta" if disarida <= 0 else f"{kopya - disarida} rafta"
    return f"{kopya} kopya, {rafta}" if kopya != kitap else rafta


## Yönetici paneli: ortak sayfalara ek olarak Kitap Kayıt, Kitap Verme ve yönetim ayarları
class Library(Panel):
    PENCERE_BASLIGI = "Yaşar Kütüphanesi - Yönetici Paneli"
    ROL = "Yönetici"

    def __init__(self):
        super().__init__()
        self.gecikme_bildir()

    def sayfalari_kur(self):
        self.user=User(self)
        self.user.kaydedildi.connect(self.kullanici_eklendi)

        ###  Kitap Kayıt: ekleme / düzenleme / silme tek ekranda; Veri Düzeltme sadece açıkken yenilenir  ###
        self.kitaplar=KitapEkrani(mesaj=lambda metin,tur=None: self.bildirim.mesaj(metin,tur,self.dur_msj),
                                  bildir=self.bildirim.eylemli)
        sag_tik_menusu(self,self.kitaplar.tablo,"Kitaplar")
        self.duzeltme=VeriDuzeltme(kitap_duzenle=self.kitap_duzenle)
        self.kayit=self.alt_sekmeli("Kitap Kayıt",[("Kitaplar",self.kitaplar),("Veri Düzeltme",self.duzeltme)])
        self.alt_sekmeler[self.kayit].currentChanged.connect(self.kayit_sekmesi_degisti)

        ###  Kitap Verme: ödünç verme, iade alma ve dışarıdaki kitaplar tek ekranda; ödünç geçmişi  ###
        self.odunc=OduncEkrani(mesaj=lambda metin,tur=None: self.bildirim.mesaj(metin,tur,8000),
                               bildir=self.bildirim.eylemli)
        self.odunc.btn_aktar.clicked.connect(lambda: disa_aktar(self,self.odunc.tablo,"Dışarıdaki Kitaplar"))
        sag_tik_menusu(self,self.odunc.tablo,"Dışarıdaki Kitaplar")
        self.odunc.tablo.sag_tik_eylemleri.append(lambda satir: [
            ("İade al",self.odunc.iade_al,True),("Hatırlatma metnini kopyala",self.odunc.hatirlatma_kopyala,True)])
        self.gecmis=OduncGecmisi()
        self.verme=self.alt_sekmeli("Kitap Verme",[("Ödünç ve İade",self.odunc),("Ödünç Geçmişi",self.gecmis)])
        self.alt_sekmeler[self.verme].currentChanged.connect(self.odunc_sekmesi_degisti)

        ###  Ayarlar: kullanıcılar, yedekleme ve kütüphane bilgileri  ###
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
            ("Kütüphane bilgileri", [], self.kutuphane_bilgisi),
        ], kilavuz=kilavuz.YONETICI, ipucu=IPUCU_YONETICI)

        ###  Ana sayfa özet panosu  ###
        self.ana_sayfa=AnaSayfa(
            kartlar=[("kitap","Kitap",tema.VURGU,"kitap"),("disarida","Dışarıda",tema.BILGI,"takas"),
                     ("geciken","Geciken",tema.TEHLIKE,"saat"),("uye","Üye",tema.YESIL,"kullanicilar")],
            listeler=[("yaklasan","Teslimi yaklaşan ve geciken kitaplar",["Kitap","Üye","Teslim Tarihi","Durum"],
                       "Önümüzdeki 3 gün içinde teslim edilecek\nveya teslim süresi geçmiş kitap yok."),
                      ("son","Son eklenen kitaplar",["Adı","Yazarı","Kayıt No"],"Henüz kitap eklenmemiş.")])
        k=self.ana_sayfa.kartlar
        k["kitap"].tiklanabilir(self.tum_kitaplari_goster,"Kitap listesini aç")
        k["disarida"].tiklanabilir(self.disaridakileri_goster,"Dışarıdaki kitapları aç")
        k["geciken"].tiklanabilir(self.disaridakileri_goster,"Dışarıdaki kitapları aç (gecikenler kırmızı)")
        k["uye"].tiklanabilir(lambda: self.ac(self.ayarlar),"Ayarlar > Kullanıcılar")
        l=self.ana_sayfa.listeler
        l["son"].tablo.cellDoubleClicked.connect(
            lambda satir,_: self.kitap_duzenle(satir_verisi(l["son"].tablo,satir)) if satir_verisi(l["son"].tablo,satir) else None)
        l["son"].tablo.setToolTip("Kitabı düzenlemek için çift tıklayın")
        l["yaklasan"].tablo.cellDoubleClicked.connect(
            lambda satir,_: self.iade_ekrani(*satir_verisi(l["yaklasan"].tablo,satir)) if satir_verisi(l["yaklasan"].tablo,satir) else None)
        l["yaklasan"].tablo.setToolTip("İade almak için çift tıklayın")
        self.ana_sayfa_yenile()

        ###  Çift tıklama: kitap satırı Kitap Kayıt ekranında açılır; sağ tık: düzenle, ödünç ver, iade al, geçmiş  ###
        for tablo in (self.liste.tablo,self.filtre.tablo):
            tablo.setToolTip("Düzenlemek için çift tıklayın; diğer işlemler için sağ tıklayın")
            tablo.cellDoubleClicked.connect(lambda satir,_,t=tablo: self.tablodan_kitap_duzenle(t,satir))
            tablo.sag_tik_eylemleri.append(lambda satir,t=tablo: self.kitap_eylemleri(t,satir))
        self.kitaplar.tablo.sag_tik_eylemleri.append(
            lambda satir: self.kitap_eylemleri(self.kitaplar.tablo,satir,duzenle=False))

        # Kayıtlar değişince panelin özetleri (ana sayfa, bilgiler, gecikme rozeti) güncellenir;
        # sayfalar (Kitap Kayıt, Kitap Verme, Filtre, İstatistik ...) olaylara kendileri bağlıdır
        olaylar.kitaplar.connect(self.ozetleri_yenile)
        olaylar.odunc.connect(self.odunc_degisti)
        olaylar.kullanicilar.connect(self.ozetleri_yenile)

        # Ana sayfa açılınca da güncellenir: program günlerce açık kalırsa gecikmeler tarihle değişir
        return [Sayfa("giris","Giriş",self.ana_sayfa,self.ana_sayfa_yenile),
                Sayfa("liste","Kitap Listesi",self.liste,self.liste.listele),
                Sayfa("kayit","Kitap Kayıt",self.kayit),
                Sayfa("filtre","Filtre",self.filtre),
                Sayfa("istatistik","İstatistik",self.istatistik),
                Sayfa("verme","Kitap Verme",self.verme),
                Sayfa("ayarlar","Ayarlar",self.ayarlar)]

    def yenile(self):
        ###  Her şeyi yenile: veritabanı topluca değişince (ör. yedekten geri yükleme)  ###
        olaylar.hepsini_yayinla()

    def odunc_degisti(self):
        self.gecikme_bildir()
        self.ozetleri_yenile()

    def ozetleri_yenile(self):
        self.ayarlar.yenile()
        self.ana_sayfa_yenile()

    def ana_sayfa_yenile(self):
        o=genel_ozet()
        gecikmis=geciken_sayisi()
        k=self.ana_sayfa.kartlar
        k["kitap"].ayarla(o["kitap"],kitap_karti_alti(o["kitap"],o["kopya"],o["disarida"]))
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

    def disaridakileri_goster(self):
        self.ac(self.verme,self.odunc)

    def gecikme_bildir(self):
        ###  Teslim süresi geçen kitap varsa Kitap Verme sekmesinin adında göster  ###
        sayi=geciken_sayisi()
        self.sayfa_adi(self.verme, f"Kitap Verme ({sayi} gecikmiş)" if sayi else "Kitap Verme")
        if sayi:
            self.bildirim.mesaj(
                f"Teslim süresi ({ODUNC_SURESI_GUN} gün) geçmiş {sayi} kitap var. Kitap Verme > Ödünç ve İade", "uyari", 10000)
        return sayi

    def kayit_sekmesi_degisti(self):
        if self.alt_sekmeler[self.kayit].currentWidget() is self.duzeltme:
            self.duzeltme.yenile()

    def odunc_sekmesi_degisti(self):
        ###  Dışarıdaki kitaplar ve geçmiş sekmesi açılınca güncel hali göster  ###
        sayfa=self.alt_sekmeler[self.verme].currentWidget()
        if sayfa is self.odunc:
            self.odunc.yenile()
        elif sayfa is self.gecmis:
            self.gecmis.yenile()

    def tablodan_kitap_duzenle(self,tablo,satir):
        hucre=tablo.item(satir,0)   # ilk kolon: kitap numarası (Id)
        if hucre and hucre.text().isdigit():
            self.kitap_duzenle(int(hucre.text()))

    ##################################
    #####   Sağ tık ve hızlı arama   #####
    ##################################

    def kitap_eylemleri(self,tablo,satir,duzenle=True):
        ###  Kitap satırına sağ tık: [(metin, işlev, açık mı)]  ###
        hucre=tablo.item(satir,0)   # ilk kolon: kitap numarası (gizli olsa da hücre durur)
        if not (hucre and hucre.text().isdigit()):
            return []
        kitap_id=int(hucre.text())
        kopya,disarida=kopya_durumu(kitap_id)
        eylemler=[("Düzenle",lambda: self.kitap_duzenle(kitap_id),True)] if duzenle else []
        return eylemler+[
            ("Ödünç ver..." if disarida<kopya else "Ödünç ver (müsait kopya yok)",
             lambda: self.odunc_ver_ekrani(kitap_id),disarida<kopya),
            ("İade al...",lambda: self.kitap_iade_ekrani(kitap_id),disarida>0),
            ("Ödünç geçmişi",lambda: self.kitap_gecmisi(kitap_id),bool(odunc_gecmisi(book_id=kitap_id)))]

    def odunc_ver_ekrani(self,kitap_id=None):
        ###  Kitap Verme > Ödünç ve İade: kitap seçili gelir, sıra üyeye gelir  ###
        self.disaridakileri_goster()
        if kitap_id is None:
            self.odunc.kitap.setFocus(Qt.OtherFocusReason)
        else:
            self.odunc.kitap_sec(kitap_id)

    def uye_ile_odunc(self,uye_id):
        self.disaridakileri_goster()
        self.odunc.uye_sec(uye_id)

    def kitap_iade_ekrani(self,kitap_id):
        ###  Dışarıdaki tek kopya ise o ödünç seçili açılır; birden fazlaysa liste kitap adıyla süzülür  ###
        odunclar=[o for o in disaridakiler() if o.kitap_id==kitap_id]
        if len(odunclar)==1:
            self.iade_ekrani(odunclar[0].uye_id,odunclar[0].kitap_id)
        elif odunclar:
            self.disaridakileri_goster()
            self.odunc.arama.setText(odunclar[0].kitap)
            self.bildirim.mesaj(f"Bu kitabın {len(odunclar)} kopyası dışarıda; iade alınacak olanı seçin.","bilgi",self.dur_msj*3)

    def kitap_gecmisi(self,kitap_id):
        self.ac(self.verme,self.gecmis)
        self.gecmis.yenile()
        i=self.gecmis.kitap.findData(kitap_id)
        if i>=0:
            self.gecmis.kitap.setCurrentIndex(i)

    def yeni_kitap_ekrani(self):
        self.ac(self.kayit,self.kitaplar)
        self.kitaplar.yeni()

    def kitabi_ac(self,kitap_id,adi):
        self.kitap_duzenle(kitap_id)

    def islem_komutlari(self):
        return [("Yeni kitap","Kitap Kayıt","arti",self.yeni_kitap_ekrani,"ekle kayıt"),
                ("Ödünç ver","Kitap Verme","ok_sag",self.odunc_ver_ekrani,"kitap verme"),
                ("İade al","Dışarıdaki kitaplar","ok_sol",self.disaridakileri_goster,"teslim geciken"),
                ("Ödünç geçmişi","Kitap Verme","liste",lambda: self.ac(self.verme,self.gecmis),""),
                ("Veri düzeltme","Kitap Kayıt","kalem",lambda: self.ac(self.kayit,self.duzeltme),"benzer yazım eksik"),
                ("Yeni kullanıcı ekle","Üye veya yönetici","kullanici_ekle",self.user.ac,"üye kayıt"),
                ("Kullanıcı yönetimi","Ayarlar","kullanicilar",self.kullanici_yonetimi,"üye şifre sıfırla"),
                ("Yedek al","Ayarlar","indir",self.yedek_al_ekrani,"yedekle")]+super().islem_komutlari()

    def ek_arama_gruplari(self,metin):
        uyeler=[(adi,f"{kullanici} · ödünç ver","kullanicilar",lambda uye_id=id: self.uye_ile_odunc(uye_id))
                for id,adi,kullanici in uye_secim_listesi() if eslesir(metin,adi,kullanici)][:6]
        return [("Üyeler",uyeler)]

    def kitap_duzenle(self,kitap_id):
        ###  Kitap Kayıt > Kitaplar ekranını bu kitapla aç  ###
        self.ac(self.kayit,self.kitaplar)
        if kitap_bul(kitap_id) is None:
            self.bildirim.mesaj("Kitap bulunamadı (silinmiş olabilir).","uyari",self.dur_msj)
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
        ###  Yeni kullanıcı kaydından sonra aynı menüde kalınır (listeler olaylar.kullanicilar ile yenilendi)  ###
        self.bildirim.mesaj(f"'{kullanici}' kullanıcısı kaydedildi.","basari",self.dur_msj*2)

    def kullanici_yonetimi(self):
        KullaniciYonetimi(self.aktif_kullanici, self).exec()

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
