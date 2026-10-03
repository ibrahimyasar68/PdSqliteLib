## Geçiş animasyonları: satır parlaması ve "Hareketi azalt" ##
import pytest
from PyQt5.QtTest import QTest

from conftest import sec
from acodes import hareket, tema, tercihler
from acodes.library import Library


@pytest.fixture
def animasyonlu(monkeypatch):
    monkeypatch.setattr(hareket, "ANIMASYON", True)
    monkeypatch.setattr(hareket, "AZALT", False)


@pytest.fixture
def lib(app, uyarilar, animasyonlu):
    l = Library()
    l.resize(1300, 800)
    l.show()
    yield l
    l.close()


def secili_satir(tablo):
    return tablo.selectionModel().selectedRows()[0].row()


def test_kaydedilen_kitap_satiri_parlar_ve_soner(lib):
    q = lib.QtLibrary
    q.tabWidget.setCurrentWidget(q.tab_3)
    q.tabWidget_3.setCurrentWidget(lib.kitaplar)
    k = lib.kitaplar
    k.yeni()
    k.alan["Adi"].setText("Parlayan Kitap")
    k.kaydet()
    parlama = k.tablo._parlama
    assert parlama is not None and parlama.indeks.row() == secili_satir(k.tablo)
    assert parlama.geometry() == k.tablo.viewport().rect()
    QTest.qWait(tema.SURE.parlama + 200)
    assert k.tablo._parlama is None                                     # bitince kendini kaldırır


def test_odunc_verilen_satir_parlar(lib):
    o = lib.odunc
    lib.disaridakileri_goster()
    sec(o.kitap, "Satranç")
    o.uye.setCurrentIndex(o.uye.findData(3))
    o.odunc_ver()
    assert o.tablo._parlama is not None and o.tablo.item(o.tablo._parlama.indeks.row(), 0).text() == "Satranç"


def test_yeni_parlama_eskisini_kaldirir(lib):
    tablo = lib.QtLibrary.tableWidget_2
    lib.QtLibrary.tabWidget.setCurrentWidget(lib.QtLibrary.tab_2)
    ilk = hareket.satiri_parlat(tablo, 0)
    ikinci = hareket.satiri_parlat(tablo, 1)
    assert ilk is not ikinci and tablo._parlama is ikinci
    assert hareket.satiri_parlat(tablo, tablo.rowCount()) is None       # olmayan satır


def test_animasyon_kapaliyken_parlama_yok(app, uyarilar):
    l = Library()
    l.show()
    assert hareket.satiri_parlat(l.QtLibrary.tableWidget_2, 0) is None  # testlerde ANIMASYON = False
    l.close()


def test_hareketi_azalt_ayari(lib, monkeypatch):
    kutu = lib.ayarlar.gorunum.hareket
    assert not kutu.isChecked()
    kutu.setChecked(True)
    assert hareket.AZALT and not hareket.izinli() and tercihler.mantiksal(hareket.TERCIH)
    sayfa = lib.QtLibrary.tab_2
    lib.QtLibrary.tabWidget.setCurrentWidget(sayfa)
    assert sayfa.graphicsEffect() is None                               # sayfa beklemeden görünür
    lib.yan_menu.btn_daralt.click()
    assert lib.yan_menu.width() == lib.yan_menu.minimumWidth()          # menü hemen daralır
    lib.yan_menu.btn_daralt.click()
    lib.QtLibrary.statusbar.showMessage("Deneme silindi")
    lib.bildirim.kaybol()
    assert lib.bildirim.kutu.isHidden()                                 # bildirim solmadan kaybolur
    kutu.setChecked(False)
    assert not hareket.AZALT and not tercihler.mantiksal(hareket.TERCIH)


# --- 2. aşama: giriş, kartlar, grafikler, menü, hızlı arama, rozet, bildirim yığını ---

def test_yanlis_giriste_kart_sallanir_bos_alan_kirmizi(app, uyarilar, animasyonlu):
    from acodes.login import Login
    w = Login()
    w.show()
    q = w.QtLogin
    q.lineEdit_kullanci_adi.setText("admin")
    w.giris()                                                           # parola boş
    assert tema.TEHLIKE in q.lineEdit_parola.styleSheet()
    assert tema.TEHLIKE not in q.lineEdit_kullanci_adi.styleSheet()
    yer = w.kart.pos()
    q.lineEdit_parola.setText("yanlis")
    w.giris()
    assert w.kart._salla is not None
    QTest.qWait(tema.SURE.uzun + 150)
    assert w.kart._salla is None and w.kart.pos() == yer                 # yerine döner
    QTest.qWait(tema.SURE.parlama * 2)
    assert tema.TEHLIKE not in q.lineEdit_parola.styleSheet()           # çerçeve normale söner
    w.close()


def test_hatali_alan_vurgulanir(lib):
    q = lib.QtLibrary
    q.tabWidget.setCurrentWidget(q.tab_3)
    k = lib.kitaplar
    k.yeni()
    k.kaydet()                                                          # kitap adı boş
    assert tema.TEHLIKE in k.alan["Adi"].styleSheet()
    k.alan["Adi"].setText("ISBN'li")
    k.ek.isbn.setText("123")
    k.kaydet()
    assert tema.TEHLIKE in k.ek.isbn.styleSheet()


def test_hareket_azaltilinca_hata_yine_gorunur(app, uyarilar):
    from PyQt5.QtWidgets import QLineEdit
    alan = QLineEdit()
    alan.setStyleSheet("QLineEdit { padding: 2px; }")
    hareket.hata_vurgula(alan)                                          # testlerde animasyon kapalı
    assert tema.TEHLIKE in alan.styleSheet()
    QTest.qWait(tema.SURE.parlama * 2 + 100)
    assert alan.styleSheet() == "QLineEdit { padding: 2px; }"


def test_ana_sayfa_sayilari_sayarak_gelir(lib):
    kart = lib.ana_sayfa.kartlar["kitap"]
    assert kart.sayildi and kart.sayi._sayac is not None
    QTest.qWait(tema.SURE.sayac + 150)
    assert kart.sayi.text() == "8" and kart.sayi._sayac is None
    lib.yenile()                                                        # sonraki yenilemelerde sayı hemen yazılır
    assert kart.sayi._sayac is None and kart.sayi.text() == "8"


def test_kart_golgesi_yumusakca_buyur(lib):
    from PyQt5.QtCore import QEvent
    from PyQt5.QtWidgets import QApplication
    kart = lib.ana_sayfa.kartlar["kitap"]
    QApplication.sendEvent(kart, QEvent(QEvent.Enter))
    assert kart.golge.isEnabled() and kart.golge_animasyonu.state()
    QTest.qWait(tema.SURE.kisa + 100)
    assert kart.golge.blurRadius() == 22
    QApplication.sendEvent(kart, QEvent(QEvent.Leave))
    QTest.qWait(tema.SURE.kisa + 100)
    assert not kart.golge.isEnabled()


def test_grafikler_buyuyerek_cizilir(lib):
    q = lib.QtLibrary
    q.tabWidget.setCurrentWidget(q.tab_5)
    q.tabWidget_5.setCurrentIndex(1)
    g = lib.grafikler.yazarlar
    assert g.ilerleme < 1 and g.animasyon.state()
    assert g.oran(0) >= g.oran(len(g.veri) - 1)                         # ilk çubuk önde
    QTest.qWait(tema.SURE.sayac + 150)
    assert g.ilerleme == 1.0 and all(g.oran(i) == 1.0 for i in range(len(g.veri)))
    lib.grafikler.yenile()                                              # veri aynıysa yeniden çizilmez
    assert not g.animasyon.state()


def test_menu_vurgusu_kayarak_gider(lib):
    m = lib.yan_menu
    hedef = m.grup.button(3)
    hedef.click()
    vurgu = m.vurgu
    assert vurgu.animasyon.state() and vurgu.animasyon.endValue() == vurgu.hedef()
    QTest.qWait(tema.SURE.orta + 150)
    assert vurgu.cerceve.geometry() == vurgu.hedef() and vurgu.hedef().topLeft() == hedef.mapTo(m, hedef.rect().topLeft())
    m.btn_daralt.click()                                                # menü daralırken vurgu butonu izler
    QTest.qWait(tema.SURE.orta + 150)
    assert vurgu.cerceve.width() == hedef.width()
    m.btn_daralt.click()                                                # tercih kaydedilir: menüyü geri aç
    assert not tercihler.mantiksal("menu/kapali")


def test_segment_vurgusu_kayar(lib):
    from acodes.yan_menu import SegmentAnahtari
    q = lib.QtLibrary
    q.tabWidget.setCurrentWidget(q.tab_3)
    anahtar = q.tab_3.findChild(SegmentAnahtari)
    QTest.qWait(50)
    anahtar.grup.button(1).click()
    assert anahtar.vurgu.animasyon.state()
    QTest.qWait(tema.SURE.orta + 150)
    assert anahtar.vurgu.cerceve.geometry() == anahtar.grup.button(1).geometry()


def test_hizli_arama_kayarak_acilir(lib):
    lib.palet.ac()
    ilk = lib.palet.pos()
    assert lib.palet.isVisible()
    QTest.qWait(tema.SURE.kisa + 100)
    assert lib.palet.pos().y() == ilk.y() - 8 and lib.palet.pos().x() == ilk.x()    # 8 piksel yukarı kayar
    lib.palet.close()


def test_gecikme_rozeti_bir_kez_atar(app, uyarilar, animasyonlu, db):
    import datetime
    eski = str(datetime.date.today() - datetime.timedelta(days=30))
    db.execute("INSERT INTO follow VALUES ('3','1',?,'10:00','out','','')", (eski,))
    db.commit()
    l = Library()
    l.show()
    QTest.qWait(20)
    rozet = [r for _, r in l.yan_menu.ogeler if r.isVisible()][0]
    assert rozet.graphicsEffect() is not None
    QTest.qWait(tema.SURE.uzun * 4 + 200)
    assert rozet.graphicsEffect() is None                               # sürekli atmaz
    l.close()


def test_geri_al_karti_yeni_mesajla_kaybolmaz(lib):
    from acodes import bildirim
    b = lib.bildirim
    cagri = []
    b.eylemli("'Deneme' silindi", "Geri Al", lambda: cagri.append(1))
    eski = b.son
    lib.QtLibrary.statusbar.showMessage("Liste görüntülendi.")
    assert b.son is not eski and b.eskiler == [eski] and eski.kutu.isVisible()
    QTest.qWait(tema.SURE.orta + 100)
    assert eski.kutu.y() + eski.kutu.height() + bildirim.ARALIK == b.kutu.y()   # yeni kart altta, eski üstünde
    eski.eylem.click()                                                  # eski kartın Geri Al'ı hâlâ çalışır
    assert cagri == [1]
    QTest.qWait(tema.SURE.uzun + 150)
    assert b.eskiler == []
    lib.QtLibrary.statusbar.showMessage("Başka bir mesaj.")             # eylemsiz kart yeniden kullanılır
    assert b.eskiler == []


def test_en_fazla_uc_kart(lib):
    from acodes import bildirim
    b = lib.bildirim
    for i in range(5):
        b.eylemli(f"'Kitap {i}' silindi", "Geri Al", lambda: None)
    QTest.qWait(tema.SURE.uzun + 150)
    assert len([k for k in b.kartlar() if k.kutu.isVisible()]) == bildirim.UST_USTE
