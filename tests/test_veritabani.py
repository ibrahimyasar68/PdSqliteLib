## Veritabanı katmanı (database/) testleri ##
import datetime
import sqlite3

import pytest

from conftest import ADMIN_SIFRE, ESKI_SIFRE
from database import odunc
from database.istatistik import BELIRTILMEMIS, rapor
from database.kitaplar import (farkli_degerler, kitap_ara, kitap_bul, kitap_ekle, kitap_filtrele, kitap_guncelle,
                               secim_listesi)
from database.kullanicilar import (giris_kontrol, kullanici_bul, kullanici_ekle, kullanici_var_mi, sifre_dogrula,
                                   sifre_hashle)
from database.modeller import Kitap, Kullanici, Odunc
from database.odunc import disaridakiler, kitap_oduncte


def odunc_ver(user_id, book_id, tarih="2026-01-01"):
    odunc.odunc_ver(user_id, book_id, datetime.datetime.fromisoformat(f"{tarih}T10:00"))


def iade_al(user_id, book_id, tarih="2026-01-15"):
    return odunc.iade_al(user_id, book_id, datetime.datetime.fromisoformat(f"{tarih}T11:00"))


def yeni_uye(kullanici="yeni", sifre="parola1"):
    return kullanici_ekle(Kullanici(None, kullanici, "Yeni Üye"), sifre)


# --- Şifreler ---

def test_sifre_hash_ve_dogrulama():
    kayitli = sifre_hashle("gizli")
    assert kayitli.startswith("pbkdf2$") and "gizli" not in kayitli
    assert sifre_dogrula("gizli", kayitli)
    assert not sifre_dogrula("yanlis", kayitli)
    assert sifre_hashle("gizli") != kayitli  # her seferinde farklı tuz


def test_giris_kontrol_yetkiyi_dondurur():
    assert giris_kontrol("admin", ADMIN_SIFRE) == "admin"
    assert giris_kontrol("admin", "yanlis") is None
    assert giris_kontrol("olmayan", ADMIN_SIFRE) is None


def test_eski_duz_metin_sifre_ilk_giriste_hashlenir(db):
    assert giris_kontrol("eski", ESKI_SIFRE) == "guest"
    kayitli = db.execute("SELECT sifre FROM users WHERE kullanici='eski'").fetchone()[0]
    assert kayitli.startswith("pbkdf2$")
    assert giris_kontrol("eski", ESKI_SIFRE) == "guest"


def test_yeni_kullanici_sifresi_hashli_kaydedilir(db):
    yeni_uye()
    kayitli = db.execute("SELECT sifre FROM users WHERE kullanici='yeni'").fetchone()[0]
    assert kayitli.startswith("pbkdf2$") and sifre_dogrula("parola1", kayitli)


def test_ayni_isimde_birden_fazla_kullanici_bulunur():
    # Eskiden 2+ eşleşmede None dönüp uyarı atlanıyordu
    assert kullanici_var_mi("adi_soyadi", "Ayşe Yılmaz") is True
    assert kullanici_var_mi("adi_soyadi", "Olmayan Kişi") is False


# --- Kitaplar, tırnak işareti ve SQL injection ---

def test_tirnakli_degerler_eklenir_bulunur_guncellenir(db):
    kitap_ekle(Kitap("Çocuk'un Kitabı", "D'Artagnan", "", "Roman", "L'Harmattan", "2021", "99"))
    satir = kitap_filtrele({"Yazari": ["D'Artagnan"]})
    assert len(satir) == 1 and satir[0][1] == "Çocuk'un Kitabı"
    kitap_guncelle(Kitap("Çocuk'un Kitabı", "D'Artagnan", "", "Roman", "O'Reilly", "2021", "100", id=satir[0][0]))
    assert db.execute("SELECT Yayinevi FROM kayitlistesi WHERE Id=?", (satir[0][0],)).fetchone()[0] == "O'Reilly"


def test_sql_injection_etkisiz(db):
    kitap_guncelle(Kitap("x'; DROP TABLE users; --", id=1))
    assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 4
    assert kitap_filtrele({"Adi": ["' OR '1'='1"]}) == []


def test_filtre_listesi_bos_degerleri_icermez():
    yillar = farkli_degerler("Yili")
    assert "" not in yillar and yillar == sorted(yillar)


def test_gecersiz_kolon_reddedilir():
    with pytest.raises(ValueError):
        farkli_degerler("Adi; DROP TABLE users")
    with pytest.raises(ValueError):
        kullanici_var_mi("sifre", "x")


def test_ayni_adli_kitaplar_ayri_idlerle_listelenir():
    iklimler = [k for k in secim_listesi() if k[1] == "İklimler"]
    assert len(iklimler) == 2 and iklimler[0][0] != iklimler[1][0]


def test_istatistik_sayilari():
    turler = rapor("Turu", 35)
    assert list(turler.items())[0] == ("Roman", 6)
    assert len(rapor("Turu", 2)) == 2   # en fazla istenen kadar
    assert len(kitap_ara("")) == 8


# --- Ödünç ve iade ---

def test_odunc_ve_iade(db):
    odunc_ver(3, 1)
    assert kitap_oduncte(1)
    assert [(o.uye_id, o.kitap_id) for o in disaridakiler()] == [(3, 1)]
    assert iade_al(3, 1) is not None
    assert not kitap_oduncte(1) and disaridakiler() == []
    assert iade_al(3, 1) is None                     # dışarıda değilse kapatılacak ödünç yok


def test_iade_gecmis_kayitlari_bozmaz(db):
    odunc_ver(3, 1, "2025-01-01")
    iade_al(3, 1, "2025-01-10")
    odunc_ver(3, 1, "2026-01-01")
    iade_al(3, 1, "2026-01-20")
    satirlar = db.execute("SELECT outdate, status, indate FROM follow ORDER BY outdate").fetchall()
    assert satirlar == [("2025-01-01", "in", "2025-01-10"), ("2026-01-01", "in", "2026-01-20")]


def test_silinmis_kitap_ve_uye_listeyi_bozmaz(db):
    odunc_ver(999, 9999)
    o = disaridakiler()[0]
    assert isinstance(o, Odunc) and o.kitap == "(silinmiş kitap)" and o.uye == "(silinmiş üye)"


def test_istatistik_her_kitabi_sayar_bos_degerler_belirtilmemis(db):
    db.execute("INSERT INTO kayitlistesi (Adi, Turu, Yili) VALUES ('Yılsız', 'Roman', NULL), ('Türsüz', '', '2000')")
    db.commit()
    turler = rapor("Turu", 35)
    assert turler["Roman"] == 7                      # yılı boş olan da sayıldı
    assert turler[BELIRTILMEMIS] == 1
    assert rapor("Yili", 35)[BELIRTILMEMIS] == 2     # Kuyucaklı Yusuf ve Yılsız


def test_olmayan_kayit_none_dondurur():
    assert kitap_bul(999) is None and kullanici_bul(999) is None


def test_kayitlar_model_olarak_doner():
    k = kitap_bul(7)
    assert k == Kitap("Kuyucaklı Yusuf", "Sabahattin ALİ", turu="Roman", yayinevi="YKY", sayfa="220", id=7)
    u = kullanici_bul(3)
    assert u == Kullanici(3, "ayse1", "Ayşe Yılmaz", "5551112233", "ayse@ornek.com", "guest")
    assert not hasattr(u, "sifre")                   # şifre modele girmez


def test_kitap_ekle_yeni_numarayi_dondurur(db):
    yeni = kitap_ekle(Kitap("Numaralı"))
    assert db.execute("SELECT Adi FROM kayitlistesi WHERE Id=?", (yeni,)).fetchone()[0] == "Numaralı"


def test_hatali_yazma_yarim_kalmaz(db):
    # Kullanıcı adı benzersizdir: ikinci kayıt hata verir, bağlantıda bekleyen yazma kalmaz
    yeni_uye("tek")
    with pytest.raises(sqlite3.IntegrityError):
        yeni_uye("tek")
    assert not db.in_transaction
