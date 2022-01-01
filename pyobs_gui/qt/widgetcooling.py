# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widgetcooling.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_WidgetCooling(object):
    def setupUi(self, WidgetCooling):
        if not WidgetCooling.objectName():
            WidgetCooling.setObjectName("WidgetCooling")
        WidgetCooling.resize(307, 218)
        self.verticalLayout = QVBoxLayout(WidgetCooling)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox_2 = QGroupBox(WidgetCooling)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.labelStatus = QLineEdit(self.groupBox_2)
        self.labelStatus.setObjectName("labelStatus")
        self.labelStatus.setAlignment(Qt.AlignCenter)
        self.labelStatus.setReadOnly(True)

        self.gridLayout_2.addWidget(self.labelStatus, 0, 1, 1, 1)

        self.buttonApply = QPushButton(self.groupBox_2)
        self.buttonApply.setObjectName("buttonApply")

        self.gridLayout_2.addWidget(self.buttonApply, 4, 1, 1, 1)

        self.checkEnabled = QCheckBox(self.groupBox_2)
        self.checkEnabled.setObjectName("checkEnabled")

        self.gridLayout_2.addWidget(self.checkEnabled, 2, 1, 1, 1)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName("label_9")

        self.gridLayout_2.addWidget(self.label_9, 0, 0, 1, 1)

        self.spinSetPoint = QDoubleSpinBox(self.groupBox_2)
        self.spinSetPoint.setObjectName("spinSetPoint")
        self.spinSetPoint.setMinimum(-50.000000000000000)
        self.spinSetPoint.setMaximum(50.000000000000000)

        self.gridLayout_2.addWidget(self.spinSetPoint, 3, 1, 1, 1)

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName("label")

        self.gridLayout_2.addWidget(self.label, 3, 0, 1, 1)

        self.labelPower = QLineEdit(self.groupBox_2)
        self.labelPower.setObjectName("labelPower")
        self.labelPower.setAlignment(Qt.AlignCenter)
        self.labelPower.setReadOnly(True)

        self.gridLayout_2.addWidget(self.labelPower, 1, 1, 1, 1)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName("label_10")

        self.gridLayout_2.addWidget(self.label_10, 1, 0, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 2)

        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(WidgetCooling)

        QMetaObject.connectSlotsByName(WidgetCooling)

    # setupUi

    def retranslateUi(self, WidgetCooling):
        WidgetCooling.setWindowTitle(QCoreApplication.translate("WidgetCooling", "Form", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("WidgetCooling", "Cooling", None))
        self.buttonApply.setText(QCoreApplication.translate("WidgetCooling", "Apply", None))
        self.checkEnabled.setText(QCoreApplication.translate("WidgetCooling", "Enabled", None))
        self.label_9.setText(QCoreApplication.translate("WidgetCooling", "Status:", None))
        self.spinSetPoint.setSuffix(QCoreApplication.translate("WidgetCooling", " \u00b0C", None))
        self.label.setText(QCoreApplication.translate("WidgetCooling", "SetPoint:", None))
        self.label_10.setText(QCoreApplication.translate("WidgetCooling", "Power:", None))

    # retranslateUi
