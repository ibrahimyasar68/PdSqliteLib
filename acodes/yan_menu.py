## Sol kenar menüsü ve alt sekmeler için üstte segment anahtarı ##
# Üstteki sekme çubuğunun yerine solda koyu, yarı saydam bir menü: en üstte "Yaşar Kütüphanesi", ikonlu
# bölümler, altta kullanıcı kartı (ad, yetki, Oturumu Kapat) ve imza. Daraltılınca yalnızca simgeler kalır;
# açık/kapalı durumu hatırlanır. Sekme adındaki "(N gecikmiş)" menüde kırmızı rozet olarak görünür.

import re

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QButtonGroup, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acodes import ikonlar, tema, tercihler
from acodes.kilavuz import IMZA

ACIK_EN, KAPALI_EN = 260, 76
YAZI_RENGI = "#E2E8F0"
_SAYI = re.compile(r"^(.*) \((\d+) gecikmiş\)$")

STIL = f"""
#yan_menu {{ background-color: rgba(15, 23, 42, 0.88); border-radius: 14px; }}
#menu_baslik {{ color: #FFE14D; font-family: "{tema.BASLIK_YAZISI}"; font-size: 27px; font-style: normal; }}
QPushButton#menu_ogesi {{ background: transparent; color: #CBD5E1; border: none; border-radius: 8px; text-align: left;
               padding: 11px 13px; font-size: 16px; font-weight: bold; }}
QPushButton#menu_ogesi:hover {{ background-color: rgba(255,255,255,0.08); color: white; }}
QPushButton#menu_ogesi:checked {{ background-color: rgba(96,165,250,0.24); color: white; }}
QPushButton#daralt {{ background: transparent; border: none; border-radius: 8px; padding: 6px; }}
QPushButton#daralt:hover {{ background-color: rgba(255,255,255,0.10); }}
#rozet {{ background-color: {tema.TEHLIKE}; color: white; border-radius: 9px; font-size: 12px; font-weight: bold;
               padding: 0 6px; min-width: 8px; }}
#kullanici_kart {{ background-color: rgba(255,255,255,0.06); border-radius: 10px; }}
#avatar {{ background-color: {tema.VURGU}; color: white; border-radius: 20px; font-size: 15px; font-weight: bold; }}
#kul_ad {{ color: white; font-size: 15px; font-weight: bold; }}
#kul_rol {{ color: #94A3B8; font-size: 13px; }}
QPushButton#pushButton_1_cikis {{ background: transparent; color: #FCA5A5; border: 1px solid rgba(252,165,165,0.5);
               border-radius: 8px; padding: 8px; font-size: 14px; font-weight: bold; }}
QPushButton#pushButton_1_cikis:hover {{ background-color: rgba(220,38,38,0.25); color: white; }}
#imza {{ color: #64748B; font-size: 12px; }}
"""


def bas_harfler(ad):
    parcalar = [p for p in re.split(r"[\s._-]+", ad or "") if p]
    harfler = "".join(p[0] for p in parcalar[:2]) if len(parcalar) > 1 else (parcalar[0][:2] if parcalar else "?")
    return harfler.replace("i", "İ").upper()


class YanMenu(QFrame):
    def __init__(self, sekmeler, sayfa_ikonlari, cikis_butonu, parent=None):
        """sayfa_ikonlari: {sekme sayfası: SEKME_IKONLARI anahtarı}; cikis_butonu kullanıcı kartına taşınır."""
        super().__init__(parent)
        self.setObjectName("yan_menu")
        self.setStyleSheet(STIL)
        self.sekmeler = sekmeler
        dikey = QVBoxLayout(self)
        dikey.setContentsMargins(10, 14, 8, 12)
        dikey.setSpacing(4)

        ust = QHBoxLayout()
        ust.setSpacing(0)
        self.baslik = QLabel("Yaşar Kütüphanesi", objectName="menu_baslik")
        self.btn_daralt = QPushButton(objectName="daralt")
        self.btn_daralt.setIconSize(QSize(22, 22))
        self.btn_daralt.setCursor(Qt.PointingHandCursor)
        self.btn_daralt.clicked.connect(lambda: self.daralt(not self.kapali))
        ust.addWidget(self.baslik, 1)
        ust.addWidget(self.btn_daralt, 0, Qt.AlignTop)
        dikey.addLayout(ust)
        dikey.addSpacing(10)

        self.grup = QButtonGroup(self)
        self.ogeler = []
        for i in range(sekmeler.count()):
            sayfa = sekmeler.widget(i)
            buton = QPushButton(objectName="menu_ogesi")
            buton.setCheckable(True)
            buton.setCursor(Qt.PointingHandCursor)
            buton.setIcon(ikonlar.ikon(ikonlar.SEKME_IKONLARI[sayfa_ikonlari[sayfa]], YAZI_RENGI, YAZI_RENGI))
            buton.setIconSize(QSize(20, 20))
            buton.setMinimumHeight(44)
            rozet = QLabel(objectName="rozet")
            rozet.setAlignment(Qt.AlignCenter)
            rozet.setFixedHeight(18)
            rozet.hide()
            ic = QHBoxLayout(buton)
            ic.setContentsMargins(0, 0, 8, 0)
            ic.addStretch()
            ic.addWidget(rozet)
            buton.clicked.connect(lambda _, s=sayfa: sekmeler.setCurrentWidget(s))
            self.grup.addButton(buton, i)
            dikey.addWidget(buton)
            self.ogeler.append((buton, rozet))
        dikey.addStretch()

        self.kart = QFrame(objectName="kullanici_kart")
        kd = QVBoxLayout(self.kart)
        kd.setContentsMargins(10, 10, 10, 10)
        kd.setSpacing(8)
        satir = QHBoxLayout()
        self.avatar = QLabel(objectName="avatar")
        self.avatar.setFixedSize(40, 40)
        self.avatar.setAlignment(Qt.AlignCenter)
        yazi = QVBoxLayout()
        yazi.setSpacing(0)
        self.kul_ad = QLabel(objectName="kul_ad")
        self.kul_rol = QLabel(objectName="kul_rol")
        yazi.addWidget(self.kul_ad)
        yazi.addWidget(self.kul_rol)
        satir.addWidget(self.avatar)
        satir.addLayout(yazi, 1)
        kd.addLayout(satir)
        self.cikis = cikis_butonu
        cikis_butonu.setParent(self.kart)
        cikis_butonu.setStyleSheet("")
        cikis_butonu.setMinimumSize(0, 38)
        cikis_butonu.setMaximumSize(16777215, 38)
        cikis_butonu.setCursor(Qt.PointingHandCursor)
        cikis_butonu.setIcon(ikonlar.ikon("guc", "#FCA5A5"))
        cikis_butonu.show()
        kd.addWidget(cikis_butonu)
        dikey.addWidget(self.kart)
        self.imza = QLabel(IMZA, objectName="imza")
        self.imza.setAlignment(Qt.AlignCenter)
        dikey.addSpacing(4)
        dikey.addWidget(self.imza)

        sekmeler.tabBar().hide()
        sekmeler.currentChanged.connect(self.secili_yap)
        self.yenile()
        self.secili_yap(sekmeler.currentIndex())
        self.kapali = False
        self.daralt(tercihler.mantiksal("menu/kapali"), kaydet=False)

    def secili_yap(self, i):
        buton = self.grup.button(i)
        if buton:
            buton.setChecked(True)

    def yenile(self):
        ###  Sekme adlarını menüye yansıt; "(N gecikmiş)" kırmızı rozet olur  ###
        for i, (buton, rozet) in enumerate(self.ogeler):
            metin = self.sekmeler.tabText(i)
            eslesme = _SAYI.match(metin)
            ad, sayi = (eslesme.group(1), eslesme.group(2)) if eslesme else (metin, None)
            buton.ad = ad
            buton.setToolTip(f"{ad} ({sayi} gecikmiş)" if sayi else ad)
            rozet.setText(sayi or "")
            rozet.setVisible(bool(sayi))
            buton.setText("" if getattr(self, "kapali", False) else f"  {ad}")

    def kullanici(self, ad, rol):
        self.kul_ad.setText(ad)
        self.kul_rol.setText(rol)
        self.avatar.setText(bas_harfler(ad))
        self.avatar.setToolTip(f"{ad} · {rol}")

    def daralt(self, kapali, kaydet=True):
        ###  Kapalıyken sadece simgeler (adlar ipucu olarak görünür), açıkken taslaktaki tam menü  ###
        self.kapali = kapali
        self.setFixedWidth(KAPALI_EN if kapali else ACIK_EN)
        for gizlenecek in (self.baslik, self.kul_ad, self.kul_rol, self.imza):
            gizlenecek.setVisible(not kapali)
        self.cikis.setText("" if kapali else "Oturumu Kapat")
        self.cikis.setToolTip("Oturumu kapatıp giriş ekranına dön")
        self.btn_daralt.setIcon(ikonlar.ikon("menu" if kapali else "daralt", YAZI_RENGI, YAZI_RENGI))
        self.btn_daralt.setToolTip("Menüyü aç" if kapali else "Menüyü daralt")
        self.kart.layout().setContentsMargins(*((4, 8, 4, 8) if kapali else (10, 10, 10, 10)))
        self.yenile()
        if kaydet:
            tercihler.yaz("menu/kapali", "1" if kapali else "0")


def menuyu_yerlestir(pencere, menu):
    """Orta alan: solda menü, sağda sekme sayfaları."""
    sekmeler = menu.sekmeler
    duzen = pencere.centralWidget().layout()
    duzen.removeWidget(sekmeler)
    kap = QWidget()
    yatay = QHBoxLayout(kap)
    yatay.setContentsMargins(6, 6, 6, 6)
    yatay.setSpacing(12)
    yatay.addWidget(menu)
    yatay.addWidget(sekmeler, 1)
    duzen.addWidget(kap, 0, 0)
    sekmeler.setStyleSheet("QTabWidget#tabWidget::pane { border: none; }")


SEGMENT_STIL = f"""
#segment {{ background-color: #E2E8F0; border-radius: 10px; }}
QPushButton#segment_ogesi {{ background: transparent; color: #475569; border: none; border-radius: 8px;
               padding: 7px 18px; font-size: 15px; font-weight: bold; }}
QPushButton#segment_ogesi:hover {{ color: {tema.METIN}; }}
QPushButton#segment_ogesi:checked {{ background-color: white; color: {tema.VURGU_KOYU}; }}
"""


class SegmentAnahtari(QFrame):
    """Alt sekmelerin (ör. Kitaplar | Veri Düzeltme) yerine sayfanın üstünde iki-üç seçenekli anahtar."""

    def __init__(self, sekmeler, parent=None):
        super().__init__(parent)
        self.setObjectName("segment")
        self.setStyleSheet(SEGMENT_STIL)
        self.sekmeler = sekmeler
        yatay = QHBoxLayout(self)
        yatay.setContentsMargins(4, 4, 4, 4)
        yatay.setSpacing(4)
        self.grup = QButtonGroup(self)
        for i in range(sekmeler.count()):
            b = QPushButton(sekmeler.tabText(i), objectName="segment_ogesi")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _, i=i: sekmeler.setCurrentIndex(i))
            self.grup.addButton(b, i)
            yatay.addWidget(b)
        self.grup.button(max(0, sekmeler.currentIndex())).setChecked(True)
        sekmeler.currentChanged.connect(lambda i: self.grup.button(i) and self.grup.button(i).setChecked(True))


def segmente_cevir(sekmeler):
    """Alt sekme çubuğunu gizler, sayfanın üstüne segment anahtarı koyar."""
    sekmeler.tabBar().hide()
    sekmeler.setStyleSheet("QTabWidget::pane { border: none; background: transparent; }")
    sayfa = sekmeler.parentWidget()
    duzen = sayfa.layout()
    duzen.removeWidget(sekmeler)
    anahtar = SegmentAnahtari(sekmeler)
    ust = QHBoxLayout()
    ust.setContentsMargins(12, 10, 12, 0)
    ust.addWidget(anahtar)
    ust.addStretch()
    yeni = QVBoxLayout()
    yeni.addLayout(ust)
    yeni.addWidget(sekmeler, 1)
    duzen.addLayout(yeni, 0, 0)
    return anahtar
