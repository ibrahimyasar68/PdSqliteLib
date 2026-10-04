## Kitap Kayıt > Kitaplar: ekleme, düzenleme ve silme tek ekranda ##
# Üstte tam genişlikte aranabilir kitap listesi, altta seçili kitabın formu (Kitap Verme ekranıyla aynı düzen).
# "Yeni Kitap" formu boşaltır; Kaydet yeni kitapta ekler, seçili kitapta günceller.

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (QCompleter, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QTableWidget, QVBoxLayout, QWidget)

from acodes.onay import onay
from acodes import hareket, tema
from acodes.ek_bilgi import EkBilgiler
from acodes.kisayollar import arama_kutusu_yap, kisayol, metin
from acodes.olaylar import olaylar
from acodes.tablo import KolonSecici, durum_ekle, durum_rozeti_kur, satir_verisi, tablo_ayarla, tabloya_yaz
from acodes.yerlesim import baslik_satiri, etiketli
from database.kitaplar import farkli_degerler, kitap_ara, kitap_bul
from database.modeller import Kitap
from database.odunc import kopya_durumu
from servis import KuralHatasi
from servis import kitap as kitap_servisi

# (veritabanı kolonu, etiket, önerilecek mevcut değerler var mı)
ALANLAR = [("Adi", "Kitap adı (zorunlu)", False), ("Yazari", "Yazarı", True), ("Ceviren", "Çevirmen", True),
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
    def __init__(self, mesaj=None, bildir=None, parent=None):
        """mesaj(metin, tur): panelin bildirimine yazar (tur: "basari", "uyari", "bilgi").
        bildir(metin, eylem adı, işlev): eylem butonlu bildirim (silmeden sonra "Geri Al")."""
        super().__init__(parent)
        self.mesaj = mesaj or (lambda metin, tur=None: None)
        self.bildir = bildir or (lambda metin, *_: self.mesaj(metin))
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
        self.kolonlar = KolonSecici(self.tablo, "kitaplar", varsayilan_gizli=(0,), otomatik=(5, 4))   # sığmazsa Kopya, Yılı
        ust = baslik_satiri(sayac=self.sonuc, butonlar=[self.btn_yeni, self.kolonlar.buton])
        self.arama.setMinimumHeight(38)

        # --- Alt: form (Kitap bilgileri ve Ek bilgiler yan yana; etiketler alanların üstünde, alanlar üç sütunda)
        self.form_baslik = QLabel(objectName="form_baslik")
        self.alan = {}
        kutu = QGroupBox("Kitap bilgileri")
        izgara = QGridLayout(kutu)
        izgara.setHorizontalSpacing(12)
        izgara.setVerticalSpacing(10)
        # (satır, sütun, genişlik): kitap adı iki sütun, yanında yazar; altında üçer alan
        yerler = {"Adi": (0, 0, 2), "Yazari": (0, 2, 1), "Ceviren": (1, 0, 1), "Turu": (1, 1, 1),
                  "Yayinevi": (1, 2, 1), "Yili": (2, 0, 1), "Sayfa": (2, 1, 1)}
        for kolon, etiket, oneri in ALANLAR:
            alan = QLineEdit()
            alan.setMinimumHeight(30)
            self.alan[kolon] = alan
            satir, sutun, genislik = yerler[kolon]
            izgara.addLayout(etiketli(etiket, alan), satir, sutun, 1, genislik)
        for sutun in range(3):
            izgara.setColumnStretch(sutun, 1)
        self.ek = EkBilgiler(izgara=True)
        self.ek.notlar.setMaximumHeight(64)
        self.kopya_bilgi = QLabel(objectName="kopya_bilgi")
        self.ek.layout().addWidget(self.kopya_bilgi, 3, 0, 1, 3)
        self.btn_kaydet = QPushButton("Kaydet")
        self.btn_sil = QPushButton("Sil", objectName="kitap_sil")
        self.btn_vazgec = QPushButton("Vazgeç")
        for b in (self.btn_kaydet, self.btn_vazgec):
            b.setMinimumSize(110, 38)
        self.btn_sil.setMinimumHeight(38)
        # Form başlığı ve butonlar bir satırda: solda "Kitap #12" / "Yeni kitap" ve (kayıtlı kitapta) zeminsiz kırmızı
        # Sil, asıl işlemden uzakta; sağda Vazgeç ve en sağda asıl işlem Kaydet
        islem = QHBoxLayout()
        islem.addWidget(self.form_baslik)
        islem.addSpacing(12)
        islem.addWidget(self.btn_sil)
        islem.addStretch()
        islem.addWidget(self.btn_vazgec)
        islem.addWidget(self.btn_kaydet)
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
        olaylar.kitaplar.connect(self.yenile)        # nereden değişirse değişsin liste güncel kalır
        olaylar.odunc.connect(self.listele)          # Durum kolonu

    # --- Liste

    def yenile(self):
        """Listeyi ve alan önerilerini veritabanından yeniden yükler; seçili kitap korunur."""
        for kolon, _, oneri in ALANLAR:
            if oneri:
                tamamlayici = QCompleter(farkli_degerler(kolon), self.alan[kolon])
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
        kitap = kitap_bul(kitap_id) if kitap_id is not None else None
        if kitap is None:
            self.yeni()
            return
        self.kitap_id = kitap_id
        for kolon, _, _ in ALANLAR:
            self.alan[kolon].setText(str(getattr(kitap, kolon.lower())))
        self.ek.doldur(kitap.isbn, kitap.kopya, kitap.raf, kitap.notlar)
        kopya, disarida = kopya_durumu(kitap_id)
        self.kopya_bilgi.setText(f"{kopya} kopyadan {disarida} tanesi şu an üyelerde." if disarida
                                 else "Tüm kopyaları kütüphanede.")
        self.form_baslik.setText(f"Kitap #{kitap_id}")
        self.btn_sil.setEnabled(True)
        self.btn_sil.show()

    def yeni(self):
        self.kitap_id = None
        for alan in self.alan.values():
            alan.clear()
        self.ek.temizle()
        self.kopya_bilgi.clear()
        self.form_baslik.setText("Yeni kitap")
        self.btn_sil.setEnabled(False)
        self.btn_sil.hide()                   # kaydedilmemiş kitapta silinecek bir şey yok
        self._satiri_sec(None)
        self.alan["Adi"].setFocus()

    def vazgec(self):
        """Seçili kitapta yapılan değişiklikleri geri alır; yeni kitapta formu boşaltır."""
        if self.kitap_id is None:
            self.yeni()
        else:
            self.goster(self.kitap_id)

    def degerler(self):
        """Formdaki kitap (id: seçili kitabın numarası, yeni kitapta None)."""
        alanlar = {k.lower(): buyuk_harf(self.alan[k].text().strip()) if k in BUYUK_HARFLI else self.alan[k].text().strip()
                   for k, _, _ in ALANLAR}
        isbn, kopya, raf, notlar = self.ek.degerler()
        return Kitap(**alanlar, isbn=isbn, kopya=kopya, raf=raf, notlar=notlar, id=self.kitap_id)

    def kaydet(self):
        kitap = self.degerler()
        # Kurallar onay sorulmadan önce denetlenir (servis/kitap.py)
        engel = kitap_servisi.kayit_engeli(kitap)
        if engel:
            self._kural_hatasi(engel)
            return
        if onay(f"'{kitap.adi}' kaydedilsin mi?" if kitap.id is None else "Kayıt değiştirilsin mi?") != QMessageBox.Yes:
            return
        try:
            self.kitap_id = kitap_servisi.kaydet(kitap)
        except KuralHatasi as hata:
            self._kural_hatasi(hata)
            return
        self.mesaj(f"'{kitap.adi}' kaydedildi" if kitap.id is None else f"'{kitap.adi}' güncellendi.", "basari")
        self._degisiklik_sonrasi()
        hareket.secili_satiri_parlat(self.tablo)              # kaydedilen satır kısa süre parlar

    def _kural_hatasi(self, hata):
        """Hatalı alanın çerçevesi kırmızı yanıp söner; uyarıdan sonra imleç o alana gider."""
        alan = {"adi": self.alan["Adi"], "isbn": self.ek.isbn, "kopya": self.ek.kopya}.get(hata.alan)
        if alan is None:
            QMessageBox.warning(self, "Uyarı!", str(hata))
            return
        hareket.hata_vurgula(alan)
        QMessageBox.warning(self, "Uyarı!", str(hata))
        alan.setFocus(Qt.OtherFocusReason)

    def sil(self):
        if self.kitap_id is None:
            return
        engel = kitap_servisi.silme_engeli(self.kitap_id)
        if engel:
            QMessageBox.information(self, "Uyarı!", str(engel))
            return
        adi = self.alan["Adi"].text()
        if onay(f"'{adi}' silinsin mi?\nSildikten sonra kısa bir süre \"Geri Al\" ile geri getirebilirsiniz.") != QMessageBox.Yes:
            return
        try:
            kitap = kitap_servisi.sil(self.kitap_id)
        except KuralHatasi as hata:
            QMessageBox.warning(self, "Uyarı!", str(hata))
            return
        self.kitap_id = None
        self._degisiklik_sonrasi()
        self.yeni()
        self.bildir(f"{adi} silindi", "Geri Al", lambda: self.silmeyi_geri_al(kitap))

    def silmeyi_geri_al(self, kitap):
        """Silinen kitabı aynı numara ve bilgilerle geri getirir, formda açar."""
        try:
            kitap_servisi.geri_getir(kitap)
        except KuralHatasi as hata:
            self.mesaj(str(hata), "uyari")
            return
        self.kitap_id = kitap.id
        self._degisiklik_sonrasi()
        hareket.secili_satiri_parlat(self.tablo)
        self.mesaj(f"'{kitap.adi}' geri getirildi.", "basari")

    def _degisiklik_sonrasi(self):
        # Liste olaylar.kitaplar ile yenilendi; kaydedilen / geri getirilen kitap seçili kalır
        if self.kitap_id is not None:
            self.sec(self.kitap_id)
