## Kullanıcı kuralları: kayıt, düzenleme, silme, şifre ##
# Kilitlenmeyi önleyen kurallar: kimse kendi hesabını silemez veya kendi yetkisini değiştiremez,
# son admin silinemez ve yetkisi düşürülemez, elinde kitap olan kullanıcı silinemez.

from database import kullanicilar
from database.baglanti import islem
from database.odunc import kullanici_odunc_sayisi
from servis import KULLANICILAR, KuralHatasi, bildir, engel_varsa
from servis.dogrulama import mail_gecerli, sifre_hatasi, telefon_gecerli

YETKILER = ["admin", "guest"]


def ekleme_engeli(kullanici, sifre):
    """Yeni kullanıcı (Kullanici, id yok sayılır) kaydedilemiyorsa KuralHatasi, kaydedilebiliyorsa None."""
    if kullanici.yetki not in YETKILER:
        return KuralHatasi("Kayıt oluşturmak için yetki seçimini belirtin!", "yetki")
    if not kullanici.kullanici or not sifre or not kullanici.adi_soyadi:
        return KuralHatasi("Kullanıcı Adı, Şifre ve Adı Soyadı boş olamaz!")
    if sifre_hatasi(sifre):
        return KuralHatasi(sifre_hatasi(sifre), "sifre")
    if kullanici.telefon and not telefon_gecerli(kullanici.telefon):
        return KuralHatasi("Uygun telefon numarası girilmedi. Kontrol edin!", "telefon")
    if kullanici.mail and not mail_gecerli(kullanici.mail):
        return KuralHatasi("Uygun mail adresi girilmedi. Kontrol edin!", "mail")
    if kullanicilar.kullanici_var_mi("kullanici", kullanici.kullanici):
        return KuralHatasi("Kullanıcı adı kullanılmaktadır!", "kullanici")
    return None


def ekle(kullanici, sifre):
    """Yeni kullanıcı; numarası döner. Şifre hash'lenerek saklanır."""
    with islem():
        engel_varsa(ekleme_engeli(kullanici, sifre))
        kullanici_id = kullanicilar.kullanici_ekle(kullanici, sifre)
    bildir(KULLANICILAR)
    return kullanici_id


def guncelleme_engeli(kullanici, aktif_kullanici):
    """kullanici: yeni bilgilerle Kullanici (kullanıcı adı ve şifre değişmez). aktif_kullanici: işlemi yapanın adı."""
    eski = kullanicilar.kullanici_bul(kullanici.id)
    if eski is None:
        return KuralHatasi("Kullanıcı bulunamadı (silinmiş olabilir).")
    if not kullanici.adi_soyadi.strip():
        return KuralHatasi("Adı soyadı boş olamaz!", "adi_soyadi")
    if kullanici.telefon and not telefon_gecerli(kullanici.telefon):
        return KuralHatasi("Telefon 10 haneli olmalıdır!", "telefon")
    if kullanici.mail and not mail_gecerli(kullanici.mail):
        return KuralHatasi("Mail adresi geçerli değil!", "mail")
    if kullanici.yetki not in YETKILER:
        return KuralHatasi("Geçersiz yetki.", "yetki")
    if kullanici.yetki != eski.yetki:
        if eski.kullanici == aktif_kullanici:
            return KuralHatasi("Kendi yetkinizi değiştiremezsiniz.", "yetki")
        if eski.yetki == "admin" and kullanicilar.admin_sayisi() <= 1:
            return KuralHatasi("Son admin kullanıcının yetkisi düşürülemez!", "yetki")
    return None


def guncelle(kullanici, aktif_kullanici):
    with islem():
        engel_varsa(guncelleme_engeli(kullanici, aktif_kullanici))
        kullanicilar.kullanici_guncelle(kullanici)
    bildir(KULLANICILAR)


def silme_engeli(kullanici, aktif_kullanici):
    if kullanici.kullanici == aktif_kullanici:
        return KuralHatasi("Kendi hesabınızı silemezsiniz!")
    if kullanici.yetki == "admin" and kullanicilar.admin_sayisi() <= 1:
        return KuralHatasi("Son admin kullanıcı silinemez!")
    odunc = kullanici_odunc_sayisi(kullanici.id)
    if odunc:
        return KuralHatasi(f"Bu kullanıcının elinde iade edilmemiş {odunc} kitap var. Önce iade alın!")
    return None


def sil(kullanici, aktif_kullanici):
    """Kullanıcıyı siler; ödünç geçmişi korunur."""
    with islem():
        engel_varsa(silme_engeli(kullanici, aktif_kullanici))
        kullanicilar.kullanici_sil(kullanici.id)
    bildir(KULLANICILAR)


def sifre_degistir(kullanici, yeni, tekrar=None, eski=None):
    """eski verilirse (kullanıcı kendi şifresini değiştiriyorsa) önce mevcut şifre doğrulanır."""
    if eski is not None and kullanicilar.giris_kontrol(kullanici, eski) is None:
        raise KuralHatasi("Mevcut şifre yanlış!", "eski")
    hata = sifre_hatasi(yeni, tekrar)
    if hata:
        raise KuralHatasi(hata, "yeni")
    kullanicilar.sifre_guncelle(kullanici, yeni)
