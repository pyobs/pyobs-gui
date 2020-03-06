# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetfilter.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WidgetFilter(object):
    def setupUi(self, WidgetFilter):
        WidgetFilter.setObjectName("WidgetFilter")
        WidgetFilter.resize(229, 126)
        self.verticalLayout = QtWidgets.QVBoxLayout(WidgetFilter)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(WidgetFilter)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName("formLayout")
        self.label_9 = QtWidgets.QLabel(self.groupBox_2)
        self.label_9.setObjectName("label_9")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.textFilter = QtWidgets.QLineEdit(self.groupBox_2)
        self.textFilter.setAlignment(QtCore.Qt.AlignCenter)
        self.textFilter.setReadOnly(True)
        self.textFilter.setObjectName("textFilter")
        self.horizontalLayout.addWidget(self.textFilter)
        self.buttonSetFilter = QtWidgets.QToolButton(self.groupBox_2)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/edit-solid.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonSetFilter.setIcon(icon)
        self.buttonSetFilter.setObjectName("buttonSetFilter")
        self.horizontalLayout.addWidget(self.buttonSetFilter)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.label_11 = QtWidgets.QLabel(self.groupBox_2)
        self.label_11.setObjectName("label_11")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.textStatus = QtWidgets.QLineEdit(self.groupBox_2)
        self.textStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.textStatus.setReadOnly(True)
        self.textStatus.setObjectName("textStatus")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.textStatus)
        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(WidgetFilter)
        QtCore.QMetaObject.connectSlotsByName(WidgetFilter)

    def retranslateUi(self, WidgetFilter):
        _translate = QtCore.QCoreApplication.translate
        WidgetFilter.setWindowTitle(_translate("WidgetFilter", "Form"))
        self.groupBox_2.setTitle(_translate("WidgetFilter", "Filter"))
        self.label_9.setText(_translate("WidgetFilter", "Filter:"))
        self.buttonSetFilter.setText(_translate("WidgetFilter", "set..."))
        self.label_11.setText(_translate("WidgetFilter", "Status:"))
from . import resources_rc
