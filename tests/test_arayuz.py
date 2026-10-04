## Arayüz (acodes/) testleri ##
# Pencereler ekranda açılmaz; butonlara basmak yerine aynı fonksiyonlar çağrılır.
import pytest
from PyQt5.QtCore import Qt

from conftest import ADMIN_SIFRE, UYE_SIFRE
from acodes.guest import Guest
from acodes.kitap_ekrani import buyuk_harf
from acodes.library import Library
from acodes.login import Login


def etiketler(cmb):
    return [cmb.itemText(i) for i in range(cmb.count())]


@pytest.fixture
def lib(app, uyarilar):
    return Library()


def giris_yap(kullanici, sifre):
    w = Login()
    w.QtLogin.lineEdit_kullanci_adi.setText(kullanici)
    w.QtLogin.lineEdit_parola.setText(sifre)
    w.giris()
    return w


# --- Giriş ---

def test_giris_yanlis_bilgide_tek_mesaj(app):
    for kullanici, sifre in (("admin", "yanlis"), ("olmayan", ADMIN_SIFRE)):
        w = giris_yap(kullanici, sifre)
        assert w.mesaj.text() == "Kullanıcı adı veya parola yanlış!"
        assert w.library is None and w.guest is None


def test_admin_ve_guest_dogru_paneli_acar(app):
    assert giris_yap("admin", ADMIN_SIFRE).library.isVisible()
    assert giris_yap("ayse1", UYE_SIFRE).guest.isVisible()


def test_giris_ekraninda_yeni_kayit_butonu_yok(app):
    assert not hasattr(Login().QtLogin, "pushButton_yeni_kayit")


# --- Yardımcılar ---

@pytest.mark.parametrize("girdi,beklenen", [
    ("anne'nin günlüğü", "Anne'nin Günlüğü"),
    ("Kemal TAHİR", "Kemal TAHİR"),
    ("istanbul ışık", "İstanbul Işık"),
])
def test_buyuk_harf(girdi, beklenen):
    assert buyuk_harf(girdi) == beklenen


# --- İstatistik (Tab 5) ---

def test_az_turle_istatistik_ekrani_acilir(app, uyarilar):
    # 35'ten az tür varken eskiden çöküyordu
    assert Library().istatistik.tablolar[0].rowCount() == 3
    assert Guest().istatistik.tablolar[0].rowCount() == 3


# --- Yeni kullanıcı formu ---

@pytest.fixture
def form(lib):
    return lib.user


def formu_doldur(form, **alanlar):
    for alan, deger in alanlar.items():
        getattr(form.QtUser, f"lineEdit_{alan}").setText(deger)


def test_yetki_listesi(form):
    assert etiketler(form.QtUser.comboBox_yetki) == ["Yetki Seçin...", "admin", "guest"]


def test_zorunlu_alan_eksikse_kaydedilmez(form, db, uyarilar):
    formu_doldur(form, kullanici_adi="veli", sifre="", adi_soyadi="Veli Can")
    form.QtUser.comboBox_yetki.setCurrentText("guest")
    form.save_user()
    assert db.execute("SELECT COUNT(*) FROM users WHERE kullanici='veli'").fetchone()[0] == 0
    assert "boş olamaz" in uyarilar[-1]


@pytest.mark.parametrize("mail,gecerli", [
    ("ali.veli@ornek.com.tr", True), ("a-b+c@alt-alan.org", True), ("abc", False), ("a@b", False),
])
def test_mail_kontrolu(form, mail, gecerli):
    form.QtUser.lineEdit_mail.setText(mail)
    form.chk_mail()
    assert (form.QtUser.lineEdit_mail.text() == mail) == gecerli


def test_baska_kullanicinin_sifresi_sizdirilmaz(form):
    formu_doldur(form, kullanici_adi="yeni", sifre=UYE_SIFRE)
    form.chk_sifre()
    assert form.QtUser.lineEdit_sifre.text() == UYE_SIFRE


def test_yeni_uye_sekme_degisince_odunc_listesinde(lib, form):
    formu_doldur(form, kullanici_adi="veli", sifre="gizli123", adi_soyadi="Veli Can",
                 telefon="5551234567", mail="veli@ornek.com")
    form.QtUser.comboBox_yetki.setCurrentText("guest")
    form.save_user()
    lib.sekmeler.setCurrentIndex(5)
    assert "Veli Can (veli)" in etiketler(lib.odunc.uye)


def test_yeni_kullanici_penceresi_temada(form):
    ui = form.QtUser
    assert ui.pushButton_kaydet.property("rol") is None and ui.pushButton_cikis.property("rol") == "ikincil"
    assert not ui.pushButton_kaydet.icon().isNull()
    form.mesaj_goster("Deneme mesajı", 3000)
    assert form.mesaj.text() == "Deneme mesajı"                                        # mesaj formun içinde


def test_yeni_uye_kaydindan_sonra_kalinan_menuye_donulur(lib, form, db):
    q = lib
    q.sekmeler.setCurrentWidget(lib.ayarlar)
    lib.ayarlar.buton("Yeni Kullanıcı Ekle").click()
    assert form.isVisible() and form.parentWidget() is lib            # panele bağlı açılır (ayrı pencere değil)
    assert form.isWindow() and form.windowModality() == Qt.WindowModal
    formu_doldur(form, kullanici_adi="veli", sifre="gizli123", adi_soyadi="Veli Can",
                 telefon="5551234567", mail="veli@ornek.com")
    form.QtUser.comboBox_yetki.setCurrentText("guest")
    form.save_user()
    assert db.execute("SELECT COUNT(*) FROM users WHERE kullanici='veli'").fetchone()[0] == 1
    assert not form.isVisible()                                         # form kapandı
    assert q.sekmeler.currentWidget() is lib.ayarlar                   # aynı menüde kalındı
    assert q.statusBar().currentMessage() == "'veli' kullanıcısı kaydedildi."
    assert "Veli Can (veli)" in etiketler(lib.odunc.uye)                 # listeler hemen yenilendi
    assert form.QtUser.lineEdit_kullanici_adi.text() == ""


def test_onay_kutusu_acik_pencereye_baglanir(app, monkeypatch):
    from PyQt5.QtWidgets import QMessageBox, QWidget
    from acodes import onay as onay_modulu
    ebeveynler = []
    monkeypatch.setattr(QMessageBox, "exec_", lambda self: ebeveynler.append(self.parentWidget()) or QMessageBox.Yes)
    w = QWidget()
    assert onay_modulu.onay("Emin misiniz?", w) == QMessageBox.Yes and ebeveynler == [w]


def test_istege_bagli_alanlar_bos_birakilinca_uyarmaz(form, uyarilar):
    form.chk_telefon()
    form.chk_mail()
    assert uyarilar == []


def test_hatali_telefon_veya_mail_ile_kaydedilmez(form, db, uyarilar):
    formu_doldur(form, kullanici_adi="veli", sifre="gizli123", adi_soyadi="Veli Can", telefon="123")
    form.QtUser.comboBox_yetki.setCurrentText("guest")
    form.save_user()
    assert db.execute("SELECT COUNT(*) FROM users WHERE kullanici='veli'").fetchone()[0] == 0
    assert "telefon" in uyarilar[-1]


def test_kisa_sifre_formda_hemen_bildirilir(form, uyarilar):
    formu_doldur(form, kullanici_adi="veli", sifre="abc")
    form.chk_sifre()
    assert "en az 6" in form.mesaj.text() and uyarilar == []


def test_silinmis_kitap_duzenlenmek_istenince_mesaj(lib, db):
    db.execute("DELETE FROM kayitlistesi WHERE Id=6")
    db.commit()
    lib.kitap_duzenle(6)
    assert lib.statusBar().currentMessage() == "Kitap bulunamadı (silinmiş olabilir)."


def test_ui_dosyalarinda_renk_ve_yazi_tipi_yok(app):
    # Görünüm tamamen temadan gelir: .ui'dan gelen bileşenlerde (yalnızca giriş ekranı kaldı) renk veya yazı tipi
    # bulunmamalı (giriş fotoğrafının border-image ve köşe yuvarlaklığı serbest).
    import re
    from PyQt5.QtWidgets import QMainWindow, QWidget
    from bforms.login_py import Ui_MainWindow
    w = QMainWindow()
    Ui_MainWindow().setupUi(w)
    stiller = {b.objectName(): b.styleSheet() for b in w.findChildren(QWidget) if b.styleSheet()}
    yasak = re.compile(r"(^|[;{\s])(color|background(-color)?|font(-[a-z]+)?)\s*:")
    assert [ad for ad, stil in stiller.items() if yasak.search(stil)] == []
