# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetimagegrabber.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WidgetImageGrabber(object):
    def setupUi(self, WidgetImageGrabber):
        WidgetImageGrabber.setObjectName("WidgetImageGrabber")
        WidgetImageGrabber.resize(512, 388)
        self.verticalLayout = QtWidgets.QVBoxLayout(WidgetImageGrabber)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(WidgetImageGrabber)
        self.tabWidget.setObjectName("tabWidget")
        self.tabImage = QtWidgets.QWidget()
        self.tabImage.setObjectName("tabImage")
        self.tabWidget.addTab(self.tabImage, "")
        self.tabFitsHeader = QtWidgets.QWidget()
        self.tabFitsHeader.setObjectName("tabFitsHeader")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tabFitsHeader)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tableFitsHeader = QtWidgets.QTableWidget(self.tabFitsHeader)
        self.tableFitsHeader.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableFitsHeader.setAlternatingRowColors(True)
        self.tableFitsHeader.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableFitsHeader.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableFitsHeader.setObjectName("tableFitsHeader")
        self.tableFitsHeader.setColumnCount(0)
        self.tableFitsHeader.setRowCount(0)
        self.tableFitsHeader.horizontalHeader().setStretchLastSection(True)
        self.tableFitsHeader.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.tableFitsHeader)
        self.tabWidget.addTab(self.tabFitsHeader, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkAutoUpdate = QtWidgets.QCheckBox(WidgetImageGrabber)
        self.checkAutoUpdate.setChecked(True)
        self.checkAutoUpdate.setObjectName("checkAutoUpdate")
        self.horizontalLayout.addWidget(self.checkAutoUpdate)
        spacerItem = QtWidgets.QSpacerItem(38, 18, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.checkAutoSave = QtWidgets.QCheckBox(WidgetImageGrabber)
        self.checkAutoSave.setObjectName("checkAutoSave")
        self.horizontalLayout.addWidget(self.checkAutoSave)
        self.textAutoSavePath = QtWidgets.QLineEdit(WidgetImageGrabber)
        self.textAutoSavePath.setEnabled(False)
        self.textAutoSavePath.setObjectName("textAutoSavePath")
        self.horizontalLayout.addWidget(self.textAutoSavePath)
        self.butAutoSave = QtWidgets.QToolButton(WidgetImageGrabber)
        self.butAutoSave.setObjectName("butAutoSave")
        self.horizontalLayout.addWidget(self.butAutoSave)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.butSaveTo = QtWidgets.QToolButton(WidgetImageGrabber)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/Crystal_Clear_device_floppy_unmount.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.butSaveTo.setIcon(icon)
        self.butSaveTo.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.butSaveTo.setObjectName("butSaveTo")
        self.horizontalLayout.addWidget(self.butSaveTo)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(WidgetImageGrabber)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(WidgetImageGrabber)

    def retranslateUi(self, WidgetImageGrabber):
        _translate = QtCore.QCoreApplication.translate
        WidgetImageGrabber.setWindowTitle(_translate("WidgetImageGrabber", "Form"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabImage), _translate("WidgetImageGrabber", "Image"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFitsHeader), _translate("WidgetImageGrabber", "FITS header"))
        self.checkAutoUpdate.setText(_translate("WidgetImageGrabber", "Auto-update"))
        self.checkAutoSave.setText(_translate("WidgetImageGrabber", "Auto-save:"))
        self.butAutoSave.setText(_translate("WidgetImageGrabber", "..."))
        self.butSaveTo.setText(_translate("WidgetImageGrabber", "Save to..."))
