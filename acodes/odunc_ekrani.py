## Kitap Verme > Ödünç ve İade: ödünç verme, iade alma ve dışarıdaki kitaplar tek ekranda ##
# Üstte tam genişlikte dışarıdaki kitaplar (gecikenler kırmızı), altta yan yana iki kart: "Ödünç ver" (kitap
# ve üye seçilince bilgileri kendiliğinden gelir) ve "İade al" (listeden seçilen ödünç). Eski üç ekranın yerine.

import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QTableWidget, QVBoxLayout, QWidget)

from bforms.onay import onay
from acodes import tema
from acodes.aranabilir import aranabilir_yap, secili_veri
from acodes.tablo import satir_verisi, tablo_ayarla, tabloya_yaz
from database.dbbase import save_work_to_db, update_work_to_db
from database.dbframe import (df_book_find_by_id, df_book_id_list, df_user_find_by_id, df_user_id_list,
                              df_work_table_book, katla, kopya_durumu, uyede_mi)
from database.odunc import (ODUNC_SURESI_GUN, gecikme_gunu, kalan_gun_yazi, tarih_yazi, teslim_tarihi,
                            uye_durumu)

SECINIZ = ' Seçiniz...'
LISTE_KOLONLARI = ["Kitap", "Yazarı", "Üye", "Telefon", "Veriliş", "Teslim", "Durum"]
IYI, KOTU = "#15803D", tema.TEHLIKE


def kitap_listesi(cmb):
    """Açılır listeyi kitap id'leriyle doldurur. Aynı adlı kitaplara yayınevi ve yıl eklenir."""
    kitaplar = df_book_id_list()
    adlar = [adi for _, adi, _, _ in kitaplar]
    cmb.addItem(SECINIZ)
    for id, adi, yayinevi, yili in kitaplar:
        cmb.addItem(f"{adi} ({yayinevi}, {yili})" if adlar.count(adi) > 1 else adi, id)


def uye_listesi(cmb):
    # Aynı isimde iki üye olabileceği için kullanıcı adı da yazılır, her satırda id saklanır
    cmb.addItem(SECINIZ)
    for id, adi, kullanici in df_user_id_list():
        cmb.addItem(f"{adi} ({kullanici})", id)


def sayi(deger):
    # follow tablosunda id'ler metin olarak saklanır
    return int(deger) if str(deger).isdigit() else deger


def renkli(etiket, metin, renk=None):
    etiket.setText(metin)
    etiket.setStyleSheet(f"color: {renk};" if renk else "")


class OduncEkrani(QWidget):
    def __init__(self, mesaj=None, degisti=None, parent=None):
        super().__init__(parent)
        self.mesaj = mesaj or (lambda metin: None)
        self.degisti = degisti

        # --- Sol: dışarıdaki kitaplar
        self.arama = QLineEdit(objectName="odunc_arama")
        self.arama.setPlaceholderText("Ara: kitap, yazar, üye...")
        self.arama.setClearButtonEnabled(True)
        self.arama.setMinimumHeight(36)
        self.arama.textChanged.connect(self.listele)
        self.btn_aktar = QPushButton("Dışa Aktar")
        self.btn_aktar.setMinimumHeight(36)
        self.btn_aktar.setToolTip("Dışarıdaki kitapları Excel veya CSV olarak kaydet")
        self.ozet = QLabel(objectName="odunc_ozet")
        self.tablo = QTableWidget(0, len(LISTE_KOLONLARI))
        self.tablo.setHorizontalHeaderLabels(LISTE_KOLONLARI)
        tablo_ayarla(self.tablo, bos_metin="Şu an dışarıda kitap yok.")
        self.tablo.setSelectionMode(QTableWidget.SingleSelection)
        self.tablo.setToolTip("İade almak için satırı seçin")
        baslik = self.tablo.horizontalHeader()
        baslik.setStretchLastSection(False)
        baslik.setMinimumSectionSize(50)
        # Liste tam genişlikte: kitap, yazar ve üye kalan yeri paylaşır, kısa kolonlar içeriğe göre
        for kolon in range(len(LISTE_KOLONLARI)):
            baslik.setSectionResizeMode(kolon, QHeaderView.Stretch if kolon in (0, 1, 2) else QHeaderView.ResizeToContents)
        self.tablo.itemSelectionChanged.connect(self.secim_degisti)
        ust = QHBoxLayout()
        ust.addWidget(self.arama, 1)
        ust.addWidget(self.btn_aktar)

        # --- Alt sol: ödünç ver (kitap ve üye yan yana, bilgileri altlarında, buton sağda)
        self.kitap = QComboBox()
        self.uye = QComboBox()
        for cmb, ipucu in ((self.kitap, "Kitap adı yazarak arayın..."), (self.uye, "Üye adı yazarak arayın...")):
            cmb.setMinimumHeight(34)
            cmb.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
            cmb.setMinimumContentsLength(12)
            aranabilir_yap(cmb, ipucu)
            cmb.currentIndexChanged.connect(self.ver_durumu)
        self.kitap_bilgi = QLabel(wordWrap=True)
        self.uye_bilgi = QLabel(wordWrap=True)
        self.ver_bilgi = QLabel(wordWrap=True, objectName="ver_bilgi")
        self.btn_ver = QPushButton("Ödünç Ver")
        self.btn_ver.clicked.connect(self.odunc_ver)
        ver = QGroupBox("Ödünç ver")
        izgara = QGridLayout(ver)
        izgara.setHorizontalSpacing(10)
        izgara.setVerticalSpacing(6)
        izgara.addWidget(QLabel("Kitap:"), 0, 0)
        izgara.addWidget(self.kitap, 0, 1)
        izgara.addWidget(QLabel("Üye:"), 0, 2)
        izgara.addWidget(self.uye, 0, 3)
        izgara.addWidget(self.kitap_bilgi, 1, 1, Qt.AlignTop)
        izgara.addWidget(self.uye_bilgi, 1, 3, Qt.AlignTop)
        izgara.addWidget(self.ver_bilgi, 2, 0, 1, 3)
        izgara.addWidget(self.btn_ver, 2, 3, Qt.AlignRight)
        izgara.setColumnStretch(1, 1)
        izgara.setColumnStretch(3, 1)

        # --- Alt sağ: iade al (listeden seçilen ödünç)
        self.iade_bilgi = QLabel(wordWrap=True, objectName="iade_bilgi")
        self.iade_bilgi.setTextFormat(Qt.RichText)
        self.iade_bilgi.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.btn_iade = QPushButton("İade Al")
        self.btn_iade.clicked.connect(self.iade_al)
        iade = QGroupBox("İade al")
        dikey = QVBoxLayout(iade)
        dikey.addWidget(self.iade_bilgi, 1)
        dikey.addWidget(self.btn_iade, 0, Qt.AlignRight)
        for b in (self.btn_ver, self.btn_iade):
            b.setMinimumSize(140, 40)

        alt = QHBoxLayout()
        alt.setSpacing(16)
        alt.addWidget(ver, 3)
        alt.addWidget(iade, 2)

        # Liste üstte ve tam genişlikte (kalan yüksekliği alır), işlem kartları altta yan yana
        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(14, 12, 14, 12)
        duzen.setSpacing(10)
        duzen.addLayout(ust)
        duzen.addWidget(self.ozet)
        duzen.addWidget(self.tablo, 1)
        duzen.addLayout(alt)
        self.yenile()

    # --- Yenileme

    def yenile(self):
        ###  Açılır listeleri ve dışarıdaki kitapları veritabanından yeniden oku (seçimler korunur)  ###
        for cmb, doldur in ((self.kitap, kitap_listesi), (self.uye, uye_listesi)):
            secili = cmb.currentData()
            cmb.blockSignals(True)
            cmb.clear()
            doldur(cmb)
            cmb.setCurrentIndex(max(0, cmb.findData(secili)) if secili is not None else 0)
            cmb.blockSignals(False)
        self.ver_durumu()
        self.listele()

    def listele(self):
        secili = self.secili_odunc()
        kelimeler = katla(self.arama.text()).split()
        satirlar, idler, gecikenler = [], [], set()
        toplam = geciken = 0
        for kitap, yazar, _, kisi, telefon, _, verilis, user_id, book_id in df_work_table_book():
            toplam += 1
            gecikmis = gecikme_gunu(verilis) > 0
            geciken += gecikmis
            if not all(k in katla(f"{kitap} {yazar} {kisi}") for k in kelimeler):
                continue
            if gecikmis:
                gecikenler.add(len(satirlar))
            satirlar.append([kitap, yazar, kisi, telefon, tarih_yazi(verilis), tarih_yazi(teslim_tarihi(verilis)),
                             kalan_gun_yazi(verilis)])
            idler.append((sayi(user_id), sayi(book_id)))
        tabloya_yaz(self.tablo, satirlar, vurgulu=gecikenler, veri=idler)
        ozet = f"Dışarıda {toplam} kitap" + (f", {geciken} tanesinin teslim süresi geçmiş" if geciken else "")
        if kelimeler:
            ozet += f" · aramaya uyan {len(satirlar)}"
        self.ozet.setText(ozet)
        if secili:
            self._satiri_sec(*secili)
        self.secim_degisti()

    # --- Ödünç verme

    def ver_durumu(self):
        ###  Seçilen kitap ve üyenin bilgilerini göster; ödünç verilebiliyorsa butonu aç  ###
        kitap_id, uye_id = self.kitap.currentData(), self.uye.currentData()
        engel = None
        if kitap_id is None:
            renkli(self.kitap_bilgi, "")
        else:
            k = df_book_find_by_id(kitap_id)
            kopya, disarida = kopya_durumu(kitap_id)
            tanim = " · ".join(str(x) for x in (k[2], k[5], k[6]) if x)
            if disarida >= kopya:
                engel = "Bu kitap başka bir üyede." if kopya == 1 else f"Bu kitabın {kopya} kopyasının hepsi üyelerde."
                renkli(self.kitap_bilgi, f"{tanim}\nMüsait kopya yok", KOTU)
            else:
                renkli(self.kitap_bilgi, f"{tanim}\nMüsait kopya: {kopya - disarida} / {kopya}", IYI)
        if uye_id is None:
            renkli(self.uye_bilgi, "")
        else:
            u = df_user_find_by_id(uye_id)
            elinde, geciken = uye_durumu(uye_id)
            iletisim = " · ".join(x for x in (u[4], u[5]) if x)
            durum = f"Elinde {elinde} kitap var" if elinde else "Elinde kitap yok"
            if geciken:
                durum += f", {geciken} tanesinin teslim süresi geçmiş"
            renkli(self.uye_bilgi, f"{iletisim}\n{durum}" if iletisim else durum, KOTU if geciken else None)
            if engel is None and kitap_id is not None and uyede_mi(uye_id, kitap_id):
                engel = "Bu kitabın bir kopyası zaten bu üyede. Önce iade alın."
        hazir = kitap_id is not None and uye_id is not None and engel is None
        if engel:
            renkli(self.ver_bilgi, engel, KOTU)
        elif hazir:
            renkli(self.ver_bilgi, f"Teslim tarihi: {tarih_yazi(teslim_tarihi(datetime.date.today()))} "
                                   f"({ODUNC_SURESI_GUN} gün)")
        else:
            renkli(self.ver_bilgi, "Ödünç vermek için kitap ve üye seçin.", tema.IKINCIL_METIN)
        self.btn_ver.setEnabled(hazir)
        return engel

    def odunc_ver(self):
        # Listeden seçmeyip adı yazdıysa, yazılan metin tek seçenekle eşleşiyorsa o seçilir
        kitap_id, uye_id = secili_veri(self.kitap), secili_veri(self.uye)
        if kitap_id is None or uye_id is None:
            self.mesaj("Kitap ve üye seçiniz!")
            return
        engel = self.ver_durumu()
        if engel:
            QMessageBox.information(self, "Uyarı!", engel)
            return
        if onay(f"'{self.kitap.currentText()}' kitabı {self.uye.currentText()} adlı üyeye verilsin mi?") != QMessageBox.Yes:
            return
        simdi = datetime.datetime.today()
        save_work_to_db([str(uye_id), str(kitap_id), simdi.date(), simdi.strftime('%X '), "out", "", ""])
        for cmb in (self.kitap, self.uye):
            cmb.setCurrentIndex(0)
        self._degisiklik_sonrasi()
        self._satiri_sec(uye_id, kitap_id)
        self.mesaj(f"İşlem kaydedildi. Teslim tarihi: {tarih_yazi(teslim_tarihi(simdi.date()))}")

    # --- İade alma

    def secili_odunc(self):
        satirlar = self.tablo.selectionModel().selectedRows()
        return satir_verisi(self.tablo, satirlar[0].row()) if satirlar else None

    def _satiri_sec(self, user_id, book_id):
        for r in range(self.tablo.rowCount()):
            if satir_verisi(self.tablo, r) == (user_id, book_id):
                self.tablo.selectRow(r)
                self.tablo.scrollToItem(self.tablo.item(r, 0))
                return True
        return False

    def sec(self, user_id, book_id):
        """Ana sayfadan gelince: bu ödüncü listede seç (arama gizliyorsa temizlenir)."""
        user_id, book_id = sayi(user_id), sayi(book_id)
        if not self._satiri_sec(user_id, book_id) and self.arama.text():
            self.arama.clear()
        if not self._satiri_sec(user_id, book_id):
            self.mesaj("Bu ödünç bulunamadı (iade alınmış olabilir).")
            return False
        return True

    def secim_degisti(self):
        secili = self.secili_odunc()
        self.btn_iade.setEnabled(secili is not None)
        if secili is None:
            renkli(self.iade_bilgi, "İade almak için üstteki listeden bir kitap seçin.", tema.IKINCIL_METIN)
            return
        r = self.tablo.selectionModel().selectedRows()[0].row()
        hucre = lambda c: self.tablo.item(r, c).text()
        renk = KOTU if hucre(6).endswith("gecikti") else IYI
        durum = f"<span style='color:{renk}'><b>{hucre(6)}</b></span>"
        renkli(self.iade_bilgi,
               f"<b>{hucre(0)}</b> · {hucre(1)}<br>Üye: <b>{hucre(2)}</b> {hucre(3)}<br>"
               f"Veriliş: {hucre(4)} · Teslim: {hucre(5)}<br>{durum}")

    def iade_al(self):
        secili = self.secili_odunc()
        if secili is None:
            self.mesaj("İade için listeden seçim yapınız!")
            return
        r = self.tablo.selectionModel().selectedRows()[0].row()
        kitap, kisi, durum = self.tablo.item(r, 0).text(), self.tablo.item(r, 2).text(), self.tablo.item(r, 6).text()
        if onay(f"'{kitap}' kitabı {kisi} adlı üyeden iade alınsın mı?") != QMessageBox.Yes:
            return
        simdi = datetime.datetime.today()
        user_id, book_id = secili
        update_work_to_db([str(user_id), str(book_id), "", "", "in", simdi.date(), simdi.strftime('%X ')])
        self.tablo.clearSelection()
        self._degisiklik_sonrasi()
        self.mesaj(f"'{kitap}' iade alındı" + (f" ({durum})." if durum.endswith("gecikti") else "."))

    def _degisiklik_sonrasi(self):
        if self.degisti:
            self.degisti()      # panel tüm listeleri (bu ekran dahil) yeniler
        else:
            self.yenile()
