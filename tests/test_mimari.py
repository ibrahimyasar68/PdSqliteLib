## Mimari kurallar ##
# Ekranlar (acodes/) veritabanına doğrudan yazmaz: yazma işlemleri kuralları denetleyen servis/ katmanından geçer.
# Okuma serbesttir. Yedekleme (database/yedek.py) bu kuralın dışındadır.
import ast
import glob
import os

import pytest

PROJE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

YAZMA_FONKSIYONLARI = {
    "kitap_ekle", "kitap_guncelle", "kitap_sil", "kitap_geri_ekle",
    "odunc_ver", "iade_al", "iade_geri_al",
    "kullanici_ekle", "kullanici_guncelle", "kullanici_sil", "sifre_guncelle",
    "birlestir", "yoksay",
}


def veritabanina_yazanlar(yol):
    """Dosyada database/ modüllerinden kullanılan yazma fonksiyonları."""
    agac = ast.parse(open(yol, encoding="utf-8").read())
    modul_adlari, bulunan = set(), set()
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.ImportFrom) and (dugum.module or "").startswith("database"):
            for ad in dugum.names:
                if dugum.module == "database":            # from database import kitaplar
                    modul_adlari.add(ad.asname or ad.name)
                elif ad.name in YAZMA_FONKSIYONLARI:      # from database.kitaplar import kitap_ekle
                    bulunan.add(ad.name)
        elif isinstance(dugum, ast.Import):
            for ad in dugum.names:
                if ad.name.startswith("database."):
                    modul_adlari.add(ad.asname or ad.name.split(".")[0])
    for dugum in ast.walk(agac):                           # kitaplar.kitap_ekle(...)
        if (isinstance(dugum, ast.Attribute) and dugum.attr in YAZMA_FONKSIYONLARI
                and isinstance(dugum.value, ast.Name) and dugum.value.id in modul_adlari):
            bulunan.add(dugum.attr)
    return bulunan


@pytest.mark.parametrize("yol", sorted(glob.glob(os.path.join(PROJE, "acodes", "*.py"))), ids=os.path.basename)
def test_ekranlar_veritabanina_dogrudan_yazmaz(yol):
    assert veritabanina_yazanlar(yol) == set(), "yazma işlemini servis/ üzerinden yapın"


def test_denetim_yazmayi_yakalar(tmp_path):
    ornek = tmp_path / "ornek.py"
    ornek.write_text("from database import kitaplar\nfrom database.odunc import iade_al\nkitaplar.kitap_sil(1)\n")
    assert veritabanina_yazanlar(ornek) == {"iade_al", "kitap_sil"}
