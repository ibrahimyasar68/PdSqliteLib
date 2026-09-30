## Kitap Kayıt > Veri Düzeltme alt sekmesi ##
# Sol: aynı değerin farklı yazımları (ör. "Adam Yayınları" / "Adam yayınları") ve birleştirme.
# Sağ: yılı, yayınevi, yazarı veya türü boş olan kitaplar (çift tıklayınca düzenlemede açılır).

import datetime
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QComboBox, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QTableWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)
from bforms.onay import onay
from acodes import tema
from acodes.tablo import tablo_ayarla, tabloya_yaz
from database.duzeltme import benzer_gruplar, birlestir, eksik_kitaplar, yoksay
from database.yedek import yedek_al, yedek_klasoru

ALANLAR = [("Yazari", "Yazar"), ("Yayinevi", "Yayınevi"), ("Ceviren", "Çevirmen"), ("Turu", "Tür")]
EKSIK_ALANLAR = [("Yili", "Basım yılı"), ("Yayinevi", "Yayınevi"), ("Yazari", "Yazar"), ("Turu", "Tür")]


class VeriDuzeltme(QWidget):
    def __init__(self, kitap_duzenle=None, degisti=None, parent=None):
        """kitap_duzenle(id): kitabı düzenleme ekranında açar. degisti(): veri değişince çağrılır."""
        super().__init__(parent)
        self.kitap_duzenle = kitap_duzenle
        self.degisti = degisti
        self.yedek_alindi = None
        self.setObjectName("tab_3_4")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            #tab_3_4 {{ background-color: {tema.SAYFA}; }}
            QLabel, QComboBox, QLineEdit, QTableWidget, QGroupBox, QPushButton {{ font: 11pt "Verdana"; }}
        """)

        # --- Benzer yazımlar
        self.alan = QComboBox()
        for kol, ad in ALANLAR:
            self.alan.addItem(ad, kol)
        self.ozet = QLabel()
        self.agac = QTreeWidget()
        self.agac.setFont(QFont("Verdana", 11))
        # Pencerenin stil sayfası altında macOS onay kutularını boş çiziyor; görünümleri açıkça verilir
        self.agac.setStyleSheet(f"""
            QTreeWidget::indicator {{ width: 14px; height: 14px; border: 1px solid #5A5A5A;
                                     border-radius: 3px; background-color: white; }}
            QTreeWidget::indicator:checked {{ background-color: {tema.VURGU}; border-color: {tema.VURGU_KOYU}; }}
        """)
        self.agac.setHeaderLabels(["Yazım (birleştirilecekleri işaretleyin)", "Kitap"])
        self.agac.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.agac.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.hedef = QLineEdit()
        self.hedef.setPlaceholderText("Doğru yazım")
        self.btn_birlestir = QPushButton("İşaretlileri Birleştir")
        self.btn_yoksay = QPushButton("Bu Öneriyi Yoksay")

        ust = QHBoxLayout()
        ust.addWidget(QLabel("Alan:"))
        ust.addWidget(self.alan)
        ust.addWidget(self.ozet, 1)
        alt = QHBoxLayout()
        alt.addWidget(QLabel("Doğru yazım:"))
        alt.addWidget(self.hedef, 1)
        alt.addWidget(self.btn_birlestir)
        alt.addWidget(self.btn_yoksay)
        benzer = QGroupBox("Aynı değerin farklı yazımları")
        kutu = QVBoxLayout(benzer)
        kutu.addLayout(ust)
        kutu.addWidget(self.agac)
        kutu.addLayout(alt)

        # --- Eksik bilgiler
        self.eksik_alan = QComboBox()
        for kol, ad in EKSIK_ALANLAR:
            self.eksik_alan.addItem(ad, kol)
        self.eksik_ozet = QLabel()
        self.eksik_tablo = QTableWidget(0, 5)
        self.eksik_tablo.setHorizontalHeaderLabels(["Sıra No", "Adı", "Yazarı", "Yayınevi", "Yılı"])
        baslik = self.eksik_tablo.horizontalHeader()
        for kol, mod in enumerate([QHeaderView.ResizeToContents, QHeaderView.Stretch, QHeaderView.Interactive,
                                   QHeaderView.Interactive, QHeaderView.ResizeToContents]):
            baslik.setSectionResizeMode(kol, mod)
        self.eksik_tablo.setColumnWidth(2, 140)
        self.eksik_tablo.setColumnWidth(3, 140)
        self.eksik_tablo.setWordWrap(False)
        self.eksik_tablo.setToolTip("Kitabı düzenlemek için satıra çift tıklayın")
        tablo_ayarla(self.eksik_tablo)
        eksik = QGroupBox("Eksik bilgiler")
        kutu2 = QVBoxLayout(eksik)
        satir = QHBoxLayout()
        satir.addWidget(QLabel("Boş olan alan:"))
        satir.addWidget(self.eksik_alan)
        satir.addWidget(self.eksik_ozet, 1)
        kutu2.addLayout(satir)
        kutu2.addWidget(self.eksik_tablo)

        duzen = QHBoxLayout(self)
        duzen.addWidget(benzer, 1)
        duzen.addWidget(eksik, 1)

        self.alan.currentIndexChanged.connect(self.gruplari_yukle)
        self.agac.currentItemChanged.connect(self.secim_degisti)
        self.agac.itemChanged.connect(lambda *_: self.butonlari_ayarla())
        self.btn_birlestir.clicked.connect(self.birlestir)
        self.btn_yoksay.clicked.connect(self.yoksay)
        self.hedef.textChanged.connect(lambda *_: self.butonlari_ayarla())
        self.eksik_alan.currentIndexChanged.connect(self.eksikleri_yukle)
        self.eksik_tablo.cellDoubleClicked.connect(self.eksik_ac)

    def yenile(self):
        self.gruplari_yukle()
        self.eksikleri_yukle()

    # --- Benzer yazımlar

    def gruplari_yukle(self):
        self.agac.blockSignals(True)
        self.agac.clear()
        gruplar = benzer_gruplar(self.alan.currentData())
        for grup in gruplar:
            toplam = sum(n for _, n in grup["degerler"])
            ust = QTreeWidgetItem([f"{'Kesin' if grup['kesin'] else 'Olası'}: {grup['degerler'][0][0]}", str(toplam)])
            ust.setToolTip(0, "Sadece büyük/küçük harf veya noktalama farkı" if grup["kesin"]
                           else "Harf farkı var; gerçekten aynı değer mi kontrol edin")
            ust.setForeground(0, Qt.darkGreen if grup["kesin"] else Qt.darkYellow)
            for deger, sayi in grup["degerler"]:
                cocuk = QTreeWidgetItem([deger, str(sayi)])
                cocuk.setFlags(cocuk.flags() | Qt.ItemIsUserCheckable)
                cocuk.setCheckState(0, Qt.Checked)
                ust.addChild(cocuk)
            self.agac.addTopLevelItem(ust)
            ust.setExpanded(True)
        self.agac.blockSignals(False)
        kesin = sum(1 for g in gruplar if g["kesin"])
        self.ozet.setText(f"{len(gruplar)} öneri ({kesin} kesin, {len(gruplar) - kesin} olası)" if gruplar
                          else "Benzer yazım bulunamadı")
        if gruplar:
            self.agac.setCurrentItem(self.agac.topLevelItem(0))
        else:
            self.hedef.clear()
        self.butonlari_ayarla()

    def secili_grup(self):
        oge = self.agac.currentItem()
        if oge is None:
            return None
        return oge.parent() or oge

    def isaretliler(self, grup):
        return [grup.child(i).text(0) for i in range(grup.childCount()) if grup.child(i).checkState(0) == Qt.Checked]

    def secim_degisti(self, oge, _onceki=None):
        # Grup seçilince en çok kullanılan yazım, yazım seçilince o yazım doğru yazım olarak önerilir
        if oge is not None:
            self.hedef.setText(oge.text(0) if oge.parent() else oge.child(0).text(0))
        self.butonlari_ayarla()

    def butonlari_ayarla(self):
        grup = self.secili_grup()
        self.btn_yoksay.setEnabled(grup is not None)
        self.btn_birlestir.setEnabled(grup is not None and bool(self.hedef.text().strip())
                                      and len(set(self.isaretliler(grup)) - {self.hedef.text().strip()}) > 0)

    def birlestir(self):
        grup = self.secili_grup()
        if grup is None:
            return
        yeni = " ".join(self.hedef.text().split())
        eskiler = [d for d in self.isaretliler(grup) if d != yeni]
        if not yeni or not eskiler:
            return
        sayilar = {grup.child(i).text(0): int(grup.child(i).text(1)) for i in range(grup.childCount())}
        kitap = sum(sayilar[d] for d in eskiler)
        liste = "\n".join(f"  • {d}  ({sayilar[d]} kitap)" for d in eskiler)
        if onay(f"Şu yazımlar '{yeni}' olarak değiştirilecek:\n{liste}\n\nToplam {kitap} kitap. "
                "Değişiklikten önce yedek alınır. Devam edilsin mi?") != QMessageBox.Yes:
            return
        if self.yedek_alindi is None:   # oturumdaki ilk birleştirmeden önce bir kez
            self.yedek_alindi = yedek_al(os.path.join(
                yedek_klasoru(), f"duzeltme_oncesi_{datetime.datetime.now():%Y%m%d_%H%M%S}.db"))
        degisen = birlestir(self.alan.currentData(), eskiler, yeni)
        self.gruplari_yukle()
        self.eksikleri_yukle()
        if self.degisti:
            self.degisti()
        QMessageBox.information(self, "Bilgi", f"{degisen} kitap güncellendi.\n\nDeğişiklik öncesi yedek:\n{self.yedek_alindi}")

    def yoksay(self):
        grup = self.secili_grup()
        if grup is None:
            return
        yoksay(self.alan.currentData(), [grup.child(i).text(0) for i in range(grup.childCount())])
        self.gruplari_yukle()

    # --- Eksik bilgiler

    def eksikleri_yukle(self):
        kitaplar = eksik_kitaplar(self.eksik_alan.currentData())
        tabloya_yaz(self.eksik_tablo, [[d or "" for d in k] for k in kitaplar])
        self.eksik_ozet.setText(f"{len(kitaplar)} kitap")

    def eksik_ac(self, satir, _kolon=None):
        hucre = self.eksik_tablo.item(satir, 0)
        if hucre and hucre.text().isdigit() and self.kitap_duzenle:
            self.kitap_duzenle(int(hucre.text()))
