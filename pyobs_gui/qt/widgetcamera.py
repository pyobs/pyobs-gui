# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetcamera.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WidgetCamera(object):
    def setupUi(self, WidgetCamera):
        WidgetCamera.setObjectName("WidgetCamera")
        WidgetCamera.resize(1000, 764)
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
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 237, 748))
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
        self.groupWindowing.setTitle("")
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
        self.groupImageFormat = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupImageFormat.setTitle("")
        self.groupImageFormat.setObjectName("groupImageFormat")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupImageFormat)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_10 = QtWidgets.QLabel(self.groupImageFormat)
        self.label_10.setObjectName("label_10")
        self.gridLayout_6.addWidget(self.label_10, 0, 0, 1, 1)
        self.comboImageFormat = QtWidgets.QComboBox(self.groupImageFormat)
        self.comboImageFormat.setObjectName("comboImageFormat")
        self.gridLayout_6.addWidget(self.comboImageFormat, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupImageFormat)
        self.groupBinning = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBinning.setTitle("")
        self.groupBinning.setObjectName("groupBinning")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBinning)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_5 = QtWidgets.QLabel(self.groupBinning)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)
        self.comboBinning = QtWidgets.QComboBox(self.groupBinning)
        self.comboBinning.setObjectName("comboBinning")
        self.gridLayout_3.addWidget(self.comboBinning, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBinning)
        self.groupGain = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupGain.setTitle("")
        self.groupGain.setObjectName("groupGain")
        self.gridLayout = QtWidgets.QGridLayout(self.groupGain)
        self.gridLayout.setObjectName("gridLayout")
        self.label_11 = QtWidgets.QLabel(self.groupGain)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 0, 0, 1, 1)
        self.spinGain = QtWidgets.QDoubleSpinBox(self.groupGain)
        self.spinGain.setObjectName("spinGain")
        self.gridLayout.addWidget(self.spinGain, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupGain)
        self.groupExpTime = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupExpTime.setTitle("")
        self.groupExpTime.setObjectName("groupExpTime")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupExpTime)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_12 = QtWidgets.QLabel(self.groupExpTime)
        self.label_12.setObjectName("label_12")
        self.gridLayout_5.addWidget(self.label_12, 0, 0, 1, 1)
        self.layoutExpTime = QtWidgets.QHBoxLayout()
        self.layoutExpTime.setObjectName("layoutExpTime")
        self.spinExpTime = QtWidgets.QDoubleSpinBox(self.groupExpTime)
        self.spinExpTime.setSuffix("")
        self.spinExpTime.setDecimals(3)
        self.spinExpTime.setMaximum(999.0)
        self.spinExpTime.setProperty("value", 1.0)
        self.spinExpTime.setObjectName("spinExpTime")
        self.layoutExpTime.addWidget(self.spinExpTime)
        self.comboExpTimeUnit = QtWidgets.QComboBox(self.groupExpTime)
        self.comboExpTimeUnit.setMinimumContentsLength(2)
        self.comboExpTimeUnit.setObjectName("comboExpTimeUnit")
        self.comboExpTimeUnit.addItem("")
        self.comboExpTimeUnit.addItem("")
        self.comboExpTimeUnit.addItem("")
        self.layoutExpTime.addWidget(self.comboExpTimeUnit)
        self.layoutExpTime.setStretch(0, 1)
        self.gridLayout_5.addLayout(self.layoutExpTime, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupExpTime)
        self.groupExposure = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupExposure.setTitle("")
        self.groupExposure.setObjectName("groupExposure")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupExposure)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.labelImageType = QtWidgets.QLabel(self.groupExposure)
        self.labelImageType.setObjectName("labelImageType")
        self.gridLayout_4.addWidget(self.labelImageType, 0, 0, 1, 1)
        self.spinCount = QtWidgets.QSpinBox(self.groupExposure)
        self.spinCount.setMinimum(1)
        self.spinCount.setMaximum(9999)
        self.spinCount.setObjectName("spinCount")
        self.gridLayout_4.addWidget(self.spinCount, 1, 1, 1, 1)
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
        self.label_8 = QtWidgets.QLabel(self.groupExposure)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 1, 0, 1, 1)
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
        self.checkBroadcast = QtWidgets.QCheckBox(self.groupExposure)
        self.checkBroadcast.setChecked(True)
        self.checkBroadcast.setObjectName("checkBroadcast")
        self.gridLayout_4.addWidget(self.checkBroadcast, 2, 1, 1, 1)
        self.comboImageType = QtWidgets.QComboBox(self.groupExposure)
        self.comboImageType.setObjectName("comboImageType")
        self.gridLayout_4.addWidget(self.comboImageType, 0, 1, 1, 1)
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
        self.frameImageGrabber = QtWidgets.QWidget(WidgetCamera)
        self.frameImageGrabber.setObjectName("frameImageGrabber")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frameImageGrabber)
        self.verticalLayout_2.setContentsMargins(-1, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2.addWidget(self.frameImageGrabber)
        self.widgetSidebar = QtWidgets.QWidget(WidgetCamera)
        self.widgetSidebar.setObjectName("widgetSidebar")
        self.horizontalLayout_2.addWidget(self.widgetSidebar)
        self.horizontalLayout_2.setStretch(1, 1)

        self.retranslateUi(WidgetCamera)
        QtCore.QMetaObject.connectSlotsByName(WidgetCamera)
        WidgetCamera.setTabOrder(self.scrollArea, self.spinWindowLeft)
        WidgetCamera.setTabOrder(self.spinWindowLeft, self.spinWindowTop)
        WidgetCamera.setTabOrder(self.spinWindowTop, self.spinWindowWidth)
        WidgetCamera.setTabOrder(self.spinWindowWidth, self.spinWindowHeight)
        WidgetCamera.setTabOrder(self.spinWindowHeight, self.butFullFrame)
        WidgetCamera.setTabOrder(self.butFullFrame, self.comboBinning)
        WidgetCamera.setTabOrder(self.comboBinning, self.comboImageFormat)
        WidgetCamera.setTabOrder(self.comboImageFormat, self.comboImageType)
        WidgetCamera.setTabOrder(self.comboImageType, self.spinCount)
        WidgetCamera.setTabOrder(self.spinCount, self.checkBroadcast)
        WidgetCamera.setTabOrder(self.checkBroadcast, self.butExpose)
        WidgetCamera.setTabOrder(self.butExpose, self.butAbort)

    def retranslateUi(self, WidgetCamera):
        _translate = QtCore.QCoreApplication.translate
        WidgetCamera.setWindowTitle(_translate("WidgetCamera", "Form"))
        self.label_2.setText(_translate("WidgetCamera", "Top:"))
        self.label_3.setText(_translate("WidgetCamera", "Width:"))
        self.label.setText(_translate("WidgetCamera", "Left:"))
        self.label_4.setText(_translate("WidgetCamera", "Height:"))
        self.butFullFrame.setText(_translate("WidgetCamera", "Full Frame"))
        self.label_10.setText(_translate("WidgetCamera", "Format:"))
        self.label_5.setText(_translate("WidgetCamera", "Binning:"))
        self.label_11.setText(_translate("WidgetCamera", "Gain:"))
        self.label_12.setText(_translate("WidgetCamera", "ExpTime:"))
        self.comboExpTimeUnit.setItemText(0, _translate("WidgetCamera", "s"))
        self.comboExpTimeUnit.setItemText(1, _translate("WidgetCamera", "ms"))
        self.comboExpTimeUnit.setItemText(2, _translate("WidgetCamera", "µs"))
        self.labelImageType.setText(_translate("WidgetCamera", "Type:"))
        self.butAbort.setText(_translate("WidgetCamera", "Abort"))
        self.label_8.setText(_translate("WidgetCamera", "Count:"))
        self.butExpose.setText(_translate("WidgetCamera", "Expose"))
        self.checkBroadcast.setText(_translate("WidgetCamera", "Broadcast"))
        self.labelStatus.setText(_translate("WidgetCamera", "IDLE"))
        self.labelExposuresLeft.setText(_translate("WidgetCamera", "IDLE"))


from . import resources_rc
