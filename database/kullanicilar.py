## Kullanıcılar (users tablosu): giriş, şifre, kayıt ##

import hashlib
import hmac
import secrets

from database.baglanti import baglantı, islem
from database.modeller import Kullanici

# Sorguya adı yazılabilecek kolonlar (değerler her zaman ? ile verilir)
USER_KOLON = {'id','kullanici','adi_soyadi','telefon','mail','yetki'}
_KOLONLAR = "id, kullanici, adi_soyadi, telefon, mail, yetki"

# Şifre hash'leme: "pbkdf2$tekrar$tuz$hash" biçiminde saklanır
SIFRE_TEKRAR = 200_000

def sifre_hashle(sifre):
    tuz = secrets.token_bytes(16)
    ozet = hashlib.pbkdf2_hmac("sha256", sifre.encode(), tuz, SIFRE_TEKRAR)
    return f"pbkdf2${SIFRE_TEKRAR}${tuz.hex()}${ozet.hex()}"

def sifre_dogrula(sifre, kayitli):
    if not kayitli:
        return False
    if not kayitli.startswith("pbkdf2$"):
        # Eski (düz metin) kayıtlar için
        return hmac.compare_digest(sifre, kayitli)
    _, tekrar, tuz, ozet = kayitli.split("$")
    yeni = hashlib.pbkdf2_hmac("sha256", sifre.encode(), bytes.fromhex(tuz), int(tekrar))
    return hmac.compare_digest(yeni.hex(), ozet)

def sifre_guncelle(kullanici, sifre):
    with islem():
        baglantı.execute("UPDATE users SET sifre=? WHERE kullanici=?", (sifre_hashle(sifre), kullanici))


## Giriş kontrolü: doğruysa yetkiyi, yanlışsa None döndürür
def giris_kontrol(name,paw):
    kayit=baglantı.execute("SELECT sifre, yetki FROM users WHERE kullanici=?",(name,)).fetchone()
    if kayit is None or not sifre_dogrula(paw,kayit[0]):
        return None
    if not kayit[0].startswith("pbkdf2$"):
        sifre_guncelle(name,paw)  # Eski düz metin şifreyi hash'e çevir
    return kayit[1]


######################
###  Okuma         ####
######################

## Kullanıcı numarasıyla (yoksa None)
def kullanici_bul(id):
    kayit=baglantı.execute(f"SELECT {_KOLONLAR} FROM users WHERE id=?",(id,)).fetchone()
    return Kullanici.satirdan(kayit) if kayit else None

## Kullanıcı adıyla (yoksa None); Ayarlar > Hesabım
def kullanici_adiyla_bul(kullanici):
    kayit=baglantı.execute(f"SELECT {_KOLONLAR} FROM users WHERE kullanici=?",(kullanici,)).fetchone()
    return Kullanici.satirdan(kayit) if kayit else None

## Kullanıcı yönetimi ekranı için tüm kullanıcılar, kullanıcı adına göre
def kullanicilar():
    return [Kullanici.satirdan(s) for s in baglantı.execute(f"SELECT {_KOLONLAR} FROM users ORDER BY kullanici")]

## Açılır listeler için (id, adı soyadı, kullanıcı adı) listesi
def secim_listesi():
    return baglantı.execute("SELECT id, adi_soyadi, kullanici FROM users ORDER BY adi_soyadi").fetchall()

## Bu kolonda bu değere sahip kullanıcı var mı?
def kullanici_var_mi(ad, deger):
    if ad not in USER_KOLON:
        raise ValueError(f"Geçersiz kolon: {ad}")
    return baglantı.execute(f"SELECT COUNT(*) FROM users WHERE {ad}=?",(deger,)).fetchone()[0]>0

def admin_sayisi():
    return baglantı.execute("SELECT COUNT(*) FROM users WHERE yetki='admin'").fetchone()[0]


######################
###  Kayıt         ####
######################

## Yeni kullanıcı (kullanici.id yok sayılır); numarası döner
def kullanici_ekle(kullanici, sifre):
    with islem():
        return baglantı.execute("INSERT INTO users (kullanici, sifre, adi_soyadi, telefon, mail, yetki) VALUES (?,?,?,?,?,?)",
                                (kullanici.kullanici, sifre_hashle(sifre), kullanici.adi_soyadi, kullanici.telefon,
                                 kullanici.mail, kullanici.yetki)).lastrowid

## Bilgileri güncelleme (kullanıcı adı ve şifre hariç)
def kullanici_guncelle(kullanici):
    with islem():
        baglantı.execute("UPDATE users SET adi_soyadi=?, telefon=?, mail=?, yetki=? WHERE id=?",
                         (kullanici.adi_soyadi, kullanici.telefon, kullanici.mail, kullanici.yetki, kullanici.id))

## Silme (ödünç geçmişi korunur)
def kullanici_sil(id):
    with islem():
        baglantı.execute("DELETE FROM users WHERE id=?", (id,))
