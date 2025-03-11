# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'user.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QStatusBar, QWidget)
import media_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 680)
        MainWindow.setMinimumSize(QSize(900, 680))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 9, 1000, 680))
        self.label.setMinimumSize(QSize(1000, 680))
        self.label.setStyleSheet(u"border-image: url(:/pic/colorful.jpg);")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(230, 20, 501, 71))
        font = QFont()
        font.setFamilies([u"Verdana"])
        font.setPointSize(23)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(u"color: rgb(255, 255, 0);")
        self.label_2.setAlignment(Qt.AlignCenter)
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(320, 530, 331, 91))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_kaydet = QPushButton(self.layoutWidget)
        self.pushButton_kaydet.setObjectName(u"pushButton_kaydet")
        self.pushButton_kaydet.setMinimumSize(QSize(90, 60))
        self.pushButton_kaydet.setMaximumSize(QSize(60, 60))
        font1 = QFont()
        font1.setFamilies([u"Verdana"])
        font1.setPointSize(14)
        font1.setBold(True)
        font1.setItalic(False)
        self.pushButton_kaydet.setFont(font1)
        self.pushButton_kaydet.setStyleSheet(u"QPushButton#pushButton_kaydet{\n"
"background-color: rgb(255, 181, 61);\n"
"border-radius:10px;}\n"
"QPushButton#pushButton_kaydet:hover{\n"
"background-color: qlineargradient(spread:pad, x1:1, y1:0.880682, x2:0.955, y2:0.0284091, stop:0.5 rgba(212, 75, 45, 255), stop:1 rgba(255, 255, 255, 255));\n"
"border-radius:10px;}\n"
"QPushButton#pushButton_kaydet:pressed{\n"
"background-color:qlineargradient(spread:repeat, x1:0, y1:1, x2:0, y2:0, stop:0.301136 rgba(135, 88, 255, 255), stop:1 rgba(255, 255, 255, 255));\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"")

        self.gridLayout.addWidget(self.pushButton_kaydet, 0, 0, 1, 1)

        self.pushButton_cikis = QPushButton(self.layoutWidget)
        self.pushButton_cikis.setObjectName(u"pushButton_cikis")
        self.pushButton_cikis.setMinimumSize(QSize(90, 60))
        self.pushButton_cikis.setMaximumSize(QSize(60, 60))
        self.pushButton_cikis.setFont(font1)
        self.pushButton_cikis.setStyleSheet(u"QPushButton#pushButton_cikis{\n"
"background-color: rgb(255, 181, 61);\n"
"border-radius:10px;}\n"
"QPushButton#pushButton_cikis:hover{\n"
"background-color:qlineargradient(spread:repeat, x1:0, y1:1, x2:0, y2:0, stop:0.301136 rgba(135, 88, 255, 255), stop:1 rgba(255, 255, 255, 255));\n"
"border-radius:10px;}\n"
"QPushButton#pushButton_cikis:pressed{\n"
"background-color: qlineargradient(spread:pad, x1:1, y1:0.880682, x2:0.955, y2:0.0284091, stop:0.5 rgba(212, 75, 45, 255), stop:1 rgba(255, 255, 255, 255));\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"")

        self.gridLayout.addWidget(self.pushButton_cikis, 0, 1, 1, 1)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(340, 100, 331, 371))
        self.groupBox.setStyleSheet(u"border-color: rgba(255,255,255,0);")
        self.lineEdit_kullanici_adi = QLineEdit(self.groupBox)
        self.lineEdit_kullanici_adi.setObjectName(u"lineEdit_kullanici_adi")
        self.lineEdit_kullanici_adi.setGeometry(QRect(10, 20, 300, 30))
        self.lineEdit_kullanici_adi.setMinimumSize(QSize(300, 30))
        self.lineEdit_kullanici_adi.setMaximumSize(QSize(200, 20))
        font2 = QFont()
        font2.setFamilies([u"Verdana"])
        font2.setPointSize(11)
        font2.setBold(False)
        font2.setItalic(False)
        self.lineEdit_kullanici_adi.setFont(font2)
        self.lineEdit_kullanici_adi.setStyleSheet(u"font: 11pt \"Verdana\";")
        self.lineEdit_kullanici_adi.setEchoMode(QLineEdit.Normal)
        self.lineEdit_sifre = QLineEdit(self.groupBox)
        self.lineEdit_sifre.setObjectName(u"lineEdit_sifre")
        self.lineEdit_sifre.setGeometry(QRect(10, 70, 300, 30))
        self.lineEdit_sifre.setMinimumSize(QSize(300, 30))
        self.lineEdit_sifre.setMaximumSize(QSize(200, 20))
        self.lineEdit_sifre.setFont(font2)
        self.lineEdit_sifre.setStyleSheet(u"font: 11pt \"Verdana\";")
        self.lineEdit_sifre.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.lineEdit_adi_soyadi = QLineEdit(self.groupBox)
        self.lineEdit_adi_soyadi.setObjectName(u"lineEdit_adi_soyadi")
        self.lineEdit_adi_soyadi.setGeometry(QRect(10, 130, 300, 30))
        self.lineEdit_adi_soyadi.setMinimumSize(QSize(300, 30))
        self.lineEdit_adi_soyadi.setMaximumSize(QSize(200, 20))
        self.lineEdit_adi_soyadi.setFont(font2)
        self.lineEdit_adi_soyadi.setStyleSheet(u"font: 11pt \"Verdana\";")
        self.lineEdit_telefon = QLineEdit(self.groupBox)
        self.lineEdit_telefon.setObjectName(u"lineEdit_telefon")
        self.lineEdit_telefon.setGeometry(QRect(10, 190, 300, 30))
        self.lineEdit_telefon.setMinimumSize(QSize(300, 30))
        self.lineEdit_telefon.setMaximumSize(QSize(200, 20))
        self.lineEdit_telefon.setFont(font2)
        self.lineEdit_telefon.setStyleSheet(u"font: 11pt \"Verdana\";")
        self.lineEdit_mail = QLineEdit(self.groupBox)
        self.lineEdit_mail.setObjectName(u"lineEdit_mail")
        self.lineEdit_mail.setGeometry(QRect(10, 250, 300, 30))
        self.lineEdit_mail.setMinimumSize(QSize(300, 30))
        self.lineEdit_mail.setMaximumSize(QSize(200, 20))
        self.lineEdit_mail.setFont(font2)
        self.lineEdit_mail.setStyleSheet(u"font: 11pt \"Verdana\";")
        self.comboBox_yetki = QComboBox(self.groupBox)
        self.comboBox_yetki.setObjectName(u"comboBox_yetki")
        self.comboBox_yetki.setGeometry(QRect(10, 310, 300, 30))
        self.comboBox_yetki.setMinimumSize(QSize(300, 30))
        self.comboBox_yetki.setMaximumSize(QSize(200, 20))
        self.comboBox_yetki.setFont(font2)
        self.comboBox_yetki.setStyleSheet(u"font: 11pt \"Verdana\";")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        font3 = QFont()
        font3.setFamilies([u"Monotype Corsiva"])
        font3.setPointSize(14)
        font3.setBold(True)
        font3.setItalic(True)
        self.statusbar.setFont(font3)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"K U L L A N I C I   G \u0130 R \u0130 \u015e \u0130", None))
        self.pushButton_kaydet.setText(QCoreApplication.translate("MainWindow", u"Kaydet", None))
        self.pushButton_cikis.setText(QCoreApplication.translate("MainWindow", u"\u00c7\u0131k\u0131\u015f", None))
        self.groupBox.setTitle("")
        self.lineEdit_kullanici_adi.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Kullan\u0131c\u0131 Ad\u0131", None))
        self.lineEdit_sifre.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u015eifre", None))
        self.lineEdit_adi_soyadi.setText("")
        self.lineEdit_adi_soyadi.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Ad\u0131 Soyad\u0131", None))
        self.lineEdit_telefon.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Telefon", None))
        self.lineEdit_mail.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Mail Adresi", None))
    # retranslateUi

