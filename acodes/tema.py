## Uygulama teması: tüm panellerde tek renk düzeni ##
# .ui dosyalarında renk ve yazı tipi tanımlanmaz; tüm görünüm bu temadan gelir.
# Kodla eklenen sekmeler (Ayarlar, Veri Düzeltme, ...) renk tanımlamaz; temayı panelden devralır.

import os
import sys

from PyQt5.QtGui import QFont, QFontDatabase

# Renkler: açık ve koyu iki palet. Kullanılan palet açılışta (ve Ayarlar > Görünüm'den değişince) ayarla() ile
# bu modülün değişkenlerine yazılır; diğer modüller renkleri her zaman tema.X olarak, kullanırken okur.
ACIK = dict(
    ZEMIN="#EEF1F6",           # pencere zemini
    SAYFA="#F7F8FB",           # sekme sayfaları
    SAYFA_RGB="247, 248, 251", # yarı saydam sayfa perdesi (arka plan fotoğrafının üstünde)
    KART="#FFFFFF",            # tablolar, kutular
    KART_2="#F6F8FB",          # tablolarda sıra sıra renklenen satırlar
    KENAR="#D5DAE3",
    KENAR_GIRDI="#C7CDD8",     # yazı kutuları
    KENAR_IKINCIL="#CBD5E1",   # ikincil butonlar
    METIN="#1F2937",
    ETIKET="#334155",          # kalın etiketler, başlıklar
    IKINCIL_METIN="#5B6475",
    SOLUK="#94A3B8",           # sönük sayılar, açıklamalar
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
    BASARI="#15803D",          # olumlu durum (ör. kitap rafta)
    UYARI="#B45309",           # kısmi durum (ör. kopyaların bir kısmı ödünçte)
    BILGI="#0EA5E9",           # ana sayfa kartları
    YESIL="#16A34A",
    GECIKME_ARKA="#FFCDCD",    # teslim süresi geçmiş satırlar
    GECIKME_YAZI="#960000",
    UYARI_ARKA="#FEF3C7",      # tablo üstündeki soru şeridi
    UYARI_KENAR="#FCD34D",
    UYARI_METIN="#78350F",
    BOS_METIN="#8A94A6",       # boş tablo mesajı
    IPUCU_ARKA="#1F2937",
    IPUCU_YAZI="#FFFFFF",
)
KOYU = dict(
    ZEMIN="#0B1120", SAYFA="#111827", SAYFA_RGB="17, 24, 39", KART="#1E293B", KART_2="#18233A",
    KENAR="#334155", KENAR_GIRDI="#475569", KENAR_IKINCIL="#475569",
    METIN="#E5E7EB", ETIKET="#CBD5E1", IKINCIL_METIN="#94A3B8", SOLUK="#64748B", PASIF="#94A3B8", IKON="#CBD5E1",
    YUZEY="#273449", YUZEY_2="#334155", SEKME="#1E293B", SEKME_HOVER="#273449", SATIR_HOVER="#24324A",
    IZGARA="#273449",
    VURGU="#3B82F6", VURGU_KOYU="#2563EB", VURGU_BASILI="#1D4ED8", VURGU_YAZI="#93C5FD", VURGU_ACIK="#1E3A5F",
    TEHLIKE="#EF4444", TEHLIKE_KOYU="#DC2626", TEHLIKE_ACIK="#4C1D1D",
    BASARI="#4ADE80", UYARI="#FBBF24", BILGI="#38BDF8", YESIL="#22C55E",
    GECIKME_ARKA="#4C1D1D", GECIKME_YAZI="#FCA5A5",
    UYARI_ARKA="#422006", UYARI_KENAR="#A16207", UYARI_METIN="#FDE68A",
    BOS_METIN="#64748B", IPUCU_ARKA="#F1F5F9", IPUCU_YAZI="#0F172A",
)
assert ACIK.keys() == KOYU.keys()

GORUNUMLER = {"sistem": "Sistemle aynı", "acik": "Açık", "koyu": "Koyu"}
GORUNUM = "sistem"          # tercih edilen görünüm
KOYU_MU = False             # şu an kullanılan palet koyu mu
# Başlangıçta açık palet; ayarla() değiştirir
(ZEMIN, SAYFA, SAYFA_RGB, KART, KART_2, KENAR, KENAR_GIRDI, KENAR_IKINCIL, METIN, ETIKET, IKINCIL_METIN,
 SOLUK, PASIF, IKON, YUZEY, YUZEY_2, SEKME, SEKME_HOVER, SATIR_HOVER, IZGARA, VURGU, VURGU_KOYU,
 VURGU_BASILI, VURGU_YAZI, VURGU_ACIK, TEHLIKE, TEHLIKE_KOYU, TEHLIKE_ACIK, BASARI, UYARI, BILGI, YESIL,
 GECIKME_ARKA, GECIKME_YAZI, UYARI_ARKA, UYARI_KENAR, UYARI_METIN, BOS_METIN, IPUCU_ARKA, IPUCU_YAZI) = ACIK.values()


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
        from PyQt5.QtGui import QGuiApplication, QPalette
        uygulama = QGuiApplication.instance()
        if uygulama is None:
            return False
        _SISTEM_KOYU = uygulama.palette().color(QPalette.Window).lightness() < 128
    return _SISTEM_KOYU


_SISTEM_KOYU = None


def ayarla(gorunum):
    """gorunum: "sistem", "acik" veya "koyu". Paleti bu modülün değişkenlerine yazar."""
    global GORUNUM, KOYU_MU
    GORUNUM = gorunum if gorunum in GORUNUMLER else "sistem"
    KOYU_MU = GORUNUM == "koyu" or (GORUNUM == "sistem" and sistem_koyu_mu())
    globals().update(KOYU if KOYU_MU else ACIK)


# Yazı: sistemin kendi yazı tipi (Mac: San Francisco, Windows: Segoe UI). Boyutlar piksel cinsinden
# verilir; Mac ve Windows nokta (pt) boyutlarını farklı ölçeklediği için iki sistemde de aynı görünür.
YAZI_PX = 15

# Geri alınamayan işlem butonları kırmızı gösterilir
TEHLIKELI_BUTONLAR = ["kitap_sil", "kullanici_sil"]

def _tema():
    return f"""
QMainWindow, #centralwidget {{ background-color: {ZEMIN}; }}

QTabWidget::pane {{ border: 1px solid {KENAR}; background-color: {SAYFA}; border-radius: 6px; }}
QTabBar {{ font-size: 17px; font-weight: bold; }}
QTabBar::tab {{ background-color: {SEKME}; color: {IKINCIL_METIN}; padding: 7px 18px; margin-right: 2px;
               border: 1px solid {KENAR}; border-bottom: none;
               border-top-left-radius: 6px; border-top-right-radius: 6px; }}
QTabBar::tab:selected {{ background-color: {KART}; color: {VURGU_YAZI}; }}
QTabBar::tab:hover:!selected {{ background-color: {SEKME_HOVER}; color: {METIN}; }}
QStackedWidget > QWidget {{ background-color: {SAYFA}; }}

QLabel {{ color: {METIN}; background: transparent; }}

QPushButton {{ background-color: {VURGU}; color: white; border: none; border-radius: 6px; padding: 4px 8px; }}
QPushButton:hover {{ background-color: {VURGU_KOYU}; }}
QPushButton:pressed {{ background-color: {VURGU_BASILI}; }}
QPushButton:disabled {{ background-color: {YUZEY_2}; color: {PASIF}; }}
QPushButton[rol="ikincil"] {{ background-color: {KART}; color: {ETIKET}; border: 1px solid {KENAR_IKINCIL}; }}
QPushButton[rol="ikincil"]:hover {{ background-color: {YUZEY}; border-color: {SOLUK}; }}
QPushButton[rol="ikincil"]:pressed {{ background-color: {YUZEY_2}; }}
QPushButton[rol="ikincil"]:checked {{ background-color: {VURGU_ACIK}; color: {VURGU_YAZI}; border-color: {VURGU}; }}
QPushButton[rol="ikincil"]:disabled {{ background-color: {KART}; color: {SOLUK}; border-color: {YUZEY_2}; }}
{", ".join("#" + ad for ad in TEHLIKELI_BUTONLAR)} {{ background-color: {TEHLIKE}; }}
{", ".join("#" + ad + ":hover" for ad in TEHLIKELI_BUTONLAR)} {{ background-color: {TEHLIKE_KOYU}; }}
{", ".join("#" + ad + ":disabled" for ad in TEHLIKELI_BUTONLAR)} {{ background-color: {YUZEY_2}; color: {PASIF}; }}
QPushButton#filtre_etiketi {{ background-color: {VURGU_ACIK}; color: {VURGU_YAZI}; border-radius: 12px;
               padding: 4px 10px; }}
QPushButton#filtre_etiketi:hover {{ background-color: {TEHLIKE_ACIK}; color: {TEHLIKE}; }}
#filtre_aciklama {{ color: {IKINCIL_METIN}; }}
#filtre_sonuc {{ font-size: 16px; font-weight: bold; color: {VURGU_YAZI}; }}

QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {{ background-color: {KART}; color: {METIN};
               border: 1px solid {KENAR_GIRDI}; border-radius: 5px; padding: 3px 6px; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus {{ border-color: {VURGU}; }}
QLineEdit:read-only {{ background-color: {YUZEY}; }}
QListView::item {{ padding: 4px 8px; }}
QComboBox QAbstractItemView {{ background-color: {KART}; color: {METIN};
               selection-background-color: {VURGU_ACIK}; selection-color: {METIN}; }}

QTableWidget, QTreeWidget {{ background-color: {KART}; alternate-background-color: {KART_2}; color: {METIN};
               gridline-color: {IZGARA}; border: 1px solid {KENAR}; border-radius: 4px;
               selection-background-color: {VURGU_ACIK}; selection-color: {METIN}; }}
QTableWidget::item {{ padding: 0 6px; }}
QTableWidget::item:hover {{ background-color: {SATIR_HOVER}; }}
QHeaderView::section:vertical {{ color: {IKINCIL_METIN}; font-weight: normal; padding: 0 8px 0 10px; }}
QHeaderView::section {{ background-color: {ZEMIN}; color: {ETIKET}; padding: 4px 6px; border: none; font-weight: bold;
               border-right: 1px solid {KENAR}; border-bottom: 1px solid {KENAR}; }}

QGroupBox {{ background-color: {KART}; border: 1px solid {KENAR}; border-radius: 8px; color: {ETIKET};
               font-weight: bold; margin-top: 0; padding: 44px 12px 12px 12px; }}
QGroupBox::title {{ subcontrol-origin: padding; subcontrol-position: top left; left: 14px; top: 12px; }}

QStatusBar {{ background-color: {SEKME}; color: {ETIKET}; }}
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
QComboBox:focus, QSpinBox:focus, QLineEdit:focus, QPlainTextEdit:focus {{ border: 2px solid {VURGU}; }}
QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: center right; width: 28px; border: none;
               background: transparent; }}
QComboBox::down-arrow {{ image: url("{ok['asagi']}"); width: 18px; height: 18px; }}
QComboBox::down-arrow:on {{ image: url("{ok['yukari']}"); }}
QSpinBox {{ padding-right: 26px; }}
QSpinBox::up-button, QSpinBox::down-button {{ subcontrol-origin: padding; width: 22px; border: none;
               background: transparent; margin-right: 2px; }}
QSpinBox::up-button {{ subcontrol-position: top right; margin-top: 2px; }}
QSpinBox::down-button {{ subcontrol-position: bottom right; margin-bottom: 2px; }}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background: {VURGU_ACIK}; border-radius: 4px; }}
QSpinBox::up-arrow {{ image: url("{ok['yukari']}"); width: 12px; height: 12px; }}
QSpinBox::down-arrow {{ image: url("{ok['asagi']}"); width: 12px; height: 12px; }}
"""


def uygula(pencere):
    """Temayı pencereye uygular (.ui dosyalarında renk ve yazı tipi tanımlanmaz)."""
    pencere.setStyleSheet(qss())


def _koyu_ek():
    """Koyu temada sistemin açık renkli çizdiği parçalar (diyalog zemini, menüler) da temaya uyar.
    Açık temada bunlar sistemin kendi görünümünde kalır."""
    return f"""
QDialog, QMessageBox {{ background-color: {ZEMIN}; }}
QMenu {{ background-color: {KART}; color: {METIN}; border: 1px solid {KENAR}; padding: 4px; }}
QMenu::item {{ padding: 6px 22px; border-radius: 4px; }}
QMenu::item:selected {{ background-color: {VURGU_ACIK}; }}
QMenu::item:disabled {{ color: {SOLUK}; }}
QMenu::separator {{ height: 1px; background: {KENAR}; margin: 4px 8px; }}
QCheckBox, QRadioButton {{ color: {METIN}; }}
""" if KOYU_MU else ""


_ILK_STIL = None


def uygulamaya_uygula(uygulama):
    """Uygulama genelindeki çizim stili ve renk paleti. Koyu temada Fusion stili ve koyu palet kullanılır
    (sistem açık görünümdeyken de onay kutuları, kaydırma çubukları, diyaloglar koyu çizilsin diye);
    açık temada sistemin kendi stili ve paleti kalır."""
    from PyQt5.QtGui import QColor, QPalette
    from PyQt5.QtWidgets import QStyleFactory
    global _ILK_STIL
    if _ILK_STIL is None:
        _ILK_STIL = uygulama.style().objectName()
    if not KOYU_MU:
        uygulama.setStyle(QStyleFactory.create(_ILK_STIL))
        uygulama.setPalette(uygulama.style().standardPalette())
        return
    uygulama.setStyle(QStyleFactory.create("Fusion"))
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
