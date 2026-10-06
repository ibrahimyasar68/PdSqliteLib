## Test ortamı ##
# Testler gerçek veritabanına dokunmaz: her oturumda geçici bir veritabanı oluşturulur
# ve her testten önce örnek verilerle sıfırlanır. Pencereler ekranda açılmaz (offscreen).

import os
import sys
import tempfile

# Bu ayarlar database/ ve PySide6 import edilmeden önce yapılmalı
_gecici = tempfile.mkdtemp(prefix="pdsqlitelib_test_")
os.environ["PDSQLITE_DB"] = os.path.join(_gecici, "test.db")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pytest  # noqa: E402
from PySide6.QtCore import QEvent  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from database.baglanti import baglantı  # noqa: E402
from database.kullanicilar import sifre_hashle  # noqa: E402
from acodes import hareket  # noqa: E402

hareket.ANIMASYON = False       # sayfa geçişleri ve menü genişliği testlerde hemen sonuçlansın

ADMIN_SIFRE = "admin123"
ESKI_SIFRE = "eski123"      # Veritabanında düz metin duran eski kullanıcı
UYE_SIFRE = "uye12345"
# Hash'ler oturumda bir kez hesaplanır (her biri ~0,1 sn; her testte yeniden hesaplamak süreyi ikiye katlıyordu)
ADMIN_HASH = sifre_hashle(ADMIN_SIFRE)
UYE_HASH = sifre_hashle(UYE_SIFRE)

KITAPLAR = [
    (1, "Yol Ayrımı", "Kemal TAHİR", "", "Roman", "İthaki Yayınları", "2005", "493"),
    (2, "Esir Şehrin İnsanları", "Kemal TAHİR", "", "Roman", "İthaki Yayınları", "2005", "463"),
    (3, "İklimler", "Andre MAUROIS", "Tahsin YÜCEL", "Roman", "Görsel Yayınlar", "1992", "32"),
    (4, "İklimler", "Andre MAUROIS", "", "Roman", "Şaheser Romanlar", "1985", "280"),
    (5, "Anne'nin Günlüğü", "O'brien", "", "Anı", "D'Arte", "2020", "10"),
    (6, "Satranç", "Stefan ZWEIG", "Ahmet CEMAL", "Roman", "İş Bankası Yayınları", "2018", "83"),
    (7, "Kuyucaklı Yusuf", "Sabahattin ALİ", "", "Roman", "YKY", "", "220"),
    (8, "Denemeler", "MONTAIGNE", "", "Deneme", "Cem Yayınevi", "1983", "553"),
]


def ornek_veri_yukle():
    baglantı.executescript("DELETE FROM follow; DELETE FROM users; DELETE FROM kayitlistesi; DELETE FROM duzeltme_yoksay;"
                           "DELETE FROM sqlite_sequence;")
    baglantı.executemany("INSERT INTO kayitlistesi (Id,Adi,Yazari,Ceviren,Turu,Yayinevi,Yili,Sayfa)"
                         " VALUES (?,?,?,?,?,?,?,?)", KITAPLAR)
    baglantı.executemany(
        "INSERT INTO users (id,kullanici,sifre,adi_soyadi,telefon,mail,yetki) VALUES (?,?,?,?,?,?,?)", [
            (1, "admin", ADMIN_HASH, "Yönetici", "", "", "admin"),
            (2, "eski", ESKI_SIFRE, "Eski Kullanıcı", "", "", "guest"),
            (3, "ayse1", UYE_HASH, "Ayşe Yılmaz", "5551112233", "ayse@ornek.com", "guest"),
            (4, "ayse2", UYE_HASH, "Ayşe Yılmaz", "5550000000", "a2@ornek.com", "guest"),
        ])
    baglantı.commit()


def sec(cmb, metin):
    """Açılır listede bir seçeneği kullanıcı gibi listeden seçer."""
    i = cmb.findText(metin)
    assert i >= 0, f"{metin!r} listede yok"
    cmb.setCurrentIndex(i)


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def db():
    ornek_veri_yukle()
    return baglantı


@pytest.fixture(autouse=True)
def pencereleri_temizle():
    """Her testten sonra açık kalan pencereler silinir (programda oturum kapatılınca panel de silinir).
    Silinmeyen paneller kayıt değişikliği sinyallerine bağlı kaldığı için sonraki testlerde boşuna yenileniyordu."""
    yield
    uygulama = QApplication.instance()
    if uygulama is None:
        return
    for pencere in uygulama.topLevelWidgets():
        pencere.close()
        pencere.deleteLater()
    QApplication.sendPostedEvents(None, QEvent.DeferredDelete)


@pytest.fixture
def uyarilar(monkeypatch):
    """Onay kutularına otomatik "Evet" der, bilgi mesajlarını listede toplar (pencere açılmaz)."""
    import acodes.kitap_ekrani
    import acodes.odunc_ekrani
    import acodes.kullanici_yonetimi
    import acodes.library
    import acodes.user
    import acodes.veri_duzeltme
    mesajlar = []
    for modul in (acodes.library, acodes.user, acodes.kullanici_yonetimi, acodes.veri_duzeltme,
                  acodes.kitap_ekrani, acodes.odunc_ekrani):
        monkeypatch.setattr(modul, "onay", lambda *a, **k: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a: mesajlar.append(a[-1])))
    monkeypatch.setattr(QMessageBox, "warning", staticmethod(lambda *a: mesajlar.append(a[-1])))
    return mesajlar
