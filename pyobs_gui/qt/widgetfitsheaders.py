# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetfitsheaders.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WidgetFitsHeaders(object):
    def setupUi(self, WidgetFitsHeaders):
        WidgetFitsHeaders.setObjectName("WidgetFitsHeaders")
        WidgetFitsHeaders.resize(259, 427)
        self.horizontalLayout = QtWidgets.QHBoxLayout(WidgetFitsHeaders)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(WidgetFitsHeaders)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.checkAddHeaders = QtWidgets.QCheckBox(self.groupBox)
        self.checkAddHeaders.setObjectName("checkAddHeaders")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.checkAddHeaders)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.textObject = QtWidgets.QLineEdit(self.groupBox)
        self.textObject.setObjectName("textObject")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.textObject)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.textUser = QtWidgets.QLineEdit(self.groupBox)
        self.textUser.setObjectName("textUser")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.textUser)
        self.tableAdditionalHeaders = QtWidgets.QTableWidget(self.groupBox)
        self.tableAdditionalHeaders.setColumnCount(2)
        self.tableAdditionalHeaders.setObjectName("tableAdditionalHeaders")
        self.tableAdditionalHeaders.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableAdditionalHeaders.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableAdditionalHeaders.setHorizontalHeaderItem(1, item)
        self.tableAdditionalHeaders.horizontalHeader().setDefaultSectionSize(50)
        self.tableAdditionalHeaders.horizontalHeader().setStretchLastSection(True)
        self.tableAdditionalHeaders.verticalHeader().setVisible(False)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.tableAdditionalHeaders)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.buttonAddHeader = QtWidgets.QToolButton(self.groupBox)
        self.buttonAddHeader.setObjectName("buttonAddHeader")
        self.horizontalLayout_2.addWidget(self.buttonAddHeader)
        self.buttonDelHeader = QtWidgets.QToolButton(self.groupBox)
        self.buttonDelHeader.setObjectName("buttonDelHeader")
        self.horizontalLayout_2.addWidget(self.buttonDelHeader)
        self.formLayout.setLayout(4, QtWidgets.QFormLayout.SpanningRole, self.horizontalLayout_2)
        self.horizontalLayout.addWidget(self.groupBox)

        self.retranslateUi(WidgetFitsHeaders)
        QtCore.QMetaObject.connectSlotsByName(WidgetFitsHeaders)

    def retranslateUi(self, WidgetFitsHeaders):
        _translate = QtCore.QCoreApplication.translate
        WidgetFitsHeaders.setWindowTitle(_translate("WidgetFitsHeaders", "Form"))
        self.groupBox.setTitle(_translate("WidgetFitsHeaders", "FITS headers"))
        self.checkAddHeaders.setText(_translate("WidgetFitsHeaders", "Add headers"))
        self.label.setText(_translate("WidgetFitsHeaders", "OBJECT:"))
        self.label_3.setText(_translate("WidgetFitsHeaders", "USER:"))
        item = self.tableAdditionalHeaders.horizontalHeaderItem(0)
        item.setText(_translate("WidgetFitsHeaders", "Key"))
        item = self.tableAdditionalHeaders.horizontalHeaderItem(1)
        item.setText(_translate("WidgetFitsHeaders", "Value"))
        self.buttonAddHeader.setText(_translate("WidgetFitsHeaders", "+"))
        self.buttonDelHeader.setText(_translate("WidgetFitsHeaders", "-"))
