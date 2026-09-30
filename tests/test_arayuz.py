## Arayüz (acodes/) testleri ##
# Pencereler ekranda açılmaz; butonlara basmak yerine aynı fonksiyonlar çağrılır.
import pytest

from conftest import ADMIN_SIFRE, UYE_SIFRE, sec
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


# --- Filtre ve istatistik (Tab 4, 5) ---

def test_filtre_coklu_secim_ve_temizleme(lib):
    q = lib.QtLibrary
    sec(q.comboBox_4_1_turu, "Roman")
    sec(q.comboBox_4_1_turu, "Deneme")
    lib.filtre_listele(1, "Turu")
    assert lib.filtre_secimleri[1] == ["Deneme", "Roman"]
    assert q.tableWidget_4_1_2.rowCount() == 7
    lib.filtre_temizle(1, "Seçilen Tür")
    assert lib.filtre_secimleri[1] == [] and q.tableWidget_4_1_2.rowCount() == 1


def test_tirnakli_yazara_gore_filtre(lib):
    sec(lib.QtLibrary.comboBox_4_2_turu, "O'brien")
    lib.filtre_listele(2, "Yazari")
    t = lib.QtLibrary.tableWidget_4_2_2
    assert t.rowCount() == 1 and t.item(0, 1).text() == "Anne'nin Günlüğü"


def test_az_turle_istatistik_ekrani_acilir(app, uyarilar):
    # 35'ten az tür varken eskiden çöküyordu
    assert Library().QtLibrary.tableWidget_5_1_1.rowCount() == 3
    assert Guest().QtLibrary.tableWidget_5_1_1.rowCount() == 3


# --- Ödünç verme ve iade (Tab 6) ---

def test_ayni_isimli_uyeden_dogru_kisiye_odunc(lib, db):
    q = lib.QtLibrary
    q.comboBox_6_1_1_liste_kitap.setCurrentText("Yol Ayrımı")
    lib.find_item_6_1_1()
    q.comboBox_6_1_2_liste_kisi.setCurrentIndex(q.comboBox_6_1_2_liste_kisi.findData(4))
    lib.find_user_6_1_2()
    lib.save_work()
    assert db.execute("SELECT userId FROM follow WHERE status='out'").fetchall() == [("4",)]
    assert q.comboBox_6_2_1_liste_kisi.findData(4) > 0   # iade listesi hemen yenilendi


def test_kisi_listesinde_kullanici_adi_gorunur(lib):
    assert "Ayşe Yılmaz (ayse2)" in etiketler(lib.QtLibrary.comboBox_6_1_2_liste_kisi)


def test_oduncteki_kitap_tekrar_verilemez(lib, db, uyarilar):
    db.execute("INSERT INTO follow VALUES ('3','1','2026-01-01','10:00','out','','')")
    db.commit()
    lib.QtLibrary.comboBox_6_1_1_liste_kitap.setCurrentText("Yol Ayrımı")
    lib.find_item_6_1_1()
    assert uyarilar[-1] == "Bu kitap başka bir üyededir!"


def test_panel_bayraklari_ayri(lib):
    q = lib.QtLibrary
    q.comboBox_6_1_2_liste_kisi.setCurrentIndex(1)
    lib.find_user_6_1_2()
    assert not q.pushButton_6_2_islemi_kaydet.isEnabled()


def test_iade_alma(lib, db):
    q = lib.QtLibrary
    db.execute("INSERT INTO follow VALUES ('3','1','2026-01-01','10:00','out','','')")
    db.commit()
    lib.list_user_6_2_1()
    q.comboBox_6_2_1_liste_kisi.setCurrentIndex(q.comboBox_6_2_1_liste_kisi.findData(3))
    lib.find_user_6_2_1()
    q.comboBox_6_2_2_liste_kitap.setCurrentIndex(1)
    lib.find_item_6_2_2()
    lib.save_work2()
    assert db.execute("SELECT status FROM follow").fetchone()[0] == "in"


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
    assert "Veli Can (veli)" in etiketler(lib.QtLibrary.comboBox_6_1_2_liste_kisi)
