# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widgetevents.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_WidgetEvents(object):
    def setupUi(self, WidgetEvents):
        if not WidgetEvents.objectName():
            WidgetEvents.setObjectName("WidgetEvents")
        WidgetEvents.resize(400, 275)
        self.verticalLayout = QVBoxLayout(WidgetEvents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableEvents = QTableWidget(WidgetEvents)
        if self.tableEvents.columnCount() < 4:
            self.tableEvents.setColumnCount(4)
        self.tableEvents.setObjectName("tableEvents")
        self.tableEvents.setFrameShape(QFrame.NoFrame)
        self.tableEvents.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableEvents.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableEvents.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableEvents.setGridStyle(Qt.NoPen)
        self.tableEvents.setSortingEnabled(False)
        self.tableEvents.setRowCount(0)
        self.tableEvents.setColumnCount(4)
        self.tableEvents.horizontalHeader().setMinimumSectionSize(1)
        self.tableEvents.horizontalHeader().setProperty("showSortIndicator", False)
        self.tableEvents.horizontalHeader().setStretchLastSection(True)
        self.tableEvents.verticalHeader().setVisible(False)
        self.tableEvents.verticalHeader().setDefaultSectionSize(30)

        self.verticalLayout.addWidget(self.tableEvents)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.comboEvent = QComboBox(WidgetEvents)
        self.comboEvent.setObjectName("comboEvent")

        self.horizontalLayout.addWidget(self.comboEvent)

        self.buttonSend = QPushButton(WidgetEvents)
        self.buttonSend.setObjectName("buttonSend")

        self.horizontalLayout.addWidget(self.buttonSend)

        self.horizontalLayout.setStretch(0, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(WidgetEvents)

        QMetaObject.connectSlotsByName(WidgetEvents)

    # setupUi

    def retranslateUi(self, WidgetEvents):
        WidgetEvents.setWindowTitle(QCoreApplication.translate("WidgetEvents", "Form", None))
        self.buttonSend.setText(QCoreApplication.translate("WidgetEvents", "Send event", None))

    # retranslateUi
