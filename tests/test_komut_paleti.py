## Hızlı arama (Ctrl+K) ve kitap satırlarındaki sağ tık işlemleri ##
import datetime

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QShortcut

from acodes.guest import Guest
from acodes.komut_paleti import eslesir
from acodes.library import Library


@pytest.fixture
def lib(app, uyarilar):
    l = Library()
    l.resize(1300, 800)
    l.show()
    yield l
    l.palet.close()
    l.close()


def gruplar(panel, metin):
    return {grup: [o[0] for o in ogeler] for grup, ogeler in panel.komut_kaynagi(metin)}


def gorunen(palet):
    return [palet.liste.item(i).text() for i in range(palet.liste.count())]


def test_eslesir_turkce_ve_tum_kelimeler():
    assert eslesir("kuyucakli", "Kuyucaklı Yusuf") and eslesir("tahir yol", "Yol Ayrımı", "Kemal TAHİR")
    assert not eslesir("tahir iklim", "Yol Ayrımı", "Kemal TAHİR")


def test_bos_aramada_bolumler_ve_islemler(lib):
    g = gruplar(lib, "")
    assert g["Bölümler"][:3] == ["Giriş", "Kitap Listesi", "Kitap Kayıt"] and "Ayarlar" in g["Bölümler"]
    assert {"Yeni kitap", "Ödünç ver", "İade al", "Yedek al", "Oturumu kapat"} <= set(g["İşlemler"])
    assert "Kitaplar" not in g                                 # tek harfle yüzlerce kitap listelenmez


def test_aramada_kitap_ve_uye_bulunur(lib):
    g = gruplar(lib, "tahir")
    assert g["Kitaplar"] == ["Yol Ayrımı", "Esir Şehrin İnsanları"] and g["Üyeler"] == []
    assert gruplar(lib, "ayse")["Üyeler"] == ["Ayşe Yılmaz", "Ayşe Yılmaz"]
    assert gruplar(lib, "yedek")["İşlemler"] == ["Yedek al"]


def test_ctrl_k_paleti_acar_oklar_ve_enter(lib):
    kisayollar = [k for k in lib.findChildren(QShortcut) if k.key() == QKeySequence("Ctrl+K")]
    assert len(kisayollar) == 1
    kisayollar[0].activated.emit()
    p = lib.palet
    assert p.isVisible() and p.arama.text() == ""
    QTest.keyClicks(p.arama, "kuyucak")
    assert "KITAPLAR" in gorunen(p) and p.liste.currentItem().text().startswith("Kuyucaklı Yusuf")
    QTest.keyClick(p.arama, Qt.Key_Return)
    QTest.qWait(10)
    q = lib
    assert not p.isVisible() and q.sekmeler.currentWidget() is q.kayit and lib.kitaplar.kitap_id == 7


def test_ok_tuslari_basliklari_atlar(lib):
    p = lib.palet
    p.ac()
    assert p.liste.currentRow() == 1 and p.liste.currentItem().text().startswith("Giriş")   # 0: grup başlığı
    QTest.keyClick(p.arama, Qt.Key_Up)                        # başa döner: son öğe
    assert p.liste.currentItem().data(Qt.UserRole) is not None
    QTest.keyClick(p.arama, Qt.Key_Escape)
    assert not p.isVisible()


def test_uye_secince_odunc_ekrani_o_uyeyle_acilir(lib):
    _, _, _, islev = next(o for g, ogeler in lib.komut_kaynagi("ayse1") if g == "Üyeler" for o in ogeler)
    islev()
    assert lib.alt_sekmeler[lib.verme].currentWidget() is lib.odunc and lib.odunc.uye.currentData() == 3


def test_menude_hizli_ara_butonu(lib):
    lib.yan_menu.btn_ara.click()
    assert lib.palet.isVisible()
    lib.palet.close()
    lib.yan_menu.daralt(True, kaydet=False)
    assert lib.yan_menu.btn_ara.text() == ""
    lib.yan_menu.daralt(False, kaydet=False)


def test_uyede_uye_ve_yonetici_islemleri_yok(app):
    g = Guest()
    sonuc = gruplar(g, "")
    assert "Yeni kitap" not in sonuc["İşlemler"] and "Kitaplarım" in sonuc["Bölümler"]
    assert "Üyeler" not in gruplar(g, "ayse")
    _, _, _, islev = next(o for grup, ogeler in g.komut_kaynagi("satranç") if grup == "Kitaplar" for o in ogeler)
    islev()
    assert g.sekmeler.currentWidget() is g.liste and g.liste.arama.text() == "Satranç"
    assert g.liste.tablo.rowCount() == 1


# --- Sağ tık ---

def menu_metinleri(tablo, satir):
    konum = tablo.visualRect(tablo.model().index(satir, 1)).center()
    return {e.text(): e for e in tablo.sag_tik_menu(konum).actions() if e.text()}


def test_kitap_listesinde_sag_tik_islemleri(lib, db):
    q = lib
    q.sekmeler.setCurrentWidget(q.liste)
    satir = next(r for r in range(q.liste.tablo.rowCount()) if q.liste.tablo.item(r, 1).text() == "Satranç")
    e = menu_metinleri(q.liste.tablo, satir)
    assert list(e)[:4] == ["Düzenle", "Ödünç ver...", "İade al...", "Ödünç geçmişi"]
    assert e["Ödünç ver..."].isEnabled() and not e["İade al..."].isEnabled() and not e["Ödünç geçmişi"].isEnabled()
    assert "Excel / CSV olarak dışa aktar..." in e
    e["Ödünç ver..."].trigger()
    assert q.alt_sekmeler[q.verme].currentWidget() is lib.odunc and lib.odunc.kitap.currentData() == 6


def test_sag_tik_iade_ve_gecmis(lib, db):
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES ('3','6',?,'10:00','out','','')", (str(datetime.date.today()),))
    db.commit()
    lib.yenile()
    t = lib.filtre.tablo
    lib.filtre.combo["Yazari"].setEditText("zweig")
    e = menu_metinleri(t, 0)
    assert "Ödünç ver (müsait kopya yok)" in e and not e["Ödünç ver (müsait kopya yok)"].isEnabled()
    e["İade al..."].trigger()
    assert lib.odunc.secili_odunc() == (3, 6)
    menu_metinleri(t, 0)["Ödünç geçmişi"].trigger()
    assert lib.alt_sekmeler[lib.verme].currentWidget() is lib.gecmis and lib.gecmis.kitap.currentData() == 6


def test_odunc_listesinde_sag_tik(lib, db):
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES ('3','1',?,'10:00','out','','')", (str(datetime.date.today()),))
    db.commit()
    lib.odunc.yenile()
    e = menu_metinleri(lib.odunc.tablo, 0)
    assert lib.odunc.secili_odunc() == (3, 1)                 # sağ tıklanan satır seçilir
    e["Hatırlatma metnini kopyala"].trigger()
    assert "Yol Ayrımı" in QApplication.clipboard().text()
