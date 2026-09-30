## Arayüz (acodes/) testleri ##
# Pencereler ekranda açılmaz; butonlara basmak yerine aynı fonksiyonlar çağrılır.
import pytest

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
    assert Login().QtLogin.pushButton_yeni_kayit.isHidden()


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
    assert Library().QtLibrary.tableWidget_5_1_1.rowCount() == 3
    assert Guest().QtLibrary.tableWidget_5_1_1.rowCount() == 3


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
    lib.QtLibrary.tabWidget.setCurrentIndex(5)
    assert "Veli Can (veli)" in etiketler(lib.odunc.uye)
