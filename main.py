import sys
from PySide6 import QtWidgets
from acodes import hareket, tema, tercihler
from acodes.login import Login
from database.yedek import otomatik_yedek

## Programın sürekli çalıştırılması  ##
def app():
    app = QtWidgets.QApplication(sys.argv)
    tema.ayarla(tercihler.oku("gorunum/tema", "sistem"))   # Ayarlar > Görünüm
    tema.uygulamaya_uygula(app)
    hareket.AZALT = tercihler.mantiksal(hareket.TERCIH)        # Ayarlar > Görünüm > Hareketi azalt
    try:
        otomatik_yedek()  # Günde bir kez, son 10 yedek saklanır
    except Exception as hata:
        print(f"Otomatik yedek alınamadı: {hata}")
    win = Login()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    app()