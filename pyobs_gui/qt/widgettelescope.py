# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgettelescope.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WidgetTelescope(object):
    def setupUi(self, WidgetTelescope):
        WidgetTelescope.setObjectName("WidgetTelescope")
        WidgetTelescope.resize(424, 333)
        self.horizontalLayout = QtWidgets.QHBoxLayout(WidgetTelescope)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(WidgetTelescope)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.labelCurRA = QtWidgets.QLineEdit(self.groupBox)
        self.labelCurRA.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurRA.setReadOnly(True)
        self.labelCurRA.setObjectName("labelCurRA")
        self.gridLayout.addWidget(self.labelCurRA, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.labelCurDec = QtWidgets.QLineEdit(self.groupBox)
        self.labelCurDec.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurDec.setReadOnly(True)
        self.labelCurDec.setObjectName("labelCurDec")
        self.gridLayout.addWidget(self.labelCurDec, 1, 1, 1, 1)
        self.labelCurAlt = QtWidgets.QLineEdit(self.groupBox)
        self.labelCurAlt.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurAlt.setReadOnly(True)
        self.labelCurAlt.setObjectName("labelCurAlt")
        self.gridLayout.addWidget(self.labelCurAlt, 2, 1, 1, 1)
        self.labelCurAz = QtWidgets.QLineEdit(self.groupBox)
        self.labelCurAz.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurAz.setReadOnly(True)
        self.labelCurAz.setObjectName("labelCurAz")
        self.gridLayout.addWidget(self.labelCurAz, 3, 1, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)
        self.verticalLayout.addWidget(self.groupBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)

        self.retranslateUi(WidgetTelescope)
        QtCore.QMetaObject.connectSlotsByName(WidgetTelescope)

    def retranslateUi(self, WidgetTelescope):
        _translate = QtCore.QCoreApplication.translate
        WidgetTelescope.setWindowTitle(_translate("WidgetTelescope", "Form"))
        self.groupBox.setTitle(_translate("WidgetTelescope", "Status:"))
        self.label_3.setText(_translate("WidgetTelescope", "Alt:"))
        self.label_2.setText(_translate("WidgetTelescope", "Dec:"))
        self.label.setText(_translate("WidgetTelescope", "RA:"))
        self.label_4.setText(_translate("WidgetTelescope", "Az:"))

