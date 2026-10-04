## Servis katmanı: kütüphanenin kuralları ##
# Ekranlar yazma işlemlerini buradan yapar; kurallar (müsait kopya, son admin, ödünçteki kitap ...) tek yerdedir
# ve pencere açmadan test edilir. Okuma için ekranlar database/ modüllerini doğrudan kullanabilir.
#
# Her kuralın iki yüzü vardır:
#   *_engeli(...)  işlem yapılamıyorsa KuralHatasi, yapılabiliyorsa None döndürür (onay sormadan önce, önizleme için)
#   işlemin kendisi aynı kontrolü tek veritabanı işleminin içinde yeniden yapar, engel varsa KuralHatasi fırlatır.


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
