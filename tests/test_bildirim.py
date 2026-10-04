## Kısa süreli bildirimler testleri ##
import datetime

import pytest
from PyQt5.QtTest import QTest

from acodes import bildirim
from acodes.guest import Guest
from acodes.library import Library


@pytest.mark.parametrize("metin,tur", [
    ("'Yeni Kitap' kaydedildi", "basari"), ("Yol Ayrımı güncellendi.", "basari"),
    ("İşlem kaydedildi. Teslim tarihi: 14.10.2026", "basari"),
    ("Seçim yapınız", "uyari"), ("Temizlenecek Veri Yok!", "uyari"),
    ("Teslim süresi (15 gün) geçmiş 2 kitap var.", "uyari"),
    ("Müsait kopya: 1 / 2", "bilgi"),
])
def test_tur_bul(metin, tur):
    assert bildirim.tur_bul(metin) == tur


def test_sure():
    assert bildirim.sure_ms("Tamam") == 2500
    assert bildirim.sure_ms("x" * 500) == 7000


@pytest.fixture
def lib(app, uyarilar):
    l = Library()
    l.resize(1200, 700)
    return l


def test_durum_cubugu_gizli_mesaj_bildirimde(lib):
    assert lib.QtLibrary.statusbar.isHidden()
    lib.QtLibrary.statusbar.showMessage("'Deneme' kaydedildi", 2000)
    kutu = lib.bildirim.kutu
    assert not kutu.isHidden() and kutu.text() == "'Deneme' kaydedildi" and lib.bildirim.tur == "basari"
    assert kutu.y() + kutu.height() <= lib.height()                     # pencerenin içinde, altta
    assert lib.QtLibrary.statusbar.currentMessage() == "'Deneme' kaydedildi"


def test_bildirim_kaybolur(lib):
    lib.QtLibrary.statusbar.showMessage("Seçim yapınız")
    lib.bildirim.kaybol()
    QTest.qWait(600)                                                    # solma animasyonu
    assert lib.bildirim.kutu.isHidden()


def test_bos_mesaj_gostermez(lib):
    lib.bildirim.kutu.hide()
    lib.QtLibrary.statusbar.clearMessage()
    assert lib.bildirim.kutu.isHidden()


def test_gercek_islemde_bildirim(lib):
    lib.kitaplar.alan["Adi"].setText("bildirim kitabı")
    lib.kitaplar.kaydet()
    assert lib.bildirim.kutu.text() == "'Bildirim Kitabı' kaydedildi" and lib.bildirim.tur == "basari"
    lib.odunc.odunc_ver()                                                # kitap ve üye seçilmeden
    assert lib.bildirim.kutu.text() == "Kitap ve üye seçiniz!" and lib.bildirim.tur == "uyari"


def test_geciken_kitap_acilista_uyari(app, uyarilar, db):
    eski = str(datetime.date.today() - datetime.timedelta(days=30))
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES ('3','1',?,'10:00','out','','')", (eski,))
    db.commit()
    l = Library()
    assert "geçmiş 1 kitap" in l.bildirim.kutu.text() and l.bildirim.tur == "uyari"


def test_guest_panelinde_de_bildirim(app):
    g = Guest()
    assert g.QtLibrary.statusbar.isHidden()
    g.QtLibrary.statusbar.showMessage("Liste görüntülendi.")
    assert g.bildirim.kutu.text() == "Liste görüntülendi."


def test_eylemli_bildirim_butonu_bir_kez_calisir(lib):
    cagri = []
    lib.bildirim.eylemli("'Deneme' silindi", "Geri Al", lambda: cagri.append(1))
    b = lib.bildirim
    assert b.kutu.text() == "'Deneme' silindi" and b.eylem.isVisibleTo(b.kutu) and b.eylem.text() == "Geri Al"
    assert lib.QtLibrary.statusbar.currentMessage() == "'Deneme' silindi"
    assert b.eylem.geometry().right() < b.kutu.width() and b.zamanlayici.remainingTime() > 6000
    b.eylem.click()
    assert cagri == [1] and not b.eylem.isVisibleTo(b.kutu)
    b.eylem.click()                                                     # ikinci tıklama bir şey yapmaz
    assert cagri == [1]


def test_yeni_mesaj_eylem_butonunu_kaldirir(lib):
    lib.bildirim.eylemli("'Deneme' silindi", "Geri Al", lambda: None)
    lib.QtLibrary.statusbar.showMessage("Liste görüntülendi.")
    assert not lib.bildirim.eylem.isVisibleTo(lib.bildirim.kutu) and lib.bildirim.eylem_islevi is None


def test_bildirim_sag_altta_kart(lib):
    lib.show()
    lib.QtLibrary.statusbar.showMessage("'Deneme' kaydedildi")
    k = lib.bildirim.kutu
    assert lib.width() - (k.x() + k.width()) == bildirim.KENAR_BOSLUK
    assert lib.height() - (k.y() + k.height()) == bildirim.KENAR_BOSLUK
    assert not lib.bildirim.simge.pixmap().isNull() and k.width() <= bildirim.EN_FAZLA_EN
    assert bildirim.renk("uyari") != bildirim.renk("basari")
    lib.close()



def test_tur_acikca_verilir(lib):
    lib.bildirim.mesaj("Liste görüntülendi!", "basari")                # metinden tahmin "uyari" olurdu
    assert lib.bildirim.tur == "basari" and lib.QtLibrary.statusbar.currentMessage() == "Liste görüntülendi!"
    lib.bildirim.mesaj("Kitap kaydedildi", "uyari")
    assert lib.bildirim.tur == "uyari"
    lib.bildirim.mesaj("Müsait kopya: 1 / 2")                           # tür verilmezse metinden
    assert lib.bildirim.tur == "bilgi"
    lib.QtLibrary.statusbar.showMessage("'Deneme' kaydedildi")         # sonraki mesaja tür taşınmaz
    assert lib.bildirim.tur == "basari"
    with pytest.raises(AssertionError):
        lib.bildirim.mesaj("x", "hata")


def test_panel_mesajlari_turuyle(lib):
    lib.kitaplar.alan["Adi"].setText("tür kitabı")
    lib.kitaplar.kaydet()
    assert lib.bildirim.tur == "basari"
    lib.filtre.temizle()
    assert lib.bildirim.tur in ("basari", "uyari")


def test_geri_al_suresi_cubukta_gorunur_ve_fare_ustundeyken_durur(lib):
    from PyQt5.QtCore import QEvent
    from PyQt5.QtWidgets import QApplication
    lib.show()
    b = lib.bildirim
    b.eylemli("'Deneme' silindi", "Geri Al", lambda: None)
    assert b.cubuk.isVisibleTo(b.kutu) and b.tur == "basari"
    tam = b.cubuk.width()
    assert tam > b.kutu.width() // 2 and b.cubuk.geometry().bottom() < b.kutu.height()
    QTest.qWait(400)
    assert b.cubuk.width() < tam                                        # kalan süreyle kısalır
    QApplication.sendEvent(b.kutu, QEvent(QEvent.Enter))
    assert not b.zamanlayici.isActive() and b.kalan_ms is not None
    durdu = b.cubuk.width()
    QTest.qWait(300)
    assert b.cubuk.width() == durdu
    QApplication.sendEvent(b.kutu, QEvent(QEvent.Leave))
    assert b.zamanlayici.isActive() and b.kalan_ms is None
    lib.QtLibrary.statusbar.showMessage("Liste görüntülendi.")          # eylemsiz bildirimde çubuk yok
    assert not b.cubuk.isVisibleTo(b.kutu)
    lib.close()


def test_acilista_gosterilen_bildirim_sag_altta(app, uyarilar, db):
    """Pencere görünmeden önce gelen bildirim (açılıştaki gecikme uyarısı) pencere açılınca sağ alttadır."""
    eski = str(datetime.date.today() - datetime.timedelta(days=30))
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES ('3','1',?,'10:00','out','','')", (eski,))
    db.commit()
    l = Library()
    l.resize(1200, 700)
    l.show()
    k = l.bildirim.kutu
    assert k.isVisible() and l.width() - (k.x() + k.width()) == bildirim.KENAR_BOSLUK
    assert l.height() - (k.y() + k.height()) == bildirim.KENAR_BOSLUK
    l.close()
