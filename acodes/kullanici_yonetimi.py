## Kullanıcı yönetimi ##
# Admin panelinden: kullanıcıları listeleme, düzenleme, şifre değiştirme ve silme.
# Guest panelinden: kendi şifresini değiştirme (SifreDegistir, eski şifre sorulur).

from dataclasses import replace

from PyQt5.QtWidgets import (QAbstractItemView, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                             QHBoxLayout, QHeaderView, QLineEdit, QMessageBox, QPushButton,
                             QTableWidget, QVBoxLayout)
from acodes.tablo import satir_verisi, tablo_ayarla, tabloya_yaz
from acodes.yerlesim import ustte_etiketli_form
from acodes.onay import onay
from acodes import ikonlar, tema
from database.kullanicilar import kullanicilar
from servis import KuralHatasi
from servis import kullanici as kullanici_servisi
from servis.kullanici import YETKILER

# Formlar koyu arka planlı panellerin üstünde açıldığı için açık ve okunur bir görünüm
def pencere_stili():
    """Pencereler panelden bağımsız açılsa da (ör. testlerde) aynı temayla görünür."""
    return tema.qss() + f"""
QDialog {{ background-color: {tema.SAYFA}; }}
QWidget {{ font-size: {tema.YAZI.metin}px; }}
QPushButton {{ padding: 6px 14px; }}
"""


class SifreDegistir(QDialog):
    """Şifre değiştirme. eski_sor=True ise kullanıcının mevcut şifresi de istenir."""

    def __init__(self, kullanici, eski_sor=False, parent=None):
        super().__init__(parent)
        self.kullanici = kullanici
        self.setWindowTitle(f"Şifre Değiştir: {kullanici}")
        self.setStyleSheet(pencere_stili())
        form = ustte_etiketli_form(QFormLayout(self))
        self.eski = None
        if eski_sor:
            self.eski = QLineEdit(echoMode=QLineEdit.Password)
            form.addRow("Mevcut şifre", self.eski)
        self.yeni = QLineEdit(echoMode=QLineEdit.Password)
        self.tekrar = QLineEdit(echoMode=QLineEdit.Password)
        form.addRow("Yeni şifre", self.yeni)
        form.addRow("Yeni şifre (tekrar)", self.tekrar)
        butonlar = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        butonlar.button(QDialogButtonBox.Ok).setText("Kaydet")
        butonlar.button(QDialogButtonBox.Cancel).setText("Vazgeç")
        butonlar.accepted.connect(self.kaydet)
        butonlar.rejected.connect(self.reject)
        form.addRow(butonlar)
        ikonlar.butonlara_uygula(self)

    def kaydet(self):
        try:
            kullanici_servisi.sifre_degistir(self.kullanici, self.yeni.text(), self.tekrar.text(),
                                             eski=None if self.eski is None else self.eski.text())
        except KuralHatasi as hata:
            QMessageBox.warning(self, "Uyarı!", str(hata))
            return
        QMessageBox.information(self, "Bilgi", "Şifre değiştirildi.")
        self.accept()


class KullaniciDuzenle(QDialog):
    """Ad soyad, telefon, mail ve yetki düzenleme (kullanıcı adı değiştirilemez)."""

    def __init__(self, kayit, aktif_kullanici, parent=None):
        """kayit: düzenlenen Kullanici."""
        super().__init__(parent)
        self.kayit = kayit
        self.aktif_kullanici = aktif_kullanici
        self.kullanici, self.eski_yetki = kayit.kullanici, kayit.yetki
        adi_soyadi, telefon, mail = kayit.adi_soyadi, kayit.telefon, kayit.mail
        self.setWindowTitle(f"Kullanıcı Düzenle: {self.kullanici}")
        self.setStyleSheet(pencere_stili())
        form = ustte_etiketli_form(QFormLayout(self))
        self.adi_soyadi = QLineEdit(adi_soyadi or "")
        self.telefon = QLineEdit(telefon or "")
        self.telefon.setPlaceholderText("10 hane, örn. 5551234567")
        self.mail = QLineEdit(mail or "")
        self.yetki = QComboBox()
        self.yetki.addItems(YETKILER)
        self.yetki.setCurrentText(self.eski_yetki)
        if self.kullanici == aktif_kullanici:
            # Kendi yetkisini düşüren admin oturum ortasında kilitlenmesin
            self.yetki.setEnabled(False)
            self.yetki.setToolTip("Kendi yetkinizi değiştiremezsiniz.")
        form.addRow("Kullanıcı adı", QLineEdit(self.kullanici, readOnly=True, enabled=False))
        form.addRow("Adı soyadı", self.adi_soyadi)
        form.addRow("Telefon", self.telefon)
        form.addRow("E-posta", self.mail)
        form.addRow("Yetki", self.yetki)
        butonlar = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        butonlar.button(QDialogButtonBox.Ok).setText("Kaydet")
        butonlar.button(QDialogButtonBox.Cancel).setText("Vazgeç")
        butonlar.accepted.connect(self.kaydet)
        butonlar.rejected.connect(self.reject)
        form.addRow(butonlar)
        ikonlar.butonlara_uygula(self)

    def kaydet(self):
        yeni = replace(self.kayit, adi_soyadi=self.adi_soyadi.text().strip(), telefon=self.telefon.text().strip(),
                       mail=self.mail.text().strip(), yetki=self.yetki.currentText())
        try:
            kullanici_servisi.guncelle(yeni, self.aktif_kullanici)   # kurallar servis/kullanici.py'de
        except KuralHatasi as hata:
            QMessageBox.warning(self, "Uyarı!", str(hata))
            return
        self.accept()


class KullaniciYonetimi(QDialog):
    KOLONLAR = ["Kullanıcı Adı", "Adı Soyadı", "Telefon", "Mail", "Yetki"]

    def __init__(self, aktif_kullanici, parent=None):
        super().__init__(parent)
        self.aktif_kullanici = aktif_kullanici
        self.setWindowTitle("Kullanıcı Yönetimi")
        self.setStyleSheet(pencere_stili())
        self.resize(900, 500)

        self.tablo = QTableWidget(0, len(self.KOLONLAR))
        self.tablo.setHorizontalHeaderLabels(self.KOLONLAR)
        tablo_ayarla(self.tablo)
        self.tablo.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.itemSelectionChanged.connect(self.butonlari_ayarla)
        self.tablo.doubleClicked.connect(self.duzenle)

        self.btn_duzenle = QPushButton("Düzenle")
        self.btn_sifre = QPushButton("Şifre Değiştir")
        self.btn_sil = QPushButton("Sil", objectName="kullanici_sil")
        btn_kapat = QPushButton("Kapat")
        self.btn_duzenle.clicked.connect(self.duzenle)
        self.btn_sifre.clicked.connect(self.sifre_degistir)
        self.btn_sil.clicked.connect(self.sil)
        btn_kapat.clicked.connect(self.accept)

        butonlar = QHBoxLayout()
        for b in (self.btn_duzenle, self.btn_sifre, self.btn_sil):
            butonlar.addWidget(b)
        butonlar.addStretch()
        butonlar.addWidget(btn_kapat)
        duzen = QVBoxLayout(self)
        duzen.addWidget(self.tablo)
        duzen.addLayout(butonlar)
        ikonlar.butonlara_uygula(self)
        self.yukle()

    def yukle(self):
        self.kayitlar = kullanicilar()
        # Kayıt satırın içinde saklanır; başlığa tıklanıp sıralansa da doğru kullanıcı seçilir
        tabloya_yaz(self.tablo, [[k.kullanici, k.adi_soyadi, k.telefon, k.mail, k.yetki] for k in self.kayitlar],
                    veri=list(range(len(self.kayitlar))))
        self.tablo.clearSelection()
        self.butonlari_ayarla()

    def secili(self):
        satirlar = self.tablo.selectionModel().selectedRows()
        if not satirlar:
            return None
        sira = satir_verisi(self.tablo, satirlar[0].row())
        return self.kayitlar[sira] if sira is not None else None

    def sec(self, kullanici):
        for r in range(self.tablo.rowCount()):
            if self.tablo.item(r, 0).text() == kullanici:
                self.tablo.selectRow(r)

    def butonlari_ayarla(self):
        var = self.secili() is not None
        for b in (self.btn_duzenle, self.btn_sifre, self.btn_sil):
            b.setEnabled(var)

    def duzenle(self):
        kayit = self.secili()
        if kayit and KullaniciDuzenle(kayit, self.aktif_kullanici, self).exec_():
            self.yukle()
            self.sec(kayit.kullanici)

    def sifre_degistir(self):
        kayit = self.secili()
        if kayit:
            SifreDegistir(kayit.kullanici, parent=self).exec_()

    def sil(self):
        kayit = self.secili()
        if not kayit:
            return
        engel = kullanici_servisi.silme_engeli(kayit, self.aktif_kullanici)
        if engel:
            QMessageBox.warning(self, "Uyarı!", str(engel))
            return
        if onay(f"'{kayit.kullanici}' ({kayit.adi_soyadi}) kullanıcısı silinsin mi?\nBu işlem geri alınamaz.") == QMessageBox.Yes:
            try:
                kullanici_servisi.sil(kayit, self.aktif_kullanici)
            except KuralHatasi as hata:
                QMessageBox.warning(self, "Uyarı!", str(hata))
            self.yukle()
