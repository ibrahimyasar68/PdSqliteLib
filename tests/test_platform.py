## Platforma göre veritabanı konumu ve paketleme betikleri testleri ##
# Windows'a özel kod yolları burada taklit edilerek (sys.platform, APPDATA) sınanır.
import os
import re
import sys

import pytest

from database import dbbase

PROJE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


@pytest.fixture
def paketli(monkeypatch, tmp_path):
    """Paketlenmiş (frozen) uygulama ortamı: pakette örnek bir veritabanı var."""
    paket = tmp_path / "paket"
    (paket / "data").mkdir(parents=True)
    (paket / "data" / "DBL_Kayit.db").write_bytes(b"paketteki veritabani")
    monkeypatch.delenv("PDSQLITE_DB", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(paket), raising=False)
    return tmp_path


def test_windows_appdata_altina_kopyalanir(paketli, monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(paketli / "AppData" / "Roaming"))
    yol = dbbase.db_yolu()
    assert yol == os.path.join(str(paketli / "AppData" / "Roaming"), "PdSqliteLib", "DBL_Kayit.db")
    assert open(yol, "rb").read() == b"paketteki veritabani"


def test_mac_application_support_altina_kopyalanir(paketli, monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setenv("HOME", str(paketli / "ev"))
    yol = dbbase.db_yolu()
    assert yol == str(paketli / "ev" / "Library" / "Application Support" / "PdSqliteLib" / "DBL_Kayit.db")
    assert os.path.exists(yol)


def test_mevcut_veritabaninin_uzerine_yazilmaz(paketli, monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(paketli / "AppData"))
    yol = dbbase.db_yolu()
    open(yol, "wb").write(b"kullanicinin verisi")
    assert dbbase.db_yolu() == yol
    assert open(yol, "rb").read() == b"kullanicinin verisi"


def test_gelistirmede_proje_data_klasoru(monkeypatch):
    monkeypatch.delenv("PDSQLITE_DB", raising=False)
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    assert os.path.normpath(dbbase.db_yolu()) == os.path.normpath(os.path.join(PROJE, "data", "DBL_Kayit.db"))


# --- Paketleme betikleri birbiriyle uyumlu kalsın ---

def oku(ad):
    with open(os.path.join(PROJE, "scripts", ad), newline="") as f:
        return f.read()


def test_windows_betikleri_ascii_ve_crlf():
    for ad in ("build_windows.bat", "baslat_windows.bat"):
        metin = oku(ad)
        assert metin.isascii(), ad
        assert "\r\n" in metin and "\n" not in metin.replace("\r\n", ""), ad


def test_mac_ve_windows_paketleri_ayni_ayarlarla():
    mac, win = oku("build_mac.sh"), oku("build_windows.bat")
    for betik in (mac, win):
        assert "requirements.txt" in betik and "--windowed" in betik and "family.ico" in betik
    assert set(re.findall(r"--exclude-module (\w+)", mac)) == set(re.findall(r"--exclude-module (\w+)", win))
    assert "DBL_Kayit.db:data" in mac and "DBL_Kayit.db;data" in win
