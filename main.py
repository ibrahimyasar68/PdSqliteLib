import sys
from PyQt5 import QtWidgets
from acodes.login import Login

## Programın sürekli çalıştırılması  ##
def app():
    app = QtWidgets.QApplication(sys.argv)
    win = Login()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app()