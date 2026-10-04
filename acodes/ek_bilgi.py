## Kitap formlarındaki "Ek bilgiler" kutusu: ISBN, kopya sayısı, raf yeri ve notlar ##

from PyQt5.QtWidgets import QFormLayout, QGridLayout, QGroupBox, QLineEdit, QPlainTextEdit, QSpinBox

from acodes import tema
from acodes.yerlesim import etiketli, ustte_etiketli_form
from servis.dogrulama import isbn_normal


class EkBilgiler(QGroupBox):
    def __init__(self, parent=None, salt_okunur=False, izgara=False):
        """izgara=True: alanlar iki sütunda (geniş ve alçak form, ör. listenin altındaki kitap formu)."""
        super().__init__("Ek bilgiler", parent)
        self.setStyleSheet(f"QGroupBox {{ font-weight: {tema.YARI_KALIN}; font-size: {tema.YAZI.alt_baslik}px; }}")
        self.isbn = QLineEdit()
        self.isbn.setPlaceholderText("ör. 978-975-07-0321-5 (isteğe bağlı)")
        self.kopya = QSpinBox()
        self.kopya.setRange(1, 999)
        self.kopya.setToolTip("Kütüphanedeki kopya sayısı: bu kadar kişiye aynı anda ödünç verilebilir")
        self.raf = QLineEdit()
        self.raf.setPlaceholderText("ör. A-3")
        self.notlar = QPlainTextEdit()
        self.notlar.setMaximumHeight(90)
        # Etiketler alanların üstünde, iki noktasız (kitap formuyla aynı)
        if izgara:
            g = QGridLayout(self)
            g.setHorizontalSpacing(12)
            g.setVerticalSpacing(10)
            self.isbn.setPlaceholderText("ör. 978-975-07-0321-5")
            g.addLayout(etiketli("ISBN (isteğe bağlı)", self.isbn), 0, 0)
            g.addLayout(etiketli("Kopya sayısı", self.kopya), 0, 1)
            g.addLayout(etiketli("Raf yeri", self.raf), 0, 2)
            g.addLayout(etiketli("Notlar", self.notlar), 1, 0, 2, 3)
            g.setColumnStretch(0, 3)
            g.setColumnStretch(1, 1)
            g.setColumnStretch(2, 1)
        else:
            form = ustte_etiketli_form(QFormLayout(self))
            form.addRow("ISBN", self.isbn)
            form.addRow("Kopya sayısı", self.kopya)
            form.addRow("Raf yeri", self.raf)
            form.addRow("Notlar", self.notlar)
        if salt_okunur:
            for alan in (self.isbn, self.kopya, self.raf, self.notlar):
                alan.setReadOnly(True)
            self.kopya.setButtonSymbols(QSpinBox.NoButtons)

    def degerler(self):
        """(isbn, kopya, raf, notlar) — ISBN tiresiz saklanır."""
        return (isbn_normal(self.isbn.text()), self.kopya.value(),
                " ".join(self.raf.text().split()), self.notlar.toPlainText().strip())

    def doldur(self, isbn, kopya, raf, notlar):
        self.isbn.setText(isbn or "")
        self.kopya.setValue(int(kopya or 1))
        self.raf.setText(raf or "")
        self.notlar.setPlainText(notlar or "")

    def temizle(self):
        self.doldur("", 1, "", "")
