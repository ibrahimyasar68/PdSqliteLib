## Ayarlar > Kullanma Kılavuzu ##
import re

import pytest

from acodes import kilavuz
from acodes.guest import Guest
from acodes.library import Library
from database.odunc import ODUNC_SURESI_GUN


@pytest.fixture(params=[Library, Guest])
def panel(request, app, uyarilar):
    return request.param()


def sekme_adlari(panel):
    t = panel.sekmeler
    return [re.sub(r" \(.*\)$", "", t.tabText(i)) for i in range(t.count())]   # "Kitap Verme (2 gecikmiş)"


def test_kilavuz_yardim_bolumunden_ayri_pencerede_acilir(panel):
    k = panel.ayarlar.kilavuz
    assert k.title() == "Kullanma Kılavuzu"
    assert k.window() is panel.ayarlar.kilavuz_penceresi and not k.isVisible()   # Ayarlar sayfası kısa kalır
    duzen = panel.ayarlar.yardim.parentWidget().layout()
    assert duzen.indexOf(panel.ayarlar.yardim) == duzen.count() - 2              # son bölüm (ardından boşluk)
    panel.ayarlar.yardim.butonlar["Kullanma Kılavuzu"].click()
    assert panel.ayarlar.kilavuz_penceresi.isVisible()
    panel.ayarlar.kilavuz_penceresi.close()
    assert "Yaşar Kütüphanesi" in k.findChild(type(k.konular[0][2]), "kilavuz_hakkinda").text()


def test_kilavuzda_yeni_ozellikler_anlatilir():
    metin = " ".join(m for _, m in kilavuz.YONETICI)
    assert "Ctrl+K" in metin and "Geri Al" in metin and "Hatırlatma Metni" in metin and "sağ" in metin
    assert "Ctrl+K" in " ".join(m for _, m in kilavuz.UYE)


def test_her_sekme_icin_konu_var(panel):
    basliklar = [b for b, _, _ in panel.ayarlar.kilavuz.konular]
    for sekme in sekme_adlari(panel):
        assert any(b.startswith(sekme) or b.startswith(sekme.split()[0]) for b in basliklar), sekme


def test_uyede_yonetici_konulari_yok():
    assert not any("Kitap Kayıt" in b or "Kitap Verme" in b for b, _ in kilavuz.UYE)
    assert any(b == "Kitaplarım" for b, _ in kilavuz.UYE)


def test_konular_tiklaninca_acilir_ve_tek_konu_acik(panel):
    panel.resize(1200, 800)
    panel.show()
    k = panel.ayarlar.kilavuz
    assert all(yazi.isHidden() for _, _, yazi in k.konular)          # başlangıçta hepsi kapalı
    k.konular[1][1].click()
    assert not k.konular[1][2].isHidden() and k.konular[1][1].text().startswith("▾")
    k.konular[2][1].click()
    assert k.konular[1][2].isHidden() and not k.konular[2][2].isHidden()   # öncekini kapatır
    k.konular[2][1].click()
    assert all(yazi.isHidden() for _, _, yazi in k.konular)          # tekrar tıklayınca kapanır
    panel.close()


def test_odunc_suresi_ayardan_gelir():
    metin = dict(kilavuz.YONETICI)["Kitap Verme: ödünç verme ve iade alma"]
    assert f"{ODUNC_SURESI_GUN} gündür" in metin


def test_uretici_imzasi(app, uyarilar):
    from acodes.login import Login
    assert kilavuz.IMZA == "IY Labs · 2025"
    assert Login().imza.text() == "IY Labs · 2025"
    assert "<b>IY Labs</b> tarafından 2025 yılında üretilmiştir." in kilavuz.HAKKINDA


def test_yedekleme_ve_disa_aktarma_konusu():
    from database.yedek import GUVENLIK_SAKLA, OTOMATIK_SAKLA
    metin = dict(kilavuz.YONETICI)["Yedekleme ve dışa aktarma"]
    assert f"son {OTOMATIK_SAKLA}" in metin and f"son {GUVENLIK_SAKLA} tanesi" in metin
    assert "Yedekten Geri Yükle" in metin and "Excel (.xlsx)" in metin
    assert "Yedekten Geri Yükle" not in dict(kilavuz.UYE)["Dışa aktarma"]     # üyede yedekleme yok
