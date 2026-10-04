## Ödünç kuralları: verme, iade alma, iadeyi geri alma ##

from database import odunc
from database.baglanti import islem
from database.kitaplar import kitap_bul
from database.kullanicilar import kullanici_bul
from servis import KuralHatasi, engel_varsa


def verme_engeli(kitap_id=None, uye_id=None):
    """Kitap bu üyeye verilemiyorsa KuralHatasi, verilebiliyorsa None. Biri None ise (ekranda seçim sürerken)
    yalnızca diğeriyle ilgili kurallar denetlenir.
    Kitap kopya sayısı kadar üyeye aynı anda verilebilir; bir üyeye aynı kitabın ikinci kopyası verilmez."""
    if kitap_id is not None:
        if kitap_bul(kitap_id) is None:
            return KuralHatasi("Bu kitap silinmiş.", "kitap")
        kopya, disarida = odunc.kopya_durumu(kitap_id)
        if disarida >= kopya:
            return KuralHatasi("Bu kitap başka bir üyede." if kopya == 1 else f"Bu kitabın {kopya} kopyasının hepsi üyelerde.",
                               "kitap")
    if uye_id is not None and kullanici_bul(uye_id) is None:
        return KuralHatasi("Bu üye silinmiş.", "uye")
    if kitap_id is not None and uye_id is not None and odunc.uyede_mi(uye_id, kitap_id):
        return KuralHatasi("Bu kitabın bir kopyası zaten bu üyede. Önce iade alın.")
    return None


def ver(kitap_id, uye_id, zaman=None):
    if kitap_id is None or uye_id is None:
        raise KuralHatasi("Kitap ve üye seçiniz!")
    with islem():
        engel_varsa(verme_engeli(kitap_id, uye_id))
        odunc.odunc_ver(uye_id, kitap_id, zaman)


def iade_al(uye_id, kitap_id, zaman=None):
    """Ödüncü kapatır; "Geri Al" için ödünç kaydının numarasını döndürür."""
    with islem():
        kayit_no = odunc.iade_al(uye_id, kitap_id, zaman)
        if kayit_no is None:
            raise KuralHatasi("Bu ödünç bulunamadı (iade alınmış olabilir).")
    return kayit_no


def iadeyi_geri_al(kayit_no, uye_id, kitap_id):
    """İade alınan ödünç yeniden dışarıda olur; bu arada kitap başka üyeye verildiyse KuralHatasi."""
    with islem():
        kopya, disarida = odunc.kopya_durumu(kitap_id)
        if disarida >= kopya or odunc.uyede_mi(uye_id, kitap_id):
            raise KuralHatasi("İade geri alınamaz: kitap bu arada yeniden ödünç verilmiş!")
        odunc.iade_geri_al(kayit_no)
