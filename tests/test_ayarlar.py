## Ayarlar sekmesi ve sadeleştirilmiş ana sayfa testleri ##
import pytest
from PyQt5.QtGui import QDesktopServices

from acodes import ayarlar as ayarlar_modulu
from acodes import kullanici_yonetimi
from acodes.guest import Guest
from acodes.library import Library
from database import yedek


def sekmeler(panel):
    t = panel.QtLibrary.tabWidget
    return [t.tabText(i) for i in range(t.count())]


def gorunen_butonlar(panel):
    sayfa = panel.QtLibrary.tab_1
    return [b.text() for b in sayfa.findChildren(type(panel.QtLibrary.pushButton_1_cikis)) if b.isVisibleTo(panel)]


@pytest.fixture
def lib(app, uyarilar):
    return Library()


def test_ana_sayfada_sadece_oturumu_kapat(lib, app):
    assert gorunen_butonlar(lib) == ["Oturumu Kapat"]
    g = Guest()
    assert gorunen_butonlar(g) == ["Oturumu Kapat"]


def test_ayarlar_son_sekme(lib, app):
    assert sekmeler(lib)[-1] == "Ayarlar"
    assert sekmeler(Guest())[-2:] == ["Kitaplarım", "Ayarlar"]


def test_admin_ayarlar_bolumleri(lib):
    assert [b.title() for b in lib.ayarlar.bolumler] == ["Kullanıcılar", "Yedekleme", "Kütüphane Bilgileri"]
    for metin in ("Yeni Kullanıcı Ekle", "Kullanıcı Yönetimi", "Şifremi Değiştir",
                  "Yedek Al", "Yedekten Geri Yükle", "Yedek Klasörünü Aç"):
        assert lib.ayarlar.buton(metin).toolTip()


def test_butonlar_ilgili_islemi_acar(lib, monkeypatch):
    acilan = []
    monkeypatch.setattr(kullanici_yonetimi.KullaniciYonetimi, "exec_", lambda self: acilan.append("yonetim"))
    monkeypatch.setattr(kullanici_yonetimi.SifreDegistir, "exec_",
                        lambda self: acilan.append(("sifre", self.kullanici, self.eski is not None)))
    lib.user_name("admin")
    lib.ayarlar.buton("Kullanıcı Yönetimi").click()
    lib.ayarlar.buton("Şifremi Değiştir").click()
    lib.ayarlar.buton("Yeni Kullanıcı Ekle").click()
    assert acilan == ["yonetim", ("sifre", "admin", True)]   # kendi şifresi: mevcut şifre sorulur
    assert lib.user.isVisible()


def test_yedek_klasorunu_ac(lib, monkeypatch):
    acilan = []
    monkeypatch.setattr(QDesktopServices, "openUrl", staticmethod(lambda url: acilan.append(url.toLocalFile())))
    lib.ayarlar.buton("Yedek Klasörünü Aç").click()
    assert acilan == [yedek.yedek_klasoru()]


def bilgiler(bolum):
    form = bolum.form
    return {form.itemAt(i, form.LabelRole).widget().text(): form.itemAt(i, form.FieldRole).widget().text()
            for i in range(form.rowCount())}


def test_kutuphane_bilgileri(lib, db):
    db.execute("UPDATE kayitlistesi SET Kopya=3 WHERE Id=1")
    db.execute("INSERT INTO follow VALUES ('3','1','2026-01-01','10:00','out','','')")
    db.commit()
    lib.ayarlar.yenile()
    b = bilgiler(lib.ayarlar.bolumler[2])
    assert b["Kitap:"] == "8 kayıt, 10 kopya"
    assert b["Kullanıcı:"] == "3 üye, 1 yönetici"
    assert b["Ödünç:"] == "1 kitap dışarıda, toplam 1 işlem"
    assert b["Veritabanı:"].endswith("test.db")


def test_yedek_bilgisi(lib):
    import shutil
    shutil.rmtree(yedek.yedek_klasoru(), ignore_errors=True)
    lib.ayarlar.yenile()
    assert bilgiler(lib.ayarlar.bolumler[1])["Son otomatik yedek:"] == "Henüz alınmadı"
    yedek.otomatik_yedek()
    lib.ayarlar.yenile()
    b = bilgiler(lib.ayarlar.bolumler[1])
    assert b["Son otomatik yedek:"] != "Henüz alınmadı" and b["Saklanan otomatik yedek:"].startswith("1 ")
    shutil.rmtree(yedek.yedek_klasoru(), ignore_errors=True)


def test_guest_hesabim(app):
    g = Guest()
    g.user_name("ayse1")
    assert [b.title() for b in g.ayarlar.bolumler] == ["Hesabım"]
    assert bilgiler(g.ayarlar.bolumler[0]) == {"Kullanıcı adı:": "ayse1", "Adı soyadı:": "Ayşe Yılmaz",
                                               "Telefon:": "5551112233", "Mail:": "ayse@ornek.com"}


def test_sekme_degisince_bilgiler_yenilenir(lib, db):
    lib.ayarlar.yenile()
    db.execute("DELETE FROM kayitlistesi WHERE Id>4")
    db.commit()
    lib.QtLibrary.tabWidget.setCurrentWidget(lib.ayarlar)
    assert bilgiler(lib.ayarlar.bolumler[2])["Kitap:"] == "4 kayıt, 4 kopya"


def test_klasoru_ac_yoksa_olusturur(tmp_path, monkeypatch):
    monkeypatch.setattr(QDesktopServices, "openUrl", staticmethod(lambda url: None))
    hedef = tmp_path / "yeni" / "klasor"
    ayarlar_modulu.klasoru_ac(str(hedef))
    assert hedef.is_dir()
