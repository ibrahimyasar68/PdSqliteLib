## Uygulama teması: tüm panellerde tek renk düzeni ##
# .ui dosyalarında renk ve yazı tipi tanımlanmaz; tüm görünüm bu temadan gelir.
# Kodla eklenen sekmeler (Ayarlar, Veri Düzeltme, ...) renk tanımlamaz; temayı panelden devralır.

import os
import sys

from PySide6.QtGui import QFont, QFontDatabase

# Renkler: açık ve koyu iki palet. Kullanılan palet açılışta (ve Ayarlar > Görünüm'den değişince) ayarla() ile
# bu modülün değişkenlerine yazılır; diğer modüller renkleri her zaman tema.X olarak, kullanırken okur.
ACIK = dict(
    ZEMIN="#EEF1F6",           # pencere zemini
    SAYFA="#F7F8FB",           # sekme sayfaları
    KART="#FFFFFF",            # tablolar, kutular
    KART_2="#F6F8FB",          # tablolarda sıra sıra renklenen satırlar
    KENAR="#D5DAE3",
    KENAR_GIRDI="#C7CDD8",     # yazı kutuları
    KENAR_IKINCIL="#CBD5E1",   # ikincil butonlar
    METIN="#1F2937",
    ETIKET="#334155",          # kalın etiketler, başlıklar
    IKINCIL_METIN="#5B6475",
    SOLUK="#647186",           # sönük sayılar, açıklamalar (kart ve sayfa zemininde en az 4,5:1 kontrast)
    PASIF="#64748B",           # devre dışı yazılar
    IKON="#475569",            # zemin üstündeki ikonlar (göz, açılır liste oku)
    YUZEY="#F1F5F9",           # ikincil buton üstüne gelince, salt okunur alan
    YUZEY_2="#E2E8F0",         # devre dışı buton, segment anahtarı zemini
    SEKME="#E3E7EE",
    SEKME_HOVER="#EDF2FB",
    SATIR_HOVER="#EEF4FF",
    IZGARA="#EDF0F4",
    VURGU="#2563EB",           # ana buton, seçili sekme
    VURGU_KOYU="#1D4ED8",      # ana buton üstüne gelince
    VURGU_BASILI="#1E40AF",
    VURGU_YAZI="#1D4ED8",      # vurgulu yazılar (seçili sekme, sonuç sayısı)
    VURGU_ACIK="#DBEAFE",      # seçili satır, etiket zemini
    TEHLIKE="#DC2626",         # geri alınamayan işlemler (Sil)
    TEHLIKE_KOYU="#B91C1C",
    TEHLIKE_ACIK="#FEE2E2",
    TEHLIKE_YAZI="#B91C1C",    # zeminsiz Sil butonunun yazısı (sayfa ve açık kırmızı zeminde 4,5:1)
    BASARI="#15803D",          # olumlu durum (ör. kitap rafta)
    UYARI="#B45309",           # kısmi durum (ör. kopyaların bir kısmı ödünçte)
    BILGI="#0EA5E9",           # ana sayfa kartları
    YESIL="#16A34A",
    GECIKME_ARKA="#FFCDCD",    # teslim süresi geçmiş satırlar
    GECIKME_YAZI="#960000",
    UYARI_ARKA="#FEF3C7",      # tablo üstündeki soru şeridi
    UYARI_KENAR="#FCD34D",
    UYARI_METIN="#78350F",
    BOS_METIN="#647186",       # boş tablo mesajı
    IPUCU_ARKA="#1F2937",
    IPUCU_YAZI="#FFFFFF",
    # Kenar menüsü iki temada da koyudur (yarı saydam lacivert; ana sayfada fotoğrafın üstünde durur)
    MENU_ZEMIN_RGB="15, 23, 42",
    MENU_YAZI="#E2E8F0",       # ikonlar, daraltma düğmesi
    MENU_OGE="#CBD5E1",        # seçili olmayan bölümler
    MENU_IKINCIL="#94A3B8",    # hızlı arama, yetki
    MENU_SONUK="#64748B",      # kısayol, imza
    MENU_LOGO="#FFE14D",       # el yazısı "Yaşar Kütüphanesi"
    MENU_CIKIS="#FCA5A5",      # Oturumu Kapat
)
KOYU = dict(
    ZEMIN="#0B1120", SAYFA="#111827", KART="#1E293B", KART_2="#18233A",
    KENAR="#334155", KENAR_GIRDI="#475569", KENAR_IKINCIL="#475569",
    METIN="#E5E7EB", ETIKET="#CBD5E1", IKINCIL_METIN="#94A3B8", SOLUK="#8B98AD", PASIF="#94A3B8", IKON="#CBD5E1",
    YUZEY="#273449", YUZEY_2="#334155", SEKME="#1E293B", SEKME_HOVER="#273449", SATIR_HOVER="#24324A",
    IZGARA="#273449",
    VURGU="#3B82F6", VURGU_KOYU="#2563EB", VURGU_BASILI="#1D4ED8", VURGU_YAZI="#93C5FD", VURGU_ACIK="#1E3A5F",
    TEHLIKE="#EF4444", TEHLIKE_KOYU="#DC2626", TEHLIKE_ACIK="#4C1D1D", TEHLIKE_YAZI="#FCA5A5",
    BASARI="#4ADE80", UYARI="#FBBF24", BILGI="#38BDF8", YESIL="#22C55E",
    GECIKME_ARKA="#4C1D1D", GECIKME_YAZI="#FCA5A5",
    UYARI_ARKA="#422006", UYARI_KENAR="#A16207", UYARI_METIN="#FDE68A",
    BOS_METIN="#8B98AD", IPUCU_ARKA="#F1F5F9", IPUCU_YAZI="#0F172A",
    MENU_ZEMIN_RGB="15, 23, 42", MENU_YAZI="#E2E8F0", MENU_OGE="#CBD5E1", MENU_IKINCIL="#94A3B8",
    MENU_SONUK="#64748B", MENU_LOGO="#FFE14D", MENU_CIKIS="#FCA5A5",
)
assert ACIK.keys() == KOYU.keys()

# Grafik serileri: ilki vurgu rengi; koyu temada aynı renklerin açık tonları
GRAFIK_ACIK = ["#2563EB", "#F59E0B", "#10B981", "#E11D48", "#0891B2", "#7C3AED", "#65A30D", "#EA580C",
               "#DB2777", "#64748B"]
GRAFIK_KOYU = ["#60A5FA", "#FBBF24", "#34D399", "#FB7185", "#22D3EE", "#A78BFA", "#A3E635", "#FB923C",
               "#F472B6", "#94A3B8"]

GORUNUMLER = {"sistem": "Sistemle aynı", "acik": "Açık", "koyu": "Koyu"}
GORUNUM = "sistem"          # tercih edilen görünüm
KOYU_MU = False             # şu an kullanılan palet koyu mu
# Başlangıçta açık palet; ayarla() değiştirir
globals().update(ACIK)
GRAFIK = GRAFIK_ACIK


def sistem_koyu_mu():
    """İşletim sistemi koyu görünümde mi? (Mac: uygulama paleti; Windows: kayıt defteri)"""
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as anahtar:
                return winreg.QueryValueEx(anahtar, "AppsUseLightTheme")[0] == 0
        except OSError:
            return False
    global _SISTEM_KOYU
    if _SISTEM_KOYU is None:
        # İlk sorulduğunda sistemin verdiği palete bakılır (sonra koyu temada palet programca değişir)
        from PySide6.QtGui import QGuiApplication, QPalette
        uygulama = QGuiApplication.instance()
        if uygulama is None:
            return False
        _SISTEM_KOYU = uygulama.palette().color(QPalette.Window).lightness() < 128
    return _SISTEM_KOYU


_SISTEM_KOYU = None


def ayarla(gorunum):
    """gorunum: "sistem", "acik" veya "koyu". Paleti bu modülün değişkenlerine yazar."""
    global GORUNUM, KOYU_MU, GRAFIK
    GORUNUM = gorunum if gorunum in GORUNUMLER else "sistem"
    KOYU_MU = GORUNUM == "koyu" or (GORUNUM == "sistem" and sistem_koyu_mu())
    globals().update(KOYU if KOYU_MU else ACIK)
    GRAFIK = GRAFIK_KOYU if KOYU_MU else GRAFIK_ACIK


# Yazı: sistemin kendi yazı tipi (Mac: San Francisco, Windows: Segoe UI). Boyutlar piksel cinsinden
# verilir; Mac ve Windows nokta (pt) boyutlarını farklı ölçeklediği için iki sistemde de aynı görünür.
class YAZI:
    """Yazı boyutu ölçeği (piksel). Modüllerde sabit font-size yazılmaz (tests/test_gorunum.py denetler)."""
    kucuk = 12          # imza, rozet, liste grup başlıkları
    ince = 13           # açıklamalar, alt yazılar, form etiketleri
    metin = 15          # varsayılan
    alt_baslik = 17     # kutu başlıkları, arama kutuları, boş tablo mesajı
    baslik = 22         # sayfa başlıkları
    buyuk = 28          # form ve giriş kartı başlığı
    gosterge = 32       # ana sayfa kartlarındaki sayılar
    karsilama = 40      # ana sayfadaki "Hoş geldiniz"
    logo_menu = 27      # el yazısı logo: kenar menüsü
    logo_giris = 48     # el yazısı logo: giriş ekranı


class KOSE:
    """Köşe yuvarlaklığı ölçeği (piksel). Rozet, avatar gibi boyuna göre tam yuvarlak öğeler bunun dışındadır."""
    kucuk = 6           # buton, yazı kutusu, tablo, menü öğesi
    orta = 10           # kart, kutu, bildirim
    buyuk = 14          # sayfa paneli, kenar menüsü, hızlı arama, giriş kartı


class SURE:
    """Animasyon süreleri (milisaniye). Modüllerde sabit süre yazılmaz; hepsi bu ölçekten gelir."""
    kisa = 120          # küçük öğeler: açılır pencere, düğme durumu
    orta = 200          # sayfa, menü genişliği, bildirimin belirmesi
    uzun = 450          # bildirimin solması, tema geçişindeki perde
    sayac = 600         # ana sayfa sayıları, grafiklerin çizilmesi
    parlama = 900       # değişen tablo satırının sönen vurgusu


YAZI_PX = YAZI.metin

# Yazı ağırlıkları: kalın (bold) yalnızca vurgu için; başlıklar yarı kalın, etiketler orta ağırlıkta.
# Qt 6 stil sayfasındaki sayısal ağırlığı CSS ölçeğinde (100-900) doğrudan kullanır: 600 DemiBold, 500 Medium.
# (Qt 5'te 8'e bölünüp çevrildiği için aynı görünüm 500 ve 460 ile elde ediliyordu.)
YARI_KALIN = 600
ORTA = 500

# Geri alınamayan işlem butonları zeminsiz, kırmızı yazılı gösterilir (asıl işlemle yarışmasın diye dolu değil)
TEHLIKELI_BUTONLAR = ["kitap_sil", "kullanici_sil"]

def _tema():
    return f"""
QMainWindow, #orta_alan {{ background-color: {ZEMIN}; }}

QTabWidget::pane {{ border: 1px solid {KENAR}; background-color: {SAYFA}; border-radius: {KOSE.kucuk}px; }}
QTabBar {{ font-size: {YAZI.alt_baslik}px; font-weight: {YARI_KALIN}; }}
QTabBar::tab {{ background-color: {SEKME}; color: {IKINCIL_METIN}; padding: 7px 18px; margin-right: 2px;
               border: 1px solid {KENAR}; border-bottom: none;
               border-top-left-radius: {KOSE.kucuk}px; border-top-right-radius: {KOSE.kucuk}px; }}
QTabBar::tab:selected {{ background-color: {KART}; color: {VURGU_YAZI}; }}
QTabBar::tab:hover:!selected {{ background-color: {SEKME_HOVER}; color: {METIN}; }}
QStackedWidget > QWidget {{ background-color: {SAYFA}; }}

QLabel {{ color: {METIN}; background: transparent; }}

QPushButton {{ background-color: {VURGU}; color: white; border: none; border-radius: {KOSE.kucuk}px; padding: 7px 14px;
               font-weight: {ORTA}; }}
QPushButton:hover {{ background-color: {VURGU_KOYU}; }}
QPushButton:pressed {{ background-color: {VURGU_BASILI}; }}
QPushButton:disabled {{ background-color: {YUZEY_2}; color: {PASIF}; }}
QPushButton[rol="ikincil"] {{ background-color: {KART}; color: {ETIKET}; border: 1px solid {KENAR_IKINCIL}; }}
QPushButton[rol="ikincil"]:hover {{ background-color: {YUZEY}; border-color: {SOLUK}; }}
QPushButton[rol="ikincil"]:pressed {{ background-color: {YUZEY_2}; }}
QPushButton[rol="ikincil"]:checked {{ background-color: {VURGU_ACIK}; color: {VURGU_YAZI}; border-color: {VURGU}; }}
QPushButton[rol="ikincil"]:disabled {{ background-color: {KART}; color: {SOLUK}; border-color: {YUZEY_2}; }}
{", ".join("#" + ad for ad in TEHLIKELI_BUTONLAR)} {{ background-color: transparent; color: {TEHLIKE_YAZI}; }}
{", ".join("#" + ad + ":hover" for ad in TEHLIKELI_BUTONLAR)} {{ background-color: {TEHLIKE_ACIK}; }}
{", ".join("#" + ad + ":pressed" for ad in TEHLIKELI_BUTONLAR)} {{ background-color: {TEHLIKE_ACIK}; }}
{", ".join("#" + ad + ":disabled" for ad in TEHLIKELI_BUTONLAR)} {{ background-color: transparent; color: {PASIF}; }}
QPushButton#filtre_etiketi {{ background-color: {VURGU_ACIK}; color: {VURGU_YAZI}; border-radius: 12px;
               padding: 4px 10px; }}
QPushButton#filtre_etiketi:hover {{ background-color: {TEHLIKE_ACIK}; color: {TEHLIKE}; }}
#sayfa_baslik {{ font-size: {YAZI.baslik}px; font-weight: {YARI_KALIN}; color: {METIN}; }}
QLabel[rol="sayac"] {{ font-size: {YAZI.metin}px; font-weight: {ORTA}; color: {VURGU_YAZI}; }}
QLabel[rol="bilgi_simgesi"] {{ color: {SOLUK}; font-size: {YAZI.alt_baslik}px; }}
QLabel[rol="alan_etiketi"] {{ color: {ETIKET}; font-size: {YAZI.ince}px; font-weight: {ORTA}; }}

QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {{ background-color: {KART}; color: {METIN};
               border: 1px solid {KENAR_GIRDI}; border-radius: {KOSE.kucuk}px; padding: 3px 6px; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus {{ border-color: {VURGU}; }}
QLineEdit:read-only {{ background-color: {YUZEY}; }}
QListView::item {{ padding: 4px 8px; }}
QComboBox QAbstractItemView {{ background-color: {KART}; color: {METIN};
               selection-background-color: {VURGU_ACIK}; selection-color: {METIN}; }}

QTableWidget, QTreeWidget {{ background-color: {KART}; alternate-background-color: {KART_2}; color: {METIN};
               gridline-color: {IZGARA}; border: 1px solid {KENAR}; border-radius: {KOSE.kucuk}px;
               selection-background-color: {VURGU_ACIK}; selection-color: {METIN}; }}
QTableWidget::item {{ padding: 0 8px; border-bottom: 1px solid {IZGARA}; }}
QTableWidget::item:hover {{ background-color: {SATIR_HOVER}; }}
QHeaderView {{ background-color: {KART}; border: none; }}
QHeaderView::section {{ background-color: {KART}; color: {IKINCIL_METIN}; padding: 6px 8px; border: none;
               border-bottom: 1px solid {KENAR}; font-size: {YAZI.ince}px; font-weight: {YARI_KALIN}; }}
QHeaderView::section:vertical {{ color: {SOLUK}; font-weight: normal; padding: 0 8px 0 7px; border-bottom: 1px solid {IZGARA};
               border-left: 3px solid transparent; }}
QHeaderView::section:vertical:checked {{ border-left-color: {VURGU}; color: {VURGU_YAZI}; background-color: {VURGU_ACIK}; }}
QTableCornerButton::section {{ background-color: {KART}; border: none; border-bottom: 1px solid {KENAR}; }}

QGroupBox {{ background-color: {KART}; border: 1px solid {KENAR}; border-radius: {KOSE.orta}px; color: {ETIKET};
               font-weight: {YARI_KALIN}; margin-top: 0; padding: 44px 12px 12px 12px; }}
QGroupBox::title {{ subcontrol-origin: padding; subcontrol-position: top left; left: 14px; top: 12px; }}

QStatusBar {{ background-color: {SEKME}; color: {ETIKET}; }}

QScrollBar:vertical {{ background: transparent; width: 12px; margin: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {KENAR_IKINCIL}; border-radius: 4px; min-height: 32px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: {KENAR_IKINCIL}; border-radius: 4px; min-width: 32px; margin: 2px; }}
QScrollBar::handle:hover {{ background: {SOLUK}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; border: none; background: none; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
QToolTip {{ background-color: {IPUCU_ARKA}; color: {IPUCU_YAZI}; border: none; padding: 4px 6px; }}
"""


def yazi_ailesi():
    return QFontDatabase.systemFont(QFontDatabase.GeneralFont).family()


def yazi_tipi(px=YAZI_PX, kalin=False):
    """Kodla çizilen metinler (ör. grafikler) için temadaki yazı tipi."""
    yazi = QFont(yazi_ailesi())
    yazi.setPixelSize(px)
    yazi.setBold(kalin)
    return yazi


# "Yaşar Kütüphanesi" başlığı için programa gömülü el yazısı (Great Vibes, SIL Open Font License; media/fonts)
BASLIK_YAZISI = "Great Vibes"
_baslik_yuklendi = False


def font_klasoru():
    kok = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(kok, "media", "fonts")


def baslik_yazisini_yukle():
    """Gömülü başlık fontunu bir kez yükler; yüklenemezse başlık sistemin italik yazısıyla görünür."""
    global _baslik_yuklendi
    if not _baslik_yuklendi:
        _baslik_yuklendi = QFontDatabase.addApplicationFont(os.path.join(font_klasoru(), "GreatVibes-Regular.ttf")) >= 0
    return _baslik_yuklendi


def qss():
    """Tema + yazı tipi kuralları (yazı ailesi uygulama açıkken belirlenebildiği için fonksiyon)."""
    baslik_yazisini_yukle()
    return _tema() + _koyu_ek() + denetimler() + f"""
* {{ font-family: "{yazi_ailesi()}"; font-style: normal; }}
QWidget {{ font-size: {YAZI_PX}px; }}
"""


def denetimler():
    """Açılır liste ve sayı kutusu: çerçeveli ok kutusu yerine sade ok, odakta mavi çerçeve, üstüne gelince vurgu."""
    from acodes.ikonlar import ok_resimleri    # ikonlar QPixmap ister: uygulama açıldıktan sonra çizilir
    ok = ok_resimleri(IKON)
    return f"""
QComboBox {{ padding-right: 30px; }}
QComboBox:hover, QSpinBox:hover, QLineEdit:hover {{ border-color: {SOLUK}; }}
QComboBox:focus, QSpinBox:focus, QLineEdit:focus, QPlainTextEdit:focus {{ border-color: {VURGU}; }}   /* kalınlık aynı: yazı kaymaz */
QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: center right; width: 28px; border: none;
               background: transparent; }}
QComboBox::down-arrow {{ image: url("{ok['asagi']}"); width: 18px; height: 18px; }}
QComboBox::down-arrow:on {{ image: url("{ok['yukari']}"); }}
QSpinBox {{ padding-right: 26px; }}
QSpinBox::up-button, QSpinBox::down-button {{ subcontrol-origin: padding; width: 22px; border: none;
               background: transparent; margin-right: 2px; }}
QSpinBox::up-button {{ subcontrol-position: top right; margin-top: 2px; }}
QSpinBox::down-button {{ subcontrol-position: bottom right; margin-bottom: 2px; }}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background: {VURGU_ACIK}; border-radius: {KOSE.kucuk}px; }}
QSpinBox::up-arrow {{ image: url("{ok['yukari']}"); width: 12px; height: 12px; }}
QSpinBox::down-arrow {{ image: url("{ok['asagi']}"); width: 12px; height: 12px; }}
"""


def _koyu_ek():
    """Koyu temada sistemin açık renkli çizdiği parçalar (diyalog zemini, menüler) da temaya uyar.
    Açık temada bunlar sistemin kendi görünümünde kalır."""
    return f"""
QDialog, QMessageBox {{ background-color: {ZEMIN}; }}
QMenu {{ background-color: {KART}; color: {METIN}; border: 1px solid {KENAR}; padding: 4px; }}
QMenu::item {{ padding: 6px 22px; border-radius: {KOSE.kucuk}px; }}
QMenu::item:selected {{ background-color: {VURGU_ACIK}; }}
QMenu::item:disabled {{ color: {SOLUK}; }}
QMenu::separator {{ height: 1px; background: {KENAR}; margin: 4px 8px; }}
QCheckBox, QRadioButton {{ color: {METIN}; }}
""" if KOYU_MU else ""


_ILK_STIL = None


def _sabit_aralikli(stil):
    """Düzen boşlukları ve form yerleşimi her temada aynı olsun diye çizim stilini sarar. macOS stili Fusion'dan
    (koyu tema) daha geniş boşluk ve kenar payı verdiği için tema değişince sayfa kayıyordu. Değerler Fusion'ınkilerdir.
    (Form yerleşimi her forma ayrıca verilir: yerlesim.form_duzeni.)"""
    from PySide6.QtWidgets import QProxyStyle, QStyle

    olculer = {QStyle.PM_LayoutLeftMargin: 9, QStyle.PM_LayoutTopMargin: 9, QStyle.PM_LayoutRightMargin: 9,
               QStyle.PM_LayoutBottomMargin: 9, QStyle.PM_LayoutHorizontalSpacing: 6,
               QStyle.PM_LayoutVerticalSpacing: 6}
    yerlesim_ogeleri = {getattr(QStyle, ad) for ad in dir(QStyle) if ad.startswith("SE_") and ad.endswith("LayoutItem")}

    from PySide6.QtWidgets import QStyleFactory
    olcu_stili = QStyleFactory.create("Fusion")       # tablo başlıklarının boyu iki temada da buna göre

    # Kodun stille çizdirdiği (QSS ile biçimlenen) parçaların ölçüleri de Fusion'dan: tablo başlığı, kaydırma alanı,
    # sayı kutusu, odak çerçevesi. macOS'un kendi çizdiği onay kutusu gibi parçaların ölçülerine dokunulmaz.
    for ad in ("PM_HeaderMargin", "PM_ScrollView_ScrollBarOverlap", "PM_ScrollView_ScrollBarSpacing",
               "PM_SpinBoxFrameWidth", "PM_FocusFrameHMargin", "PM_FocusFrameVMargin"):
        olculer[getattr(QStyle, ad)] = olcu_stili.pixelMetric(getattr(QStyle, ad))

    class SabitAralik(QProxyStyle):
        def sizeFromContents(self, tur, secenek, boyut, bilesen=None):
            if tur == QStyle.CT_HeaderSection:
                return olcu_stili.sizeFromContents(tur, secenek, boyut, bilesen)
            return super().sizeFromContents(tur, secenek, boyut, bilesen)

        def pixelMetric(self, olcu, secenek=None, bilesen=None):
            return olculer[olcu] if olcu in olculer else super().pixelMetric(olcu, secenek, bilesen)

        def layoutSpacing(self, *args):
            return 6

        def subElementRect(self, oge, secenek, bilesen=None):
            # macOS stili düğme, liste, sekme kabı gibi bileşenlerin yerleşim alanını görünmez paylarla genişletir
            if oge in yerlesim_ogeleri and secenek is not None:
                return secenek.rect
            return super().subElementRect(oge, secenek, bilesen)

    ad = stil.objectName()          # sarıldıktan sonra stil nesnesine Python'dan erişilemez (sahibi sarmalayıcı olur)
    sarilmis = SabitAralik(stil)
    # Ölçü stili sarmalayıcıyla birlikte yaşar: Qt tarafında ona bağlanır. Yalnızca Python niteliğinde tutulunca
    # program kapanırken (Python nesneleri silinirken) sarmalayıcıdan önce silinip hata veriyordu.
    olcu_stili.setParent(sarilmis)
    sarilmis.olcu_stili = olcu_stili
    sarilmis.setObjectName(ad)
    return sarilmis


def uygulamaya_uygula(uygulama):
    """Uygulama genelindeki çizim stili ve renk paleti. Koyu temada Fusion stili ve koyu palet kullanılır
    (sistem açık görünümdeyken de onay kutuları, kaydırma çubukları, diyaloglar koyu çizilsin diye);
    açık temada sistemin kendi stili ve paleti kalır."""
    from PySide6.QtGui import QColor, QPalette
    from PySide6.QtWidgets import QStyleFactory
    global _ILK_STIL
    if _ILK_STIL is None:
        _ILK_STIL = uygulama.style().objectName()
    if not KOYU_MU:
        uygulama.setStyle(_sabit_aralikli(QStyleFactory.create(_ILK_STIL)))
        uygulama.setPalette(uygulama.style().standardPalette())
        return
    uygulama.setStyle(_sabit_aralikli(QStyleFactory.create("Fusion")))
    p = QPalette()
    for rol, renk in ((QPalette.Window, ZEMIN), (QPalette.WindowText, METIN), (QPalette.Base, KART),
                      (QPalette.AlternateBase, KART_2), (QPalette.Text, METIN), (QPalette.Button, KART),
                      (QPalette.ButtonText, METIN), (QPalette.ToolTipBase, IPUCU_ARKA), (QPalette.ToolTipText, IPUCU_YAZI),
                      (QPalette.Highlight, VURGU), (QPalette.HighlightedText, "#FFFFFF"), (QPalette.Link, VURGU_YAZI),
                      (QPalette.PlaceholderText, SOLUK), (QPalette.Light, KENAR), (QPalette.Mid, KENAR),
                      (QPalette.Dark, ZEMIN), (QPalette.Shadow, "#000000")):
        p.setColor(rol, QColor(renk))
    for rol in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, rol, QColor(SOLUK))
    uygulama.setPalette(p)
