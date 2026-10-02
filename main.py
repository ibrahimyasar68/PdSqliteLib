import sys
from PyQt5 import QtWidgets
from acodes import tema, tercihler
from acodes.login import Login
from database.yedek import otomatik_yedek

## Programın sürekli çalıştırılması  ##
def app():
    app = QtWidgets.QApplication(sys.argv)
    tema.ayarla(tercihler.oku("gorunum/tema", "sistem"))   # Ayarlar > Görünüm
    tema.uygulamaya_uygula(app)
    try:
        otomatik_yedek()  # Günde bir kez, son 10 yedek saklanır
    except Exception as hata:
        print(f"Otomatik yedek alınamadı: {hata}")
    win = Login()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app()