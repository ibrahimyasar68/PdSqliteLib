## Ödünç takibi: teslim tarihi, gecikme ve ödünç geçmişi ##
# Teslim tarihi veritabanında tutulmaz; veriliş tarihine ODUNC_SURESI_GUN eklenerek hesaplanır.
# Böylece eski kayıtlar da değişiklik gerektirmeden bu özelliklerden yararlanır.

import datetime

from database.baglanti import baglantı, islem
from database.modeller import Odunc

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


## Ödünç verirken üye bilgisi: elindeki kitap sayısı ve bunlardan kaçının teslim süresi geçmiş
def uye_durumu(user_id, bugun=None):
    satirlar = baglantı.execute("SELECT outdate FROM follow WHERE userId=? AND status='out'", (str(user_id),)).fetchall()
    return len(satirlar), sum(1 for (verilis,) in satirlar if gecikme_gunu(verilis, bugun=bugun) > 0)


######################
###  Kayıt         ####
######################
# follow tablosunda id'ler metin, saat "10:00:00 " biçiminde saklanır (eski kayıtlarla aynı)

def _zaman(zaman):
    zaman = zaman or datetime.datetime.today()
    return str(zaman.date()), zaman.strftime("%X ")


def odunc_ver(uye_id, kitap_id, zaman=None):
    tarih_, saat = _zaman(zaman)
    with islem():
        baglantı.execute("INSERT INTO follow (userId,bookId,outdate,outtime,status,indate,intime) VALUES (?,?,?,?,'out','','')",
                         (str(uye_id), str(kitap_id), tarih_, saat))


def iade_al(uye_id, kitap_id, zaman=None):
    """Dışarıdaki ödüncü kapatır (geçmiş iadelere dokunmaz); ödünç kaydının numarası (rowid) döner,
    iade geri alınırken kullanılır. Dışarıda böyle bir ödünç yoksa None."""
    tarih_, saat = _zaman(zaman)
    with islem():
        satir = baglantı.execute("SELECT rowid FROM follow WHERE userId=? AND bookId=? AND status='out'",
                                 (str(uye_id), str(kitap_id))).fetchone()
        baglantı.execute("UPDATE follow SET status='in', indate=?, intime=? WHERE userId=? AND bookId=? AND status='out'",
                         (tarih_, saat, str(uye_id), str(kitap_id)))
    return satir[0] if satir else None


def iade_geri_al(rowid):
    """İadeyi geri alma ("Geri Al"): ödünç kaydı yeniden dışarıda olur."""
    with islem():
        baglantı.execute("UPDATE follow SET status='out', indate='', intime='' WHERE rowid=? AND status='in'", (rowid,))


######################
###  Durum         ####
######################

def disaridakiler():
    """Dışarıdaki ödünçler (Odunc), en eski veriliş en üstte."""
    return [Odunc(*satir) for satir in baglantı.execute(
        """SELECT COALESCE(k.Adi,'(silinmiş kitap)'), COALESCE(k.Yazari,''), COALESCE(k.Turu,''),
                  COALESCE(u.adi_soyadi,'(silinmiş üye)'), COALESCE(u.telefon,''), COALESCE(u.mail,''), f.outdate,
                  f.userId, f.bookId
           FROM follow f
           LEFT JOIN kayitlistesi k ON k.Id=f.bookId
           LEFT JOIN users u ON u.id=f.userId
           WHERE f.status='out' ORDER BY f.outdate, f.rowid""")]


def kitap_oduncte(kitap_id):
    return baglantı.execute("SELECT COUNT(*) FROM follow WHERE bookId=? AND status='out'", (str(kitap_id),)).fetchone()[0] > 0


def kopya_durumu(kitap_id):
    """(kopya sayısı, dışarıdaki kopya sayısı); kitap yoksa kopya 0."""
    kopya = baglantı.execute("SELECT COALESCE(Kopya,1) FROM kayitlistesi WHERE Id=?", (kitap_id,)).fetchone()
    disarida = baglantı.execute("SELECT COUNT(*) FROM follow WHERE bookId=? AND status='out'", (str(kitap_id),)).fetchone()[0]
    return (kopya[0] if kopya else 0), disarida


def uyede_mi(uye_id, kitap_id):
    """Üyede bu kitabın iade edilmemiş bir kopyası var mı?"""
    return baglantı.execute("SELECT COUNT(*) FROM follow WHERE userId=? AND bookId=? AND status='out'",
                            (str(uye_id), str(kitap_id))).fetchone()[0] > 0


def kullanici_odunc_sayisi(uye_id):
    """Kullanıcının elinde iade edilmemiş kitap sayısı."""
    return baglantı.execute("SELECT COUNT(*) FROM follow WHERE userId=? AND status='out'", (str(uye_id),)).fetchone()[0]
