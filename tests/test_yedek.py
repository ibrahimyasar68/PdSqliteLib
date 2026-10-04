## Yedekleme testleri ##
import os
import shutil
import sqlite3

import pytest

from acodes.library import Library
from database import yedek


@pytest.fixture(autouse=True)
def bos_yedek_klasoru():
    shutil.rmtree(yedek.yedek_klasoru(), ignore_errors=True)
    yield
    shutil.rmtree(yedek.yedek_klasoru(), ignore_errors=True)


def kitap_sayisi(yol):
    b = sqlite3.connect(yol)
    try:
        return b.execute("SELECT COUNT(*) FROM kayitlistesi").fetchone()[0]
    finally:
        b.close()


def test_yedek_tum_veriyi_icerir(tmp_path):
    yol = yedek.yedek_al(str(tmp_path / "elle.db"))
    assert kitap_sayisi(yol) == 8


def test_otomatik_yedek_gunde_bir_kez():
    ilk = yedek.otomatik_yedek()
    assert ilk and os.path.basename(ilk).startswith("DBL_Kayit_")
    assert yedek.otomatik_yedek() is None
    assert len(yedek.otomatik_yedekler()) == 1


def test_eski_otomatik_yedekler_temizlenir():
    klasor = yedek.yedek_klasoru()
    for gun in range(1, 13):
        open(os.path.join(klasor, f"DBL_Kayit_202501{gun:02d}_090000.db"), "w").close()
    elle = os.path.join(klasor, "DBL_Kayit_yedek_20250101.db")   # elle alınan yedeğe dokunulmaz
    open(elle, "w").close()
    yedek.otomatik_yedek()
    kalanlar = [os.path.basename(y) for y in yedek.otomatik_yedekler()]
    assert len(kalanlar) == yedek.OTOMATIK_SAKLA
    # 12 eski + bugünkü = 13 yedek; en yeni 10 tanesi kalır, 1-3 Ocak silinir
    assert kalanlar[0] == "DBL_Kayit_20250104_090000.db"
    assert os.path.exists(elle)


def test_geri_yukleme(db, tmp_path):
    yol = yedek.yedek_al(str(tmp_path / "yedek.db"))
    db.execute("DELETE FROM kayitlistesi WHERE Id>2")
    db.commit()
    onceki = yedek.geri_yukle(yol)
    assert db.execute("SELECT COUNT(*) FROM kayitlistesi").fetchone()[0] == 8
    assert kitap_sayisi(onceki) == 2          # geri yüklemeden önceki hal saklandı


@pytest.mark.parametrize("icerik,beklenen", [
    ("sqlite degil", "okunamadı"),
    ("bos_tablo", "eksik tablolar"),
    ("admin_yok", "admin kullanıcı yok"),
])
def test_uygunsuz_yedek_reddedilir(db, tmp_path, icerik, beklenen):
    yol = str(tmp_path / "hatali.db")
    if icerik == "sqlite degil":
        open(yol, "w").write("bu bir veritabanı değil" * 100)
    elif icerik == "bos_tablo":
        sqlite3.connect(yol).execute("CREATE TABLE baska (x)").connection.close()
    else:
        yedek.yedek_al(yol)
        b = sqlite3.connect(yol)
        b.execute("UPDATE users SET yetki='guest'")
        b.commit()
        b.close()
    assert beklenen in yedek.yedek_hatasi(yol)
    with pytest.raises(ValueError):
        yedek.geri_yukle(yol)
    assert db.execute("SELECT COUNT(*) FROM kayitlistesi").fetchone()[0] == 8


# --- Admin panelindeki butonlar ---

def test_panelden_yedek_alma(app, uyarilar, monkeypatch, tmp_path):
    hedef = str(tmp_path / "panel.db")
    monkeypatch.setattr(yedek_modulu_dialog(), "getSaveFileName", staticmethod(lambda *a: (hedef, "")))
    Library().yedek_al_ekrani()
    assert kitap_sayisi(hedef) == 8 and uyarilar[-1].startswith("Yedek alındı")


def test_panelden_geri_yukleme_listeleri_yeniler(app, uyarilar, monkeypatch, db, tmp_path):
    yol = yedek.yedek_al(str(tmp_path / "yedek.db"))
    lib = Library()
    db.execute("DELETE FROM kayitlistesi WHERE Id>2")
    db.commit()
    lib.yenile()
    assert lib.kitaplar.tablo.rowCount() == 2
    monkeypatch.setattr(yedek_modulu_dialog(), "getOpenFileName", staticmethod(lambda *a: (yol, "")))
    lib.geri_yukle_ekrani()
    assert lib.kitaplar.tablo.rowCount() == 8
    assert uyarilar[-1].startswith("Yedek geri yüklendi")


def test_panel_hatali_yedegi_yuklemez(app, uyarilar, monkeypatch, db, tmp_path):
    yol = str(tmp_path / "bozuk.db")
    open(yol, "w").write("bozuk" * 100)
    monkeypatch.setattr(yedek_modulu_dialog(), "getOpenFileName", staticmethod(lambda *a: (yol, "")))
    Library().geri_yukle_ekrani()
    assert "okunamadı" in uyarilar[-1]


def yedek_modulu_dialog():
    from PySide6.QtWidgets import QFileDialog
    return QFileDialog


def test_guvenlik_yedekleri_sinirli_sayida_tutulur():
    klasor = yedek.yedek_klasoru()
    for onek in yedek.GUVENLIK_ONEKLERI:
        for i in range(yedek.GUVENLIK_SAKLA + 4):
            open(os.path.join(klasor, f"{onek}20250101_{i:06d}.db"), "w").close()
    open(os.path.join(klasor, "elle_alinan.db"), "w").close()       # başka yedeklere dokunulmaz
    assert yedek.guvenlik_yedeklerini_temizle() == 4 * len(yedek.GUVENLIK_ONEKLERI)
    for onek in yedek.GUVENLIK_ONEKLERI:
        kalan = sorted(f for f in os.listdir(klasor) if f.startswith(onek))
        assert len(kalan) == yedek.GUVENLIK_SAKLA and kalan[-1].endswith("000013.db")   # en yeniler kalır
    assert os.path.exists(os.path.join(klasor, "elle_alinan.db"))


def test_geri_yuklemede_guvenlik_yedegi_alinir_ve_temizlenir(db, tmp_path):
    klasor = yedek.yedek_klasoru()
    for i in range(yedek.GUVENLIK_SAKLA):
        open(os.path.join(klasor, f"geri_yukleme_oncesi_20200101_{i:06d}.db"), "w").close()
    onceki = yedek.geri_yukle(yedek.yedek_al(str(tmp_path / "y.db")))
    kalan = [f for f in os.listdir(klasor) if f.startswith("geri_yukleme_oncesi_")]
    assert len(kalan) == yedek.GUVENLIK_SAKLA and os.path.basename(onceki) in kalan
