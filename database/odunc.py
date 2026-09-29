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


## Geçmiş filtreleri için ödünç almış üyeler ve ödünç verilmiş kitaplar
def odunc_alan_uyeler():
    return baglantı.execute("""SELECT DISTINCT u.id, u.adi_soyadi, u.kullanici FROM follow f
                               JOIN users u ON u.id=f.userId ORDER BY u.adi_soyadi""").fetchall()


def odunc_verilen_kitaplar():
    return baglantı.execute("""SELECT DISTINCT k.Id, k.Adi, k.Yayinevi, k.Yili FROM follow f
                               JOIN kayitlistesi k ON k.Id=f.bookId ORDER BY k.Adi, k.Yili""").fetchall()
