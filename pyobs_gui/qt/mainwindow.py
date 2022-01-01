# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from . import resources_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1374, 916)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelAutonomousWarning = QLabel(self.centralwidget)
        self.labelAutonomousWarning.setObjectName("labelAutonomousWarning")
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(35, 38, 41, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush1)
        brush2 = QBrush(QColor(255, 0, 0, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush2)
        brush3 = QBrush(QColor(110, 113, 117, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush2)
        self.labelAutonomousWarning.setPalette(palette)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.labelAutonomousWarning.setFont(font)
        self.labelAutonomousWarning.setAutoFillBackground(True)
        self.labelAutonomousWarning.setFrameShape(QFrame.Box)
        self.labelAutonomousWarning.setFrameShadow(QFrame.Plain)
        self.labelAutonomousWarning.setLineWidth(2)
        self.labelAutonomousWarning.setAlignment(Qt.AlignCenter)
        self.labelAutonomousWarning.setMargin(0)

        self.verticalLayout.addWidget(self.labelAutonomousWarning)

        self.labelWeatherWarning = QLabel(self.centralwidget)
        self.labelWeatherWarning.setObjectName("labelWeatherWarning")
        palette1 = QPalette()
        palette1.setBrush(QPalette.Active, QPalette.WindowText, brush)
        palette1.setBrush(QPalette.Active, QPalette.Base, brush1)
        brush4 = QBrush(QColor(255, 85, 0, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Window, brush4)
        palette1.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.Base, brush1)
        palette1.setBrush(QPalette.Inactive, QPalette.Window, brush4)
        palette1.setBrush(QPalette.Disabled, QPalette.WindowText, brush3)
        palette1.setBrush(QPalette.Disabled, QPalette.Base, brush4)
        palette1.setBrush(QPalette.Disabled, QPalette.Window, brush4)
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
        self.splitterLog.setObjectName("splitterLog")
        self.splitterLog.setOrientation(Qt.Vertical)
        self.layoutWidget = QWidget(self.splitterLog)
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.listPages = QListWidget(self.layoutWidget)
        self.listPages.setObjectName("listPages")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listPages.sizePolicy().hasHeightForWidth())
        self.listPages.setSizePolicy(sizePolicy)
        self.listPages.setMinimumSize(QSize(100, 0))
        self.listPages.setMaximumSize(QSize(100, 16777215))
        self.listPages.setFrameShape(QFrame.NoFrame)
        self.listPages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listPages.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listPages.setProperty("showDropIndicator", False)
        self.listPages.setDragDropMode(QAbstractItemView.DragDrop)
        self.listPages.setDefaultDropAction(Qt.IgnoreAction)
        self.listPages.setIconSize(QSize(64, 64))
        self.listPages.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.listPages.setViewMode(QListView.IconMode)

        self.horizontalLayout.addWidget(self.listPages)

        self.splitterToolBox = QSplitter(self.layoutWidget)
        self.splitterToolBox.setObjectName("splitterToolBox")
        self.splitterToolBox.setOrientation(Qt.Horizontal)
        self.stackedWidget = QStackedWidget(self.splitterToolBox)
        self.stackedWidget.setObjectName("stackedWidget")
        self.splitterToolBox.addWidget(self.stackedWidget)

        self.horizontalLayout.addWidget(self.splitterToolBox)

        self.splitterLog.addWidget(self.layoutWidget)
        self.splitterClients = QSplitter(self.splitterLog)
        self.splitterClients.setObjectName("splitterClients")
        self.splitterClients.setOrientation(Qt.Horizontal)
        self.tableLog = QTableView(self.splitterClients)
        self.tableLog.setObjectName("tableLog")
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
        self.listClients.setObjectName("listClients")
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
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "pyobs GUI", None))
        self.labelAutonomousWarning.setText(
            QCoreApplication.translate("MainWindow", "!!! WARNING: autonomous module(s) active !!!", None)
        )
        self.labelWeatherWarning.setText(
            QCoreApplication.translate("MainWindow", "!!! WARNING: weather module disabled !!!", None)
        )

    # retranslateUi
