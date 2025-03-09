# from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from bforms.user_py import Ui_MainWindow
from database.dbframe import df_user_list
from database.dbbase import user_ekle


class User(QMainWindow):
    def __init__(self):
        super().__init__()
        self.QtUser = Ui_MainWindow()
        self.QtUser.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.QtUser.pushButton_cikis.clicked.connect(self.user_exit)
        self.QtUser.pushButton_kaydet.clicked.connect(self.save_user)

    def user_exit(self):
        self.close()

    def save_user(self):
        pass

# Uygulamanın sürekli çalışması
if __name__=="__main__":
    app=QApplication([])
    pencere = User()
    pencere.show()
    app.exec_()

# # Uygulamanın sürekli çalışması
# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = Ui_MainWindow()
#     ui.setupUi(MainWindow)
#     MainWindow.showMaximized()
#     sys.exit(app.exec_())    