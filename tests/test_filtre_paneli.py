## Filtre sekmesi: dört ölçüt tek panelde ##
import pytest

from conftest import sec
from acodes.guest import Guest
from acodes.library import Library
from database.dbframe import kitap_filtrele


def adlar(tablo):
    return [tablo.item(r, 1).text() for r in range(tablo.rowCount())]


# --- Sorgu ---

def test_ayni_olcutte_veya_farkli_olcutte_ve():
    assert len(kitap_filtrele({"Turu": ["Roman", "Deneme"]})) == 7
    sonuc = kitap_filtrele({"Turu": ["Roman", "Deneme"], "Yayinevi": ["İthaki Yayınları", "Cem Yayınevi"]})
    assert [s[1] for s in sonuc] == ["Denemeler", "Esir Şehrin İnsanları", "Yol Ayrımı"]   # Türk alfabesiyle sıralı
    assert kitap_filtrele({"Turu": ["Anı"], "Yili": ["2005"]}) == []


def test_secim_yoksa_bos_ve_gecersiz_kolon_reddedilir():
    assert kitap_filtrele({"Turu": [], "Yazari": []}) == []
    with pytest.raises(ValueError):
        kitap_filtrele({"Adi) OR (1=1": ["x"]})


# --- Panel ---

@pytest.fixture
def lib(app, uyarilar):
    return Library()


@pytest.fixture
def f(lib):
    return lib.filtre


def etiketler(f, kolon):
    duzen = f.etiketler[kolon].layout()
    return [duzen.itemAt(i).widget().text() for i in range(duzen.count())]


def test_eski_alt_sekmeler_yok(lib):
    q = lib.QtLibrary
    assert q.tab_4.findChild(type(q.tabWidget_3), "tabWidget_4") is None
    assert f"{lib.filtre.parentWidget().objectName()}" == "tab_4"


def test_secim_yapinca_sonuclar_kendiliginden_gelir(f):
    assert f.tablo.rowCount() == 0 and f.sonuc.text() == ""
    assert "ölçütlerden" in f.tablo.bos_durum.etiket.text()
    sec(f.combo["Turu"], "Roman")
    assert f.secimler["Turu"] == ["Roman"] and f.tablo.rowCount() == 6 and f.sonuc.text() == "6 kitap bulundu"
    assert f.combo["Turu"].currentIndex() == 0            # liste bir sonraki seçim için başa döner
    sec(f.combo["Turu"], "Deneme")
    assert f.tablo.rowCount() == 7 and f.kutu["Turu"].title() == "Tür (2)"
    assert etiketler(f, "Turu") == ["Deneme  ✕", "Roman  ✕"]


def test_olcutler_birlikte_daraltir(f):
    sec(f.combo["Turu"], "Roman")
    sec(f.combo["Yazari"], "Kemal TAHİR")
    sec(f.combo["Yazari"], "Stefan ZWEIG")
    sec(f.combo["Yili"], "2005")
    assert adlar(f.tablo) == ["Esir Şehrin İnsanları", "Yol Ayrımı"]


def test_uyan_kitap_yoksa_yonlendirir(f):
    sec(f.combo["Turu"], "Anı")
    sec(f.combo["Yili"], "2005")
    assert f.tablo.rowCount() == 0 and f.sonuc.text() == "0 kitap bulundu"
    assert "kaldırmayı" in f.tablo.bos_durum.etiket.text()


def test_etikete_tiklayinca_secim_kalkar(f):
    sec(f.combo["Turu"], "Roman")
    sec(f.combo["Turu"], "Anı")
    duzen = f.etiketler["Turu"].layout()
    [etiket] = [duzen.itemAt(i).widget() for i in range(duzen.count()) if duzen.itemAt(i).widget().text().startswith("Anı")]
    etiket.click()
    assert f.secimler["Turu"] == ["Roman"] and f.tablo.rowCount() == 6 and f.kutu["Turu"].title() == "Tür (1)"


def test_ayni_deger_iki_kez_eklenmez(f):
    sec(f.combo["Yazari"], "O'brien")
    sec(f.combo["Yazari"], "O'brien")
    assert f.secimler["Yazari"] == ["O'brien"] and adlar(f.tablo) == ["Anne'nin Günlüğü"]


def test_temizle(f, uyarilar, lib):
    assert not f.btn_temizle.isEnabled()
    sec(f.combo["Turu"], "Roman")
    sec(f.combo["Yili"], "1992")
    f.temizle()
    assert all(not v for v in f.secimler.values()) and f.tablo.rowCount() == 0
    assert etiketler(f, "Turu") == [] and f.kutu["Turu"].title() == "Tür"
    assert lib.QtLibrary.statusbar.currentMessage() == "Filtre temizlendi."


def test_yenilemede_secimler_korunur_yeni_degerler_eklenir(lib, f, db):
    sec(f.combo["Turu"], "Roman")
    db.execute("INSERT INTO kayitlistesi (Adi,Turu) VALUES ('Yeni','Roman'), ('Şiirler','Şiir')")
    db.commit()
    lib.yenile()
    assert f.secimler["Turu"] == ["Roman"] and f.tablo.rowCount() == 7
    assert f.combo["Turu"].findText("Şiir") > 0


def test_guest_panelinde_de_var(app, uyarilar):
    g = Guest()
    sec(g.filtre.combo["Yayinevi"], "YKY")
    assert adlar(g.filtre.tablo) == ["Kuyucaklı Yusuf"]
