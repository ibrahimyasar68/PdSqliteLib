## Veri düzeltme: benzer yazımları bulma, birleştirme ve eksik bilgiler ##
# Hiçbir değişiklik kendiliğinden yapılmaz; öneriler kullanıcı onayıyla birleştirilir.

import re
import unicodedata
from collections import Counter

from database.baglanti import baglantı
from database.kitaplar import KITAP_KOLON, kolon

_KATLAMA = str.maketrans("ÇĞIİÖŞÜçğıöşü", "CGIIOSUcgiosu")


def anahtar(deger):
    """Karşılaştırma anahtarı: büyük/küçük harf, Türkçe karakter, aksan, noktalama ve boşluk farkı yok sayılır."""
    metin = unicodedata.normalize("NFKD", str(deger or "").translate(_KATLAMA))
    metin = "".join(h for h in metin if not unicodedata.combining(h)).lower()
    metin = re.sub(r"[^\w\s]", "", metin)
    return " ".join(metin.split())


def _mesafe(a, b):
    """İki kelime arasındaki harf farkı (Levenshtein)."""
    onceki = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        simdiki = [i]
        for j, y in enumerate(b, 1):
            simdiki.append(min(onceki[j] + 1, simdiki[j - 1] + 1, onceki[j - 1] + (x != y)))
        onceki = simdiki
    return onceki[-1]


def olasi_ayni(a, b):
    """İki anahtar büyük ihtimalle aynı değerin farklı yazımı mı?
    Kelime sayısı aynı olmalı; farklı kelimeler en az 5 harfli olmalı ve 1 harf (8+ harfte 2 harf)
    farklı olabilir. Böylece "Can Yayınları" / "Cem Yayınları" gibi kısa kelime farkları eşleşmez."""
    ka, kb = a.split(), b.split()
    if len(ka) != len(kb) or a == b:
        return False
    for x, y in zip(ka, kb):
        if x == y:
            continue
        if min(len(x), len(y)) < 5 or abs(len(x) - len(y)) > 2:
            return False
        if _mesafe(x, y) > (1 if min(len(x), len(y)) < 8 else 2):
            return False
    return True


def _imza(degerler):
    return "|".join(sorted(degerler))


def yoksayilanlar(kol):
    return {s for (s,) in baglantı.execute("SELECT imza FROM duzeltme_yoksay WHERE kolon=?", (kol,))}


def yoksay(kol, degerler):
    with baglantı:
        baglantı.execute("INSERT INTO duzeltme_yoksay (kolon, imza) VALUES (?,?)", (kolon(kol, KITAP_KOLON), _imza(degerler)))


def benzer_gruplar(kol):
    """[{'degerler': [(yazım, kitap sayısı), ...], 'kesin': bool}, ...]
    kesin: yazımlar sadece büyük/küçük harf, aksan veya noktalama bakımından farklı."""
    k = kolon(kol, KITAP_KOLON)
    sayim = Counter(d for (d,) in baglantı.execute(f"SELECT {k} FROM kayitlistesi") if d and str(d).strip())
    degerler = list(sayim)
    anahtarlar = {d: anahtar(d) for d in degerler}
    ebeveyn = {d: d for d in degerler}

    def kok(d):
        while ebeveyn[d] != d:
            ebeveyn[d] = ebeveyn[ebeveyn[d]]
            d = ebeveyn[d]
        return d

    for i, a in enumerate(degerler):
        for b in degerler[i + 1:]:
            if anahtarlar[a] == anahtarlar[b] or olasi_ayni(anahtarlar[a], anahtarlar[b]):
                ebeveyn[kok(a)] = kok(b)

    gruplar = {}
    for d in degerler:
        gruplar.setdefault(kok(d), []).append(d)
    atla = yoksayilanlar(k)
    sonuc = []
    for uyeler in gruplar.values():
        if len(uyeler) < 2 or _imza(uyeler) in atla:
            continue
        uyeler.sort(key=lambda d: (-sayim[d], d))
        sonuc.append({"degerler": [(d, sayim[d]) for d in uyeler],
                      "kesin": len({anahtarlar[d] for d in uyeler}) == 1})
    sonuc.sort(key=lambda g: (not g["kesin"], anahtar(g["degerler"][0][0])))
    return sonuc


def birlestir(kol, eskiler, yeni):
    """eskiler listesindeki yazımları yeni yazımla değiştirir; değişen kitap sayısını döndürür."""
    k = kolon(kol, KITAP_KOLON)
    eskiler = [e for e in eskiler if e != yeni]
    if not eskiler:
        return 0
    with baglantı:
        imlec = baglantı.execute(f"UPDATE kayitlistesi SET {k}=? WHERE {k} IN ({','.join('?' * len(eskiler))})",
                                 [yeni] + eskiler)
    return imlec.rowcount


def eksik_kitaplar(kol):
    """Bu alanı boş olan kitaplar: (Id, Adı, Yazarı, Yayınevi, Yılı)"""
    k = kolon(kol, KITAP_KOLON)
    return baglantı.execute(f"""SELECT Id, Adi, Yazari, Yayinevi, Yili FROM kayitlistesi
                                WHERE {k} IS NULL OR TRIM({k})='' ORDER BY Adi""").fetchall()
