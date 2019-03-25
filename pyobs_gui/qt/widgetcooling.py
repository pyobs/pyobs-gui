# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetcooling.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WidgetCooling(object):
    def setupUi(self, WidgetCooling):
        WidgetCooling.setObjectName("WidgetCooling")
        WidgetCooling.resize(307, 180)
        self.verticalLayout = QtWidgets.QVBoxLayout(WidgetCooling)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(WidgetCooling)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.labelCurFilter = QtWidgets.QLineEdit(self.groupBox_2)
        self.labelCurFilter.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurFilter.setReadOnly(True)
        self.labelCurFilter.setObjectName("labelCurFilter")
        self.gridLayout_2.addWidget(self.labelCurFilter, 0, 1, 1, 1)
        self.buttonApply = QtWidgets.QPushButton(self.groupBox_2)
        self.buttonApply.setObjectName("buttonApply")
        self.gridLayout_2.addWidget(self.buttonApply, 3, 1, 1, 1)
        self.checkEnabled = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkEnabled.setObjectName("checkEnabled")
        self.gridLayout_2.addWidget(self.checkEnabled, 1, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox_2)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 0, 0, 1, 1)
        self.spinSetPoint = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.spinSetPoint.setMinimum(-50.0)
        self.spinSetPoint.setMaximum(50.0)
        self.spinSetPoint.setObjectName("spinSetPoint")
        self.gridLayout_2.addWidget(self.spinSetPoint, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)
        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 2)
        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(WidgetCooling)
        QtCore.QMetaObject.connectSlotsByName(WidgetCooling)

    def retranslateUi(self, WidgetCooling):
        _translate = QtCore.QCoreApplication.translate
        WidgetCooling.setWindowTitle(_translate("WidgetCooling", "Form"))
        self.groupBox_2.setTitle(_translate("WidgetCooling", "Cooling"))
        self.buttonApply.setText(_translate("WidgetCooling", "Apply"))
        self.checkEnabled.setText(_translate("WidgetCooling", "Enabled"))
        self.label_9.setText(_translate("WidgetCooling", "Status:"))
        self.spinSetPoint.setSuffix(_translate("WidgetCooling", " °C"))
        self.label.setText(_translate("WidgetCooling", "SetPoint:"))

