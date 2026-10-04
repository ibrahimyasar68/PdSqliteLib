## Değişiklik olayları: servis katmanının bildirimleri Qt sinyali olarak ##
# Kitap, ödünç veya kullanıcı kaydı değişince ilgili sinyal yayınlanır; her ekran ilgilendiği sinyale kendisi
# bağlanıp yenilenir (paneli kimin neyi yenileyeceğini bilmek zorunda kalmaz). Panel kapanınca (oturum kapatma)
# Qt bağlantıları kendiliğinden kopar.
#
#   from acodes.olaylar import olaylar
#   olaylar.kitaplar.connect(self.yenile)

from PyQt5.QtCore import QObject, pyqtSignal

import servis


class Olaylar(QObject):
    kitaplar = pyqtSignal()       # kitap eklendi, değişti, silindi, yazımlar birleştirildi
    odunc = pyqtSignal()          # ödünç verildi, iade alındı, iade geri alındı
    kullanicilar = pyqtSignal()   # kullanıcı eklendi, değişti, silindi

    def yayinla(self, konu):
        getattr(self, konu).emit()

    def hepsini_yayinla(self):
        """Veritabanı topluca değişince (yedekten geri yükleme): bütün ekranlar yenilenir."""
        for konu in servis.KONULAR:
            self.yayinla(konu)


olaylar = Olaylar()
servis.dinle(olaylar.yayinla)
