## Uygulama teması: tüm panellerde tek renk düzeni ##
# .ui dosyalarından gelen sekme/buton renkleri silinir, yerine bu tema uygulanır.
# Kodla eklenen sekmeler (Ayarlar, Veri Düzeltme, ...) renk tanımlamaz; temayı panelden devralır.

import os
import sys

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QWidget

# Renkler
ZEMIN = "#EEF1F6"          # pencere zemini
SAYFA = "#F7F8FB"          # sekme sayfaları
KART = "#FFFFFF"           # tablolar, kutular
KENAR = "#D5DAE3"
METIN = "#1F2937"
IKINCIL_METIN = "#5B6475"
VURGU = "#2563EB"          # ana buton, seçili sekme
VURGU_KOYU = "#1D4ED8"
VURGU_ACIK = "#DBEAFE"     # seçili satır
TEHLIKE = "#DC2626"        # geri alınamayan işlemler (Sil)
TEHLIKE_KOYU = "#B91C1C"

# Yazı: sistemin kendi yazı tipi (Mac: San Francisco, Windows: Segoe UI). Boyutlar piksel cinsinden
# verilir; Mac ve Windows nokta (pt) boyutlarını farklı ölçeklediği için iki sistemde de aynı görünür.
YAZI_PX = 15

# Geri alınamayan işlem butonları kırmızı gösterilir
TEHLIKELI_BUTONLAR = ["kitap_sil", "kullanici_sil"]

TEMA = f"""
QMainWindow, #centralwidget {{ background-color: {ZEMIN}; }}

QTabWidget::pane {{ border: 1px solid {KENAR}; background-color: {SAYFA}; border-radius: 6px; }}
QTabBar {{ font-size: 17px; font-weight: bold; }}
QTabBar::tab {{ background-color: #E3E7EE; color: {IKINCIL_METIN}; padding: 7px 18px; margin-right: 2px;
               border: 1px solid {KENAR}; border-bottom: none;
               border-top-left-radius: 6px; border-top-right-radius: 6px; }}
QTabBar::tab:selected {{ background-color: {KART}; color: {VURGU_KOYU}; }}
QTabBar::tab:hover:!selected {{ background-color: #EDF2FB; color: {METIN}; }}
QStackedWidget > QWidget {{ background-color: {SAYFA}; }}

QLabel {{ color: {METIN}; background: transparent; }}

QPushButton {{ background-color: {VURGU}; color: white; border: none; border-radius: 6px; padding: 4px 8px; }}
QPushButton:hover {{ background-color: {VURGU_KOYU}; }}
QPushButton:pressed {{ background-color: #1E40AF; }}
QPushButton:disabled {{ background-color: #E2E8F0; color: #64748B; }}
QPushButton[rol="ikincil"] {{ background-color: {KART}; color: #334155; border: 1px solid #CBD5E1; }}
QPushButton[rol="ikincil"]:hover {{ background-color: #F1F5F9; border-color: #94A3B8; }}
QPushButton[rol="ikincil"]:pressed {{ background-color: #E2E8F0; }}
QPushButton[rol="ikincil"]:disabled {{ background-color: #F8FAFC; color: #94A3B8; border-color: #E2E8F0; }}
{", ".join("#" + ad for ad in TEHLIKELI_BUTONLAR)} {{ background-color: {TEHLIKE}; }}
{", ".join("#" + ad + ":hover" for ad in TEHLIKELI_BUTONLAR)} {{ background-color: {TEHLIKE_KOYU}; }}
{", ".join("#" + ad + ":disabled" for ad in TEHLIKELI_BUTONLAR)} {{ background-color: #E2E8F0; color: #64748B; }}
QPushButton#filtre_etiketi {{ background-color: {VURGU_ACIK}; color: {VURGU_KOYU}; border-radius: 12px;
               padding: 4px 10px; }}
QPushButton#filtre_etiketi:hover {{ background-color: #FEE2E2; color: {TEHLIKE_KOYU}; }}
#filtre_aciklama {{ color: {IKINCIL_METIN}; }}
#filtre_sonuc {{ font-size: 16px; font-weight: bold; color: {VURGU_KOYU}; }}

QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {{ background-color: {KART}; color: {METIN};
               border: 1px solid #C7CDD8; border-radius: 5px; padding: 3px 6px; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus {{ border-color: {VURGU}; }}
QLineEdit:read-only {{ background-color: #F1F4F8; }}
QListView::item {{ padding: 4px 8px; }}
QComboBox QAbstractItemView {{ background-color: {KART}; color: {METIN};
               selection-background-color: {VURGU_ACIK}; selection-color: {METIN}; }}

QTableWidget, QTreeWidget {{ background-color: {KART}; alternate-background-color: #F6F8FB; color: {METIN};
               gridline-color: #EDF0F4; border: 1px solid {KENAR}; border-radius: 4px;
               selection-background-color: {VURGU_ACIK}; selection-color: {METIN}; }}
QTableWidget::item {{ padding: 0 6px; }}
QTableWidget::item:hover {{ background-color: #EEF4FF; }}
QHeaderView::section:vertical {{ color: {IKINCIL_METIN}; font-weight: normal; padding: 0 8px 0 10px; }}
QHeaderView::section {{ background-color: {ZEMIN}; color: #334155; padding: 4px 6px; border: none; font-weight: bold;
               border-right: 1px solid {KENAR}; border-bottom: 1px solid {KENAR}; }}

QGroupBox {{ background-color: {KART}; border: 1px solid {KENAR}; border-radius: 8px; color: #334155;
               font-weight: bold; margin-top: 0; padding: 44px 12px 12px 12px; }}
QGroupBox::title {{ subcontrol-origin: padding; subcontrol-position: top left; left: 14px; top: 12px; }}

QStatusBar {{ background-color: #E3E7EE; color: #334155; }}
QToolTip {{ background-color: {METIN}; color: white; border: none; padding: 4px 6px; }}
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
    return TEMA + denetimler() + f"""
* {{ font-family: "{yazi_ailesi()}"; font-style: normal; }}
QWidget {{ font-size: {YAZI_PX}px; }}
"""


def denetimler():
    """Açılır liste ve sayı kutusu: çerçeveli ok kutusu yerine sade ok, odakta mavi çerçeve, üstüne gelince vurgu."""
    from acodes.ikonlar import ok_resimleri    # ikonlar QPixmap ister: uygulama açıldıktan sonra çizilir
    ok = ok_resimleri("#475569")
    return f"""
QComboBox {{ padding-right: 30px; }}
QComboBox:hover, QSpinBox:hover, QLineEdit:hover {{ border-color: #94A3B8; }}
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
    """setupUi'den hemen sonra çağrılır: .ui'dan gelen stilleri siler, temayı uygular."""
    for bilesen in pencere.findChildren(QWidget):
        if bilesen.styleSheet():
            bilesen.setStyleSheet("")
    pencere.setStyleSheet(qss())
