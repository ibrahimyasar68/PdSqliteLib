## Ana sayfa özet panosu testleri ##
import datetime

import pytest
from PySide6.QtCore import Qt

from acodes.guest import Guest
from acodes.library import Library
from PySide6.QtGui import QColor
from acodes import ana_sayfa, tema
from database import odunc

BUGUN = datetime.date.today()


def gun_once(n):
    return str(BUGUN - datetime.timedelta(days=n))


def odunc_ekle(db, user_id, book_id, verilis):
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES (?,?,?,'10:00','out','','')", (str(user_id), str(book_id), verilis))
    db.commit()


def kart(panel, anahtar):
    k = panel.ana_sayfa.kartlar[anahtar]
    return k.sayi.text(), k.alt.text()


@pytest.fixture
def veri(db):
    db.execute("UPDATE kayitlistesi SET Kopya=2 WHERE Id=1")
    odunc_ekle(db, 3, 1, gun_once(20))    # gecikmiş
    odunc_ekle(db, 3, 6, gun_once(13))    # 2 gün sonra teslim
    odunc_ekle(db, 4, 7, gun_once(1))     # 14 gün var: listede görünmez
    return db


@pytest.fixture
def lib(app, uyarilar, veri):
    l = Library()
    l.user_name("admin")
    return l


def test_yaklasan_teslimler(veri):
    assert [k[0] for k in odunc.yaklasan_teslimler()] == ["Yol Ayrımı", "Satranç"]
    assert odunc.yaklasan_teslimler()[0][3:] == (3, 1)


def test_eski_ana_sayfa_icerigi_yok(lib):
    q = lib
    assert not hasattr(q, "label") and not hasattr(q, "verticalLayoutWidget")
    assert q.btn_cikis.isVisibleTo(lib) and q.btn_cikis.text() == "Oturumu Kapat"
    assert q.btn_cikis.parentWidget() is lib.yan_menu.kart                    # Oturumu Kapat menüde
    a = lib.ana_sayfa
    assert a.hosgeldin.text() == ana_sayfa.selamlama() and a.karsilama.text() == "admin  ·  Yönetici"
    assert a.hosgeldin.alignment() & Qt.AlignHCenter
    assert not hasattr(a, "baslik_yazi")                         # "Yaşar Kütüphanesi" sadece menüde


def test_admin_kartlari(lib):
    assert kart(lib, "kitap") == ("8", "9 kopya, 6 rafta")
    assert kart(lib, "disarida") == ("3", "şu an ödünçte")
    assert kart(lib, "geciken") == ("1", "teslim süresi geçmiş")
    assert kart(lib, "uye") == ("3", "1 yönetici")


def test_kitap_karti_ayni_sayiyi_iki_kez_yazmaz():
    from acodes.library import kitap_karti_alti
    assert kitap_karti_alti(737, 737, 0) == "hepsi rafta"
    assert kitap_karti_alti(737, 737, 4) == "733 rafta"
    assert kitap_karti_alti(8, 9, 3) == "9 kopya, 6 rafta"


def test_admin_listeleri(lib):
    yak = lib.ana_sayfa.listeler["yaklasan"].tablo
    assert yak.rowCount() == 2
    assert [yak.item(0, c).text() for c in (0, 1, 3)] == ["Yol Ayrımı", "Ayşe Yılmaz", "5 gün gecikti"]
    assert yak.item(0, 0).background().color() == QColor(tema.GECIKME_ARKA)
    assert yak.item(1, 3).text() == "2 gün kaldı"
    son = lib.ana_sayfa.listeler["son"].tablo
    assert son.item(0, 0).text() == "Denemeler" and son.rowCount() == 8


def test_kart_ikonlari_ve_gecikme_rengi(lib):
    from acodes import tema
    k = lib.ana_sayfa.kartlar
    assert [k[a].ikon_adi for a in ("kitap", "disarida", "geciken", "uye")] == ["kitap", "takas", "saat", "kullanicilar"]
    assert not k["kitap"].ikon.pixmap().isNull()
    k["geciken"].ayarla(0, "", renk=tema.SOLUK)                   # gecikme yoksa sönük
    assert k["geciken"].ikon.renk == tema.SOLUK
    k["geciken"].ayarla(2, "")
    assert k["geciken"].ikon.renk == tema.TEHLIKE


def test_kart_tiklamalari(lib):
    q = lib
    lib.ana_sayfa.kartlar["geciken"].tiklandi.emit()
    assert q.sekmeler.currentWidget() is q.verme and q.alt_sekmeler[q.verme].currentWidget() is lib.odunc
    lib.ana_sayfa.kartlar["kitap"].tiklandi.emit()
    assert q.sekmeler.currentWidget() is q.liste and q.liste.tablo.rowCount() == 8
    lib.ana_sayfa.kartlar["uye"].tiklandi.emit()
    assert q.sekmeler.currentWidget() is lib.ayarlar


def test_liste_cift_tiklama(lib):
    q = lib
    lib.ana_sayfa.listeler["son"].tablo.cellDoubleClicked.emit(0, 0)
    assert q.alt_sekmeler[q.kayit].currentWidget() is lib.kitaplar and lib.kitaplar.alan["Adi"].text() == "Denemeler"
    lib.ana_sayfa.listeler["yaklasan"].tablo.cellDoubleClicked.emit(1, 0)
    assert q.alt_sekmeler[q.verme].currentWidget() is lib.odunc and "Satranç" in lib.odunc.iade_bilgi.text()


def test_ana_sayfa_guncellenir(lib, db):
    db.execute("UPDATE follow SET status='in' WHERE bookId='1'")
    db.commit()
    lib.sekmeler.setCurrentWidget(lib.liste)
    lib.sekmeler.setCurrentWidget(lib.ana_sayfa)
    assert kart(lib, "geciken")[0] == "0" and kart(lib, "disarida")[0] == "2"


def test_guest_panosu(app, veri):
    g = Guest()
    g.user_name("ayse1")
    assert g.ana_sayfa.karsilama.text() == "ayse1  ·  Üye"
    assert kart(g, "elimdeki") == ("2", "şu an sizde")
    assert kart(g, "geciken") == ("1", "teslim süresi geçmiş")
    assert kart(g, "teslim") == (odunc.tarih_yazi(BUGUN - datetime.timedelta(days=5)), "5 gün gecikti")
    liste = g.ana_sayfa.listeler["elimdeki"].tablo
    assert [liste.item(r, 0).text() for r in range(liste.rowCount())] == ["Yol Ayrımı", "Satranç"]  # en yakın teslim üstte
    g.ana_sayfa.kartlar["elimdeki"].tiklandi.emit()
    assert g.sekmeler.currentWidget() is g.kitaplarim


def test_kitabi_olmayan_uye_panosu(app, veri):
    g = Guest()
    g.user_name("eski")
    assert kart(g, "elimdeki")[0] == "0" and kart(g, "teslim") == ("-", "ödünç kitabınız yok")
    assert not g.ana_sayfa.listeler["elimdeki"].tablo.bos_durum.etiket.isHidden()
