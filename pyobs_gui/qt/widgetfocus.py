# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetfocus.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WidgetFocus(object):
    def setupUi(self, WidgetFocus):
        WidgetFocus.setObjectName("WidgetFocus")
        WidgetFocus.resize(310, 184)
        self.verticalLayout = QtWidgets.QVBoxLayout(WidgetFocus)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_5 = QtWidgets.QGroupBox(WidgetFocus)
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_11 = QtWidgets.QLabel(self.groupBox_5)
        self.label_11.setObjectName("label_11")
        self.gridLayout_6.addWidget(self.label_11, 3, 0, 1, 1)
        self.labelCurFocus = QtWidgets.QLineEdit(self.groupBox_5)
        self.labelCurFocus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurFocus.setReadOnly(True)
        self.labelCurFocus.setObjectName("labelCurFocus")
        self.gridLayout_6.addWidget(self.labelCurFocus, 1, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.groupBox_5)
        self.label_12.setObjectName("label_12")
        self.gridLayout_6.addWidget(self.label_12, 1, 0, 1, 1)
        self.butSetFocus = QtWidgets.QPushButton(self.groupBox_5)
        self.butSetFocus.setObjectName("butSetFocus")
        self.gridLayout_6.addWidget(self.butSetFocus, 4, 1, 1, 1)
        self.spinFocus = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.spinFocus.setObjectName("spinFocus")
        self.gridLayout_6.addWidget(self.spinFocus, 3, 1, 1, 1)
        self.labelCurStatus = QtWidgets.QLineEdit(self.groupBox_5)
        self.labelCurStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurStatus.setReadOnly(True)
        self.labelCurStatus.setObjectName("labelCurStatus")
        self.gridLayout_6.addWidget(self.labelCurStatus, 5, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.groupBox_5)
        self.label_13.setObjectName("label_13")
        self.gridLayout_6.addWidget(self.label_13, 5, 0, 1, 1)
        self.gridLayout_6.setColumnStretch(0, 1)
        self.gridLayout_6.setColumnStretch(1, 2)
        self.verticalLayout.addWidget(self.groupBox_5)

        self.retranslateUi(WidgetFocus)
        QtCore.QMetaObject.connectSlotsByName(WidgetFocus)

    def retranslateUi(self, WidgetFocus):
        _translate = QtCore.QCoreApplication.translate
        WidgetFocus.setWindowTitle(_translate("WidgetFocus", "Form"))
        self.groupBox_5.setTitle(_translate("WidgetFocus", "Focus"))
        self.label_11.setText(_translate("WidgetFocus", "Set:"))
        self.label_12.setText(_translate("WidgetFocus", "Current:"))
        self.butSetFocus.setText(_translate("WidgetFocus", "Set focus"))
        self.label_13.setText(_translate("WidgetFocus", "Status:"))
