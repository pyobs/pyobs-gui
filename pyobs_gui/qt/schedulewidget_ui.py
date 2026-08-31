# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'schedulewidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QLineEdit, QPushButton, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_ScheduleWidget(object):
    def setupUi(self, ScheduleWidget):
        if not ScheduleWidget.objectName():
            ScheduleWidget.setObjectName(u"ScheduleWidget")
        ScheduleWidget.resize(500, 400)
        self.verticalLayout = QVBoxLayout(ScheduleWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.buttonStart = QPushButton(ScheduleWidget)
        self.buttonStart.setObjectName(u"buttonStart")

        self.horizontalLayout.addWidget(self.buttonStart)

        self.buttonStop = QPushButton(ScheduleWidget)
        self.buttonStop.setObjectName(u"buttonStop")

        self.horizontalLayout.addWidget(self.buttonStop)

        self.buttonReschedule = QPushButton(ScheduleWidget)
        self.buttonReschedule.setObjectName(u"buttonReschedule")

        self.horizontalLayout.addWidget(self.buttonReschedule)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.labelStatus = QLineEdit(ScheduleWidget)
        self.labelStatus.setObjectName(u"labelStatus")
        self.labelStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelStatus.setReadOnly(True)

        self.verticalLayout.addWidget(self.labelStatus)

        self.tableSchedule = QTableWidget(ScheduleWidget)
        if (self.tableSchedule.columnCount() < 6):
            self.tableSchedule.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableSchedule.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableSchedule.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableSchedule.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableSchedule.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableSchedule.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableSchedule.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.tableSchedule.setObjectName(u"tableSchedule")
        self.tableSchedule.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableSchedule.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableSchedule.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableSchedule.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.tableSchedule)

        QWidget.setTabOrder(self.buttonStart, self.buttonStop)
        QWidget.setTabOrder(self.buttonStop, self.buttonReschedule)

        self.retranslateUi(ScheduleWidget)

        QMetaObject.connectSlotsByName(ScheduleWidget)
    # setupUi

    def retranslateUi(self, ScheduleWidget):
        ScheduleWidget.setWindowTitle(QCoreApplication.translate("ScheduleWidget", u"Form", None))
        self.buttonStart.setText(QCoreApplication.translate("ScheduleWidget", u"Start", None))
        self.buttonStop.setText(QCoreApplication.translate("ScheduleWidget", u"Stop", None))
        self.buttonReschedule.setText(QCoreApplication.translate("ScheduleWidget", u"Re-schedule now", None))
        ___qtablewidgetitem = self.tableSchedule.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ScheduleWidget", u"Start", None))
        ___qtablewidgetitem1 = self.tableSchedule.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ScheduleWidget", u"End", None))
        ___qtablewidgetitem2 = self.tableSchedule.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ScheduleWidget", u"Task", None))
        ___qtablewidgetitem3 = self.tableSchedule.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ScheduleWidget", u"Target", None))
        ___qtablewidgetitem4 = self.tableSchedule.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("ScheduleWidget", u"State", None))
        ___qtablewidgetitem5 = self.tableSchedule.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("ScheduleWidget", u"Priority", None))
    # retranslateUi

