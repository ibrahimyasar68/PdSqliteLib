## Kitap Kayıt > Kitaplar: ekleme, düzenleme ve silme tek ekranda ##
# Üstte tam genişlikte aranabilir kitap listesi, altta seçili kitabın formu (Kitap Verme ekranıyla aynı düzen).
# "Yeni Kitap" formu boşaltır; Kaydet yeni kitapta ekler, seçili kitapta günceller.

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QCompleter, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QTableWidget, QVBoxLayout, QWidget)

from acodes.onay import onay
from acodes import hareket, tema
from acodes.ek_bilgi import EkBilgiler
from acodes.kisayollar import arama_kutusu_yap, kisayol, metin
from acodes.tablo import KolonSecici, durum_ekle, durum_rozeti_kur, satir_verisi, tablo_ayarla, tabloya_yaz
from acodes.yerlesim import baslik_satiri
from database.dbbase import baglantı, degistir_kayit, ekle_kayit, geri_ekle_kayit, sil_kayit
from database.dbframe import df_book_find_by_id, df_sort_list, kitap_ara, kitap_oduncte, kopya_durumu

# (veritabanı kolonu, etiket, önerilecek mevcut değerler var mı)
ALANLAR = [("Adi", "Kitap adı *", False), ("Yazari", "Yazarı", True), ("Ceviren", "Çevirmen", True),
           ("Turu", "Türü", True), ("Yayinevi", "Yayınevi", True), ("Yili", "Basım yılı", False),
           ("Sayfa", "Sayfa", False)]
BUYUK_HARFLI = {"Adi", "Yazari", "Ceviren", "Turu", "Yayinevi"}
LISTE_KOLONLARI = ["Kayıt No", "Adı", "Yazarı", "Yayınevi", "Yılı", "Kopya", "Durum"]


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
    def __init__(self, mesaj=None, degisti=None, bildir=None, parent=None):
        """mesaj(metin, tur): panelin bildirimine yazar (tur: "basari", "uyari", "bilgi"). degisti(): kitap eklenince/değişince/silinince çağrılır.
        bildir(metin, eylem adı, işlev): eylem butonlu bildirim (silmeden sonra "Geri Al")."""
        super().__init__(parent)
        self.mesaj = mesaj or (lambda metin, tur=None: None)
        self.bildir = bildir or (lambda metin, *_: self.mesaj(metin))
        self.degisti = degisti
        self.kitap_id = None
        self.setObjectName("kitap_ekrani")
        self.setStyleSheet(f"""
            #kitap_arama {{ font-size: {tema.YAZI.alt_baslik}px; padding: 4px 8px; }}
            #form_baslik {{ font-size: {tema.YAZI.alt_baslik}px; font-weight: {tema.YARI_KALIN}; }}
            #kopya_bilgi {{ color: {tema.IKINCIL_METIN}; }}
            QGroupBox {{ font-weight: {tema.YARI_KALIN}; }}
        """)

        # --- Üst: arama ve liste
        self.arama = arama_kutusu_yap(QLineEdit(objectName="kitap_arama"))
        self.arama.setPlaceholderText("Ara: kitap adı, yazar, yayınevi, ISBN, raf, not...")
        self.arama.setClearButtonEnabled(True)
        self.btn_yeni = QPushButton("Yeni Kitap")
        self.sonuc = QLabel()
        self.tablo = QTableWidget(0, len(LISTE_KOLONLARI))
        self.tablo.setHorizontalHeaderLabels(LISTE_KOLONLARI)
        tablo_ayarla(self.tablo, bos_metin="Aramanıza uyan kitap yok.", bos_simge="ara",
                     bos_eylem=("Aramayı Temizle", self.arama.clear))
        durum_rozeti_kur(self.tablo)
        # Kitap adı, yazar ve yayınevi kalan yeri paylaşır; kısa kolonlar içeriğe göre
        baslik = self.tablo.horizontalHeader()
        baslik.setStretchLastSection(False)
        baslik.setMinimumSectionSize(50)
        for kolon, kip in ((0, QHeaderView.ResizeToContents), (1, QHeaderView.Stretch),
                           (4, QHeaderView.ResizeToContents), (5, QHeaderView.ResizeToContents),
                           (6, QHeaderView.ResizeToContents)):
            baslik.setSectionResizeMode(kolon, kip)
        for kolon in (2, 3):
            baslik.setSectionResizeMode(kolon, QHeaderView.Stretch)
        self.tablo.setSelectionMode(QTableWidget.SingleSelection)
        self.kolonlar = KolonSecici(self.tablo, "kitaplar", varsayilan_gizli=(0,))
        ust = baslik_satiri(sayac=self.sonuc, butonlar=[self.btn_yeni, self.kolonlar.buton])
        self.arama.setMinimumHeight(38)

        # --- Alt: form (Kitap bilgileri ve Ek Bilgiler yan yana, alanlar iki sütunda)
        self.form_baslik = QLabel(objectName="form_baslik")
        self.alan = {}
        kutu = QGroupBox("Kitap bilgileri")
        izgara = QGridLayout(kutu)
        izgara.setHorizontalSpacing(10)
        izgara.setVerticalSpacing(8)
        # (kolon, satır, sütun, genişlik): kitap adı tam satır, diğerleri ikişer
        yerler = {"Adi": (0, 0, 3), "Yazari": (1, 0, 1), "Ceviren": (1, 2, 1), "Turu": (2, 0, 1),
                  "Yayinevi": (2, 2, 1), "Yili": (3, 0, 1), "Sayfa": (3, 2, 1)}
        for kolon, etiket, oneri in ALANLAR:
            alan = QLineEdit()
            alan.setMinimumHeight(30)
            self.alan[kolon] = alan
            satir, sutun, genislik = yerler[kolon]
            izgara.addWidget(QLabel(etiket + ":"), satir, sutun, Qt.AlignRight | Qt.AlignVCenter)
            izgara.addWidget(alan, satir, sutun + 1, 1, genislik)
        izgara.setColumnStretch(1, 1)
        izgara.setColumnStretch(3, 1)
        self.alan["Yili"].setMaximumWidth(120)
        self.alan["Sayfa"].setMaximumWidth(120)
        self.ek = EkBilgiler(izgara=True)
        self.ek.notlar.setMaximumHeight(64)
        self.kopya_bilgi = QLabel(objectName="kopya_bilgi")
        self.ek.layout().addWidget(self.kopya_bilgi, 3, 1, 1, 3)
        self.btn_kaydet = QPushButton("Kaydet")
        self.btn_sil = QPushButton("Sil", objectName="kitap_sil")
        self.btn_vazgec = QPushButton("Vazgeç")
        for b in (self.btn_kaydet, self.btn_sil, self.btn_vazgec):
            b.setMinimumSize(110, 38)
        # Form başlığı ve butonlar bir satırda: solda "Kitap #12" / "Yeni kitap", sağda Kaydet, Vazgeç, Sil
        islem = QHBoxLayout()
        islem.addWidget(self.form_baslik)
        islem.addStretch()
        islem.addWidget(self.btn_kaydet)
        islem.addWidget(self.btn_vazgec)
        islem.addSpacing(16)
        islem.addWidget(self.btn_sil)
        kartlar = QHBoxLayout()
        kartlar.setSpacing(16)
        kartlar.addWidget(kutu, 3)
        kartlar.addWidget(self.ek, 2)

        # Liste üstte ve tam genişlikte (kalan yüksekliği alır), form altta (Kitap Verme ekranıyla aynı düzen)
        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(14, 12, 14, 12)
        duzen.setSpacing(10)
        duzen.addLayout(ust)
        duzen.addWidget(self.arama)
        duzen.addWidget(self.kolonlar.soru)
        duzen.addWidget(self.tablo, 1)
        duzen.addLayout(islem)
        duzen.addLayout(kartlar)

        self.arama.textChanged.connect(self.listele)
        self.tablo.itemSelectionChanged.connect(self.secim_degisti)
        self.btn_yeni.clicked.connect(self.yeni)
        self.btn_kaydet.clicked.connect(self.kaydet)
        self.btn_sil.clicked.connect(self.sil)
        self.btn_vazgec.clicked.connect(self.vazgec)
        for tus, buton, ipucu in ((QKeySequence.New, self.btn_yeni, "Formu yeni kitap için boşalt"),
                                  (QKeySequence.Save, self.btn_kaydet, "Kaydet"),
                                  ("Esc", self.btn_vazgec, "Kaydedilmemiş değişiklikleri geri al")):
            kisayol(tus, self, buton.click)
            buton.setToolTip(f"{ipucu} ({metin(tus)})")
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
        satirlar, renkler = durum_ekle([[k[0], k[1], k[2], k[5], k[6], k[9] or 1] for k in kitaplar])
        tabloya_yaz(self.tablo, satirlar, veri=[k[0] for k in kitaplar], renkler=renkler)
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
        # Hatalı alanın çerçevesi kırmızı yanıp söner; uyarıdan sonra imleç o alana gider
        if not kayit[0]:
            self._hatali(self.alan["Adi"], "Kitap adı boş olamaz.")
            return
        if self.ek.hata():
            self._hatali(self.ek.isbn, self.ek.hata())
            return
        if self.kitap_id is None:
            if onay(f"'{kayit[0]}' kaydedilsin mi?") != QMessageBox.Yes:
                return
            ekle_kayit(kayit)
            self.kitap_id = baglantı.execute("SELECT MAX(Id) FROM kayitlistesi").fetchone()[0]
            self.mesaj(f"'{kayit[0]}' kaydedildi", "basari")
        else:
            disarida = kopya_durumu(self.kitap_id)[1]
            if kayit[8] < disarida:
                self._hatali(self.ek.kopya, f"Bu kitabın {disarida} kopyası şu an üyelerde. "
                                            f"Kopya sayısı {disarida}'den az olamaz.")
                return
            if onay("Kayıt değiştirilsin mi?") != QMessageBox.Yes:
                return
            degistir_kayit([self.kitap_id] + kayit)
            self.mesaj(f"'{kayit[0]}' güncellendi.", "basari")
        self._degisiklik_sonrasi()
        hareket.secili_satiri_parlat(self.tablo)              # kaydedilen satır kısa süre parlar

    def _hatali(self, alan, metin):
        hareket.hata_vurgula(alan)
        QMessageBox.warning(self, "Uyarı!", metin)
        alan.setFocus(Qt.OtherFocusReason)

    def sil(self):
        if self.kitap_id is None:
            return
        if kitap_oduncte(self.kitap_id):
            QMessageBox.information(self, "Uyarı!", "Bu kitap ödünçte. İade alınmadan silinemez!")
            return
        adi = self.alan["Adi"].text()
        if onay(f"'{adi}' silinsin mi?\nSildikten sonra kısa bir süre \"Geri Al\" ile geri getirebilirsiniz.") != QMessageBox.Yes:
            return
        kayit = df_book_find_by_id(self.kitap_id)
        sil_kayit(self.kitap_id)
        self.kitap_id = None
        self._degisiklik_sonrasi()
        self.yeni()
        self.bildir(f"{adi} silindi", "Geri Al", lambda: self.silmeyi_geri_al(kayit))

    def silmeyi_geri_al(self, kayit):
        """Silinen kitabı aynı numara ve bilgilerle geri getirir, formda açar."""
        if kayit is None or df_book_find_by_id(kayit[0]) is not None:
            return
        geri_ekle_kayit(kayit)
        self.kitap_id = kayit[0]
        self._degisiklik_sonrasi()
        hareket.secili_satiri_parlat(self.tablo)
        self.mesaj(f"'{kayit[1]}' geri getirildi.", "basari")

    def _degisiklik_sonrasi(self):
        if self.degisti:
            self.degisti()        # panel listeleri ve istatistikleri yeniler (bu ekran dahil)
        else:
            self.yenile()
        if self.kitap_id is not None:
            self.sec(self.kitap_id)
