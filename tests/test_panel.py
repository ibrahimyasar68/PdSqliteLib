## Panel iskeleti (acodes/panel.py): sayfa listesi menüyü, kısayolları ve hızlı aramayı belirler ##
import pytest

from acodes import ikonlar
from acodes.guest import Guest
from acodes.library import Library


@pytest.mark.parametrize("panel,basliklar", [
    (Library, ["Giriş", "Kitap Listesi", "Kitap Kayıt", "Filtre", "İstatistik", "Kitap Verme", "Ayarlar"]),
    (Guest, ["Giriş", "Kitap Listesi", "Filtre", "İstatistik", "Kitaplarım", "Ayarlar"]),
])
def test_menu_sayfa_listesinden_kurulur(app, uyarilar, panel, basliklar):
    p = panel()
    assert [s.baslik for s in p.sayfalar] == basliklar
    assert [p.sekmeler.widget(i) for i in range(p.sekmeler.count())] == [s.bilesen for s in p.sayfalar]
    assert [buton.ad for buton, _ in p.yan_menu.ogeler] == basliklar
    assert all(s.anahtar in ikonlar.SEKME_IKONLARI for s in p.sayfalar)
    assert [k[0] for k in p.bolum_komutlari()] == basliklar        # hızlı aramadaki bölümler


def test_sayfa_acilinca_yenilenir(app, uyarilar, db):
    p = Library()
    db.execute("DELETE FROM kayitlistesi WHERE Id>2")
    db.commit()
    p.ac(p.liste)
    assert p.liste.tablo.rowCount() == 2


def test_alt_sayfa_acilir(app, uyarilar):
    p = Library()
    p.ac(p.verme, p.gecmis)
    assert p.sekmeler.currentWidget() is p.verme and p.alt_sekmeler[p.verme].currentWidget() is p.gecmis
