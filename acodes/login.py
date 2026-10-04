from PySide6.QtWidgets import QApplication, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QSizePolicy, QVBoxLayout, QWidget
from PySide6.QtGui import QAction
from PySide6.QtCore import QEvent, QEventLoop, QSize, Qt
from PySide6.QtGui import QColor
import ctypes
import sys
from acodes.library import Library
from acodes.guest import Guest
from acodes import hareket, ikonlar, kilavuz, tema
from bforms.login_py import Ui_MainWindow
from database.kullanicilar import giris_kontrol


def panel_goster(panel):
    # Mac'te tam ekran ayrı bir masaüstü alanı açar, pencere küçültülemez; büyütülmüş pencere kullanılır
    if sys.platform=="darwin":
        panel.showMaximized()
    else:
        panel.showFullScreen()


def caps_lock_acik():
    """Caps Lock açık mı? Qt5 bunu sormaya izin vermediği için sistemden okunur; bilinemezse False."""
    try:
        if sys.platform=="darwin":
            servis=ctypes.cdll.LoadLibrary("/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices")
            servis.CGEventSourceFlagsState.restype=ctypes.c_uint64
            servis.CGEventSourceFlagsState.argtypes=[ctypes.c_int32]
            return bool(servis.CGEventSourceFlagsState(0) & 0x10000)    # birleşik oturum durumu, AlphaShift bayrağı
        if sys.platform=="win32":
            return bool(ctypes.windll.user32.GetKeyState(0x14) & 1)       # VK_CAPITAL
    except (OSError, AttributeError):
        pass
    return False


# Solda fotoğraf ve el yazısı başlık, sağda ortalanmış giriş kartı; yerleşim layout ile (sabit koordinat yok)
def giris_stili():
    return f"""
#giris_paneli {{ background-color: {tema.KART}; border-top-right-radius: {tema.KOSE.buyuk}px;
               border-bottom-right-radius: {tema.KOSE.buyuk}px; }}
#label_5 {{ color: white; font-family: "{tema.BASLIK_YAZISI}"; font-size: {tema.YAZI.logo_giris}px; font-style: normal; }}
#giris_karti QLabel {{ color: {tema.ETIKET}; font-size: {tema.YAZI.ince}px; font-weight: {tema.ORTA}; }}
#giris_karti QLabel#giris_baslik {{ color: {tema.METIN}; font-size: {tema.YAZI.buyuk}px; font-weight: {tema.YARI_KALIN}; }}
#giris_karti QLabel#giris_alt {{ color: {tema.IKINCIL_METIN}; font-size: {tema.YAZI.ince}px; font-weight: normal; }}
#giris_karti QLineEdit {{ font-size: {tema.YAZI.metin}px; padding: 8px 10px; border-radius: {tema.KOSE.kucuk}px; min-height: 22px; }}
#giris_karti QLabel#giris_mesaj {{ color: {tema.TEHLIKE}; font-weight: normal; }}
#giris_karti QLabel#giris_mesaj[tur="bilgi"] {{ color: {tema.BASARI}; }}
#giris_karti QLabel#caps_uyari {{ color: {tema.UYARI}; font-size: {tema.YAZI.kucuk}px; }}
QLabel#giris_imza {{ color: {tema.IKINCIL_METIN}; font-size: {tema.YAZI.kucuk}px; font-weight: normal; }}
#pushButton_giris {{ font-size: {tema.YAZI.metin}px; font-weight: {tema.YARI_KALIN}; padding: 10px;
               border-radius: {tema.KOSE.kucuk}px; }}
#pushButton_cikis {{ background: transparent; border: none; border-radius: {tema.KOSE.kucuk}px; padding: 0; }}
#pushButton_cikis:hover {{ background-color: {tema.TEHLIKE_ACIK}; }}
"""


class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.QtLogin = Ui_MainWindow()
        self.QtLogin.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(self.minimumSize())
        ekran=QApplication.primaryScreen()
        if ekran is not None:                     # ekranın ortasında açılır
            alan=ekran.availableGeometry()
            self.move(alan.center().x()-self.width()//2, alan.center().y()-self.height()//2)
        self.setWindowTitle("Yaşar Kütüphanesi - Giriş")
        self.library=None  # Paneller giriş yapılınca oluşturulur
        self.guest=None
        self._surukle=None
        self.tasarim()

        self.QtLogin.pushButton_giris.clicked.connect(self.giris)
        self.QtLogin.lineEdit_parola.returnPressed.connect(self.giris)
        self.QtLogin.lineEdit_kullanci_adi.returnPressed.connect(self.QtLogin.lineEdit_parola.setFocus)
        self.QtLogin.pushButton_cikis.setToolTip("Programdan çık")
        self.QtLogin.pushButton_cikis.clicked.connect(self.close)
        self.QtLogin.lineEdit_kullanci_adi.setFocus()   # açılınca doğrudan kullanıcı adı yazılabilsin

    def tasarim(self):
        ###  Solda fotoğraf ve başlık, sağda panel: üstte kapatma (×), ortada giriş kartı, altta imza  ###
        ui=self.QtLogin
        ui.statusbar.hide()                       # mesajlar kartın içinde gösterilir
        ui.label_2.deleteLater()                  # .ui'daki sağ zemin yerine layout'lu panel

        foto=ui.label
        foto.setFixedWidth(410)
        foto.setStyleSheet(f"QLabel#label {{ border-image: url(:/pic/login.jpeg); border-top-left-radius: {tema.KOSE.buyuk}px;"
                           f" border-bottom-left-radius: {tema.KOSE.buyuk}px; }}")   # seçicili: başlığa geçmesin
        ust_yazi=QVBoxLayout(foto)
        ust_yazi.setContentsMargins(12,60,12,0)
        ust_yazi.addWidget(ui.label_5)
        ust_yazi.addStretch()
        ui.label_5.setAlignment(Qt.AlignCenter)
        golge=QGraphicsDropShadowEffect(ui.label_5)
        golge.setBlurRadius(16)
        golge.setOffset(0,2)
        golge.setColor(QColor(0,0,0,180))
        ui.label_5.setGraphicsEffect(golge)

        kart=QWidget(objectName="giris_karti")
        self.kart=kart                            # yanlış girişte sallanır
        kart.setFixedWidth(320)
        duzen=QVBoxLayout(kart)
        duzen.setContentsMargins(0,0,0,0)
        duzen.setSpacing(8)
        alt=QLabel("Devam etmek için hesabınıza giriş yapın.",objectName="giris_alt")
        alt.setWordWrap(True)
        self.mesaj=QLabel("",objectName="giris_mesaj")
        self.mesaj.setWordWrap(True)
        self.mesaj.setMinimumHeight(20)
        self.caps=QLabel("Caps Lock açık",objectName="caps_uyari")
        bosluk_kalsin=self.caps.sizePolicy()
        bosluk_kalsin.setRetainSizeWhenHidden(True)   # görünüp kaybolurken kart kaymasın
        self.caps.setSizePolicy(bosluk_kalsin)
        self.caps.hide()
        for alan,ipucu in ((ui.lineEdit_kullanci_adi,"Kullanıcı adınız"),(ui.lineEdit_parola,"Parolanız")):
            alan.setParent(kart)
            alan.setPlaceholderText(ipucu)
            alan.setMinimumWidth(0)
            alan.setMaximumWidth(16777215)
            alan.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            alan.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        ui.lineEdit_parola.setEchoMode(QLineEdit.Password)
        ui.lineEdit_parola.installEventFilter(self)   # Caps Lock uyarısı
        ui.pushButton_giris.setParent(kart)
        ui.pushButton_giris.setMinimumSize(0,46)
        ui.pushButton_giris.setMaximumSize(16777215,46)
        ui.pushButton_giris.setCursor(Qt.PointingHandCursor)
        duzen.addWidget(QLabel("Giriş Yap",objectName="giris_baslik"))
        duzen.addWidget(alt)
        duzen.addSpacing(18)
        duzen.addWidget(QLabel("Kullanıcı adı"))
        duzen.addWidget(ui.lineEdit_kullanci_adi)
        duzen.addSpacing(6)
        duzen.addWidget(QLabel("Parola"))
        duzen.addWidget(ui.lineEdit_parola)
        duzen.addWidget(self.caps)
        duzen.addWidget(self.mesaj)
        duzen.addWidget(ui.pushButton_giris)

        # Parolayı göster/gizle
        self.goster=QAction("Parolayı göster",ui.lineEdit_parola)
        self.goster.triggered.connect(self.parola_goster_gizle)
        ui.lineEdit_parola.addAction(self.goster,QLineEdit.TrailingPosition)
        ikonlar.yazili_ikon(ui.pushButton_giris, "ok_sag")

        cikis=ui.pushButton_cikis
        cikis.setFixedSize(32,32)
        cikis.setIconSize(QSize(16,16))
        cikis.setCursor(Qt.PointingHandCursor)
        self.imza=QLabel(kilavuz.IMZA,objectName="giris_imza")
        self.imza.setAlignment(Qt.AlignRight)

        panel=QFrame(objectName="giris_paneli")
        sag=QVBoxLayout(panel)
        sag.setContentsMargins(24,12,12,18)
        ust=QHBoxLayout()
        ust.addStretch()
        ust.addWidget(cikis)
        sag.addLayout(ust)
        sag.addStretch(2)
        sag.addWidget(kart,0,Qt.AlignHCenter)
        sag.addStretch(3)
        sag.addWidget(self.imza)

        yatay=QHBoxLayout(ui.widget)
        yatay.setContentsMargins(0,0,0,0)
        yatay.setSpacing(0)
        yatay.addWidget(foto)
        yatay.addWidget(panel,1)
        dis=QVBoxLayout(ui.centralwidget)
        dis.setContentsMargins(18,18,18,18)
        dis.addWidget(ui.widget)
        self.stil_uygula()

    def stil_uygula(self):
        ###  Temaya bağlı renkler (açılışta ve görünüm değişince)  ###
        gizli=self.QtLogin.lineEdit_parola.echoMode()==QLineEdit.Password
        self.goster.setIcon(ikonlar.ikon("goz" if gizli else "goz_kapali",tema.IKON))
        self.QtLogin.pushButton_cikis.setIcon(ikonlar.ikon("x",tema.IKON))
        self.setStyleSheet(tema.qss()+giris_stili())

    def parola_goster_gizle(self):
        alan=self.QtLogin.lineEdit_parola
        gizli=alan.echoMode()==QLineEdit.Password
        alan.setEchoMode(QLineEdit.Normal if gizli else QLineEdit.Password)
        self.goster.setIcon(ikonlar.ikon("goz_kapali" if gizli else "goz",tema.IKON))
        self.goster.setText("Parolayı gizle" if gizli else "Parolayı göster")

    def mesaj_goster(self,metin,tur="hata"):
        self.mesaj.setText(metin)
        self.mesaj.setProperty("tur",tur)
        self.mesaj.style().unpolish(self.mesaj)   # tür değişince rengi yeniden uygula
        self.mesaj.style().polish(self.mesaj)

    def eventFilter(self,nesne,olay):
        # Parola kutusundayken Caps Lock açıksa uyar
        if nesne is self.QtLogin.lineEdit_parola:
            if olay.type() in (QEvent.FocusIn,QEvent.KeyPress,QEvent.KeyRelease):
                self.caps.setVisible(caps_lock_acik())
            elif olay.type()==QEvent.FocusOut:
                self.caps.hide()
        return super().eventFilter(nesne,olay)

    def _bekliyor(self,durum):
        ###  Giriş sürerken (şifre denetimi, panelin kurulması) buton kapalı ve "Giriş yapılıyor…" yazar  ###
        buton=self.QtLogin.pushButton_giris
        buton.setEnabled(not durum)
        buton.setText("Giriş yapılıyor…" if durum else "Giriş")
        if durum:       # yazı panel açılmadan görünsün; bu arada yapılan tıklama ve tuşlar işlenmez
            QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    # Çerçevesiz pencere fareyle sürüklenerek taşınabilir
    def mousePressEvent(self,olay):
        if olay.button()==Qt.LeftButton:
            self._surukle=olay.globalPosition().toPoint()-self.frameGeometry().topLeft()

    def mouseMoveEvent(self,olay):
        if self._surukle is not None and olay.buttons() & Qt.LeftButton:
            self.move(olay.globalPosition().toPoint()-self._surukle)

    def mouseReleaseEvent(self,olay):
        self._surukle=None

    def giris(self):
        ad=self.QtLogin.lineEdit_kullanci_adi.text()
        sifre=self.QtLogin.lineEdit_parola.text()

        if ad=="" or sifre=="":
            self.mesaj_goster("Kullanıcı adı ve parola bilgilerini giriniz!")
            for alan in (self.QtLogin.lineEdit_kullanci_adi,self.QtLogin.lineEdit_parola):
                if alan.text()=="":
                    hareket.hata_vurgula(alan)
            return
        self._bekliyor(True)
        try:
            yetki=giris_kontrol(ad,sifre)
            if yetki is None:
                # Hangisinin yanlış olduğu söylenmez (kullanıcı adı tahminini zorlaştırır)
                self.mesaj_goster("Kullanıcı adı veya parola yanlış!")
                hareket.salla(self.kart)
                self.QtLogin.lineEdit_parola.selectAll()
                self.QtLogin.lineEdit_parola.setFocus()
            elif yetki in ('admin','guest'):
                # Her oturumda panel sıfırdan oluşturulur; önceki kullanıcıdan bir şey kalmaz
                self.mesaj_goster("")
                self.panel_ac(yetki,ad)
                self.hide()
            else:
                self.mesaj_goster("Yetkiniz yok!")
        finally:
            self._bekliyor(False)

    def panel_ac(self,yetki,ad,goster=True):
        panel=Library() if yetki=='admin' else Guest()
        if yetki=='admin':
            self.library=panel
        else:
            self.guest=panel
        panel.user_name(ad)
        panel.oturum_kapandi.connect(self.giris_ekranina_don)
        panel.ayarlar.gorunum.degisti.connect(self.gorunumu_degistir)
        if goster:
            panel_goster(panel)
            hareket.pencere_belir(panel)          # giriş ekranından panele yumuşak geçiş
        return panel

    def gorunumu_degistir(self,gorunum):
        ###  Ayarlar > Görünüm: tema değişir, panel aynı kullanıcı, sayfa, kaydırma ve pencere boyutuyla yeniden kurulur  ###
        # Yeni panel gösterilmeden önce eskisinin yerine oturtulur: sayfa en üste zıplamaz, pencere yeniden büyümez.
        # Eski görünümün resmi yeni panelin üstünde solarak kaybolur (yanıp sönme yerine yumuşak geçiş).
        eski=self.library or self.guest
        goruntu=eski.grab() if hareket.acik_mi(eski) else None    # stil değişmeden önce
        if eski is not None:
            eski.bildirim.temizle()             # stil değişirken bildirim animasyonu sürmesin
        tema.ayarla(gorunum)
        tema.uygulamaya_uygula(QApplication.instance())
        self.stil_uygula()
        if eski is None:
            return
        sekme=eski.sekmeler.currentIndex()
        kaydirma=eski.ayarlar.verticalScrollBar().value()
        yeni=self.panel_ac('admin' if eski is self.library else 'guest',eski.aktif_kullanici,goster=False)
        yeni.sekmeler.setCurrentIndex(sekme)
        yeni.bildirim.temizle()                 # açılıştaki gecikme uyarısı tema değişiminde tekrar çıkmasın
        yeni.statusBar().clearMessage()
        yeni.setGeometry(eski.geometry())
        if eski.isFullScreen():
            yeni.showFullScreen()
        elif eski.isMaximized():
            yeni.showMaximized()
        else:
            yeni.show()
        yeni.ayarlar.widget().adjustSize()
        QApplication.processEvents()            # sayfa yerleşsin, kaydırma sınırı belli olsun
        yeni.ayarlar.verticalScrollBar().setValue(kaydirma)
        hareket.perde(yeni,goruntu)
        eski.hide()
        eski.deleteLater()

    def giris_ekranina_don(self):
        for panel in (self.library,self.guest):
            if panel is not None:
                panel.deleteLater()
        self.library=None
        self.guest=None
        self.QtLogin.lineEdit_kullanci_adi.clear()
        self.QtLogin.lineEdit_parola.clear()
        self.show()
        hareket.pencere_belir(self)
        self.raise_()
        self.activateWindow()
        self.QtLogin.lineEdit_kullanci_adi.setFocus()
        self.mesaj_goster("Oturum kapatıldı.","bilgi")
