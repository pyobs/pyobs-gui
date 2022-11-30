# -*- coding: utf-8 -*-

# Form implementation generated from ..reading ui file 'filterwidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FilterWidget(object):
    def setupUi(self, FilterWidget):
        FilterWidget.setObjectName("FilterWidget")
        FilterWidget.resize(229, 128)
        self.verticalLayout = QtWidgets.QVBoxLayout(FilterWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(FilterWidget)
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

        self.retranslateUi(FilterWidget)
        QtCore.QMetaObject.connectSlotsByName(FilterWidget)

    def retranslateUi(self, FilterWidget):
        _translate = QtCore.QCoreApplication.translate
        FilterWidget.setWindowTitle(_translate("FilterWidget", "Form"))
        self.groupBox_2.setTitle(_translate("FilterWidget", "Filter"))
        self.label_9.setText(_translate("FilterWidget", "Filter:"))
        self.buttonSetFilter.setText(_translate("FilterWidget", "set..."))
        self.label_11.setText(_translate("FilterWidget", "Status:"))
from . import resources_rc
