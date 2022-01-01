# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widgettemperatures.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_WidgetTemperatures(object):
    def setupUi(self, WidgetTemperatures):
        if not WidgetTemperatures.objectName():
            WidgetTemperatures.setObjectName("WidgetTemperatures")
        WidgetTemperatures.resize(307, 63)
        self.verticalLayout = QVBoxLayout(WidgetTemperatures)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QGroupBox(WidgetTemperatures)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(WidgetTemperatures)

        QMetaObject.connectSlotsByName(WidgetTemperatures)

    # setupUi

    def retranslateUi(self, WidgetTemperatures):
        WidgetTemperatures.setWindowTitle(QCoreApplication.translate("WidgetTemperatures", "Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("WidgetTemperatures", "Temperatures", None))

    # retranslateUi
