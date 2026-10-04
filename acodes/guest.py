from acodes import kilavuz, tema
from acodes.ana_sayfa import AnaSayfa
from acodes.ayarlar import Ayarlar
from acodes.kitaplarim import Kitaplarim
from acodes.panel import Panel, Sayfa
from database.istatistik import genel_ozet
from database.kitaplar import son_eklenenler
from database.kullanicilar import kullanici_adiyla_bul
from database.odunc import gecikme_gunu, kalan_gun_yazi, tarih_yazi, teslim_tarihi, uye_odunc


## Üye paneli: Giriş, Kitap Listesi, Filtre, İstatistik (salt okunur), Kitaplarım ve Hesabım
class Guest(Panel):
    PENCERE_BASLIGI = "Yaşar Kütüphanesi - Üye Paneli"
    ROL = "Üye"

    def sayfalari_kur(self):
        ###  Kitaplarım: üyenin elindeki ve daha önce aldığı kitaplar  ###
        self.kitaplarim=Kitaplarim()

        ###  Ayarlar: hesap bilgileri ve şifre değiştirme  ###
        self.ayarlar=Ayarlar([("Hesabım", [("Şifremi Değiştir", self.sifremi_degistir, "Kendi şifrenizi değiştirin")],
                               self.hesap_bilgisi)], kilavuz=kilavuz.UYE)

        ###  Ana sayfa özet panosu  ###
        self.ana_sayfa=AnaSayfa(
            kartlar=[("kitap","Kütüphanedeki kitap",tema.VURGU,"kitap"),("elimdeki","Elimdeki kitap",tema.BILGI,"takas"),
                     ("geciken","Gecikmiş",tema.TEHLIKE,"saat"),("teslim","En yakın teslim",tema.YESIL,"takvim")],
            listeler=[("elimdeki","Elimdeki kitaplar",["Kitap","Teslim Tarihi","Durum"],"Şu an elinizde ödünç kitap yok."),
                      ("son","Son eklenen kitaplar",["Adı","Yazarı"],"Henüz kitap eklenmemiş.")])
        k=self.ana_sayfa.kartlar
        k["kitap"].tiklanabilir(self.tum_kitaplari_goster,"Kitap listesini aç")
        for anahtar in ("elimdeki","geciken","teslim"):
            k[anahtar].tiklanabilir(lambda: self.ac(self.kitaplarim),"Kitaplarım sekmesini aç")
        self.ana_sayfa_yenile()

        return [Sayfa("giris","Giriş",self.ana_sayfa,self.ana_sayfa_yenile),
                Sayfa("liste","Kitap Listesi",self.liste,self.liste.listele),
                Sayfa("filtre","Filtre",self.filtre),
                Sayfa("istatistik","İstatistik",self.istatistik),
                Sayfa("kitaplarim","Kitaplarım",self.kitaplarim,self.kitaplarim_yenile),
                Sayfa("ayarlar","Ayarlar",self.ayarlar)]

    def user_name(self,name):
        super().user_name(name)
        self.ayarlar.yenile()
        self.ana_sayfa_yenile()
        if self.kitaplarim_yenile():
            self.bildirim.mesaj("Teslim süresi geçmiş kitabınız var. Kitaplarım sekmesine bakın.","uyari",10000)

    def kitaplarim_yenile(self):
        sayi=self.kitaplarim.yukle(self.aktif_kullanici)
        self.sayfa_adi(self.kitaplarim, f"Kitaplarım ({sayi} gecikmiş)" if sayi else "Kitaplarım")
        return sayi

    def ana_sayfa_yenile(self):
        elimdeki=[(kitap,verilis) for kitap,_,verilis,durum,_ in uye_odunc(self.aktif_kullanici)
                  if durum=="out"] if self.aktif_kullanici else []
        elimdeki.sort(key=lambda e: str(teslim_tarihi(e[1]) or ""))   # teslim tarihi en yakın olan en üstte
        gecikmis={i for i,(_,verilis) in enumerate(elimdeki) if gecikme_gunu(verilis)}
        k=self.ana_sayfa.kartlar
        k["kitap"].ayarla(genel_ozet()["kitap"],"kitap listesinde aranabilir")
        k["elimdeki"].ayarla(len(elimdeki),"şu an sizde")
        k["geciken"].ayarla(len(gecikmis),"teslim süresi geçmiş" if gecikmis else "gecikmiş kitabınız yok",
                            renk=None if gecikmis else tema.SOLUK)
        en_yakin=min((teslim_tarihi(v) for _,v in elimdeki if teslim_tarihi(v)),default=None)
        k["teslim"].ayarla(tarih_yazi(en_yakin) if en_yakin else "-",
                           kalan_gun_yazi(min(elimdeki,key=lambda e: teslim_tarihi(e[1]))[1]) if en_yakin else "ödünç kitabınız yok")
        self.ana_sayfa.listeler["elimdeki"].doldur(
            [[kitap,tarih_yazi(teslim_tarihi(v)),kalan_gun_yazi(v)] for kitap,v in elimdeki],vurgulu=gecikmis)
        self.ana_sayfa.listeler["son"].doldur([[adi,yazar] for _,adi,yazar in son_eklenenler()])

    def hesap_bilgisi(self):
        k=kullanici_adiyla_bul(self.aktif_kullanici) if self.aktif_kullanici else None
        if k is None:
            return []
        return [("Kullanıcı adı",k.kullanici),("Adı soyadı",k.adi_soyadi or "-"),
                ("Telefon",k.telefon or "-"),("Mail",k.mail or "-")]
