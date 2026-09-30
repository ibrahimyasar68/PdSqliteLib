## Ödünç takibi: teslim tarihi, gecikme ve ödünç geçmişi ##
# Teslim tarihi veritabanında tutulmaz; veriliş tarihine ODUNC_SURESI_GUN eklenerek hesaplanır.
# Böylece eski kayıtlar da değişiklik gerektirmeden bu özelliklerden yararlanır.

import datetime

from database.dbbase import baglantı

ODUNC_SURESI_GUN = 15


def tarih(metin):
    """'YYYY-MM-DD' metnini tarihe çevirir; boş veya hatalıysa None döndürür."""
    try:
        return datetime.date.fromisoformat(str(metin)[:10])
    except (TypeError, ValueError):
        return None


def tarih_yazi(deger):
    """Tarihi ekranda gösterilecek biçime çevirir: 29.09.2026"""
    t = deger if isinstance(deger, datetime.date) else tarih(deger)
    return t.strftime("%d.%m.%Y") if t else ""


def teslim_tarihi(verilis):
    t = tarih(verilis)
    return t + datetime.timedelta(days=ODUNC_SURESI_GUN) if t else None


def gun_sayisi(verilis, iade=None, bugun=None):
    """Kitabın kaç gündür dışarıda olduğu (iade edildiyse kaç gün dışarıda kaldığı)."""
    baslangic = tarih(verilis)
    if baslangic is None:
        return None
    bitis = tarih(iade) or bugun or datetime.date.today()
    return (bitis - baslangic).days


def gecikme_gunu(verilis, iade=None, bugun=None):
    """Teslim tarihinden kaç gün geç kalındığı (gecikme yoksa 0)."""
    teslim = teslim_tarihi(verilis)
    if teslim is None:
        return 0
    bitis = tarih(iade) or bugun or datetime.date.today()
    return max(0, (bitis - teslim).days)


def geciken_sayisi(bugun=None):
    satirlar = baglantı.execute("SELECT outdate FROM follow WHERE status='out'").fetchall()
    return sum(1 for (verilis,) in satirlar if gecikme_gunu(verilis, bugun=bugun) > 0)


## Üyedeki kitabın veriliş tarihi (iade ekranında gecikmeyi göstermek için)
def odunc_verilis(user_id, book_id):
    satir = baglantı.execute("SELECT outdate FROM follow WHERE userId=? AND bookId=? AND status='out'",
                             (str(user_id), str(book_id))).fetchone()
    return satir[0] if satir else None


## Ödünç geçmişi: (kitap, üye, veriliş, durum, iade) — en yeni en üstte
def odunc_gecmisi(user_id=None, book_id=None):
    kosullar, parametreler = [], []
    if user_id is not None:
        kosullar.append("f.userId=?")
        parametreler.append(str(user_id))
    if book_id is not None:
        kosullar.append("f.bookId=?")
        parametreler.append(str(book_id))
    where = f"WHERE {' AND '.join(kosullar)}" if kosullar else ""
    return baglantı.execute(f"""SELECT COALESCE(k.Adi,'(silinmiş kitap)'), COALESCE(u.adi_soyadi,'(silinmiş üye)'),
                                       f.outdate, f.status, f.indate
                                FROM follow f
                                LEFT JOIN kayitlistesi k ON k.Id=f.bookId
                                LEFT JOIN users u ON u.id=f.userId
                                {where}
                                ORDER BY f.outdate DESC, f.rowid DESC""", parametreler).fetchall()


## Ana sayfa: teslim tarihi geçmiş veya önümüzdeki `gun` gün içinde dolacak ödünçler
## (kitap, üye, veriliş, userId, bookId) — teslim tarihi en yakın olan en üstte
def yaklasan_teslimler(gun=3, bugun=None):
    sinir = (bugun or datetime.date.today()) + datetime.timedelta(days=gun)
    satirlar = baglantı.execute("""SELECT COALESCE(k.Adi,'(silinmiş kitap)'), COALESCE(u.adi_soyadi,'(silinmiş üye)'), f.outdate,
                                          f.userId, f.bookId
                                   FROM follow f
                                   LEFT JOIN kayitlistesi k ON k.Id=f.bookId
                                   LEFT JOIN users u ON u.id=f.userId
                                   WHERE f.status='out'""").fetchall()
    secilen = [s for s in satirlar if teslim_tarihi(s[2]) and teslim_tarihi(s[2]) <= sinir]
    return sorted(secilen, key=lambda s: teslim_tarihi(s[2]))


## Bir üyenin ödünçleri: (kitap, yazar, veriliş, durum, iade) — dışarıdakiler önce, en yeni en üstte
def uye_odunc(kullanici):
    return baglantı.execute("""SELECT COALESCE(k.Adi,'(silinmiş kitap)'), COALESCE(k.Yazari,''),
                                      f.outdate, f.status, f.indate
                               FROM follow f
                               JOIN users u ON u.id=f.userId
                               LEFT JOIN kayitlistesi k ON k.Id=f.bookId
                               WHERE u.kullanici=?
                               ORDER BY f.status='in', f.outdate DESC, f.rowid DESC""", (kullanici,)).fetchall()


def kalan_gun_yazi(verilis, bugun=None):
    """Dışarıdaki kitap için: '5 gün kaldı', 'Bugün teslim', '3 gün gecikti'"""
    teslim = teslim_tarihi(verilis)
    if teslim is None:
        return ""
    fark = (teslim - (bugun or datetime.date.today())).days
    if fark > 0:
        return f"{fark} gün kaldı"
    return "Bugün teslim" if fark == 0 else f"{-fark} gün gecikti"


## Geçmiş filtreleri için ödünç almış üyeler ve ödünç verilmiş kitaplar
def odunc_alan_uyeler():
    return baglantı.execute("""SELECT DISTINCT u.id, u.adi_soyadi, u.kullanici FROM follow f
                               JOIN users u ON u.id=f.userId ORDER BY u.adi_soyadi""").fetchall()


def odunc_verilen_kitaplar():
    return baglantı.execute("""SELECT DISTINCT k.Id, k.Adi, k.Yayinevi, k.Yili FROM follow f
                               JOIN kayitlistesi k ON k.Id=f.bookId ORDER BY k.Adi, k.Yili""").fetchall()
