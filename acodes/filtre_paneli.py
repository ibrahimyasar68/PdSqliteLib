## Filtre sekmesi: tür, yazar, yayınevi ve yıl ölçütleri tek panelde ##
# Ölçüt kutusuna yazılan metin Kitap Listesi'ndeki arama gibi süzer ("şiir" → "Şiir" ve "şiir" türleri).
# Diğer ölçütlerin listelerinde yalnızca süzülen kitaplarda geçen değerler kalır (türe "şiir" yazılınca yazar
# listesinde sadece şiir kitabı olan yazarlar). Listeden seçilen değerler etikete dönüşür: aynı ölçütteki
# seçimlerden biri ("Roman veya Deneme"), farklı ölçütlerin hepsi ("Roman ve Kemal TAHİR") tutmalıdır.
# Sonuçlar her değişiklikte kendiliğinden güncellenir.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QGroupBox, QHBoxLayout, QLabel, QPushButton, QTableWidget,
                             QVBoxLayout, QWidget)

from acodes.aranabilir import aranabilir_yap
from acodes.kisayollar import arama_kutusu_yap
from acodes.tablo import KolonSecici, OrantiliKolonlar, durum_ekle, durum_rozeti_kur, tablo_ayarla, tabloya_yaz
from acodes.yerlesim import AkisDuzeni, baslik_satiri
from acodes.olaylar import olaylar
from database.kitaplar import filtre_secenekleri, kitap_filtrele
from database.metin import tr_sirala

# (veritabanı kolonu, ölçüt adı)
OLCUTLER = [("Turu", "Tür"), ("Yazari", "Yazar"), ("Yayinevi", "Yayınevi"), ("Yili", "Yıl")]
SONUC_KOLONLARI = ["Kayıt No", "Adı", "Yazarı", "Çeviren", "Türü", "Yayınevi", "Yılı", "Sayfa", "Durum"]
SECIM_YOK = "Üstteki ölçütlere yazın veya listeden seçin;\nuyan kitaplar burada listelenir."
ACIKLAMA = ("Ölçüt kutusuna yazdıkça liste süzülür; diğer ölçütlerde yalnızca uyan seçenekler kalır.\n"
            "Listeden seçilen değerler etikete dönüşür (etikete tıklamak kaldırır).\n"
            "Aynı ölçütteki seçimlerden biri, farklı ölçütlerin hepsi tutmalıdır.")
SONUC_YOK = "Ölçütlerin hepsine uyan kitap yok.\nBir seçimi kaldırmayı veya aramayı değiştirmeyi deneyin."


class FiltrePaneli(QWidget):
    def __init__(self, mesaj=None, parent=None):
        super().__init__(parent)
        self.mesaj = mesaj or (lambda metin, tur=None: None)
        self.secimler = {kolon: [] for kolon, _ in OLCUTLER}
        self.combo, self.kutu, self.etiketler = {}, {}, {}
        self.secenekler = {}

        # --- Üst: başlık, sonuç sayısı ve butonlar
        self.sonuc = QLabel()
        self.btn_temizle = QPushButton("Temizle")
        self.btn_temizle.setToolTip("Tüm seçimleri kaldır")
        self.btn_temizle.clicked.connect(self.temizle)
        self.btn_aktar = QPushButton("Dışa Aktar")
        self.btn_aktar.setToolTip("Sonuçları Excel veya CSV olarak kaydet")
        self.tablo = QTableWidget(0, len(SONUC_KOLONLARI))
        self.kolonlar = KolonSecici(self.tablo, "filtre", varsayilan_gizli=(0,), otomatik=(3, 7))   # sığmazsa Çeviren, Sayfa
        ust = baslik_satiri("Filtre", self.sonuc, [self.btn_temizle, self.btn_aktar, self.kolonlar.buton], bilgi=ACIKLAMA)

        # --- Ölçütler tek satırda yan yana; seçilen değerler kutunun altında etiket olur
        olcutler = QHBoxLayout()
        olcutler.setSpacing(12)
        for kolon, ad in OLCUTLER:
            kutu = QGroupBox(ad, objectName="olcut")
            dikey = QVBoxLayout(kutu)
            dikey.setSpacing(8)
            cmb = QComboBox()
            cmb.setMinimumHeight(32)
            cmb.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)   # uzun adlar genişletmesin
            cmb.setMinimumContentsLength(10)
            aranabilir_yap(cmb, f"{ad} yazın veya seçin...")
            # Yazılan metin hemen süzer; listeden bir seçenek seçilince etikete dönüşür
            cmb.editTextChanged.connect(self.listele)
            cmb.currentIndexChanged.connect(lambda i, kolon=kolon: self._combo_secildi(kolon, i))
            dikey.addWidget(cmb)
            etiketler = QWidget()
            etiketler.setLayout(AkisDuzeni())
            dikey.addWidget(etiketler)
            dikey.addStretch()
            self.combo[kolon], self.kutu[kolon], self.etiketler[kolon] = cmb, kutu, etiketler
            olcutler.addWidget(kutu, 1)
        arama_kutusu_yap(self.combo["Turu"].lineEdit())       # Ctrl+F ilk ölçüte gider

        # --- Sonuçlar tam genişlikte
        self.tablo.setHorizontalHeaderLabels(SONUC_KOLONLARI)
        tablo_ayarla(self.tablo, bos_metin=SECIM_YOK, bos_simge="huni")
        durum_rozeti_kur(self.tablo)
        self.tablo.orantili = OrantiliKolonlar(self.tablo, {1: 3, 2: 2, 3: 1.5, 5: 2})   # Adı, Yazarı, Çeviren, Yayınevi

        self.setStyleSheet("QGroupBox#olcut { padding: 34px 10px 10px 10px; }"
                           " QGroupBox#olcut::title { top: 10px; left: 12px; }")
        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(14, 12, 14, 12)
        duzen.setSpacing(10)
        duzen.addLayout(ust)
        duzen.addLayout(olcutler)
        duzen.addWidget(self.kolonlar.soru)
        duzen.addWidget(self.tablo, 1)
        self.yenile()
        olaylar.kitaplar.connect(self.yenile)
        olaylar.odunc.connect(self.yenile)           # Durum kolonu

    def yenile(self):
        ###  Veritabanı değişince seçenekleri ve sonuçları yeniden oku (seçimler ve aramalar korunur)  ###
        self.secenekler = {}
        self.listele()

    def kosullar(self):
        """Her ölçüt için etiketler (seçilen değerler) veya etiket yoksa kutuya yazılan metin."""
        return {kolon: list(self.secimler[kolon]) or self.combo[kolon].currentText().strip() for kolon, _ in OLCUTLER}

    def _secenekleri_yaz(self, secenekler):
        # Sadece değişen listeler yeniden doldurulur; kutuya yazılmış metin korunur
        for kolon, degerler in secenekler.items():
            if self.secenekler.get(kolon) == degerler:
                continue
            cmb = self.combo[kolon]
            metin = cmb.currentText()
            cmb.blockSignals(True)
            cmb.clear()
            cmb.addItems(degerler)
            cmb.setCurrentIndex(-1)
            cmb.setEditText(metin)
            cmb.blockSignals(False)
        self.secenekler = secenekler

    def _combo_secildi(self, kolon, i):
        if i < 0:
            return
        cmb = self.combo[kolon]
        deger = cmb.itemText(i)
        cmb.blockSignals(True)
        cmb.setCurrentIndex(-1)         # bir sonraki seçim için kutu boşalır
        cmb.setEditText("")
        cmb.blockSignals(False)
        cmb.suzgec.ayarla("")
        if deger in self.secimler[kolon]:
            self.listele()
        else:
            self.ekle(kolon, deger)

    def ekle(self, kolon, deger):
        if not deger or deger in self.secimler[kolon]:
            return
        self.secimler[kolon].append(deger)
        self.listele()

    def cikar(self, kolon, deger):
        if deger in self.secimler[kolon]:
            self.secimler[kolon].remove(deger)
            self.listele()

    def temizle(self):
        if not any(self.kosullar().values()):
            self.mesaj("Temizlenecek seçim yok!", "uyari")
            return
        for kolon, secilen in self.secimler.items():
            secilen.clear()
            cmb = self.combo[kolon]
            cmb.blockSignals(True)
            cmb.setEditText("")
            cmb.blockSignals(False)
            cmb.suzgec.ayarla("")
        self.listele()
        self.mesaj("Filtre temizlendi.", "basari")

    def listele(self):
        for kolon, ad in OLCUTLER:
            self._etiketleri_yaz(kolon)
            adet = len(self.secimler[kolon])
            self.kutu[kolon].setTitle(f"{ad} ({adet})" if adet else ad)
        kosullar = self.kosullar()
        secim_var = any(kosullar.values())
        self._secenekleri_yaz(filtre_secenekleri(kosullar, [kolon for kolon, _ in OLCUTLER]))
        satirlar = kitap_filtrele(kosullar)
        satirlar_durumlu, renkler = durum_ekle(satirlar)
        tabloya_yaz(self.tablo, satirlar_durumlu, renkler=renkler)
        self.tablo.bos_durum.etiket.setText(SONUC_YOK if secim_var else SECIM_YOK)
        self.sonuc.setText(f"{len(satirlar)} kitap bulundu" if secim_var else "")
        self.btn_temizle.setEnabled(secim_var)

    def _etiketleri_yaz(self, kolon):
        duzen = self.etiketler[kolon].layout()
        while duzen.count():
            duzen.takeAt(0).widget().deleteLater()
        for deger in sorted(self.secimler[kolon], key=tr_sirala):
            etiket = QPushButton(f"{deger}  ✕", objectName="filtre_etiketi")
            etiket.setCursor(Qt.PointingHandCursor)
            etiket.setToolTip("Seçimi kaldırmak için tıklayın")
            etiket.clicked.connect(lambda _, deger=deger: self.cikar(kolon, deger))
            duzen.addWidget(etiket)
        self.etiketler[kolon].setVisible(duzen.count() > 0)
