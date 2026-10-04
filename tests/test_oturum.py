## Oturum kapatma ve panel penceresi testleri ##
import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QApplication

from conftest import ADMIN_SIFRE, UYE_SIFRE
from acodes import login as login_modulu
from acodes.guest import Guest
from acodes.library import Library
from acodes.login import Login
from database.modeller import Kitap
from servis import kitap as kitap_servisi


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
    assert panel.btn_cikis.text() == "Oturumu Kapat"
    panel.btn_cikis.click()
    assert not panel.isVisible() and w.isVisible()
    assert w.library is None
    assert w.QtLogin.lineEdit_kullanci_adi.text() == "" and w.QtLogin.lineEdit_parola.text() == ""
    assert w.mesaj.text() == "Oturum kapatıldı."


def test_oturum_kapatip_baska_kullaniciyla_girilir(w):
    giris_yap(w, "admin", ADMIN_SIFRE)
    w.library.oturumu_kapat()
    giris_yap(w, "ayse1", UYE_SIFRE)
    assert w.guest.isVisible() and w.guest.aktif_kullanici == "ayse1"
    assert w.guest.btn_cikis.text() == "Oturumu Kapat"
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
    buton = w.QtLogin.pushButton_cikis              # ikon Qt ile çizilir, dosyaya bağlı değil
    assert not buton.icon().isNull() and buton.icon().availableSizes()
    assert buton.toolTip() == "Programdan çık"


# --- Giriş ekranı tasarımı ---

def test_giris_karti(w):
    ui = w.QtLogin
    assert not hasattr(ui, "formFrame") and ui.statusbar.isHidden()
    kart = w.findChild(type(ui.widget), "giris_karti")
    assert ui.lineEdit_kullanci_adi.parent() is kart and ui.pushButton_giris.parent() is kart
    assert ui.lineEdit_kullanci_adi.placeholderText() == "Kullanıcı adınız"


def test_parola_goster_gizle(w):
    from PySide6.QtWidgets import QLineEdit
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


def test_acilista_kullanici_adi_odakta(app):
    from acodes.login import Login
    w = Login()
    w.show()
    app.processEvents()
    assert w.focusWidget() is w.QtLogin.lineEdit_kullanci_adi


def test_caps_lock_uyarisi(w, monkeypatch):
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QFocusEvent
    from PySide6.QtWidgets import QApplication
    alan = w.QtLogin.lineEdit_parola
    monkeypatch.setattr(login_modulu, "caps_lock_acik", lambda: True)
    QApplication.sendEvent(alan, QFocusEvent(QEvent.FocusIn))
    assert not w.caps.isHidden() and w.caps.text() == "Caps Lock açık"
    monkeypatch.setattr(login_modulu, "caps_lock_acik", lambda: False)
    QApplication.sendEvent(alan, QFocusEvent(QEvent.FocusIn))
    assert w.caps.isHidden()
    monkeypatch.setattr(login_modulu, "caps_lock_acik", lambda: True)
    QApplication.sendEvent(alan, QFocusEvent(QEvent.FocusIn))
    QApplication.sendEvent(alan, QFocusEvent(QEvent.FocusOut))      # başka alana geçince kaybolur
    assert w.caps.isHidden()


def test_caps_lock_sistemden_okunur():
    assert isinstance(login_modulu.caps_lock_acik(), bool)          # hata vermez; bilinemezse False


def test_giris_surerken_buton_bekler(w, monkeypatch):
    durum = []
    gercek = login_modulu.giris_kontrol

    def kontrol(ad, sifre):
        b = w.QtLogin.pushButton_giris
        durum.append((b.isEnabled(), b.text()))
        return gercek(ad, sifre)

    monkeypatch.setattr(login_modulu, "giris_kontrol", kontrol)
    giris_yap(w, "admin", "yanlis")
    assert durum == [(False, "Giriş yapılıyor…")]
    assert w.QtLogin.pushButton_giris.isEnabled() and w.QtLogin.pushButton_giris.text() == "Giriş"


def test_giris_ekrani_yerlesimi(w):
    from PySide6.QtCore import QPoint
    ui = w.QtLogin
    panel = w.findChild(type(ui.widget), "giris_paneli")
    cikis = ui.pushButton_cikis
    assert cikis.parent() is panel and cikis.size().width() == 32
    sag_ust = cikis.mapTo(panel, QPoint(cikis.width(), 0))
    assert panel.width() - sag_ust.x() < 20 and sag_ust.y() < 20               # panelin sağ üst köşesinde
    kart = w.findChild(type(ui.widget), "giris_karti")
    orta = kart.mapTo(panel, QPoint(kart.width() // 2, 0)).x()
    assert abs(orta - panel.width() // 2) <= 12                                 # kart panelde ortalı (iç paylar hariç)


@pytest.mark.parametrize("panel", [Library, Guest])
def test_silinen_panelden_sonra_olaylar_cokmez(app, uyarilar, panel):
    # Oturum kapatılınca panel silinir; ertelenmiş işler (boş tablo mesajı, kolon yerleşimi) ve kayıt değişikliği
    # sinyalleri silinmiş tablolara dokunmamalı (PySide6'da bağlamsız QTimer.singleShot buna yol açıyordu)
    p = panel()
    p.user_name("admin")
    p.show()
    QApplication.processEvents()
    p.close()
    p.deleteLater()
    QApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    QApplication.processEvents()
    kitap_servisi.kaydet(Kitap("Sonradan Eklenen"))      # olaylar.kitaplar artık silinmiş ekranlara gitmez
    QApplication.processEvents()
