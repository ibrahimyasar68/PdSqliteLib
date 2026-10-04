## Veri düzeltme kuralları: farklı yazımları birleştirme ##

from database import duzeltme
from database.yedek import guvenlik_yedegi_al
from servis import KuralHatasi


def birlestir(kolon, eskiler, yeni, onceki_yedek=None):
    """eskiler listesindeki yazımları yeni yazımla değiştirir. Değişiklikten önce güvenlik yedeği alınır;
    onceki_yedek verilirse (bu oturumda zaten alındıysa) yeniden alınmaz.
    (değişen kitap sayısı, yedeğin yolu) döndürür."""
    yeni = " ".join(str(yeni or "").split())
    if not yeni:
        raise KuralHatasi("Doğru yazım boş olamaz.")
    yedek = onceki_yedek or guvenlik_yedegi_al("duzeltme_oncesi_")
    return duzeltme.birlestir(kolon, eskiler, yeni), yedek


def yoksay(kolon, degerler):
    """Yanlış bir benzerlik önerisi bir daha gösterilmez."""
    duzeltme.yoksay(kolon, degerler)
