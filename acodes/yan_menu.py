## Sol kenar menüsü ve alt sekmeler için üstte segment anahtarı ##
# Üstteki sekme çubuğunun yerine solda koyu, yarı saydam bir menü: en üstte "Yaşar Kütüphanesi", ikonlu
# bölümler, altta kullanıcı kartı (ad, yetki, Oturumu Kapat) ve imza. Daraltılınca yalnızca simgeler kalır;
# açık/kapalı durumu hatırlanır. Sekme adındaki "(N gecikmiş)" menüde kırmızı rozet olarak görünür.

import re

from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QButtonGroup, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from acodes import hareket, ikonlar, tema, tercihler
from acodes.kilavuz import IMZA
from acodes.kisayollar import metin as kisayol_metni

ACIK_EN, KAPALI_EN = 260, 76
_SAYI = re.compile(r"^(.*) \((\d+) gecikmiş\)$")

def stil():
    t, Y, K = tema, tema.YAZI, tema.KOSE
    return f"""
#yan_menu {{ background-color: rgba({t.MENU_ZEMIN_RGB}, 0.88); border-radius: {K.buyuk}px; }}
#menu_baslik {{ color: {t.MENU_LOGO}; font-family: "{t.BASLIK_YAZISI}"; font-size: {Y.logo_menu}px; font-style: normal; }}
QPushButton#menu_ogesi {{ background: transparent; color: {t.MENU_OGE}; border: none; border-radius: {K.kucuk}px;
               text-align: left; padding: 11px 13px; font-size: {Y.metin}px; font-weight: {t.ORTA}; }}
QPushButton#menu_ogesi:hover {{ background-color: rgba(255,255,255,0.08); color: white; }}
QPushButton#menu_ogesi:checked {{ background: transparent; color: white; font-weight: {t.YARI_KALIN}; }}
#menu_vurgu {{ background-color: rgba(96,165,250,0.24); border-radius: {K.kucuk}px; }}
QPushButton#menu_ara {{ background-color: rgba(255,255,255,0.07); color: {t.MENU_IKINCIL};
               border: 1px solid rgba(255,255,255,0.10); border-radius: {K.kucuk}px; text-align: left; padding: 8px 12px;
               font-size: {Y.metin}px; }}
QPushButton#menu_ara:hover {{ background-color: rgba(255,255,255,0.12); color: white; }}
#menu_ara_kisayol {{ color: {t.MENU_SONUK}; font-size: {Y.ince}px; }}
QPushButton#daralt {{ background: transparent; border: none; border-radius: {K.kucuk}px; padding: 6px; }}
QPushButton#daralt:hover {{ background-color: rgba(255,255,255,0.10); }}
#rozet {{ background-color: {t.TEHLIKE}; color: white; border-radius: 9px; font-size: {Y.kucuk}px; font-weight: bold;
               padding: 0 6px; min-width: 8px; }}
#kullanici_kart {{ background-color: rgba(255,255,255,0.06); border-radius: {K.orta}px; }}
#avatar {{ background-color: {t.VURGU}; color: white; border-radius: 20px; font-size: {Y.metin}px;
               font-weight: {t.YARI_KALIN}; }}
#kul_ad {{ color: white; font-size: {Y.metin}px; font-weight: {t.YARI_KALIN}; }}
#kul_rol {{ color: {t.MENU_IKINCIL}; font-size: {Y.ince}px; }}
QPushButton#pushButton_1_cikis {{ background: transparent; color: {t.MENU_CIKIS}; border: 1px solid rgba(252,165,165,0.5);
               border-radius: {K.kucuk}px; padding: 8px; font-size: {Y.ince}px; font-weight: {t.ORTA}; }}
QPushButton#pushButton_1_cikis:hover {{ background-color: rgba(220,38,38,0.25); color: white; }}
#imza {{ color: {t.MENU_SONUK}; font-size: {Y.kucuk}px; }}
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
        self.setStyleSheet(stil())
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
        dikey.addSpacing(8)
        # Hızlı arama (Ctrl+K): paneli panel bağlar
        self.btn_ara = QPushButton(objectName="menu_ara")
        self.btn_ara.setCursor(Qt.PointingHandCursor)
        self.btn_ara.setIcon(ikonlar.ikon("ara", tema.MENU_IKINCIL, tema.MENU_IKINCIL))
        self.btn_ara.setIconSize(QSize(17, 17))
        self.btn_ara.setMinimumHeight(38)
        self.ara_kisayol = QLabel(objectName="menu_ara_kisayol")
        self.ara_kisayol.setText(kisayol_metni("Ctrl+K"))
        ara_ic = QHBoxLayout(self.btn_ara)
        ara_ic.setContentsMargins(0, 0, 10, 0)
        ara_ic.addStretch()
        ara_ic.addWidget(self.ara_kisayol)
        dikey.addWidget(self.btn_ara)
        dikey.addSpacing(8)

        self.grup = QButtonGroup(self)
        self.ogeler = []
        for i in range(sekmeler.count()):
            sayfa = sekmeler.widget(i)
            buton = QPushButton(objectName="menu_ogesi")
            buton.setCheckable(True)
            buton.setCursor(Qt.PointingHandCursor)
            buton.setIcon(ikonlar.ikon(ikonlar.SEKME_IKONLARI[sayfa_ikonlari[sayfa]], tema.MENU_YAZI, tema.MENU_YAZI))
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
        # Seçili bölümün zemini butonların arkasında ayrı bir parça: bölüm değişince kayarak gider
        self.vurgu = hareket.KayanVurgu(self, self.grup, "menu_vurgu")

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
        cikis_butonu.show()
        kd.addWidget(cikis_butonu)
        dikey.addWidget(self.kart)
        self.imza = QLabel(IMZA, objectName="imza")
        self.imza.setAlignment(Qt.AlignCenter)
        dikey.addSpacing(4)
        dikey.addWidget(self.imza)

        sekmeler.tabBar().hide()
        sekmeler.currentChanged.connect(self.secili_yap)
        sekmeler.currentChanged.connect(lambda i: hareket.belir(sekmeler.widget(i)))   # yeni sayfa hafifçe belirir
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
            onceki, rozet.sayi = getattr(rozet, "sayi", 0), int(sayi or 0)
            if rozet.sayi > onceki:
                hareket.nabiz(rozet)            # gecikme arttı: rozet bir kez dikkat çeker (sürekli değil)
            buton.setText("" if getattr(self, "kapali", False) else f"  {ad}")

    def showEvent(self, olay):
        super().showEvent(olay)
        if not getattr(self, "_ilk_gorunus", False):
            self._ilk_gorunus = True
            # Panel açılınca gecikme rozeti bir kez atar (yerleşim bittikten sonra)
            QTimer.singleShot(0, self._rozetleri_atlat)

    def _rozetleri_atlat(self):
        for _, rozet in self.ogeler:
            if rozet.isVisible():
                hareket.nabiz(rozet)

    def kullanici(self, ad, rol):
        self.kul_ad.setText(ad)
        self.kul_rol.setText(rol)
        self.avatar.setText(bas_harfler(ad))
        self.avatar.setToolTip(f"{ad} · {rol}")

    def daralt(self, kapali, kaydet=True):
        ###  Kapalıyken sadece simgeler (adlar ipucu olarak görünür), açıkken taslaktaki tam menü  ###
        # Genişlik yumuşakça değişir; daralırken yazılar hemen gizlenir, açılırken genişlik yerine oturunca görünür
        self.kapali = kapali
        if kapali:
            self._gorunumu_uygula(True)
            hareket.genislige_kay(self, KAPALI_EN)
        else:
            hareket.genislige_kay(self, ACIK_EN, lambda: self._gorunumu_uygula(False))
        if kaydet:
            tercihler.yaz("menu/kapali", "1" if kapali else "0")

    def _gorunumu_uygula(self, kapali):
        for gizlenecek in (self.baslik, self.kul_ad, self.kul_rol, self.imza, self.ara_kisayol):
            gizlenecek.setVisible(not kapali)
        self.btn_ara.setText("" if kapali else " Hızlı ara")
        self.cikis.setText("" if kapali else "Oturumu Kapat")
        if kapali:          # yalnızca simge: ortalı dursun diye yanında boşluk payı olmayan ikon
            self.cikis.setIcon(ikonlar.ikon("guc", tema.MENU_CIKIS))
            self.cikis.setIconSize(QSize(16, 16))
        else:
            ikonlar.yazili_ikon(self.cikis, "guc", tema.MENU_CIKIS)
        self.cikis.setToolTip("Oturumu kapatıp giriş ekranına dön")
        self.btn_daralt.setIcon(ikonlar.ikon("menu" if kapali else "daralt", tema.MENU_YAZI, tema.MENU_YAZI))
        self.btn_daralt.setToolTip("Menüyü aç" if kapali else "Menüyü daralt")
        self.kart.layout().setContentsMargins(*((4, 8, 4, 8) if kapali else (10, 10, 10, 10)))
        self.yenile()


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


def segment_stil():
    return f"""
#segment {{ background-color: {tema.YUZEY_2}; border-radius: {tema.KOSE.orta}px; }}
QPushButton#segment_ogesi {{ background: transparent; color: {tema.IKON}; border: none; border-radius: {tema.KOSE.kucuk}px;
               padding: 7px 18px; min-width: 0; font-size: {tema.YAZI.metin}px; font-weight: {tema.ORTA}; }}
QPushButton#segment_ogesi:hover {{ color: {tema.METIN}; }}
QPushButton#segment_ogesi:checked {{ background: transparent; color: {tema.VURGU_YAZI}; }}
#segment_vurgu {{ background-color: {tema.KART}; border-radius: {tema.KOSE.kucuk}px; }}
"""


class SegmentAnahtari(QFrame):
    """Alt sekmelerin (ör. Kitaplar | Veri Düzeltme) yerine sayfanın üstünde iki-üç seçenekli anahtar.
    sekmeler verilmezse adlar listesindeki seçenekler gösterilir (ör. Ayarlar > Görünüm); seçim secildi(i) ile
    bildirilir."""
    secildi = pyqtSignal(int)

    def __init__(self, sekmeler=None, parent=None, adlar=(), secili=0):
        super().__init__(parent)
        self.setObjectName("segment")
        self.setStyleSheet(segment_stil())
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.sekmeler = sekmeler
        if sekmeler is not None:
            adlar = [sekmeler.tabText(i) for i in range(sekmeler.count())]
            secili = sekmeler.currentIndex()
        yatay = QHBoxLayout(self)
        yatay.setContentsMargins(4, 4, 4, 4)
        yatay.setSpacing(4)
        self.grup = QButtonGroup(self)
        for i, ad in enumerate(adlar):
            b = QPushButton(ad, objectName="segment_ogesi")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _, i=i: self._tiklandi(i))
            self.grup.addButton(b, i)
            yatay.addWidget(b)
        self.grup.button(max(0, secili)).setChecked(True)
        self.vurgu = hareket.KayanVurgu(self, self.grup, "segment_vurgu")     # seçili zemin kayarak gider
        if sekmeler is not None:
            sekmeler.currentChanged.connect(lambda i: self.grup.button(i) and self.grup.button(i).setChecked(True))

    def _tiklandi(self, i):
        if self.sekmeler is not None:
            self.sekmeler.setCurrentIndex(i)
        self.secildi.emit(i)


def segmente_cevir(sekmeler, baslik=None):
    """Alt sekme çubuğunu gizler, sayfanın üstüne segment anahtarı koyar. baslik: anahtarın solundaki sayfa adı
    (her sayfanın üstünde aynı düzen: solda sayfa adı, yanında alt bölümler)."""
    sekmeler.tabBar().hide()
    sekmeler.setStyleSheet("QTabWidget::pane { border: none; background: transparent; }")
    sayfa = sekmeler.parentWidget()
    duzen = sayfa.layout()
    duzen.removeWidget(sekmeler)
    anahtar = SegmentAnahtari(sekmeler)
    ust = QHBoxLayout()
    ust.setContentsMargins(14, 10, 12, 0)
    if baslik:
        ust.addWidget(QLabel(baslik, objectName="sayfa_baslik"))
        ust.addSpacing(16)
    ust.addWidget(anahtar)
    ust.addStretch()
    yeni = QVBoxLayout()
    yeni.addLayout(ust)
    yeni.addWidget(sekmeler, 1)
    duzen.addLayout(yeni, 0, 0)
    return anahtar
