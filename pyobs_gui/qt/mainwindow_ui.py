# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QListView, QListWidget,
    QListWidgetItem, QMainWindow, QSizePolicy, QSplitter,
    QStackedWidget, QTableView, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1374, 916)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labelAutonomousWarning = QLabel(self.centralwidget)
        self.labelAutonomousWarning.setObjectName(u"labelAutonomousWarning")
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        brush1 = QBrush(QColor(35, 38, 41, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush1)
        brush2 = QBrush(QColor(255, 0, 0, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush2)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush2)
        brush3 = QBrush(QColor(110, 113, 117, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush3)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush2)
        self.labelAutonomousWarning.setPalette(palette)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.labelAutonomousWarning.setFont(font)
        self.labelAutonomousWarning.setAutoFillBackground(True)
        self.labelAutonomousWarning.setFrameShape(QFrame.Box)
        self.labelAutonomousWarning.setFrameShadow(QFrame.Plain)
        self.labelAutonomousWarning.setLineWidth(2)
        self.labelAutonomousWarning.setAlignment(Qt.AlignCenter)
        self.labelAutonomousWarning.setMargin(0)

        self.verticalLayout.addWidget(self.labelAutonomousWarning)

        self.labelWeatherWarning = QLabel(self.centralwidget)
        self.labelWeatherWarning.setObjectName(u"labelWeatherWarning")
        palette1 = QPalette()
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush1)
        brush4 = QBrush(QColor(255, 85, 0, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush4)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush4)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush3)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush4)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush4)
        self.labelWeatherWarning.setPalette(palette1)
        self.labelWeatherWarning.setFont(font)
        self.labelWeatherWarning.setAutoFillBackground(True)
        self.labelWeatherWarning.setFrameShape(QFrame.Box)
        self.labelWeatherWarning.setFrameShadow(QFrame.Plain)
        self.labelWeatherWarning.setLineWidth(2)
        self.labelWeatherWarning.setAlignment(Qt.AlignCenter)
        self.labelWeatherWarning.setMargin(0)

        self.verticalLayout.addWidget(self.labelWeatherWarning)

        self.splitterLog = QSplitter(self.centralwidget)
        self.splitterLog.setObjectName(u"splitterLog")
        self.splitterLog.setOrientation(Qt.Vertical)
        self.layoutWidget = QWidget(self.splitterLog)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.listPages = QListWidget(self.layoutWidget)
        self.listPages.setObjectName(u"listPages")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listPages.sizePolicy().hasHeightForWidth())
        self.listPages.setSizePolicy(sizePolicy)
        self.listPages.setMinimumSize(QSize(90, 90))
        self.listPages.setMaximumSize(QSize(90, 16777215))
        self.listPages.setFrameShape(QFrame.NoFrame)
        self.listPages.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.listPages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listPages.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listPages.setProperty(u"showDropIndicator", False)
        self.listPages.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.listPages.setDefaultDropAction(Qt.IgnoreAction)
        self.listPages.setIconSize(QSize(32, 32))
        self.listPages.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.listPages.setMovement(QListView.Static)
        self.listPages.setFlow(QListView.LeftToRight)
        self.listPages.setViewMode(QListView.IconMode)
        self.listPages.setSelectionRectVisible(False)

        self.horizontalLayout.addWidget(self.listPages)

        self.splitterToolBox = QSplitter(self.layoutWidget)
        self.splitterToolBox.setObjectName(u"splitterToolBox")
        self.splitterToolBox.setOrientation(Qt.Horizontal)
        self.stackedWidget = QStackedWidget(self.splitterToolBox)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.splitterToolBox.addWidget(self.stackedWidget)

        self.horizontalLayout.addWidget(self.splitterToolBox)

        self.splitterLog.addWidget(self.layoutWidget)
        self.splitterClients = QSplitter(self.splitterLog)
        self.splitterClients.setObjectName(u"splitterClients")
        self.splitterClients.setOrientation(Qt.Horizontal)
        self.tableLog = QTableView(self.splitterClients)
        self.tableLog.setObjectName(u"tableLog")
        self.tableLog.setFrameShape(QFrame.NoFrame)
        self.tableLog.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableLog.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableLog.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableLog.setGridStyle(Qt.NoPen)
        self.tableLog.setSortingEnabled(False)
        self.splitterClients.addWidget(self.tableLog)
        self.tableLog.horizontalHeader().setVisible(False)
        self.tableLog.horizontalHeader().setStretchLastSection(True)
        self.tableLog.verticalHeader().setVisible(False)
        self.tableLog.verticalHeader().setMinimumSectionSize(20)
        self.tableLog.verticalHeader().setDefaultSectionSize(20)
        self.listClients = QListWidget(self.splitterClients)
        self.listClients.setObjectName(u"listClients")
        sizePolicy.setHeightForWidth(self.listClients.sizePolicy().hasHeightForWidth())
        self.listClients.setSizePolicy(sizePolicy)
        self.listClients.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listClients.setSelectionMode(QAbstractItemView.NoSelection)
        self.splitterClients.addWidget(self.listClients)
        self.splitterLog.addWidget(self.splitterClients)

        self.verticalLayout.addWidget(self.splitterLog)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"pyobs GUI", None))
        self.labelAutonomousWarning.setText(QCoreApplication.translate("MainWindow", u"!!! WARNING: autonomous module(s) active !!!", None))
        self.labelWeatherWarning.setText(QCoreApplication.translate("MainWindow", u"!!! WARNING: weather module disabled !!!", None))
    # retranslateUi

