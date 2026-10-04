## Kitap Listesi sayfası: tüm kitaplar, yazdıkça süzen arama, kolon seçimi, dışa aktarma ##
# Yönetici ve üye panellerinde aynıdır; yönetici paneli tabloya çift tık ve sağ tık eylemleri ekler.

from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QTableWidget, QWidget

from acodes import tema
from acodes.disa_aktar import disa_aktar, sag_tik_menusu
from acodes.kisayollar import arama_kutusu_yap
from acodes.tablo import KolonSecici, OrantiliKolonlar, durum_ekle, durum_rozeti_kur, tablo_ayarla, tablo_basliklari, tabloya_yaz
from acodes.yerlesim import baslik_satiri, liste_sayfasi
from database.kitaplar import kitap_ara

LISTE_KOLONLARI = [(70,"Kayıt No"),(200,"Adı"),(160,"Yazarı"),(120,"Çeviren"),(90,"Türü"),
                   (160,"Yayınevi"),(50,"Yılı"),(55,"Sayfa"),(120,"ISBN"),(55,"Kopya"),(60,"Raf"),(150,"Durum")]
GENIS_KOLONLAR = {1:3,2:2,3:1.5,5:2}  # Adı, Yazarı, Çeviren, Yayınevi kalan yeri bu oranlarla paylaşır
VARSAYILAN_GIZLI = (0,8)            # Kayıt No (sıra numarası var) ve ISBN; Kolonlar'dan açılabilir
OTOMATIK_GIZLI = (10,9,3,7)         # liste sığmazsa sırayla gizlenir: Raf, Kopya, Çeviren, Sayfa


class KitapListesi(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("kitap_listesi")
        self.tablo=QTableWidget(0,len(LISTE_KOLONLARI))
        tablo_basliklari(self.tablo,LISTE_KOLONLARI)
        self.tablo.horizontalHeader().setMinimumSectionSize(48)
        tablo_ayarla(self.tablo,bos_metin="Aramanıza uyan kitap yok.",bos_simge="ara",
                     bos_eylem=("Aramayı Temizle",self.temizle))
        durum_rozeti_kur(self.tablo)
        self.tablo.orantili=OrantiliKolonlar(self.tablo,GENIS_KOLONLAR)

        self.arama=arama_kutusu_yap(QLineEdit())
        self.arama.setPlaceholderText("Ara: kitap adı, yazar, çevirmen, tür, yayınevi, yıl, ISBN, raf, not...")
        self.arama.setClearButtonEnabled(True)
        self.arama.setStyleSheet(f'font-size: {tema.YAZI.alt_baslik}px; padding: 2px 8px;')
        self.arama.textChanged.connect(self.listele)
        self.sonuc=QLabel()

        self.btn_temizle=QPushButton("Temizle")
        self.btn_temizle.clicked.connect(self.temizle)
        self.btn_aktar=QPushButton("Dışa Aktar")
        self.btn_aktar.setToolTip("Kitap Listesi tablosunu Excel veya CSV olarak kaydet")
        self.btn_aktar.clicked.connect(lambda: disa_aktar(self,self.tablo,"Kitap Listesi"))
        sag_tik_menusu(self,self.tablo,"Kitap Listesi")
        self.kolonlar=KolonSecici(self.tablo,"kitap_listesi",varsayilan_gizli=VARSAYILAN_GIZLI,otomatik=OTOMATIK_GIZLI)

        # Üstte başlık, sonuç sayısı ve butonlar; altında arama; tablo pencereyle büyür
        ust=baslik_satiri("Kitap Listesi",self.sonuc,[self.btn_temizle,self.btn_aktar,self.kolonlar.buton])
        liste_sayfasi(self,ust,self.arama,self.tablo,uyari=self.kolonlar.soru)

    def listele(self):
        sorgu=self.arama.text().strip()
        kitaplar=kitap_ara(sorgu)
        satirlar,renkler=durum_ekle(kitaplar)
        tabloya_yaz(self.tablo,satirlar,renkler=renkler)
        self.sonuc.setText(f"{len(kitaplar)} kitap bulundu" if sorgu else f"Toplam {len(kitaplar)} kitap")

    def temizle(self):
        ###  Aramayı temizle: tüm kitaplar listelenir  ###
        self.arama.clear()
