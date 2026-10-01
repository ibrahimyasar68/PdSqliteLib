## Buton ve sekme ikonları testleri ##
import os

import pytest
from PyQt5.QtGui import QIcon

from acodes import ikonlar
from acodes.guest import Guest
from acodes.kullanici_yonetimi import KullaniciYonetimi, SifreDegistir
from acodes.library import Library


@pytest.mark.parametrize("ad", sorted(ikonlar.CIZIMLER))
def test_her_ikon_cizilir(app, ad):
    simge = ikonlar.ikon(ad)
    normal = simge.pixmap(32, 32, QIcon.Normal).toImage()
    pasif = simge.pixmap(32, 32, QIcon.Disabled).toImage()
    assert not normal.isNull()
    dolu = [(x, y) for x in range(32) for y in range(32) if normal.pixelColor(x, y).alpha() > 0]
    assert len(dolu) > 20                                              # boş resim değil
    x, y = max(dolu, key=lambda n: normal.pixelColor(*n).alpha())
    assert normal.pixelColor(x, y) != pasif.pixelColor(x, y)          # pasif hali farklı renkte


def test_eslemelerdeki_ikonlar_tanimli():
    assert set(ikonlar.BUTON_IKONLARI.values()) <= set(ikonlar.CIZIMLER)
    assert set(ikonlar.SEKME_IKONLARI.values()) <= set(ikonlar.CIZIMLER)


def test_panel_butonlarinda_ikon(app, uyarilar):
    lib = Library()
    q = lib.QtLibrary
    for buton in (q.pushButton_2_temizle, lib.kitaplar.btn_kaydet, lib.kitaplar.btn_sil,
                  lib.odunc.btn_ver, lib.odunc.btn_iade, lib.odunc.btn_aktar, lib.filtre.btn_temizle,
                  q.pushButton_1_cikis, lib.ayarlar.buton("Yedek Al")):
        assert not buton.icon().isNull(), buton.text()


def test_sekmelerde_ikon(app, uyarilar):
    for panel in (Library(), Guest()):
        t = panel.QtLibrary.tabWidget
        assert all(not t.tabIcon(i).isNull() for i in range(t.count()))


def test_pencerelerde_ikon(app):
    y = KullaniciYonetimi("admin")
    assert all(not b.icon().isNull() for b in (y.btn_duzenle, y.btn_sifre, y.btn_sil))
    s = SifreDegistir("admin")
    from PyQt5.QtWidgets import QPushButton
    assert all(not b.icon().isNull() for b in s.findChildren(QPushButton))


def test_ikincil_ve_asil_butonlar(app, uyarilar):
    lib = Library()
    k = lib.kitaplar
    assert k.btn_kaydet.property("rol") is None                         # asıl işlem: dolu mavi
    assert k.btn_vazgec.property("rol") == "ikincil" and k.btn_yeni.property("rol") == "ikincil"
    assert lib.odunc.btn_ver.property("rol") is None and lib.odunc.btn_aktar.property("rol") == "ikincil"
    assert lib.QtLibrary.pushButton_2_temizle.property("rol") == "ikincil"
    y = KullaniciYonetimi("admin")
    assert y.btn_sil.objectName() == "kullanici_sil"                    # silme kırmızı


def test_acilir_liste_ve_sayi_kutusu_oklari(app):
    import os
    from acodes import tema
    yollar = ikonlar.ok_resimleri("#475569")
    assert all(os.path.getsize(y) > 0 for y in yollar.values())
    stil = tema.qss()
    assert yollar["asagi"] in stil and "QSpinBox::up-arrow" in stil and "QComboBox::drop-down" in stil


def test_baslik_yazisi_gomulu(app):
    from PyQt5.QtGui import QFontDatabase
    from acodes import tema
    assert tema.baslik_yazisini_yukle()
    assert tema.BASLIK_YAZISI in QFontDatabase().families()
    assert os.path.exists(os.path.join(tema.font_klasoru(), "OFL.txt"))      # lisans fontla birlikte dağıtılır
