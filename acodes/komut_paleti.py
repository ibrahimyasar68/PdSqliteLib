## Hızlı arama (Ctrl+K, Mac'te ⌘K) ##
# Panelin her yerinden açılan tek arama kutusu: menü bölümleri, işlemler (Yeni kitap, Yedek al ...), kitaplar ve
# (yöneticide) üyeler. Yazdıkça süzülür; büyük/küçük harf ve Türkçe karakter farkı gözetilmez. Ok tuşlarıyla
# seçilip Enter ile çalıştırılır, Esc kapatır. Ne listeleneceğini panel verir (kaynak fonksiyonu).

from PyQt5.QtCore import QEvent, QSize, Qt, QTimer
from PyQt5.QtWidgets import QDialog, QFrame, QLabel, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout

from acodes import hareket, ikonlar, tema
from database.metin import katla

EN = 680
ISLEV = Qt.UserRole


def eslesir(metin, *alanlar):
    """Yazılan kelimelerin hepsi alanlardan birinde geçiyor mu?"""
    hepsi = katla(" ".join(str(a) for a in alanlar if a))
    return all(k in hepsi for k in katla(metin).split())


def stil():
    return f"""
#palet {{ background-color: {tema.KART}; border: 1px solid {tema.KENAR}; border-radius: {tema.KOSE.buyuk}px; }}
#palet_arama {{ font-size: {tema.YAZI.alt_baslik}px; padding: 10px 12px; border: none; border-bottom: 1px solid {tema.KENAR};
               border-radius: 0; background: transparent; }}
#palet_arama:focus {{ border: none; border-bottom: 1px solid {tema.KENAR}; }}
#palet_liste {{ border: none; background: transparent; outline: none; }}
#palet_liste::item {{ padding: 6px 10px; border-radius: {tema.KOSE.kucuk}px; color: {tema.METIN}; }}
#palet_liste::item:selected {{ background-color: {tema.VURGU_ACIK}; color: {tema.METIN}; }}
#palet_ipucu {{ color: {tema.SOLUK}; font-size: {tema.YAZI.ince}px; padding: 6px 12px; border-top: 1px solid {tema.KENAR}; }}
"""


class KomutPaleti(QDialog):
    def __init__(self, kaynak, parent):
        """kaynak(metin) -> [(grup adı, [(başlık, açıklama, ikon adı, işlev)])]; boş gruplar gösterilmez."""
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.kaynak = kaynak
        self.setAttribute(Qt.WA_TranslucentBackground)
        cerceve = QFrame(objectName="palet")
        cerceve.setStyleSheet(stil())
        ic = QVBoxLayout(cerceve)
        ic.setContentsMargins(6, 6, 6, 4)
        ic.setSpacing(4)
        self.arama = QLineEdit(objectName="palet_arama")
        self.arama.setPlaceholderText("Kitap, üye veya bölüm arayın...")
        self.arama.setClearButtonEnabled(True)
        self.arama.textChanged.connect(self.doldur)
        self.arama.installEventFilter(self)
        self.liste = QListWidget(objectName="palet_liste")
        self.liste.setIconSize(QSize(18, 18))
        self.liste.setFocusPolicy(Qt.NoFocus)          # yazı kutusu odakta kalır, oklar listeyi gezer
        self.liste.itemClicked.connect(self.calistir)
        ipucu = QLabel("↑ ↓ seç   ·   Enter aç   ·   Esc kapat", objectName="palet_ipucu")
        ic.addWidget(self.arama)
        ic.addWidget(self.liste, 1)
        ic.addWidget(ipucu)
        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(0, 0, 0, 0)
        duzen.addWidget(cerceve)
        self.resize(EN, 460)

    def ac(self):
        pencere = self.parentWidget().window()
        sol_ust = pencere.mapToGlobal(pencere.rect().topLeft())
        en = min(EN, pencere.width() - 40)
        self.resize(en, min(460, pencere.height() - 120))
        self.move(sol_ust.x() + (pencere.width() - en) // 2, sol_ust.y() + 70)
        self.arama.clear()
        self.doldur("")
        self.show()
        hareket.acilir_pencere_belir(self)          # birkaç piksel aşağıdan kayarak ve belirerek gelir
        self.raise_()
        self.activateWindow()
        self.arama.setFocus(Qt.PopupFocusReason)

    def doldur(self, metin=None):
        metin = self.arama.text() if metin is None else metin
        self.liste.clear()
        for grup, ogeler in self.kaynak(metin.strip()):
            if not ogeler:
                continue
            baslik = QListWidgetItem(grup.upper())
            baslik.setFlags(Qt.NoItemFlags)
            yazi = baslik.font()
            yazi.setPixelSize(tema.YAZI.kucuk)
            yazi.setBold(True)
            baslik.setFont(yazi)
            baslik.setForeground(self.palette().placeholderText())
            self.liste.addItem(baslik)
            for ad, aciklama, ikon_adi, islev in ogeler:
                oge = QListWidgetItem(f"{ad}   —   {aciklama}" if aciklama else ad)
                if ikon_adi:
                    oge.setIcon(ikonlar.ikon(ikon_adi, tema.IKON, tema.IKON))
                oge.setData(ISLEV, islev)
                self.liste.addItem(oge)
        if not self.secilebilenler():
            bos = QListWidgetItem("Sonuç yok")
            bos.setFlags(Qt.NoItemFlags)
            self.liste.addItem(bos)
        self.sec(0)

    def secilebilenler(self):
        return [i for i in range(self.liste.count()) if self.liste.item(i).data(ISLEV) is not None]

    def sec(self, sira):
        """sira: seçilebilen öğeler arasında kaçıncısı (taşarsa başa/sona döner)."""
        secilebilen = self.secilebilenler()
        if not secilebilen:
            return
        satir = secilebilen[sira % len(secilebilen)]
        self.liste.setCurrentRow(satir)
        self.liste.scrollToItem(self.liste.item(satir))

    def adim(self, yon):
        secilebilen = self.secilebilenler()
        if secilebilen:
            simdiki = self.liste.currentRow()
            sira = secilebilen.index(simdiki) if simdiki in secilebilen else -1
            self.sec(sira + yon)

    def calistir(self, oge=None):
        oge = oge or self.liste.currentItem()
        islev = oge.data(ISLEV) if oge else None
        if islev is None:
            return
        self.close()
        QTimer.singleShot(0, islev)           # palet kapandıktan sonra (açılan pencere odaklansın)

    def eventFilter(self, nesne, olay):
        if olay.type() == QEvent.KeyPress:
            tus = olay.key()
            if tus in (Qt.Key_Down, Qt.Key_Up):
                self.adim(1 if tus == Qt.Key_Down else -1)
                return True
            if tus in (Qt.Key_Return, Qt.Key_Enter):
                self.calistir()
                return True
            if tus == Qt.Key_Escape:
                self.close()
                return True
        return False
