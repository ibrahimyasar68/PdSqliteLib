## Filtre sekmesi: tür, yazar, yayınevi ve yıl ölçütleri tek panelde ##
# Her ölçütte birden fazla değer seçilebilir. Aynı ölçütteki seçimlerden biri ("Roman veya Deneme"),
# farklı ölçütlerin hepsi ("Roman ve Kemal TAHİR") tutmalıdır. Sonuçlar her seçimde kendiliğinden güncellenir.

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QComboBox, QFrame, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QPushButton,
                             QScrollArea, QTableWidget, QVBoxLayout, QWidget)

from acodes.aranabilir import aranabilir_yap
from acodes.tablo import tablo_ayarla, tabloya_yaz
from acodes.yerlesim import AkisDuzeni
from database.dbframe import df_sort_list, kitap_filtrele, tr_sirala

SECINIZ = ' Seçiniz...'
# (veritabanı kolonu, ölçüt adı)
OLCUTLER = [("Turu", "Tür"), ("Yazari", "Yazar"), ("Yayinevi", "Yayınevi"), ("Yili", "Yıl")]
SONUC_KOLONLARI = ["Kayıt No", "Adı", "Yazarı", "Çeviren", "Türü", "Yayınevi", "Yılı", "Sayfa"]
SECIM_YOK = "Soldaki ölçütlerden bir veya birkaç seçim yapın;\nuyan kitaplar burada listelenir."
SONUC_YOK = "Seçimlerin hepsine uyan kitap yok.\nBir seçimi kaldırmayı deneyin."


class FiltrePaneli(QWidget):
    def __init__(self, mesaj=None, parent=None):
        super().__init__(parent)
        self.mesaj = mesaj or (lambda metin: None)
        self.secimler = {kolon: [] for kolon, _ in OLCUTLER}
        self.combo, self.kutu, self.etiketler = {}, {}, {}

        # --- Sol: ölçütler (pencere küçükse kaydırılır), altında butonlar
        olcutler = QVBoxLayout()
        olcutler.setContentsMargins(0, 0, 6, 0)
        olcutler.setSpacing(10)
        aciklama = QLabel("Aynı ölçütteki seçimlerden <b>biri</b>, farklı ölçütlerin <b>hepsi</b> tutmalı.")
        aciklama.setWordWrap(True)
        aciklama.setObjectName("filtre_aciklama")
        olcutler.addWidget(aciklama)
        for kolon, ad in OLCUTLER:
            kutu = QGroupBox(ad)
            dikey = QVBoxLayout(kutu)
            dikey.setSpacing(8)
            cmb = QComboBox()
            cmb.setMinimumHeight(32)
            cmb.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)   # uzun adlar genişletmesin
            cmb.setMinimumContentsLength(12)
            aranabilir_yap(cmb, f"{ad} yazarak arayın...")
            # Seçime ekleme listeden bir seçenek seçilince yapılır (yazarken değil)
            cmb.currentIndexChanged.connect(lambda i, kolon=kolon: self._combo_secildi(kolon, i))
            dikey.addWidget(cmb)
            etiketler = QWidget()
            etiketler.setLayout(AkisDuzeni())
            dikey.addWidget(etiketler)
            self.combo[kolon], self.kutu[kolon], self.etiketler[kolon] = cmb, kutu, etiketler
            olcutler.addWidget(kutu)
        olcutler.addStretch()
        icerik = QWidget(objectName="filtre_olcutleri")
        icerik.setLayout(olcutler)
        kaydirma = QScrollArea()
        kaydirma.setWidgetResizable(True)
        kaydirma.setFrameShape(QFrame.NoFrame)
        kaydirma.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        kaydirma.setWidget(icerik)
        kaydirma.setStyleSheet("QScrollArea, #filtre_olcutleri { background: transparent; }")
        sol = QVBoxLayout()
        sol.setSpacing(10)
        sol.addWidget(kaydirma, 1)
        butonlar = QHBoxLayout()
        self.btn_temizle = QPushButton("Temizle")
        self.btn_temizle.setToolTip("Tüm seçimleri kaldır")
        self.btn_temizle.clicked.connect(self.temizle)
        self.btn_aktar = QPushButton("Dışa Aktar")
        self.btn_aktar.setToolTip("Sonuçları Excel veya CSV olarak kaydet")
        for b in (self.btn_temizle, self.btn_aktar):
            b.setMinimumSize(120, 38)
            butonlar.addWidget(b)
        butonlar.addStretch()
        sol.addLayout(butonlar)

        # --- Sağ: sonuçlar
        self.sonuc = QLabel(objectName="filtre_sonuc")
        self.tablo = QTableWidget(0, len(SONUC_KOLONLARI))
        self.tablo.setHorizontalHeaderLabels(SONUC_KOLONLARI)
        tablo_ayarla(self.tablo, bos_metin=SECIM_YOK)
        baslik = self.tablo.horizontalHeader()
        baslik.setStretchLastSection(False)
        for kolon in range(len(SONUC_KOLONLARI)):
            baslik.setSectionResizeMode(kolon, QHeaderView.ResizeToContents)
        baslik.setSectionResizeMode(1, QHeaderView.Stretch)
        sag = QVBoxLayout()
        sag.addWidget(self.sonuc)
        sag.addWidget(self.tablo, 1)

        solda = QWidget()
        solda.setLayout(sol)
        solda.setFixedWidth(340)
        duzen = QHBoxLayout(self)
        duzen.setContentsMargins(14, 12, 14, 12)
        duzen.setSpacing(16)
        duzen.addWidget(solda)
        duzen.addLayout(sag, 1)
        self.yenile()

    def yenile(self):
        ###  Açılır listeleri veritabanından doldur (seçimler korunur), sonuçları güncelle  ###
        for kolon, _ in OLCUTLER:
            cmb = self.combo[kolon]
            cmb.blockSignals(True)
            cmb.clear()
            cmb.addItems([SECINIZ] + df_sort_list(kolon))
            cmb.setCurrentIndex(0)
            cmb.blockSignals(False)
        self.listele()

    def _combo_secildi(self, kolon, i):
        if i <= 0:
            return
        self.ekle(kolon, self.combo[kolon].itemText(i))
        cmb = self.combo[kolon]
        cmb.blockSignals(True)
        cmb.setCurrentIndex(0)          # bir sonraki seçim için liste başa döner
        cmb.blockSignals(False)
        cmb.suzgec.ayarla("")

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
        if not any(self.secimler.values()):
            self.mesaj("Temizlenecek seçim yok!")
            return
        for secilen in self.secimler.values():
            secilen.clear()
        self.listele()
        self.mesaj("Filtre temizlendi.")

    def listele(self):
        for kolon, ad in OLCUTLER:
            self._etiketleri_yaz(kolon)
            adet = len(self.secimler[kolon])
            self.kutu[kolon].setTitle(f"{ad} ({adet})" if adet else ad)
        secim_var = any(self.secimler.values())
        satirlar = kitap_filtrele(self.secimler)
        tabloya_yaz(self.tablo, satirlar)
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
