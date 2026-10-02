## Görünüm: açık / koyu tema ##
import os
import re

import pytest
from PyQt5.QtWidgets import QApplication

from conftest import ADMIN_SIFRE, UYE_SIFRE
from acodes import tema, tercihler
from acodes.login import Login


@pytest.fixture(autouse=True)
def acik_temaya_don(app):
    yield
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
    """Renkler tema.py'deki paletten gelir; aşağıdakiler her iki temada aynı kalması istenen bilinçli istisnalardır:
    koyu kenar menüsü, fotoğraf üstündeki başlık, bildirim kutuları, grafik serileri, mavi buton ikonu."""
    istisna = {"tema.py", "yan_menu.py", "bildirim.py", "grafikler.py", "ikonlar.py", "ana_sayfa.py"}
    klasor = os.path.join(os.path.dirname(__file__), "..", "acodes")
    bulunan = {}
    for ad in sorted(os.listdir(klasor)):
        if ad.endswith(".py") and ad not in istisna:
            renkler = re.findall(r"#[0-9A-Fa-f]{6}\b", open(os.path.join(klasor, ad), encoding="utf-8").read())
            if renkler:
                bulunan[ad] = renkler
    assert bulunan == {}


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
            if x.isVisible():
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
    assert [k for k in acik if acik[k] != koyu[k]] == []


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
