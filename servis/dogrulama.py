## Alan doğrulamaları: ISBN, telefon, e-posta, şifre ##

import re

SIFRE_EN_AZ = 6


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


def telefon_gecerli(tel):
    return re.fullmatch(r"\d{10}", tel) is not None


def mail_gecerli(mail):
    return re.fullmatch(r"[\w.+-]+@[\w-]+(\.[\w-]+)*\.[a-zA-Z]{2,}", mail) is not None


def sifre_hatasi(sifre, tekrar=None):
    """Şifre kurallara uymuyorsa hata mesajını, uyuyorsa None döndürür."""
    if len(sifre) < SIFRE_EN_AZ:
        return f"Şifre en az {SIFRE_EN_AZ} karakter olmalıdır!"
    if tekrar is not None and sifre != tekrar:
        return "Şifreler birbiriyle aynı değil!"
    return None
