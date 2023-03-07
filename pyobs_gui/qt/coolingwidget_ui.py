# -*- coding: utf-8 -*-

# Form implementation generated from ..reading ui file 'coolingwidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CoolingWidget(object):
    def setupUi(self, CoolingWidget):
        CoolingWidget.setObjectName("CoolingWidget")
        CoolingWidget.resize(210, 161)
        self.verticalLayout = QtWidgets.QVBoxLayout(CoolingWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(CoolingWidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_9 = QtWidgets.QLabel(self.groupBox_2)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 0, 0, 1, 1)
        self.labelStatus = QtWidgets.QLineEdit(self.groupBox_2)
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setReadOnly(True)
        self.labelStatus.setObjectName("labelStatus")
        self.gridLayout.addWidget(self.labelStatus, 0, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 1, 0, 1, 1)
        self.labelPower = QtWidgets.QLineEdit(self.groupBox_2)
        self.labelPower.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPower.setReadOnly(True)
        self.labelPower.setObjectName("labelPower")
        self.gridLayout.addWidget(self.labelPower, 1, 1, 1, 1)
        self.line = QtWidgets.QFrame(self.groupBox_2)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 2, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.spinSetPoint = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.spinSetPoint.setDecimals(1)
        self.spinSetPoint.setMinimum(-50.0)
        self.spinSetPoint.setMaximum(50.0)
        self.spinSetPoint.setObjectName("spinSetPoint")
        self.horizontalLayout.addWidget(self.spinSetPoint)
        self.buttonApply = QtWidgets.QToolButton(self.groupBox_2)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/arrow-alt-circle-right-solid.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonApply.setIcon(icon)
        self.buttonApply.setObjectName("buttonApply")
        self.horizontalLayout.addWidget(self.buttonApply)
        self.horizontalLayout.setStretch(0, 1)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 1, 1, 1)
        self.checkEnabled = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkEnabled.setObjectName("checkEnabled")
        self.gridLayout.addWidget(self.checkEnabled, 3, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(CoolingWidget)
        QtCore.QMetaObject.connectSlotsByName(CoolingWidget)

    def retranslateUi(self, CoolingWidget):
        _translate = QtCore.QCoreApplication.translate
        CoolingWidget.setWindowTitle(_translate("CoolingWidget", "Form"))
        self.groupBox_2.setTitle(_translate("CoolingWidget", "Cooling"))
        self.label_9.setText(_translate("CoolingWidget", "Set temp:"))
        self.label_10.setText(_translate("CoolingWidget", "Power:"))
        self.spinSetPoint.setSuffix(_translate("CoolingWidget", " °C"))
        self.buttonApply.setText(_translate("CoolingWidget", "..."))
        self.checkEnabled.setText(_translate("CoolingWidget", "Enable"))
from . import resources_rc
