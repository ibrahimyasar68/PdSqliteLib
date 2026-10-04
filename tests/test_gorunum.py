## Görünüm: açık / koyu tema ##
import os
import re

import pytest
from PyQt5.QtWidgets import QApplication

from conftest import ADMIN_SIFRE, UYE_SIFRE
from acodes import tema, tercihler
from acodes.login import Login


def pencereleri_sil(app):
    """Önceki testlerden kalan pencereleri siler: çizim stili değişince Qt her açık pencereyi yeniden biçimlendirir,
    kalan yüzlerce pencere bu testleri yavaşlatıyor ve birbirine bağımlı kılıyordu."""
    from PyQt5.QtCore import QEvent
    for pencere in app.topLevelWidgets():
        pencere.close()
        pencere.deleteLater()
    QApplication.sendPostedEvents(None, QEvent.DeferredDelete)


@pytest.fixture(autouse=True)
def acik_temaya_don(app):
    pencereleri_sil(app)
    yield
    pencereleri_sil(app)
    tema.ayarla("acik")
    tema.uygulamaya_uygula(app)
    tercihler.yaz("gorunum/tema", "sistem")


def test_paletler_ayni_renkleri_tanimlar():
    assert tema.ACIK.keys() == tema.KOYU.keys()
    assert all(re.fullmatch(r"#[0-9A-F]{6}|\d+, \d+, \d+", d) for d in list(tema.ACIK.values()) + list(tema.KOYU.values()))


def test_ayarla_paleti_degistirir(app):
    tema.ayarla("koyu")
    assert tema.KOYU_MU and tema.KART == tema.KOYU["KART"] and tema.KOYU["KART"] in tema.qss()
    tema.uygulamaya_uygula(app)
    assert app.style().objectName().lower() == "fusion"
    tema.ayarla("acik")
    assert not tema.KOYU_MU and tema.KART == "#FFFFFF" and tema.KOYU["KART"] not in tema.qss()
    tema.ayarla("bilinmeyen")
    assert tema.GORUNUM == "sistem"


@pytest.mark.parametrize("kullanici,sifre", [("admin", ADMIN_SIFRE), ("ayse1", UYE_SIFRE)])
def test_ayarlardan_degisince_panel_ayni_yerde_yeniden_kurulur(app, uyarilar, kullanici, sifre):
    w = Login()
    w.show()
    w.QtLogin.lineEdit_kullanci_adi.setText(kullanici)
    w.QtLogin.lineEdit_parola.setText(sifre)
    w.giris()
    eski = w.library or w.guest
    eski.QtLibrary.tabWidget.setCurrentWidget(eski.ayarlar)
    sekme = eski.QtLibrary.tabWidget.currentIndex()
    eski.ayarlar.gorunum.butonlar["koyu"].click()
    yeni = w.library or w.guest
    assert yeni is not eski and not eski.isVisible() and yeni.isVisible()
    assert yeni.aktif_kullanici == kullanici and yeni.QtLibrary.tabWidget.currentIndex() == sekme
    assert tema.KOYU_MU and tercihler.oku("gorunum/tema") == "koyu"
    assert yeni.ayarlar.gorunum.butonlar["koyu"].isChecked()
    assert tema.KOYU["KART"] in w.styleSheet()                         # giriş ekranı da koyu
    yeni.oturumu_kapat()                                                # oturum kapatma yeni panelde de çalışır
    assert w.isVisible() and w.library is None and w.guest is None
    QApplication.processEvents()


def test_modullerde_sabit_renk_yok():
    """Renkler tema.py'deki paletten gelir (kenar menüsü, bildirimler ve grafik serileri dahil); tek istisna mavi
    butonların üstündeki beyaz ikon rengidir."""
    istisna = {"tema.py", "ikonlar.py"}
    klasor = os.path.join(os.path.dirname(__file__), "..", "acodes")
    bulunan = {}
    for ad in sorted(os.listdir(klasor)):
        if ad.endswith(".py") and ad not in istisna:
            renkler = re.findall(r"#[0-9A-Fa-f]{6}\b", open(os.path.join(klasor, ad), encoding="utf-8").read())
            if renkler:
                bulunan[ad] = renkler
    assert bulunan == {}


def test_modullerde_sabit_yazi_boyutu_yok():
    """Yazı boyutları tema.YAZI ölçeğinden gelir (stil sayfalarında ve kodla çizilen metinlerde)."""
    klasor = os.path.join(os.path.dirname(__file__), "..", "acodes")
    bulunan = {}
    for ad in sorted(os.listdir(klasor)):
        if ad.endswith(".py") and ad != "tema.py":
            metin = open(os.path.join(klasor, ad), encoding="utf-8").read()
            sabitler = re.findall(r"font-size: *\d+px|setPixelSize\(\d+\)|yazi_tipi\(\d+", metin)
            if sabitler:
                bulunan[ad] = sabitler
    assert bulunan == {}


def _parlaklik(renk):
    kanallar = [int(renk[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [k / 12.92 if k <= 0.03928 else ((k + 0.055) / 1.055) ** 2.4 for k in kanallar]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def kontrast(on, arka):
    a, b = sorted((_parlaklik(on), _parlaklik(arka)), reverse=True)
    return (a + 0.05) / (b + 0.05)


@pytest.mark.parametrize("palet", ["ACIK", "KOYU"])
def test_yazi_renkleri_okunur(palet):
    """Yazı renkleri kart, sıra sıra renkli satır ve sayfa zemininde en az 4,5:1 kontrastlı (WCAG AA)."""
    p = getattr(tema, palet)
    zayif = [(yazi, zemin, round(kontrast(p[yazi], p[zemin]), 2))
             for yazi in ("METIN", "ETIKET", "IKINCIL_METIN", "SOLUK", "BOS_METIN", "VURGU_YAZI")
             for zemin in ("KART", "KART_2", "SAYFA") if kontrast(p[yazi], p[zemin]) < 4.5]
    assert zayif == []
    assert kontrast(p["TEHLIKE_YAZI"], p["TEHLIKE_ACIK"]) >= 4.5      # zeminsiz Sil: üstüne gelince de okunur
    assert min(kontrast(p["TEHLIKE_YAZI"], p[z]) for z in ("KART", "SAYFA", "ZEMIN")) >= 4.5


def test_modullerde_sabit_animasyon_suresi_yok():
    """Animasyon süreleri tema.SURE ölçeğinden gelir."""
    klasor = os.path.join(os.path.dirname(__file__), "..", "acodes")
    bulunan = {}
    for ad in sorted(os.listdir(klasor)):
        if ad.endswith(".py") and ad != "tema.py":
            sabitler = re.findall(r"setDuration\(\d+|_solma\([^)]*, \d+\)", open(os.path.join(klasor, ad), encoding="utf-8").read())
            if sabitler:
                bulunan[ad] = sabitler
    assert bulunan == {}


def test_tema_degisince_eski_gorunum_solarak_kaybolur(app, uyarilar, monkeypatch):
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QLabel
    from acodes import hareket
    monkeypatch.setattr(hareket, "ANIMASYON", True)
    monkeypatch.setattr(hareket, "AZALT", False)
    w = Login()
    w.panel_ac("admin", "admin")
    eski = w.library
    eski.ayarlar.gorunum.butonlar["koyu"].click()
    yeni = w.library
    perde = yeni.findChild(QLabel, "tema_perdesi")
    assert perde is not None and perde.isVisible() and perde.geometry() == yeni.rect()
    assert not perde.pixmap().isNull()
    QTest.qWait(tema.SURE.uzun + 200)
    assert yeni.findChild(QLabel, "tema_perdesi") is None
    yeni.close()


def test_animasyon_kapaliyken_tema_perdesi_yok(app, uyarilar):
    from PyQt5.QtWidgets import QLabel
    w = Login()
    w.panel_ac("admin", "admin")
    w.library.ayarlar.gorunum.butonlar["koyu"].click()
    assert w.library.findChild(QLabel, "tema_perdesi") is None
    w.library.close()


def test_olcekler_artan_sirada():
    yazi = [v for k, v in vars(tema.YAZI).items() if not k.startswith("_") and not k.startswith("logo")]
    kose = [v for k, v in vars(tema.KOSE).items() if not k.startswith("_")]
    sure = [v for k, v in vars(tema.SURE).items() if not k.startswith("_")]
    assert yazi == sorted(yazi) and kose == sorted(kose) and sure == sorted(sure)
    assert tema.YAZI_PX == tema.YAZI.metin


def test_bildirim_ve_grafik_renkleri_temadan(app):
    from acodes import bildirim, grafikler
    tema.ayarla("koyu")
    assert grafikler.renk(0).name().upper() == tema.GRAFIK_KOYU[0]
    assert bildirim.renk("basari") == tema.KOYU["BASARI"] and bildirim.renk("uyari") == tema.KOYU["TEHLIKE"]
    tema.ayarla("acik")
    assert grafikler.renk(0).name().upper() == tema.VURGU
    assert grafikler.renk(len(tema.GRAFIK)) == grafikler.renk(0)


def _yerlesim(app, gorunum):
    from PyQt5.QtCore import QPoint
    from PyQt5.QtWidgets import QWidget
    from acodes.library import Library
    tema.ayarla(gorunum)
    tema.uygulamaya_uygula(app)
    w = Library()
    w.resize(1300, 800)
    w.show()
    olculer = {}
    t = w.QtLibrary.tabWidget
    for i in range(t.count()):
        t.setCurrentIndex(i)
        QApplication.processEvents()
        for j, x in enumerate(t.currentWidget().findChildren(QWidget)):
            if x.isVisible() and x.objectName() != "segment_vurgu":     # seçili tema vurgusu temaya göre yer değiştirir
                p = x.mapTo(w, QPoint())
                olculer[(i, j, type(x).__name__)] = (p.x(), p.y(), x.width(), x.height())
    w.close()
    return olculer


def test_acik_ve_koyu_temada_yerlesim_ayni(app, uyarilar, monkeypatch):
    """Tema değişince sayfa kaymasın: boşluklar, kaydırma çubukları ve tablo başlıkları iki temada aynı ölçüde.
    Açık temada Mac'teki gibi macOS stili kullanılır (koyu tema Fusion); farkı ancak böyle yakalar."""
    from PyQt5.QtWidgets import QStyleFactory
    if "macintosh" in QStyleFactory.keys():
        tema.uygulamaya_uygula(app)                          # ilk stil kaydedilsin, sonra Mac'inkiyle değiştirilir
        monkeypatch.setattr(tema, "_ILK_STIL", "macintosh")
    acik, koyu = _yerlesim(app, "acik"), _yerlesim(app, "koyu")
    assert acik.keys() == koyu.keys()
    assert [(k, acik[k], koyu[k]) for k in acik if acik[k] != koyu[k]] == []


def test_tema_degisince_kaydirma_ve_pencere_korunur(app, uyarilar):
    w = Login()
    w.panel_ac("admin", "admin")
    eski = w.library
    eski.QtLibrary.tabWidget.setCurrentWidget(eski.ayarlar)
    QApplication.processEvents()
    kaydirma = eski.ayarlar.verticalScrollBar()
    kaydirma.setValue(kaydirma.maximum())
    deger, geometri = kaydirma.value(), eski.geometry()
    eski.ayarlar.gorunum.butonlar["koyu"].click()
    yeni = w.library
    assert yeni.ayarlar.verticalScrollBar().value() == deger and yeni.geometry() == geometri
    assert yeni.bildirim.kutu.isHidden()                     # gecikme uyarısı her geçişte tekrar çıkmaz
    yeni.close()
