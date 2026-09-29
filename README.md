# PdSqliteLib

PyQt5, SQLite ve pandas ile yazılmış masaüstü kütüphane yönetim uygulaması.
Kitap kaydı, üye yönetimi, ödünç verme / iade takibi ve istatistikler içerir.
Windows ve macOS üzerinde çalışır.

## Özellikler

Giriş ekranında kullanıcının yetkisine göre iki farklı panel açılır:

| Sekme | Admin | Guest |
|---|:---:|:---:|
| **Giriş**: karşılama, yeni kullanıcı / üye ekleme | ✓ | ✓ (kullanıcı ekleme yok) |
| **Kitap Listesi**: tüm kitaplar | ✓ | ✓ |
| **Kitap Kayıt**: ekleme, güncelleme, silme | ✓ | |
| **Filtre**: tür, yazar, yayınevi ve yıla göre çoklu seçim | ✓ | ✓ |
| **İstatistik**: en çok kitabı olan tür, yazar, yayınevi ve yıllar | ✓ | ✓ |
| **Kitap Verme**: ödünç verme, iade alma, dışarıdaki kitaplar | ✓ | |

Yeni kullanıcı ve üye kayıtlarını (`admin` veya `guest`) sadece giriş yapmış bir admin,
**Giriş** sekmesindeki **Yeni Kullanıcı Girişi** butonuyla oluşturabilir.

## Kurulum

Python 3.9 veya üzeri gerekir.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Windows'ta `.venv/bin/` yerine `.venv\Scripts\` kullanın.

### Veritabanı

Uygulama `data/DBL_Kayit.db` dosyasını kullanır. Bu dosya kişisel veri içerdiği için
git'e eklenmez. Yeni bir makinede bu dosyayı elde etmenin iki yolu var:

- Mevcut `DBL_Kayit.db` dosyasını `data/` klasörüne kopyalamak, veya
- Eski `librarySqlite` projesinin veritabanlarından aktarmak:

  ```bash
  python3 scripts/aktar_eski_db.py --kaynak ~/Desktop/librarySqlite
  ```

  Bu betik `kitapliste.db` ve `kayıt.db` dosyalarını birleştirir ve tekrar eden kayıtları ayıklar.
  Kullanıcı tablosu boş oluşur; giriş yapabilmek için bir admin kullanıcısı eklemeniz gerekir.

## Çalıştırma

```bash
.venv/bin/python main.py
```

## macOS uygulaması (.app)

```bash
./scripts/build_mac.sh
```

Çıktı `dist/PdSqliteLib.app` klasörüne yazılır. Paketlenmiş uygulama veritabanını
proje klasöründe değil, kullanıcı klasöründe tutar:

| Sistem | Konum |
|---|---|
| macOS | `~/Library/Application Support/PdSqliteLib/DBL_Kayit.db` |
| Windows | `%APPDATA%\PdSqliteLib\DBL_Kayit.db` |

İlk açılışta, paket oluşturulurken `data/` klasöründe bulunan veritabanı bu konuma kopyalanır.
Sonraki paketler mevcut verinin üzerine yazmaz. Bu yüzden `.app` ile `python main.py`
ayrı veritabanları kullanır.

Paket imzalanmamıştır. Başka bir Mac'te ilk açılışta sağ tık → **Aç** demek gerekir.
Apple Silicon (arm64) için derlenir.

## Proje yapısı

```
main.py              Giriş noktası
acodes/              Pencerelerin iş mantığı (login, library, guest, user)
acodes/ortak.py      Admin ve Guest panellerinde ortak sekmeler (liste, filtre, istatistik)
bforms/              .ui dosyalarından üretilen formlar (elle düzenlenmez)
cuis/                Qt Designer .ui kaynakları
database/dbbase.py   Yazma işlemleri, şifre hash'leme, veritabanı yolu
database/dbframe.py  Okuma, filtreleme ve raporlar
media/               Resimler, ikon ve media.qrc
scripts/             Dönüştürme, veri aktarma ve paketleme betikleri
data/                Veritabanı (git dışında)
```

### Arayüzü düzenlemek

`cuis/` altındaki `.ui` dosyalarını Qt Designer ile düzenleyin, sonra `bforms/` altındaki
Python dosyalarını yeniden üretin:

```bash
.venv/bin/python scripts/convertFiles.py
```

Betiği sanal ortam etkinken çalıştırın (`source .venv/bin/activate`); `pyuic5` ve
`pyrcc5` komutları PyQt5 ile birlikte kurulur.

## Veritabanı şeması

```sql
kayitlistesi (Id INTEGER PRIMARY KEY, Adi, Yazari, Ceviren, Turu, Yayinevi, Yili, Sayfa)
users        (id INTEGER PRIMARY KEY, kullanici UNIQUE, sifre, adi_soyadi, telefon, mail, yetki)
follow       (userId, bookId, outdate, outtime, status, indate, intime)
```

- `users.yetki`: `admin` veya `guest`
- `users.sifre`: PBKDF2-SHA256 hash'i (`pbkdf2$tekrar$tuz$hash`). Eski düz metin şifreler
  ilk başarılı girişte otomatik olarak hash'e çevrilir.
- `follow.status`: `out` (ödünçte) veya `in` (iade edildi). Her ödünç işlemi yeni bir satırdır;
  iade sadece `out` durumundaki satırı günceller.
