## Veri düzeltme testleri ##
import os
import shutil
import sqlite3

import pytest
from PyQt5.QtCore import Qt

from acodes.library import Library
from database import duzeltme as dz
from database import yedek


def kitap_ekle(db, **alanlar):
    kolonlar = ",".join(alanlar)
    db.execute(f"INSERT INTO kayitlistesi ({kolonlar}) VALUES ({','.join('?' * len(alanlar))})", list(alanlar.values()))


@pytest.fixture
def varyasyonlar(db):
    for yayinevi in ["Adam Yayınları", "Adam Yayınları", "Adam yayınları", "Can Yayınları", "Cem Yayınları"]:
        kitap_ekle(db, Adi="Deneme", Yayinevi=yayinevi, Yili="2000")
    for ceviren in ["Sebahattin EYÜBOĞLU", "Sebahattin EYÜBOĞLU", "Sebahattin EYYÜBOĞLU"]:
        kitap_ekle(db, Adi="Çeviri", Ceviren=ceviren, Yili="2000")
    db.commit()
    return db


@pytest.fixture(autouse=True)
def bos_yedek_klasoru():
    shutil.rmtree(yedek.yedek_klasoru(), ignore_errors=True)
    yield
    shutil.rmtree(yedek.yedek_klasoru(), ignore_errors=True)


# --- Benzerlik kuralları ---

@pytest.mark.parametrize("a,b", [
    ("Adam Yayınları", "ADAM yayınları"), ("Honoré de BALZAC", "Honore de Balzac"),
    ("M.E.B Yayınları", "MEB Yayınları"), ("Jean-Paul SARTRE", "JeanPaul  Sartre"), ("Şiir", "şiir"),
])
def test_anahtar_ayni(a, b):
    assert dz.anahtar(a) == dz.anahtar(b)


@pytest.mark.parametrize("a,b,beklenen", [
    ("sebahattin eyyuboglu", "sebahattin eyuboglu", True),
    ("lev tolstoy", "lev tolstoi", True),
    ("can yayinlari", "cem yayinlari", False),   # kısa kelimede harf farkı: farklı yayınevleri
    ("adam yayinlari", "adam yayinevi", False),  # 2'den fazla harf farkı
    ("orhan pamuk", "pamuk", False),             # kelime sayısı farklı
    ("ayni", "ayni", False),
])
def test_olasi_ayni(a, b, beklenen):
    assert dz.olasi_ayni(a, b) is beklenen


def test_benzer_gruplar(varyasyonlar):
    yayinevi = dz.benzer_gruplar("Yayinevi")
    assert yayinevi == [{"degerler": [("Adam Yayınları", 2), ("Adam yayınları", 1)], "kesin": True}]
    ceviren = dz.benzer_gruplar("Ceviren")
    assert ceviren == [{"degerler": [("Sebahattin EYÜBOĞLU", 2), ("Sebahattin EYYÜBOĞLU", 1)], "kesin": False}]
    assert dz.benzer_gruplar("Yazari") == []


def test_yoksayilan_oneri_bir_daha_gelmez(varyasyonlar):
    dz.yoksay("Ceviren", ["Sebahattin EYÜBOĞLU", "Sebahattin EYYÜBOĞLU"])
    assert dz.benzer_gruplar("Ceviren") == []
    assert len(dz.benzer_gruplar("Yayinevi")) == 1   # başka alanı etkilemez


def test_birlestir(varyasyonlar, db):
    assert dz.birlestir("Yayinevi", ["Adam yayınları", "Adam Yayınları"], "Adam Yayınları") == 1
    assert db.execute("SELECT COUNT(*) FROM kayitlistesi WHERE Yayinevi='Adam Yayınları'").fetchone()[0] == 3
    assert dz.benzer_gruplar("Yayinevi") == []
    assert dz.birlestir("Yayinevi", ["Adam Yayınları"], "Adam Yayınları") == 0


def test_birlestir_tirnak_ve_gecersiz_kolon(db):
    kitap_ekle(db, Adi="x", Yazari="O'Neil")
    assert dz.birlestir("Yazari", ["O'Neil"], "O'NEIL") == 1
    with pytest.raises(ValueError):
        dz.birlestir("Adi; DROP TABLE users", ["a"], "b")


def test_eksik_kitaplar():
    assert [k[1] for k in dz.eksik_kitaplar("Yili")] == ["Kuyucaklı Yusuf"]
    assert dz.eksik_kitaplar("Yazari") == []


def test_eski_yedek_geri_yuklenince_yoksay_tablosu_olusur(db, tmp_path):
    yol = yedek.yedek_al(str(tmp_path / "eski.db"))
    b = sqlite3.connect(yol)
    b.execute("DROP TABLE duzeltme_yoksay")
    b.commit()
    b.close()
    yedek.geri_yukle(yol)
    assert dz.benzer_gruplar("Yayinevi") == []   # tablo yeniden oluşturuldu, hata yok


# --- Ekran ---

@pytest.fixture
def lib(app, uyarilar, varyasyonlar):
    l = Library()
    q = l
    q.sekmeler.setCurrentWidget(q.kayit)
    q.alt_sekmeler[q.kayit].setCurrentWidget(l.duzeltme)
    return l


def alan_sec(ekran, kolon):
    ekran.alan.setCurrentIndex(ekran.alan.findData(kolon))


def test_sekme_acilinca_oneriler_yuklenir(lib):
    e = lib.duzeltme
    q = lib
    assert q.alt_sekmeler[q.kayit].tabText(q.alt_sekmeler[q.kayit].indexOf(e)) == "Veri Düzeltme"
    alan_sec(e, "Yayinevi")
    assert e.agac.topLevelItemCount() == 1 and e.ozet.text() == "1 öneri (1 kesin, 0 olası)"
    assert e.hedef.text() == "Adam Yayınları"       # en çok kullanılan yazım önerilir
    assert e.eksik_ozet.text() == "1 kitap"


def test_birlestirme_ekrandan(lib, db, uyarilar):
    e = lib.duzeltme
    alan_sec(e, "Yayinevi")
    e.birlestir()
    assert db.execute("SELECT COUNT(*) FROM kayitlistesi WHERE Yayinevi='Adam yayınları'").fetchone()[0] == 0
    assert e.agac.topLevelItemCount() == 0 and e.ozet.text() == "Benzer yazım bulunamadı"
    assert uyarilar[-1].startswith("1 kitap güncellendi")
    assert os.path.exists(e.yedek_alindi) and "duzeltme_oncesi_" in e.yedek_alindi
    cmb = lib.filtre.combo["Yayinevi"]
    yayinevleri = [cmb.itemText(i) for i in range(cmb.count())]
    assert "Adam yayınları" not in yayinevleri       # diğer listeler de yenilendi


def test_isareti_kaldirilan_yazim_degismez_ve_ozel_yazim(lib, db):
    e = lib.duzeltme
    alan_sec(e, "Ceviren")
    grup = e.agac.topLevelItem(0)
    grup.child(0).setCheckState(0, Qt.Unchecked)     # "Sebahattin EYÜBOĞLU" dokunulmasın
    e.hedef.setText("Sabahattin EYÜBOĞLU")
    e.birlestir()
    sayim = dict(db.execute("SELECT Ceviren, COUNT(*) FROM kayitlistesi WHERE Ceviren LIKE 'Sa%' "
                            "OR Ceviren LIKE 'Se%' GROUP BY Ceviren").fetchall())
    assert sayim == {"Sebahattin EYÜBOĞLU": 2, "Sabahattin EYÜBOĞLU": 1}


def test_birlestirilecek_bir_sey_yoksa_buton_pasif(lib):
    e = lib.duzeltme
    alan_sec(e, "Yayinevi")
    grup = e.agac.topLevelItem(0)
    grup.child(1).setCheckState(0, Qt.Unchecked)     # sadece hedefle aynı yazım işaretli kaldı
    assert not e.btn_birlestir.isEnabled()
    e.hedef.clear()
    assert not e.btn_birlestir.isEnabled()


def test_yoksay_butonu(lib):
    e = lib.duzeltme
    alan_sec(e, "Ceviren")
    e.yoksay()
    assert e.agac.topLevelItemCount() == 0
    e.yenile()
    assert e.agac.topLevelItemCount() == 0


def test_eksik_kitaba_cift_tiklama_duzenlemede_acar(lib):
    e = lib.duzeltme
    e.eksik_ac(0)
    q = lib
    assert q.alt_sekmeler[q.kayit].currentWidget() is lib.kitaplar and lib.kitaplar.alan["Adi"].text() == "Kuyucaklı Yusuf"
