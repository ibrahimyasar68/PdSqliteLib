## Buton ve sekme ikonları ##
# İkonlar dosya yerine Qt ile çizilir: her boyutta ve Retina ekranda nettir, rengi temadan gelir,
# Mac ve Windows'ta aynı görünür. Çizimler 24x24'lük bir ızgarada ince çizgili sade bir stildedir.

import math
import os
import tempfile

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF
from PyQt5.QtWidgets import QPushButton

BUTON_RENGI = "#FFFFFF"
PASIF_RENGI = "#64748B"
SEKME_RENGI = "#475569"


def _cizgi(p, *noktalar):
    p.drawPolyline(QPolygonF([QPointF(x, y) for x, y in noktalar]))


def _cokgen(p, *noktalar):
    p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in noktalar]))


def _daire(p, x, y, r):
    p.drawEllipse(QPointF(x, y), r, r)


def _tepsi(p):
    _cizgi(p, (3, 15), (3, 19), (5, 21), (19, 21), (21, 19), (21, 15))


CIZIMLER = {
    "ara": lambda p: (_daire(p, 11, 11, 7), _cizgi(p, (16.5, 16.5), (21, 21))),
    "liste": lambda p: ([_cizgi(p, (8, y), (21, y)) for y in (6, 12, 18)], [_daire(p, 3.5, y, 0.6) for y in (6, 12, 18)]),
    "x": lambda p: (_cizgi(p, (18, 6), (6, 18)), _cizgi(p, (6, 6), (18, 18))),
    "kontrol": lambda p: _cizgi(p, (20, 6), (9, 17), (4, 12)),
    "sil": lambda p: (_cizgi(p, (3, 6), (21, 6)), _cizgi(p, (19, 6), (18, 21), (6, 21), (5, 6)),
                      _cizgi(p, (9, 6), (9, 3), (15, 3), (15, 6)), _cizgi(p, (10, 11), (10, 17)), _cizgi(p, (14, 11), (14, 17))),
    "disa_aktar": lambda p: (_tepsi(p), _cizgi(p, (17, 8), (12, 3), (7, 8)), _cizgi(p, (12, 3), (12, 15))),
    "indir": lambda p: (_tepsi(p), _cizgi(p, (7, 10), (12, 15), (17, 10)), _cizgi(p, (12, 15), (12, 3))),
    "ok_sag": lambda p: (_cizgi(p, (5, 12), (19, 12)), _cizgi(p, (12, 5), (19, 12), (12, 19))),
    "ok_sol": lambda p: (_cizgi(p, (19, 12), (5, 12)), _cizgi(p, (12, 5), (5, 12), (12, 19))),
    "guc": lambda p: (p.drawArc(QRectF(4, 5, 16, 16), 125 * 16, 290 * 16), _cizgi(p, (12, 2), (12, 12))),
    "kullanici_ekle": lambda p: (_daire(p, 9, 7, 4), _cizgi(p, (2, 21), (2, 19), (4, 16), (7, 15), (11, 15), (14, 16), (16, 19), (16, 21)),
                                 _cizgi(p, (20, 8), (20, 14)), _cizgi(p, (17, 11), (23, 11))),
    "kullanicilar": lambda p: (_daire(p, 9, 7, 4), _cizgi(p, (2, 21), (2, 19), (4, 16), (7, 15), (11, 15), (14, 16), (16, 19), (16, 21)),
                               p.drawArc(QRectF(13, 3, 7, 8), -90 * 16, 180 * 16), _cizgi(p, (18, 15), (21, 17), (22, 19), (22, 21))),
    "kilit": lambda p: (p.drawRoundedRect(QRectF(4, 11, 16, 11), 2, 2), p.drawArc(QRectF(7, 3, 10, 12), 0, 180 * 16),
                        _cizgi(p, (7, 9), (7, 11)), _cizgi(p, (17, 9), (17, 11))),
    "geri_yukle": lambda p: (p.drawArc(QRectF(3, 3, 18, 18), 20 * 16, 300 * 16), _cizgi(p, (2, 5), (3.5, 10), (8.5, 8.5))),
    "klasor": lambda p: _cokgen(p, (2, 5), (4, 3), (9, 3), (11, 6), (20, 6), (22, 8), (22, 19), (20, 21), (4, 21), (2, 19)),
    "kalem": lambda p: (_cokgen(p, (17, 3), (21, 7), (8, 20), (3, 21), (4, 16)), _cizgi(p, (14, 6), (18, 10))),
    "ev": lambda p: (_cizgi(p, (3, 10), (12, 3), (21, 10)), _cizgi(p, (5, 9), (5, 21), (19, 21), (19, 9)),
                     _cizgi(p, (10, 21), (10, 14), (14, 14), (14, 21))),
    "huni": lambda p: _cokgen(p, (22, 3), (2, 3), (10, 12.5), (10, 19), (14, 21), (14, 12.5)),
    "grafik": lambda p: (_cizgi(p, (18, 20), (18, 10)), _cizgi(p, (12, 20), (12, 4)), _cizgi(p, (6, 20), (6, 14)),
                         _cizgi(p, (3, 21), (21, 21))),
    "takas": lambda p: (_cizgi(p, (17, 2), (21, 6), (17, 10)), _cizgi(p, (3, 12), (3, 10), (7, 6), (21, 6)),
                        _cizgi(p, (7, 22), (3, 18), (7, 14)), _cizgi(p, (21, 12), (21, 14), (17, 18), (3, 18))),
    "disli": lambda p: (_daire(p, 12, 12, 3), _daire(p, 12, 12, 7),
                        [_cizgi(p, (12 + 7 * math.cos(a), 12 + 7 * math.sin(a)), (12 + 10 * math.cos(a), 12 + 10 * math.sin(a)))
                         for a in (i * math.pi / 4 for i in range(8))]),
    "kitap": lambda p: (_cokgen(p, (6.5, 2), (20, 2), (20, 22), (6.5, 22), (4, 19.5), (4, 4.5)),
                        _cizgi(p, (4, 19.5), (6.5, 17), (20, 17))),
    "goz": lambda p: (_goz(p), _daire(p, 12, 12, 3)),
    "goz_kapali": lambda p: (_goz(p), _cizgi(p, (3, 3), (21, 21))),
    "menu": lambda p: [_cizgi(p, (4, y), (20, y)) for y in (6, 12, 18)],
    "daralt": lambda p: (_cizgi(p, (15, 6), (9, 12), (15, 18)), _cizgi(p, (4, 4), (4, 20))),
    "asagi": lambda p: _cizgi(p, (5, 8.5), (12, 15.5), (19, 8.5)),
    "yukari": lambda p: _cizgi(p, (5, 15.5), (12, 8.5), (19, 15.5)),
}


def _goz(p):
    yol = QPainterPath(QPointF(1, 12))
    yol.quadTo(12, 1, 23, 12)
    yol.quadTo(12, 23, 1, 12)
    p.drawPath(yol)


def _resim(ad, renk, boyut=64):
    resim = QPixmap(boyut, boyut)
    resim.fill(Qt.transparent)
    p = QPainter(resim)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(boyut / 24, boyut / 24)
    kalem = QPen(QColor(renk), 2)
    kalem.setCapStyle(Qt.RoundCap)
    kalem.setJoinStyle(Qt.RoundJoin)
    p.setPen(kalem)
    p.setBrush(Qt.NoBrush)
    CIZIMLER[ad](p)
    p.end()
    return resim


def ok_resimleri(renk="#64748B"):
    """Açılır liste ve sayı kutusu okları için stil sayfasının kullanacağı PNG dosyaları.
    Stil sayfası resmi dosyadan okuduğu için geçici klasöre çizilir: {ad: yol}."""
    klasor = os.path.join(tempfile.gettempdir(), "pdsqlitelib_oklar")
    os.makedirs(klasor, exist_ok=True)
    yollar = {}
    for ad in ("asagi", "yukari"):
        yol = os.path.join(klasor, f"{ad}_{renk.strip('#')}.png")
        _resim(ad, renk, 48).save(yol)          # her açılışta yazılır: çizim değişirse eskisi kalmaz
        yollar[ad] = yol.replace(os.sep, "/")
    return yollar


def ikon(ad, renk=BUTON_RENGI, pasif=PASIF_RENGI):
    simge = QIcon()
    simge.addPixmap(_resim(ad, renk), QIcon.Normal)
    simge.addPixmap(_resim(ad, pasif), QIcon.Disabled)
    return simge


# Buton yazısına göre ikon (aynı işlev her yerde aynı ikonla görünür)
BUTON_IKONLARI = {
    "Listele": "liste", "Temizle": "x", "Bul": "ara", "Kaydet": "kontrol",
    "İptal": "x", "Sil": "sil", "Dışa Aktar": "disa_aktar", "Ödünç Ver": "ok_sag", "İade Al": "ok_sol",
    "Oturumu Kapat": "guc", "Yeni Kullanıcı Ekle": "kullanici_ekle", "Kullanıcı Yönetimi": "kullanicilar",
    "Şifremi Değiştir": "kilit", "Şifre Değiştir": "kilit", "Yedek Al": "indir", "Yedekten Geri Yükle": "geri_yukle",
    "Yedek Klasörünü Aç": "klasor", "İşaretlileri Birleştir": "kontrol", "Bu Öneriyi Yoksay": "x",
    "Düzenle": "kalem", "Kapat": "x", "Vazgeç": "x",
}

# Sekme nesnesinin adına göre ikon
SEKME_IKONLARI = {"tab_1": "ev", "tab_2": "liste", "tab_3": "kalem", "tab_4": "huni", "tab_5": "grafik",
                  "tab_6": "takas", "ayarlar": "disli", "kitaplarim": "kitap"}


# Yardımcı işlemler beyaz zeminli, çerçeveli (ikincil) gösterilir; asıl işlem (Kaydet, Ödünç Ver ...) mavi kalır
IKINCIL_BUTONLAR = {"Vazgeç", "Temizle", "Kapat", "Dışa Aktar", "Yeni Kitap", "Yedek Klasörünü Aç",
                    "Bu Öneriyi Yoksay", "İptal"}
IKINCIL_RENK = "#334155"


def butonlara_uygula(pencere):
    for buton in pencere.findChildren(QPushButton):
        ikincil = buton.text() in IKINCIL_BUTONLAR
        if ikincil and buton.property("rol") is None:
            buton.setProperty("rol", "ikincil")
            buton.style().unpolish(buton)
            buton.style().polish(buton)
        ad = BUTON_IKONLARI.get(buton.text())
        if ad and buton.icon().isNull():
            buton.setIcon(ikon(ad, IKINCIL_RENK) if ikincil else ikon(ad))


def sekmelere_uygula(sekmeler, sayfa_adlari):
    """sayfa_adlari: {sayfa bileşeni: SEKME_IKONLARI anahtarı}"""
    for sayfa, anahtar in sayfa_adlari.items():
        sekmeler.setTabIcon(sekmeler.indexOf(sayfa), ikon(SEKME_IKONLARI[anahtar], SEKME_RENGI, SEKME_RENGI))
