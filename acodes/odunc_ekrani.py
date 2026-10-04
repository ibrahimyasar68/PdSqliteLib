## Kitap Verme > Ödünç ve İade: ödünç verme, iade alma ve dışarıdaki kitaplar tek ekranda ##
# Üstte tam genişlikte dışarıdaki kitaplar (gecikenler kırmızı), altta yan yana iki kart: "Ödünç ver" (kitap
# ve üye seçilince bilgileri kendiliğinden gelir) ve "İade al" (listeden seçilen ödünç). Eski üç ekranın yerine.

import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QHeaderView, QLabel,
                             QLineEdit, QMessageBox, QPushButton, QTableWidget, QVBoxLayout, QWidget)

from acodes.kisayollar import arama_kutusu_yap
from acodes.onay import onay
from acodes import hareket, tema
from acodes.aranabilir import aranabilir_yap, secili_veri
from acodes.tablo import satir_verisi, tablo_ayarla, tabloya_yaz
from acodes.yerlesim import baslik_satiri, etiketli
from database import kitaplar, kullanicilar
from database.metin import katla
from database.modeller import id_sayi
from database.odunc import (ODUNC_SURESI_GUN, disaridakiler, gecikme_gunu, iade_al, iade_geri_al, kalan_gun_yazi,
                            kopya_durumu, odunc_ver, tarih_yazi, teslim_tarihi, uye_durumu, uyede_mi)

SECINIZ = ' Seçiniz...'
LISTE_KOLONLARI = ["Kitap", "Yazarı", "Üye", "Telefon", "Veriliş", "Teslim", "Durum"]


def kitap_listesi(cmb):
    """Açılır listeyi kitap id'leriyle doldurur. Aynı adlı kitaplara yayınevi ve yıl eklenir."""
    secenekler = kitaplar.secim_listesi()
    adlar = [adi for _, adi, _, _ in secenekler]
    cmb.addItem(SECINIZ)
    for id, adi, yayinevi, yili in secenekler:
        cmb.addItem(f"{adi} ({yayinevi}, {yili})" if adlar.count(adi) > 1 else adi, id)


def uye_listesi(cmb):
    # Aynı isimde iki üye olabileceği için kullanıcı adı da yazılır, her satırda id saklanır
    cmb.addItem(SECINIZ)
    for id, adi, kullanici in kullanicilar.secim_listesi():
        cmb.addItem(f"{adi} ({kullanici})", id)


def hatirlatma_metni(kitap, uye, teslim, durum, kutuphane="Yaşar Kütüphanesi"):
    """Üyeye gönderilecek (telefon mesajı, e-posta) hazır hatırlatma metni.
    teslim: "29.09.2026", durum: "3 gün gecikti" / "Bugün teslim" / "5 gün kaldı"."""
    if durum.endswith("gecikti"):
        zaman = f"teslim tarihi {teslim} idi ({durum})"
        rica = "Uygun olduğunuzda iade etmenizi rica ederiz."
    elif durum == "Bugün teslim":
        zaman = f"teslim tarihi bugün ({teslim})"
        rica = "Bugün iade etmenizi rica ederiz."
    else:
        zaman = f"teslim tarihi {teslim} ({durum})"
        rica = "Teslim tarihini hatırlatmak istedik."
    return (f"Merhaba {uye}, {kutuphane}'nden ödünç aldığınız \"{kitap}\" kitabının {zaman}. {rica} "
            "İyi okumalar dileriz.")


def renkli(etiket, metin, renk=None):
    etiket.setText(metin)
    etiket.setStyleSheet(f"color: {renk};" if renk else "")


class OduncEkrani(QWidget):
    def __init__(self, mesaj=None, degisti=None, bildir=None, parent=None):
        """bildir(metin, eylem adı, işlev): eylem butonlu bildirim (iadeden sonra "Geri Al")."""
        super().__init__(parent)
        self.mesaj = mesaj or (lambda metin, tur=None: None)
        self.bildir = bildir or (lambda metin, *_: self.mesaj(metin))
        self.degisti = degisti

        # --- Sol: dışarıdaki kitaplar
        self.arama = arama_kutusu_yap(QLineEdit(objectName="odunc_arama"))
        self.arama.setPlaceholderText("Ara: kitap, yazar, üye...")
        self.arama.setClearButtonEnabled(True)
        self.arama.setMinimumHeight(38)
        self.arama.textChanged.connect(self.listele)
        self.btn_aktar = QPushButton("Dışa Aktar")
        self.btn_aktar.setToolTip("Dışarıdaki kitapları Excel veya CSV olarak kaydet")
        self.ozet = QLabel(objectName="odunc_ozet")
        self.tablo = QTableWidget(0, len(LISTE_KOLONLARI))
        self.tablo.setHorizontalHeaderLabels(LISTE_KOLONLARI)
        tablo_ayarla(self.tablo, bos_metin="Şu an dışarıda kitap yok.", bos_simge="takas",
                     bos_eylem=("Ödünç Ver", lambda: self.kitap.setFocus(Qt.OtherFocusReason)))
        self.tablo.setSelectionMode(QTableWidget.SingleSelection)
        self.tablo.setToolTip("İade almak için satırı seçin")
        baslik = self.tablo.horizontalHeader()
        baslik.setStretchLastSection(False)
        baslik.setMinimumSectionSize(50)
        # Liste tam genişlikte: kitap, yazar ve üye kalan yeri paylaşır, kısa kolonlar içeriğe göre
        for kolon in range(len(LISTE_KOLONLARI)):
            baslik.setSectionResizeMode(kolon, QHeaderView.Stretch if kolon in (0, 1, 2) else QHeaderView.ResizeToContents)
        self.tablo.itemSelectionChanged.connect(self.secim_degisti)
        ust = baslik_satiri(sayac=self.ozet, butonlar=[self.btn_aktar])

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
        izgara.setHorizontalSpacing(12)
        izgara.addLayout(etiketli("Kitap", self.kitap), 0, 0)          # etiketler alanların üstünde
        izgara.addLayout(etiketli("Üye", self.uye), 0, 1)
        izgara.addWidget(self.kitap_bilgi, 1, 0, Qt.AlignTop)
        izgara.addWidget(self.uye_bilgi, 1, 1, Qt.AlignTop)
        izgara.addWidget(self.ver_bilgi, 2, 0)
        izgara.addWidget(self.btn_ver, 2, 1, Qt.AlignRight)
        izgara.setColumnStretch(0, 1)
        izgara.setColumnStretch(1, 1)

        # --- Alt sağ: iade al (listeden seçilen ödünç)
        self.iade_bilgi = QLabel(wordWrap=True, objectName="iade_bilgi")
        self.iade_bilgi.setTextFormat(Qt.RichText)
        self.iade_bilgi.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.btn_iade = QPushButton("İade Al")
        self.btn_iade.clicked.connect(self.iade_al)
        self.btn_hatirlat = QPushButton("Hatırlatma Metni")
        self.btn_hatirlat.setProperty("rol", "ikincil")
        self.btn_hatirlat.setToolTip("Üyeye gönderilecek hatırlatma mesajını panoya kopyala")
        self.btn_hatirlat.clicked.connect(self.hatirlatma_kopyala)
        iade = QGroupBox("İade al")
        dikey = QVBoxLayout(iade)
        dikey.addWidget(self.iade_bilgi, 1)
        iade_butonlari = QHBoxLayout()
        iade_butonlari.addStretch()
        iade_butonlari.addWidget(self.btn_hatirlat)
        iade_butonlari.addWidget(self.btn_iade)
        dikey.addLayout(iade_butonlari)
        for b in (self.btn_ver, self.btn_iade, self.btn_hatirlat):
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
        duzen.addWidget(self.arama)
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
        for o in disaridakiler():
            toplam += 1
            gecikmis = gecikme_gunu(o.verilis) > 0
            geciken += gecikmis
            if not all(k in katla(f"{o.kitap} {o.yazar} {o.uye}") for k in kelimeler):
                continue
            if gecikmis:
                gecikenler.add(len(satirlar))
            satirlar.append([o.kitap, o.yazar, o.uye, o.telefon, tarih_yazi(o.verilis),
                             tarih_yazi(teslim_tarihi(o.verilis)), kalan_gun_yazi(o.verilis)])
            idler.append((o.uye_id, o.kitap_id))
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
            k = kitaplar.kitap_bul(kitap_id)
            kopya, disarida = kopya_durumu(kitap_id)
            tanim = " · ".join(str(x) for x in (k.yazari, k.yayinevi, k.yili) if x) if k else ""
            if k is None:
                engel = "Bu kitap silinmiş."
                renkli(self.kitap_bilgi, engel, tema.TEHLIKE)
            elif disarida >= kopya:
                engel = "Bu kitap başka bir üyede." if kopya == 1 else f"Bu kitabın {kopya} kopyasının hepsi üyelerde."
                renkli(self.kitap_bilgi, f"{tanim}\nMüsait kopya yok", tema.TEHLIKE)
            else:
                renkli(self.kitap_bilgi, f"{tanim}\nMüsait kopya: {kopya - disarida} / {kopya}", tema.BASARI)
        if uye_id is None:
            renkli(self.uye_bilgi, "")
        else:
            u = kullanicilar.kullanici_bul(uye_id)
            elinde, geciken = uye_durumu(uye_id)
            iletisim = " · ".join(x for x in (u.telefon, u.mail) if x) if u else ""
            if u is None and engel is None:
                engel = "Bu üye silinmiş."
            durum = f"Elinde {elinde} kitap var" if elinde else "Elinde kitap yok"
            if geciken:
                durum += f", {geciken} tanesinin teslim süresi geçmiş"
            renkli(self.uye_bilgi, f"{iletisim}\n{durum}" if iletisim else durum, tema.TEHLIKE if geciken else None)
            if engel is None and kitap_id is not None and uyede_mi(uye_id, kitap_id):
                engel = "Bu kitabın bir kopyası zaten bu üyede. Önce iade alın."
        hazir = kitap_id is not None and uye_id is not None and engel is None
        if engel:
            renkli(self.ver_bilgi, engel, tema.TEHLIKE)
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
            self.mesaj("Kitap ve üye seçiniz!", "uyari")
            return
        engel = self.ver_durumu()
        if engel:
            QMessageBox.information(self, "Uyarı!", engel)
            return
        if onay(f"'{self.kitap.currentText()}' kitabı {self.uye.currentText()} adlı üyeye verilsin mi?") != QMessageBox.Yes:
            return
        simdi = datetime.datetime.today()
        odunc_ver(uye_id, kitap_id, simdi)
        for cmb in (self.kitap, self.uye):
            cmb.setCurrentIndex(0)
        self._degisiklik_sonrasi()
        self._satiri_sec(uye_id, kitap_id)
        hareket.secili_satiri_parlat(self.tablo)              # yeni ödünç listede kısa süre parlar
        self.mesaj(f"İşlem kaydedildi. Teslim tarihi: {tarih_yazi(teslim_tarihi(simdi.date()))}", "basari")

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
        user_id, book_id = id_sayi(user_id), id_sayi(book_id)
        if not self._satiri_sec(user_id, book_id) and self.arama.text():
            self.arama.clear()
        if not self._satiri_sec(user_id, book_id):
            self.mesaj("Bu ödünç bulunamadı (iade alınmış olabilir).", "uyari")
            return False
        return True

    def kitap_sec(self, kitap_id):
        """Başka ekrandan "Ödünç ver" denince: kitap seçili gelir, sıra üye seçmeye gelir."""
        i = self.kitap.findData(kitap_id)
        if i < 0:
            self.yenile()
            i = self.kitap.findData(kitap_id)
        self.kitap.setCurrentIndex(max(0, i))
        self.uye.setFocus(Qt.OtherFocusReason)
        self.uye.lineEdit().selectAll()
        return i >= 0

    def uye_sec(self, uye_id):
        """Hızlı aramadan bir üye seçilince: üye seçili gelir, sıra kitap seçmeye gelir."""
        i = self.uye.findData(uye_id)
        self.uye.setCurrentIndex(max(0, i))
        self.kitap.setFocus(Qt.OtherFocusReason)
        self.kitap.lineEdit().selectAll()
        return i >= 0

    def secim_degisti(self):
        secili = self.secili_odunc()
        self.btn_iade.setEnabled(secili is not None)
        self.btn_hatirlat.setEnabled(secili is not None)
        if secili is None:
            renkli(self.iade_bilgi, "İade almak için üstteki listeden bir kitap seçin.", tema.IKINCIL_METIN)
            return
        r = self.tablo.selectionModel().selectedRows()[0].row()
        hucre = lambda c: self.tablo.item(r, c).text()
        renk = tema.TEHLIKE if hucre(6).endswith("gecikti") else tema.BASARI
        durum = f"<span style='color:{renk}'><b>{hucre(6)}</b></span>"
        renkli(self.iade_bilgi,
               f"<b>{hucre(0)}</b> · {hucre(1)}<br>Üye: <b>{hucre(2)}</b> {hucre(3)}<br>"
               f"Veriliş: {hucre(4)} · Teslim: {hucre(5)}<br>{durum}")

    def iade_al(self):
        # Onay sorulmaz: yanlışlıkla alınan iade bildirimdeki "Geri Al" ile kısa süre içinde geri alınabilir
        secili = self.secili_odunc()
        if secili is None:
            self.mesaj("İade için listeden seçim yapınız!", "uyari")
            return
        r = self.tablo.selectionModel().selectedRows()[0].row()
        kitap, durum = self.tablo.item(r, 0).text(), self.tablo.item(r, 6).text()
        user_id, book_id = secili
        kayit_no = iade_al(user_id, book_id)
        self.tablo.clearSelection()
        self._degisiklik_sonrasi()
        self.bildir(f"'{kitap}' iade alındı" + (f" ({durum})." if durum.endswith("gecikti") else "."),
                    "Geri Al", lambda: self.iadeyi_geri_al(kayit_no, user_id, book_id, kitap))

    def iadeyi_geri_al(self, kayit_no, user_id, book_id, kitap):
        """İade alınan ödünç yeniden dışarıda olur (bu arada kitap başka üyeye verildiyse geri alınamaz)."""
        kopya, disarida = kopya_durumu(book_id)
        if kayit_no is None or disarida >= kopya or uyede_mi(user_id, book_id):
            self.mesaj("İade geri alınamaz: kitap bu arada yeniden ödünç verilmiş!", "uyari")
            return
        iade_geri_al(kayit_no)
        self._degisiklik_sonrasi()
        self._satiri_sec(user_id, book_id)
        hareket.secili_satiri_parlat(self.tablo)
        self.mesaj(f"'{kitap}' iadesi geri alındı; kitap yeniden üyede görünüyor.", "basari")

    def hatirlatma_kopyala(self):
        if self.secili_odunc() is None:
            self.mesaj("Hatırlatma için listeden seçim yapınız!", "uyari")
            return
        r = self.tablo.selectionModel().selectedRows()[0].row()
        hucre = lambda c: self.tablo.item(r, c).text()
        QApplication.clipboard().setText(hatirlatma_metni(hucre(0), hucre(2), hucre(5), hucre(6)))
        self.mesaj(f"Hatırlatma metni panoya kopyalandı: {hucre(2)}", "basari")

    def _degisiklik_sonrasi(self):
        if self.degisti:
            self.degisti()      # panel tüm listeleri (bu ekran dahil) yeniler
        else:
            self.yenile()
