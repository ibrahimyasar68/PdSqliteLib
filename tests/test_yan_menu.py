## Sol kenar menüsü, segment anahtarı ve kolon seçici ##
import datetime

import pytest
from PyQt5.QtWidgets import QApplication

from acodes import tercihler
from acodes.guest import Guest
from acodes.library import Library
from acodes.yan_menu import ACIK_EN, KAPALI_EN, bas_harfler


@pytest.fixture(autouse=True)
def temiz_tercihler():
    for anahtar in ("menu/kapali", "kolonlar/kitap_listesi", "kolonlar/kitap_listesi_sorma"):
        tercihler.yaz(anahtar, "")
    yield


@pytest.fixture
def lib(app, uyarilar):
    l = Library()
    l.user_name("iyasar")
    return l


def ogeler(menu):
    return [b.ad for b, _ in menu.ogeler]


def test_menu_sekmelerin_yerinde(lib):
    m = lib.yan_menu
    q = lib.QtLibrary
    assert q.tabWidget.tabBar().isHidden()
    assert ogeler(m) == ["Giriş", "Kitap Listesi", "Kitap Kayıt", "Filtre", "İstatistik", "Kitap Verme", "Ayarlar"]
    m.ogeler[2][0].click()
    assert q.tabWidget.currentWidget() is q.tab_3 and m.grup.checkedId() == 2
    q.tabWidget.setCurrentWidget(lib.ayarlar)                   # başka yoldan geçince de menü işaretlenir
    assert m.grup.checkedButton() is m.ogeler[6][0]
    assert m.baslik.text() == "Yaşar Kütüphanesi"
    assert ogeler(Guest().yan_menu) == ["Giriş", "Kitap Listesi", "Filtre", "İstatistik", "Kitaplarım", "Ayarlar"]


def test_kullanici_karti(lib):
    m = lib.yan_menu
    assert (m.kul_ad.text(), m.kul_rol.text(), m.avatar.text()) == ("iyasar", "Yönetici", "İY")
    assert bas_harfler("Ayşe Yılmaz") == "AY" and bas_harfler("veli.can") == "VC"


def test_daralt_ve_hatirla(app, uyarilar, lib):
    m = lib.yan_menu
    assert not m.kapali and m.width() == ACIK_EN and m.ogeler[1][0].text().strip() == "Kitap Listesi"
    m.btn_daralt.click()
    assert m.kapali and m.maximumWidth() == KAPALI_EN
    assert m.ogeler[1][0].text() == "" and m.ogeler[1][0].toolTip() == "Kitap Listesi"    # sadece simge
    assert m.baslik.isHidden() and m.cikis.text() == "" and not m.cikis.icon().isNull()
    assert Library().yan_menu.kapali                            # bir sonraki açılışta hatırlanır
    m.btn_daralt.click()
    assert not m.kapali and m.cikis.text() == "Oturumu Kapat"


def test_gecikme_rozeti(app, uyarilar, db):
    eski = str(datetime.date.today() - datetime.timedelta(days=30))
    db.execute("INSERT INTO follow VALUES ('3','1',?,'10:00','out','','')", (eski,))
    db.commit()
    l = Library()
    buton, rozet = l.yan_menu.ogeler[5]
    assert buton.ad == "Kitap Verme" and rozet.text() == "1" and not rozet.isHidden()
    l.odunc.tablo.selectRow(0)
    l.odunc.iade_al()
    assert rozet.isHidden()


def test_alt_sekmeler_segment_anahtari(lib):
    q = lib.QtLibrary
    for alt in (q.tabWidget_3, q.tabWidget_5, q.tabWidget_6):
        assert alt.tabBar().isHidden()
    from acodes.yan_menu import SegmentAnahtari
    anahtar = q.tab_6.findChild(SegmentAnahtari)
    assert [b.text() for b in anahtar.grup.buttons()] == ["Ödünç ve İade", "Ödünç Geçmişi"]
    anahtar.grup.button(1).click()
    assert q.tabWidget_6.currentWidget() is lib.gecmis


# --- Kolon seçici ---

def test_kolon_gizle_hatirla_zorunlular_gizlenmez(app, uyarilar):
    l = Library()
    s, t = l.liste_kolonlari, l.QtLibrary.tableWidget_2
    s.goster(3, False)                                          # Çeviren
    s.goster(1, False)                                          # Adı: zorunlu, gizlenmez
    assert t.isColumnHidden(3) and not t.isColumnHidden(1)
    eylemler = s.menu().actions()
    assert not eylemler[1].isEnabled() and eylemler[0].isEnabled() and not eylemler[3].isChecked()
    assert Library().QtLibrary.tableWidget_2.isColumnHidden(3)  # hatırlanır
    s.hepsini_goster()
    assert not Library().QtLibrary.tableWidget_2.isColumnHidden(3)


def test_kayit_no_ve_isbn_varsayilan_gizli_secim_yapilinca_hatirlanir(app, uyarilar):
    from acodes import tercihler
    tercihler._dosya().remove("kolonlar/kitap_listesi")            # henüz seçim yapılmamış
    t = Library().QtLibrary.tableWidget_2
    assert t.isColumnHidden(0) and t.isColumnHidden(8) and not t.isColumnHidden(1)   # Kayıt No, ISBN
    l = Library()
    l.liste_kolonlari.goster(0, True)
    t = Library().QtLibrary.tableWidget_2
    assert not t.isColumnHidden(0) and t.isColumnHidden(8)
    l.liste_kolonlari.hepsini_goster()


def test_sigmayan_listede_soru_cikar_ve_bir_daha_sorulmaz(app, uyarilar):
    l = Library()
    q = l.QtLibrary
    l.resize(1100, 700)
    l.show()
    q.tabWidget.setCurrentWidget(q.tab_2)
    QApplication.processEvents()
    s = l.liste_kolonlari
    s.denetle()
    assert s.sigmiyor() and s.soru.isVisible()
    s.btn_sorma.click()
    assert not s.soru.isVisible()
    s.denetle()
    assert not s.soru.isVisible()
    l.close()


def test_kolon_secici_uc_listede(app, uyarilar):
    l = Library()
    for secici in (l.liste_kolonlari, l.kitaplar.kolonlar, l.filtre.kolonlar):
        assert secici.buton.text() == "Kolonlar" and secici.buton.property("rol") == "ikincil"


def test_daralma_ve_sayfa_gecisi_animasyonlu(app, uyarilar, monkeypatch):
    from PyQt5.QtTest import QTest
    from acodes import hareket, tema
    monkeypatch.setattr(hareket, "ANIMASYON", True)
    l = Library()
    l.resize(1200, 700)
    l.show()
    m = l.yan_menu
    m.btn_daralt.click()
    assert m.kapali and m.width() > KAPALI_EN                          # genişlik hemen değil, yumuşakça değişir
    QTest.qWait(tema.SURE.orta + 150)
    assert m.width() == KAPALI_EN
    m.btn_daralt.click()
    assert m.baslik.isHidden()                                          # açılırken yazılar genişlik oturunca gelir
    QTest.qWait(tema.SURE.orta + 150)
    assert m.width() == ACIK_EN and not m.baslik.isHidden()
    sayfa = l.QtLibrary.tab_2
    l.QtLibrary.tabWidget.setCurrentWidget(sayfa)
    assert sayfa.graphicsEffect() is not None                           # yeni sayfa belirerek gelir
    QTest.qWait(tema.SURE.kisa + 150)
    assert sayfa.graphicsEffect() is None                               # bitince efekt kalkar
    l.close()
