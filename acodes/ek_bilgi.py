## Kitap formlarındaki "Ek Bilgiler" kutusu: ISBN, kopya sayısı, raf yeri ve notlar ##

import re

from PyQt5.QtWidgets import QFormLayout, QGroupBox, QLineEdit, QPlainTextEdit, QSpinBox


def isbn_normal(metin):
    """Tire ve boşlukları atar, sondaki x'i büyütür: '978-975-07-0321-5' -> '9789750703215'"""
    return re.sub(r"[\s-]", "", str(metin or "")).upper()


def isbn_gecerli(metin):
    """ISBN-10 veya ISBN-13 kontrol basamağını doğrular."""
    isbn = isbn_normal(metin)
    if re.fullmatch(r"\d{9}[\dX]", isbn):
        toplam = sum((10 - i) * (10 if h == "X" else int(h)) for i, h in enumerate(isbn))
        return toplam % 11 == 0
    if re.fullmatch(r"\d{13}", isbn):
        toplam = sum(int(h) * (1 if i % 2 == 0 else 3) for i, h in enumerate(isbn))
        return toplam % 10 == 0
    return False


class EkBilgiler(QGroupBox):
    def __init__(self, parent=None, salt_okunur=False):
        super().__init__("Ek Bilgiler", parent)
        self.setStyleSheet("""
            QGroupBox { font: bold 12pt "Verdana"; }
            QLabel, QLineEdit, QSpinBox, QPlainTextEdit { font: 11pt "Verdana"; }
        """)
        self.isbn = QLineEdit()
        self.isbn.setPlaceholderText("ör. 978-975-07-0321-5 (isteğe bağlı)")
        self.kopya = QSpinBox()
        self.kopya.setRange(1, 999)
        self.kopya.setToolTip("Kütüphanedeki kopya sayısı: bu kadar kişiye aynı anda ödünç verilebilir")
        self.raf = QLineEdit()
        self.raf.setPlaceholderText("ör. A-3")
        self.notlar = QPlainTextEdit()
        self.notlar.setMaximumHeight(90)
        form = QFormLayout(self)
        form.setVerticalSpacing(12)
        form.addRow("ISBN:", self.isbn)
        form.addRow("Kopya sayısı:", self.kopya)
        form.addRow("Raf yeri:", self.raf)
        form.addRow("Notlar:", self.notlar)
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

    def hata(self):
        """Geçersiz bir değer varsa uyarı metnini, yoksa None döndürür."""
        if self.isbn.text().strip() and not isbn_gecerli(self.isbn.text()):
            return "ISBN geçerli değil. 10 veya 13 haneli ISBN'i kontrol edin (boş da bırakılabilir)."
        return None
