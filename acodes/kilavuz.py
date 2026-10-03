## Ayarlar > Yardım > Kullanma Kılavuzu (ayrı pencerede) ##
# En üstte program hakkında kısa bilgi, altında her sekme için tıklanınca açılan konu başlıkları.
# Yönetici ve üye panelleri kendi sekmelerine göre farklı konular gösterir.

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout

from acodes import tema
from database.odunc import ODUNC_SURESI_GUN
from database.yedek import GUVENLIK_SAKLA, OTOMATIK_SAKLA

URETICI = "IY Labs"
URETIM_YILI = 2025
IMZA = f"{URETICI} · {URETIM_YILI}"      # giriş ekranında ve kılavuzda gösterilir

HAKKINDA = (
    "<b>Yaşar Kütüphanesi</b> (PdSqliteLib), ev ya da küçük kurum kütüphaneleri için hazırlanmış bir masaüstü "
    "programıdır. Kitapların kaydını tutar, üyelere ödünç verilen kitapları ve teslim tarihlerini izler, "
    "kitaplığın istatistiklerini gösterir. Veriler bilgisayardaki tek bir veritabanı dosyasında saklanır; "
    "internet bağlantısı gerekmez. Python, PyQt5 ve SQLite ile yazılmıştır.<br><br>"
    f"<b>{URETICI}</b> tarafından {URETIM_YILI} yılında üretilmiştir.<br><br>"
    "Programı iki tür kullanıcı kullanır: <b>yönetici</b> kitapları, üyeleri ve ödünç işlemlerini yönetir; "
    "<b>üye</b> kitapları arar, istatistikleri görür ve kendi ödünç aldığı kitapları izler. "
    "Aşağıdaki başlıklara tıklayarak her bölümün nasıl kullanıldığını okuyabilirsiniz."
)

ORTAK_ARAMA = (
    "Aramalarda büyük/küçük harf ve Türkçe karakter farkı gözetilmez: <i>sahin</i> yazınca <i>Şahin</i>, "
    "<i>kuyucakli</i> yazınca <i>Kuyucaklı</i> bulunur. Birden fazla kelime yazılırsa hepsini içeren kayıtlar "
    "gelir (<i>tahir yol</i> → <i>Yol Ayrımı</i>)."
)

KITAP_LISTESI = (
    "Sekmeye gelince bütün kitaplar kendiliğinden listelenir. Üstteki kutuya yazdıkça liste süzülür; kitap adı, "
    "yazar, çevirmen, tür, yayınevi, yıl, ISBN, raf yeri ve notlarda aranır. " + ORTAK_ARAMA + "<br><br>"
    "<b>Durum</b> kolonu kitabın şu an rafta mı ödünçte mi olduğunu gösterir: <i>Rafta</i> yeşil, "
    "<i>Ödünçte</i> kırmızı; birden fazla kopyası olan kitaplarda kaç kopyanın rafta olduğu turuncu yazar "
    "(<i>1/2 kopya rafta</i>). Filtre sonuçlarında da aynı kolon vardır.<br><br>"
    "Kolon başlığına tıklayınca liste o kolona göre sıralanır (tekrar tıklayınca ters sırada). "
    "<b>Kolonlar</b> butonu (veya kolon başlığına sağ tık) listede gösterilecek kolonları seçtirir; liste "
    "pencereye sığmazsa tablonun üstünde hangi kolonların gizleneceği sorulur. Seçim hatırlanır. "
    "Başlangıçta <i>Kayıt No</i> (soldaki sıra numarası aynı işi görür) ve <i>ISBN</i> gizlidir; "
    "<b>Kolonlar</b>'dan açılabilir. "
    "<b>Temizle</b> aramayı silip tüm listeye döner. <b>Dışa Aktar</b> listeyi ekranda göründüğü haliyle "
    "Excel veya CSV dosyası olarak kaydeder; tabloya sağ tıklayarak da aktarabilirsiniz."
)

FILTRE = (
    "Tür, yazar, yayınevi ve yıl ölçütleri sayfanın üstünde yan yana durur, sonuçlar altlarında listelenir. "
    "Başlığın yanındaki <b>ⓘ</b> simgesinin üzerine gelince kısa bir açıklama görünür.<ul>"
    "<li>Ölçüt kutusuna yazmak arama gibi süzer: türe <i>şiir</i> yazınca türü şiir olan kitaplar listelenir.</li>"
    "<li>Diğer ölçütlerin listelerinde yalnızca bu kitaplarda geçen değerler kalır: yazar listesinde sadece "
    "şiir kitabı olan yazarlar görünür.</li>"
    "<li>Listeden seçilen değer ölçütün altında etikete dönüşür; etikete tıklamak seçimi kaldırır. "
    "Aynı ölçütte birden fazla değer seçilebilir.</li>"
    "<li>Aynı ölçütteki seçimlerden <b>biri</b>, farklı ölçütlerin <b>hepsi</b> tutmalıdır: "
    "<i>Roman veya Hikaye</i> <b>ve</b> <i>Kemal TAHİR</i>.</li></ul>"
    "Sonuçlar her değişiklikte kendiliğinden güncellenir. <b>Temizle</b> tüm seçimleri kaldırır, "
    "<b>Dışa Aktar</b> sonuçları kaydeder."
)

ISTATISTIK = (
    "<b>Çizelgeler</b> alt sekmesi en çok kitabı olan türleri, yazarları, yayınevlerini ve basım yıllarını "
    "sayılarıyla listeler; her sayının yanındaki çubuk o değerin en büyüğe oranını gösterir, böylece dağılım "
    "bir bakışta görülür. <b>Grafikler</b> alt sekmesi türlere göre dağılımı, en çok kitabı olan yazar ve "
    "yayınevlerini ve on yıllık dönemlere göre basım yıllarını grafikle gösterir. Bilgiler her açılışta "
    "veritabanından yeniden hesaplanır."
)

YEDEKLEME = (
    "<b>Yedek</b>, bütün kütüphanenin (kitaplar, üyeler, ödünç kayıtları) tek bir <i>.db</i> dosyası olarak "
    "kopyasıdır; program açıkken alınsa da tutarlıdır.<ul>"
    f"<li><b>Otomatik yedek:</b> Program her gün ilk açıldığında kendiliğinden yedek alır; son {OTOMATIK_SAKLA} "
    "otomatik yedek saklanır, daha eskileri silinir. Dosya adı tarih ve saati gösterir "
    "(<i>DBL_Kayit_20261001_001948.db</i>).</li>"
    "<li><b>Güvenlik yedekleri:</b> Geri alınması zor işlemlerden önce de yedek alınır: Veri Düzeltme'de "
    "birleştirmeden önce (<i>duzeltme_oncesi_...</i>) ve yedekten geri yüklemeden önce mevcut hal "
    f"(<i>geri_yukleme_oncesi_...</i>). Her türden son {GUVENLIK_SAKLA} tanesi saklanır.</li>"
    "<li><b>Yedek klasörü:</b> Veritabanının yanındaki <i>yedekler</i> klasörüdür (Mac'te "
    "<i>~/Library/Application Support/PdSqliteLib/yedekler</i>, Windows'ta "
    "<i>%APPDATA%\\PdSqliteLib\\yedekler</i>). <b>Ayarlar → Yedek Klasörünü Aç</b> bu klasörü açar.</li>"
    "<li><b>Yedek Al:</b> Yedeği istediğiniz yere kaydeder. Otomatik yedekler aynı bilgisayarda durduğu için "
    "disk arızasına karşı korumaz; ara sıra USB belleğe veya bulut klasörüne yedek alın.</li>"
    "<li><b>Yedekten Geri Yükle:</b> Seçilen yedeğe döner; mevcut tüm kayıtlar o yedektekilerle değişir. "
    "Önce mevcut halin yedeği alınır, yani yanlışlıkla yapılırsa geri dönülebilir. Geçerli bir kütüphane "
    "yedeği olmayan dosya yüklenmez; eski sürümlerin yedeklerine yeni alanlar kendiliğinden eklenir.</li>"
    "<li><b>Mac ↔ Windows:</b> Bir bilgisayarda <b>Yedek Al</b> ile USB belleğe kaydedip diğerinde "
    "<b>Yedekten Geri Yükle</b> ile açarak veriyi taşıyabilirsiniz.</li></ul>"
)

DISA_AKTARMA = (
    "<b>Dışa aktarma</b> bir listeyi rapor veya çıktı için Excel ya da CSV dosyasına kaydeder; geri "
    "yüklenemez, yedek yerine geçmez.<ul>"
    "<li><b>Dışa Aktar</b> butonu Kitap Listesi, Filtre sonuçları, dışarıdaki kitaplar ve Ödünç Geçmişi'nde "
    "vardır; bütün tablolarda (İstatistik çizelgeleri dahil) sağ tıklayıp <i>Excel / CSV olarak dışa "
    "aktar</i> da seçilebilir.</li>"
    "<li>Tablo ekranda nasıl görünüyorsa öyle kaydedilir: arama, filtre, sıralama ve gizlenen kolonlar dahil.</li>"
    "<li><b>Excel (.xlsx):</b> kalın başlık, sabit ilk satır ve filtre okları; sayılar ve tarihler Excel'de "
    "hesaplanabilir. <b>CSV:</b> Türkçe karakterler bozulmadan, kolonlara ayrılmış olarak Excel'de açılır.</li>"
    "<li>Önerilen dosya adı liste adı ve tarihtir (<i>Kitap_Listesi_20261001.xlsx</i>); kayıt yeri olarak "
    "Belgeler klasörü önerilir.</li></ul>"
)

def kisayollar_ve_gorunum(yonetici):
    kayit = ("<li>Kitap Kayıt ekranında <b>Ctrl+N</b> yeni kitap, <b>Ctrl+S</b> kaydet, <b>Esc</b> vazgeç "
             "(kaydedilmemiş değişiklikleri geri alır).</li>") if yonetici else ""
    hizli = ("kitap, üye (seçince ödünç verme ekranı o üyeyle açılır), bölüm veya işlem (<i>yeni kitap</i>, "
             "<i>yedek al</i>, <i>iade al</i> ...)") if yonetici else "kitap veya bölüm"
    return ("Mac'te <b>Ctrl</b> yerine <b>⌘ (Cmd)</b> tuşu kullanılır.<ul>"
            f"<li><b>Ctrl+K</b> her yerden <b>hızlı aramayı</b> açar (menüdeki <i>Hızlı ara</i> da aynısını yapar): "
            f"{hizli} adını yazın, ok tuşlarıyla seçip Enter'a basın. Esc kapatır.</li>"
            "<li><b>Ctrl+1</b>, <b>Ctrl+2</b> ... menüdeki bölümleri yukarıdan aşağıya sırayla açar.</li>"
            "<li><b>Ctrl+F</b> açık sayfadaki arama kutusuna gider; sayfada arama yoksa Kitap Listesi'ni açıp "
            "aramaya gider.</li>" + kayit + "</ul>"
            "<b>Görünüm:</b> <b>Ayarlar → Görünüm</b> bölümünden açık veya koyu renkler seçilebilir; "
            "<b>Sistemle aynı</b> bilgisayarın açık/koyu ayarını izler. Seçim hemen uygulanır ve hatırlanır.")


YONETICI = [
    ("Menü ve gezinme",
     "Bölümler soldaki menüdedir; açık bölüm mavi zeminle işaretlenir. Menünün sağ üstündeki düğme menüyü "
     "daraltır: yalnızca simgeler kalır, içeriğe daha çok yer açılır (simgenin üzerine gelince bölümün adı görünür); "
     "aynı düğme menüyü yeniden açar. Bu tercih bir sonraki açılışta hatırlanır. Menünün altında kullanıcı "
     "adınız, yetkiniz ve <b>Oturumu Kapat</b> vardır. Alt bölümleri olan sayfalarda (ör. Kitaplar / Veri "
     "Düzeltme) sayfanın üstündeki anahtar kullanılır."),
    ("Giriş (ana sayfa)",
     "Özet kartları kitap, dışarıdaki, geciken ve üye sayılarını gösterir; bir karta tıklamak ilgili sekmeyi "
     "açar. <b>Teslimi yaklaşan ve geciken kitaplar</b> listesinde bir satıra çift tıklamak o ödüncü iade "
     "ekranında seçili olarak açar. <b>Son eklenen kitaplar</b> listesinde çift tıklamak kitabı düzenleme "
     "ekranında açar. Programdan çıkmak için önce oturumu kapatıp giriş ekranındaki çıkış düğmesini "
     "kullanın."),
    ("Kitap Listesi",
     KITAP_LISTESI + " Bir satıra çift tıklamak kitabı <b>Kitap Kayıt</b> ekranında açar. Satıra sağ "
     "tıklayınca <b>Düzenle</b>, <b>Ödünç ver</b> (kitap seçili gelir, yalnızca üyeyi seçersiniz), "
     "<b>İade al</b> ve <b>Ödünç geçmişi</b> seçenekleri çıkar."),
    ("Kitap Kayıt: kitap ekleme, düzenleme, silme",
     "<b>Kitaplar</b> alt sekmesinde üstte tam genişlikte kitap listesi, altta seçili kitabın formu vardır; Kaydet, Vazgeç ve Sil formun üstündedir.<ul>"
     "<li><b>Yeni kitap:</b> <b>Yeni Kitap</b>'a basın, bilgileri yazıp <b>Kaydet</b>'e basın. "
     "Yalnızca kitap adı zorunludur.</li>"
     "<li><b>Düzenleme:</b> Listeden kitabı seçin, bilgileri değiştirip <b>Kaydet</b>'e basın. "
     "<b>Vazgeç</b> kaydedilmemiş değişiklikleri geri alır.</li>"
     "<li><b>Silme:</b> Kitabı seçip <b>Sil</b>'e basın. Ödünçteki bir kitap iade alınmadan silinemez. "
     "Yanlışlıkla sildiyseniz, alttaki bildirimdeki <b>Geri Al</b>'a birkaç saniye içinde basarak kitabı aynı "
     "numara ve bilgilerle geri getirebilirsiniz.</li>"
     "<li>Yazar, çevirmen, tür ve yayınevi alanlarına yazarken var olan değerler önerilir; öneriden seçmek "
     "aynı adın farklı yazımlarını önler.</li>"
     "<li><b>Ek Bilgiler:</b> ISBN (yazılırsa doğruluğu kontrol edilir), kopya sayısı, raf yeri ve notlar. "
     "Kopya sayısı kadar üyeye aynı kitap aynı anda verilebilir.</li></ul>"
     "<b>Veri Düzeltme</b> alt sekmesi aynı yazar, yayınevi, çevirmen veya türün farklı yazımlarını "
     "(<i>Adam Yayınları</i> / <i>Adam yayınları</i>) bulur. Doğru yazımı seçip "
     "<b>İşaretlileri Birleştir</b>'e basınca kayıtlar düzeltilir; öncesinde otomatik yedek alınır. "
     "Basım yılı, yazar gibi bilgisi eksik kitaplar da burada listelenir."),
    ("Filtre", FILTRE + " Bir satıra çift tıklamak kitabı düzenleme ekranında açar; sağ tıklayınca Kitap "
     "Listesi'ndeki işlemler (ödünç ver, iade al ...) çıkar."),
    ("İstatistik", ISTATISTIK),
    ("Kitap Verme: ödünç verme ve iade alma",
     f"Ödünç süresi <b>{ODUNC_SURESI_GUN} gündür</b>. <b>Ödünç ve İade</b> alt sekmesinde üstte, tam genişlikte şu an "
     "dışarıdaki kitaplar listelenir; teslim süresi geçenler kırmızıdır. Kitap, yazar veya üye adıyla "
     "aranabilir. İşlem kartları listenin altında yan yana durur.<ul>"
     "<li><b>Ödünç verme:</b> <b>Ödünç ver</b> kartında kitabı ve üyeyi seçin (yazarak arayabilirsiniz). "
     "Kitabın müsait kopya sayısı, üyenin elindeki ve geciken kitapları ile teslim tarihi gösterilir. "
     "<b>Ödünç Ver</b>'e basın. Kitabın müsait kopyası yoksa ya da üyede zaten varsa buton kapalı kalır "
     "ve nedeni yazılır.</li>"
     "<li><b>İade alma:</b> Üstteki listeden kitabı seçin; bilgileri <b>İade al</b> kartında görünür. "
     "<b>İade Al</b>'a basın; onay sorulmaz. Gecikme varsa kaç gün geciktiği bildirilir. Yanlış kitabı iade "
     "aldıysanız bildirimdeki <b>Geri Al</b> ile birkaç saniye içinde geri alabilirsiniz.</li>"
     "<li><b>Hatırlatma:</b> Listeden bir ödünç seçip <b>Hatırlatma Metni</b>'ne basın: üyeye gönderilecek "
     "kibar bir mesaj (kitap adı, teslim tarihi, gecikme) panoya kopyalanır; telefon mesajına veya e-postaya "
     "yapıştırabilirsiniz.</li></ul>"
     "Teslim süresi geçmiş kitap varsa sekmenin adında sayısı yazar (<i>Kitap Verme (2 gecikmiş)</i>). "
     "<b>Ödünç Geçmişi</b> alt sekmesi tüm ödünç kayıtlarını gösterir; üye, kitap ve duruma göre süzülebilir."),
    ("Ayarlar: kullanıcılar ve yedekleme",
     "<b>Yeni Kullanıcı Ekle</b> ile üye (guest) veya yönetici (admin) kaydı açılır. "
     "<b>Kullanıcı Yönetimi</b>nde kullanıcıların bilgileri ve yetkileri düzenlenir, şifreleri sıfırlanır "
     "veya silinir; elinde kitap olan kullanıcı ve son yönetici silinemez. <b>Şifremi Değiştir</b> kendi "
     "şifrenizi değiştirir. Yedekleme butonları için <b>Yedekleme ve dışa aktarma</b> başlığına bakın."),
    ("Yedekleme ve dışa aktarma", YEDEKLEME + "<br><br>" + DISA_AKTARMA),
    ("Kısayollar ve görünüm", kisayollar_ve_gorunum(yonetici=True)),
    ("İpuçları",
     "<ul><li>Aradığınız şeyin nerede olduğunu bilmiyorsanız <b>Ctrl+K</b> ile hızlı aramayı açıp yazın.</li>"
     "<li>Uzun açılır listelerde (kitap, üye, filtre ölçütleri) kaydırmak yerine yazarak arayın.</li>"
     "<li>İşlemlerin sonucu pencerenin altında birkaç saniye görünen bildirimlerle haber verilir: "
     "başarılı işlemler yeşil, uyarılar kırmızı. Kitap silme ve iade alma bildirimlerinde <b>Geri Al</b> "
     "butonu vardır.</li>"
     "<li>Tüm tablolar kolon başlığına tıklanarak sıralanabilir; sağ tıklayarak Excel/CSV'ye aktarılabilir.</li>"
     "</ul>"),
]

UYE = [
    ("Menü ve gezinme",
     "Bölümler soldaki menüdedir; açık bölüm mavi zeminle işaretlenir. Menünün sağ üstündeki düğme menüyü "
     "daraltır: yalnızca simgeler kalır, içeriğe daha çok yer açılır (simgenin üzerine gelince bölümün adı görünür); "
     "aynı düğme menüyü yeniden açar. Bu tercih bir sonraki açılışta hatırlanır. Menünün altında kullanıcı "
     "adınız, yetkiniz ve <b>Oturumu Kapat</b> vardır. Alt bölümleri olan sayfalarda (ör. Kitaplar / Veri "
     "Düzeltme) sayfanın üstündeki anahtar kullanılır."),
    ("Giriş (ana sayfa)",
     "Özet kartları kütüphanedeki kitap sayısını, elinizdeki ve gecikmiş kitapları ve en yakın teslim "
     "tarihini gösterir; bir karta tıklamak ilgili sekmeyi açar."),
    ("Kitap Listesi", KITAP_LISTESI),
    ("Filtre", FILTRE),
    ("İstatistik", ISTATISTIK),
    ("Kitaplarım",
     f"Elinizdeki kitaplar, aldığınız tarih, teslim tarihi ve kalan gün sayısıyla listelenir (ödünç süresi "
     f"{ODUNC_SURESI_GUN} gün). Teslim süresi geçen kitaplar kırmızıdır ve sekmenin adında sayısı yazar. "
     "Daha önce aldığınız kitaplar da ne zaman aldığınız ve iade ettiğiniz bilgisiyle aşağıda görünür. "
     "Kitap ödünç almak veya iade etmek için kütüphane yöneticisine başvurun."),
    ("Dışa aktarma", DISA_AKTARMA),
    ("Ayarlar: hesabım",
     "<b>Hesabım</b> bölümünde kullanıcı adınız, adınız ve iletişim bilgileriniz görünür. "
     "<b>Şifremi Değiştir</b> ile mevcut şifrenizi girerek yeni şifre belirleyebilirsiniz. "
     "Bilgilerinizin değişmesi gerekiyorsa kütüphane yöneticisine başvurun."),
    ("Kısayollar ve görünüm", kisayollar_ve_gorunum(yonetici=False)),
]

def stil():
    return f"""
#kilavuz_hakkinda {{ color: {tema.METIN}; font-size: 16px; font-weight: normal; }}
QPushButton#kilavuz_konu {{ background: transparent; color: {tema.METIN}; border: none; border-radius: 0;
               border-top: 1px solid {tema.KENAR}; padding: 10px 4px; min-width: 0; text-align: left;
               font-size: 17px; font-weight: {tema.YARI_KALIN}; }}
QPushButton#kilavuz_konu:hover {{ color: {tema.VURGU_YAZI}; }}
QPushButton#kilavuz_konu:checked {{ color: {tema.VURGU_YAZI}; }}
#kilavuz_metin {{ color: {tema.METIN}; font-size: 16px; font-weight: normal; padding: 0 8px 10px 22px; }}
"""


class Kilavuz(QGroupBox):
    """Program hakkında bilgi ve tıklanınca açılan konu başlıkları (aynı anda bir konu açık)."""

    def __init__(self, konular, parent=None):
        super().__init__("Kullanma Kılavuzu", parent)
        self.setStyleSheet(stil())
        duzen = QVBoxLayout(self)
        duzen.setSpacing(0)
        hakkinda = QLabel(HAKKINDA, objectName="kilavuz_hakkinda")
        hakkinda.setWordWrap(True)
        hakkinda.setContentsMargins(0, 0, 0, 12)
        duzen.addWidget(hakkinda)
        self.konular = []
        for baslik, metin in konular:
            buton = QPushButton(f"▸  {baslik}", objectName="kilavuz_konu")
            buton.setCheckable(True)
            buton.setCursor(Qt.PointingHandCursor)
            yazi = QLabel(metin, objectName="kilavuz_metin")
            yazi.setWordWrap(True)
            yazi.setTextFormat(Qt.RichText)
            yazi.hide()
            buton.toggled.connect(lambda acik, i=len(self.konular): self.ac(i, acik))
            duzen.addWidget(buton)
            duzen.addWidget(yazi)
            self.konular.append((baslik, buton, yazi))

    def ac(self, secilen, acik=True):
        for i, (baslik, buton, yazi) in enumerate(self.konular):
            goster = acik and i == secilen
            buton.blockSignals(True)
            buton.setChecked(goster)
            buton.blockSignals(False)
            buton.setText(f"{'▾' if goster else '▸'}  {baslik}")
            yazi.setVisible(goster)

    def yenile(self):
        pass    # Ayarlar sekmesi yenilenirken diğer bölümlerle aynı arayüz
