# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1045, 619)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitterLog = QtWidgets.QSplitter(self.centralwidget)
        self.splitterLog.setOrientation(QtCore.Qt.Vertical)
        self.splitterLog.setObjectName("splitterLog")
        self.layoutWidget = QtWidgets.QWidget(self.splitterLog)
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listPages = QtWidgets.QListWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listPages.sizePolicy().hasHeightForWidth())
        self.listPages.setSizePolicy(sizePolicy)
        self.listPages.setMaximumSize(QtCore.QSize(100, 16777215))
        self.listPages.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.listPages.setIconSize(QtCore.QSize(64, 64))
        self.listPages.setViewMode(QtWidgets.QListView.IconMode)
        self.listPages.setObjectName("listPages")
        self.horizontalLayout.addWidget(self.listPages)
        self.splitterToolBox = QtWidgets.QSplitter(self.layoutWidget)
        self.splitterToolBox.setOrientation(QtCore.Qt.Horizontal)
        self.splitterToolBox.setObjectName("splitterToolBox")
        self.stackedWidget = QtWidgets.QStackedWidget(self.splitterToolBox)
        self.stackedWidget.setObjectName("stackedWidget")
        self.horizontalLayout.addWidget(self.splitterToolBox)
        self.splitterClients = QtWidgets.QSplitter(self.splitterLog)
        self.splitterClients.setOrientation(QtCore.Qt.Horizontal)
        self.splitterClients.setObjectName("splitterClients")
        self.tableLog = QtWidgets.QTableView(self.splitterClients)
        self.tableLog.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.tableLog.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableLog.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableLog.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableLog.setGridStyle(QtCore.Qt.NoPen)
        self.tableLog.setSortingEnabled(False)
        self.tableLog.setObjectName("tableLog")
        self.tableLog.horizontalHeader().setVisible(False)
        self.tableLog.horizontalHeader().setStretchLastSection(True)
        self.tableLog.verticalHeader().setVisible(False)
        self.tableLog.verticalHeader().setDefaultSectionSize(20)
        self.tableLog.verticalHeader().setMinimumSectionSize(20)
        self.listClients = QtWidgets.QListWidget(self.splitterClients)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listClients.sizePolicy().hasHeightForWidth())
        self.listClients.setSizePolicy(sizePolicy)
        self.listClients.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listClients.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.listClients.setObjectName("listClients")
        self.verticalLayout.addWidget(self.splitterLog)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "pyobs GUI"))

from . import resources_rc
