## Yazdıkça süzülen açılır listeler testleri ##
import pytest
from PyQt5.QtWidgets import QComboBox

from acodes.aranabilir import aranabilir_yap, secili_veri
from acodes.library import Library


@pytest.fixture
def cmb(app):
    c = QComboBox()
    c.addItem(" Seçiniz...")
    for veri, metin in [(3, "İklimler (Görsel Yayınlar, 1992)"), (4, "İklimler (Şaheser Romanlar, 1985)"),
                        (7, "Kuyucaklı Yusuf"), (8, "Denemeler")]:
        c.addItem(metin, veri)
    return aranabilir_yap(c)


def gorunenler(c):
    s = c.suzgec
    return [s.index(i, 0).data() for i in range(s.rowCount())]


@pytest.mark.parametrize("yazilan,beklenen", [
    ("iklim", ["İklimler (Görsel Yayınlar, 1992)", "İklimler (Şaheser Romanlar, 1985)"]),
    ("IKLIMLER saheser", ["İklimler (Şaheser Romanlar, 1985)"]),    # Türkçe karakter ve büyük harf farksız
    ("kuyucakli", ["Kuyucaklı Yusuf"]),
    ("yok böyle", []),
])
def test_yazdikca_suzulur(cmb, yazilan, beklenen):
    cmb.suzgec.ayarla(yazilan)
    assert gorunenler(cmb) == beklenen


def test_bos_aramada_hepsi(cmb):
    cmb.suzgec.ayarla("")
    assert len(gorunenler(cmb)) == 5


def test_yazilan_metin_listeye_eklenmez(cmb):
    assert cmb.isEditable() and cmb.insertPolicy() == QComboBox.NoInsert


def test_listeden_secilince_veri(cmb):
    cmb.setCurrentIndex(3)
    assert secili_veri(cmb) == 7


@pytest.mark.parametrize("yazilan,veri", [
    ("Kuyucaklı Yusuf", 7),     # tam ad
    ("kuyucakli yusuf", 7),     # farklı yazımla tam ad
    ("deneme", 8),              # tek eşleşen parça
    ("iklimler", None),         # iki eşleşme: belirsiz
    ("olmayan", None),
    ("", None),
])
def test_yazilan_metinden_secim(cmb, yazilan, veri):
    cmb.setCurrentIndex(0)
    cmb.setEditText(yazilan)
    assert secili_veri(cmb) == veri


def test_seciniz_secenegi_veri_vermez(cmb):
    cmb.setCurrentIndex(0)
    assert secili_veri(cmb) is None


# --- Panellerde ---

def test_panelde_aranabilir_listeler(app, uyarilar):
    lib = Library()
    q = lib.QtLibrary
    for c in (q.comboBox_6_1_1_liste_kitap,
              q.comboBox_6_1_2_liste_kisi, q.comboBox_6_2_1_liste_kisi, lib.filtre.combo["Yazari"]):
        assert c.isEditable() and c.completer() is not None


def test_yazarken_filtreye_eklenmez(app, uyarilar):
    lib = Library()
    cmb = lib.filtre.combo["Yazari"]
    cmb.setEditText("Kem")                        # yarım yazılmış metin seçim sayılmaz
    assert lib.filtre.secimler["Yazari"] == []
    cmb.setCurrentIndex(cmb.findText("Kemal TAHİR"))
    assert lib.filtre.secimler["Yazari"] == ["Kemal TAHİR"]
