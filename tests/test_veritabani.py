## Veritabanı katmanı (database/) testleri ##
from conftest import ADMIN_SIFRE, ESKI_SIFRE
from database.dbbase import (degistir_kayit, ekle_kayit, save_work_to_db, sifre_dogrula,
                             sifre_hashle, update_work_to_db, user_ekle)
from database.dbframe import (df_all_list, df_book_id_list, df_sort_list,
                              df_user_query, df_work_table_book,
                              giris_kontrol, kitap_filtrele, kitap_oduncte, rapor)


def odunc_ver(user_id, book_id, tarih="2026-01-01"):
    save_work_to_db([str(user_id), str(book_id), tarih, "10:00 ", "out", "", ""])


def iade_al(user_id, book_id, tarih="2026-01-15"):
    update_work_to_db([str(user_id), str(book_id), "", "", "in", tarih, "11:00 "])


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
    user_ekle(["yeni", "parola1", "Yeni Üye", "", "", "guest"])
    kayitli = db.execute("SELECT sifre FROM users WHERE kullanici='yeni'").fetchone()[0]
    assert kayitli.startswith("pbkdf2$") and sifre_dogrula("parola1", kayitli)


def test_ayni_isimde_birden_fazla_kullanici_bulunur():
    # Eskiden 2+ eşleşmede None dönüp uyarı atlanıyordu
    assert df_user_query("adi_soyadi", "Ayşe Yılmaz") is True
    assert df_user_query("adi_soyadi", "Olmayan Kişi") is False


# --- Kitaplar, tırnak işareti ve SQL injection ---

def test_tirnakli_degerler_eklenir_bulunur_guncellenir(db):
    ekle_kayit(["Çocuk'un Kitabı", "D'Artagnan", "", "Roman", "L'Harmattan", "2021", "99"])
    satir = kitap_filtrele({"Yazari": ["D'Artagnan"]})
    assert len(satir) == 1 and satir[0][1] == "Çocuk'un Kitabı"
    degistir_kayit([satir[0][0], "Çocuk'un Kitabı", "D'Artagnan", "", "Roman", "O'Reilly", "2021", "100"])
    assert db.execute("SELECT Yayinevi FROM kayitlistesi WHERE Id=?", (satir[0][0],)).fetchone()[0] == "O'Reilly"


def test_sql_injection_etkisiz(db):
    degistir_kayit([1, "x'; DROP TABLE users; --", "", "", "", "", "", ""])
    assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 4
    assert kitap_filtrele({"Adi": ["' OR '1'='1"]}) == []


def test_filtre_listesi_bos_degerleri_icermez():
    yillar = df_sort_list("Yili")
    assert "" not in yillar and yillar == sorted(yillar)


def test_gecersiz_kolon_reddedilir():
    import pytest
    with pytest.raises(ValueError):
        df_sort_list("Adi; DROP TABLE users")


def test_ayni_adli_kitaplar_ayri_idlerle_listelenir():
    iklimler = [k for k in df_book_id_list() if k[1] == "İklimler"]
    assert len(iklimler) == 2 and iklimler[0][0] != iklimler[1][0]


def test_istatistik_sayilari():
    turler = rapor("Turu", 35)
    assert turler.index[0] == "Roman" and turler.iloc[0] == 6
    assert len(rapor("Turu", 2)) == 2   # en fazla istenen kadar
    assert len(df_all_list()) == 8


# --- Ödünç ve iade ---

def test_odunc_ve_iade(db):
    odunc_ver(3, 1)
    assert kitap_oduncte(1)
    assert [s[7:] for s in df_work_table_book()] == [["3", "1"]]
    iade_al(3, 1)
    assert not kitap_oduncte(1) and df_work_table_book() == []


def test_iade_gecmis_kayitlari_bozmaz(db):
    odunc_ver(3, 1, "2025-01-01")
    iade_al(3, 1, "2025-01-10")
    odunc_ver(3, 1, "2026-01-01")
    iade_al(3, 1, "2026-01-20")
    satirlar = db.execute("SELECT outdate, status, indate FROM follow ORDER BY outdate").fetchall()
    assert satirlar == [("2025-01-01", "in", "2025-01-10"), ("2026-01-01", "in", "2026-01-20")]


def test_silinmis_kitap_ve_uye_listeyi_bozmaz(db):
    odunc_ver(999, 9999)
    satir = df_work_table_book()[0]
    assert satir[0] == "(silinmiş kitap)" and satir[3] == "(silinmiş üye)"


def test_istatistik_her_kitabi_sayar_bos_degerler_belirtilmemis(db):
    from database.dbframe import BELIRTILMEMIS
    db.execute("INSERT INTO kayitlistesi (Adi, Turu, Yili) VALUES ('Yılsız', 'Roman', NULL), ('Türsüz', '', '2000')")
    db.commit()
    turler = rapor("Turu", 35)
    assert turler["Roman"] == 7                      # yılı boş olan da sayıldı
    assert turler[BELIRTILMEMIS] == 1
    assert rapor("Yili", 35)[BELIRTILMEMIS] == 2     # Kuyucaklı Yusuf ve Yılsız
