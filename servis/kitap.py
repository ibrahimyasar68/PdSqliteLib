## Kitap kuralları: kaydetme, silme, silmeyi geri alma ##

from dataclasses import replace

from database.baglanti import islem
from database.kitaplar import kitap_bul, kitap_ekle, kitap_geri_ekle, kitap_guncelle, kitap_sil
from database.odunc import kitap_oduncte, kopya_durumu
from servis import KuralHatasi, engel_varsa
from servis.dogrulama import isbn_gecerli, isbn_normal


def kayit_engeli(kitap):
    """Kitap kaydedilemiyorsa KuralHatasi (alan: hatalı alan), kaydedilebiliyorsa None."""
    if not kitap.adi:
        return KuralHatasi("Kitap adı boş olamaz.", "adi")
    if kitap.isbn and not isbn_gecerli(kitap.isbn):
        return KuralHatasi("ISBN geçerli değil. 10 veya 13 haneli ISBN'i kontrol edin (boş da bırakılabilir).", "isbn")
    if kitap.id is not None:
        disarida = kopya_durumu(kitap.id)[1]
        if kitap.kopya < disarida:
            return KuralHatasi(f"Bu kitabın {disarida} kopyası şu an üyelerde. "
                               f"Kopya sayısı {disarida}'den az olamaz.", "kopya")
    return None


def kaydet(kitap):
    """Yeni kitabı ekler (id None) veya günceller; kitabın numarasını döndürür. ISBN tiresiz saklanır."""
    kitap = replace(kitap, isbn=isbn_normal(kitap.isbn))
    with islem():
        engel_varsa(kayit_engeli(kitap))
        if kitap.id is None:
            return kitap_ekle(kitap)
        kitap_guncelle(kitap)
        return kitap.id


def silme_engeli(kitap_id):
    if kitap_oduncte(kitap_id):
        return KuralHatasi("Bu kitap ödünçte. İade alınmadan silinemez!")
    return None


def sil(kitap_id):
    """Kitabı siler; "Geri Al" için silinen kitabı (Kitap) döndürür."""
    with islem():
        engel_varsa(silme_engeli(kitap_id))
        kitap = kitap_bul(kitap_id)
        if kitap is None:
            raise KuralHatasi("Kitap bulunamadı (silinmiş olabilir).")
        kitap_sil(kitap_id)
    return kitap


def geri_getir(kitap):
    """Silinen kitabı aynı numara ve bilgilerle geri getirir; numara bu arada kullanıldıysa KuralHatasi."""
    with islem():
        if kitap_bul(kitap.id) is not None:
            raise KuralHatasi("Kitap geri getirilemez: bu kayıt numarası yeniden kullanılmış.")
        kitap_geri_ekle(kitap)
