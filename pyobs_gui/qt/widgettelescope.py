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
        WidgetTelescope.resize(670, 506)
        self.horizontalLayout = QtWidgets.QHBoxLayout(WidgetTelescope)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupStatus = QtWidgets.QGroupBox(WidgetTelescope)
        self.groupStatus.setObjectName("groupStatus")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupStatus)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.labelStatus = QtWidgets.QLineEdit(self.groupStatus)
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setReadOnly(True)
        self.labelStatus.setObjectName("labelStatus")
        self.gridLayout_5.addWidget(self.labelStatus, 0, 0, 1, 2)
        self.butInit = QtWidgets.QPushButton(self.groupStatus)
        self.butInit.setObjectName("butInit")
        self.gridLayout_5.addWidget(self.butInit, 1, 0, 1, 1)
        self.butPark = QtWidgets.QPushButton(self.groupStatus)
        self.butPark.setObjectName("butPark")
        self.gridLayout_5.addWidget(self.butPark, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_5)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.groupStatus)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.labelCurRA = QtWidgets.QLineEdit(self.groupStatus)
        self.labelCurRA.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurRA.setReadOnly(True)
        self.labelCurRA.setObjectName("labelCurRA")
        self.gridLayout.addWidget(self.labelCurRA, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupStatus)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.labelCurDec = QtWidgets.QLineEdit(self.groupStatus)
        self.labelCurDec.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurDec.setReadOnly(True)
        self.labelCurDec.setObjectName("labelCurDec")
        self.gridLayout.addWidget(self.labelCurDec, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupStatus)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.labelCurAlt = QtWidgets.QLineEdit(self.groupStatus)
        self.labelCurAlt.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurAlt.setReadOnly(True)
        self.labelCurAlt.setObjectName("labelCurAlt")
        self.gridLayout.addWidget(self.labelCurAlt, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupStatus)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.labelCurAz = QtWidgets.QLineEdit(self.groupStatus)
        self.labelCurAz.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurAz.setReadOnly(True)
        self.labelCurAz.setObjectName("labelCurAz")
        self.gridLayout.addWidget(self.labelCurAz, 3, 1, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_4.addWidget(self.groupStatus)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox_3 = QtWidgets.QGroupBox(WidgetTelescope)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)
        self.spinMoveAlt = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.spinMoveAlt.setDecimals(3)
        self.spinMoveAlt.setMaximum(90.0)
        self.spinMoveAlt.setSingleStep(10.0)
        self.spinMoveAlt.setObjectName("spinMoveAlt")
        self.gridLayout_3.addWidget(self.spinMoveAlt, 0, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox_3)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 1, 0, 1, 1)
        self.spinMoveAz = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.spinMoveAz.setDecimals(3)
        self.spinMoveAz.setMaximum(360.0)
        self.spinMoveAz.setSingleStep(10.0)
        self.spinMoveAz.setObjectName("spinMoveAz")
        self.gridLayout_3.addWidget(self.spinMoveAz, 1, 1, 1, 1)
        self.butMove = QtWidgets.QPushButton(self.groupBox_3)
        self.butMove.setObjectName("butMove")
        self.gridLayout_3.addWidget(self.butMove, 2, 1, 1, 1)
        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 2)
        self.verticalLayout_3.addWidget(self.groupBox_3)
        self.groupBox_4 = QtWidgets.QGroupBox(WidgetTelescope)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_7 = QtWidgets.QLabel(self.groupBox_4)
        self.label_7.setObjectName("label_7")
        self.gridLayout_4.addWidget(self.label_7, 0, 0, 1, 1)
        self.textTrackRA = QtWidgets.QLineEdit(self.groupBox_4)
        self.textTrackRA.setObjectName("textTrackRA")
        self.gridLayout_4.addWidget(self.textTrackRA, 0, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox_4)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 1, 0, 1, 1)
        self.textTrackDec = QtWidgets.QLineEdit(self.groupBox_4)
        self.textTrackDec.setObjectName("textTrackDec")
        self.gridLayout_4.addWidget(self.textTrackDec, 1, 1, 1, 1)
        self.butTrack = QtWidgets.QPushButton(self.groupBox_4)
        self.butTrack.setObjectName("butTrack")
        self.gridLayout_4.addWidget(self.butTrack, 2, 1, 1, 1)
        self.gridLayout_4.setColumnStretch(0, 1)
        self.gridLayout_4.setColumnStretch(1, 2)
        self.verticalLayout_3.addWidget(self.groupBox_4)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_2 = QtWidgets.QGroupBox(WidgetTelescope)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.comboFilter = QtWidgets.QComboBox(self.groupBox_2)
        self.comboFilter.setObjectName("comboFilter")
        self.gridLayout_2.addWidget(self.comboFilter, 1, 1, 1, 1)
        self.labelCurFilter = QtWidgets.QLineEdit(self.groupBox_2)
        self.labelCurFilter.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurFilter.setReadOnly(True)
        self.labelCurFilter.setObjectName("labelCurFilter")
        self.gridLayout_2.addWidget(self.labelCurFilter, 0, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 1, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox_2)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 0, 0, 1, 1)
        self.butSetFilter = QtWidgets.QPushButton(self.groupBox_2)
        self.butSetFilter.setObjectName("butSetFilter")
        self.gridLayout_2.addWidget(self.butSetFilter, 2, 1, 1, 1)
        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 2)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.groupBox_5 = QtWidgets.QGroupBox(WidgetTelescope)
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.labelCurFocus = QtWidgets.QLineEdit(self.groupBox_5)
        self.labelCurFocus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurFocus.setReadOnly(True)
        self.labelCurFocus.setObjectName("labelCurFocus")
        self.gridLayout_6.addWidget(self.labelCurFocus, 0, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox_5)
        self.label_11.setObjectName("label_11")
        self.gridLayout_6.addWidget(self.label_11, 1, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.groupBox_5)
        self.label_12.setObjectName("label_12")
        self.gridLayout_6.addWidget(self.label_12, 0, 0, 1, 1)
        self.butSetFocus = QtWidgets.QPushButton(self.groupBox_5)
        self.butSetFocus.setObjectName("butSetFocus")
        self.gridLayout_6.addWidget(self.butSetFocus, 2, 1, 1, 1)
        self.spinFocus = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.spinFocus.setObjectName("spinFocus")
        self.gridLayout_6.addWidget(self.spinFocus, 1, 1, 1, 1)
        self.gridLayout_6.setColumnStretch(0, 1)
        self.gridLayout_6.setColumnStretch(1, 2)
        self.verticalLayout_2.addWidget(self.groupBox_5)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)

        self.retranslateUi(WidgetTelescope)
        QtCore.QMetaObject.connectSlotsByName(WidgetTelescope)

    def retranslateUi(self, WidgetTelescope):
        _translate = QtCore.QCoreApplication.translate
        WidgetTelescope.setWindowTitle(_translate("WidgetTelescope", "Form"))
        self.groupStatus.setTitle(_translate("WidgetTelescope", "Status"))
        self.butInit.setText(_translate("WidgetTelescope", "Init"))
        self.butPark.setText(_translate("WidgetTelescope", "Park"))
        self.label.setText(_translate("WidgetTelescope", "RA:"))
        self.label_2.setText(_translate("WidgetTelescope", "Dec:"))
        self.label_3.setText(_translate("WidgetTelescope", "Alt:"))
        self.label_4.setText(_translate("WidgetTelescope", "Az:"))
        self.groupBox_3.setTitle(_translate("WidgetTelescope", "Move Alt/Az"))
        self.label_5.setText(_translate("WidgetTelescope", "Alt:"))
        self.spinMoveAlt.setSuffix(_translate("WidgetTelescope", "°"))
        self.label_6.setText(_translate("WidgetTelescope", "Az:"))
        self.spinMoveAz.setSuffix(_translate("WidgetTelescope", "°"))
        self.butMove.setText(_translate("WidgetTelescope", "Move"))
        self.groupBox_4.setTitle(_translate("WidgetTelescope", "Track RA/Dec"))
        self.label_7.setText(_translate("WidgetTelescope", "RA:"))
        self.label_8.setText(_translate("WidgetTelescope", "Dec:"))
        self.butTrack.setText(_translate("WidgetTelescope", "Track"))
        self.groupBox_2.setTitle(_translate("WidgetTelescope", "Filter"))
        self.label_10.setText(_translate("WidgetTelescope", "Set:"))
        self.label_9.setText(_translate("WidgetTelescope", "Current:"))
        self.butSetFilter.setText(_translate("WidgetTelescope", "Set filter"))
        self.groupBox_5.setTitle(_translate("WidgetTelescope", "Focus"))
        self.label_11.setText(_translate("WidgetTelescope", "Set:"))
        self.label_12.setText(_translate("WidgetTelescope", "Current:"))
        self.butSetFocus.setText(_translate("WidgetTelescope", "Set focus"))
