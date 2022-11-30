# -*- coding: utf-8 -*-

# Form implementation generated from ..reading ui file 'compassmovewidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CompassMoveWidget(object):
    def setupUi(self, CompassMoveWidget):
        CompassMoveWidget.setObjectName("CompassMoveWidget")
        CompassMoveWidget.resize(276, 126)
        self.gridLayout = QtWidgets.QGridLayout(CompassMoveWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonOffsetNorth = QtWidgets.QPushButton(CompassMoveWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/arrow-alt-circle-up-solid.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonOffsetNorth.setIcon(icon)
        self.buttonOffsetNorth.setObjectName("buttonOffsetNorth")
        self.gridLayout.addWidget(self.buttonOffsetNorth, 0, 1, 1, 1)
        self.buttonOffsetEast = QtWidgets.QPushButton(CompassMoveWidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/resources/arrow-alt-circle-left-solid.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonOffsetEast.setIcon(icon1)
        self.buttonOffsetEast.setObjectName("buttonOffsetEast")
        self.gridLayout.addWidget(self.buttonOffsetEast, 1, 0, 1, 1)
        self.spinOffset = QtWidgets.QSpinBox(CompassMoveWidget)
        self.spinOffset.setPrefix("")
        self.spinOffset.setMaximum(999)
        self.spinOffset.setSingleStep(10)
        self.spinOffset.setProperty("value", 30)
        self.spinOffset.setObjectName("spinOffset")
        self.gridLayout.addWidget(self.spinOffset, 1, 1, 1, 1)
        self.buttonOffsetWest = QtWidgets.QPushButton(CompassMoveWidget)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/resources/arrow-alt-circle-right-solid.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonOffsetWest.setIcon(icon2)
        self.buttonOffsetWest.setObjectName("buttonOffsetWest")
        self.gridLayout.addWidget(self.buttonOffsetWest, 1, 2, 1, 1)
        self.buttonOffsetSouth = QtWidgets.QPushButton(CompassMoveWidget)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/resources/arrow-alt-circle-down-solid.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonOffsetSouth.setIcon(icon3)
        self.buttonOffsetSouth.setObjectName("buttonOffsetSouth")
        self.gridLayout.addWidget(self.buttonOffsetSouth, 2, 1, 1, 1)

        self.retranslateUi(CompassMoveWidget)
        QtCore.QMetaObject.connectSlotsByName(CompassMoveWidget)

    def retranslateUi(self, CompassMoveWidget):
        _translate = QtCore.QCoreApplication.translate
        CompassMoveWidget.setWindowTitle(_translate("CompassMoveWidget", "Form"))
        self.buttonOffsetNorth.setText(_translate("CompassMoveWidget", "N"))
        self.buttonOffsetEast.setText(_translate("CompassMoveWidget", "E"))
        self.spinOffset.setSuffix(_translate("CompassMoveWidget", "\""))
        self.buttonOffsetWest.setText(_translate("CompassMoveWidget", "W"))
        self.buttonOffsetSouth.setText(_translate("CompassMoveWidget", "S"))
from . import resources_rc
