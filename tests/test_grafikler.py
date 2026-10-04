## İstatistik > Grafikler testleri ##
from acodes.grafikler import (DikeyCubukGrafik, GrafikPaneli, PastaGrafik, YatayCubukGrafik,
                              tur_dagilimi)
from acodes.guest import Guest
from acodes.library import Library
from database.istatistik import yil_dagilimi


def test_yil_dagilimi_turkce_eklerle():
    # Örnek veride yıllar: 2005, 2005, 1992, 1985, 2020, 2018, (boş), 1983
    assert yil_dagilimi() == [("1980'ler", 2), ("1990'lar", 1), ("2000'ler", 2),
                              ("2010'lar", 1), ("2020'ler", 1)]


def test_tur_dagilimi_digeri_birlestirir(db):
    veri = tur_dagilimi()
    assert veri[0] == ("Roman", 6) and sorted(veri[1:]) == [("Anı", 1), ("Deneme", 1)]
    for i in range(10):
        db.execute("INSERT INTO kayitlistesi (Adi,Turu,Yili) VALUES (?,?,?)", (f"K{i}", f"Tür{i}", "2000"))
    db.commit()
    veri = tur_dagilimi()
    assert len(veri) == 8 and veri[-1][0] == "Diğer"
    assert sum(d for _, d in veri) == 18      # toplam kitap sayısı korunur


def test_bos_etiket_ve_sifir_deger():
    g = YatayCubukGrafik("Deneme")
    g.veri_ver([("", 3), ("A", 0), ("B", 2)])
    assert g.veri == [("(belirtilmemiş)", 3), ("B", 2)]


def test_grafikler_verisiz_ve_verili_cizilir(app):
    for sinif in (PastaGrafik, YatayCubukGrafik, DikeyCubukGrafik):
        g = sinif("Deneme")
        g.resize(400, 300)
        assert not g.grab().isNull()          # veri yokken "Gösterilecek veri yok"
        g.veri_ver([("A", 5), ("B", 3), ("C", 1)])
        assert not g.grab().isNull()


def test_panellerde_sabit_resim_yerine_grafik(app, uyarilar):
    for panel in (Library(), Guest()):
        q = panel
        assert not hasattr(q, "widget")                 # eski sabit resim kutusu .ui'dan kaldırıldı
        assert panel.istatistik.grafikler.parent() is q.istatistik.sekmeler.widget(1)
        assert panel.istatistik.grafikler.yazarlar.veri[:2] == [("Andre MAUROIS", 2), ("Kemal TAHİR", 2)]   # eşitlikte alfabetik
        assert panel.istatistik.grafikler.yillar.veri == yil_dagilimi()


def test_kitap_eklenince_grafik_guncellenir(app, uyarilar):
    lib = Library()
    for alan, deger in [("Adi", "yeni kitap"), ("Yazari", "yeni yazar"), ("Turu", "Şiir"), ("Yili", "1975")]:
        lib.kitaplar.alan[alan].setText(deger)
    lib.kitaplar.kaydet()
    assert ("Şiir", 1) in lib.istatistik.grafikler.turler.veri
    assert ("1970'ler", 1) in lib.istatistik.grafikler.yillar.veri


def test_panel_tek_basina_kullanilabilir(app):
    p = GrafikPaneli()
    p.yenile()
    p.resize(900, 600)
    assert p.turler.veri and not p.grab().isNull()


def test_en_cok_yazar_grafiginde_bos_yazar_yok(app, uyarilar, db):
    db.executemany("INSERT INTO kayitlistesi (Adi, Yazari) VALUES (?, '')", [("a",), ("b",), ("c",)])
    db.commit()
    lib = Library()
    assert all(ad != "(belirtilmemiş)" for ad, _ in lib.istatistik.grafikler.yazarlar.veri)
