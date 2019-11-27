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
        WidgetFilter.resize(328, 190)
        self.verticalLayout = QtWidgets.QVBoxLayout(WidgetFilter)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(WidgetFilter)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 2, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox_2)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 1, 0, 1, 1)
        self.labelCurFilter = QtWidgets.QLineEdit(self.groupBox_2)
        self.labelCurFilter.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurFilter.setReadOnly(True)
        self.labelCurFilter.setObjectName("labelCurFilter")
        self.gridLayout_2.addWidget(self.labelCurFilter, 1, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox_2)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 4, 0, 1, 1)
        self.comboFilter = QtWidgets.QComboBox(self.groupBox_2)
        self.comboFilter.setObjectName("comboFilter")
        self.gridLayout_2.addWidget(self.comboFilter, 2, 1, 1, 1)
        self.butSetFilter = QtWidgets.QPushButton(self.groupBox_2)
        self.butSetFilter.setObjectName("butSetFilter")
        self.gridLayout_2.addWidget(self.butSetFilter, 3, 1, 1, 1)
        self.labelCurStatus = QtWidgets.QLineEdit(self.groupBox_2)
        self.labelCurStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurStatus.setReadOnly(True)
        self.labelCurStatus.setObjectName("labelCurStatus")
        self.gridLayout_2.addWidget(self.labelCurStatus, 4, 1, 1, 1)
        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 2)
        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(WidgetFilter)
        QtCore.QMetaObject.connectSlotsByName(WidgetFilter)

    def retranslateUi(self, WidgetFilter):
        _translate = QtCore.QCoreApplication.translate
        WidgetFilter.setWindowTitle(_translate("WidgetFilter", "Form"))
        self.groupBox_2.setTitle(_translate("WidgetFilter", "Filter"))
        self.label_10.setText(_translate("WidgetFilter", "Set:"))
        self.label_9.setText(_translate("WidgetFilter", "Current:"))
        self.label_11.setText(_translate("WidgetFilter", "Status:"))
        self.butSetFilter.setText(_translate("WidgetFilter", "Set filter"))
