## Kitap Verme > Ödünç ve İade: ödünç verme, iade alma ve dışarıdaki kitaplar tek ekranda ##
import datetime

import pytest
from PyQt5.QtCore import Qt

from conftest import sec
from acodes.library import Library
from PyQt5.QtGui import QColor
from acodes import tema
from database import odunc
from database.dbframe import kopya_durumu

BUGUN = datetime.date.today()


def gun_once(n):
    return str(BUGUN - datetime.timedelta(days=n))


def odunc_ekle(db, user_id, book_id, verilis):
    db.execute("INSERT INTO follow VALUES (?,?,?,'10:00 ','out','','')", (str(user_id), str(book_id), verilis))
    db.commit()


@pytest.fixture
def lib(app, uyarilar):
    return Library()


@pytest.fixture
def o(lib):
    return lib.odunc


def kolon(tablo, c):
    return [tablo.item(r, c).text() for r in range(tablo.rowCount())]


def uye_sec(o, user_id):
    o.uye.setCurrentIndex(o.uye.findData(user_id))


def odunc_ver(o, kitap, user_id):
    sec(o.kitap, kitap)
    uye_sec(o, user_id)
    o.odunc_ver()


def satiri_sec(o, kitap):
    o.tablo.selectRow(kolon(o.tablo, 0).index(kitap))


# --- Ekran ---

def test_eski_uc_ekran_yerine_tek_ekran(lib):
    t = lib.QtLibrary.tabWidget_6
    assert [t.tabText(i) for i in range(t.count())] == ["Ödünç ve İade", "Ödünç Geçmişi"]
    assert t.currentWidget() is lib.odunc


def test_disaridaki_kitaplar(lib, o, db):
    odunc_ekle(db, 3, 1, gun_once(3))
    odunc_ekle(db, 4, 2, gun_once(20))
    o.yenile()
    assert o.tablo.rowCount() == 2
    # en eski ödünç en üstte ve kırmızı
    assert kolon(o.tablo, 0) == ["Esir Şehrin İnsanları", "Yol Ayrımı"]
    assert o.tablo.item(0, 2).text() == "Ayşe Yılmaz" and o.tablo.item(0, 6).text() == "5 gün gecikti"
    assert o.tablo.item(0, 5).text() == odunc.tarih_yazi(BUGUN - datetime.timedelta(days=5))
    assert o.tablo.item(0, 0).background().color() == QColor(tema.GECIKME_ARKA)
    assert o.tablo.item(1, 0).background().color() != QColor(tema.GECIKME_ARKA) and o.tablo.item(1, 6).text() == "12 gün kaldı"
    assert o.ozet.text() == "Dışarıda 2 kitap, 1 tanesinin teslim süresi geçmiş"


def test_arama(o, db):
    odunc_ekle(db, 3, 1, gun_once(3))
    odunc_ekle(db, 4, 6, gun_once(2))
    o.yenile()
    o.arama.setText("zweig")                          # yazara göre
    assert kolon(o.tablo, 0) == ["Satranç"] and o.ozet.text().endswith("aramaya uyan 1")
    o.arama.setText("ayse")                           # üyeye göre, Türkçe karakter farkı gözetmez
    assert o.tablo.rowCount() == 2


def test_bos_liste_mesaji(o):
    assert o.tablo.rowCount() == 0 and o.tablo.bos_durum.etiket.text() == "Şu an dışarıda kitap yok."
    assert not o.btn_iade.isEnabled() and "üstteki listeden" in o.iade_bilgi.text()


# --- Ödünç verme ---

def test_secince_bilgiler_gelir_ve_buton_acilir(o):
    assert not o.btn_ver.isEnabled() and o.ver_bilgi.text() == "Ödünç vermek için kitap ve üye seçin."
    sec(o.kitap, "Satranç")
    assert o.kitap_bilgi.text() == "Stefan ZWEIG · İş Bankası Yayınları · 2018\nMüsait kopya: 1 / 1"
    assert not o.btn_ver.isEnabled()
    uye_sec(o, 3)
    assert o.uye_bilgi.text() == "5551112233 · ayse@ornek.com\nElinde kitap yok"
    teslim = odunc.tarih_yazi(BUGUN + datetime.timedelta(days=15))
    assert o.btn_ver.isEnabled() and o.ver_bilgi.text() == f"Teslim tarihi: {teslim} (15 gün)"


def test_odunc_verme(lib, o, db):
    odunc_ver(o, "Satranç", 4)
    assert db.execute("SELECT userId, bookId, status FROM follow").fetchall() == [("4", "6", "out")]
    teslim = odunc.tarih_yazi(BUGUN + datetime.timedelta(days=15))
    assert lib.QtLibrary.statusbar.currentMessage() == f"İşlem kaydedildi. Teslim tarihi: {teslim}"
    assert o.kitap.currentIndex() == 0 and o.uye.currentIndex() == 0 and not o.btn_ver.isEnabled()
    # yeni ödünç listede seçili, iade kartında görünür
    assert kolon(o.tablo, 0) == ["Satranç"] and o.secili_odunc() == (4, 6) and o.btn_iade.isEnabled()
    assert lib.ana_sayfa.kartlar["disarida"].sayi.text() == "1"          # diğer ekranlar da yenilendi


def test_ayni_isimli_uyelerden_dogru_kisiye(o, db):
    assert "Ayşe Yılmaz (ayse1)" in [o.uye.itemText(i) for i in range(o.uye.count())]
    odunc_ver(o, "Yol Ayrımı", 4)
    assert db.execute("SELECT userId FROM follow").fetchall() == [("4",)]


def test_yazilan_adla_da_verilir(o, db):
    o.kitap.setEditText("satranç")                    # listeden seçmeden yazıldı
    uye_sec(o, 3)
    o.odunc_ver()
    assert db.execute("SELECT bookId FROM follow").fetchall() == [("6",)]


def test_seçim_eksikse_uyarir(lib, o):
    o.odunc_ver()
    assert lib.QtLibrary.statusbar.currentMessage() == "Kitap ve üye seçiniz!"


def test_oduncteki_kitap_verilemez(o, db, uyarilar):
    odunc_ekle(db, 3, 1, gun_once(1))
    o.yenile()
    sec(o.kitap, "Yol Ayrımı")
    uye_sec(o, 4)
    assert o.kitap_bilgi.text().endswith("Müsait kopya yok") and not o.btn_ver.isEnabled()
    assert o.ver_bilgi.text() == "Bu kitap başka bir üyede."
    o.odunc_ver()
    assert uyarilar[-1] == "Bu kitap başka bir üyede."
    assert db.execute("SELECT COUNT(*) FROM follow").fetchone()[0] == 1


def test_cok_kopyali_kitap(o, db):
    db.execute("UPDATE kayitlistesi SET Kopya=2 WHERE Id=6")
    db.commit()
    o.yenile()
    odunc_ver(o, "Satranç", 3)
    sec(o.kitap, "Satranç")
    assert o.kitap_bilgi.text().endswith("Müsait kopya: 1 / 2")
    uye_sec(o, 3)                                    # aynı üyeye ikinci kopya verilmez
    assert o.ver_bilgi.text() == "Bu kitabın bir kopyası zaten bu üyede. Önce iade alın." and not o.btn_ver.isEnabled()
    uye_sec(o, 4)
    o.odunc_ver()
    assert kopya_durumu(6) == (2, 2)
    sec(o.kitap, "Satranç")
    assert o.ver_bilgi.text() == "Bu kitabın 2 kopyasının hepsi üyelerde."


def test_geciken_kitabi_olan_uye_uyarisi(o, db):
    odunc_ekle(db, 3, 1, gun_once(20))
    odunc_ekle(db, 3, 2, gun_once(1))
    o.yenile()
    uye_sec(o, 3)
    assert o.uye_bilgi.text().endswith("Elinde 2 kitap var, 1 tanesinin teslim süresi geçmiş")
    assert "#DC2626" in o.uye_bilgi.styleSheet().upper()


def test_yeni_kitap_ve_uye_listelere_gelir(lib, o, db):
    sec(o.kitap, "Satranç")
    db.execute("INSERT INTO kayitlistesi (Adi) VALUES ('Yeni Gelen')")
    db.execute("INSERT INTO users (kullanici,sifre,adi_soyadi,yetki) VALUES ('veli','x','Veli Can','guest')")
    db.commit()
    lib.QtLibrary.tabWidget.setCurrentWidget(lib.QtLibrary.tab_6)     # sekme değişince yenilenir
    assert o.kitap.findText("Yeni Gelen") > 0 and o.uye.findText("Veli Can (veli)") > 0
    assert o.kitap.currentText() == "Satranç"                        # yarım kalan seçim korunur


# --- İade alma ---

def test_iade_alma(lib, o, db):
    odunc_ekle(db, 3, 1, gun_once(20))
    odunc_ekle(db, 4, 6, gun_once(2))
    o.yenile()
    satiri_sec(o, "Yol Ayrımı")
    assert o.btn_iade.isEnabled() and "Yol Ayrımı" in o.iade_bilgi.text() and "5 gün gecikti" in o.iade_bilgi.text()
    o.iade_al()
    assert db.execute("SELECT status FROM follow WHERE bookId='1'").fetchone()[0] == "in"
    assert db.execute("SELECT status FROM follow WHERE bookId='6'").fetchone()[0] == "out"
    assert lib.QtLibrary.statusbar.currentMessage() == "'Yol Ayrımı' iade alındı (5 gün gecikti)."
    assert kolon(o.tablo, 0) == ["Satranç"] and not o.btn_iade.isEnabled()
    q = lib.QtLibrary
    assert q.tabWidget.tabText(q.tabWidget.indexOf(q.tab_6)) == "Kitap Verme"            # gecikme kalmadı


def test_siralanmis_listede_dogru_odunc_iade_edilir(o, db):
    odunc_ekle(db, 4, 6, gun_once(1))
    odunc_ekle(db, 3, 1, gun_once(1))
    o.yenile()
    o.tablo.sortItems(0, Qt.DescendingOrder)
    satiri_sec(o, "Satranç")
    o.iade_al()
    assert db.execute("SELECT bookId FROM follow WHERE status='in'").fetchall() == [("6",)]


def test_silinmis_uyenin_oduncu_iade_alinabilir(o, db):
    odunc_ekle(db, 999, 1, gun_once(1))
    o.yenile()
    assert o.tablo.item(0, 2).text() == "(silinmiş üye)"
    o.tablo.selectRow(0)
    o.iade_al()
    assert db.execute("SELECT status FROM follow").fetchone()[0] == "in"


def test_ana_sayfadan_iade_ekrani(lib, o, db):
    odunc_ekle(db, 3, 1, gun_once(20))
    odunc_ekle(db, 4, 6, gun_once(14))
    lib.ana_sayfa_yenile()
    o.arama.setText("tahir")                          # arama gizlese de seçilir
    lib.ana_sayfa.listeler["yaklasan"].tablo.cellDoubleClicked.emit(1, 0)
    q = lib.QtLibrary
    assert q.tabWidget.currentWidget() is q.tab_6 and q.tabWidget_6.currentWidget() is o
    assert o.secili_odunc() == (4, 6) and o.arama.text() == ""


def test_dis_aktar_butonu_ve_menu(o):
    assert o.btn_aktar.text() == "Dışa Aktar" and o.tablo.contextMenuPolicy() == Qt.CustomContextMenu


def test_listede_kalan_silinmis_kitap_ve_uye_verilemez(o, db):
    sec(o.kitap, "Satranç")
    uye_sec(o, 3)
    db.execute("DELETE FROM kayitlistesi WHERE Id=6")
    db.execute("DELETE FROM users WHERE id=3")
    db.commit()
    o.ver_durumu()                                       # liste henüz yenilenmedi: çökmeden engellenir
    assert o.kitap_bilgi.text() == "Bu kitap silinmiş." and not o.btn_ver.isEnabled()
