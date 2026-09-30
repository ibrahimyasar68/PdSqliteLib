## Oturum kapatma ve panel penceresi testleri ##
import pytest
from PyQt5.QtCore import Qt

from conftest import ADMIN_SIFRE, UYE_SIFRE
from acodes import login as login_modulu
from acodes.login import Login


def giris_yap(w, kullanici, sifre):
    w.QtLogin.lineEdit_kullanci_adi.setText(kullanici)
    w.QtLogin.lineEdit_parola.setText(sifre)
    w.giris()


@pytest.fixture
def w(app):
    pencere = Login()
    pencere.show()
    return pencere


def test_giriste_giris_ekrani_gizlenir(w):
    giris_yap(w, "admin", ADMIN_SIFRE)
    assert w.library.isVisible() and not w.isVisible()


def test_oturumu_kapat_giris_ekranina_doner(w):
    giris_yap(w, "admin", ADMIN_SIFRE)
    panel = w.library
    assert panel.QtLibrary.pushButton_1_cikis.text() == "Oturumu Kapat"
    panel.QtLibrary.pushButton_1_cikis.click()
    assert not panel.isVisible() and w.isVisible()
    assert w.library is None
    assert w.QtLogin.lineEdit_kullanci_adi.text() == "" and w.QtLogin.lineEdit_parola.text() == ""
    assert w.mesaj.text() == "Oturum kapatıldı."


def test_oturum_kapatip_baska_kullaniciyla_girilir(w):
    giris_yap(w, "admin", ADMIN_SIFRE)
    w.library.oturumu_kapat()
    giris_yap(w, "ayse1", UYE_SIFRE)
    assert w.guest.isVisible() and w.guest.aktif_kullanici == "ayse1"
    assert w.guest.QtLibrary.pushButton_1_cikis.text() == "Oturumu Kapat"
    w.guest.oturumu_kapat()
    assert w.isVisible() and w.guest is None
    giris_yap(w, "admin", ADMIN_SIFRE)
    assert w.library.aktif_kullanici == "admin"


def test_her_oturumda_yeni_panel(w):
    giris_yap(w, "admin", ADMIN_SIFRE)
    ilk = w.library
    ilk.oturumu_kapat()
    giris_yap(w, "admin", ADMIN_SIFRE)
    assert w.library is not ilk


def test_oturum_kapaninca_yeni_kullanici_formu_kapanir(w):
    giris_yap(w, "admin", ADMIN_SIFRE)
    form = w.library.user
    w.library.ayarlar.buton("Yeni Kullanıcı Ekle").click()
    assert form.isVisible()
    w.library.oturumu_kapat()
    assert not form.isVisible()


def test_parolada_enter_ile_giris(w):
    w.QtLogin.lineEdit_kullanci_adi.setText("admin")
    w.QtLogin.lineEdit_parola.setText(ADMIN_SIFRE)
    w.QtLogin.lineEdit_parola.returnPressed.emit()
    assert w.library is not None and w.library.isVisible()


@pytest.mark.parametrize("platform,durum", [("darwin", Qt.WindowMaximized), ("win32", Qt.WindowFullScreen)])
def test_panel_penceresi_platforma_gore(w, monkeypatch, platform, durum):
    monkeypatch.setattr(login_modulu.sys, "platform", platform)
    giris_yap(w, "admin", ADMIN_SIFRE)
    assert w.library.windowState() & durum


def test_pencere_basliklari(w):
    assert w.windowTitle() == "Yaşar Kütüphanesi - Giriş"
    giris_yap(w, "admin", ADMIN_SIFRE)
    assert w.library.windowTitle() == "Yaşar Kütüphanesi - Yönetici Paneli - admin"
    w.library.oturumu_kapat()
    giris_yap(w, "ayse1", UYE_SIFRE)
    assert w.guest.windowTitle() == "Yaşar Kütüphanesi - Üye Paneli - ayse1"


def test_cikis_butonu_ikonu(w):
    from PyQt5.QtCore import QFile
    buton = w.QtLogin.pushButton_cikis
    assert QFile(":/pic/guc.png").exists()          # ikon programın içinde, dışarıdaki dosyaya bağlı değil
    assert not buton.icon().isNull() and buton.icon().availableSizes()
    assert buton.toolTip() == "Programdan çık"


# --- Giriş ekranı tasarımı ---

def test_giris_karti(w):
    ui = w.QtLogin
    assert ui.formFrame.isHidden() and ui.statusbar.isHidden()
    kart = w.findChild(type(ui.widget), "giris_karti")
    assert ui.lineEdit_kullanci_adi.parent() is kart and ui.pushButton_giris.parent() is kart
    assert ui.lineEdit_kullanci_adi.placeholderText() == "Kullanıcı adınız"


def test_parola_goster_gizle(w):
    from PyQt5.QtWidgets import QLineEdit
    alan = w.QtLogin.lineEdit_parola
    assert alan.echoMode() == QLineEdit.Password
    w.goster.trigger()
    assert alan.echoMode() == QLineEdit.Normal and w.goster.text() == "Parolayı gizle"
    w.goster.trigger()
    assert alan.echoMode() == QLineEdit.Password


def test_mesajlar_kartta(w):
    w.giris()
    assert w.mesaj.text() == "Kullanıcı adı ve parola bilgilerini giriniz!" and w.mesaj.property("tur") == "hata"
    giris_yap(w, "admin", "yanlis")
    assert w.QtLogin.lineEdit_parola.selectedText() == "yanlis"      # tekrar yazmak için seçili
    giris_yap(w, "admin", ADMIN_SIFRE)
    assert w.mesaj.text() == ""
    w.library.oturumu_kapat()
    assert w.mesaj.property("tur") == "bilgi"
