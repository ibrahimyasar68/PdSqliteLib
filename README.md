# PdSqliteLib

PyQt5, SQLite ve pandas ile yazılmış masaüstü kütüphane yönetim uygulaması.
Kitap kaydı, üye yönetimi, ödünç verme / iade takibi ve istatistikler içerir.
Windows ve macOS üzerinde çalışır.

**IY Labs** tarafından 2025 yılında üretilmiştir.

## Özellikler

Giriş ekranında kullanıcının yetkisine göre iki farklı panel açılır:

| Sekme | Admin | Guest |
|---|:---:|:---:|
| **Giriş**: özet panosu (kitap, dışarıdaki, geciken sayıları; yaklaşan teslimler; son eklenenler) | ✓ | ✓ (kendi kitapları) |
| **Kitap Listesi**: tüm kitaplar, anlık arama | ✓ | ✓ |
| **Kitap Kayıt**: tek ekranda ekleme, güncelleme, silme; veri düzeltme | ✓ | |
| **Filtre**: tür, yazar, yayınevi ve yıl tek panelde, çoklu seçim | ✓ | ✓ |
| **İstatistik**: çizelgeler ve güncel grafikler (tür, yazar, yayınevi, basım yılı) | ✓ | ✓ |
| **Kitap Verme**: ödünç verme, iade alma ve dışarıdaki kitaplar tek ekranda; ödünç geçmişi | ✓ | |
| **Kitaplarım**: üyenin elindeki kitaplar (teslim tarihi, kalan gün) ve geçmişi | | ✓ |
| **Ayarlar**: kullanıcılar, yedekleme, kütüphane bilgileri / hesap bilgileri ve şifre; kullanma kılavuzu | ✓ | ✓ (Hesabım) |

Panellerdeki **Oturumu Kapat** butonu giriş ekranına döner; başka bir kullanıcıyla giriş yapılabilir.
Programdan çıkmak için giriş ekranındaki kırmızı çıkış butonu kullanılır. Paneller macOS'ta büyütülmüş
pencerede (küçültülebilir, diğer programlara geçilebilir), Windows'ta tam ekran açılır.
Panellerin arka planı yaprak fotoğrafıdır (`media/autumn.jpg`). Giriş sekmesinde fotoğraf olduğu gibi
görünür; diğer sayfalar yarı saydam olduğu için içeriğin arkasından hafifçe görünür, tablolar ve formlar
okunaklı kalsın diye beyazdır (saydamlık `acodes/arka_plan.py` içindeki `SAYFA_SAYDAMLIK` ile ayarlanır).

**Ayarlar**'ın en altında **Kullanma Kılavuzu** vardır: program hakkında kısa bilgi ve her sekmenin nasıl
kullanıldığını anlatan, tıklanınca açılan başlıklar (yönetici ve üye panellerinde kendi sekmelerine göre).

Yeni kullanıcı ve üye kayıtlarını (`admin` veya `guest`) sadece giriş yapmış bir admin,
**Ayarlar → Yeni Kullanıcı Ekle** ile oluşturabilir.

### Arama

**Kitap Listesi** sekmesine gelince tüm kitaplar kendiliğinden listelenir (her gelişte güncel hali);
arama kutusu yazdıkça sonuçları günceller, **Temizle** aramayı silip tüm listeye döner. Kitap adı, yazar, çevirmen,
tür, yayınevi ve yılda arar; büyük/küçük harf ve Türkçe karakter farkı gözetmez ("sahin" → "Şahin",
"kuyucakli" → "Kuyucaklı"). Birden fazla kelime yazılırsa hepsini içeren kitaplar listelenir.

### Kitap kayıt ekranı

**Kitap Kayıt → Kitaplar** ekranında solda aranabilir kitap listesi, sağda seçili kitabın formu vardır.
Listeden bir kitap seçince bilgileri forma gelir; değiştirip **Kaydet**'e basmak günceller, **Sil**
siler (ödünçteki kitap iade alınmadan silinemez), **Vazgeç** kaydedilmemiş değişiklikleri geri alır.
**Yeni Kitap** formu boşaltır; Kaydet yeni kitabı ekler ve listede seçili bırakır. Yazar, çevirmen,
tür ve yayınevi alanlarında yazdıkça mevcut değerler önerilir (yazım farklılıklarını önler).

### Filtre

**Filtre** sekmesinde tür, yazar, yayınevi ve yıl ölçütleri tek panelde yan yana durur.

- Ölçüt kutusuna yazmak Kitap Listesi'ndeki arama gibi süzer; büyük/küçük harf ve Türkçe karakter
  farkı gözetilmez ("şiir" yazınca türü "Şiir" veya "şiir" olan kitaplar gelir).
- Diğer ölçütlerin listelerinde yalnızca süzülen kitaplarda geçen değerler kalır: türe "şiir" yazınca
  yazar listesinde sadece şiir kitabı olan yazarlar, yıl listesinde o kitapların yılları görünür.
- Listeden seçilen değer ölçütün altında etikete dönüşür (etikete tıklamak kaldırır); böylece bir ölçütte
  birden fazla değer seçilebilir. Aynı ölçütteki seçimlerden **biri**, farklı ölçütlerin **hepsi**
  tutmalıdır ("Roman veya Hikaye" **ve** "Kemal TAHİR").
- Sonuçlar her değişiklikte kendiliğinden güncellenir; **Temizle** tüm seçimleri ve aramaları kaldırır.

### Aranabilir listeler

Kitap Verme'deki kitap/üye seçimleri ile Filtre'deki tür, yazar, yayınevi ve yıl
listelerine yazdıkça liste süzülür ("iklim" → iki "İklimler" baskısı); büyük/küçük harf ve Türkçe
karakter farkı gözetilmez.

### Tablolar

- Listelerin solunda kayıt numarasından bağımsız bir **sıra numarası** vardır; 1'den başlar, sıralama
  değişince de ekrandaki sıraya göre numaralanır. Son numara listedeki kayıt sayısını gösterir.
- Kolon başlığına tıklayınca tablo o kolona göre sıralanır (tekrar tıklayınca ters sırada).
  Sayılar sayı olarak, tarihler tarih olarak, metinler Türk alfabesine göre sıralanır; boşlar en sona gider.
- Hücreler salt okunurdur; değişiklikler ilgili düzenleme ekranlarından yapılır.
- Admin panelinde **Kitap Listesi** veya **Filtre** sonuçlarında bir satıra çift tıklamak kitabı
  **Kitap Kayıt → Kitaplar** ekranında açar.
- Ana sayfadaki teslimi yaklaşan bir kitaba çift tıklamak **Kitap Verme → Ödünç ve İade** ekranını
  o ödünç seçili olarak açar; sadece **İade Al**'a basmak kalır.

### Ek bilgiler: ISBN, kopya sayısı, raf yeri, notlar

Kitap Kayıt formundaki **Ek Bilgiler** kutusunda girilir; Kitap Listesi'nde ISBN, Kopya ve Raf
kolonları görünür, arama bu alanlarda ve notlarda da yapılır.

- **ISBN** isteğe bağlıdır; yazılırsa ISBN-10 / ISBN-13 kontrol basamağı doğrulanır, tiresiz saklanır.
- **Kopya sayısı** kadar üyeye aynı kitap aynı anda ödünç verilebilir (verirken müsait kopya gösterilir).
  Bir üyeye aynı kitabın ikinci kopyası verilmez; kopya sayısı dışarıdaki kopya sayısının altına düşürülemez.
- Eski veritabanları ve yedekler açılışta bu alanlarla otomatik güncellenir (mevcut kitaplar 1 kopya).

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

Kitap Listesi, Filtre sonuçları, dışarıdaki kitaplar ve Ödünç Geçmişi'nde **Dışa Aktar** butonu vardır;
tüm tablolarda (İstatistik çizelgeleri dahil) sağ tıklayarak da aktarılabilir. Tablo ekranda nasıl
görünüyorsa (arama, filtre, sıralama) öyle kaydedilir.

- **Excel (.xlsx):** kalın başlık, sabit ilk satır ve otomatik filtre. Sayılar sayı, tarihler tarih
  olarak yazılır; telefon gibi uzun rakam dizileri baştaki sıfır kaybolmasın diye metin kalır.
- **CSV:** Türkçe Excel'in doğrudan açabileceği biçimde (UTF-8, `;` ayırıcı).

### Ödünç takibi

- Ödünç süresi **15 gündür** (`database/odunc.py` içindeki `ODUNC_SURESI_GUN`). Teslim tarihi veriliş
  tarihinden hesaplanır; eski kayıtlar için de geçerlidir.
- **Kitap Verme → Ödünç ve İade** ekranı tek yerde:
  - Solda dışarıdaki kitaplar: veriliş ve teslim tarihi, kalan veya geciken gün; süresi geçenler kırmızı.
    Kitap, yazar veya üye adıyla aranabilir.
  - **Ödünç ver** kartı: kitap ve üye seçilince bilgileri kendiliğinden gelir. Müsait kopya sayısı,
    üyenin elindeki ve geciken kitapları ile teslim tarihi gösterilir. Kitabın müsait kopyası yoksa
    veya üyede zaten varsa **Ödünç Ver** kapalı kalır ve nedeni yazılır.
  - **İade al** kartı: listeden seçilen ödüncün bilgileri ve gecikmesi; **İade Al** ile kapatılır.
    Silinmiş bir üyenin ödüncü de iade alınabilir.
- Süresi geçmiş kitap varsa sekme adı **Kitap Verme (N gecikmiş)** olur ve panel açılırken uyarı verilir.
- **Ödünç Geçmişi**: tüm ödünç kayıtları; üye, kitap ve duruma (dışarıda / gecikmiş / iade edildi) göre süzülür.
- Üyeler kendi panellerindeki **Kitaplarım** sekmesinde elindeki kitapları, teslim tarihini ve kalan
  günü ("5 gün kaldı", "3 gün gecikti") görür; gecikmiş kitabı olan üye girişte uyarılır.

### Kullanıcı yönetimi

Admin panelinde **Ayarlar → Kullanıcı Yönetimi**: kullanıcıları listeleme, bilgilerini ve yetkisini
düzenleme, şifresini sıfırlama ve silme. Kilitlenmeyi önleyen kurallar:

- Kimse kendi hesabını silemez veya kendi yetkisini değiştiremez.
- Son `admin` kullanıcı silinemez, yetkisi düşürülemez.
- Elinde iade edilmemiş kitap olan kullanıcı silinemez. Silinen kullanıcının ödünç geçmişi korunur.
- Şifreler en az 6 karakter olmalıdır.

Herkes **Ayarlar → Şifremi Değiştir** ile kendi şifresini değiştirebilir (mevcut şifre sorulur).

### Yedekleme

- **Otomatik:** Program her gün ilk açılışta veritabanının yedeğini alır; son 10 otomatik yedek saklanır.
- **Elle:** Admin panelinde **Ayarlar → Yedek Al** ile istenen yere (ör. USB bellek) yedek alınır.
- **Geri yükleme:** **Ayarlar → Yedekten Geri Yükle**. Dosya önce doğrulanır (PdSqliteLib veritabanı mı,
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

## Windows

**Kurulum ve çalıştırma:** [python.org](https://www.python.org/downloads/windows/) adresinden Python 3.9+
kurun ("Add python.exe to PATH" işaretli), veritabanını `data\DBL_Kayit.db` olarak koyun ve
`scripts\baslat_windows.bat` dosyasına çift tıklayın. İlk çalıştırmada sanal ortam kurulur, sonra program
konsol penceresi açılmadan başlar. Masaüstü kısayolu için dosyaya sağ tık → **Kısayol oluştur**.

**Program paketi (.exe):** Windows'ta proje klasöründe:

```bat
scripts\build_windows.bat
```

Çıktı `dist\PdSqliteLib\` klasörüdür; `PdSqliteLib.exe` bu klasördeki diğer dosyalarla birlikte çalışır,
başka bir bilgisayara klasörün tamamı (örneğin zip olarak) taşınır. Paketlenmiş program veritabanını
`%APPDATA%\PdSqliteLib\` altında tutar ve ilk açılışta pakete eklenen veritabanını oraya kopyalar.
Paket imzasız olduğu için Windows SmartScreen ilk açılışta uyarabilir: **Ek bilgi → Yine de çalıştır**.

## Proje yapısı

```
main.py              Giriş noktası
acodes/              Pencerelerin iş mantığı (login, library, guest, user)
acodes/ortak.py      Admin ve Guest panellerinde ortak sekmeler (liste, filtre, istatistik)
acodes/tema.py       Tek renk teması (renkler burada; .ui dosyalarındaki renkler açılışta silinir)
acodes/kullanici_yonetimi.py  Kullanıcı yönetimi ve şifre değiştirme pencereleri
acodes/odunc_ekrani.py        Kitap Verme > Ödünç ve İade (ödünç verme, iade, dışarıdakiler tek ekranda)
acodes/odunc_gecmisi.py       Kitap Verme > Ödünç Geçmişi sekmesi
acodes/grafikler.py           İstatistik > Grafikler (veritabanından her seferinde çizilir)
acodes/tablo.py               Tablo doldurma, Türkçe sıralama, satır vurgulama, boş tablo mesajı
acodes/aranabilir.py          Yazdıkça süzülen açılır listeler
acodes/ikonlar.py             Buton ve sekme ikonları (Qt ile çizilir, dosya gerektirmez)
acodes/bildirim.py            Kısa süre görünen bildirimler (başarı yeşil, uyarı kırmızı)
acodes/yerlesim.py            Esnek yerleşim kalıpları (.ui sayfalarını pencereyle büyüyen düzene alır)
acodes/disa_aktar.py          Tabloları Excel / CSV olarak kaydetme
acodes/kitap_ekrani.py        Kitap Kayıt > Kitaplar (liste ve form tek ekranda)
acodes/veri_duzeltme.py       Kitap Kayıt > Veri Düzeltme sekmesi
acodes/filtre_paneli.py       Filtre sekmesi (dört ölçüt tek panelde)
acodes/ek_bilgi.py            Kitap formundaki Ek Bilgiler kutusu, ISBN doğrulama
acodes/kitaplarim.py          Guest paneli > Kitaplarım sekmesi
acodes/ana_sayfa.py           Ana sayfa özet panosu (kartlar ve listeler)
acodes/arka_plan.py           Panellerin arka plan fotoğrafı
acodes/kilavuz.py             Ayarlar > Kullanma Kılavuzu metinleri (yönetici ve üye)
acodes/ayarlar.py             Ayarlar sekmesi (kullanıcılar, yedekleme, bilgiler / hesabım)
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
kayitlistesi (Id INTEGER PRIMARY KEY, Adi, Yazari, Ceviren, Turu, Yayinevi, Yili, Sayfa,
              ISBN, Kopya INTEGER DEFAULT 1, Raf, Notlar)
users        (id INTEGER PRIMARY KEY, kullanici UNIQUE, sifre, adi_soyadi, telefon, mail, yetki)
follow       (userId, bookId, outdate, outtime, status, indate, intime)
```

- `users.yetki`: `admin` veya `guest`
- `users.sifre`: PBKDF2-SHA256 hash'i (`pbkdf2$tekrar$tuz$hash`). Eski düz metin şifreler
  ilk başarılı girişte otomatik olarak hash'e çevrilir.
- `follow.status`: `out` (ödünçte) veya `in` (iade edildi). Her ödünç işlemi yeni bir satırdır;
  iade sadece `out` durumundaki satırı günceller.
