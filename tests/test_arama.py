## Kitap listesi arama testleri ##
import pytest

from acodes.guest import Guest
from acodes.library import Library
from database.kitaplar import kitap_ara
from database.metin import katla


@pytest.mark.parametrize("girdi,beklenen", [
    ("İklimler", "iklimler"), ("ŞAHİN", "sahin"), ("Işık", "isik"), ("Güneş Çiçeği", "gunes cicegi"),
    (None, ""),
])
def test_katla(girdi, beklenen):
    assert katla(girdi) == beklenen


@pytest.mark.parametrize("sorgu,sayi", [
    ("iklimler", 2),
    ("IKLIMLER", 2),
    ("kemal tahir", 2),          # kelimeler aynı alanda
    ("tahir yol", 1),            # kelimeler farklı alanlarda (yazar + ad)
    ("kuyucakli sabahattin", 1), # Türkçe karakter yazmadan
    ("o'brien", 1),              # tırnak işareti
    ("ithaki", 2),               # yayınevi
    ("2005", 2),                 # yıl
    ("cemal", 1),                # çevirmen
    ("", 8),                     # boş arama: hepsi
    ("böyle bir kitap yok", 0),
])
def test_kitap_ara(sorgu, sayi):
    assert len(kitap_ara(sorgu)) == sayi


@pytest.mark.parametrize("panel", [Library, Guest])
def test_arama_kutusu(app, uyarilar, panel):
    p = panel()
    tablo = p.liste.tablo
    p.liste.arama.setText("tahir")               # yazdıkça liste güncellenir
    assert tablo.rowCount() == 2 and p.liste.sonuc.text() == "2 kitap bulundu"
    assert {tablo.item(r, 1).text() for r in range(2)} == {"Yol Ayrımı", "Esir Şehrin İnsanları"}
    p.liste.arama.clear()
    assert tablo.rowCount() == 8 and p.liste.sonuc.text() == "Toplam 8 kitap"
    p.liste.arama.setText("iklimler")
    p.liste.temizle()                            # arama temizlenince tüm kitaplar
    assert p.liste.arama.text() == "" and tablo.rowCount() == 8 and p.liste.sonuc.text() == "Toplam 8 kitap"


@pytest.mark.parametrize("panel", [Library, Guest])
def test_sekmeye_gelince_kendiliginden_listelenir(app, uyarilar, db, panel):
    p = panel()
    q = p
    assert not hasattr(q, "pushButton_2_listele")
    q.sekmeler.setCurrentWidget(q.liste)
    assert q.liste.tablo.rowCount() == 8 and p.liste.sonuc.text() == "Toplam 8 kitap"
    db.execute("INSERT INTO kayitlistesi (Adi) VALUES ('Yeni')")
    db.commit()
    q.sekmeler.setCurrentWidget(q.ana_sayfa)
    q.sekmeler.setCurrentWidget(q.liste)   # her gelişte güncel
    assert q.liste.tablo.rowCount() == 9


def test_listele_butonu_aramayi_dikkate_alir(app, uyarilar):
    p = Library()
    p.liste.arama.blockSignals(True)
    p.liste.arama.setText("zweig")
    p.liste.arama.blockSignals(False)
    p.liste.listele()
    assert p.liste.tablo.rowCount() == 1 and p.liste.tablo.item(0, 1).text() == "Satranç"
