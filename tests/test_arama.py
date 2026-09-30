## Kitap listesi arama testleri ##
import pytest

from acodes.guest import Guest
from acodes.library import Library
from database.dbframe import katla, kitap_ara


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
    tablo = p.QtLibrary.tableWidget_2
    p.arama.setText("tahir")               # yazdıkça liste güncellenir
    assert tablo.rowCount() == 2 and p.arama_sonuc.text() == "2 kitap bulundu"
    assert {tablo.item(r, 1).text() for r in range(2)} == {"Yol Ayrımı", "Esir Şehrin İnsanları"}
    p.arama.clear()
    assert tablo.rowCount() == 8 and p.arama_sonuc.text() == "Toplam 8 kitap"
    p.arama.setText("iklimler")
    p.temizle()                            # arama temizlenince tüm kitaplar
    assert p.arama.text() == "" and tablo.rowCount() == 8 and p.arama_sonuc.text() == "Toplam 8 kitap"


@pytest.mark.parametrize("panel", [Library, Guest])
def test_sekmeye_gelince_kendiliginden_listelenir(app, uyarilar, db, panel):
    p = panel()
    q = p.QtLibrary
    assert q.pushButton_2_listele.isHidden()
    q.tabWidget.setCurrentWidget(q.tab_2)
    assert q.tableWidget_2.rowCount() == 8 and p.arama_sonuc.text() == "Toplam 8 kitap"
    db.execute("INSERT INTO kayitlistesi (Adi) VALUES ('Yeni')")
    db.commit()
    q.tabWidget.setCurrentWidget(q.tab_1)
    q.tabWidget.setCurrentWidget(q.tab_2)   # her gelişte güncel
    assert q.tableWidget_2.rowCount() == 9


def test_listele_butonu_aramayi_dikkate_alir(app, uyarilar):
    p = Library()
    p.arama.blockSignals(True)
    p.arama.setText("zweig")
    p.arama.blockSignals(False)
    p.listele()
    assert p.QtLibrary.tableWidget_2.rowCount() == 1 and p.QtLibrary.tableWidget_2.item(0, 1).text() == "Satranç"
