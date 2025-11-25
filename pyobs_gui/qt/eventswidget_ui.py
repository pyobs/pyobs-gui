# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'eventswidget.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFrame,
    QHBoxLayout, QHeaderView, QPushButton, QSizePolicy,
    QSpacerItem, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_EventsWidget(object):
    def setupUi(self, EventsWidget):
        if not EventsWidget.objectName():
            EventsWidget.setObjectName(u"EventsWidget")
        EventsWidget.resize(409, 278)
        self.verticalLayout = QVBoxLayout(EventsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tableEvents = QTableWidget(EventsWidget)
        if (self.tableEvents.columnCount() < 4):
            self.tableEvents.setColumnCount(4)
        self.tableEvents.setObjectName(u"tableEvents")
        self.tableEvents.setFrameShape(QFrame.Shape.NoFrame)
        self.tableEvents.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableEvents.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableEvents.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableEvents.setGridStyle(Qt.PenStyle.NoPen)
        self.tableEvents.setSortingEnabled(False)
        self.tableEvents.setRowCount(0)
        self.tableEvents.setColumnCount(4)
        self.tableEvents.horizontalHeader().setMinimumSectionSize(1)
        self.tableEvents.horizontalHeader().setProperty(u"showSortIndicator", False)
        self.tableEvents.horizontalHeader().setStretchLastSection(True)
        self.tableEvents.verticalHeader().setVisible(False)
        self.tableEvents.verticalHeader().setDefaultSectionSize(30)

        self.verticalLayout.addWidget(self.tableEvents)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.comboEvent = QComboBox(EventsWidget)
        self.comboEvent.setObjectName(u"comboEvent")

        self.horizontalLayout.addWidget(self.comboEvent)

        self.buttonSend = QPushButton(EventsWidget)
        self.buttonSend.setObjectName(u"buttonSend")

        self.horizontalLayout.addWidget(self.buttonSend)

        self.horizontalLayout.setStretch(0, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(EventsWidget)

        QMetaObject.connectSlotsByName(EventsWidget)
    # setupUi

    def retranslateUi(self, EventsWidget):
        EventsWidget.setWindowTitle(QCoreApplication.translate("EventsWidget", u"Form", None))
        self.buttonSend.setText(QCoreApplication.translate("EventsWidget", u"Send event", None))
    # retranslateUi

