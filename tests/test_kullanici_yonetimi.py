## Kullanıcı yönetimi testleri ##
import pytest

from conftest import ADMIN_SIFRE, UYE_SIFRE
from acodes.guest import Guest
from acodes.kullanici_yonetimi import KullaniciDuzenle, KullaniciYonetimi, SifreDegistir
from acodes.library import Library
from database.kullanicilar import giris_kontrol


@pytest.fixture
def yonetim(app, uyarilar):
    return KullaniciYonetimi("admin")


def kayit(yonetim, kullanici):
    return next(k for k in yonetim.kayitlar if k.kullanici == kullanici)


def duzenle(yonetim, kullanici, aktif="admin", **alanlar):
    d = KullaniciDuzenle(kayit(yonetim, kullanici), aktif)
    for alan, deger in alanlar.items():
        if alan == "yetki":
            d.yetki.setCurrentText(deger)
        else:
            getattr(d, alan).setText(deger)
    d.kaydet()
    return d


def yetki(db, kullanici):
    return db.execute("SELECT yetki FROM users WHERE kullanici=?", (kullanici,)).fetchone()[0]


# --- Listeleme ---

def test_liste_sifre_gostermez(yonetim):
    assert yonetim.tablo.rowCount() == 4
    hucreler = [yonetim.tablo.item(r, c).text() for r in range(4) for c in range(5)]
    assert not any("pbkdf2$" in h for h in hucreler)
    assert [yonetim.tablo.horizontalHeaderItem(c).text() for c in range(5)] == KullaniciYonetimi.KOLONLAR


def test_secim_olmadan_butonlar_pasif(yonetim):
    assert not yonetim.btn_sil.isEnabled()
    yonetim.sec("ayse1")
    assert yonetim.btn_sil.isEnabled() and yonetim.secili().kullanici == "ayse1"


# --- Düzenleme ---

def test_bilgiler_guncellenir(yonetim, db):
    duzenle(yonetim, "ayse1", adi_soyadi="Ayşe Kaya", telefon="5559998877", mail="kaya@ornek.com")
    assert db.execute("SELECT adi_soyadi, telefon, mail FROM users WHERE kullanici='ayse1'").fetchone() == \
        ("Ayşe Kaya", "5559998877", "kaya@ornek.com")


@pytest.mark.parametrize("alanlar,mesaj", [
    ({"adi_soyadi": ""}, "Adı soyadı boş olamaz!"),
    ({"telefon": "123"}, "Telefon 10 haneli olmalıdır!"),
    ({"mail": "gecersiz"}, "Mail adresi geçerli değil!"),
])
def test_gecersiz_bilgi_kaydedilmez(yonetim, db, uyarilar, alanlar, mesaj):
    duzenle(yonetim, "ayse1", **alanlar)
    assert uyarilar[-1] == mesaj
    assert db.execute("SELECT adi_soyadi FROM users WHERE kullanici='ayse1'").fetchone()[0] == "Ayşe Yılmaz"


def test_bos_telefon_ve_mail_kabul_edilir(yonetim, db):
    duzenle(yonetim, "ayse1", telefon="", mail="")
    assert db.execute("SELECT telefon, mail FROM users WHERE kullanici='ayse1'").fetchone() == ("", "")


def test_yetki_yukseltilip_dusurulebilir(yonetim, db):
    duzenle(yonetim, "ayse1", yetki="admin")
    assert yetki(db, "ayse1") == "admin"
    yonetim.yukle()
    duzenle(yonetim, "admin", aktif="ayse1", yetki="guest")   # artık iki admin var
    assert yetki(db, "admin") == "guest"


def test_son_adminin_yetkisi_dusurulemez(yonetim, db, uyarilar):
    duzenle(yonetim, "admin", aktif="baska", yetki="guest")
    assert uyarilar[-1] == "Son admin kullanıcının yetkisi düşürülemez!"
    assert yetki(db, "admin") == "admin"


def test_kendi_yetkisini_degistiremez(yonetim):
    assert not KullaniciDuzenle(kayit(yonetim, "admin"), "admin").yetki.isEnabled()


# --- Silme ---

@pytest.mark.parametrize("kullanici,aktif,mesaj", [
    ("admin", "admin", "Kendi hesabınızı silemezsiniz!"),
    ("admin", "ayse1", "Son admin kullanıcı silinemez!"),
])
def test_silme_engelleri(app, uyarilar, db, kullanici, aktif, mesaj):
    y = KullaniciYonetimi(aktif)
    y.sec(kullanici)
    y.sil()
    assert uyarilar[-1] == mesaj
    assert db.execute("SELECT COUNT(*) FROM users WHERE kullanici=?", (kullanici,)).fetchone()[0] == 1


def test_elinde_kitap_olan_silinemez(yonetim, db, uyarilar):
    db.execute("INSERT INTO follow VALUES ('3','1','2026-01-01','10:00','out','','')")
    db.commit()
    yonetim.sec("ayse1")
    yonetim.sil()
    assert "iade edilmemiş 1 kitap" in uyarilar[-1]
    assert db.execute("SELECT COUNT(*) FROM users WHERE kullanici='ayse1'").fetchone()[0] == 1


def test_silme_gecmisi_korur(yonetim, db):
    db.execute("INSERT INTO follow VALUES ('3','1','2025-01-01','10:00','in','2025-01-10','10:00')")
    db.commit()
    yonetim.sec("ayse1")
    yonetim.sil()
    assert db.execute("SELECT COUNT(*) FROM users WHERE kullanici='ayse1'").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM follow").fetchone()[0] == 1
    assert yonetim.tablo.rowCount() == 3


# --- Şifre ---

def test_admin_sifre_sifirlar(app, uyarilar):
    d = SifreDegistir("ayse1")
    d.yeni.setText("yenisifre")
    d.tekrar.setText("yenisifre")
    d.kaydet()
    assert giris_kontrol("ayse1", "yenisifre") == "guest"
    assert giris_kontrol("ayse1", UYE_SIFRE) is None


@pytest.mark.parametrize("yeni,tekrar,mesaj", [
    ("kisa", "kisa", "Şifre en az 6 karakter olmalıdır!"),
    ("yenisifre", "baskasifre", "Şifreler birbiriyle aynı değil!"),
])
def test_gecersiz_sifre(app, uyarilar, yeni, tekrar, mesaj):
    d = SifreDegistir("ayse1")
    d.yeni.setText(yeni)
    d.tekrar.setText(tekrar)
    d.kaydet()
    assert uyarilar[-1] == mesaj
    assert giris_kontrol("ayse1", UYE_SIFRE) == "guest"


def test_kendi_sifresini_degistirirken_eskisi_sorulur(app, uyarilar):
    d = SifreDegistir("ayse1", eski_sor=True)
    d.eski.setText("yanlis")
    d.yeni.setText("yenisifre")
    d.tekrar.setText("yenisifre")
    d.kaydet()
    assert uyarilar[-1] == "Mevcut şifre yanlış!"
    d.eski.setText(UYE_SIFRE)
    d.kaydet()
    assert giris_kontrol("ayse1", "yenisifre") == "guest"


def test_yeni_kullanici_formu_kisa_sifreyi_reddeder(app, uyarilar, db):
    form = Library().user
    for alan, deger in [("kullanici_adi", "veli"), ("sifre", "123"), ("adi_soyadi", "Veli Can")]:
        getattr(form.QtUser, f"lineEdit_{alan}").setText(deger)
    form.QtUser.comboBox_yetki.setCurrentText("guest")
    form.save_user()
    assert uyarilar[-1] == "Şifre en az 6 karakter olmalıdır!"
    assert db.execute("SELECT COUNT(*) FROM users WHERE kullanici='veli'").fetchone()[0] == 0


# --- Panel butonları ---

def test_ayarlarda_kullanici_butonlari(app, uyarilar):
    lib = Library()
    for metin in ("Yeni Kullanıcı Ekle", "Kullanıcı Yönetimi", "Şifremi Değiştir"):
        assert lib.ayarlar.buton(metin).text() == metin
    g = Guest()
    g.user_name("ayse1")
    assert g.ayarlar.buton("Şifremi Değiştir") and g.aktif_kullanici == "ayse1"


def test_giriste_aktif_kullanici_kaydedilir(app):
    from acodes.login import Login
    w = Login()
    w.QtLogin.lineEdit_kullanci_adi.setText("admin")
    w.QtLogin.lineEdit_parola.setText(ADMIN_SIFRE)
    w.giris()
    assert w.library.aktif_kullanici == "admin"
