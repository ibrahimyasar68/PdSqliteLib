import sys
from PyQt5 import QtWidgets
from acodes.login import Login
from database.yedek import otomatik_yedek

## Programın sürekli çalıştırılması  ##
def app():
    app = QtWidgets.QApplication(sys.argv)
    try:
        otomatik_yedek()  # Günde bir kez, son 10 yedek saklanır
    except Exception as hata:
        print(f"Otomatik yedek alınamadı: {hata}")
    win = Login()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app()