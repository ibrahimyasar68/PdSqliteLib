## Ayarlar > Kullanma Kılavuzu ##
# En üstte program hakkında kısa bilgi, altında her sekme için tıklanınca açılan konu başlıkları.
# Yönetici ve üye panelleri kendi sekmelerine göre farklı konular gösterir.

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout

from acodes import tema
from database.odunc import ODUNC_SURESI_GUN
from database.yedek import OTOMATIK_SAKLA

HAKKINDA = (
    "<b>Yaşar Kütüphanesi</b> (PdSqliteLib), ev ya da küçük kurum kütüphaneleri için hazırlanmış bir masaüstü "
    "programıdır. Kitapların kaydını tutar, üyelere ödünç verilen kitapları ve teslim tarihlerini izler, "
    "kitaplığın istatistiklerini gösterir. Veriler bilgisayardaki tek bir veritabanı dosyasında saklanır; "
    "internet bağlantısı gerekmez. Python, PyQt5 ve SQLite ile yazılmıştır.<br><br>"
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
    "Kolon başlığına tıklayınca liste o kolona göre sıralanır (tekrar tıklayınca ters sırada). "
    "<b>Temizle</b> aramayı silip tüm listeye döner. <b>Dışa Aktar</b> listeyi ekranda göründüğü haliyle "
    "Excel veya CSV dosyası olarak kaydeder; tabloya sağ tıklayarak da aktarabilirsiniz."
)

FILTRE = (
    "Tür, yazar, yayınevi ve yıl ölçütleri tek panelde durur.<ul>"
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
    "sayılarıyla listeler. <b>Grafikler</b> alt sekmesi türlere göre dağılımı, en çok kitabı olan yazar ve "
    "yayınevlerini ve on yıllık dönemlere göre basım yıllarını grafikle gösterir. Bilgiler her açılışta "
    "veritabanından yeniden hesaplanır."
)

YONETICI = [
    ("Giriş (ana sayfa)",
     "Özet kartları kitap, dışarıdaki, geciken ve üye sayılarını gösterir; bir karta tıklamak ilgili sekmeyi "
     "açar. <b>Teslimi yaklaşan ve geciken kitaplar</b> listesinde bir satıra çift tıklamak o ödüncü iade "
     "ekranında seçili olarak açar. <b>Son eklenen kitaplar</b> listesinde çift tıklamak kitabı düzenleme "
     "ekranında açar. <b>Oturumu Kapat</b> giriş ekranına döner; programdan çıkmak için giriş ekranındaki "
     "çıkış düğmesi kullanılır."),
    ("Kitap Listesi",
     KITAP_LISTESI + " Bir satıra çift tıklamak kitabı <b>Kitap Kayıt</b> ekranında açar."),
    ("Kitap Kayıt: kitap ekleme, düzenleme, silme",
     "<b>Kitaplar</b> alt sekmesinde solda kitap listesi, sağda seçili kitabın formu vardır.<ul>"
     "<li><b>Yeni kitap:</b> <b>Yeni Kitap</b>'a basın, bilgileri yazıp <b>Kaydet</b>'e basın. "
     "Yalnızca kitap adı zorunludur.</li>"
     "<li><b>Düzenleme:</b> Listeden kitabı seçin, bilgileri değiştirip <b>Kaydet</b>'e basın. "
     "<b>Vazgeç</b> kaydedilmemiş değişiklikleri geri alır.</li>"
     "<li><b>Silme:</b> Kitabı seçip <b>Sil</b>'e basın. Ödünçteki bir kitap iade alınmadan silinemez.</li>"
     "<li>Yazar, çevirmen, tür ve yayınevi alanlarına yazarken var olan değerler önerilir; öneriden seçmek "
     "aynı adın farklı yazımlarını önler.</li>"
     "<li><b>Ek Bilgiler:</b> ISBN (yazılırsa doğruluğu kontrol edilir), kopya sayısı, raf yeri ve notlar. "
     "Kopya sayısı kadar üyeye aynı kitap aynı anda verilebilir.</li></ul>"
     "<b>Veri Düzeltme</b> alt sekmesi aynı yazar, yayınevi, çevirmen veya türün farklı yazımlarını "
     "(<i>Adam Yayınları</i> / <i>Adam yayınları</i>) bulur. Doğru yazımı seçip "
     "<b>İşaretlileri Birleştir</b>'e basınca kayıtlar düzeltilir; öncesinde otomatik yedek alınır. "
     "Basım yılı, yazar gibi bilgisi eksik kitaplar da burada listelenir."),
    ("Filtre", FILTRE + " Bir satıra çift tıklamak kitabı düzenleme ekranında açar."),
    ("İstatistik", ISTATISTIK),
    ("Kitap Verme: ödünç verme ve iade alma",
     f"Ödünç süresi <b>{ODUNC_SURESI_GUN} gündür</b>. <b>Ödünç ve İade</b> alt sekmesinde solda şu an "
     "dışarıdaki kitaplar listelenir; teslim süresi geçenler kırmızıdır. Kitap, yazar veya üye adıyla "
     "aranabilir.<ul>"
     "<li><b>Ödünç verme:</b> <b>Ödünç ver</b> kartında kitabı ve üyeyi seçin (yazarak arayabilirsiniz). "
     "Kitabın müsait kopya sayısı, üyenin elindeki ve geciken kitapları ile teslim tarihi gösterilir. "
     "<b>Ödünç Ver</b>'e basın. Kitabın müsait kopyası yoksa ya da üyede zaten varsa buton kapalı kalır "
     "ve nedeni yazılır.</li>"
     "<li><b>İade alma:</b> Soldaki listeden kitabı seçin; bilgileri <b>İade al</b> kartında görünür. "
     "<b>İade Al</b>'a basın. Gecikme varsa kaç gün geciktiği bildirilir.</li></ul>"
     "Teslim süresi geçmiş kitap varsa sekmenin adında sayısı yazar (<i>Kitap Verme (2 gecikmiş)</i>). "
     "<b>Ödünç Geçmişi</b> alt sekmesi tüm ödünç kayıtlarını gösterir; üye, kitap ve duruma göre süzülebilir."),
    ("Ayarlar: kullanıcılar ve yedekleme",
     "<b>Yeni Kullanıcı Ekle</b> ile üye (guest) veya yönetici (admin) kaydı açılır. "
     "<b>Kullanıcı Yönetimi</b>nde kullanıcıların bilgileri ve yetkileri düzenlenir, şifreleri sıfırlanır "
     "veya silinir; elinde kitap olan kullanıcı ve son yönetici silinemez. <b>Şifremi Değiştir</b> kendi "
     "şifrenizi değiştirir.<br><br>"
     f"Program her gün ilk açılışta veritabanının otomatik yedeğini alır; son {OTOMATIK_SAKLA} yedek saklanır. "
     "<b>Yedek Al</b> istediğiniz bir yere (ör. USB bellek) yedek kaydeder. <b>Yedekten Geri Yükle</b> "
     "seçilen yedeğe döner; bunu yapmadan önce mevcut halin yedeği otomatik olarak alınır. "
     "<b>Yedek Klasörünü Aç</b> otomatik yedeklerin bulunduğu klasörü açar."),
    ("İpuçları",
     "<ul><li>Uzun açılır listelerde (kitap, üye, filtre ölçütleri) kaydırmak yerine yazarak arayın.</li>"
     "<li>İşlemlerin sonucu pencerenin altında birkaç saniye görünen bildirimlerle haber verilir: "
     "başarılı işlemler yeşil, uyarılar kırmızı.</li>"
     "<li>Tüm tablolar kolon başlığına tıklanarak sıralanabilir; sağ tıklayarak Excel/CSV'ye aktarılabilir.</li>"
     "</ul>"),
]

UYE = [
    ("Giriş (ana sayfa)",
     "Özet kartları kütüphanedeki kitap sayısını, elinizdeki ve gecikmiş kitapları ve en yakın teslim "
     "tarihini gösterir; bir karta tıklamak ilgili sekmeyi açar. <b>Oturumu Kapat</b> giriş ekranına döner."),
    ("Kitap Listesi", KITAP_LISTESI),
    ("Filtre", FILTRE),
    ("İstatistik", ISTATISTIK),
    ("Kitaplarım",
     f"Elinizdeki kitaplar, aldığınız tarih, teslim tarihi ve kalan gün sayısıyla listelenir (ödünç süresi "
     f"{ODUNC_SURESI_GUN} gün). Teslim süresi geçen kitaplar kırmızıdır ve sekmenin adında sayısı yazar. "
     "Daha önce aldığınız kitaplar da ne zaman aldığınız ve iade ettiğiniz bilgisiyle aşağıda görünür. "
     "Kitap ödünç almak veya iade etmek için kütüphane yöneticisine başvurun."),
    ("Ayarlar: hesabım",
     "<b>Hesabım</b> bölümünde kullanıcı adınız, adınız ve iletişim bilgileriniz görünür. "
     "<b>Şifremi Değiştir</b> ile mevcut şifrenizi girerek yeni şifre belirleyebilirsiniz. "
     "Bilgilerinizin değişmesi gerekiyorsa kütüphane yöneticisine başvurun."),
]

STIL = f"""
#kilavuz_hakkinda {{ color: {tema.METIN}; font-size: 16px; font-weight: normal; }}
QPushButton#kilavuz_konu {{ background: transparent; color: {tema.METIN}; border: none; border-radius: 0;
               border-top: 1px solid {tema.KENAR}; padding: 10px 4px; min-width: 0; text-align: left;
               font-size: 17px; font-weight: bold; }}
QPushButton#kilavuz_konu:hover {{ color: {tema.VURGU_KOYU}; }}
QPushButton#kilavuz_konu:checked {{ color: {tema.VURGU_KOYU}; }}
#kilavuz_metin {{ color: {tema.METIN}; font-size: 16px; font-weight: normal; padding: 0 8px 10px 22px; }}
"""


class Kilavuz(QGroupBox):
    """Program hakkında bilgi ve tıklanınca açılan konu başlıkları (aynı anda bir konu açık)."""

    def __init__(self, konular, parent=None):
        super().__init__("Kullanma Kılavuzu", parent)
        self.setStyleSheet(STIL)
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
