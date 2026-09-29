## Eski librarySqlite veritabanlarını (kitapliste.db + kayıt.db) PdSqliteLib şemasına aktarma ##
# Kullanım: python3 scripts/aktar_eski_db.py [--kaynak KLASOR] [--hedef DOSYA] [--force]
# Kaynak dosyalar sadece okunur, değiştirilmez.

import argparse
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from database.sema import SEMA  # noqa: E402  (uygulamanın beklediği şema)

VARSAYILAN_KAYNAK = os.path.expanduser("~/Desktop/librarySqlite")
VARSAYILAN_HEDEF = os.path.join(os.path.dirname(__file__), "..", "data", "DBL_Kayit.db")

# Bilinen veri giriş hataları: (adi, yazari, hatalı sayfa) -> doğru sayfa
SAYFA_DUZELTME = {("Acımak", "Stefan ZWEIG", "4045"): "404"}


def temizle(deger):
    """'None' yazısını boş metne çevirir, fazla boşlukları siler."""
    if deger is None or str(deger).strip() == "None":
        return ""
    return " ".join(str(deger).split())


def tr_kucuk(metin):
    """Türkçe İ/I harflerini dikkate alarak küçük harfe çevirir."""
    return metin.replace("İ", "i").replace("I", "ı").lower()


def anahtar(kitap):
    """Tekrar kontrolü için büyük/küçük harf ve boşluktan bağımsız tüm alanlar."""
    return tuple(tr_kucuk(alan) for alan in kitap)


def oku(kaynak):
    # kitapliste.db: id, adi, yazari, ceviren, turu, yayinevi, yili, sayfa
    b1 = sqlite3.connect(f"file:{os.path.join(kaynak, 'kitapliste.db')}?mode=ro", uri=True)
    liste1 = b1.execute("SELECT id, adi, yazari, ceviren, turu, yayinevi, yili, sayfa FROM Kayıt ORDER BY id").fetchall()
    b1.close()

    # kayıt.db: id yok, kolon sırası farklı ve yıl kolonu 'Basim'
    b2 = sqlite3.connect(f"file:{os.path.join(kaynak, 'kayıt.db')}?mode=ro", uri=True)
    liste2 = b2.execute("SELECT NULL, Adi, Yazari, Ceviren, Turu, Yayinevi, Basim, Sayfa FROM Kayıt ORDER BY rowid").fetchall()
    b2.close()
    return liste1, liste2


def birlestir(liste1, liste2):
    """kitapliste.db öncelikli olarak iki listeyi birleştirir, tekrarları atar."""
    gorulen = set()
    sonuc = []
    atlanan = 0
    for id_, *alanlar in liste1 + liste2:
        kitap = [temizle(a) for a in alanlar]
        kitap[6] = SAYFA_DUZELTME.get((kitap[0], kitap[1], kitap[6]), kitap[6])
        ktr = anahtar(kitap)
        if ktr in gorulen:
            atlanan += 1
            continue
        gorulen.add(ktr)
        sonuc.append((id_, kitap))
    return sonuc, atlanan


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kaynak", default=VARSAYILAN_KAYNAK)
    ap.add_argument("--hedef", default=VARSAYILAN_HEDEF)
    ap.add_argument("--force", action="store_true", help="Hedef dosya varsa üzerine yaz")
    arg = ap.parse_args()

    hedef = os.path.abspath(arg.hedef)
    if os.path.exists(hedef):
        if not arg.force:
            raise SystemExit(f"{hedef} zaten var. Üzerine yazmak için --force kullanın.")
        os.remove(hedef)
    os.makedirs(os.path.dirname(hedef), exist_ok=True)

    liste1, liste2 = oku(arg.kaynak)
    kitaplar, atlanan = birlestir(liste1, liste2)

    # kitapliste.db'deki id'ler korunur, kayıt.db'den gelenlere yeni id verilir
    sonraki_id = max(i for i, _ in kitaplar if i is not None) + 1
    db = sqlite3.connect(hedef)
    db.executescript(SEMA)
    for id_, kitap in kitaplar:
        if id_ is None:
            id_, sonraki_id = sonraki_id, sonraki_id + 1
        db.execute("INSERT INTO kayitlistesi (Id, Adi, Yazari, Ceviren, Turu, Yayinevi, Yili, Sayfa) VALUES (?,?,?,?,?,?,?,?)",
                   (id_, *kitap))
    db.commit()
    db.close()

    print(f"kitapliste.db : {len(liste1)} kayıt")
    print(f"kayıt.db      : {len(liste2)} kayıt")
    print(f"Tekrar atlanan: {atlanan}")
    print(f"Aktarılan     : {len(kitaplar)} kitap -> {hedef}")


if __name__ == "__main__":
    main()
