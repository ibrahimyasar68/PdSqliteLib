## Veri modelleri ##
# Kayıtlar sıra numarasıyla (kayit[8]) değil adıyla (kitap.kopya) kullanılır; kolon eklemek indeksleri kaydırmaz.
# Tablolara yazılan liste satırları (arama sonuçları, raporlar) model değildir, düz satır olarak kalır.

from dataclasses import dataclass
from typing import Optional


def id_sayi(deger):
    # follow tablosunda id'ler metin olarak saklanır
    return int(deger) if str(deger).isdigit() else deger


@dataclass
class Kitap:
    adi: str
    yazari: str = ""
    ceviren: str = ""
    turu: str = ""
    yayinevi: str = ""
    yili: str = ""
    sayfa: str = ""
    isbn: str = ""
    kopya: int = 1
    raf: str = ""
    notlar: str = ""
    id: Optional[int] = None     # kaydedilmemiş kitapta None

    # Veritabanı kolonlarının sırası (id hariç); sorgular ve kayıt bu sırayı kullanır
    KOLONLAR = ("Adi", "Yazari", "Ceviren", "Turu", "Yayinevi", "Yili", "Sayfa", "ISBN", "Kopya", "Raf", "Notlar")

    @classmethod
    def satirdan(cls, satir):
        """(Id, Adi, ..., Notlar) satırından kitap; boş (NULL) metinler "" olur."""
        id, *degerler = satir
        kitap = cls(*("" if d is None else d for d in degerler), id=id)
        kitap.kopya = int(kitap.kopya or 1)
        return kitap

    def degerler(self):
        """Veritabanına yazılacak değerler, KOLONLAR sırasıyla."""
        return (self.adi, self.yazari, self.ceviren, self.turu, self.yayinevi, self.yili, self.sayfa,
                self.isbn, self.kopya, self.raf, self.notlar)


@dataclass
class Kullanici:
    id: int
    kullanici: str
    adi_soyadi: str = ""
    telefon: str = ""
    mail: str = ""
    yetki: str = "guest"

    @classmethod
    def satirdan(cls, satir):
        """(id, kullanici, adi_soyadi, telefon, mail, yetki) satırından; şifre modele hiç girmez."""
        id, kullanici, *diger = satir
        return cls(id, kullanici, *("" if d is None else d for d in diger))


@dataclass
class Odunc:
    """Dışarıdaki (iade edilmemiş) bir ödünç: kitap ve üye bilgileriyle."""
    kitap: str
    yazar: str
    tur: str
    uye: str
    telefon: str
    mail: str
    verilis: str
    uye_id: int
    kitap_id: int

    def __post_init__(self):
        self.uye_id, self.kitap_id = id_sayi(self.uye_id), id_sayi(self.kitap_id)
