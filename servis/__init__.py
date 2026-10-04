## Servis katmanı: kütüphanenin kuralları ##
# Ekranlar yazma işlemlerini buradan yapar; kurallar (müsait kopya, son admin, ödünçteki kitap ...) tek yerdedir
# ve pencere açmadan test edilir. Okuma için ekranlar database/ modüllerini doğrudan kullanabilir.
#
# Her kuralın iki yüzü vardır:
#   *_engeli(...)  işlem yapılamıyorsa KuralHatasi, yapılabiliyorsa None döndürür (onay sormadan önce, önizleme için)
#   işlemin kendisi aynı kontrolü tek veritabanı işleminin içinde yeniden yapar, engel varsa KuralHatasi fırlatır.
#
# Başarıyla kaydedilen her yazma işleminden sonra konusu bildirilir (KITAPLAR, ODUNC, KULLANICILAR);
# ekranlar acodes/olaylar.py üzerinden dinleyip kendilerini yeniler. Bu modül Qt'ye bağlı değildir.

KITAPLAR, ODUNC, KULLANICILAR = "kitaplar", "odunc", "kullanicilar"
KONULAR = (KITAPLAR, ODUNC, KULLANICILAR)

_dinleyiciler = []


def dinle(islev):
    """islev(konu): her başarılı yazma işleminden sonra çağrılır."""
    _dinleyiciler.append(islev)


def bildir(*konular):
    """İşlem kaydedildikten sonra (with islem() bloğunun dışında) çağrılır: geri alınan işlem bildirilmez."""
    for konu in konular:
        for islev in list(_dinleyiciler):
            islev(konu)


class KuralHatasi(Exception):
    """Bir kütüphane kuralı işlemi engelledi. str(hata) kullanıcıya gösterilecek metindir.
    alan: hatanın ilgili olduğu form alanı ("adi", "isbn", "kopya" ...) veya None."""

    def __init__(self, metin, alan=None):
        super().__init__(metin)
        self.alan = alan


def engel_varsa(engel):
    """*_engeli() sonucu bir KuralHatasi ise fırlatır."""
    if engel is not None:
        raise engel
