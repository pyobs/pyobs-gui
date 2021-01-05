# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetcamera.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WidgetCamera(object):
    def setupUi(self, WidgetCamera):
        WidgetCamera.setObjectName("WidgetCamera")
        WidgetCamera.resize(967, 657)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(WidgetCamera)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.scrollArea = QtWidgets.QScrollArea(WidgetCamera)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 183, 641))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupWindowing = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupWindowing.setObjectName("groupWindowing")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupWindowing)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.spinWindowWidth = QtWidgets.QSpinBox(self.groupWindowing)
        self.spinWindowWidth.setMinimum(1)
        self.spinWindowWidth.setMaximum(9999)
        self.spinWindowWidth.setObjectName("spinWindowWidth")
        self.gridLayout_2.addWidget(self.spinWindowWidth, 2, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupWindowing)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupWindowing)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.groupWindowing)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.spinWindowHeight = QtWidgets.QSpinBox(self.groupWindowing)
        self.spinWindowHeight.setMinimum(1)
        self.spinWindowHeight.setMaximum(9999)
        self.spinWindowHeight.setObjectName("spinWindowHeight")
        self.gridLayout_2.addWidget(self.spinWindowHeight, 3, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupWindowing)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)
        self.spinWindowLeft = QtWidgets.QSpinBox(self.groupWindowing)
        self.spinWindowLeft.setMaximum(9999)
        self.spinWindowLeft.setObjectName("spinWindowLeft")
        self.gridLayout_2.addWidget(self.spinWindowLeft, 0, 1, 1, 1)
        self.spinWindowTop = QtWidgets.QSpinBox(self.groupWindowing)
        self.spinWindowTop.setMaximum(9999)
        self.spinWindowTop.setObjectName("spinWindowTop")
        self.gridLayout_2.addWidget(self.spinWindowTop, 1, 1, 1, 1)
        self.butFullFrame = QtWidgets.QPushButton(self.groupWindowing)
        self.butFullFrame.setObjectName("butFullFrame")
        self.gridLayout_2.addWidget(self.butFullFrame, 4, 0, 1, 2)
        self.verticalLayout.addWidget(self.groupWindowing)
        self.groupBinning = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBinning.setObjectName("groupBinning")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBinning)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.spinBinningY = QtWidgets.QSpinBox(self.groupBinning)
        self.spinBinningY.setMinimum(1)
        self.spinBinningY.setMaximum(3)
        self.spinBinningY.setObjectName("spinBinningY")
        self.gridLayout_3.addWidget(self.spinBinningY, 1, 1, 1, 1)
        self.spinBinningX = QtWidgets.QSpinBox(self.groupBinning)
        self.spinBinningX.setMinimum(1)
        self.spinBinningX.setMaximum(3)
        self.spinBinningX.setObjectName("spinBinningX")
        self.gridLayout_3.addWidget(self.spinBinningX, 0, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBinning)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 1, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBinning)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBinning)
        self.groupExposure = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupExposure.setObjectName("groupExposure")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupExposure)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_7 = QtWidgets.QLabel(self.groupExposure)
        self.label_7.setObjectName("label_7")
        self.gridLayout_4.addWidget(self.label_7, 1, 0, 1, 1)
        self.comboImageType = QtWidgets.QComboBox(self.groupExposure)
        self.comboImageType.setObjectName("comboImageType")
        self.gridLayout_4.addWidget(self.comboImageType, 0, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupExposure)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 2, 0, 1, 1)
        self.spinCount = QtWidgets.QSpinBox(self.groupExposure)
        self.spinCount.setMinimum(1)
        self.spinCount.setMaximum(9999)
        self.spinCount.setObjectName("spinCount")
        self.gridLayout_4.addWidget(self.spinCount, 2, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupExposure)
        self.label_9.setObjectName("label_9")
        self.gridLayout_4.addWidget(self.label_9, 0, 0, 1, 1)
        self.butExpose = QtWidgets.QPushButton(self.groupExposure)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 127, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 106, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 42, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 56, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 42, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 127, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 106, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 42, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 56, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 42, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 42, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 127, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 106, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 42, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 56, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 42, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 42, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.butExpose.setPalette(palette)
        self.butExpose.setObjectName("butExpose")
        self.gridLayout_4.addWidget(self.butExpose, 3, 0, 1, 2)
        self.butAbort = QtWidgets.QPushButton(self.groupExposure)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(212, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(113, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(212, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(212, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(113, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(212, 127, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(212, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(113, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.butAbort.setPalette(palette)
        self.butAbort.setObjectName("butAbort")
        self.gridLayout_4.addWidget(self.butAbort, 4, 0, 1, 2)
        self.spinExpTime = QtWidgets.QDoubleSpinBox(self.groupExposure)
        self.spinExpTime.setMaximum(99999.0)
        self.spinExpTime.setProperty("value", 1.0)
        self.spinExpTime.setObjectName("spinExpTime")
        self.gridLayout_4.addWidget(self.spinExpTime, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupExposure)
        spacerItem = QtWidgets.QSpacerItem(20, 26, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.labelStatus = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setObjectName("labelStatus")
        self.verticalLayout.addWidget(self.labelStatus)
        self.progressExposure = QtWidgets.QProgressBar(self.scrollAreaWidgetContents)
        self.progressExposure.setProperty("value", 0)
        self.progressExposure.setTextVisible(True)
        self.progressExposure.setInvertedAppearance(False)
        self.progressExposure.setObjectName("progressExposure")
        self.verticalLayout.addWidget(self.progressExposure)
        self.labelExposuresLeft = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.labelExposuresLeft.setAlignment(QtCore.Qt.AlignCenter)
        self.labelExposuresLeft.setObjectName("labelExposuresLeft")
        self.verticalLayout.addWidget(self.labelExposuresLeft)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.addWidget(self.scrollArea)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(WidgetCamera)
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
        self.verticalLayout_3.addWidget(self.tabWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkAutoUpdate = QtWidgets.QCheckBox(WidgetCamera)
        self.checkAutoUpdate.setChecked(True)
        self.checkAutoUpdate.setObjectName("checkAutoUpdate")
        self.horizontalLayout.addWidget(self.checkAutoUpdate)
        spacerItem1 = QtWidgets.QSpacerItem(38, 18, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.checkAutoSave = QtWidgets.QCheckBox(WidgetCamera)
        self.checkAutoSave.setObjectName("checkAutoSave")
        self.horizontalLayout.addWidget(self.checkAutoSave)
        self.textAutoSavePath = QtWidgets.QLineEdit(WidgetCamera)
        self.textAutoSavePath.setEnabled(False)
        self.textAutoSavePath.setObjectName("textAutoSavePath")
        self.horizontalLayout.addWidget(self.textAutoSavePath)
        self.butAutoSave = QtWidgets.QToolButton(WidgetCamera)
        self.butAutoSave.setObjectName("butAutoSave")
        self.horizontalLayout.addWidget(self.butAutoSave)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.butSaveTo = QtWidgets.QToolButton(WidgetCamera)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/Crystal_Clear_device_floppy_unmount.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.butSaveTo.setIcon(icon)
        self.butSaveTo.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.butSaveTo.setObjectName("butSaveTo")
        self.horizontalLayout.addWidget(self.butSaveTo)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.widgetSidebar = QtWidgets.QWidget(WidgetCamera)
        self.widgetSidebar.setObjectName("widgetSidebar")
        self.horizontalLayout_2.addWidget(self.widgetSidebar)
        self.horizontalLayout_2.setStretch(1, 1)

        self.retranslateUi(WidgetCamera)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(WidgetCamera)
        WidgetCamera.setTabOrder(self.scrollArea, self.spinWindowLeft)
        WidgetCamera.setTabOrder(self.spinWindowLeft, self.spinWindowTop)
        WidgetCamera.setTabOrder(self.spinWindowTop, self.spinWindowWidth)
        WidgetCamera.setTabOrder(self.spinWindowWidth, self.spinWindowHeight)
        WidgetCamera.setTabOrder(self.spinWindowHeight, self.butFullFrame)
        WidgetCamera.setTabOrder(self.butFullFrame, self.spinBinningX)
        WidgetCamera.setTabOrder(self.spinBinningX, self.spinBinningY)
        WidgetCamera.setTabOrder(self.spinBinningY, self.comboImageType)
        WidgetCamera.setTabOrder(self.comboImageType, self.spinExpTime)
        WidgetCamera.setTabOrder(self.spinExpTime, self.spinCount)
        WidgetCamera.setTabOrder(self.spinCount, self.butExpose)
        WidgetCamera.setTabOrder(self.butExpose, self.butAbort)
        WidgetCamera.setTabOrder(self.butAbort, self.tabWidget)
        WidgetCamera.setTabOrder(self.tabWidget, self.checkAutoUpdate)
        WidgetCamera.setTabOrder(self.checkAutoUpdate, self.checkAutoSave)
        WidgetCamera.setTabOrder(self.checkAutoSave, self.textAutoSavePath)
        WidgetCamera.setTabOrder(self.textAutoSavePath, self.butAutoSave)
        WidgetCamera.setTabOrder(self.butAutoSave, self.butSaveTo)
        WidgetCamera.setTabOrder(self.butSaveTo, self.tableFitsHeader)

    def retranslateUi(self, WidgetCamera):
        _translate = QtCore.QCoreApplication.translate
        WidgetCamera.setWindowTitle(_translate("WidgetCamera", "Form"))
        self.groupWindowing.setTitle(_translate("WidgetCamera", "Window"))
        self.label_2.setText(_translate("WidgetCamera", "Top:"))
        self.label_3.setText(_translate("WidgetCamera", "Width:"))
        self.label.setText(_translate("WidgetCamera", "Left:"))
        self.label_4.setText(_translate("WidgetCamera", "Height:"))
        self.butFullFrame.setText(_translate("WidgetCamera", "Full Frame"))
        self.groupBinning.setTitle(_translate("WidgetCamera", "Binning:"))
        self.label_6.setText(_translate("WidgetCamera", "Y:"))
        self.label_5.setText(_translate("WidgetCamera", "X:"))
        self.groupExposure.setTitle(_translate("WidgetCamera", "Exposure"))
        self.label_7.setText(_translate("WidgetCamera", "ExpTime:"))
        self.label_8.setText(_translate("WidgetCamera", "Count:"))
        self.label_9.setText(_translate("WidgetCamera", "Type:"))
        self.butExpose.setText(_translate("WidgetCamera", "Expose"))
        self.butAbort.setText(_translate("WidgetCamera", "Abort"))
        self.spinExpTime.setSuffix(_translate("WidgetCamera", "s"))
        self.labelStatus.setText(_translate("WidgetCamera", "IDLE"))
        self.labelExposuresLeft.setText(_translate("WidgetCamera", "IDLE"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabImage), _translate("WidgetCamera", "Image"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFitsHeader), _translate("WidgetCamera", "FITS header"))
        self.checkAutoUpdate.setText(_translate("WidgetCamera", "Auto-update"))
        self.checkAutoSave.setText(_translate("WidgetCamera", "Auto-save:"))
        self.butAutoSave.setText(_translate("WidgetCamera", "..."))
        self.butSaveTo.setText(_translate("WidgetCamera", "Save to..."))
from . import resources_rc
