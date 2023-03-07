# -*- coding: utf-8 -*-

# Form implementation generated from ..reading ui file 'eventswidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EventsWidget(object):
    def setupUi(self, EventsWidget):
        EventsWidget.setObjectName("EventsWidget")
        EventsWidget.resize(400, 275)
        self.verticalLayout = QtWidgets.QVBoxLayout(EventsWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableEvents = QtWidgets.QTableWidget(EventsWidget)
        self.tableEvents.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.tableEvents.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableEvents.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableEvents.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableEvents.setGridStyle(QtCore.Qt.NoPen)
        self.tableEvents.setRowCount(0)
        self.tableEvents.setColumnCount(4)
        self.tableEvents.setObjectName("tableEvents")
        self.tableEvents.horizontalHeader().setMinimumSectionSize(1)
        self.tableEvents.horizontalHeader().setSortIndicatorShown(False)
        self.tableEvents.horizontalHeader().setStretchLastSection(True)
        self.tableEvents.verticalHeader().setVisible(False)
        self.tableEvents.verticalHeader().setDefaultSectionSize(30)
        self.verticalLayout.addWidget(self.tableEvents)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.comboEvent = QtWidgets.QComboBox(EventsWidget)
        self.comboEvent.setObjectName("comboEvent")
        self.horizontalLayout.addWidget(self.comboEvent)
        self.buttonSend = QtWidgets.QPushButton(EventsWidget)
        self.buttonSend.setObjectName("buttonSend")
        self.horizontalLayout.addWidget(self.buttonSend)
        self.horizontalLayout.setStretch(0, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(EventsWidget)
        QtCore.QMetaObject.connectSlotsByName(EventsWidget)

    def retranslateUi(self, EventsWidget):
        _translate = QtCore.QCoreApplication.translate
        EventsWidget.setWindowTitle(_translate("EventsWidget", "Form"))
        self.tableEvents.setSortingEnabled(False)
        self.buttonSend.setText(_translate("EventsWidget", "Send event"))
