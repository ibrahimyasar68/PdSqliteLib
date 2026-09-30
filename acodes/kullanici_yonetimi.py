## Kullanıcı yönetimi ##
# Admin panelinden: kullanıcıları listeleme, düzenleme, şifre değiştirme ve silme.
# Guest panelinden: kendi şifresini değiştirme (SifreDegistir, eski şifre sorulur).

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAbstractItemView, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                             QHBoxLayout, QHeaderView, QLineEdit, QMessageBox, QPushButton,
                             QTableWidget, QVBoxLayout)
from acodes.tablo import satir_verisi, tablo_ayarla, tabloya_yaz
from bforms.onay import onay
from acodes import ikonlar, tema
from acodes.user import mail_gecerli, sifre_hatasi, telefon_gecerli
from database.dbbase import kullanici_guncelle, kullanici_sil, sifre_guncelle
from database.dbframe import admin_sayisi, df_user_all, giris_kontrol, kullanici_odunc_sayisi

YETKILER = ["admin", "guest"]

# Formlar koyu arka planlı panellerin üstünde açıldığı için açık ve okunur bir görünüm
def pencere_stili():
    """Pencereler panelden bağımsız açılsa da (ör. testlerde) aynı temayla, biraz daha büyük yazıyla görünür."""
    return tema.qss() + f"""
QDialog {{ background-color: {tema.SAYFA}; }}
QWidget {{ font-size: 16px; }}
QPushButton {{ padding: 6px 14px; }}
"""


class SifreDegistir(QDialog):
    """Şifre değiştirme. eski_sor=True ise kullanıcının mevcut şifresi de istenir."""

    def __init__(self, kullanici, eski_sor=False, parent=None):
        super().__init__(parent)
        self.kullanici = kullanici
        self.setWindowTitle(f"Şifre Değiştir: {kullanici}")
        self.setStyleSheet(pencere_stili())
        form = QFormLayout(self)
        self.eski = None
        if eski_sor:
            self.eski = QLineEdit(echoMode=QLineEdit.Password)
            form.addRow("Mevcut şifre:", self.eski)
        self.yeni = QLineEdit(echoMode=QLineEdit.Password)
        self.tekrar = QLineEdit(echoMode=QLineEdit.Password)
        form.addRow("Yeni şifre:", self.yeni)
        form.addRow("Yeni şifre (tekrar):", self.tekrar)
        butonlar = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        butonlar.button(QDialogButtonBox.Ok).setText("Kaydet")
        butonlar.button(QDialogButtonBox.Cancel).setText("Vazgeç")
        butonlar.accepted.connect(self.kaydet)
        butonlar.rejected.connect(self.reject)
        form.addRow(butonlar)
        ikonlar.butonlara_uygula(self)

    def kaydet(self):
        if self.eski is not None and giris_kontrol(self.kullanici, self.eski.text()) is None:
            QMessageBox.warning(self, "Uyarı!", "Mevcut şifre yanlış!")
            return
        hata = sifre_hatasi(self.yeni.text(), self.tekrar.text())
        if hata:
            QMessageBox.warning(self, "Uyarı!", hata)
            return
        sifre_guncelle(self.kullanici, self.yeni.text())
        QMessageBox.information(self, "Bilgi", "Şifre değiştirildi.")
        self.accept()


class KullaniciDuzenle(QDialog):
    """Ad soyad, telefon, mail ve yetki düzenleme (kullanıcı adı değiştirilemez)."""

    def __init__(self, kayit, aktif_kullanici, parent=None):
        super().__init__(parent)
        self.id, self.kullanici, adi_soyadi, telefon, mail, self.eski_yetki = kayit
        self.setWindowTitle(f"Kullanıcı Düzenle: {self.kullanici}")
        self.setStyleSheet(pencere_stili())
        form = QFormLayout(self)
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
        form.addRow("Kullanıcı adı:", QLineEdit(self.kullanici, readOnly=True, enabled=False))
        form.addRow("Adı soyadı:", self.adi_soyadi)
        form.addRow("Telefon:", self.telefon)
        form.addRow("Mail:", self.mail)
        form.addRow("Yetki:", self.yetki)
        butonlar = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        butonlar.button(QDialogButtonBox.Ok).setText("Kaydet")
        butonlar.button(QDialogButtonBox.Cancel).setText("Vazgeç")
        butonlar.accepted.connect(self.kaydet)
        butonlar.rejected.connect(self.reject)
        form.addRow(butonlar)
        ikonlar.butonlara_uygula(self)

    def kaydet(self):
        adi_soyadi = self.adi_soyadi.text().strip()
        telefon = self.telefon.text().strip()
        mail = self.mail.text().strip()
        yetki = self.yetki.currentText()
        if not adi_soyadi:
            hata = "Adı soyadı boş olamaz!"
        elif telefon and not telefon_gecerli(telefon):
            hata = "Telefon 10 haneli olmalıdır!"
        elif mail and not mail_gecerli(mail):
            hata = "Mail adresi geçerli değil!"
        elif self.eski_yetki == "admin" and yetki != "admin" and admin_sayisi() <= 1:
            hata = "Son admin kullanıcının yetkisi düşürülemez!"
        else:
            hata = None
        if hata:
            QMessageBox.warning(self, "Uyarı!", hata)
            return
        kullanici_guncelle(self.id, adi_soyadi, telefon, mail, yetki)
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
        self.btn_sil = QPushButton("Sil")
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
        self.kayitlar = df_user_all()
        # Kayıt satırın içinde saklanır; başlığa tıklanıp sıralansa da doğru kullanıcı seçilir
        tabloya_yaz(self.tablo, [[d or "" for d in k[1:]] for k in self.kayitlar], veri=list(range(len(self.kayitlar))))
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
            self.sec(kayit[1])

    def sifre_degistir(self):
        kayit = self.secili()
        if kayit:
            SifreDegistir(kayit[1], parent=self).exec_()

    def silme_engeli(self, kayit):
        """Kullanıcı silinemiyorsa nedenini, silinebiliyorsa None döndürür."""
        id, kullanici, _, _, _, yetki = kayit
        if kullanici == self.aktif_kullanici:
            return "Kendi hesabınızı silemezsiniz!"
        if yetki == "admin" and admin_sayisi() <= 1:
            return "Son admin kullanıcı silinemez!"
        odunc = kullanici_odunc_sayisi(id)
        if odunc:
            return f"Bu kullanıcının elinde iade edilmemiş {odunc} kitap var. Önce iade alın!"
        return None

    def sil(self):
        kayit = self.secili()
        if not kayit:
            return
        engel = self.silme_engeli(kayit)
        if engel:
            QMessageBox.warning(self, "Uyarı!", engel)
            return
        if onay(f"'{kayit[1]}' ({kayit[2]}) kullanıcısı silinsin mi?\nBu işlem geri alınamaz.") == QMessageBox.Yes:
            kullanici_sil(kayit[0])
            self.yukle()


def panel_butonu(ornek, metin, ad):
    """Paneldeki mevcut bir butonla aynı yazı tipi ve stilde yeni buton oluşturur."""
    buton = QPushButton(metin)
    buton.setObjectName(ad)
    buton.setFont(ornek.font())
    buton.setMinimumSize(ornek.minimumSize())
    buton.setMaximumSize(ornek.maximumSize())
    buton.setCursor(Qt.PointingHandCursor)
    buton.setStyleSheet(ornek.styleSheet().replace(ornek.objectName(), ad))
    return buton
