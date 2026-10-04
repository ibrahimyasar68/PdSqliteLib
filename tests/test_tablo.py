## Tablolarda sıralama, salt okunur hücreler ve çift tıklama testleri ##

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QHeaderView, QTableWidget

from conftest import sec
from acodes import tema
from acodes.guest import Guest
from acodes.kullanici_yonetimi import KullaniciYonetimi
from acodes.library import Library
from acodes.tablo import SATIR_BOY, siralama_anahtari, tablo_ayarla, tabloya_yaz
from database.dbframe import df_sort_list, tr_sirala


def kolon(tablo, c):
    return [tablo.item(r, c).text() for r in range(tablo.rowCount())]


# --- Sıralama anahtarı ---

def test_turk_alfabesi_sirasi():
    kelimeler = ["Zeytin", "Şiir", "Çanlar", "İklimler", "ırmak", "Ödev", "Cam", "Ilgaz", "sabah", "Üzüm", "Ukala"]
    assert sorted(kelimeler, key=tr_sirala) == \
        ["Cam", "Çanlar", "Ilgaz", "ırmak", "İklimler", "Ödev", "sabah", "Şiir", "Ukala", "Üzüm", "Zeytin"]


def test_filtre_listeleri_turk_alfabesiyle_sirali(db):
    db.execute("INSERT INTO kayitlistesi (Adi,Turu) VALUES ('x','Şiir'), ('y','Çocuk'), ('z','Tarih')")
    db.commit()
    assert df_sort_list("Turu") == ["Anı", "Çocuk", "Deneme", "Roman", "Şiir", "Tarih"]


@pytest.mark.parametrize("kucuk,buyuk", [
    ("9", "10"),                    # sayılar sayı olarak
    ("31.12.2025", "01.01.2026"),   # tarihler tarih olarak
    ("Cam", "Çam"),                 # Türk alfabesi
    ("10", "01.01.2020"),           # sayı < tarih < metin < boş
    ("01.01.2020", "abc"),
    ("abc", ""),
])
def test_siralama_anahtari(kucuk, buyuk):
    assert siralama_anahtari(kucuk) < siralama_anahtari(buyuk)


# --- Tablo davranışı ---

def test_basliga_tiklayinca_siralanir_ve_veri_satirla_tasinir(app):
    t = QTableWidget(0, 2)
    tablo_ayarla(t)
    tabloya_yaz(t, [["b", "10"], ["a", "9"], ["c", "100"]], vurgulu={0}, veri=["B", "A", "C"])
    assert kolon(t, 0) == ["b", "a", "c"]           # ilk açılışta veri geldiği sırada
    t.sortItems(1, Qt.AscendingOrder)
    assert kolon(t, 1) == ["9", "10", "100"]
    assert [t.item(r, 0).data(Qt.UserRole) for r in range(3)] == ["A", "B", "C"]
    assert t.item(1, 1).background().color() == QColor(tema.GECIKME_ARKA)   # "b" satırı hâlâ vurgulu
    tabloya_yaz(t, [["z", "2"], ["y", "1"]])        # yenilemede seçilen sıralama korunur
    assert kolon(t, 1) == ["1", "2"]


def test_tablolar_salt_okunur_ve_siralanabilir(app, uyarilar):
    lib = Library()
    q = lib.QtLibrary
    for t in (q.tableWidget_2, lib.filtre.tablo, q.tableWidget_5_1_1, lib.odunc.tablo, lib.gecmis.tablo):
        assert t.isSortingEnabled()
        assert t.editTriggers() == QAbstractItemView.NoEditTriggers
    g = Guest()
    assert g.QtLibrary.tableWidget_2.isSortingEnabled()


def test_kitap_listesi_yila_gore_siralanir(app, uyarilar):
    lib = Library()
    t = lib.QtLibrary.tableWidget_2
    lib.listele()
    t.sortItems(6, Qt.AscendingOrder)
    yillar = kolon(t, 6)
    assert yillar[0] == "1983" and yillar[-1] == ""   # boş yıl en sonda


# --- Çift tıklama ---

@pytest.fixture
def lib(app, uyarilar):
    return Library()


def test_listeden_cift_tiklama_kitabi_duzenlemede_acar(lib):
    q = lib.QtLibrary
    lib.arama.setText("şaheser")                   # İklimler'in ikinci baskısı (Id 4)
    lib.tablodan_kitap_duzenle(q.tableWidget_2, 0)
    k = lib.kitaplar
    assert q.tabWidget.currentWidget() is q.tab_3 and q.tabWidget_3.currentWidget() is k
    assert k.kitap_id == 4 and k.alan["Yayinevi"].text() == "Şaheser Romanlar"
    assert k.btn_sil.isEnabled() and k.form_baslik.text() == "Kitap #4"


def test_filtreden_cift_tiklama(lib):
    sec(lib.filtre.combo["Yazari"], "Stefan ZWEIG")
    lib.tablodan_kitap_duzenle(lib.filtre.tablo, 0)
    assert lib.kitaplar.alan["Adi"].text() == "Satranç"


def test_bos_satira_cift_tiklama_bir_sey_yapmaz(lib):
    q = lib.QtLibrary
    lib.tablodan_kitap_duzenle(q.tableWidget_2, 0)  # liste henüz boş
    assert q.tabWidget.currentWidget() is q.tab_1


def test_kullanici_tablosu_siralaninca_dogru_kullanici_secilir(app, uyarilar):
    y = KullaniciYonetimi("admin")
    y.tablo.sortItems(0, Qt.DescendingOrder)
    y.sec("ayse1")
    assert y.secili()[1] == "ayse1"
    y.tablo.selectRow(0)
    assert y.secili()[1] == y.tablo.item(0, 0).text()


# --- Görünüm: satır renkleri, satır numarası, boş tablo mesajı ---

def test_tablo_gorunumu(app):
    t = QTableWidget(0, 2)
    tablo_ayarla(t)
    assert not t.verticalHeader().isHidden()                                  # sıra numarası görünür
    assert not t.alternatingRowColors() and not t.showGrid()                  # satırlar yalnızca ince çizgiyle ayrılır
    assert t.verticalHeader().defaultSectionSize() == SATIR_BOY
    assert t.verticalHeader().highlightSections()                             # seçili satırda vurgu çizgisi
    t2 = QTableWidget(0, 2)
    tablo_ayarla(t2, sira_no=False)
    assert t2.verticalHeader().isHidden()
    assert t.horizontalHeader().stretchLastSection()
    tabloya_yaz(t, [["Kitap", "42"]])
    assert t.item(0, 1).textAlignment() & Qt.AlignRight          # sayılar sağa yaslı
    assert not t.item(0, 0).textAlignment() & Qt.AlignRight


def test_bos_tablo_mesaji(app):
    t = QTableWidget(1, 2)
    tablo_ayarla(t, bos_metin="Henüz kayıt yok")
    etiket = t.bos_durum.etiket
    assert etiket.text() == "Henüz kayıt yok" and not etiket.isHidden()
    tabloya_yaz(t, [["a", "1"], ["b", "2"]])
    app.processEvents()                                              # doldurma bitince bir kez kontrol edilir
    assert etiket.isHidden()
    t.clear()
    t.setRowCount(1)
    app.processEvents()
    assert not etiket.isHidden()


def test_panellerde_bos_tablo_mesajlari(lib, app):
    q = lib.QtLibrary
    lib.arama.setText("tahir")
    app.processEvents()
    assert q.tableWidget_2.bos_durum.etiket.isHidden()
    lib.arama.setText("olmayan kitap")
    app.processEvents()
    assert q.tableWidget_2.bos_durum.etiket.text() == "Aramanıza uyan kitap yok."
    assert not q.tableWidget_2.bos_durum.etiket.isHidden()
    assert lib.odunc.tablo.bos_durum.etiket.text() == "Şu an dışarıda kitap yok."


def test_icerige_gore_kolonlu_buyuk_tablo_hizli_dolar(app):
    # Eskiden her hücrede kolon genişliği baştan ölçülüyordu: 737 kitaplık liste ~18 sn sürüyordu
    import time
    t = QTableWidget(0, 6)
    tablo_ayarla(t)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    t.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
    t.resize(900, 500)
    t.show()
    satirlar = [[i, f"Kitap {i}", "Yazar", "Yayınevi", 1990 + i % 30, 1] for i in range(1500)]
    bas = time.time()
    tabloya_yaz(t, satirlar)
    assert time.time() - bas < 3
    modlar = [t.horizontalHeader().sectionResizeMode(c) for c in range(6)]
    assert modlar[1] == QHeaderView.Stretch and modlar[0] == modlar[5] == QHeaderView.ResizeToContents
    assert t.columnWidth(0) >= t.fontMetrics().horizontalAdvance("1499")    # sonunda içeriğe göre ölçüldü
    t.close()


def sira_numaralari(t):
    return [t.model().headerData(r, Qt.Vertical) for r in range(t.rowCount())]


def test_listelerde_sira_numarasi(app, uyarilar):
    lib = Library()
    q = lib.QtLibrary
    q.tabWidget.setCurrentWidget(q.tab_2)
    t = q.tableWidget_2
    assert not t.verticalHeader().isHidden() and sira_numaralari(t) == list(range(1, 9))   # son numara = kayıt sayısı
    t.sortItems(0, Qt.DescendingOrder)                  # kayıt numarası tersine: sıra numarası yine 1'den
    assert kolon(t, 0)[0] == "8" and sira_numaralari(t) == list(range(1, 9))
    lib.arama.setText("tahir")
    assert sira_numaralari(t) == [1, 2]
    for tablo in (lib.kitaplar.tablo, lib.filtre.tablo, lib.odunc.tablo, lib.gecmis.tablo, q.tableWidget_5_1_1):
        assert not tablo.verticalHeader().isHidden()


def test_bos_listede_sira_numarasi_yok(app, uyarilar):
    lib = Library()
    assert lib.QtLibrary.tableWidget_2.rowCount() == 0      # sekme açılmadan boş satır ("1") görünmez


def test_istatistik_cizelgeleri_kartlarda_ve_sayilar_sigar(app, uyarilar):
    from PyQt5.QtWidgets import QGroupBox
    lib = Library()
    q = lib.QtLibrary
    t = q.tableWidget_5_1_2
    assert isinstance(t.parentWidget(), QGroupBox) and t.parentWidget().title() == "Yazarlara göre"
    assert not hasattr(q, "label_56") and t.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert t.horizontalHeader().sectionResizeMode(1) == QHeaderView.Fixed and t.columnWidth(1) == 170
    from acodes.tablo import OranCubugu
    assert isinstance(t.itemDelegateForColumn(1), OranCubugu)                 # adette oran çubuğu


def test_durum_kolonu_rozet_ve_bos_tabloda_eylem(app, uyarilar):
    from acodes.tablo import DurumRozeti
    lib = Library()
    q = lib.QtLibrary
    t = q.tableWidget_2
    assert isinstance(t.itemDelegateForColumn(t.columnCount() - 1), DurumRozeti)
    assert isinstance(lib.filtre.tablo.itemDelegateForColumn(8), DurumRozeti)
    assert isinstance(lib.kitaplar.tablo.itemDelegateForColumn(6), DurumRozeti)
    lib.arama.setText("bulunmayan kitap")
    bos = t.bos_durum
    QApplication.processEvents()
    assert not bos.etiket.isHidden() and bos.buton.text() == "Aramayı Temizle"
    bos.buton.click()
    assert lib.arama.text() == "" and t.rowCount() == 8


def test_kitap_adi_kolonu_turden_genis(app, uyarilar):
    lib = Library()
    q = lib.QtLibrary
    lib.resize(1300, 800)
    lib.show()
    q.tabWidget.setCurrentWidget(q.tab_2)
    from PyQt5.QtTest import QTest
    QTest.qWait(50)                                         # genişlikler liste dolduktan sonra dağıtılır
    t = q.tableWidget_2
    assert t.columnWidth(1) > t.columnWidth(4) and t.columnWidth(1) > t.columnWidth(2)   # Adı > Türü, Yazarı
    assert t.horizontalScrollBar().maximum() == 0 and not t.wordWrap()
    lib.close()
