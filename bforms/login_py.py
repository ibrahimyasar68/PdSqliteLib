# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login.ui'
##
## Created by: Qt User Interface Compiler version 6.10.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QStatusBar, QWidget)
import bforms.media_rc  # noqa: F401  (Qt kaynakları)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(850, 680)
        MainWindow.setMinimumSize(QSize(850, 680))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(9, 9, 830, 660))
        self.label_5 = QLabel(self.widget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(50, 80, 291, 121))
        self.pushButton_giris = QPushButton(self.widget)
        self.pushButton_giris.setObjectName(u"pushButton_giris")
        self.pushButton_giris.setGeometry(QRect(560, 360, 121, 81))
        self.pushButton_giris.setMinimumSize(QSize(90, 60))
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(9, 9, 410, 640))
        self.label.setStyleSheet(u"border-image:url(:/pic/login.jpeg);\n"
"\n"
"\n"
"border-top-left-radius:20px;\n"
"border-bottom-left-radius:20px;")
        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(410, 9, 410, 640))
        self.pushButton_cikis = QPushButton(self.widget)
        self.pushButton_cikis.setObjectName(u"pushButton_cikis")
        self.pushButton_cikis.setGeometry(QRect(750, 560, 61, 61))
        self.pushButton_cikis.setMaximumSize(QSize(100, 80))
        self.lineEdit_kullanci_adi = QLineEdit(self.widget)
        self.lineEdit_kullanci_adi.setObjectName(u"lineEdit_kullanci_adi")
        self.lineEdit_kullanci_adi.setEnabled(True)
        self.lineEdit_kullanci_adi.setGeometry(QRect(140, 9, 220, 41))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_kullanci_adi.sizePolicy().hasHeightForWidth())
        self.lineEdit_kullanci_adi.setSizePolicy(sizePolicy)
        self.lineEdit_kullanci_adi.setAlignment(Qt.AlignCenter)
        self.lineEdit_parola = QLineEdit(self.widget)
        self.lineEdit_parola.setObjectName(u"lineEdit_parola")
        self.lineEdit_parola.setGeometry(QRect(140, 60, 220, 41))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEdit_parola.sizePolicy().hasHeightForWidth())
        self.lineEdit_parola.setSizePolicy(sizePolicy1)
        self.lineEdit_parola.setEchoMode(QLineEdit.Password)
        self.lineEdit_parola.setAlignment(Qt.AlignCenter)
        self.label.raise_()
        self.label_2.raise_()
        self.pushButton_giris.raise_()
        self.label_5.raise_()
        self.pushButton_cikis.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Ya\u015far K\u00fct\u00fcphanesi", None))
        self.pushButton_giris.setText(QCoreApplication.translate("MainWindow", u"Giri\u015f", None))
        self.label.setText("")
        self.label_2.setText("")
        self.pushButton_cikis.setText("")
#if QT_CONFIG(tooltip)
        self.lineEdit_kullanci_adi.setToolTip(QCoreApplication.translate("MainWindow", u"Kullan\u0131c\u0131 Ad\u0131n\u0131 Girin", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.lineEdit_parola.setToolTip(QCoreApplication.translate("MainWindow", u"Parolay\u0131 Girin", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

