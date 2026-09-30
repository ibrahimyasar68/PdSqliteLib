## Uygulama teması: tüm panellerde tek renk düzeni ##
# .ui dosyalarından gelen sekme/buton renkleri silinir, yerine bu tema uygulanır.
# Kodla eklenen sekmeler (Ayarlar, Veri Düzeltme, ...) renk tanımlamaz; temayı panelden devralır.

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
YAZI_PX = 13

# Geri alınamayan işlem butonları kırmızı gösterilir
TEHLIKELI_BUTONLAR = ["kitap_sil"]

TEMA = f"""
QMainWindow, #centralwidget {{ background-color: {ZEMIN}; }}

QTabWidget::pane {{ border: 1px solid {KENAR}; background-color: {SAYFA}; border-radius: 6px; }}
QTabBar::tab {{ background-color: #E3E7EE; color: {IKINCIL_METIN}; padding: 6px 16px; margin-right: 2px;
               border: 1px solid {KENAR}; border-bottom: none;
               border-top-left-radius: 6px; border-top-right-radius: 6px; }}
QTabBar::tab:selected {{ background-color: {KART}; color: {VURGU_KOYU}; }}
QTabBar::tab:hover:!selected {{ background-color: #EDF2FB; color: {METIN}; }}
QStackedWidget > QWidget {{ background-color: {SAYFA}; }}

QLabel {{ color: {METIN}; background: transparent; }}
#label {{ color: #FFE14D; font: italic 50pt "Monotype Corsiva"; }}
#label_32, #label_log_on {{ color: white; font-size: 18px; font-weight: bold; }}

QPushButton {{ background-color: {VURGU}; color: white; border: none; border-radius: 6px; padding: 4px 8px; }}
QPushButton:hover {{ background-color: {VURGU_KOYU}; }}
QPushButton:pressed {{ background-color: #1E40AF; }}
QPushButton:disabled {{ background-color: #E2E8F0; color: #64748B; }}
{", ".join("#" + ad for ad in TEHLIKELI_BUTONLAR)} {{ background-color: {TEHLIKE}; }}
{", ".join("#" + ad + ":hover" for ad in TEHLIKELI_BUTONLAR)} {{ background-color: {TEHLIKE_KOYU}; }}
{", ".join("#" + ad + ":disabled" for ad in TEHLIKELI_BUTONLAR)} {{ background-color: #E2E8F0; color: #64748B; }}

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
QHeaderView::section {{ background-color: {ZEMIN}; color: #334155; padding: 4px 6px; border: none; font-weight: bold;
               border-right: 1px solid {KENAR}; border-bottom: 1px solid {KENAR}; }}

QGroupBox {{ background-color: {KART}; border: 1px solid {KENAR}; border-radius: 8px;
               margin-top: 14px; padding: 12px 10px 10px 10px; color: #334155; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}

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


def qss():
    """Tema + yazı tipi kuralları (yazı ailesi uygulama açıkken belirlenebildiği için fonksiyon)."""
    return TEMA + f"""
* {{ font-family: "{yazi_ailesi()}"; font-style: normal; }}
QWidget {{ font-size: {YAZI_PX}px; }}
"""


def uygula(pencere):
    """setupUi'den hemen sonra çağrılır: .ui'dan gelen stilleri siler, temayı uygular."""
    for bilesen in pencere.findChildren(QWidget):
        if bilesen.styleSheet():
            bilesen.setStyleSheet("")
    pencere.setStyleSheet(qss())
