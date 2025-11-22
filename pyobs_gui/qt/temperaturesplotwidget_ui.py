# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'temperaturesplotwidget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QToolButton, QVBoxLayout, QWidget)

class Ui_TemperaturesPlotWidget(object):
    def setupUi(self, TemperaturesPlotWidget):
        if not TemperaturesPlotWidget.objectName():
            TemperaturesPlotWidget.setObjectName(u"TemperaturesPlotWidget")
        TemperaturesPlotWidget.resize(515, 293)
        self.verticalLayout = QVBoxLayout(TemperaturesPlotWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(TemperaturesPlotWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)

        self.verticalLayout.addWidget(self.frame)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(TemperaturesPlotWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.comboShow = QComboBox(TemperaturesPlotWidget)
        self.comboShow.setObjectName(u"comboShow")

        self.horizontalLayout.addWidget(self.comboShow)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.checkLogFile = QCheckBox(TemperaturesPlotWidget)
        self.checkLogFile.setObjectName(u"checkLogFile")

        self.horizontalLayout.addWidget(self.checkLogFile)

        self.lineLogFile = QLineEdit(TemperaturesPlotWidget)
        self.lineLogFile.setObjectName(u"lineLogFile")
        self.lineLogFile.setReadOnly(True)

        self.horizontalLayout.addWidget(self.lineLogFile)

        self.buttonPickFile = QToolButton(TemperaturesPlotWidget)
        self.buttonPickFile.setObjectName(u"buttonPickFile")

        self.horizontalLayout.addWidget(self.buttonPickFile)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(TemperaturesPlotWidget)

        QMetaObject.connectSlotsByName(TemperaturesPlotWidget)
    # setupUi

    def retranslateUi(self, TemperaturesPlotWidget):
        TemperaturesPlotWidget.setWindowTitle(QCoreApplication.translate("TemperaturesPlotWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("TemperaturesPlotWidget", u"Show:", None))
        self.checkLogFile.setText(QCoreApplication.translate("TemperaturesPlotWidget", u"Log file:", None))
        self.buttonPickFile.setText(QCoreApplication.translate("TemperaturesPlotWidget", u"...", None))
    # retranslateUi

