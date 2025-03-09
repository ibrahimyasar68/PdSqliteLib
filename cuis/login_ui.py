# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QLineEdit,
    QMainWindow, QPushButton, QSizePolicy, QStatusBar,
    QWidget)
import media_rc

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
        font = QFont()
        font.setFamilies([u"Monotype Corsiva"])
        font.setPointSize(28)
        font.setBold(False)
        font.setItalic(True)
        self.label_5.setFont(font)
        self.label_5.setStyleSheet(u"color: rgb(255, 255, 255);\n"
"font: italic 28pt \"Monotype Corsiva\";")
        self.formFrame = QFrame(self.widget)
        self.formFrame.setObjectName(u"formFrame")
        self.formFrame.setGeometry(QRect(440, 110, 371, 121))
        self.formFrame.setStyleSheet(u"#formFrame{background-color: qlineargradient(spread:pad, x1:0.943182, y1:0.966, x2:0.074, y2:0.074, stop:0 rgba(165, 111, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
"border-radius:10px;}")
        self.label_3 = QLabel(self.formFrame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(9, 10, 101, 51))
        font1 = QFont()
        font1.setFamilies([u"Monotype Corsiva"])
        font1.setPointSize(17)
        font1.setBold(True)
        self.label_3.setFont(font1)
        self.lineEdit_kullanci_adi = QLineEdit(self.formFrame)
        self.lineEdit_kullanci_adi.setObjectName(u"lineEdit_kullanci_adi")
        self.lineEdit_kullanci_adi.setEnabled(True)
        self.lineEdit_kullanci_adi.setGeometry(QRect(110, 9, 231, 41))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_kullanci_adi.sizePolicy().hasHeightForWidth())
        self.lineEdit_kullanci_adi.setSizePolicy(sizePolicy)
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        self.lineEdit_kullanci_adi.setFont(font2)
        self.lineEdit_kullanci_adi.setAlignment(Qt.AlignCenter)
        self.label_4 = QLabel(self.formFrame)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(9, 70, 91, 31))
        font3 = QFont()
        font3.setFamilies([u"Monotype Corsiva"])
        font3.setPointSize(20)
        font3.setBold(True)
        font3.setItalic(False)
        self.label_4.setFont(font3)
        self.label_4.setStyleSheet(u"selection-color: qlineargradient(spread:pad, x1:0.949438, y1:0.938, x2:0.073, y2:0.505682, stop:0 rgba(245, 81, 1, 255), stop:1 rgba(255, 255, 255, 255));")
        self.lineEdit_parola = QLineEdit(self.formFrame)
        self.lineEdit_parola.setObjectName(u"lineEdit_parola")
        self.lineEdit_parola.setGeometry(QRect(110, 60, 231, 41))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEdit_parola.sizePolicy().hasHeightForWidth())
        self.lineEdit_parola.setSizePolicy(sizePolicy1)
        self.lineEdit_parola.setFont(font2)
        self.lineEdit_parola.setEchoMode(QLineEdit.Password)
        self.lineEdit_parola.setAlignment(Qt.AlignCenter)
        self.pushButton_giris = QPushButton(self.widget)
        self.pushButton_giris.setObjectName(u"pushButton_giris")
        self.pushButton_giris.setGeometry(QRect(570, 410, 121, 81))
        self.pushButton_giris.setMinimumSize(QSize(90, 60))
        font4 = QFont()
        font4.setFamilies([u"Monotype Corsiva"])
        font4.setPointSize(24)
        font4.setBold(True)
        self.pushButton_giris.setFont(font4)
        self.pushButton_giris.setStyleSheet(u"QPushButton#pushButton_giris{\n"
"background-color: rgb(255, 181, 61);\n"
"border-radius:10px;}\n"
"QPushButton#pushButton_giris:hover{\n"
"background-color: qlineargradient(spread:pad, x1:1, y1:0.880682, x2:0.955, y2:0.0284091, stop:0.5 rgba(212, 75, 45, 255), stop:1 rgba(255, 255, 255, 255));\n"
"border-radius:10px;}\n"
"QPushButton#pushButton_giris:pressed{\n"
"background-color:qlineargradient(spread:repeat, x1:0, y1:1, x2:0, y2:0, stop:0.301136 rgba(135, 88, 255, 255), stop:1 rgba(255, 255, 255, 255));\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"")
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
        self.label_2.setStyleSheet(u"background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(0, 0, 0, 255), stop:0.05 rgba(14, 8, 73, 255), stop:0.36 rgba(28, 17, 145, 255), stop:0.6 rgba(126, 14, 81, 255), stop:0.75 rgba(234, 11, 11, 255), stop:0.79 rgba(244, 70, 5, 255), stop:0.86 rgba(255, 136, 0, 255), stop:0.935 rgba(239, 236, 55, 255));\n"
"border-top-right-radius:20px;\n"
"border-bottom-right-radius:20px\n"
"")
        self.label.raise_()
        self.label_2.raise_()
        self.formFrame.raise_()
        self.pushButton_giris.raise_()
        self.label_5.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        font5 = QFont()
        font5.setFamilies([u"Monotype Corsiva"])
        font5.setPointSize(12)
        font5.setItalic(True)
        self.statusbar.setFont(font5)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Ya\u015far K\u00fct\u00fcphanesi", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Kullan\u0131c\u0131\n"
"     Ad\u0131", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_kullanci_adi.setToolTip(QCoreApplication.translate("MainWindow", u"Kullan\u0131c\u0131 Ad\u0131n\u0131 Girin", None))
#endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Parola", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_parola.setToolTip(QCoreApplication.translate("MainWindow", u"Parolay\u0131 Girin", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_giris.setText(QCoreApplication.translate("MainWindow", u"G i r i \u015f", None))
        self.label.setText("")
        self.label_2.setText("")
    # retranslateUi

