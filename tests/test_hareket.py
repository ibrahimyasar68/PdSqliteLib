## Geçiş animasyonları: satır parlaması ve "Hareketi azalt" ##
import pytest
from PySide6.QtCore import QAbstractAnimation, Qt
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtTest import QTest

from conftest import sec
from acodes import hareket, tema, tercihler
from acodes.library import Library

CALISIYOR, DURDU = QAbstractAnimation.Running, QAbstractAnimation.Stopped


@pytest.fixture
def animasyonlu(monkeypatch):
    monkeypatch.setattr(hareket, "ANIMASYON", True)
    monkeypatch.setattr(hareket, "AZALT", False)


@pytest.fixture
def lib(app, uyarilar, animasyonlu):
    l = Library()
    l.resize(1300, 800)
    l.show()
    yield l
    l.close()


def secili_satir(tablo):
    return tablo.selectionModel().selectedRows()[0].row()


def test_kaydedilen_kitap_satiri_parlar_ve_soner(lib):
    q = lib
    q.sekmeler.setCurrentWidget(q.kayit)
    q.alt_sekmeler[q.kayit].setCurrentWidget(lib.kitaplar)
    k = lib.kitaplar
    k.yeni()
    k.alan["Adi"].setText("Parlayan Kitap")
    k.kaydet()
    parlama = k.tablo._parlama
    assert parlama is not None and parlama.indeks.row() == secili_satir(k.tablo)
    assert parlama.geometry() == k.tablo.viewport().rect()
    QTest.qWait(tema.SURE.parlama + 200)
    assert k.tablo._parlama is None                                     # bitince kendini kaldırır


def test_odunc_verilen_satir_parlar(lib):
    o = lib.odunc
    lib.disaridakileri_goster()
    sec(o.kitap, "Satranç")
    o.uye.setCurrentIndex(o.uye.findData(3))
    o.odunc_ver()
    assert o.tablo._parlama is not None and o.tablo.item(o.tablo._parlama.indeks.row(), 0).text() == "Satranç"


def test_yeni_parlama_eskisini_kaldirir(lib):
    tablo = lib.liste.tablo
    lib.sekmeler.setCurrentWidget(lib.liste)
    ilk = hareket.satiri_parlat(tablo, 0)
    ikinci = hareket.satiri_parlat(tablo, 1)
    assert ilk is not ikinci and tablo._parlama is ikinci
    assert hareket.satiri_parlat(tablo, tablo.rowCount()) is None       # olmayan satır


def test_animasyon_kapaliyken_parlama_yok(app, uyarilar):
    l = Library()
    l.show()
    assert hareket.satiri_parlat(l.liste.tablo, 0) is None  # testlerde ANIMASYON = False
    l.close()


def test_hareketi_azalt_ayari(lib, monkeypatch):
    kutu = lib.ayarlar.gorunum.hareket
    assert not kutu.isChecked()
    kutu.setChecked(True)
    assert hareket.AZALT and not hareket.izinli() and tercihler.mantiksal(hareket.TERCIH)
    sayfa = lib.liste
    lib.sekmeler.setCurrentWidget(sayfa)
    assert sayfa.graphicsEffect() is None                               # sayfa beklemeden görünür
    lib.yan_menu.btn_daralt.click()
    assert lib.yan_menu.width() == lib.yan_menu.minimumWidth()          # menü hemen daralır
    lib.yan_menu.btn_daralt.click()
    lib.statusBar().showMessage("Deneme silindi")
    lib.bildirim.kaybol()
    assert lib.bildirim.kutu.isHidden()                                 # bildirim solmadan kaybolur
    kutu.setChecked(False)
    assert not hareket.AZALT and not tercihler.mantiksal(hareket.TERCIH)


# --- 2. aşama: giriş, kartlar, grafikler, menü, hızlı arama, rozet, bildirim yığını ---

def test_yanlis_giriste_kart_sallanir_bos_alan_kirmizi(app, uyarilar, animasyonlu):
    from acodes.login import Login
    w = Login()
    w.show()
    q = w.QtLogin
    q.lineEdit_kullanci_adi.setText("admin")
    w.giris()                                                           # parola boş
    assert tema.TEHLIKE in q.lineEdit_parola.styleSheet()
    assert tema.TEHLIKE not in q.lineEdit_kullanci_adi.styleSheet()
    yer = w.kart.pos()
    q.lineEdit_parola.setText("yanlis")
    w.giris()
    assert w.kart._salla is not None
    QTest.qWait(tema.SURE.uzun + 150)
    assert w.kart._salla is None and w.kart.pos() == yer                 # yerine döner
    QTest.qWait(tema.SURE.parlama * 2)
    assert tema.TEHLIKE not in q.lineEdit_parola.styleSheet()           # çerçeve normale söner
    w.close()


def test_hatali_alan_vurgulanir(lib):
    q = lib
    q.sekmeler.setCurrentWidget(q.kayit)
    k = lib.kitaplar
    k.yeni()
    k.kaydet()                                                          # kitap adı boş
    assert tema.TEHLIKE in k.alan["Adi"].styleSheet()
    k.alan["Adi"].setText("ISBN'li")
    k.ek.isbn.setText("123")
    k.kaydet()
    assert tema.TEHLIKE in k.ek.isbn.styleSheet()


def test_hareket_azaltilinca_hata_yine_gorunur(app, uyarilar):
    from PySide6.QtWidgets import QLineEdit
    alan = QLineEdit()
    alan.setStyleSheet("QLineEdit { padding: 2px; }")
    hareket.hata_vurgula(alan)                                          # testlerde animasyon kapalı
    assert tema.TEHLIKE in alan.styleSheet()
    QTest.qWait(tema.SURE.parlama * 2 + 100)
    assert alan.styleSheet() == "QLineEdit { padding: 2px; }"


def test_ana_sayfa_sayilari_sayarak_gelir(lib):
    kart = lib.ana_sayfa.kartlar["kitap"]
    assert kart.sayildi and kart.sayi._sayac is not None
    QTest.qWait(tema.SURE.sayac + 150)
    assert kart.sayi.text() == "8" and kart.sayi._sayac is None
    lib.yenile()                                                        # sonraki yenilemelerde sayı hemen yazılır
    assert kart.sayi._sayac is None and kart.sayi.text() == "8"


def bitene_kadar_bekle(animasyon, sinir_ms=3000):
    """Sabit süre beklemek yük altında yetmeyebilir: animasyon durana kadar (en fazla sinir_ms) bekler."""
    for _ in range(sinir_ms // 20):
        if animasyon.state() == DURDU:
            return
        QTest.qWait(20)


def test_kart_golgesi_yumusakca_buyur(lib):
    from PySide6.QtCore import QEvent
    from PySide6.QtWidgets import QApplication
    a = lib.ana_sayfa
    kart = a.kartlar["kitap"]
    QTest.qWait(tema.SURE.adim * (len(a.kartlar) + len(a.listeler)) + tema.SURE.orta + 150)   # kartlar yerine otursun
    QApplication.sendEvent(kart, QEvent(QEvent.Enter))
    assert kart.golge.isEnabled() and kart.golge_animasyonu.state() == CALISIYOR
    bitene_kadar_bekle(kart.golge_animasyonu)
    assert kart.golge.blurRadius() == 22
    QApplication.sendEvent(kart, QEvent(QEvent.Leave))
    bitene_kadar_bekle(kart.golge_animasyonu)
    assert not kart.golge.isEnabled()


def test_grafikler_buyuyerek_cizilir(lib):
    q = lib
    q.sekmeler.setCurrentWidget(q.istatistik)
    q.istatistik.sekmeler.setCurrentIndex(1)
    g = lib.istatistik.grafikler.yazarlar
    assert g.ilerleme < 1 and g.animasyon.state() == CALISIYOR
    assert g.oran(0) >= g.oran(len(g.veri) - 1)                         # ilk çubuk önde
    QTest.qWait(tema.SURE.sayac + 150)
    assert g.ilerleme == 1.0 and all(g.oran(i) == 1.0 for i in range(len(g.veri)))
    lib.istatistik.grafikler.yenile()                                              # veri aynıysa yeniden çizilmez
    assert g.animasyon.state() == DURDU


def test_menu_vurgusu_kayarak_gider(lib):
    m = lib.yan_menu
    hedef = m.grup.button(3)
    hedef.click()
    vurgu = m.vurgu
    assert vurgu.animasyon.state() == CALISIYOR and vurgu.animasyon.endValue() == vurgu.hedef()
    QTest.qWait(tema.SURE.orta + 150)
    assert vurgu.cerceve.geometry() == vurgu.hedef() and vurgu.hedef().topLeft() == hedef.mapTo(m, hedef.rect().topLeft())
    m.btn_daralt.click()                                                # menü daralırken vurgu butonu izler
    QTest.qWait(tema.SURE.orta + 150)
    assert vurgu.cerceve.width() == hedef.width()
    m.btn_daralt.click()                                                # tercih kaydedilir: menüyü geri aç
    assert not tercihler.mantiksal("menu/kapali")


def test_segment_vurgusu_kayar(lib):
    from acodes.yan_menu import SegmentAnahtari
    q = lib
    q.sekmeler.setCurrentWidget(q.kayit)
    anahtar = q.kayit.findChild(SegmentAnahtari)
    QTest.qWait(50)
    anahtar.grup.button(1).click()
    assert anahtar.vurgu.animasyon.state() == CALISIYOR
    QTest.qWait(tema.SURE.orta + 150)
    assert anahtar.vurgu.cerceve.geometry() == anahtar.grup.button(1).geometry()


def test_hizli_arama_kayarak_acilir(lib):
    lib.palet.ac()
    ilk = lib.palet.pos()
    assert lib.palet.isVisible()
    QTest.qWait(tema.SURE.kisa + 100)
    assert lib.palet.pos().y() == ilk.y() - 8 and lib.palet.pos().x() == ilk.x()    # 8 piksel yukarı kayar
    lib.palet.close()


def test_gecikme_rozeti_bir_kez_atar(app, uyarilar, animasyonlu, db):
    import datetime
    eski = str(datetime.date.today() - datetime.timedelta(days=30))
    db.execute("INSERT INTO follow (userId, bookId, outdate, outtime, status, indate, intime) VALUES ('3','1',?,'10:00','out','','')", (eski,))
    db.commit()
    l = Library()
    l.show()
    QTest.qWait(20)
    rozet = [r for _, r in l.yan_menu.ogeler if r.isVisible()][0]
    assert rozet.graphicsEffect() is not None
    QTest.qWait(tema.SURE.uzun * 4 + 200)
    assert rozet.graphicsEffect() is None                               # sürekli atmaz
    l.close()


def test_geri_al_karti_yeni_mesajla_kaybolmaz(lib):
    from acodes import bildirim
    b = lib.bildirim
    cagri = []
    b.eylemli("'Deneme' silindi", "Geri Al", lambda: cagri.append(1))
    eski = b.son
    lib.statusBar().showMessage("Liste görüntülendi.")
    assert b.son is not eski and b.eskiler == [eski] and eski.kutu.isVisible()
    QTest.qWait(tema.SURE.orta + 100)
    assert eski.kutu.y() + eski.kutu.height() + bildirim.ARALIK == b.kutu.y()   # yeni kart altta, eski üstünde
    eski.eylem.click()                                                  # eski kartın Geri Al'ı hâlâ çalışır
    assert cagri == [1]
    QTest.qWait(tema.SURE.uzun + 150)
    assert b.eskiler == []
    lib.statusBar().showMessage("Başka bir mesaj.")             # eylemsiz kart yeniden kullanılır
    assert b.eskiler == []


def test_en_fazla_uc_kart(lib):
    from acodes import bildirim
    b = lib.bildirim
    for i in range(5):
        b.eylemli(f"'Kitap {i}' silindi", "Geri Al", lambda: None)
    QTest.qWait(tema.SURE.uzun + 150)
    assert len([k for k in b.kartlar() if k.kutu.isVisible()]) == bildirim.UST_USTE


# --- 3. aşama: alt bölüm kayması, arka plan geçişi, kılavuz, onay penceresi ---

def test_alt_bolum_secilen_yonden_kayarak_gelir(lib):
    sayfa = lib.kayit
    lib.sekmeler.setCurrentWidget(sayfa)
    alt = lib.alt_sekmeler[sayfa]
    QTest.qWait(tema.SURE.orta + 100)
    hedef = alt.widget(1)
    alt.setCurrentIndex(1)                                              # sağdaki bölüm: sağdan gelir
    yer = alt.widget(0).pos()
    assert hedef.graphicsEffect() is not None and hedef.x() > yer.x()
    QTest.qWait(tema.SURE.orta + 150)
    assert hedef.graphicsEffect() is None and hedef.pos() == yer        # yerine oturur, efekt kalkar
    alt.setCurrentIndex(0)                                              # soldaki bölüm: soldan gelir
    assert alt.widget(0).x() < yer.x()
    QTest.qWait(tema.SURE.orta + 150)


def test_giris_fotografi_solarak_gecer(lib):
    a = lib.arka_plan
    assert a.gorunurluk == 1.0
    lib.sekmeler.setCurrentWidget(lib.liste)
    assert a.gecis.state() == CALISIYOR                                 # birden kaybolmaz
    QTest.qWait(tema.SURE.orta + 150)
    assert a.gorunurluk == 0.0
    lib.sekmeler.setCurrentIndex(0)
    QTest.qWait(tema.SURE.orta + 150)
    assert a.gorunurluk == 1.0


def test_kilavuz_konusu_yukseklikle_acilir_ok_doner(lib):
    from acodes import kilavuz
    pencere = lib.ayarlar.kilavuz_penceresi
    pencere.show()
    k = lib.ayarlar.kilavuz
    _, buton, yazi = k.konular[1]
    buton.click()
    assert yazi.isVisible() and yazi._yukseklik_animasyonu is not None
    assert buton.donus.state() == CALISIYOR
    QTest.qWait(tema.SURE.orta + 150)
    assert yazi.height() > 0 and yazi.maximumHeight() == hareket.SINIRSIZ and buton.aci == kilavuz.ACIK_ACI
    k.konular[2][1].click()
    assert yazi.isVisible()                                             # önceki konu kapanarak gider
    QTest.qWait(tema.SURE.orta + 150)
    assert yazi.isHidden() and buton.aci == kilavuz.KAPALI_ACI and not k.konular[2][2].isHidden()
    pencere.close()


def test_onay_penceresi_buyuyerek_gelir_ve_cevap_doner(lib):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QMessageBox
    from acodes.onay import OnayPenceresi
    d = OnayPenceresi("Devam edilsin mi?", lib)
    goruldu = []

    def bak():
        goruldu.append((d.geometry() == lib.geometry(), d.resim is not None, 0 < d.guc < 1))
        QTimer.singleShot(tema.SURE.orta + 100, d.btn_evet.click)

    QTimer.singleShot(tema.SURE.orta // 3, bak)
    assert d.exec() == QMessageBox.Yes
    assert goruldu == [(True, True, True)]                              # paneli kaplar, kart büyürken çizilir


def test_tehlikeli_onayda_hayir_secili_esc_hayir(app, uyarilar):
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import QMessageBox
    from acodes.onay import OnayPenceresi
    d = OnayPenceresi("Silinsin mi?", tehlikeli=True)
    assert d.btn_hayir.isDefault() and not d.btn_evet.isDefault() and d.btn_evet.property("tehlikeli")
    QTimer.singleShot(50, lambda: QTest.keyClick(d, Qt.Key_Escape))
    assert d.exec() == QMessageBox.No                                   # testlerde animasyon kapalı: hemen kapanır


# --- 4. aşama: sayfa kayması, sayılar, etiketler, giriş, kartlar, grafikler, üstüne gelme, odak ---

def test_menu_sayfasi_asagidan_gelir(lib):
    sayfa = lib.filtre
    lib.sekmeler.setCurrentWidget(sayfa)                               # menüde aşağıda: aşağıdan gelir
    yer = lib.liste.pos()
    assert sayfa.graphicsEffect() is not None and sayfa.y() > yer.y() and sayfa.x() == yer.x()
    QTest.qWait(tema.SURE.orta + 150)
    assert sayfa.pos() == yer and sayfa.graphicsEffect() is None


def test_sonuc_sayisi_akarak_degisir(lib):
    l = lib.liste
    lib.sekmeler.setCurrentWidget(l)
    QTest.qWait(tema.SURE.orta + 100)
    hareket.sayi_yaz(l.sonuc, "8 kitap bulundu")                       # kalıp değişti: hemen
    assert l.sonuc.text() == "8 kitap bulundu"
    hareket.sayi_yaz(l.sonuc, "2 kitap bulundu")
    assert l.sonuc._sayac is not None and l.sonuc.text() == "8 kitap bulundu"
    QTest.qWait(tema.SURE.uzun + 150)
    assert l.sonuc.text() == "2 kitap bulundu" and l.sonuc._sayac is None
    hareket.sayi_yaz(l.sonuc, "")                                       # sayısız metin hemen yazılır
    assert l.sonuc.text() == ""


def test_filtre_etiketi_acilarak_gelir_daralarak_gider(lib):
    f = lib.filtre
    lib.sekmeler.setCurrentWidget(f)
    QTest.qWait(tema.SURE.orta + 100)
    f.ekle("Turu", "Roman")
    duzen = f.etiketler["Turu"].layout()
    [etiket] = [duzen.itemAt(i).widget() for i in range(duzen.count())]
    assert etiket.maximumWidth() < hareket.SINIRSIZ                     # sıfırdan açılıyor
    QTest.qWait(tema.SURE.orta + 150)
    assert etiket.maximumWidth() == hareket.SINIRSIZ and etiket.graphicsEffect() is None
    f.ekle("Turu", "Anı")
    QTest.qWait(tema.SURE.orta + 150)
    assert [duzen.itemAt(i).widget().deger for i in range(duzen.count())] == ["Anı", "Roman"]   # sırasına girer
    f.cikar("Turu", "Roman")
    assert duzen.count() == 2 and not etiket.isEnabled()               # daralarak gidiyor
    QTest.qWait(tema.SURE.kisa + 150)
    assert [duzen.itemAt(i).widget().deger for i in range(duzen.count())] == ["Anı"]
    f.cikar("Turu", "Anı")
    QTest.qWait(tema.SURE.kisa + 150)
    assert duzen.count() == 0 and f.etiketler["Turu"].isHidden()


def test_giris_formu_sirayla_gelir_ve_fotograf_gezinir(app, uyarilar, animasyonlu):
    from acodes.login import Login
    w = Login()
    w.show()
    QTest.qWait(30)
    efektli = [o for o in w._kart_ogeleri() if o.graphicsEffect() is not None]
    assert len(efektli) >= 3                                            # başlık, alanlar, buton sırada
    QTest.qWait(tema.SURE.adim * 10 + tema.SURE.orta + 150)
    assert all(o.graphicsEffect() is None for o in w._kart_ogeleri())
    f = w.fotograf
    assert f.zamanlayici.isActive() and 0 <= f.oran() <= 1
    hareket.AZALT = True
    assert f.oran() == 0                                                # hareketi azaltınca fotoğraf durur
    hareket.AZALT = False
    w.hide()
    assert not f.zamanlayici.isActive()
    w.close()


def test_dogru_giriste_buton_yesile_doner(app, uyarilar, monkeypatch):
    from acodes import login as login_modulu
    from acodes.login import Login
    from conftest import ADMIN_SIFRE
    w = Login()
    w.show()
    gorulen = []
    gercek = login_modulu.Login.panel_ac

    def panel_ac(self, *a, **k):
        b = self.QtLogin.pushButton_giris
        gorulen.append((b.text(), b.property("basari")))
        return gercek(self, *a, **k)

    monkeypatch.setattr(login_modulu.Login, "panel_ac", panel_ac)
    w.QtLogin.lineEdit_kullanci_adi.setText("admin")
    w.QtLogin.lineEdit_parola.setText(ADMIN_SIFRE)
    w.giris()
    assert gorulen == [("Giriş başarılı", True)]                       # panel kurulurken başarı görünür
    b = w.QtLogin.pushButton_giris
    assert b.text() == "Giriş" and not b.property("basari")             # sonra eski haline döner
    w.library.close()


def test_ana_sayfa_kartlari_sirayla_gelir(lib):
    a = lib.ana_sayfa
    kartlar = list(a.kartlar.values())
    assert a.geldi and any(isinstance(k.graphicsEffect(), QGraphicsOpacityEffect) for k in kartlar)
    QTest.qWait(tema.SURE.adim * (len(kartlar) + len(a.listeler)) + tema.SURE.orta + 150)
    assert all(k.golge is not None and k.graphicsEffect() is k.golge for k in kartlar)   # gölgeler geri gelir


def test_selamlama_ve_gecikme_karti():
    from acodes import ana_sayfa
    assert [ana_sayfa.selamlama(s) for s in (6, 12, 18, 23, 3)] == \
        ["Günaydın", "İyi günler", "İyi akşamlar", "İyi geceler", "İyi geceler"]
    kart = ana_sayfa.Kart("Geciken", tema.TEHLIKE)
    kart.ayarla(2, "teslim süresi geçmiş", parla=True)
    assert kart.property("parla") and kart.golge.isEnabled() and kart.golge_guc == kart.taban() > 0
    kart.ayarla(0, "", parla=False)
    assert not kart.property("parla") and not kart.golge.isEnabled()


def test_grafik_ustune_gelince_vurgulanir_veri_akarak_degisir(lib, db):
    from PySide6.QtCore import QEvent, QPointF
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtWidgets import QApplication
    lib.sekmeler.setCurrentWidget(lib.istatistik)
    lib.istatistik.sekmeler.setCurrentIndex(1)
    g = lib.istatistik.grafikler.yazarlar
    bitene_kadar_bekle(g.animasyon)
    alan = g.parcalar[1][1]
    QApplication.sendEvent(g, QMouseEvent(QEvent.MouseMove, alan.center(), g.mapToGlobal(alan.center()),
                                          Qt.NoButton, Qt.NoButton, Qt.NoModifier))
    assert g.uzerinde == 1 and g.guc(1) >= 0 and g.guc(0) == 0
    assert g.ipucu(1).startswith(g.veri[1][0] + ": ")
    bitene_kadar_bekle(g.vurgu_animasyonu)
    assert g.vurgu == 1.0
    once = dict(g.veri)
    db.execute("INSERT INTO kayitlistesi (Adi,Yazari) VALUES ('Yeni 1','MONTAIGNE'), ('Yeni 2','MONTAIGNE'),"
               " ('Yeni 3','MONTAIGNE')")
    db.commit()
    lib.istatistik.grafikler.yenile()
    assert g.akiyor() and g.oran(0) == 1.0                              # sıfırdan büyümez, akar
    assert g.deger_su_an(0) < 4 and g.veri[0] == ("MONTAIGNE", 4) and once["MONTAIGNE"] == 1
    bitene_kadar_bekle(g.animasyon)
    assert not g.akiyor() and g.deger_su_an(0) == 4


def test_buton_rengi_yumusakca_degisir(lib):
    from PySide6.QtCore import QEvent, QPointF
    from PySide6.QtGui import QEnterEvent
    from PySide6.QtWidgets import QApplication
    lib.sekmeler.setCurrentWidget(lib.liste)
    QTest.qWait(tema.SURE.orta + 100)
    b = lib.liste.btn_aktar                                             # ikincil buton
    assert b.property("yumusak")
    QApplication.sendEvent(b, QEnterEvent(QPointF(3, 3), QPointF(3, 3), QPointF(3, 3)))
    assert "background-color" in b.styleSheet()                         # geçiş sürerken kendi rengiyle
    QTest.qWait(tema.SURE.kisa + 150)
    assert b.styleSheet() == ""                                         # bitince QSS'teki :hover devralır
    assert hareket.uzerinde_renkleri(lib.yan_menu.btn_daralt) is None   # özel butonlar anında
    assert hareket.uzerinde_renkleri(b)[1]["background-color"].name().upper() == tema.YUZEY


def test_odaklanan_alanda_isik(lib):
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QFocusEvent
    from PySide6.QtWidgets import QApplication
    l = lib.liste
    lib.sekmeler.setCurrentWidget(l)
    QTest.qWait(tema.SURE.orta + 100)
    QApplication.sendEvent(l.arama, QFocusEvent(QEvent.FocusIn))
    isik = l.arama._odak_isigi
    assert isik.isVisible() and isik.geometry() == l.arama.geometry().adjusted(-4, -4, 4, 4)
    QTest.qWait(tema.SURE.kisa + 150)
    assert isik.guc == 1.0
    QApplication.sendEvent(l.arama, QFocusEvent(QEvent.FocusOut))
    QTest.qWait(tema.SURE.kisa + 150)
    assert isik.guc == 0.0 and isik.isHidden()
