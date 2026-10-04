## Servis katmanı (servis/) testleri: kurallar pencere açmadan denetlenir ##
import pytest

from database.baglanti import islem
from database.kitaplar import kitap_bul, kitap_ekle
from database.kullanicilar import giris_kontrol, kullanici_bul
from database.modeller import Kitap, Kullanici
from servis import KuralHatasi
from servis import duzeltme, kitap, kullanici, odunc


def sayi(db, sql):
    return db.execute(sql).fetchone()[0]


# --- İşlem (transaction) ---

def test_ic_ice_islemde_hata_hepsini_geri_alir(db):
    with pytest.raises(RuntimeError):
        with islem():
            kitap_ekle(Kitap("Yarım Kalan"))            # kendi islem() bloğu kaydetmez
            raise RuntimeError
    assert sayi(db, "SELECT COUNT(*) FROM kayitlistesi WHERE Adi='Yarım Kalan'") == 0
    assert not db.in_transaction


# --- Kitap ---

@pytest.mark.parametrize("yeni,alan", [(Kitap(""), "adi"), (Kitap("Hatalı", isbn="978-0-306-40615-8"), "isbn")])
def test_hatali_kitap_kaydedilmez(db, yeni, alan):
    assert kitap.kayit_engeli(yeni).alan == alan
    with pytest.raises(KuralHatasi):
        kitap.kaydet(yeni)
    assert sayi(db, "SELECT COUNT(*) FROM kayitlistesi") == 8


def test_kitap_kaydedilir_isbn_tiresiz(db):
    yeni = kitap.kaydet(Kitap("Yeni", isbn="978-0-306-40615-7"))
    assert kitap_bul(yeni).isbn == "9780306406157"


def test_kopya_disaridakinden_az_olamaz(db):
    db.execute("UPDATE kayitlistesi SET Kopya=2 WHERE Id=1")
    db.commit()
    odunc.ver(1, 3)
    odunc.ver(1, 4)
    with pytest.raises(KuralHatasi, match="2 kopyası şu an üyelerde") as hata:
        kitap.kaydet(Kitap("Yol Ayrımı", kopya=1, id=1))
    assert hata.value.alan == "kopya" and kitap_bul(1).kopya == 2


def test_oduncteki_kitap_silinemez_silinen_geri_gelir(db):
    odunc.ver(1, 3)
    with pytest.raises(KuralHatasi, match="ödünçte"):
        kitap.sil(1)
    silinen = kitap.sil(2)
    assert kitap_bul(2) is None
    kitap.geri_getir(silinen)
    assert kitap_bul(2) == silinen
    with pytest.raises(KuralHatasi):
        kitap.geri_getir(silinen)                     # numara dolu: iki kez geri getirilmez


# --- Ödünç ---

def test_odunc_ver_ve_iade(db):
    odunc.ver(1, 3)
    assert odunc.verme_engeli(1, 4).alan == "kitap"   # tek kopya dışarıda
    kayit_no = odunc.iade_al(3, 1)
    assert odunc.verme_engeli(1, 4) is None
    with pytest.raises(KuralHatasi, match="bulunamadı"):
        odunc.iade_al(3, 1)                           # ikinci kez iade alınmaz
    odunc.iadeyi_geri_al(kayit_no, 3, 1)
    assert sayi(db, "SELECT COUNT(*) FROM follow WHERE status='out'") == 1


@pytest.mark.parametrize("kitap_id,uye_id,mesaj", [
    (999, 3, "Bu kitap silinmiş."),
    (1, 999, "Bu üye silinmiş."),
    (None, 3, "Kitap ve üye seçiniz!"),
])
def test_verilemeyen_odunc_yazilmaz(db, kitap_id, uye_id, mesaj):
    with pytest.raises(KuralHatasi, match=mesaj):
        odunc.ver(kitap_id, uye_id)
    assert sayi(db, "SELECT COUNT(*) FROM follow") == 0


def test_uyeye_ayni_kitabin_ikinci_kopyasi_verilmez(db):
    db.execute("UPDATE kayitlistesi SET Kopya=3 WHERE Id=1")
    db.commit()
    odunc.ver(1, 3)
    with pytest.raises(KuralHatasi, match="zaten bu üyede"):
        odunc.ver(1, 3)


def test_iade_geri_alinamaz_kitap_yeniden_verildiyse(db):
    odunc.ver(1, 3)
    kayit_no = odunc.iade_al(3, 1)
    odunc.ver(1, 4)
    with pytest.raises(KuralHatasi, match="geri alınamaz"):
        odunc.iadeyi_geri_al(kayit_no, 3, 1)


# --- Kullanıcı ---

def uye(kullanici_adi="veli", **alanlar):
    return Kullanici(None, kullanici_adi, alanlar.pop("adi_soyadi", "Veli Can"), **alanlar)


@pytest.mark.parametrize("yeni,sifre,alan", [
    (uye(yetki="yonetici"), "parola1", "yetki"),
    (uye(), "kisa", "sifre"),
    (uye(telefon="123"), "parola1", "telefon"),
    (uye(mail="gecersiz"), "parola1", "mail"),
    (uye("ayse1"), "parola1", "kullanici"),
])
def test_hatali_kullanici_eklenmez(db, yeni, sifre, alan):
    assert kullanici.ekleme_engeli(yeni, sifre).alan == alan
    with pytest.raises(KuralHatasi):
        kullanici.ekle(yeni, sifre)
    assert sayi(db, "SELECT COUNT(*) FROM users") == 4


def test_kullanici_eklenir(db):
    assert kullanici_bul(kullanici.ekle(uye(), "parola1")).kullanici == "veli"


def test_son_admin_ve_kendi_yetkisi_korunur(db):
    admin = kullanici_bul(1)
    with pytest.raises(KuralHatasi, match="Son admin"):
        kullanici.guncelle(Kullanici(**{**vars(admin), "yetki": "guest"}), "ayse1")
    with pytest.raises(KuralHatasi, match="Kendi yetkinizi"):
        kullanici.guncelle(Kullanici(**{**vars(admin), "yetki": "guest"}), "admin")
    assert kullanici_bul(1).yetki == "admin"


@pytest.mark.parametrize("silinen,aktif,mesaj", [
    (1, "admin", "Kendi hesabınızı"),
    (1, "ayse1", "Son admin"),
    (3, "admin", "iade edilmemiş 1 kitap"),
])
def test_silinemeyen_kullanici(db, silinen, aktif, mesaj):
    odunc.ver(1, 3)
    with pytest.raises(KuralHatasi, match=mesaj):
        kullanici.sil(kullanici_bul(silinen), aktif)
    assert kullanici_bul(silinen) is not None


def test_sifre_degistir_mevcut_sifreyi_sorar(db):
    with pytest.raises(KuralHatasi, match="Mevcut şifre yanlış"):
        kullanici.sifre_degistir("ayse1", "yeniparola", eski="yanlis")
    kullanici.sifre_degistir("admin", "yeniparola", "yeniparola")
    assert giris_kontrol("admin", "yeniparola") == "admin"


# --- Veri düzeltme ---

def test_birlestirmeden_once_bir_kez_yedek_alinir(db):
    degisen, yedek = duzeltme.birlestir("Yayinevi", ["YKY"], "Yapı Kredi Yayınları")
    assert degisen == 1 and "duzeltme_oncesi_" in yedek
    assert duzeltme.birlestir("Yayinevi", ["Cem Yayınevi"], "Cem", onceki_yedek=yedek)[1] == yedek
    with pytest.raises(KuralHatasi):
        duzeltme.birlestir("Yayinevi", ["Cem"], "  ")


# --- Değişiklik bildirimleri ---

@pytest.fixture
def bildirilen(monkeypatch):
    import servis
    konular = []
    monkeypatch.setattr(servis, "_dinleyiciler", [konular.append])
    return konular


def test_basarili_yazma_konusuyla_bildirilir(db, bildirilen):
    kitap.sil(kitap.kaydet(Kitap("Geçici")))
    odunc.ver(1, 3)
    odunc.iade_al(3, 1)
    kullanici.ekle(uye(), "parola1")
    duzeltme.birlestir("Yayinevi", ["YKY"], "Yapı Kredi")
    assert bildirilen == ["kitaplar", "kitaplar", "odunc", "odunc", "kullanicilar", "kitaplar"]


def test_basarisiz_yazma_bildirilmez(db, bildirilen):
    for islev in (lambda: kitap.kaydet(Kitap("")), lambda: odunc.ver(999, 3), lambda: kullanici.ekle(uye(), "kisa"),
                  lambda: kitap.sil(999)):
        with pytest.raises(KuralHatasi):
            islev()
    assert bildirilen == []
