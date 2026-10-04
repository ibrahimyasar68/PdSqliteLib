## Yazdıkça süzülen açılır listeler ##
# Uzun listelerde (737 kitap, yüzlerce yazar) kaydırmak yerine yazarak seçim yapılır.
# Büyük/küçük harf ve Türkçe karakter farkı gözetilmez: "iklim" -> "İklimler", "sabahattin" -> "Sabahattin ALİ".

from PyQt5.QtCore import QModelIndex, QSortFilterProxyModel
from PyQt5.QtWidgets import QComboBox, QCompleter

from database.metin import katla


class TurkceSuzgec(QSortFilterProxyModel):
    """Yazılan kelimelerin hepsini içeren seçenekleri gösterir."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.kelimeler = []

    def ayarla(self, metin):
        self.kelimeler = katla(metin).split()
        self.invalidateFilter()

    def filterAcceptsRow(self, satir, ust):
        if not self.kelimeler:
            return True
        metin = katla(self.sourceModel().index(satir, 0, ust).data() or "")
        return all(k in metin for k in self.kelimeler)


def aranabilir_yap(cmb, ipucu="Yazarak arayın..."):
    cmb.setEditable(True)
    cmb.setInsertPolicy(QComboBox.NoInsert)       # yazılan metin listeye yeni seçenek olarak eklenmez
    suzgec = TurkceSuzgec(cmb)
    suzgec.setSourceModel(cmb.model())
    tamamlayici = QCompleter(suzgec, cmb)
    tamamlayici.setCompletionMode(QCompleter.UnfilteredPopupCompletion)   # süzmeyi TurkceSuzgec yapar
    tamamlayici.setMaxVisibleItems(15)
    cmb.setCompleter(tamamlayici)
    cmb.lineEdit().setPlaceholderText(ipucu)
    cmb.lineEdit().textEdited.connect(suzgec.ayarla)
    tamamlayici.activated[QModelIndex].connect(lambda i: cmb.setCurrentIndex(suzgec.mapToSource(i).row()))
    cmb.suzgec = suzgec
    return cmb


def secili_veri(cmb):
    """Seçili seçeneğin verisi (ör. kitap id). Kullanıcı listeden seçmeyip adı yazdıysa, yazılan metin
    tek bir seçenekle eşleşiyorsa o seçilir. Eşleşme yoksa veya birden fazlaysa None."""
    i = cmb.currentIndex()
    if i >= 0 and cmb.itemText(i) == cmb.currentText():
        return cmb.itemData(i)
    aranan = katla(cmb.currentText()).strip()
    if not aranan:
        return None
    eslesen = [j for j in range(cmb.count()) if katla(cmb.itemText(j)).strip() == aranan]
    if not eslesen:
        kelimeler = aranan.split()
        eslesen = [j for j in range(cmb.count()) if all(k in katla(cmb.itemText(j)) for k in kelimeler)]
    if len(eslesen) != 1:
        return None
    cmb.setCurrentIndex(eslesen[0])
    return cmb.itemData(eslesen[0])
