## Kitap Kayıt > Kitaplar: tek ekranda ekleme, düzenleme, silme ##
import pytest

from acodes.library import Library


@pytest.fixture
def lib(app, uyarilar):
    return Library()


@pytest.fixture
def k(lib):
    return lib.kitaplar


def liste(k):
    return [k.tablo.item(r, 1).text() for r in range(k.tablo.rowCount())]


def doldur(k, **alanlar):
    for kolon, deger in alanlar.items():
        k.alan[kolon].setText(deger)


# --- Liste ve seçim ---

def test_eski_uc_ekran_yerine_tek_ekran(lib):
    t = lib.QtLibrary.tabWidget_3
    assert [t.tabText(i) for i in range(t.count())] == ["Kitaplar", "Veri Düzeltme"]


def test_liste_ve_arama(k):
    assert k.tablo.rowCount() == 8 and k.sonuc.text() == "8 kitap"
    k.arama.setText("iklimler")
    assert liste(k) == ["İklimler", "İklimler"] and k.sonuc.text() == "2 kitap bulundu"   # aynı adlı baskılar ayrı


def test_secince_formda_acilir(k, db):
    db.execute("UPDATE kayitlistesi SET Kopya=2, Raf='A-1' WHERE Id=1")
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES ('3','1','2026-01-01','10:00','out','','')")
    db.commit()
    k.yenile()
    k.sec(1)
    assert k.alan["Adi"].text() == "Yol Ayrımı" and k.alan["Yazari"].text() == "Kemal TAHİR"
    assert k.ek.raf.text() == "A-1" and k.ek.kopya.value() == 2
    assert k.form_baslik.text() == "Kitap #1" and k.btn_sil.isEnabled()
    assert k.kopya_bilgi.text() == "2 kopyadan 1 tanesi şu an üyelerde."
    satir = k.tablo.selectionModel().selectedRows()[0].row()
    assert k.tablo.item(satir, 1).text() == "Yol Ayrımı"


def test_tabloda_tiklayinca_secilir(k):
    k.tablo.selectRow(2)
    assert k.kitap_id == int(k.tablo.item(2, 0).text())


# --- Ekleme ---

def test_yeni_kitap_ekleme(lib, k, db):
    k.yeni()
    assert k.form_baslik.text() == "Yeni kitap" and not k.btn_sil.isEnabled()
    doldur(k, Adi="anne'nin kitabı", Yazari="yeni yazar", Turu="roman", Yili="2025", Sayfa="120")
    k.ek.isbn.setText("978-0-306-40615-7")
    k.ek.kopya.setValue(3)
    k.kaydet()
    kayit = db.execute("SELECT Id, Adi, Yazari, Turu, ISBN, Kopya FROM kayitlistesi WHERE Adi LIKE 'Anne%kitab%'").fetchone()
    assert kayit[1:] == ("Anne'nin Kitabı", "Yeni Yazar", "Roman", "9780306406157", 3)
    assert k.kitap_id == kayit[0] and k.form_baslik.text() == f"Kitap #{kayit[0]}"    # yeni kitap seçili kalır
    # diğer ekranların listeleri de yenilendi
    assert lib.odunc.kitap.findText("Anne'nin Kitabı") > 0
    yazarlar = lib.filtre.combo["Yazari"]
    assert "Yeni Yazar" in [yazarlar.itemText(i) for i in range(yazarlar.count())]


@pytest.mark.parametrize("adi,isbn,mesaj", [
    ("", "", "Kitap adı boş olamaz."),
    ("Hatalı ISBN", "978-0-306-40615-8", "ISBN geçerli değil"),
])
def test_eksik_veya_hatali_kayit(k, db, uyarilar, adi, isbn, mesaj):
    k.yeni()
    doldur(k, Adi=adi)
    k.ek.isbn.setText(isbn)
    k.kaydet()
    assert mesaj in uyarilar[-1]
    assert db.execute("SELECT COUNT(*) FROM kayitlistesi").fetchone()[0] == 8


# --- Güncelleme ---

def test_guncelleme_mevcut_yazimi_bozmaz(k, db):
    k.sec(1)
    k.ek.raf.setText("C-9")
    k.kaydet()
    assert db.execute("SELECT Yazari, Raf FROM kayitlistesi WHERE Id=1").fetchone() == ("Kemal TAHİR", "C-9")


def test_kopya_disaridakinden_az_olamaz(k, db, uyarilar):
    db.execute("UPDATE kayitlistesi SET Kopya=3 WHERE Id=1")
    db.executemany("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES (?,'1','2026-01-01','10:00','out','','')", [("3",), ("4",)])
    db.commit()
    k.sec(1)
    k.ek.kopya.setValue(1)
    k.kaydet()
    assert "2 kopyası şu an üyelerde" in uyarilar[-1]
    assert db.execute("SELECT Kopya FROM kayitlistesi WHERE Id=1").fetchone()[0] == 3


def test_vazgec_degisiklikleri_geri_alir(k):
    k.sec(6)
    k.alan["Adi"].setText("değişti")
    k.vazgec()
    assert k.alan["Adi"].text() == "Satranç"


# --- Silme ---

def test_silme(k, db):
    k.sec(8)
    k.sil()
    assert db.execute("SELECT COUNT(*) FROM kayitlistesi WHERE Id=8").fetchone()[0] == 0
    assert k.kitap_id is None and k.form_baslik.text() == "Yeni kitap" and "Denemeler" not in liste(k)


def test_silme_geri_alinir(lib, k, db):
    k.sec(8)
    k.sil()
    b = lib.bildirim
    assert b.kutu.text() == "Denemeler silindi" and b.eylem.isVisibleTo(b.kutu) and b.eylem.text() == "Geri Al"
    b.eylem.click()
    assert db.execute("SELECT Adi, Yazari, Yili FROM kayitlistesi WHERE Id=8").fetchone() == ("Denemeler", "MONTAIGNE", "1983")
    assert k.kitap_id == 8 and "Denemeler" in liste(k) and lib.QtLibrary.statusbar.currentMessage() == "'Denemeler' geri getirildi."
    assert not b.eylem.isVisibleTo(b.kutu)


def test_oduncteki_kitap_silinemez(k, db, uyarilar):
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES ('3','1','2026-01-01','10:00','out','','')")
    db.commit()
    k.sec(1)
    k.sil()
    assert uyarilar[-1] == "Bu kitap ödünçte. İade alınmadan silinemez!"
    assert db.execute("SELECT COUNT(*) FROM kayitlistesi WHERE Id=1").fetchone()[0] == 1


def test_sil_butonu_kirmizi_ve_ikonlu(k):
    assert k.btn_sil.objectName() == "kitap_sil" and not k.btn_sil.icon().isNull()


# --- Öneriler ---

def test_alanlarda_mevcut_degerler_onerilir(k):
    tamamlayici = k.alan["Yazari"].completer()
    tamamlayici.setCompletionPrefix("mal ta")      # kelimenin ortasından da bulur
    assert tamamlayici.currentCompletion() == "Kemal TAHİR"
    assert k.alan["Adi"].completer() is None
