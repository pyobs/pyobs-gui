# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetfitsheaders.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WidgetFitsHeaders(object):
    def setupUi(self, WidgetFitsHeaders):
        WidgetFitsHeaders.setObjectName("WidgetFitsHeaders")
        WidgetFitsHeaders.resize(259, 168)
        self.horizontalLayout = QtWidgets.QHBoxLayout(WidgetFitsHeaders)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(WidgetFitsHeaders)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.textObject = QtWidgets.QLineEdit(self.groupBox)
        self.textObject.setObjectName("textObject")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.textObject)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.textProject = QtWidgets.QLineEdit(self.groupBox)
        self.textProject.setObjectName("textProject")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.textProject)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.textUser = QtWidgets.QLineEdit(self.groupBox)
        self.textUser.setObjectName("textUser")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.textUser)
        self.horizontalLayout.addWidget(self.groupBox)

        self.retranslateUi(WidgetFitsHeaders)
        QtCore.QMetaObject.connectSlotsByName(WidgetFitsHeaders)

    def retranslateUi(self, WidgetFitsHeaders):
        _translate = QtCore.QCoreApplication.translate
        WidgetFitsHeaders.setWindowTitle(_translate("WidgetFitsHeaders", "Form"))
        self.groupBox.setTitle(_translate("WidgetFitsHeaders", "FITS headers"))
        self.label.setText(_translate("WidgetFitsHeaders", "OBJECT:"))
        self.label_2.setText(_translate("WidgetFitsHeaders", "PROPID:"))
        self.label_3.setText(_translate("WidgetFitsHeaders", "USER:"))


