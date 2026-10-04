## Filtre sekmesi: dört ölçüt tek panelde ##
import pytest

from conftest import sec
from acodes.guest import Guest
from acodes.library import Library
from database.kitaplar import filtre_secenekleri, kitap_filtrele


def adlar(tablo):
    return [tablo.item(r, 1).text() for r in range(tablo.rowCount())]


# --- Sorgu ---

def test_ayni_olcutte_veya_farkli_olcutte_ve():
    assert len(kitap_filtrele({"Turu": ["Roman", "Deneme"]})) == 7
    sonuc = kitap_filtrele({"Turu": ["Roman", "Deneme"], "Yayinevi": ["İthaki Yayınları", "Cem Yayınevi"]})
    assert [s[1] for s in sonuc] == ["Denemeler", "Esir Şehrin İnsanları", "Yol Ayrımı"]   # Türk alfabesiyle sıralı
    assert kitap_filtrele({"Turu": ["Anı"], "Yili": ["2005"]}) == []


def test_metinle_arama_turkce_karakter_farksiz(db):
    db.execute("INSERT INTO kayitlistesi (Adi,Turu,Yazari) VALUES ('Şiirler','Şiir','Nazım HİKMET'),"
               " ('Kuşlar','şiir','Cahit KÜLEBİ')")
    db.commit()
    assert [s[1] for s in kitap_filtrele({"Turu": "siir"})] == ["Kuşlar", "Şiirler"]    # yazım farkı olsa da
    assert [s[1] for s in kitap_filtrele({"Turu": "şiir", "Yazari": "hikmet"})] == ["Şiirler"]
    assert kitap_filtrele({"Turu": "   "}) == []


def test_secenekler_diger_olcutlere_gore_daralir(db):
    db.execute("INSERT INTO kayitlistesi (Adi,Turu,Yazari,Yili) VALUES ('Şiirler','Şiir','Nazım HİKMET','1990')")
    db.commit()
    s = filtre_secenekleri({"Turu": "şiir", "Yazari": []}, ["Turu", "Yazari", "Yili"])
    assert s["Yazari"] == ["Nazım HİKMET"] and s["Yili"] == ["1990"]
    assert "Roman" in s["Turu"]                      # kendi ölçütü kendini daraltmaz (başka tür de eklenebilir)
    tum = filtre_secenekleri({}, ["Turu"])["Turu"]
    assert tum == ["Anı", "Deneme", "Roman", "Şiir"]


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
    assert not hasattr(q, "tabWidget_4")
    assert f"{lib.filtre.parentWidget().objectName()}" == "tab_4"


def test_secim_yapinca_sonuclar_kendiliginden_gelir(f):
    assert f.tablo.rowCount() == 0 and f.sonuc.text() == ""
    assert "yazın veya listeden seçin" in f.tablo.bos_durum.etiket.text()
    sec(f.combo["Turu"], "Roman")
    assert f.secimler["Turu"] == ["Roman"] and f.tablo.rowCount() == 6 and f.sonuc.text() == "6 kitap bulundu"
    assert f.combo["Turu"].currentIndex() == -1 and f.combo["Turu"].currentText() == ""   # kutu boşalır
    sec(f.combo["Turu"], "Deneme")
    assert f.tablo.rowCount() == 7 and f.kutu["Turu"].title() == "Tür (2)"
    assert etiketler(f, "Turu") == ["Deneme  ✕", "Roman  ✕"]


def test_olcutler_birlikte_daraltir(f):
    sec(f.combo["Turu"], "Roman")
    sec(f.combo["Yazari"], "Kemal TAHİR")
    sec(f.combo["Yazari"], "Stefan ZWEIG")
    sec(f.combo["Yili"], "2005")
    assert adlar(f.tablo) == ["Esir Şehrin İnsanları", "Yol Ayrımı"]


def test_yazinca_arama_gibi_suzer_ve_diger_listeler_daralir(f, db):
    db.execute("INSERT INTO kayitlistesi (Adi,Turu,Yazari,Yayinevi,Yili) VALUES "
               "('Şiirler','Şiir','Nazım HİKMET','YKY','1990'), ('Kuşlar','şiir','Cahit KÜLEBİ','Can','1995')")
    db.commit()
    f.yenile()
    f.combo["Turu"].setEditText("şiir")                 # listeden seçmeden yazıldı
    assert adlar(f.tablo) == ["Kuşlar", "Şiirler"] and f.sonuc.text() == "2 kitap bulundu"
    yazarlar = [f.combo["Yazari"].itemText(i) for i in range(f.combo["Yazari"].count())]
    assert yazarlar == ["Cahit KÜLEBİ", "Nazım HİKMET"]  # sadece türü şiir olan kitapların yazarları
    assert f.combo["Yili"].count() == 2 and f.btn_temizle.isEnabled()
    sec(f.combo["Yazari"], "Nazım HİKMET")
    assert adlar(f.tablo) == ["Şiirler"]
    assert f.combo["Turu"].currentText() == "şiir"     # yazılan metin listeler yenilenirken silinmez
    f.combo["Turu"].setEditText("")                     # tür araması silindi, yazar seçimi kaldı
    assert [f.combo["Turu"].itemText(i) for i in range(f.combo["Turu"].count())] == ["Şiir"]


def test_uyan_kitap_yoksa_yonlendirir(f):
    f.combo["Yazari"].setEditText("olmayan yazar")
    assert f.tablo.rowCount() == 0 and f.sonuc.text() == "0 kitap bulundu"
    assert "kaldırmayı" in f.tablo.bos_durum.etiket.text()
    assert f.combo["Turu"].count() == 0                 # uyan kitap yoksa seçenek de yok


def test_secilen_tur_diger_listeleri_daraltir(f):
    sec(f.combo["Turu"], "Anı")
    assert [f.combo["Yili"].itemText(i) for i in range(f.combo["Yili"].count())] == ["2020"]
    assert f.combo["Turu"].findText("Roman") >= 0     # aynı ölçütte başka tür eklenebilir


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
    f.combo["Yazari"].setEditText("maurois")
    assert f.tablo.rowCount() == 2
    f.temizle()
    assert all(not v for v in f.secimler.values()) and f.tablo.rowCount() == 0
    assert f.combo["Yazari"].currentText() == "" and f.combo["Yazari"].count() == 6
    assert etiketler(f, "Turu") == [] and f.kutu["Turu"].title() == "Tür"
    assert lib.QtLibrary.statusbar.currentMessage() == "Filtre temizlendi."


def test_yenilemede_secimler_korunur_yeni_degerler_eklenir(lib, f, db):
    sec(f.combo["Turu"], "Roman")
    db.execute("INSERT INTO kayitlistesi (Adi,Turu) VALUES ('Yeni','Roman'), ('Şiirler','Şiir')")
    db.commit()
    lib.yenile()
    assert f.secimler["Turu"] == ["Roman"] and f.tablo.rowCount() == 7
    assert f.combo["Turu"].findText("Şiir") >= 0


def test_guest_panelinde_de_var(app, uyarilar):
    g = Guest()
    sec(g.filtre.combo["Yayinevi"], "YKY")
    assert adlar(g.filtre.tablo) == ["Kuyucaklı Yusuf"]


def test_olcutler_ustte_yan_yana_sonuclar_altta(app, uyarilar):
    from PyQt5.QtWidgets import QApplication
    from acodes.library import Library
    lib = Library()
    lib.resize(1300, 800)
    lib.show()
    lib.QtLibrary.tabWidget.setCurrentWidget(lib.QtLibrary.tab_4)
    QApplication.processEvents()
    f = lib.filtre
    ustler = {f.kutu[k].mapTo(f, f.kutu[k].rect().topLeft()).y() for k in f.kutu}
    assert len(ustler) == 1                                              # dört ölçüt aynı satırda
    assert f.tablo.mapTo(f, f.tablo.rect().topLeft()).y() > max(ustler) + 40
    assert f.tablo.width() > f.width() - 60 and f.tablo.isColumnHidden(0)  # tam genişlik, Kayıt No gizli
    lib.close()
