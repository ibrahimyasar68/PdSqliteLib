## Kitap Kayıt > Kitaplar: ekleme, düzenleme ve silme tek ekranda ##
# Solda aranabilir kitap listesi, sağda seçili kitabın formu. "Yeni Kitap" formu boşaltır;
# Kaydet yeni kitapta ekler, seçili kitapta günceller. Pencere büyüdükçe liste ve form genişler.

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QCompleter, QFormLayout, QFrame, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QScrollArea, QTableWidget, QVBoxLayout, QWidget)

from bforms.onay import onay
from acodes import tema
from acodes.ek_bilgi import EkBilgiler
from acodes.tablo import KolonSecici, satir_verisi, tablo_ayarla, tabloya_yaz
from database.dbbase import baglantı, degistir_kayit, ekle_kayit, sil_kayit
from database.dbframe import df_book_find_by_id, df_sort_list, kitap_ara, kitap_oduncte, kopya_durumu

# (veritabanı kolonu, etiket, önerilecek mevcut değerler var mı)
ALANLAR = [("Adi", "Kitap adı *", False), ("Yazari", "Yazarı", True), ("Ceviren", "Çevirmen", True),
           ("Turu", "Türü", True), ("Yayinevi", "Yayınevi", True), ("Yili", "Basım yılı", False),
           ("Sayfa", "Sayfa", False)]
BUYUK_HARFLI = {"Adi", "Yazari", "Ceviren", "Turu", "Yayinevi"}
LISTE_KOLONLARI = ["Kayıt No", "Adı", "Yazarı", "Yayınevi", "Yılı", "Kopya"]


def buyuk_harf(metin):
    """Her kelimenin ilk harfini büyütür, gerisine dokunmaz (Türkçe i/İ uyumlu).
    str.title() "Anne'nin" -> "Anne'Nin", "TAHİR" -> "Tahi̇r" yaptığı için kullanılmıyor."""
    kelimeler = []
    for k in metin.split(" "):
        if k:
            ilk = k[0]
            k = ("İ" if ilk == "i" else "I" if ilk == "ı" else ilk.upper()) + k[1:]
        kelimeler.append(k)
    return " ".join(kelimeler)


class KitapEkrani(QWidget):
    def __init__(self, mesaj=None, degisti=None, parent=None):
        """mesaj(metin): panelin bildirimine yazar. degisti(): kitap eklenince/değişince/silinince çağrılır."""
        super().__init__(parent)
        self.mesaj = mesaj or (lambda metin: None)
        self.degisti = degisti
        self.kitap_id = None
        self.setObjectName("kitap_ekrani")
        self.setStyleSheet(f"""
            #kitap_arama {{ font-size: 17px; padding: 4px 8px; }}
            #form_baslik {{ font-size: 18px; font-weight: bold; }}
            #kopya_bilgi {{ color: {tema.IKINCIL_METIN}; }}
            QGroupBox {{ font-weight: bold; }}
        """)

        # --- Sol: arama ve liste
        self.arama = QLineEdit(objectName="kitap_arama")
        self.arama.setPlaceholderText("Ara: kitap adı, yazar, yayınevi, ISBN, raf, not...")
        self.arama.setClearButtonEnabled(True)
        self.arama.setMinimumHeight(36)
        self.btn_yeni = QPushButton("Yeni Kitap")
        self.btn_yeni.setMinimumHeight(36)
        self.sonuc = QLabel()
        self.tablo = QTableWidget(0, len(LISTE_KOLONLARI))
        self.tablo.setHorizontalHeaderLabels(LISTE_KOLONLARI)
        tablo_ayarla(self.tablo, bos_metin="Aramanıza uyan kitap yok.")
        # Kitap adı, yazar ve yayınevi kalan yeri paylaşır; kısa kolonlar içeriğe göre:
        # dar pencerede de yatay kaydırma olmadan Yılı ve Kopya görünür kalır
        baslik = self.tablo.horizontalHeader()
        baslik.setStretchLastSection(False)
        baslik.setMinimumSectionSize(50)
        for kolon, kip in ((0, QHeaderView.ResizeToContents), (1, QHeaderView.Stretch),
                           (4, QHeaderView.ResizeToContents), (5, QHeaderView.ResizeToContents)):
            baslik.setSectionResizeMode(kolon, kip)
        for kolon in (2, 3):
            baslik.setSectionResizeMode(kolon, QHeaderView.Stretch)
        self.tablo.setSelectionMode(QTableWidget.SingleSelection)
        ust = QHBoxLayout()
        ust.addWidget(self.arama, 1)
        ust.addWidget(self.btn_yeni)
        self.kolonlar = KolonSecici(self.tablo, "kitaplar")
        self.kolonlar.buton.setMinimumHeight(36)
        ust.addWidget(self.kolonlar.buton)
        sol = QVBoxLayout()
        sol.addLayout(ust)
        sol.addWidget(self.sonuc)
        sol.addWidget(self.kolonlar.soru)
        sol.addWidget(self.tablo, 1)

        # --- Sağ: form
        self.form_baslik = QLabel(objectName="form_baslik")
        self.alan = {}
        kutu = QGroupBox("Kitap bilgileri")
        form = QFormLayout(kutu)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setVerticalSpacing(8)
        for kolon, etiket, oneri in ALANLAR:
            alan = QLineEdit()
            alan.setMinimumHeight(30)
            self.alan[kolon] = alan
            form.addRow(etiket + ":", alan)
        self.alan["Yili"].setMaximumWidth(120)
        self.alan["Sayfa"].setMaximumWidth(120)
        self.ek = EkBilgiler()
        self.kopya_bilgi = QLabel(objectName="kopya_bilgi")
        self.btn_kaydet = QPushButton("Kaydet")
        self.btn_sil = QPushButton("Sil", objectName="kitap_sil")
        self.btn_vazgec = QPushButton("Vazgeç")
        for b in (self.btn_kaydet, self.btn_sil, self.btn_vazgec):
            b.setMinimumSize(110, 38)
        butonlar = QHBoxLayout()
        butonlar.addWidget(self.btn_kaydet)
        butonlar.addWidget(self.btn_vazgec)
        butonlar.addStretch()
        butonlar.addWidget(self.btn_sil)
        alanlar = QVBoxLayout()
        alanlar.setContentsMargins(0, 0, 0, 0)
        alanlar.addWidget(kutu)
        alanlar.addWidget(self.ek)
        alanlar.addWidget(self.kopya_bilgi)
        alanlar.addStretch()

        duzen = QHBoxLayout(self)
        duzen.setContentsMargins(14, 12, 14, 12)
        duzen.setSpacing(16)
        duzen.addLayout(sol, 3)
        # Küçük pencerede alanlar üst üste binmesin: sığmazsa alanlar kaydırılır, başlık ve butonlar yerinde kalır
        form_alani = QWidget(objectName="kitap_formu")
        form_alani.setLayout(alanlar)
        kaydirma = QScrollArea()
        kaydirma.setWidgetResizable(True)
        kaydirma.setFrameShape(QFrame.NoFrame)
        kaydirma.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        kaydirma.setWidget(form_alani)
        kaydirma.setStyleSheet("QScrollArea, #kitap_formu { background: transparent; }")
        sag = QVBoxLayout()
        sag.addWidget(self.form_baslik)
        sag.addWidget(kaydirma, 1)
        sag.addLayout(butonlar)
        duzen.addLayout(sag, 2)
        self.ek.layout().setVerticalSpacing(8)
        self.ek.notlar.setMaximumHeight(70)

        self.arama.textChanged.connect(self.listele)
        self.tablo.itemSelectionChanged.connect(self.secim_degisti)
        self.btn_yeni.clicked.connect(self.yeni)
        self.btn_kaydet.clicked.connect(self.kaydet)
        self.btn_sil.clicked.connect(self.sil)
        self.btn_vazgec.clicked.connect(self.vazgec)
        self.alan["Adi"].returnPressed.connect(self.kaydet)
        self.yenile()
        self.yeni()

    # --- Liste

    def yenile(self):
        """Listeyi ve alan önerilerini veritabanından yeniden yükler; seçili kitap korunur."""
        for kolon, _, oneri in ALANLAR:
            if oneri:
                tamamlayici = QCompleter(df_sort_list(kolon), self.alan[kolon])
                tamamlayici.setCaseSensitivity(Qt.CaseInsensitive)
                tamamlayici.setFilterMode(Qt.MatchContains)
                self.alan[kolon].setCompleter(tamamlayici)
        self.listele()

    def listele(self):
        secili = self.kitap_id
        kitaplar = kitap_ara(self.arama.text().strip())
        self.tablo.blockSignals(True)
        tabloya_yaz(self.tablo, [[k[0], k[1], k[2], k[5], k[6], k[9] or 1] for k in kitaplar],
                    veri=[k[0] for k in kitaplar])
        self.tablo.blockSignals(False)
        self.sonuc.setText(f"{len(kitaplar)} kitap" + (" bulundu" if self.arama.text().strip() else ""))
        self._satiri_sec(secili)

    def _satiri_sec(self, kitap_id):
        self.tablo.blockSignals(True)
        self.tablo.clearSelection()
        for r in range(self.tablo.rowCount()):
            if satir_verisi(self.tablo, r) == kitap_id and kitap_id is not None:
                self.tablo.selectRow(r)
                self.tablo.scrollToItem(self.tablo.item(r, 0))
                break
        self.tablo.blockSignals(False)

    def secim_degisti(self):
        satirlar = self.tablo.selectionModel().selectedRows()
        if satirlar:
            self.goster(satir_verisi(self.tablo, satirlar[0].row()))

    def sec(self, kitap_id):
        """Kitabı listede seçip formda açar (arama bu kitabı gizliyorsa arama temizlenir)."""
        if not any(satir_verisi(self.tablo, r) == kitap_id for r in range(self.tablo.rowCount())):
            self.arama.clear()
        self.goster(kitap_id)
        self._satiri_sec(kitap_id)

    # --- Form

    def goster(self, kitap_id):
        kayit = df_book_find_by_id(kitap_id) if kitap_id is not None else None
        if kayit is None:
            self.yeni()
            return
        self.kitap_id = kitap_id
        for i, (kolon, _, _) in enumerate(ALANLAR, start=1):
            self.alan[kolon].setText("" if kayit[i] is None else str(kayit[i]))
        self.ek.doldur(*kayit[8:12])
        kopya, disarida = kopya_durumu(kitap_id)
        self.kopya_bilgi.setText(f"{kopya} kopyadan {disarida} tanesi şu an üyelerde." if disarida
                                 else "Tüm kopyaları kütüphanede.")
        self.form_baslik.setText(f"Kitap #{kitap_id}")
        self.btn_sil.setEnabled(True)

    def yeni(self):
        self.kitap_id = None
        for alan in self.alan.values():
            alan.clear()
        self.ek.temizle()
        self.kopya_bilgi.clear()
        self.form_baslik.setText("Yeni kitap")
        self.btn_sil.setEnabled(False)
        self._satiri_sec(None)
        self.alan["Adi"].setFocus()

    def vazgec(self):
        """Seçili kitapta yapılan değişiklikleri geri alır; yeni kitapta formu boşaltır."""
        if self.kitap_id is None:
            self.yeni()
        else:
            self.goster(self.kitap_id)

    def degerler(self):
        kayit = [buyuk_harf(self.alan[k].text().strip()) if k in BUYUK_HARFLI else self.alan[k].text().strip()
                 for k, _, _ in ALANLAR]
        return kayit + list(self.ek.degerler())

    def kaydet(self):
        kayit = self.degerler()
        if not kayit[0]:
            QMessageBox.warning(self, "Uyarı!", "Kitap adı boş olamaz.")
            return
        if self.ek.hata():
            QMessageBox.warning(self, "Uyarı!", self.ek.hata())
            return
        if self.kitap_id is None:
            if onay(f"'{kayit[0]}' kaydedilsin mi?") != QMessageBox.Yes:
                return
            ekle_kayit(kayit)
            self.kitap_id = baglantı.execute("SELECT MAX(Id) FROM kayitlistesi").fetchone()[0]
            self.mesaj(f"'{kayit[0]}' kaydedildi")
        else:
            disarida = kopya_durumu(self.kitap_id)[1]
            if kayit[8] < disarida:
                QMessageBox.warning(self, "Uyarı!", f"Bu kitabın {disarida} kopyası şu an üyelerde. "
                                                    f"Kopya sayısı {disarida}'den az olamaz.")
                return
            if onay("Kayıt değiştirilsin mi?") != QMessageBox.Yes:
                return
            degistir_kayit([self.kitap_id] + kayit)
            self.mesaj(f"'{kayit[0]}' güncellendi.")
        self._degisiklik_sonrasi()

    def sil(self):
        if self.kitap_id is None:
            return
        if kitap_oduncte(self.kitap_id):
            QMessageBox.information(self, "Uyarı!", "Bu kitap ödünçte. İade alınmadan silinemez!")
            return
        adi = self.alan["Adi"].text()
        if onay(f"'{adi}' silinsin mi?\nBu işlem geri alınamaz.") != QMessageBox.Yes:
            return
        sil_kayit(self.kitap_id)
        self.mesaj(f"{adi} silindi")
        self.kitap_id = None
        self._degisiklik_sonrasi()
        self.yeni()

    def _degisiklik_sonrasi(self):
        if self.degisti:
            self.degisti()        # panel listeleri ve istatistikleri yeniler (bu ekran dahil)
        else:
            self.yenile()
        if self.kitap_id is not None:
            self.sec(self.kitap_id)
