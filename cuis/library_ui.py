# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'library.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QGridLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)
import media_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1518, 744)
        MainWindow.setMinimumSize(QSize(1300, 720))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"#centralwidget{background-color: rgb(85, 255, 255);}")
        self.gridLayout_7 = QGridLayout(self.centralwidget)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        font = QFont()
        font.setFamilies([u"Monotype Corsiva"])
        font.setPointSize(14)
        font.setItalic(True)
        self.tabWidget.setFont(font)
        self.tabWidget.setStyleSheet(u"\n"
"#tab_1{background-color: rgb(0, 255, 0);}\n"
"#tab_1{border-image: url(:/pic/autumn.jpg);}\n"
"\n"
"\n"
"\n"
"#tab_2{background-color: rgb(85, 255, 0);}\n"
"\n"
"#tab_3{background-color: rgb(170, 255, 0);}\n"
"\n"
"#tab_3_1{background-color: rgb(150, 210, 0);}\n"
"#tab_3_2{background-color: rgb(150, 205, 0);}\n"
"#tab_3_3{background-color: rgb(150, 200, 0);}\n"
"\n"
"#tab_4{background-color: rgb(204, 255, 0);}\n"
"\n"
"#tab_4_1{background-color: rgb(204, 255, 20);}\n"
"#tab_4_2{background-color: rgb(204, 255, 80);}\n"
"#tab_4_3{background-color: rgb(204, 255, 150);}\n"
"#tab_4_4{background-color: rgb(204, 255, 220);}\n"
"\n"
"#tab_5{background-color: rgb(255, 255, 0);}\n"
"\n"
"#tab_5_1{background-color: rgb(255, 255, 150);}\n"
"#tab_5_2{background-color: rgb(255, 255,200);}\n"
"\n"
"#tab_6{background-color: rgb(255, 170, 255);}\n"
"\n"
"\n"
"#tab_6_1{background-color: rgb(255, 190, 255);}\n"
"#tab_6_2{background-color: rgb(255, 220,255);}\n"
"#tab_6_3{background-color: rgb(255, 240,255);}")
        self.tab_1 = QWidget()
        self.tab_1.setObjectName(u"tab_1")
        self.tab_1.setStyleSheet(u"color: rgb(0, 255, 0);")
        self.label = QLabel(self.tab_1)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(410, 200, 511, 151))
        font1 = QFont()
        font1.setFamilies([u"Monotype Corsiva"])
        font1.setPointSize(50)
        font1.setBold(False)
        font1.setItalic(True)
        self.label.setFont(font1)
        self.label.setStyleSheet(u"color: rgb(255, 255, 0);\n"
"font: italic 50pt \"Monotype Corsiva\";")
        self.verticalLayoutWidget = QWidget(self.tab_1)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(570, 440, 221, 151))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_1_yeni_kullanici = QPushButton(self.verticalLayoutWidget)
        self.pushButton_1_yeni_kullanici.setObjectName(u"pushButton_1_yeni_kullanici")
        self.pushButton_1_yeni_kullanici.setEnabled(True)
        self.pushButton_1_yeni_kullanici.setMinimumSize(QSize(200, 50))
        self.pushButton_1_yeni_kullanici.setMaximumSize(QSize(300, 50))
        font2 = QFont()
        font2.setFamilies([u"Monotype Corsiva"])
        font2.setPointSize(14)
        font2.setBold(True)
        font2.setItalic(True)
        self.pushButton_1_yeni_kullanici.setFont(font2)
        self.pushButton_1_yeni_kullanici.setStyleSheet(u"\n"
"QPushButton#pushButton_1_yeni_kullanici{	\n"
"color: rgb(171, 0, 0);\n"
"border-color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 255, 127);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_1_yeni_kullanici:hover{\n"
"color: rgb(0,171, 0 );\n"
"border-color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 255, 127);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_1_yeni_kullanici:pressed{\n"
"color: rgb(0,0,171);\n"
"border-color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 255, 127);\n"
"border-radius:10px;\n"
"padding-left:5px;\n"
"padding-top:6px;}\n"
"\n"
"\n"
"")

        self.verticalLayout.addWidget(self.pushButton_1_yeni_kullanici)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.pushButton_1_cikis = QPushButton(self.verticalLayoutWidget)
        self.pushButton_1_cikis.setObjectName(u"pushButton_1_cikis")
        self.pushButton_1_cikis.setEnabled(True)
        self.pushButton_1_cikis.setMinimumSize(QSize(200, 50))
        self.pushButton_1_cikis.setMaximumSize(QSize(300, 50))
        self.pushButton_1_cikis.setFont(font2)
        self.pushButton_1_cikis.setStyleSheet(u"\n"
"QPushButton#pushButton_1_cikis{	\n"
"color: rgb(171, 0, 0);\n"
"border-color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 255, 127);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_1_cikis:hover{\n"
"color: rgb(0,171, 0);\n"
"border-color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 255, 127);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_1_cikis:pressed{\n"
"color: rgb(0,0,171);\n"
"border-color: rgb(255, 255, 255);\n"
"background-color: rgb(255, 255, 127);\n"
"border-radius:10px;\n"
"padding-left:5px;\n"
"padding-top:6px;}\n"
"\n"
"")

        self.verticalLayout.addWidget(self.pushButton_1_cikis)

        self.label_32 = QLabel(self.tab_1)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setGeometry(QRect(30, 30, 91, 61))
        font3 = QFont()
        font3.setFamilies([u"Monotype Corsiva"])
        font3.setPointSize(20)
        font3.setBold(False)
        font3.setItalic(True)
        self.label_32.setFont(font3)
        self.label_32.setStyleSheet(u"\n"
"color: rgb(255, 85, 255);\n"
"font: italic 20pt \"Monotype Corsiva\";")
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tableWidget_2 = QTableWidget(self.tab_2)
        if (self.tableWidget_2.columnCount() < 8):
            self.tableWidget_2.setColumnCount(8)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        self.tableWidget_2.setObjectName(u"tableWidget_2")
        self.tableWidget_2.setGeometry(QRect(160, 10, 1160, 590))
        font4 = QFont()
        font4.setFamilies([u"Monotype Corsiva"])
        font4.setPointSize(14)
        font4.setBold(False)
        font4.setItalic(True)
        self.tableWidget_2.setFont(font4)
        self.tableWidget_2.setStyleSheet(u"font: italic 14pt \"Monotype Corsiva\";")
        self.tableWidget_2.setShowGrid(True)
        self.tableWidget_2.setColumnCount(8)
        self.pushButton_2_temizle = QPushButton(self.tab_2)
        self.pushButton_2_temizle.setObjectName(u"pushButton_2_temizle")
        self.pushButton_2_temizle.setGeometry(QRect(40, 350, 100, 60))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2_temizle.sizePolicy().hasHeightForWidth())
        self.pushButton_2_temizle.setSizePolicy(sizePolicy)
        self.pushButton_2_temizle.setMinimumSize(QSize(100, 60))
        font5 = QFont()
        font5.setFamilies([u"Monotype Corsiva"])
        font5.setPointSize(12)
        font5.setBold(True)
        self.pushButton_2_temizle.setFont(font5)
        self.pushButton_2_temizle.setStyleSheet(u"QPushButton#pushButton_2_temizle{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_2_temizle:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_2_temizle:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.pushButton_2_listele = QPushButton(self.tab_2)
        self.pushButton_2_listele.setObjectName(u"pushButton_2_listele")
        self.pushButton_2_listele.setGeometry(QRect(40, 220, 100, 60))
        sizePolicy.setHeightForWidth(self.pushButton_2_listele.sizePolicy().hasHeightForWidth())
        self.pushButton_2_listele.setSizePolicy(sizePolicy)
        self.pushButton_2_listele.setMinimumSize(QSize(100, 60))
        self.pushButton_2_listele.setFont(font5)
        self.pushButton_2_listele.setStyleSheet(u"QPushButton#pushButton_2_listele{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_2_listele:hover{\n"
"background-color: rgba(6, 211, 166,150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_2_listele:pressed{\n"
"\n"
"background-color: rgba(0, 248, 49, 150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.gridLayout_2 = QGridLayout(self.tab_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget_3 = QTabWidget(self.tab_3)
        self.tabWidget_3.setObjectName(u"tabWidget_3")
        self.tabWidget_3.setFont(font)
        self.tabWidget_3.setStyleSheet(u"\n"
"#tab_3_1{background-color: rgb(150, 255, 0);}\n"
"#tab_3_2{background-color: rgb(150, 170, 0);}\n"
"#tab_3_3{background-color: rgb(150, 85, 0);}")
        self.tabWidget_3.setTabPosition(QTabWidget.South)
        self.tab_3_1 = QWidget()
        self.tab_3_1.setObjectName(u"tab_3_1")
        self.tab_3_1.setToolTipDuration(-8)
        self.formLayoutWidget = QWidget(self.tab_3_1)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(70, 20, 511, 521))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout.setHorizontalSpacing(10)
        self.formLayout.setVerticalSpacing(31)
        self.formLayout.setContentsMargins(8, 0, 5, 0)
        self.label_2 = QLabel(self.formLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        font6 = QFont()
        font6.setFamilies([u"Monotype Corsiva"])
        font6.setPointSize(12)
        font6.setItalic(True)
        self.label_2.setFont(font6)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.lineEdit_3_1_adi = QLineEdit(self.formLayoutWidget)
        self.lineEdit_3_1_adi.setObjectName(u"lineEdit_3_1_adi")
        self.lineEdit_3_1_adi.setFont(font6)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.lineEdit_3_1_adi)

        self.label_3 = QLabel(self.formLayoutWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font6)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.lineEdit_3_1_yazari = QLineEdit(self.formLayoutWidget)
        self.lineEdit_3_1_yazari.setObjectName(u"lineEdit_3_1_yazari")
        self.lineEdit_3_1_yazari.setFont(font6)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lineEdit_3_1_yazari)

        self.label_4 = QLabel(self.formLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font6)

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_4)

        self.label_5 = QLabel(self.formLayoutWidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font6)

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_5)

        self.label_6 = QLabel(self.formLayoutWidget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font6)

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_6)

        self.label_7 = QLabel(self.formLayoutWidget)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font6)

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_7)

        self.label_8 = QLabel(self.formLayoutWidget)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font6)

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.label_8)

        self.lineEdit_3_1_ceviren = QLineEdit(self.formLayoutWidget)
        self.lineEdit_3_1_ceviren.setObjectName(u"lineEdit_3_1_ceviren")
        self.lineEdit_3_1_ceviren.setFont(font6)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.lineEdit_3_1_ceviren)

        self.lineEdit_3_1_turu = QLineEdit(self.formLayoutWidget)
        self.lineEdit_3_1_turu.setObjectName(u"lineEdit_3_1_turu")
        self.lineEdit_3_1_turu.setFont(font6)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.lineEdit_3_1_turu)

        self.lineEdit_3_1_yayinevi = QLineEdit(self.formLayoutWidget)
        self.lineEdit_3_1_yayinevi.setObjectName(u"lineEdit_3_1_yayinevi")
        self.lineEdit_3_1_yayinevi.setFont(font6)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.lineEdit_3_1_yayinevi)

        self.lineEdit_3_1_yili = QLineEdit(self.formLayoutWidget)
        self.lineEdit_3_1_yili.setObjectName(u"lineEdit_3_1_yili")
        self.lineEdit_3_1_yili.setFont(font6)

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.lineEdit_3_1_yili)

        self.lineEdit_3_1_sayfa = QLineEdit(self.formLayoutWidget)
        self.lineEdit_3_1_sayfa.setObjectName(u"lineEdit_3_1_sayfa")
        self.lineEdit_3_1_sayfa.setFont(font6)

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.lineEdit_3_1_sayfa)

        self.pushButton_3_1_kaydet = QPushButton(self.tab_3_1)
        self.pushButton_3_1_kaydet.setObjectName(u"pushButton_3_1_kaydet")
        self.pushButton_3_1_kaydet.setGeometry(QRect(690, 150, 100, 60))
        sizePolicy.setHeightForWidth(self.pushButton_3_1_kaydet.sizePolicy().hasHeightForWidth())
        self.pushButton_3_1_kaydet.setSizePolicy(sizePolicy)
        self.pushButton_3_1_kaydet.setMinimumSize(QSize(100, 60))
        self.pushButton_3_1_kaydet.setFont(font5)
        self.pushButton_3_1_kaydet.setStyleSheet(u"QPushButton#pushButton_3_1_kaydet{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_1_kaydet:hover{\n"
"background-color: rgba(6, 211, 166,150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_1_kaydet:pressed{\n"
"\n"
"background-color: rgba(0, 248, 49, 150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.pushButton_3_1_temizle = QPushButton(self.tab_3_1)
        self.pushButton_3_1_temizle.setObjectName(u"pushButton_3_1_temizle")
        self.pushButton_3_1_temizle.setGeometry(QRect(690, 370, 100, 60))
        sizePolicy.setHeightForWidth(self.pushButton_3_1_temizle.sizePolicy().hasHeightForWidth())
        self.pushButton_3_1_temizle.setSizePolicy(sizePolicy)
        self.pushButton_3_1_temizle.setMinimumSize(QSize(100, 60))
        self.pushButton_3_1_temizle.setFont(font5)
        self.pushButton_3_1_temizle.setStyleSheet(u"QPushButton#pushButton_3_1_temizle{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_1_temizle:hover{\n"
"background-color: rgba(6, 211, 166,150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_1_temizle:pressed{\n"
"\n"
"background-color: rgba(0, 248, 49, 150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.tabWidget_3.addTab(self.tab_3_1, "")
        self.tab_3_2 = QWidget()
        self.tab_3_2.setObjectName(u"tab_3_2")
        self.pushButton_3_2_bul = QPushButton(self.tab_3_2)
        self.pushButton_3_2_bul.setObjectName(u"pushButton_3_2_bul")
        self.pushButton_3_2_bul.setGeometry(QRect(240, 180, 111, 51))
        sizePolicy.setHeightForWidth(self.pushButton_3_2_bul.sizePolicy().hasHeightForWidth())
        self.pushButton_3_2_bul.setSizePolicy(sizePolicy)
        self.pushButton_3_2_bul.setMinimumSize(QSize(80, 50))
        font7 = QFont()
        font7.setFamilies([u"Monotype Corsiva"])
        font7.setPointSize(13)
        font7.setBold(False)
        font7.setItalic(True)
        self.pushButton_3_2_bul.setFont(font7)
        self.pushButton_3_2_bul.setStyleSheet(u"QPushButton#pushButton_3_2_bul{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_2_bul:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_2_bul:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.formLayoutWidget_2 = QWidget(self.tab_3_2)
        self.formLayoutWidget_2.setObjectName(u"formLayoutWidget_2")
        self.formLayoutWidget_2.setGeometry(QRect(510, 20, 371, 551))
        self.formLayout_2 = QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout_2.setHorizontalSpacing(10)
        self.formLayout_2.setVerticalSpacing(31)
        self.formLayout_2.setContentsMargins(8, 0, 5, 0)
        self.label_9 = QLabel(self.formLayoutWidget_2)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font6)

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_9)

        self.lineEdit_3_2_adi = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_3_2_adi.setObjectName(u"lineEdit_3_2_adi")
        self.lineEdit_3_2_adi.setFont(font)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.lineEdit_3_2_adi)

        self.label_10 = QLabel(self.formLayoutWidget_2)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setFont(font6)

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_10)

        self.lineEdit_3_2_yazari = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_3_2_yazari.setObjectName(u"lineEdit_3_2_yazari")
        self.lineEdit_3_2_yazari.setFont(font)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.lineEdit_3_2_yazari)

        self.label_11 = QLabel(self.formLayoutWidget_2)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setFont(font6)

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_11)

        self.lineEdit_3_2_ceviren = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_3_2_ceviren.setObjectName(u"lineEdit_3_2_ceviren")
        self.lineEdit_3_2_ceviren.setFont(font)

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.lineEdit_3_2_ceviren)

        self.label_12 = QLabel(self.formLayoutWidget_2)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setFont(font6)

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.label_12)

        self.lineEdit_3_2_turu = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_3_2_turu.setObjectName(u"lineEdit_3_2_turu")
        self.lineEdit_3_2_turu.setFont(font)

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.lineEdit_3_2_turu)

        self.label_13 = QLabel(self.formLayoutWidget_2)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFont(font6)

        self.formLayout_2.setWidget(5, QFormLayout.LabelRole, self.label_13)

        self.lineEdit_3_2_yayinevi = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_3_2_yayinevi.setObjectName(u"lineEdit_3_2_yayinevi")
        self.lineEdit_3_2_yayinevi.setFont(font)

        self.formLayout_2.setWidget(5, QFormLayout.FieldRole, self.lineEdit_3_2_yayinevi)

        self.label_14 = QLabel(self.formLayoutWidget_2)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setFont(font6)

        self.formLayout_2.setWidget(6, QFormLayout.LabelRole, self.label_14)

        self.lineEdit_3_2_yili = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_3_2_yili.setObjectName(u"lineEdit_3_2_yili")
        self.lineEdit_3_2_yili.setFont(font)

        self.formLayout_2.setWidget(6, QFormLayout.FieldRole, self.lineEdit_3_2_yili)

        self.label_15 = QLabel(self.formLayoutWidget_2)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setFont(font6)

        self.formLayout_2.setWidget(7, QFormLayout.LabelRole, self.label_15)

        self.lineEdit_3_2_sayfa = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_3_2_sayfa.setObjectName(u"lineEdit_3_2_sayfa")
        self.lineEdit_3_2_sayfa.setFont(font)

        self.formLayout_2.setWidget(7, QFormLayout.FieldRole, self.lineEdit_3_2_sayfa)

        self.lineEdit_3_2_id = QLineEdit(self.formLayoutWidget_2)
        self.lineEdit_3_2_id.setObjectName(u"lineEdit_3_2_id")
        self.lineEdit_3_2_id.setFont(font)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.lineEdit_3_2_id)

        self.label_30 = QLabel(self.formLayoutWidget_2)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setFont(font6)

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_30)

        self.formLayoutWidget_3 = QWidget(self.tab_3_2)
        self.formLayoutWidget_3.setObjectName(u"formLayoutWidget_3")
        self.formLayoutWidget_3.setGeometry(QRect(60, 80, 441, 51))
        self.formLayout_3 = QFormLayout(self.formLayoutWidget_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_16 = QLabel(self.formLayoutWidget_3)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setFont(font6)

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_16)

        self.comboBox_3_2_bul_adi = QComboBox(self.formLayoutWidget_3)
        self.comboBox_3_2_bul_adi.setObjectName(u"comboBox_3_2_bul_adi")
        self.comboBox_3_2_bul_adi.setFont(font)

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.comboBox_3_2_bul_adi)

        self.pushButton_3_2_deg_kaydet = QPushButton(self.tab_3_2)
        self.pushButton_3_2_deg_kaydet.setObjectName(u"pushButton_3_2_deg_kaydet")
        self.pushButton_3_2_deg_kaydet.setEnabled(False)
        self.pushButton_3_2_deg_kaydet.setGeometry(QRect(1000, 280, 80, 61))
        sizePolicy.setHeightForWidth(self.pushButton_3_2_deg_kaydet.sizePolicy().hasHeightForWidth())
        self.pushButton_3_2_deg_kaydet.setSizePolicy(sizePolicy)
        self.pushButton_3_2_deg_kaydet.setMinimumSize(QSize(80, 50))
        self.pushButton_3_2_deg_kaydet.setFont(font7)
        self.pushButton_3_2_deg_kaydet.setStyleSheet(u"QPushButton#pushButton_3_2_deg_kaydet{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_2_deg_kaydet:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_2_deg_kaydet:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.tabWidget_3.addTab(self.tab_3_2, "")
        self.tab_3_3 = QWidget()
        self.tab_3_3.setObjectName(u"tab_3_3")
        self.pushButton_3_3_bul = QPushButton(self.tab_3_3)
        self.pushButton_3_3_bul.setObjectName(u"pushButton_3_3_bul")
        self.pushButton_3_3_bul.setGeometry(QRect(240, 180, 111, 51))
        sizePolicy.setHeightForWidth(self.pushButton_3_3_bul.sizePolicy().hasHeightForWidth())
        self.pushButton_3_3_bul.setSizePolicy(sizePolicy)
        self.pushButton_3_3_bul.setMinimumSize(QSize(80, 50))
        self.pushButton_3_3_bul.setFont(font7)
        self.pushButton_3_3_bul.setStyleSheet(u"QPushButton#pushButton_3_3_bul{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_3_bul:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_3_bul:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.formLayoutWidget_4 = QWidget(self.tab_3_3)
        self.formLayoutWidget_4.setObjectName(u"formLayoutWidget_4")
        self.formLayoutWidget_4.setGeometry(QRect(510, 20, 371, 551))
        self.formLayout_4 = QFormLayout(self.formLayoutWidget_4)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.formLayout_4.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout_4.setHorizontalSpacing(10)
        self.formLayout_4.setVerticalSpacing(31)
        self.formLayout_4.setContentsMargins(8, 0, 5, 0)
        self.label_17 = QLabel(self.formLayoutWidget_4)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setFont(font6)

        self.formLayout_4.setWidget(1, QFormLayout.LabelRole, self.label_17)

        self.lineEdit_3_3_adi = QLineEdit(self.formLayoutWidget_4)
        self.lineEdit_3_3_adi.setObjectName(u"lineEdit_3_3_adi")
        self.lineEdit_3_3_adi.setFont(font)

        self.formLayout_4.setWidget(1, QFormLayout.FieldRole, self.lineEdit_3_3_adi)

        self.label_18 = QLabel(self.formLayoutWidget_4)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setFont(font6)

        self.formLayout_4.setWidget(2, QFormLayout.LabelRole, self.label_18)

        self.lineEdit_3_3_yazari = QLineEdit(self.formLayoutWidget_4)
        self.lineEdit_3_3_yazari.setObjectName(u"lineEdit_3_3_yazari")
        self.lineEdit_3_3_yazari.setFont(font)

        self.formLayout_4.setWidget(2, QFormLayout.FieldRole, self.lineEdit_3_3_yazari)

        self.label_19 = QLabel(self.formLayoutWidget_4)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setFont(font6)

        self.formLayout_4.setWidget(3, QFormLayout.LabelRole, self.label_19)

        self.lineEdit_3_3_ceviren = QLineEdit(self.formLayoutWidget_4)
        self.lineEdit_3_3_ceviren.setObjectName(u"lineEdit_3_3_ceviren")
        self.lineEdit_3_3_ceviren.setFont(font)

        self.formLayout_4.setWidget(3, QFormLayout.FieldRole, self.lineEdit_3_3_ceviren)

        self.label_20 = QLabel(self.formLayoutWidget_4)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setFont(font6)

        self.formLayout_4.setWidget(4, QFormLayout.LabelRole, self.label_20)

        self.lineEdit_3_3_turu = QLineEdit(self.formLayoutWidget_4)
        self.lineEdit_3_3_turu.setObjectName(u"lineEdit_3_3_turu")
        self.lineEdit_3_3_turu.setFont(font)

        self.formLayout_4.setWidget(4, QFormLayout.FieldRole, self.lineEdit_3_3_turu)

        self.label_21 = QLabel(self.formLayoutWidget_4)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setFont(font6)

        self.formLayout_4.setWidget(5, QFormLayout.LabelRole, self.label_21)

        self.lineEdit_3_3_yayinevi = QLineEdit(self.formLayoutWidget_4)
        self.lineEdit_3_3_yayinevi.setObjectName(u"lineEdit_3_3_yayinevi")
        self.lineEdit_3_3_yayinevi.setFont(font)

        self.formLayout_4.setWidget(5, QFormLayout.FieldRole, self.lineEdit_3_3_yayinevi)

        self.label_22 = QLabel(self.formLayoutWidget_4)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setFont(font6)

        self.formLayout_4.setWidget(6, QFormLayout.LabelRole, self.label_22)

        self.lineEdit_3_3_yili = QLineEdit(self.formLayoutWidget_4)
        self.lineEdit_3_3_yili.setObjectName(u"lineEdit_3_3_yili")
        self.lineEdit_3_3_yili.setFont(font)

        self.formLayout_4.setWidget(6, QFormLayout.FieldRole, self.lineEdit_3_3_yili)

        self.label_23 = QLabel(self.formLayoutWidget_4)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setFont(font6)

        self.formLayout_4.setWidget(7, QFormLayout.LabelRole, self.label_23)

        self.lineEdit_3_3_sayfa = QLineEdit(self.formLayoutWidget_4)
        self.lineEdit_3_3_sayfa.setObjectName(u"lineEdit_3_3_sayfa")
        self.lineEdit_3_3_sayfa.setFont(font)

        self.formLayout_4.setWidget(7, QFormLayout.FieldRole, self.lineEdit_3_3_sayfa)

        self.lineEdit_3_3_id = QLineEdit(self.formLayoutWidget_4)
        self.lineEdit_3_3_id.setObjectName(u"lineEdit_3_3_id")
        self.lineEdit_3_3_id.setFont(font)

        self.formLayout_4.setWidget(0, QFormLayout.FieldRole, self.lineEdit_3_3_id)

        self.label_31 = QLabel(self.formLayoutWidget_4)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setFont(font6)

        self.formLayout_4.setWidget(0, QFormLayout.LabelRole, self.label_31)

        self.label_31.raise_()
        self.label_17.raise_()
        self.lineEdit_3_3_adi.raise_()
        self.label_18.raise_()
        self.lineEdit_3_3_yazari.raise_()
        self.label_19.raise_()
        self.label_20.raise_()
        self.label_21.raise_()
        self.label_22.raise_()
        self.label_23.raise_()
        self.lineEdit_3_3_ceviren.raise_()
        self.lineEdit_3_3_turu.raise_()
        self.lineEdit_3_3_yayinevi.raise_()
        self.lineEdit_3_3_yili.raise_()
        self.lineEdit_3_3_sayfa.raise_()
        self.lineEdit_3_3_id.raise_()
        self.formLayoutWidget_5 = QWidget(self.tab_3_3)
        self.formLayoutWidget_5.setObjectName(u"formLayoutWidget_5")
        self.formLayoutWidget_5.setGeometry(QRect(60, 80, 441, 51))
        self.formLayout_5 = QFormLayout(self.formLayoutWidget_5)
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.formLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_24 = QLabel(self.formLayoutWidget_5)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setFont(font6)

        self.formLayout_5.setWidget(0, QFormLayout.LabelRole, self.label_24)

        self.comboBox_3_3_bul_adi = QComboBox(self.formLayoutWidget_5)
        self.comboBox_3_3_bul_adi.setObjectName(u"comboBox_3_3_bul_adi")
        self.comboBox_3_3_bul_adi.setFont(font)

        self.formLayout_5.setWidget(0, QFormLayout.FieldRole, self.comboBox_3_3_bul_adi)

        self.pushButton_3_3_Sil = QPushButton(self.tab_3_3)
        self.pushButton_3_3_Sil.setObjectName(u"pushButton_3_3_Sil")
        self.pushButton_3_3_Sil.setEnabled(False)
        self.pushButton_3_3_Sil.setGeometry(QRect(1000, 280, 80, 61))
        sizePolicy.setHeightForWidth(self.pushButton_3_3_Sil.sizePolicy().hasHeightForWidth())
        self.pushButton_3_3_Sil.setSizePolicy(sizePolicy)
        self.pushButton_3_3_Sil.setMinimumSize(QSize(80, 50))
        self.pushButton_3_3_Sil.setFont(font7)
        self.pushButton_3_3_Sil.setStyleSheet(u"QPushButton#pushButton_3_3_Sil{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_3_Sil:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_3_Sil:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.tabWidget_3.addTab(self.tab_3_3, "")

        self.gridLayout_2.addWidget(self.tabWidget_3, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.gridLayout_3 = QGridLayout(self.tab_4)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.tabWidget_4 = QTabWidget(self.tab_4)
        self.tabWidget_4.setObjectName(u"tabWidget_4")
        self.tabWidget_4.setFont(font)
        self.tabWidget_4.setTabPosition(QTabWidget.South)
        self.tab_4_1 = QWidget()
        self.tab_4_1.setObjectName(u"tab_4_1")
        self.label_26 = QLabel(self.tab_4_1)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setGeometry(QRect(46, 160, 181, 40))
        self.label_26.setFont(font6)
        self.label_26.setAlignment(Qt.AlignCenter)
        self.tableWidget_4_1_1 = QTableWidget(self.tab_4_1)
        if (self.tableWidget_4_1_1.columnCount() < 1):
            self.tableWidget_4_1_1.setColumnCount(1)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget_4_1_1.setHorizontalHeaderItem(0, __qtablewidgetitem8)
        self.tableWidget_4_1_1.setObjectName(u"tableWidget_4_1_1")
        self.tableWidget_4_1_1.setGeometry(QRect(40, 200, 200, 176))
        self.tableWidget_4_1_1.setMinimumSize(QSize(100, 100))
        self.tableWidget_4_1_1.setMaximumSize(QSize(200, 300))
        font8 = QFont()
        font8.setFamilies([u"Monotype Corsiva"])
        font8.setPointSize(12)
        font8.setBold(False)
        font8.setItalic(True)
        self.tableWidget_4_1_1.setFont(font8)
        self.tableWidget_4_1_1.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";\n"
"")
        self.tableWidget_4_1_2 = QTableWidget(self.tab_4_1)
        if (self.tableWidget_4_1_2.columnCount() < 8):
            self.tableWidget_4_1_2.setColumnCount(8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget_4_1_2.setHorizontalHeaderItem(0, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget_4_1_2.setHorizontalHeaderItem(1, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget_4_1_2.setHorizontalHeaderItem(2, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget_4_1_2.setHorizontalHeaderItem(3, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget_4_1_2.setHorizontalHeaderItem(4, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableWidget_4_1_2.setHorizontalHeaderItem(5, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableWidget_4_1_2.setHorizontalHeaderItem(6, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tableWidget_4_1_2.setHorizontalHeaderItem(7, __qtablewidgetitem16)
        self.tableWidget_4_1_2.setObjectName(u"tableWidget_4_1_2")
        self.tableWidget_4_1_2.setGeometry(QRect(294, 10, 990, 545))
        self.tableWidget_4_1_2.setFont(font8)
        self.tableWidget_4_1_2.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";")
        self.tableWidget_4_1_2.setShowGrid(True)
        self.tableWidget_4_1_2.setColumnCount(8)
        self.pushButton_4_1_listele = QPushButton(self.tab_4_1)
        self.pushButton_4_1_listele.setObjectName(u"pushButton_4_1_listele")
        self.pushButton_4_1_listele.setGeometry(QRect(80, 430, 111, 51))
        sizePolicy.setHeightForWidth(self.pushButton_4_1_listele.sizePolicy().hasHeightForWidth())
        self.pushButton_4_1_listele.setSizePolicy(sizePolicy)
        self.pushButton_4_1_listele.setMinimumSize(QSize(80, 50))
        self.pushButton_4_1_listele.setFont(font7)
        self.pushButton_4_1_listele.setStyleSheet(u"QPushButton#pushButton_4_1_listele{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_1_listele:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_1_listele:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.formLayoutWidget_6 = QWidget(self.tab_4_1)
        self.formLayoutWidget_6.setObjectName(u"formLayoutWidget_6")
        self.formLayoutWidget_6.setGeometry(QRect(10, 80, 281, 51))
        self.formLayout_6 = QFormLayout(self.formLayoutWidget_6)
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.formLayout_6.setContentsMargins(0, 0, 0, 0)
        self.comboBox_4_1_turu = QComboBox(self.formLayoutWidget_6)
        self.comboBox_4_1_turu.setObjectName(u"comboBox_4_1_turu")
        font9 = QFont()
        font9.setFamilies([u"Monotype Corsiva"])
        font9.setPointSize(13)
        font9.setItalic(True)
        self.comboBox_4_1_turu.setFont(font9)

        self.formLayout_6.setWidget(0, QFormLayout.FieldRole, self.comboBox_4_1_turu)

        self.pushButton_4_1_temizle = QPushButton(self.tab_4_1)
        self.pushButton_4_1_temizle.setObjectName(u"pushButton_4_1_temizle")
        self.pushButton_4_1_temizle.setEnabled(False)
        self.pushButton_4_1_temizle.setGeometry(QRect(80, 500, 111, 51))
        sizePolicy.setHeightForWidth(self.pushButton_4_1_temizle.sizePolicy().hasHeightForWidth())
        self.pushButton_4_1_temizle.setSizePolicy(sizePolicy)
        self.pushButton_4_1_temizle.setMinimumSize(QSize(80, 50))
        self.pushButton_4_1_temizle.setFont(font7)
        self.pushButton_4_1_temizle.setStyleSheet(u"QPushButton#pushButton_4_1_temizle{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_1_temizle:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_1_temizle:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.tabWidget_4.addTab(self.tab_4_1, "")
        self.tab_4_2 = QWidget()
        self.tab_4_2.setObjectName(u"tab_4_2")
        self.label_27 = QLabel(self.tab_4_2)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(46, 160, 181, 40))
        self.label_27.setFont(font6)
        self.label_27.setAlignment(Qt.AlignCenter)
        self.tableWidget_4_2_1 = QTableWidget(self.tab_4_2)
        if (self.tableWidget_4_2_1.columnCount() < 1):
            self.tableWidget_4_2_1.setColumnCount(1)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tableWidget_4_2_1.setHorizontalHeaderItem(0, __qtablewidgetitem17)
        self.tableWidget_4_2_1.setObjectName(u"tableWidget_4_2_1")
        self.tableWidget_4_2_1.setGeometry(QRect(40, 200, 200, 176))
        self.tableWidget_4_2_1.setMinimumSize(QSize(100, 100))
        self.tableWidget_4_2_1.setMaximumSize(QSize(200, 300))
        self.tableWidget_4_2_1.setFont(font8)
        self.tableWidget_4_2_1.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";\n"
"")
        self.tableWidget_4_2_2 = QTableWidget(self.tab_4_2)
        if (self.tableWidget_4_2_2.columnCount() < 8):
            self.tableWidget_4_2_2.setColumnCount(8)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tableWidget_4_2_2.setHorizontalHeaderItem(0, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.tableWidget_4_2_2.setHorizontalHeaderItem(1, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.tableWidget_4_2_2.setHorizontalHeaderItem(2, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.tableWidget_4_2_2.setHorizontalHeaderItem(3, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.tableWidget_4_2_2.setHorizontalHeaderItem(4, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.tableWidget_4_2_2.setHorizontalHeaderItem(5, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        self.tableWidget_4_2_2.setHorizontalHeaderItem(6, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        self.tableWidget_4_2_2.setHorizontalHeaderItem(7, __qtablewidgetitem25)
        self.tableWidget_4_2_2.setObjectName(u"tableWidget_4_2_2")
        self.tableWidget_4_2_2.setGeometry(QRect(294, 10, 990, 545))
        self.tableWidget_4_2_2.setFont(font8)
        self.tableWidget_4_2_2.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";")
        self.tableWidget_4_2_2.setShowGrid(True)
        self.tableWidget_4_2_2.setColumnCount(8)
        self.pushButton_4_2_listele = QPushButton(self.tab_4_2)
        self.pushButton_4_2_listele.setObjectName(u"pushButton_4_2_listele")
        self.pushButton_4_2_listele.setGeometry(QRect(80, 430, 111, 51))
        sizePolicy.setHeightForWidth(self.pushButton_4_2_listele.sizePolicy().hasHeightForWidth())
        self.pushButton_4_2_listele.setSizePolicy(sizePolicy)
        self.pushButton_4_2_listele.setMinimumSize(QSize(80, 50))
        self.pushButton_4_2_listele.setFont(font7)
        self.pushButton_4_2_listele.setStyleSheet(u"QPushButton#pushButton_4_2_listele{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_2_listele:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_2_listele:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.formLayoutWidget_7 = QWidget(self.tab_4_2)
        self.formLayoutWidget_7.setObjectName(u"formLayoutWidget_7")
        self.formLayoutWidget_7.setGeometry(QRect(10, 80, 281, 51))
        self.formLayout_7 = QFormLayout(self.formLayoutWidget_7)
        self.formLayout_7.setObjectName(u"formLayout_7")
        self.formLayout_7.setContentsMargins(0, 0, 0, 0)
        self.comboBox_4_2_turu = QComboBox(self.formLayoutWidget_7)
        self.comboBox_4_2_turu.setObjectName(u"comboBox_4_2_turu")
        self.comboBox_4_2_turu.setFont(font9)

        self.formLayout_7.setWidget(0, QFormLayout.FieldRole, self.comboBox_4_2_turu)

        self.pushButton_4_2_temizle = QPushButton(self.tab_4_2)
        self.pushButton_4_2_temizle.setObjectName(u"pushButton_4_2_temizle")
        self.pushButton_4_2_temizle.setEnabled(False)
        self.pushButton_4_2_temizle.setGeometry(QRect(80, 500, 111, 51))
        sizePolicy.setHeightForWidth(self.pushButton_4_2_temizle.sizePolicy().hasHeightForWidth())
        self.pushButton_4_2_temizle.setSizePolicy(sizePolicy)
        self.pushButton_4_2_temizle.setMinimumSize(QSize(80, 50))
        self.pushButton_4_2_temizle.setFont(font7)
        self.pushButton_4_2_temizle.setStyleSheet(u"QPushButton#pushButton_4_2_temizle{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_2_temizle:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_2_temizle:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.tabWidget_4.addTab(self.tab_4_2, "")
        self.tab_4_3 = QWidget()
        self.tab_4_3.setObjectName(u"tab_4_3")
        self.label_28 = QLabel(self.tab_4_3)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setGeometry(QRect(46, 160, 181, 40))
        self.label_28.setFont(font6)
        self.label_28.setAlignment(Qt.AlignCenter)
        self.tableWidget_4_3_1 = QTableWidget(self.tab_4_3)
        if (self.tableWidget_4_3_1.columnCount() < 1):
            self.tableWidget_4_3_1.setColumnCount(1)
        __qtablewidgetitem26 = QTableWidgetItem()
        self.tableWidget_4_3_1.setHorizontalHeaderItem(0, __qtablewidgetitem26)
        self.tableWidget_4_3_1.setObjectName(u"tableWidget_4_3_1")
        self.tableWidget_4_3_1.setGeometry(QRect(40, 200, 200, 176))
        self.tableWidget_4_3_1.setMinimumSize(QSize(100, 100))
        self.tableWidget_4_3_1.setMaximumSize(QSize(200, 300))
        self.tableWidget_4_3_1.setFont(font8)
        self.tableWidget_4_3_1.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";\n"
"")
        self.tableWidget_4_3_2 = QTableWidget(self.tab_4_3)
        if (self.tableWidget_4_3_2.columnCount() < 8):
            self.tableWidget_4_3_2.setColumnCount(8)
        __qtablewidgetitem27 = QTableWidgetItem()
        self.tableWidget_4_3_2.setHorizontalHeaderItem(0, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        self.tableWidget_4_3_2.setHorizontalHeaderItem(1, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        self.tableWidget_4_3_2.setHorizontalHeaderItem(2, __qtablewidgetitem29)
        __qtablewidgetitem30 = QTableWidgetItem()
        self.tableWidget_4_3_2.setHorizontalHeaderItem(3, __qtablewidgetitem30)
        __qtablewidgetitem31 = QTableWidgetItem()
        self.tableWidget_4_3_2.setHorizontalHeaderItem(4, __qtablewidgetitem31)
        __qtablewidgetitem32 = QTableWidgetItem()
        self.tableWidget_4_3_2.setHorizontalHeaderItem(5, __qtablewidgetitem32)
        __qtablewidgetitem33 = QTableWidgetItem()
        self.tableWidget_4_3_2.setHorizontalHeaderItem(6, __qtablewidgetitem33)
        __qtablewidgetitem34 = QTableWidgetItem()
        self.tableWidget_4_3_2.setHorizontalHeaderItem(7, __qtablewidgetitem34)
        self.tableWidget_4_3_2.setObjectName(u"tableWidget_4_3_2")
        self.tableWidget_4_3_2.setGeometry(QRect(294, 10, 990, 545))
        self.tableWidget_4_3_2.setFont(font8)
        self.tableWidget_4_3_2.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";")
        self.tableWidget_4_3_2.setShowGrid(True)
        self.tableWidget_4_3_2.setColumnCount(8)
        self.pushButton_4_3_listele = QPushButton(self.tab_4_3)
        self.pushButton_4_3_listele.setObjectName(u"pushButton_4_3_listele")
        self.pushButton_4_3_listele.setGeometry(QRect(80, 430, 111, 51))
        sizePolicy.setHeightForWidth(self.pushButton_4_3_listele.sizePolicy().hasHeightForWidth())
        self.pushButton_4_3_listele.setSizePolicy(sizePolicy)
        self.pushButton_4_3_listele.setMinimumSize(QSize(80, 50))
        self.pushButton_4_3_listele.setFont(font7)
        self.pushButton_4_3_listele.setStyleSheet(u"QPushButton#pushButton_4_3_listele{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_3_listele:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_3_listele:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.formLayoutWidget_8 = QWidget(self.tab_4_3)
        self.formLayoutWidget_8.setObjectName(u"formLayoutWidget_8")
        self.formLayoutWidget_8.setGeometry(QRect(10, 80, 281, 51))
        self.formLayout_8 = QFormLayout(self.formLayoutWidget_8)
        self.formLayout_8.setObjectName(u"formLayout_8")
        self.formLayout_8.setContentsMargins(0, 0, 0, 0)
        self.comboBox_4_3_turu = QComboBox(self.formLayoutWidget_8)
        self.comboBox_4_3_turu.setObjectName(u"comboBox_4_3_turu")
        self.comboBox_4_3_turu.setFont(font9)

        self.formLayout_8.setWidget(0, QFormLayout.FieldRole, self.comboBox_4_3_turu)

        self.pushButton_4_3_temizle = QPushButton(self.tab_4_3)
        self.pushButton_4_3_temizle.setObjectName(u"pushButton_4_3_temizle")
        self.pushButton_4_3_temizle.setEnabled(False)
        self.pushButton_4_3_temizle.setGeometry(QRect(80, 500, 111, 51))
        sizePolicy.setHeightForWidth(self.pushButton_4_3_temizle.sizePolicy().hasHeightForWidth())
        self.pushButton_4_3_temizle.setSizePolicy(sizePolicy)
        self.pushButton_4_3_temizle.setMinimumSize(QSize(80, 50))
        self.pushButton_4_3_temizle.setFont(font7)
        self.pushButton_4_3_temizle.setStyleSheet(u"QPushButton#pushButton_4_3_temizle{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_3_temizle:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_3_temizle:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.tabWidget_4.addTab(self.tab_4_3, "")
        self.tab_4_4 = QWidget()
        self.tab_4_4.setObjectName(u"tab_4_4")
        self.label_29 = QLabel(self.tab_4_4)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setGeometry(QRect(46, 160, 181, 40))
        self.label_29.setFont(font6)
        self.label_29.setAlignment(Qt.AlignCenter)
        self.tableWidget_4_4_1 = QTableWidget(self.tab_4_4)
        if (self.tableWidget_4_4_1.columnCount() < 1):
            self.tableWidget_4_4_1.setColumnCount(1)
        __qtablewidgetitem35 = QTableWidgetItem()
        self.tableWidget_4_4_1.setHorizontalHeaderItem(0, __qtablewidgetitem35)
        self.tableWidget_4_4_1.setObjectName(u"tableWidget_4_4_1")
        self.tableWidget_4_4_1.setGeometry(QRect(40, 200, 200, 176))
        self.tableWidget_4_4_1.setMinimumSize(QSize(100, 100))
        self.tableWidget_4_4_1.setMaximumSize(QSize(200, 300))
        self.tableWidget_4_4_1.setFont(font8)
        self.tableWidget_4_4_1.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";\n"
"")
        self.tableWidget_4_4_2 = QTableWidget(self.tab_4_4)
        if (self.tableWidget_4_4_2.columnCount() < 8):
            self.tableWidget_4_4_2.setColumnCount(8)
        __qtablewidgetitem36 = QTableWidgetItem()
        self.tableWidget_4_4_2.setHorizontalHeaderItem(0, __qtablewidgetitem36)
        __qtablewidgetitem37 = QTableWidgetItem()
        self.tableWidget_4_4_2.setHorizontalHeaderItem(1, __qtablewidgetitem37)
        __qtablewidgetitem38 = QTableWidgetItem()
        self.tableWidget_4_4_2.setHorizontalHeaderItem(2, __qtablewidgetitem38)
        __qtablewidgetitem39 = QTableWidgetItem()
        self.tableWidget_4_4_2.setHorizontalHeaderItem(3, __qtablewidgetitem39)
        __qtablewidgetitem40 = QTableWidgetItem()
        self.tableWidget_4_4_2.setHorizontalHeaderItem(4, __qtablewidgetitem40)
        __qtablewidgetitem41 = QTableWidgetItem()
        self.tableWidget_4_4_2.setHorizontalHeaderItem(5, __qtablewidgetitem41)
        __qtablewidgetitem42 = QTableWidgetItem()
        self.tableWidget_4_4_2.setHorizontalHeaderItem(6, __qtablewidgetitem42)
        __qtablewidgetitem43 = QTableWidgetItem()
        self.tableWidget_4_4_2.setHorizontalHeaderItem(7, __qtablewidgetitem43)
        self.tableWidget_4_4_2.setObjectName(u"tableWidget_4_4_2")
        self.tableWidget_4_4_2.setGeometry(QRect(294, 10, 990, 545))
        self.tableWidget_4_4_2.setFont(font8)
        self.tableWidget_4_4_2.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";")
        self.tableWidget_4_4_2.setShowGrid(True)
        self.tableWidget_4_4_2.setColumnCount(8)
        self.pushButton_4_4_listele = QPushButton(self.tab_4_4)
        self.pushButton_4_4_listele.setObjectName(u"pushButton_4_4_listele")
        self.pushButton_4_4_listele.setGeometry(QRect(80, 430, 111, 51))
        sizePolicy.setHeightForWidth(self.pushButton_4_4_listele.sizePolicy().hasHeightForWidth())
        self.pushButton_4_4_listele.setSizePolicy(sizePolicy)
        self.pushButton_4_4_listele.setMinimumSize(QSize(80, 50))
        self.pushButton_4_4_listele.setFont(font7)
        self.pushButton_4_4_listele.setStyleSheet(u"QPushButton#pushButton_4_4_listele{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_4_listele:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_4_listele:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.formLayoutWidget_9 = QWidget(self.tab_4_4)
        self.formLayoutWidget_9.setObjectName(u"formLayoutWidget_9")
        self.formLayoutWidget_9.setGeometry(QRect(10, 80, 281, 51))
        self.formLayout_9 = QFormLayout(self.formLayoutWidget_9)
        self.formLayout_9.setObjectName(u"formLayout_9")
        self.formLayout_9.setContentsMargins(0, 0, 0, 0)
        self.comboBox_4_4_turu = QComboBox(self.formLayoutWidget_9)
        self.comboBox_4_4_turu.setObjectName(u"comboBox_4_4_turu")
        self.comboBox_4_4_turu.setFont(font9)

        self.formLayout_9.setWidget(0, QFormLayout.FieldRole, self.comboBox_4_4_turu)

        self.pushButton_4_4_temizle = QPushButton(self.tab_4_4)
        self.pushButton_4_4_temizle.setObjectName(u"pushButton_4_4_temizle")
        self.pushButton_4_4_temizle.setEnabled(False)
        self.pushButton_4_4_temizle.setGeometry(QRect(80, 500, 111, 51))
        sizePolicy.setHeightForWidth(self.pushButton_4_4_temizle.sizePolicy().hasHeightForWidth())
        self.pushButton_4_4_temizle.setSizePolicy(sizePolicy)
        self.pushButton_4_4_temizle.setMinimumSize(QSize(80, 50))
        self.pushButton_4_4_temizle.setFont(font7)
        self.pushButton_4_4_temizle.setStyleSheet(u"QPushButton#pushButton_4_4_temizle{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_4_temizle:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_4_4_temizle:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.tabWidget_4.addTab(self.tab_4_4, "")

        self.gridLayout_3.addWidget(self.tabWidget_4, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.gridLayout_4 = QGridLayout(self.tab_5)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.tabWidget_5 = QTabWidget(self.tab_5)
        self.tabWidget_5.setObjectName(u"tabWidget_5")
        self.tabWidget_5.setFont(font)
        self.tabWidget_5.setStyleSheet(u"")
        self.tabWidget_5.setTabPosition(QTabWidget.South)
        self.tab_5_1 = QWidget()
        self.tab_5_1.setObjectName(u"tab_5_1")
        self.gridLayout_5 = QGridLayout(self.tab_5_1)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_25 = QLabel(self.tab_5_1)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setFont(font6)

        self.gridLayout_5.addWidget(self.label_25, 0, 0, 1, 1)

        self.label_56 = QLabel(self.tab_5_1)
        self.label_56.setObjectName(u"label_56")
        self.label_56.setFont(font6)

        self.gridLayout_5.addWidget(self.label_56, 0, 1, 1, 1)

        self.label_58 = QLabel(self.tab_5_1)
        self.label_58.setObjectName(u"label_58")
        self.label_58.setFont(font6)

        self.gridLayout_5.addWidget(self.label_58, 0, 2, 1, 1)

        self.label_59 = QLabel(self.tab_5_1)
        self.label_59.setObjectName(u"label_59")
        self.label_59.setFont(font6)

        self.gridLayout_5.addWidget(self.label_59, 0, 3, 1, 1)

        self.tableWidget_5_1_1 = QTableWidget(self.tab_5_1)
        if (self.tableWidget_5_1_1.columnCount() < 2):
            self.tableWidget_5_1_1.setColumnCount(2)
        __qtablewidgetitem44 = QTableWidgetItem()
        self.tableWidget_5_1_1.setHorizontalHeaderItem(0, __qtablewidgetitem44)
        __qtablewidgetitem45 = QTableWidgetItem()
        self.tableWidget_5_1_1.setHorizontalHeaderItem(1, __qtablewidgetitem45)
        self.tableWidget_5_1_1.setObjectName(u"tableWidget_5_1_1")
        self.tableWidget_5_1_1.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";")

        self.gridLayout_5.addWidget(self.tableWidget_5_1_1, 1, 0, 1, 1)

        self.tableWidget_5_1_2 = QTableWidget(self.tab_5_1)
        if (self.tableWidget_5_1_2.columnCount() < 2):
            self.tableWidget_5_1_2.setColumnCount(2)
        __qtablewidgetitem46 = QTableWidgetItem()
        self.tableWidget_5_1_2.setHorizontalHeaderItem(0, __qtablewidgetitem46)
        __qtablewidgetitem47 = QTableWidgetItem()
        self.tableWidget_5_1_2.setHorizontalHeaderItem(1, __qtablewidgetitem47)
        self.tableWidget_5_1_2.setObjectName(u"tableWidget_5_1_2")
        self.tableWidget_5_1_2.setEnabled(True)
        self.tableWidget_5_1_2.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";")

        self.gridLayout_5.addWidget(self.tableWidget_5_1_2, 1, 1, 1, 1)

        self.tableWidget_5_1_3 = QTableWidget(self.tab_5_1)
        if (self.tableWidget_5_1_3.columnCount() < 2):
            self.tableWidget_5_1_3.setColumnCount(2)
        __qtablewidgetitem48 = QTableWidgetItem()
        self.tableWidget_5_1_3.setHorizontalHeaderItem(0, __qtablewidgetitem48)
        __qtablewidgetitem49 = QTableWidgetItem()
        self.tableWidget_5_1_3.setHorizontalHeaderItem(1, __qtablewidgetitem49)
        self.tableWidget_5_1_3.setObjectName(u"tableWidget_5_1_3")
        self.tableWidget_5_1_3.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";")

        self.gridLayout_5.addWidget(self.tableWidget_5_1_3, 1, 2, 1, 1)

        self.tableWidget_5_1_4 = QTableWidget(self.tab_5_1)
        if (self.tableWidget_5_1_4.columnCount() < 2):
            self.tableWidget_5_1_4.setColumnCount(2)
        __qtablewidgetitem50 = QTableWidgetItem()
        self.tableWidget_5_1_4.setHorizontalHeaderItem(0, __qtablewidgetitem50)
        __qtablewidgetitem51 = QTableWidgetItem()
        self.tableWidget_5_1_4.setHorizontalHeaderItem(1, __qtablewidgetitem51)
        self.tableWidget_5_1_4.setObjectName(u"tableWidget_5_1_4")
        self.tableWidget_5_1_4.setStyleSheet(u"font: italic 12pt \"Monotype Corsiva\";")

        self.gridLayout_5.addWidget(self.tableWidget_5_1_4, 1, 3, 1, 1)

        self.tabWidget_5.addTab(self.tab_5_1, "")
        self.tab_5_2 = QWidget()
        self.tab_5_2.setObjectName(u"tab_5_2")
        self.gridLayout_6 = QGridLayout(self.tab_5_2)
        self.gridLayout_6.setSpacing(5)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(5, 5, 5, 5)
        self.widget = QWidget(self.tab_5_2)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"border-image: url(:/figure/figure.png);")

        self.gridLayout_6.addWidget(self.widget, 0, 0, 1, 1)

        self.tabWidget_5.addTab(self.tab_5_2, "")

        self.gridLayout_4.addWidget(self.tabWidget_5, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_5, "")
        self.tab_6 = QWidget()
        self.tab_6.setObjectName(u"tab_6")
        self.gridLayout = QGridLayout(self.tab_6)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget_6 = QTabWidget(self.tab_6)
        self.tabWidget_6.setObjectName(u"tabWidget_6")
        self.tabWidget_6.setFont(font)
        self.tabWidget_6.setStyleSheet(u"\n"
"#tab_3_1{background-color: rgb(150, 255, 0);}\n"
"#tab_3_2{background-color: rgb(150, 170, 0);}\n"
"#tab_3_3{background-color: rgb(150, 85, 0);}")
        self.tabWidget_6.setTabPosition(QTabWidget.South)
        self.tab_6_1 = QWidget()
        self.tab_6_1.setObjectName(u"tab_6_1")
        self.pushButton_6_1_1_bul_kitap = QPushButton(self.tab_6_1)
        self.pushButton_6_1_1_bul_kitap.setObjectName(u"pushButton_6_1_1_bul_kitap")
        self.pushButton_6_1_1_bul_kitap.setGeometry(QRect(60, 170, 94, 50))
        sizePolicy.setHeightForWidth(self.pushButton_6_1_1_bul_kitap.sizePolicy().hasHeightForWidth())
        self.pushButton_6_1_1_bul_kitap.setSizePolicy(sizePolicy)
        self.pushButton_6_1_1_bul_kitap.setMinimumSize(QSize(80, 50))
        self.pushButton_6_1_1_bul_kitap.setFont(font7)
        self.pushButton_6_1_1_bul_kitap.setStyleSheet(u"QPushButton#pushButton_6_1_1_bul_kitap{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_1_1_bul_kitap:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_1_1_bul_kitap:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.formLayoutWidget_11 = QWidget(self.tab_6_1)
        self.formLayoutWidget_11.setObjectName(u"formLayoutWidget_11")
        self.formLayoutWidget_11.setGeometry(QRect(228, 30, 381, 501))
        self.formLayout_11 = QFormLayout(self.formLayoutWidget_11)
        self.formLayout_11.setObjectName(u"formLayout_11")
        self.formLayout_11.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout_11.setHorizontalSpacing(10)
        self.formLayout_11.setVerticalSpacing(30)
        self.formLayout_11.setContentsMargins(10, 0, 10, 0)
        self.label_39 = QLabel(self.formLayoutWidget_11)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setFont(font6)

        self.formLayout_11.setWidget(1, QFormLayout.LabelRole, self.label_39)

        self.lineEdit_6_1_adi = QLineEdit(self.formLayoutWidget_11)
        self.lineEdit_6_1_adi.setObjectName(u"lineEdit_6_1_adi")
        self.lineEdit_6_1_adi.setFont(font)

        self.formLayout_11.setWidget(1, QFormLayout.FieldRole, self.lineEdit_6_1_adi)

        self.label_40 = QLabel(self.formLayoutWidget_11)
        self.label_40.setObjectName(u"label_40")
        self.label_40.setFont(font6)

        self.formLayout_11.setWidget(2, QFormLayout.LabelRole, self.label_40)

        self.lineEdit_6_1_yazari = QLineEdit(self.formLayoutWidget_11)
        self.lineEdit_6_1_yazari.setObjectName(u"lineEdit_6_1_yazari")
        self.lineEdit_6_1_yazari.setFont(font)

        self.formLayout_11.setWidget(2, QFormLayout.FieldRole, self.lineEdit_6_1_yazari)

        self.label_41 = QLabel(self.formLayoutWidget_11)
        self.label_41.setObjectName(u"label_41")
        self.label_41.setFont(font6)

        self.formLayout_11.setWidget(3, QFormLayout.LabelRole, self.label_41)

        self.lineEdit_6_1_ceviren = QLineEdit(self.formLayoutWidget_11)
        self.lineEdit_6_1_ceviren.setObjectName(u"lineEdit_6_1_ceviren")
        self.lineEdit_6_1_ceviren.setFont(font)

        self.formLayout_11.setWidget(3, QFormLayout.FieldRole, self.lineEdit_6_1_ceviren)

        self.label_42 = QLabel(self.formLayoutWidget_11)
        self.label_42.setObjectName(u"label_42")
        self.label_42.setFont(font6)

        self.formLayout_11.setWidget(4, QFormLayout.LabelRole, self.label_42)

        self.lineEdit_6_1_turu = QLineEdit(self.formLayoutWidget_11)
        self.lineEdit_6_1_turu.setObjectName(u"lineEdit_6_1_turu")
        self.lineEdit_6_1_turu.setFont(font)

        self.formLayout_11.setWidget(4, QFormLayout.FieldRole, self.lineEdit_6_1_turu)

        self.label_43 = QLabel(self.formLayoutWidget_11)
        self.label_43.setObjectName(u"label_43")
        self.label_43.setFont(font6)

        self.formLayout_11.setWidget(5, QFormLayout.LabelRole, self.label_43)

        self.lineEdit_6_1_yayinevi = QLineEdit(self.formLayoutWidget_11)
        self.lineEdit_6_1_yayinevi.setObjectName(u"lineEdit_6_1_yayinevi")
        self.lineEdit_6_1_yayinevi.setFont(font)

        self.formLayout_11.setWidget(5, QFormLayout.FieldRole, self.lineEdit_6_1_yayinevi)

        self.label_44 = QLabel(self.formLayoutWidget_11)
        self.label_44.setObjectName(u"label_44")
        self.label_44.setFont(font6)

        self.formLayout_11.setWidget(6, QFormLayout.LabelRole, self.label_44)

        self.lineEdit_6_1_yili = QLineEdit(self.formLayoutWidget_11)
        self.lineEdit_6_1_yili.setObjectName(u"lineEdit_6_1_yili")
        self.lineEdit_6_1_yili.setFont(font)

        self.formLayout_11.setWidget(6, QFormLayout.FieldRole, self.lineEdit_6_1_yili)

        self.label_45 = QLabel(self.formLayoutWidget_11)
        self.label_45.setObjectName(u"label_45")
        self.label_45.setFont(font6)

        self.formLayout_11.setWidget(7, QFormLayout.LabelRole, self.label_45)

        self.lineEdit_6_1_sayfa = QLineEdit(self.formLayoutWidget_11)
        self.lineEdit_6_1_sayfa.setObjectName(u"lineEdit_6_1_sayfa")
        self.lineEdit_6_1_sayfa.setFont(font)

        self.formLayout_11.setWidget(7, QFormLayout.FieldRole, self.lineEdit_6_1_sayfa)

        self.lineEdit_6_1_id = QLineEdit(self.formLayoutWidget_11)
        self.lineEdit_6_1_id.setObjectName(u"lineEdit_6_1_id")
        self.lineEdit_6_1_id.setFont(font)

        self.formLayout_11.setWidget(0, QFormLayout.FieldRole, self.lineEdit_6_1_id)

        self.label_46 = QLabel(self.formLayoutWidget_11)
        self.label_46.setObjectName(u"label_46")
        self.label_46.setFont(font6)

        self.formLayout_11.setWidget(0, QFormLayout.LabelRole, self.label_46)

        self.pushButton_6_1_islemi_kaydet = QPushButton(self.tab_6_1)
        self.pushButton_6_1_islemi_kaydet.setObjectName(u"pushButton_6_1_islemi_kaydet")
        self.pushButton_6_1_islemi_kaydet.setEnabled(False)
        self.pushButton_6_1_islemi_kaydet.setGeometry(QRect(1080, 460, 191, 71))
        sizePolicy.setHeightForWidth(self.pushButton_6_1_islemi_kaydet.sizePolicy().hasHeightForWidth())
        self.pushButton_6_1_islemi_kaydet.setSizePolicy(sizePolicy)
        self.pushButton_6_1_islemi_kaydet.setMinimumSize(QSize(80, 50))
        self.pushButton_6_1_islemi_kaydet.setFont(font7)
        self.pushButton_6_1_islemi_kaydet.setStyleSheet(u"QPushButton#pushButton_6_1_islemi_kaydet{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_1_islemi_kaydet:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_1_islemi_kaydet:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.comboBox_6_1_1_liste_kitap = QComboBox(self.tab_6_1)
        self.comboBox_6_1_1_liste_kitap.setObjectName(u"comboBox_6_1_1_liste_kitap")
        self.comboBox_6_1_1_liste_kitap.setGeometry(QRect(20, 90, 200, 35))
        self.comboBox_6_1_1_liste_kitap.setFont(font)
        self.label_47 = QLabel(self.tab_6_1)
        self.label_47.setObjectName(u"label_47")
        self.label_47.setGeometry(QRect(40, 20, 151, 51))
        self.label_47.setFont(font9)
        self.pushButton_6_1_2_bul_kisi = QPushButton(self.tab_6_1)
        self.pushButton_6_1_2_bul_kisi.setObjectName(u"pushButton_6_1_2_bul_kisi")
        self.pushButton_6_1_2_bul_kisi.setGeometry(QRect(720, 170, 94, 50))
        sizePolicy.setHeightForWidth(self.pushButton_6_1_2_bul_kisi.sizePolicy().hasHeightForWidth())
        self.pushButton_6_1_2_bul_kisi.setSizePolicy(sizePolicy)
        self.pushButton_6_1_2_bul_kisi.setMinimumSize(QSize(80, 50))
        self.pushButton_6_1_2_bul_kisi.setFont(font7)
        self.pushButton_6_1_2_bul_kisi.setStyleSheet(u"QPushButton#pushButton_6_1_2_bul_kisi{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_1_2_bul_kisi:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_1_2_bul_kisi:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.comboBox_6_1_2_liste_kisi = QComboBox(self.tab_6_1)
        self.comboBox_6_1_2_liste_kisi.setObjectName(u"comboBox_6_1_2_liste_kisi")
        self.comboBox_6_1_2_liste_kisi.setGeometry(QRect(670, 90, 200, 35))
        self.comboBox_6_1_2_liste_kisi.setFont(font)
        self.label_78 = QLabel(self.tab_6_1)
        self.label_78.setObjectName(u"label_78")
        self.label_78.setGeometry(QRect(680, 20, 131, 41))
        self.label_78.setFont(font9)
        self.formLayoutWidget_17 = QWidget(self.tab_6_1)
        self.formLayoutWidget_17.setObjectName(u"formLayoutWidget_17")
        self.formLayoutWidget_17.setGeometry(QRect(890, 30, 371, 331))
        self.formLayout_18 = QFormLayout(self.formLayoutWidget_17)
        self.formLayout_18.setObjectName(u"formLayout_18")
        self.formLayout_18.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout_18.setHorizontalSpacing(10)
        self.formLayout_18.setVerticalSpacing(30)
        self.formLayout_18.setContentsMargins(10, 0, 10, 0)
        self.label_94 = QLabel(self.formLayoutWidget_17)
        self.label_94.setObjectName(u"label_94")
        self.label_94.setFont(font6)

        self.formLayout_18.setWidget(0, QFormLayout.LabelRole, self.label_94)

        self.lineEdit_6_1_kullanici = QLineEdit(self.formLayoutWidget_17)
        self.lineEdit_6_1_kullanici.setObjectName(u"lineEdit_6_1_kullanici")
        self.lineEdit_6_1_kullanici.setFont(font)

        self.formLayout_18.setWidget(0, QFormLayout.FieldRole, self.lineEdit_6_1_kullanici)

        self.label_87 = QLabel(self.formLayoutWidget_17)
        self.label_87.setObjectName(u"label_87")
        self.label_87.setFont(font6)

        self.formLayout_18.setWidget(1, QFormLayout.LabelRole, self.label_87)

        self.lineEdit_6_1_adi_soyadi = QLineEdit(self.formLayoutWidget_17)
        self.lineEdit_6_1_adi_soyadi.setObjectName(u"lineEdit_6_1_adi_soyadi")
        self.lineEdit_6_1_adi_soyadi.setFont(font)

        self.formLayout_18.setWidget(1, QFormLayout.FieldRole, self.lineEdit_6_1_adi_soyadi)

        self.label_88 = QLabel(self.formLayoutWidget_17)
        self.label_88.setObjectName(u"label_88")
        self.label_88.setFont(font6)

        self.formLayout_18.setWidget(2, QFormLayout.LabelRole, self.label_88)

        self.lineEdit_6_1_telefon = QLineEdit(self.formLayoutWidget_17)
        self.lineEdit_6_1_telefon.setObjectName(u"lineEdit_6_1_telefon")
        self.lineEdit_6_1_telefon.setFont(font)

        self.formLayout_18.setWidget(2, QFormLayout.FieldRole, self.lineEdit_6_1_telefon)

        self.label_89 = QLabel(self.formLayoutWidget_17)
        self.label_89.setObjectName(u"label_89")
        self.label_89.setFont(font6)

        self.formLayout_18.setWidget(3, QFormLayout.LabelRole, self.label_89)

        self.lineEdit_6_1_mail = QLineEdit(self.formLayoutWidget_17)
        self.lineEdit_6_1_mail.setObjectName(u"lineEdit_6_1_mail")
        self.lineEdit_6_1_mail.setFont(font)

        self.formLayout_18.setWidget(3, QFormLayout.FieldRole, self.lineEdit_6_1_mail)

        self.label_90 = QLabel(self.formLayoutWidget_17)
        self.label_90.setObjectName(u"label_90")
        self.label_90.setFont(font6)

        self.formLayout_18.setWidget(4, QFormLayout.LabelRole, self.label_90)

        self.lineEdit_6_1_yetki = QLineEdit(self.formLayoutWidget_17)
        self.lineEdit_6_1_yetki.setObjectName(u"lineEdit_6_1_yetki")
        self.lineEdit_6_1_yetki.setFont(font)

        self.formLayout_18.setWidget(4, QFormLayout.FieldRole, self.lineEdit_6_1_yetki)

        self.pushButton_6_1_1_bul_kitap_temizle = QPushButton(self.tab_6_1)
        self.pushButton_6_1_1_bul_kitap_temizle.setObjectName(u"pushButton_6_1_1_bul_kitap_temizle")
        self.pushButton_6_1_1_bul_kitap_temizle.setEnabled(False)
        self.pushButton_6_1_1_bul_kitap_temizle.setGeometry(QRect(60, 270, 94, 50))
        sizePolicy.setHeightForWidth(self.pushButton_6_1_1_bul_kitap_temizle.sizePolicy().hasHeightForWidth())
        self.pushButton_6_1_1_bul_kitap_temizle.setSizePolicy(sizePolicy)
        self.pushButton_6_1_1_bul_kitap_temizle.setMinimumSize(QSize(80, 50))
        self.pushButton_6_1_1_bul_kitap_temizle.setFont(font7)
        self.pushButton_6_1_1_bul_kitap_temizle.setStyleSheet(u"QPushButton#pushButton_6_1_1_bul_kitap_temizle{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_1_1_bul_kitap_temizle:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_1_1_bul_kitap_temizle:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.pushButton_6_1_2_bul_kisi_temizle = QPushButton(self.tab_6_1)
        self.pushButton_6_1_2_bul_kisi_temizle.setObjectName(u"pushButton_6_1_2_bul_kisi_temizle")
        self.pushButton_6_1_2_bul_kisi_temizle.setEnabled(False)
        self.pushButton_6_1_2_bul_kisi_temizle.setGeometry(QRect(720, 260, 94, 50))
        sizePolicy.setHeightForWidth(self.pushButton_6_1_2_bul_kisi_temizle.sizePolicy().hasHeightForWidth())
        self.pushButton_6_1_2_bul_kisi_temizle.setSizePolicy(sizePolicy)
        self.pushButton_6_1_2_bul_kisi_temizle.setMinimumSize(QSize(80, 50))
        self.pushButton_6_1_2_bul_kisi_temizle.setFont(font7)
        self.pushButton_6_1_2_bul_kisi_temizle.setStyleSheet(u"QPushButton#pushButton_6_1_2_bul_kisi_temizle{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_1_2_bul_kisi_temizle:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_1_2_bul_kisi_temizle:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.tabWidget_6.addTab(self.tab_6_1, "")
        self.tab_6_2 = QWidget()
        self.tab_6_2.setObjectName(u"tab_6_2")
        self.label_79 = QLabel(self.tab_6_2)
        self.label_79.setObjectName(u"label_79")
        self.label_79.setGeometry(QRect(50, 20, 131, 41))
        self.label_79.setFont(font9)
        self.pushButton_6_2_1_bul_kisi = QPushButton(self.tab_6_2)
        self.pushButton_6_2_1_bul_kisi.setObjectName(u"pushButton_6_2_1_bul_kisi")
        self.pushButton_6_2_1_bul_kisi.setGeometry(QRect(90, 170, 94, 50))
        sizePolicy.setHeightForWidth(self.pushButton_6_2_1_bul_kisi.sizePolicy().hasHeightForWidth())
        self.pushButton_6_2_1_bul_kisi.setSizePolicy(sizePolicy)
        self.pushButton_6_2_1_bul_kisi.setMinimumSize(QSize(80, 50))
        self.pushButton_6_2_1_bul_kisi.setFont(font7)
        self.pushButton_6_2_1_bul_kisi.setStyleSheet(u"QPushButton#pushButton_6_2_1_bul_kisi{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_2_1_bul_kisi:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_2_1_bul_kisi:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.comboBox_6_2_1_liste_kisi = QComboBox(self.tab_6_2)
        self.comboBox_6_2_1_liste_kisi.setObjectName(u"comboBox_6_2_1_liste_kisi")
        self.comboBox_6_2_1_liste_kisi.setGeometry(QRect(40, 90, 200, 35))
        self.comboBox_6_2_1_liste_kisi.setFont(font)
        self.formLayoutWidget_18 = QWidget(self.tab_6_2)
        self.formLayoutWidget_18.setObjectName(u"formLayoutWidget_18")
        self.formLayoutWidget_18.setGeometry(QRect(260, 30, 371, 331))
        self.formLayout_19 = QFormLayout(self.formLayoutWidget_18)
        self.formLayout_19.setObjectName(u"formLayout_19")
        self.formLayout_19.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout_19.setHorizontalSpacing(10)
        self.formLayout_19.setVerticalSpacing(30)
        self.formLayout_19.setContentsMargins(10, 0, 10, 0)
        self.label_95 = QLabel(self.formLayoutWidget_18)
        self.label_95.setObjectName(u"label_95")
        self.label_95.setFont(font6)

        self.formLayout_19.setWidget(0, QFormLayout.LabelRole, self.label_95)

        self.lineEdit_6_2_kullanici = QLineEdit(self.formLayoutWidget_18)
        self.lineEdit_6_2_kullanici.setObjectName(u"lineEdit_6_2_kullanici")
        self.lineEdit_6_2_kullanici.setFont(font)

        self.formLayout_19.setWidget(0, QFormLayout.FieldRole, self.lineEdit_6_2_kullanici)

        self.label_91 = QLabel(self.formLayoutWidget_18)
        self.label_91.setObjectName(u"label_91")
        self.label_91.setFont(font6)

        self.formLayout_19.setWidget(1, QFormLayout.LabelRole, self.label_91)

        self.lineEdit_6_2_adi_soyadi = QLineEdit(self.formLayoutWidget_18)
        self.lineEdit_6_2_adi_soyadi.setObjectName(u"lineEdit_6_2_adi_soyadi")
        self.lineEdit_6_2_adi_soyadi.setFont(font)

        self.formLayout_19.setWidget(1, QFormLayout.FieldRole, self.lineEdit_6_2_adi_soyadi)

        self.label_92 = QLabel(self.formLayoutWidget_18)
        self.label_92.setObjectName(u"label_92")
        self.label_92.setFont(font6)

        self.formLayout_19.setWidget(2, QFormLayout.LabelRole, self.label_92)

        self.lineEdit_6_2_telefon = QLineEdit(self.formLayoutWidget_18)
        self.lineEdit_6_2_telefon.setObjectName(u"lineEdit_6_2_telefon")
        self.lineEdit_6_2_telefon.setFont(font)

        self.formLayout_19.setWidget(2, QFormLayout.FieldRole, self.lineEdit_6_2_telefon)

        self.label_93 = QLabel(self.formLayoutWidget_18)
        self.label_93.setObjectName(u"label_93")
        self.label_93.setFont(font6)

        self.formLayout_19.setWidget(3, QFormLayout.LabelRole, self.label_93)

        self.lineEdit_6_2_mail = QLineEdit(self.formLayoutWidget_18)
        self.lineEdit_6_2_mail.setObjectName(u"lineEdit_6_2_mail")
        self.lineEdit_6_2_mail.setFont(font)

        self.formLayout_19.setWidget(3, QFormLayout.FieldRole, self.lineEdit_6_2_mail)

        self.label_96 = QLabel(self.formLayoutWidget_18)
        self.label_96.setObjectName(u"label_96")
        self.label_96.setFont(font6)

        self.formLayout_19.setWidget(4, QFormLayout.LabelRole, self.label_96)

        self.lineEdit_6_2_yetki = QLineEdit(self.formLayoutWidget_18)
        self.lineEdit_6_2_yetki.setObjectName(u"lineEdit_6_2_yetki")
        self.lineEdit_6_2_yetki.setFont(font)

        self.formLayout_19.setWidget(4, QFormLayout.FieldRole, self.lineEdit_6_2_yetki)

        self.pushButton_6_2_1_bul_kisi_temizle = QPushButton(self.tab_6_2)
        self.pushButton_6_2_1_bul_kisi_temizle.setObjectName(u"pushButton_6_2_1_bul_kisi_temizle")
        self.pushButton_6_2_1_bul_kisi_temizle.setEnabled(False)
        self.pushButton_6_2_1_bul_kisi_temizle.setGeometry(QRect(90, 260, 94, 50))
        sizePolicy.setHeightForWidth(self.pushButton_6_2_1_bul_kisi_temizle.sizePolicy().hasHeightForWidth())
        self.pushButton_6_2_1_bul_kisi_temizle.setSizePolicy(sizePolicy)
        self.pushButton_6_2_1_bul_kisi_temizle.setMinimumSize(QSize(80, 50))
        self.pushButton_6_2_1_bul_kisi_temizle.setFont(font7)
        self.pushButton_6_2_1_bul_kisi_temizle.setStyleSheet(u"QPushButton#pushButton_6_2_1_bul_kisi_temizle{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_2_1_bul_kisi_temizle:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_2_1_bul_kisi_temizle:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.comboBox_6_2_2_liste_kitap = QComboBox(self.tab_6_2)
        self.comboBox_6_2_2_liste_kitap.setObjectName(u"comboBox_6_2_2_liste_kitap")
        self.comboBox_6_2_2_liste_kitap.setEnabled(True)
        self.comboBox_6_2_2_liste_kitap.setGeometry(QRect(680, 90, 200, 35))
        self.comboBox_6_2_2_liste_kitap.setFont(font)
        self.formLayoutWidget_12 = QWidget(self.tab_6_2)
        self.formLayoutWidget_12.setObjectName(u"formLayoutWidget_12")
        self.formLayoutWidget_12.setGeometry(QRect(888, 30, 381, 501))
        self.formLayout_12 = QFormLayout(self.formLayoutWidget_12)
        self.formLayout_12.setObjectName(u"formLayout_12")
        self.formLayout_12.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout_12.setHorizontalSpacing(10)
        self.formLayout_12.setVerticalSpacing(30)
        self.formLayout_12.setContentsMargins(10, 0, 10, 0)
        self.label_48 = QLabel(self.formLayoutWidget_12)
        self.label_48.setObjectName(u"label_48")
        self.label_48.setFont(font6)

        self.formLayout_12.setWidget(1, QFormLayout.LabelRole, self.label_48)

        self.lineEdit_6_2_adi = QLineEdit(self.formLayoutWidget_12)
        self.lineEdit_6_2_adi.setObjectName(u"lineEdit_6_2_adi")
        self.lineEdit_6_2_adi.setFont(font)

        self.formLayout_12.setWidget(1, QFormLayout.FieldRole, self.lineEdit_6_2_adi)

        self.label_49 = QLabel(self.formLayoutWidget_12)
        self.label_49.setObjectName(u"label_49")
        self.label_49.setFont(font6)

        self.formLayout_12.setWidget(2, QFormLayout.LabelRole, self.label_49)

        self.lineEdit_6_2_yazari = QLineEdit(self.formLayoutWidget_12)
        self.lineEdit_6_2_yazari.setObjectName(u"lineEdit_6_2_yazari")
        self.lineEdit_6_2_yazari.setFont(font)

        self.formLayout_12.setWidget(2, QFormLayout.FieldRole, self.lineEdit_6_2_yazari)

        self.label_50 = QLabel(self.formLayoutWidget_12)
        self.label_50.setObjectName(u"label_50")
        self.label_50.setFont(font6)

        self.formLayout_12.setWidget(3, QFormLayout.LabelRole, self.label_50)

        self.lineEdit_6_2_ceviren = QLineEdit(self.formLayoutWidget_12)
        self.lineEdit_6_2_ceviren.setObjectName(u"lineEdit_6_2_ceviren")
        self.lineEdit_6_2_ceviren.setFont(font)

        self.formLayout_12.setWidget(3, QFormLayout.FieldRole, self.lineEdit_6_2_ceviren)

        self.label_51 = QLabel(self.formLayoutWidget_12)
        self.label_51.setObjectName(u"label_51")
        self.label_51.setFont(font6)

        self.formLayout_12.setWidget(4, QFormLayout.LabelRole, self.label_51)

        self.lineEdit_6_2_turu = QLineEdit(self.formLayoutWidget_12)
        self.lineEdit_6_2_turu.setObjectName(u"lineEdit_6_2_turu")
        self.lineEdit_6_2_turu.setFont(font)

        self.formLayout_12.setWidget(4, QFormLayout.FieldRole, self.lineEdit_6_2_turu)

        self.label_52 = QLabel(self.formLayoutWidget_12)
        self.label_52.setObjectName(u"label_52")
        self.label_52.setFont(font6)

        self.formLayout_12.setWidget(5, QFormLayout.LabelRole, self.label_52)

        self.lineEdit_6_2_yayinevi = QLineEdit(self.formLayoutWidget_12)
        self.lineEdit_6_2_yayinevi.setObjectName(u"lineEdit_6_2_yayinevi")
        self.lineEdit_6_2_yayinevi.setFont(font)

        self.formLayout_12.setWidget(5, QFormLayout.FieldRole, self.lineEdit_6_2_yayinevi)

        self.label_53 = QLabel(self.formLayoutWidget_12)
        self.label_53.setObjectName(u"label_53")
        self.label_53.setFont(font6)

        self.formLayout_12.setWidget(6, QFormLayout.LabelRole, self.label_53)

        self.lineEdit_6_2_yili = QLineEdit(self.formLayoutWidget_12)
        self.lineEdit_6_2_yili.setObjectName(u"lineEdit_6_2_yili")
        self.lineEdit_6_2_yili.setFont(font)

        self.formLayout_12.setWidget(6, QFormLayout.FieldRole, self.lineEdit_6_2_yili)

        self.label_54 = QLabel(self.formLayoutWidget_12)
        self.label_54.setObjectName(u"label_54")
        self.label_54.setFont(font6)

        self.formLayout_12.setWidget(7, QFormLayout.LabelRole, self.label_54)

        self.lineEdit_6_2_sayfa = QLineEdit(self.formLayoutWidget_12)
        self.lineEdit_6_2_sayfa.setObjectName(u"lineEdit_6_2_sayfa")
        self.lineEdit_6_2_sayfa.setFont(font)

        self.formLayout_12.setWidget(7, QFormLayout.FieldRole, self.lineEdit_6_2_sayfa)

        self.lineEdit_6_2_id = QLineEdit(self.formLayoutWidget_12)
        self.lineEdit_6_2_id.setObjectName(u"lineEdit_6_2_id")
        self.lineEdit_6_2_id.setFont(font)

        self.formLayout_12.setWidget(0, QFormLayout.FieldRole, self.lineEdit_6_2_id)

        self.label_55 = QLabel(self.formLayoutWidget_12)
        self.label_55.setObjectName(u"label_55")
        self.label_55.setFont(font6)

        self.formLayout_12.setWidget(0, QFormLayout.LabelRole, self.label_55)

        self.label_57 = QLabel(self.tab_6_2)
        self.label_57.setObjectName(u"label_57")
        self.label_57.setGeometry(QRect(700, 20, 151, 51))
        self.label_57.setFont(font9)
        self.pushButton_6_2_2_bul_kitap_temizle = QPushButton(self.tab_6_2)
        self.pushButton_6_2_2_bul_kitap_temizle.setObjectName(u"pushButton_6_2_2_bul_kitap_temizle")
        self.pushButton_6_2_2_bul_kitap_temizle.setEnabled(False)
        self.pushButton_6_2_2_bul_kitap_temizle.setGeometry(QRect(720, 270, 94, 50))
        sizePolicy.setHeightForWidth(self.pushButton_6_2_2_bul_kitap_temizle.sizePolicy().hasHeightForWidth())
        self.pushButton_6_2_2_bul_kitap_temizle.setSizePolicy(sizePolicy)
        self.pushButton_6_2_2_bul_kitap_temizle.setMinimumSize(QSize(80, 50))
        self.pushButton_6_2_2_bul_kitap_temizle.setFont(font7)
        self.pushButton_6_2_2_bul_kitap_temizle.setStyleSheet(u"QPushButton#pushButton_6_2_2_bul_kitap_temizle{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_2_2_bul_kitap_temizle:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_2_2_bul_kitap_temizle:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.pushButton_6_2_2_bul_kitap = QPushButton(self.tab_6_2)
        self.pushButton_6_2_2_bul_kitap.setObjectName(u"pushButton_6_2_2_bul_kitap")
        self.pushButton_6_2_2_bul_kitap.setEnabled(False)
        self.pushButton_6_2_2_bul_kitap.setGeometry(QRect(720, 170, 94, 50))
        sizePolicy.setHeightForWidth(self.pushButton_6_2_2_bul_kitap.sizePolicy().hasHeightForWidth())
        self.pushButton_6_2_2_bul_kitap.setSizePolicy(sizePolicy)
        self.pushButton_6_2_2_bul_kitap.setMinimumSize(QSize(80, 50))
        self.pushButton_6_2_2_bul_kitap.setFont(font7)
        self.pushButton_6_2_2_bul_kitap.setStyleSheet(u"QPushButton#pushButton_6_2_2_bul_kitap{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_2_2_bul_kitap:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_2_2_bul_kitap:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.pushButton_6_2_islemi_kaydet = QPushButton(self.tab_6_2)
        self.pushButton_6_2_islemi_kaydet.setObjectName(u"pushButton_6_2_islemi_kaydet")
        self.pushButton_6_2_islemi_kaydet.setEnabled(False)
        self.pushButton_6_2_islemi_kaydet.setGeometry(QRect(260, 460, 191, 71))
        sizePolicy.setHeightForWidth(self.pushButton_6_2_islemi_kaydet.sizePolicy().hasHeightForWidth())
        self.pushButton_6_2_islemi_kaydet.setSizePolicy(sizePolicy)
        self.pushButton_6_2_islemi_kaydet.setMinimumSize(QSize(80, 50))
        self.pushButton_6_2_islemi_kaydet.setFont(font7)
        self.pushButton_6_2_islemi_kaydet.setStyleSheet(u"QPushButton#pushButton_6_2_islemi_kaydet{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_2_islemi_kaydet:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_2_islemi_kaydet:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.tabWidget_6.addTab(self.tab_6_2, "")
        self.tab_6_3 = QWidget()
        self.tab_6_3.setObjectName(u"tab_6_3")
        self.pushButton_3_3_Sil_2 = QPushButton(self.tab_6_3)
        self.pushButton_3_3_Sil_2.setObjectName(u"pushButton_3_3_Sil_2")
        self.pushButton_3_3_Sil_2.setEnabled(False)
        self.pushButton_3_3_Sil_2.setGeometry(QRect(1000, 280, 80, 61))
        sizePolicy.setHeightForWidth(self.pushButton_3_3_Sil_2.sizePolicy().hasHeightForWidth())
        self.pushButton_3_3_Sil_2.setSizePolicy(sizePolicy)
        self.pushButton_3_3_Sil_2.setMinimumSize(QSize(80, 50))
        self.pushButton_3_3_Sil_2.setFont(font7)
        self.pushButton_3_3_Sil_2.setStyleSheet(u"QPushButton#pushButton_3_3_Sil{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_3_Sil:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_3_3_Sil:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.pushButton_6_3_temizle = QPushButton(self.tab_6_3)
        self.pushButton_6_3_temizle.setObjectName(u"pushButton_6_3_temizle")
        self.pushButton_6_3_temizle.setGeometry(QRect(40, 340, 100, 60))
        sizePolicy.setHeightForWidth(self.pushButton_6_3_temizle.sizePolicy().hasHeightForWidth())
        self.pushButton_6_3_temizle.setSizePolicy(sizePolicy)
        self.pushButton_6_3_temizle.setMinimumSize(QSize(100, 60))
        self.pushButton_6_3_temizle.setFont(font5)
        self.pushButton_6_3_temizle.setStyleSheet(u"QPushButton#pushButton_6_3_temizle{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_3_temizle:hover{\n"
"background-color: rgba(0, 248, 49, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_3_temizle:pressed{\n"
"background-color: rgba(6, 211, 166,150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.pushButton_6_3_listele = QPushButton(self.tab_6_3)
        self.pushButton_6_3_listele.setObjectName(u"pushButton_6_3_listele")
        self.pushButton_6_3_listele.setGeometry(QRect(40, 210, 100, 60))
        sizePolicy.setHeightForWidth(self.pushButton_6_3_listele.sizePolicy().hasHeightForWidth())
        self.pushButton_6_3_listele.setSizePolicy(sizePolicy)
        self.pushButton_6_3_listele.setMinimumSize(QSize(100, 60))
        self.pushButton_6_3_listele.setFont(font5)
        self.pushButton_6_3_listele.setStyleSheet(u"QPushButton#pushButton_6_3_listele{	\n"
"background-color: rgba(6, 211, 166, 150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_3_listele:hover{\n"
"background-color: rgba(6, 211, 166,150);\n"
"border-radius:10px;}\n"
"\n"
"QPushButton#pushButton_6_3_listele:pressed{\n"
"\n"
"background-color: rgba(0, 248, 49, 150);\n"
"padding-left:5px;\n"
"padding-top:6px;\n"
"border-radius:10px;}\n"
"\n"
"\n"
"")
        self.tableWidget_6_2 = QTableWidget(self.tab_6_3)
        if (self.tableWidget_6_2.columnCount() < 7):
            self.tableWidget_6_2.setColumnCount(7)
        __qtablewidgetitem52 = QTableWidgetItem()
        self.tableWidget_6_2.setHorizontalHeaderItem(0, __qtablewidgetitem52)
        __qtablewidgetitem53 = QTableWidgetItem()
        self.tableWidget_6_2.setHorizontalHeaderItem(1, __qtablewidgetitem53)
        __qtablewidgetitem54 = QTableWidgetItem()
        self.tableWidget_6_2.setHorizontalHeaderItem(2, __qtablewidgetitem54)
        __qtablewidgetitem55 = QTableWidgetItem()
        self.tableWidget_6_2.setHorizontalHeaderItem(3, __qtablewidgetitem55)
        __qtablewidgetitem56 = QTableWidgetItem()
        self.tableWidget_6_2.setHorizontalHeaderItem(4, __qtablewidgetitem56)
        __qtablewidgetitem57 = QTableWidgetItem()
        self.tableWidget_6_2.setHorizontalHeaderItem(5, __qtablewidgetitem57)
        __qtablewidgetitem58 = QTableWidgetItem()
        self.tableWidget_6_2.setHorizontalHeaderItem(6, __qtablewidgetitem58)
        self.tableWidget_6_2.setObjectName(u"tableWidget_6_2")
        self.tableWidget_6_2.setGeometry(QRect(160, 0, 1160, 590))
        self.tableWidget_6_2.setFont(font4)
        self.tableWidget_6_2.setStyleSheet(u"font: italic 14pt \"Monotype Corsiva\";")
        self.tableWidget_6_2.setShowGrid(True)
        self.tableWidget_6_2.setColumnCount(7)
        self.tabWidget_6.addTab(self.tab_6_3, "")

        self.gridLayout.addWidget(self.tabWidget_6, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_6, "")

        self.gridLayout_7.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setFont(font)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_3.setCurrentIndex(0)
        self.tabWidget_4.setCurrentIndex(0)
        self.tabWidget_5.setCurrentIndex(0)
        self.tabWidget_6.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Ya\u015far K\u00fct\u00fcphanesi", None))
        self.pushButton_1_yeni_kullanici.setText(QCoreApplication.translate("MainWindow", u"Yeni Kullan\u0131c\u0131 Giri\u015fi", None))
        self.pushButton_1_cikis.setText(QCoreApplication.translate("MainWindow", u"\u00c7 \u0131 k \u0131 \u015f", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"Y\u00f6netici", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), QCoreApplication.translate("MainWindow", u"Giri\u015f", None))
        ___qtablewidgetitem = self.tableWidget_2.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem1 = self.tableWidget_2.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem2 = self.tableWidget_2.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem3 = self.tableWidget_2.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem4 = self.tableWidget_2.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem5 = self.tableWidget_2.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem6 = self.tableWidget_2.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem7 = self.tableWidget_2.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        self.pushButton_2_temizle.setText(QCoreApplication.translate("MainWindow", u"T e m i z l e", None))
        self.pushButton_2_listele.setText(QCoreApplication.translate("MainWindow", u"L i s t e l e", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Kitap Listesi", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Kitap Ad\u0131", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Yazar\u0131", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u00c7eviren", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"T\u00fcr\u00fc", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Yay\u0131nevi", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Y\u0131l\u0131", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Sayfa", None))
        self.pushButton_3_1_kaydet.setText(QCoreApplication.translate("MainWindow", u"K a y d e t", None))
        self.pushButton_3_1_temizle.setText(QCoreApplication.translate("MainWindow", u"T e m i z l e", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_3_1), QCoreApplication.translate("MainWindow", u"Kay\u0131t Ekleme", None))
        self.pushButton_3_2_bul.setText(QCoreApplication.translate("MainWindow", u"Aranan Kayd\u0131\n"
"B u l", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Kitap Ad\u0131", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Yazar\u0131", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"\u00c7eviren", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"T\u00fcr\u00fc", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Yay\u0131nevi", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Y\u0131l\u0131", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Sayfa", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131t No", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Bulunacak Kitap Ad\u0131", None))
        self.pushButton_3_2_deg_kaydet.setText(QCoreApplication.translate("MainWindow", u"De\u011fi\u015fikli\u011fi\n"
"Kaydet", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_3_2), QCoreApplication.translate("MainWindow", u"Kay\u0131t D\u00fczenleme", None))
        self.pushButton_3_3_bul.setText(QCoreApplication.translate("MainWindow", u"Aranan Kayd\u0131\n"
"B u l", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Kitap Ad\u0131", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Yazar\u0131", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"\u00c7eviren", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"T\u00fcr\u00fc", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"Yay\u0131nevi", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"Y\u0131l\u0131", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"Sayfa", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131t No", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"Bulunacak Kitap Ad\u0131", None))
        self.pushButton_3_3_Sil.setText(QCoreApplication.translate("MainWindow", u"Kayd\u0131\n"
"S i l", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_3_3), QCoreApplication.translate("MainWindow", u"Kay\u0131t Silme", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"Kitap Kay\u0131t", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"Listelenecek Kay\u0131t ", None))
        ___qtablewidgetitem8 = self.tableWidget_4_1_1.horizontalHeaderItem(0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem9 = self.tableWidget_4_1_2.horizontalHeaderItem(0)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem10 = self.tableWidget_4_1_2.horizontalHeaderItem(1)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem11 = self.tableWidget_4_1_2.horizontalHeaderItem(2)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem12 = self.tableWidget_4_1_2.horizontalHeaderItem(3)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem13 = self.tableWidget_4_1_2.horizontalHeaderItem(4)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem14 = self.tableWidget_4_1_2.horizontalHeaderItem(5)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem15 = self.tableWidget_4_1_2.horizontalHeaderItem(6)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem16 = self.tableWidget_4_1_2.horizontalHeaderItem(7)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        self.pushButton_4_1_listele.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131tlar\u0131\n"
"Listele", None))
        self.pushButton_4_1_temizle.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131tlar\u0131\n"
"Temizle", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_4_1), QCoreApplication.translate("MainWindow", u"T\u00fcre G\u00f6re Listele", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"Listelenecek Kay\u0131t ", None))
        ___qtablewidgetitem17 = self.tableWidget_4_2_1.horizontalHeaderItem(0)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem18 = self.tableWidget_4_2_2.horizontalHeaderItem(0)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem19 = self.tableWidget_4_2_2.horizontalHeaderItem(1)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem20 = self.tableWidget_4_2_2.horizontalHeaderItem(2)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem21 = self.tableWidget_4_2_2.horizontalHeaderItem(3)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem22 = self.tableWidget_4_2_2.horizontalHeaderItem(4)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem23 = self.tableWidget_4_2_2.horizontalHeaderItem(5)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem24 = self.tableWidget_4_2_2.horizontalHeaderItem(6)
        ___qtablewidgetitem24.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem25 = self.tableWidget_4_2_2.horizontalHeaderItem(7)
        ___qtablewidgetitem25.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        self.pushButton_4_2_listele.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131tlar\u0131\n"
"Listele", None))
        self.pushButton_4_2_temizle.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131tlar\u0131\n"
"Temizle", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_4_2), QCoreApplication.translate("MainWindow", u"Yazara G\u00f6re Listeleme", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"Listelenecek Kay\u0131t ", None))
        ___qtablewidgetitem26 = self.tableWidget_4_3_1.horizontalHeaderItem(0)
        ___qtablewidgetitem26.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem27 = self.tableWidget_4_3_2.horizontalHeaderItem(0)
        ___qtablewidgetitem27.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem28 = self.tableWidget_4_3_2.horizontalHeaderItem(1)
        ___qtablewidgetitem28.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem29 = self.tableWidget_4_3_2.horizontalHeaderItem(2)
        ___qtablewidgetitem29.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem30 = self.tableWidget_4_3_2.horizontalHeaderItem(3)
        ___qtablewidgetitem30.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem31 = self.tableWidget_4_3_2.horizontalHeaderItem(4)
        ___qtablewidgetitem31.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem32 = self.tableWidget_4_3_2.horizontalHeaderItem(5)
        ___qtablewidgetitem32.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem33 = self.tableWidget_4_3_2.horizontalHeaderItem(6)
        ___qtablewidgetitem33.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem34 = self.tableWidget_4_3_2.horizontalHeaderItem(7)
        ___qtablewidgetitem34.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        self.pushButton_4_3_listele.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131tlar\u0131\n"
"Listele", None))
        self.pushButton_4_3_temizle.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131tlar\u0131\n"
"Temizle", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_4_3), QCoreApplication.translate("MainWindow", u"Yay\u0131nevine G\u00f6re Listeleme", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"Listelenecek Kay\u0131t ", None))
        ___qtablewidgetitem35 = self.tableWidget_4_4_1.horizontalHeaderItem(0)
        ___qtablewidgetitem35.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem36 = self.tableWidget_4_4_2.horizontalHeaderItem(0)
        ___qtablewidgetitem36.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem37 = self.tableWidget_4_4_2.horizontalHeaderItem(1)
        ___qtablewidgetitem37.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem38 = self.tableWidget_4_4_2.horizontalHeaderItem(2)
        ___qtablewidgetitem38.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem39 = self.tableWidget_4_4_2.horizontalHeaderItem(3)
        ___qtablewidgetitem39.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem40 = self.tableWidget_4_4_2.horizontalHeaderItem(4)
        ___qtablewidgetitem40.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem41 = self.tableWidget_4_4_2.horizontalHeaderItem(5)
        ___qtablewidgetitem41.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem42 = self.tableWidget_4_4_2.horizontalHeaderItem(6)
        ___qtablewidgetitem42.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem43 = self.tableWidget_4_4_2.horizontalHeaderItem(7)
        ___qtablewidgetitem43.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        self.pushButton_4_4_listele.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131tlar\u0131\n"
"Listele", None))
        self.pushButton_4_4_temizle.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131tlar\u0131\n"
"Temizle", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_4_4), QCoreApplication.translate("MainWindow", u"Y\u0131llara G\u00f6re Listeleme", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", u"Filtre", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"T\u00fcre G\u00f6re Liste", None))
        self.label_56.setText(QCoreApplication.translate("MainWindow", u"Yazarlara G\u00f6re Liste", None))
        self.label_58.setText(QCoreApplication.translate("MainWindow", u"Yay\u0131nevine G\u00f6re Liste", None))
        self.label_59.setText(QCoreApplication.translate("MainWindow", u"Y\u0131llara G\u00f6re Liste", None))
        ___qtablewidgetitem44 = self.tableWidget_5_1_1.horizontalHeaderItem(0)
        ___qtablewidgetitem44.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem45 = self.tableWidget_5_1_1.horizontalHeaderItem(1)
        ___qtablewidgetitem45.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem46 = self.tableWidget_5_1_2.horizontalHeaderItem(0)
        ___qtablewidgetitem46.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem47 = self.tableWidget_5_1_2.horizontalHeaderItem(1)
        ___qtablewidgetitem47.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem48 = self.tableWidget_5_1_3.horizontalHeaderItem(0)
        ___qtablewidgetitem48.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem49 = self.tableWidget_5_1_3.horizontalHeaderItem(1)
        ___qtablewidgetitem49.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem50 = self.tableWidget_5_1_4.horizontalHeaderItem(0)
        ___qtablewidgetitem50.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem51 = self.tableWidget_5_1_4.horizontalHeaderItem(1)
        ___qtablewidgetitem51.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        self.tabWidget_5.setTabText(self.tabWidget_5.indexOf(self.tab_5_1), QCoreApplication.translate("MainWindow", u"\u00c7izelgeler", None))
        self.tabWidget_5.setTabText(self.tabWidget_5.indexOf(self.tab_5_2), QCoreApplication.translate("MainWindow", u"Grafikler", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("MainWindow", u"\u0130statistik", None))
        self.pushButton_6_1_1_bul_kitap.setText(QCoreApplication.translate("MainWindow", u"Aranan Kayd\u0131\n"
"B u l", None))
        self.label_39.setText(QCoreApplication.translate("MainWindow", u"Kitap Ad\u0131", None))
        self.label_40.setText(QCoreApplication.translate("MainWindow", u"Yazar\u0131", None))
        self.label_41.setText(QCoreApplication.translate("MainWindow", u"\u00c7eviren", None))
        self.label_42.setText(QCoreApplication.translate("MainWindow", u"T\u00fcr\u00fc", None))
        self.label_43.setText(QCoreApplication.translate("MainWindow", u"Yay\u0131nevi", None))
        self.label_44.setText(QCoreApplication.translate("MainWindow", u"Y\u0131l\u0131", None))
        self.label_45.setText(QCoreApplication.translate("MainWindow", u"Sayfa", None))
        self.label_46.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131t No", None))
        self.pushButton_6_1_islemi_kaydet.setText(QCoreApplication.translate("MainWindow", u"\u0130\u015flemi\n"
"Kaydet", None))
        self.label_47.setText(QCoreApplication.translate("MainWindow", u"\u00d6d\u00fcn\u00e7 Verilecek  Kitap", None))
        self.pushButton_6_1_2_bul_kisi.setText(QCoreApplication.translate("MainWindow", u"Aranan Kayd\u0131\n"
"B u l", None))
        self.label_78.setText(QCoreApplication.translate("MainWindow", u"\u00d6d\u00fcn\u00e7 Alacak Ki\u015fi", None))
        self.label_94.setText(QCoreApplication.translate("MainWindow", u"Kullan\u0131c\u0131 Ad\u0131", None))
        self.label_87.setText(QCoreApplication.translate("MainWindow", u"Ad\u0131 Soyad\u0131", None))
        self.label_88.setText(QCoreApplication.translate("MainWindow", u"Telefon", None))
        self.label_89.setText(QCoreApplication.translate("MainWindow", u"Mail", None))
        self.label_90.setText(QCoreApplication.translate("MainWindow", u"Yetki", None))
        self.pushButton_6_1_1_bul_kitap_temizle.setText(QCoreApplication.translate("MainWindow", u"Kayd\u0131\n"
"Temizle", None))
        self.pushButton_6_1_2_bul_kisi_temizle.setText(QCoreApplication.translate("MainWindow", u"Kayd\u0131\n"
"Temizle", None))
        self.tabWidget_6.setTabText(self.tabWidget_6.indexOf(self.tab_6_1), QCoreApplication.translate("MainWindow", u"Verme Kayd\u0131", None))
        self.label_79.setText(QCoreApplication.translate("MainWindow", u"Teslim Edecek Ki\u015fi", None))
        self.pushButton_6_2_1_bul_kisi.setText(QCoreApplication.translate("MainWindow", u"Aranan Kayd\u0131\n"
"B u l", None))
        self.label_95.setText(QCoreApplication.translate("MainWindow", u"Kullan\u0131c\u0131 Ad\u0131", None))
        self.label_91.setText(QCoreApplication.translate("MainWindow", u"Ad\u0131 Soyad\u0131", None))
        self.label_92.setText(QCoreApplication.translate("MainWindow", u"Telefon", None))
        self.label_93.setText(QCoreApplication.translate("MainWindow", u"Mail", None))
        self.label_96.setText(QCoreApplication.translate("MainWindow", u"Yetki", None))
        self.pushButton_6_2_1_bul_kisi_temizle.setText(QCoreApplication.translate("MainWindow", u"Kayd\u0131\n"
"Temizle", None))
        self.label_48.setText(QCoreApplication.translate("MainWindow", u"Kitap Ad\u0131", None))
        self.label_49.setText(QCoreApplication.translate("MainWindow", u"Yazar\u0131", None))
        self.label_50.setText(QCoreApplication.translate("MainWindow", u"\u00c7eviren", None))
        self.label_51.setText(QCoreApplication.translate("MainWindow", u"T\u00fcr\u00fc", None))
        self.label_52.setText(QCoreApplication.translate("MainWindow", u"Yay\u0131nevi", None))
        self.label_53.setText(QCoreApplication.translate("MainWindow", u"Y\u0131l\u0131", None))
        self.label_54.setText(QCoreApplication.translate("MainWindow", u"Sayfa", None))
        self.label_55.setText(QCoreApplication.translate("MainWindow", u"Kay\u0131t No", None))
        self.label_57.setText(QCoreApplication.translate("MainWindow", u"Al\u0131nacak Kitap", None))
        self.pushButton_6_2_2_bul_kitap_temizle.setText(QCoreApplication.translate("MainWindow", u"Kayd\u0131\n"
"Temizle", None))
        self.pushButton_6_2_2_bul_kitap.setText(QCoreApplication.translate("MainWindow", u"Aranan Kayd\u0131\n"
"B u l", None))
        self.pushButton_6_2_islemi_kaydet.setText(QCoreApplication.translate("MainWindow", u"\u0130\u015flemi\n"
"Kaydet", None))
        self.tabWidget_6.setTabText(self.tabWidget_6.indexOf(self.tab_6_2), QCoreApplication.translate("MainWindow", u"Alma Kayd\u0131", None))
        self.pushButton_3_3_Sil_2.setText(QCoreApplication.translate("MainWindow", u"Kayd\u0131\n"
"S i l", None))
        self.pushButton_6_3_temizle.setText(QCoreApplication.translate("MainWindow", u"T e m i z l e", None))
        self.pushButton_6_3_listele.setText(QCoreApplication.translate("MainWindow", u"L i s t e l e", None))
        ___qtablewidgetitem52 = self.tableWidget_6_2.horizontalHeaderItem(0)
        ___qtablewidgetitem52.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem53 = self.tableWidget_6_2.horizontalHeaderItem(1)
        ___qtablewidgetitem53.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem54 = self.tableWidget_6_2.horizontalHeaderItem(2)
        ___qtablewidgetitem54.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem55 = self.tableWidget_6_2.horizontalHeaderItem(3)
        ___qtablewidgetitem55.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem56 = self.tableWidget_6_2.horizontalHeaderItem(4)
        ___qtablewidgetitem56.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem57 = self.tableWidget_6_2.horizontalHeaderItem(5)
        ___qtablewidgetitem57.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        ___qtablewidgetitem58 = self.tableWidget_6_2.horizontalHeaderItem(6)
        ___qtablewidgetitem58.setText(QCoreApplication.translate("MainWindow", u"New Column", None));
        self.tabWidget_6.setTabText(self.tabWidget_6.indexOf(self.tab_6_3), QCoreApplication.translate("MainWindow", u"D\u0131\u015fardaki  Kitaplar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), QCoreApplication.translate("MainWindow", u"Kitap Verme", None))
    # retranslateUi

