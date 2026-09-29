# PdSqliteLib

PyQt5, SQLite ve pandas ile yazılmış masaüstü kütüphane yönetim uygulaması.
Kitap kaydı, üye yönetimi, ödünç verme / iade takibi ve istatistikler içerir.
Windows ve macOS üzerinde çalışır.

## Özellikler

Giriş ekranında kullanıcının yetkisine göre iki farklı panel açılır:

| Sekme | Admin | Guest |
|---|:---:|:---:|
| **Giriş**: yeni kullanıcı, kullanıcı yönetimi, yedekleme | ✓ | sadece kendi şifresini değiştirme |
| **Kitap Listesi**: tüm kitaplar, anlık arama | ✓ | ✓ |
| **Kitap Kayıt**: ekleme, güncelleme, silme, veri düzeltme | ✓ | |
| **Filtre**: tür, yazar, yayınevi ve yıla göre çoklu seçim | ✓ | ✓ |
| **İstatistik**: çizelgeler ve güncel grafikler (tür, yazar, yayınevi, basım yılı) | ✓ | ✓ |
| **Kitap Verme**: ödünç verme, iade alma, dışarıdaki kitaplar, ödünç geçmişi | ✓ | |

Panellerdeki **Oturumu Kapat** butonu giriş ekranına döner; başka bir kullanıcıyla giriş yapılabilir.
Programdan çıkmak için giriş ekranındaki kırmızı çıkış butonu kullanılır. Paneller macOS'ta büyütülmüş
pencerede (küçültülebilir, diğer programlara geçilebilir), Windows'ta tam ekran açılır.

Yeni kullanıcı ve üye kayıtlarını (`admin` veya `guest`) sadece giriş yapmış bir admin,
**Giriş** sekmesindeki **Yeni Kullanıcı Girişi** butonuyla oluşturabilir.

### Arama

**Kitap Listesi** sekmesindeki arama kutusu yazdıkça sonuçları günceller. Kitap adı, yazar, çevirmen,
tür, yayınevi ve yılda arar; büyük/küçük harf ve Türkçe karakter farkı gözetmez ("sahin" → "Şahin",
"kuyucakli" → "Kuyucaklı"). Birden fazla kelime yazılırsa hepsini içeren kitaplar listelenir.

### Tablolar

- Kolon başlığına tıklayınca tablo o kolona göre sıralanır (tekrar tıklayınca ters sırada).
  Sayılar sayı olarak, tarihler tarih olarak, metinler Türk alfabesine göre sıralanır; boşlar en sona gider.
- Hücreler salt okunurdur; değişiklikler ilgili düzenleme ekranlarından yapılır.
- Admin panelinde **Kitap Listesi** veya **Filtre** sonuçlarında bir satıra çift tıklamak kitabı
  **Kitap Kayıt → Kayıt Düzenleme** ekranında açar.
- **Dışardaki Kitaplar**'da bir satıra çift tıklamak **Alma Kaydı** ekranını üye ve kitap seçili
  olarak açar; sadece Kaydet'e basmak kalır.

### Veri düzeltme

**Kitap Kayıt → Veri Düzeltme** alt sekmesi:

- **Aynı değerin farklı yazımları:** Yazar, yayınevi, çevirmen veya türde birbirine çok benzeyen
  yazımları bulur. Sadece büyük/küçük harf, aksan veya noktalama farkı olanlar **Kesin**
  ("Adam Yayınları" / "Adam yayınları"), harf farkı olanlar **Olası** ("EYÜBOĞLU" / "EYYÜBOĞLU")
  olarak gösterilir. Hiçbir şey kendiliğinden değişmez: birleştirilecek yazımları işaretleyip doğru
  yazımı seçer (veya düzeltir) ve **İşaretlileri Birleştir**'e basarsınız. Değişiklikten önce yedek alınır.
- Yanlış bir öneri (ör. "Antoloji" / "Astroloji") **Bu Öneriyi Yoksay** ile bir daha gösterilmez.
- **Eksik bilgiler:** Basım yılı, yayınevi, yazar veya türü boş olan kitaplar; çift tıklayınca kitap
  düzenleme ekranında açılır.

### Dışa aktarma (Excel / CSV)

Kitap Listesi, Filtre sonuçları, Dışardaki Kitaplar ve Ödünç Geçmişi'nde **Dışa Aktar** butonu vardır;
tüm tablolarda (İstatistik çizelgeleri dahil) sağ tıklayarak da aktarılabilir. Tablo ekranda nasıl
görünüyorsa (arama, filtre, sıralama) öyle kaydedilir.

- **Excel (.xlsx):** kalın başlık, sabit ilk satır ve otomatik filtre. Sayılar sayı, tarihler tarih
  olarak yazılır; telefon gibi uzun rakam dizileri baştaki sıfır kaybolmasın diye metin kalır.
- **CSV:** Türkçe Excel'in doğrudan açabileceği biçimde (UTF-8, `;` ayırıcı).

### Ödünç takibi

- Ödünç süresi **15 gündür** (`database/odunc.py` içindeki `ODUNC_SURESI_GUN`). Teslim tarihi veriliş
  tarihinden hesaplanır; eski kayıtlar için de geçerlidir.
- Kitap verilirken teslim tarihi, iade alınırken gecikme varsa kaç gün geciktiği gösterilir.
- **Dışardaki Kitaplar**: teslim tarihi ve kaç gündür dışarıda olduğu; süresi geçenler kırmızı.
- Süresi geçmiş kitap varsa sekme adı **Kitap Verme (N gecikmiş)** olur ve panel açılırken uyarı verilir.
- **Ödünç Geçmişi**: tüm ödünç kayıtları; üye, kitap ve duruma (dışarıda / gecikmiş / iade edildi) göre süzülür.

### Kullanıcı yönetimi

Admin panelinde **Giriş → Kullanıcı Yönetimi**: kullanıcıları listeleme, bilgilerini ve yetkisini
düzenleme, şifresini sıfırlama ve silme. Kilitlenmeyi önleyen kurallar:

- Kimse kendi hesabını silemez veya kendi yetkisini değiştiremez.
- Son `admin` kullanıcı silinemez, yetkisi düşürülemez.
- Elinde iade edilmemiş kitap olan kullanıcı silinemez. Silinen kullanıcının ödünç geçmişi korunur.
- Şifreler en az 6 karakter olmalıdır.

Guest kullanıcılar **Giriş → Şifremi Değiştir** ile kendi şifrelerini değiştirebilir (mevcut şifre sorulur).

### Yedekleme

- **Otomatik:** Program her gün ilk açılışta veritabanının yedeğini alır; son 10 otomatik yedek saklanır.
- **Elle:** Admin panelinde **Giriş → Yedek Al** ile istenen yere (ör. USB bellek) yedek alınır.
- **Geri yükleme:** **Giriş → Yedekten Geri Yükle**. Dosya önce doğrulanır (PdSqliteLib veritabanı mı,
  içinde admin kullanıcı var mı); geri yüklemeden önce mevcut halin yedeği otomatik alınır.

Yedekler veritabanının yanındaki `yedekler/` klasöründedir
(`data/yedekler/` veya `~/Library/Application Support/PdSqliteLib/yedekler/`).
Bu klasör aynı diskte durduğu için ara sıra harici bir diske de yedek almanız önerilir.

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

## Testler

Testler geçici bir veritabanı kullanır; gerçek verilere dokunmaz ve pencere açmaz.

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest
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
acodes/kullanici_yonetimi.py  Kullanıcı yönetimi ve şifre değiştirme pencereleri
acodes/odunc_gecmisi.py       Kitap Verme > Ödünç Geçmişi sekmesi
acodes/grafikler.py           İstatistik > Grafikler (veritabanından her seferinde çizilir)
acodes/tablo.py               Tablo doldurma, Türkçe sıralama, satır vurgulama
acodes/disa_aktar.py          Tabloları Excel / CSV olarak kaydetme
acodes/veri_duzeltme.py       Kitap Kayıt > Veri Düzeltme sekmesi
bforms/              .ui dosyalarından üretilen formlar (elle düzenlenmez)
cuis/                Qt Designer .ui kaynakları
database/dbbase.py   Yazma işlemleri, şifre hash'leme, veritabanı yolu
database/dbframe.py  Okuma, filtreleme ve raporlar
database/sema.py     Tablo şeması (eksik tablolar açılışta oluşturulur)
database/yedek.py    Yedek alma ve geri yükleme
database/odunc.py    Teslim tarihi, gecikme ve ödünç geçmişi
database/duzeltme.py Benzer yazımları bulma ve birleştirme, eksik bilgiler
tests/               Otomatik testler (pytest)
media/               Resimler, ikon ve media.qrc
scripts/             Dönüştürme, veri aktarma ve paketleme betikleri
data/                Veritabanı ve yedekler (git dışında)
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
