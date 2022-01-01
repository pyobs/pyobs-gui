# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widgetcamera.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from . import resources_rc


class Ui_WidgetCamera(object):
    def setupUi(self, WidgetCamera):
        if not WidgetCamera.objectName():
            WidgetCamera.setObjectName("WidgetCamera")
        WidgetCamera.resize(1000, 764)
        self.horizontalLayout_2 = QHBoxLayout(WidgetCamera)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.scrollArea = QScrollArea(WidgetCamera)
        self.scrollArea.setObjectName("scrollArea")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 232, 748))
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy1)
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupWindowing = QGroupBox(self.scrollAreaWidgetContents)
        self.groupWindowing.setObjectName("groupWindowing")
        self.gridLayout_2 = QGridLayout(self.groupWindowing)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.spinWindowWidth = QSpinBox(self.groupWindowing)
        self.spinWindowWidth.setObjectName("spinWindowWidth")
        self.spinWindowWidth.setMinimum(1)
        self.spinWindowWidth.setMaximum(9999)

        self.gridLayout_2.addWidget(self.spinWindowWidth, 2, 1, 1, 1)

        self.label_2 = QLabel(self.groupWindowing)
        self.label_2.setObjectName("label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_3 = QLabel(self.groupWindowing)
        self.label_3.setObjectName("label_3")

        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)

        self.label = QLabel(self.groupWindowing)
        self.label.setObjectName("label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.spinWindowHeight = QSpinBox(self.groupWindowing)
        self.spinWindowHeight.setObjectName("spinWindowHeight")
        self.spinWindowHeight.setMinimum(1)
        self.spinWindowHeight.setMaximum(9999)

        self.gridLayout_2.addWidget(self.spinWindowHeight, 3, 1, 1, 1)

        self.label_4 = QLabel(self.groupWindowing)
        self.label_4.setObjectName("label_4")

        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)

        self.spinWindowLeft = QSpinBox(self.groupWindowing)
        self.spinWindowLeft.setObjectName("spinWindowLeft")
        self.spinWindowLeft.setMaximum(9999)

        self.gridLayout_2.addWidget(self.spinWindowLeft, 0, 1, 1, 1)

        self.spinWindowTop = QSpinBox(self.groupWindowing)
        self.spinWindowTop.setObjectName("spinWindowTop")
        self.spinWindowTop.setMaximum(9999)

        self.gridLayout_2.addWidget(self.spinWindowTop, 1, 1, 1, 1)

        self.butFullFrame = QPushButton(self.groupWindowing)
        self.butFullFrame.setObjectName("butFullFrame")

        self.gridLayout_2.addWidget(self.butFullFrame, 4, 0, 1, 2)

        self.verticalLayout.addWidget(self.groupWindowing)

        self.groupBinning = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBinning.setObjectName("groupBinning")
        self.gridLayout_3 = QGridLayout(self.groupBinning)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_5 = QLabel(self.groupBinning)
        self.label_5.setObjectName("label_5")

        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)

        self.comboBinning = QComboBox(self.groupBinning)
        self.comboBinning.setObjectName("comboBinning")

        self.gridLayout_3.addWidget(self.comboBinning, 0, 1, 1, 1)

        self.verticalLayout.addWidget(self.groupBinning)

        self.groupImageFormat = QGroupBox(self.scrollAreaWidgetContents)
        self.groupImageFormat.setObjectName("groupImageFormat")
        self.gridLayout_6 = QGridLayout(self.groupImageFormat)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_10 = QLabel(self.groupImageFormat)
        self.label_10.setObjectName("label_10")

        self.gridLayout_6.addWidget(self.label_10, 0, 0, 1, 1)

        self.comboImageFormat = QComboBox(self.groupImageFormat)
        self.comboImageFormat.setObjectName("comboImageFormat")

        self.gridLayout_6.addWidget(self.comboImageFormat, 0, 1, 1, 1)

        self.verticalLayout.addWidget(self.groupImageFormat)

        self.groupExposure = QGroupBox(self.scrollAreaWidgetContents)
        self.groupExposure.setObjectName("groupExposure")
        self.gridLayout_4 = QGridLayout(self.groupExposure)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_8 = QLabel(self.groupExposure)
        self.label_8.setObjectName("label_8")

        self.gridLayout_4.addWidget(self.label_8, 2, 0, 1, 1)

        self.labelImageType = QLabel(self.groupExposure)
        self.labelImageType.setObjectName("labelImageType")

        self.gridLayout_4.addWidget(self.labelImageType, 0, 0, 1, 1)

        self.butExpose = QPushButton(self.groupExposure)
        self.butExpose.setObjectName("butExpose")
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(0, 85, 0, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        brush2 = QBrush(QColor(0, 127, 0, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Light, brush2)
        brush3 = QBrush(QColor(0, 106, 0, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Midlight, brush3)
        brush4 = QBrush(QColor(0, 42, 0, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Dark, brush4)
        brush5 = QBrush(QColor(0, 56, 0, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        palette.setBrush(QPalette.Active, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        brush6 = QBrush(QColor(0, 0, 0, 255))
        brush6.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush6)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush6)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush4)
        brush7 = QBrush(QColor(255, 255, 220, 255))
        brush7.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush7)
        palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush6)
        brush8 = QBrush(QColor(255, 255, 255, 128))
        brush8.setStyle(Qt.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush8)
        # endif
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Light, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush6)
        brush9 = QBrush(QColor(255, 255, 255, 128))
        brush9.setStyle(Qt.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush9)
        # endif
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Light, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush6)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush7)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush6)
        brush10 = QBrush(QColor(255, 255, 255, 128))
        brush10.setStyle(Qt.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush10)
        # endif
        self.butExpose.setPalette(palette)

        self.gridLayout_4.addWidget(self.butExpose, 4, 0, 1, 2)

        self.labelExpTime = QLabel(self.groupExposure)
        self.labelExpTime.setObjectName("labelExpTime")

        self.gridLayout_4.addWidget(self.labelExpTime, 1, 0, 1, 1)

        self.checkBroadcast = QCheckBox(self.groupExposure)
        self.checkBroadcast.setObjectName("checkBroadcast")
        self.checkBroadcast.setChecked(True)

        self.gridLayout_4.addWidget(self.checkBroadcast, 3, 1, 1, 1)

        self.comboImageType = QComboBox(self.groupExposure)
        self.comboImageType.setObjectName("comboImageType")

        self.gridLayout_4.addWidget(self.comboImageType, 0, 1, 1, 1)

        self.butAbort = QPushButton(self.groupExposure)
        self.butAbort.setObjectName("butAbort")
        palette1 = QPalette()
        palette1.setBrush(QPalette.Active, QPalette.WindowText, brush6)
        brush11 = QBrush(QColor(170, 0, 0, 255))
        brush11.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Button, brush11)
        brush12 = QBrush(QColor(255, 0, 0, 255))
        brush12.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Light, brush12)
        brush13 = QBrush(QColor(212, 0, 0, 255))
        brush13.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Midlight, brush13)
        brush14 = QBrush(QColor(85, 0, 0, 255))
        brush14.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Dark, brush14)
        brush15 = QBrush(QColor(113, 0, 0, 255))
        brush15.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Mid, brush15)
        palette1.setBrush(QPalette.Active, QPalette.Text, brush6)
        palette1.setBrush(QPalette.Active, QPalette.BrightText, brush)
        palette1.setBrush(QPalette.Active, QPalette.ButtonText, brush6)
        palette1.setBrush(QPalette.Active, QPalette.Base, brush)
        palette1.setBrush(QPalette.Active, QPalette.Window, brush11)
        palette1.setBrush(QPalette.Active, QPalette.Shadow, brush6)
        brush16 = QBrush(QColor(212, 127, 127, 255))
        brush16.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.AlternateBase, brush16)
        palette1.setBrush(QPalette.Active, QPalette.ToolTipBase, brush7)
        palette1.setBrush(QPalette.Active, QPalette.ToolTipText, brush6)
        brush17 = QBrush(QColor(0, 0, 0, 128))
        brush17.setStyle(Qt.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Active, QPalette.PlaceholderText, brush17)
        # endif
        palette1.setBrush(QPalette.Inactive, QPalette.WindowText, brush6)
        palette1.setBrush(QPalette.Inactive, QPalette.Button, brush11)
        palette1.setBrush(QPalette.Inactive, QPalette.Light, brush12)
        palette1.setBrush(QPalette.Inactive, QPalette.Midlight, brush13)
        palette1.setBrush(QPalette.Inactive, QPalette.Dark, brush14)
        palette1.setBrush(QPalette.Inactive, QPalette.Mid, brush15)
        palette1.setBrush(QPalette.Inactive, QPalette.Text, brush6)
        palette1.setBrush(QPalette.Inactive, QPalette.BrightText, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.ButtonText, brush6)
        palette1.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.Window, brush11)
        palette1.setBrush(QPalette.Inactive, QPalette.Shadow, brush6)
        palette1.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush16)
        palette1.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush7)
        palette1.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush6)
        brush18 = QBrush(QColor(0, 0, 0, 128))
        brush18.setStyle(Qt.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush18)
        # endif
        palette1.setBrush(QPalette.Disabled, QPalette.WindowText, brush14)
        palette1.setBrush(QPalette.Disabled, QPalette.Button, brush11)
        palette1.setBrush(QPalette.Disabled, QPalette.Light, brush12)
        palette1.setBrush(QPalette.Disabled, QPalette.Midlight, brush13)
        palette1.setBrush(QPalette.Disabled, QPalette.Dark, brush14)
        palette1.setBrush(QPalette.Disabled, QPalette.Mid, brush15)
        palette1.setBrush(QPalette.Disabled, QPalette.Text, brush14)
        palette1.setBrush(QPalette.Disabled, QPalette.BrightText, brush)
        palette1.setBrush(QPalette.Disabled, QPalette.ButtonText, brush14)
        palette1.setBrush(QPalette.Disabled, QPalette.Base, brush11)
        palette1.setBrush(QPalette.Disabled, QPalette.Window, brush11)
        palette1.setBrush(QPalette.Disabled, QPalette.Shadow, brush6)
        palette1.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush11)
        palette1.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush7)
        palette1.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush6)
        brush19 = QBrush(QColor(0, 0, 0, 128))
        brush19.setStyle(Qt.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush19)
        # endif
        self.butAbort.setPalette(palette1)

        self.gridLayout_4.addWidget(self.butAbort, 5, 0, 1, 2)

        self.spinCount = QSpinBox(self.groupExposure)
        self.spinCount.setObjectName("spinCount")
        self.spinCount.setMinimum(1)
        self.spinCount.setMaximum(9999)

        self.gridLayout_4.addWidget(self.spinCount, 2, 1, 1, 1)

        self.layoutExpTime = QHBoxLayout()
        self.layoutExpTime.setObjectName("layoutExpTime")
        self.spinExpTime = QDoubleSpinBox(self.groupExposure)
        self.spinExpTime.setObjectName("spinExpTime")
        self.spinExpTime.setDecimals(3)
        self.spinExpTime.setMaximum(999.000000000000000)
        self.spinExpTime.setValue(1.000000000000000)

        self.layoutExpTime.addWidget(self.spinExpTime)

        self.comboExpTimeUnit = QComboBox(self.groupExposure)
        self.comboExpTimeUnit.addItem("")
        self.comboExpTimeUnit.addItem("")
        self.comboExpTimeUnit.addItem("")
        self.comboExpTimeUnit.setObjectName("comboExpTimeUnit")
        self.comboExpTimeUnit.setMinimumContentsLength(2)

        self.layoutExpTime.addWidget(self.comboExpTimeUnit)

        self.layoutExpTime.setStretch(0, 1)

        self.gridLayout_4.addLayout(self.layoutExpTime, 1, 1, 1, 1)

        self.verticalLayout.addWidget(self.groupExposure)

        self.verticalSpacer = QSpacerItem(20, 26, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.labelStatus = QLabel(self.scrollAreaWidgetContents)
        self.labelStatus.setObjectName("labelStatus")
        self.labelStatus.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.labelStatus)

        self.progressExposure = QProgressBar(self.scrollAreaWidgetContents)
        self.progressExposure.setObjectName("progressExposure")
        self.progressExposure.setValue(0)
        self.progressExposure.setTextVisible(True)
        self.progressExposure.setInvertedAppearance(False)

        self.verticalLayout.addWidget(self.progressExposure)

        self.labelExposuresLeft = QLabel(self.scrollAreaWidgetContents)
        self.labelExposuresLeft.setObjectName("labelExposuresLeft")
        self.labelExposuresLeft.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.labelExposuresLeft)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_2.addWidget(self.scrollArea)

        self.frameDataDisplay = QWidget(WidgetCamera)
        self.frameDataDisplay.setObjectName("frameDataDisplay")
        self.verticalLayout_2 = QVBoxLayout(self.frameDataDisplay)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 0, 0, 0)

        self.horizontalLayout_2.addWidget(self.frameDataDisplay)

        self.widgetSidebar = QWidget(WidgetCamera)
        self.widgetSidebar.setObjectName("widgetSidebar")

        self.horizontalLayout_2.addWidget(self.widgetSidebar)

        self.horizontalLayout_2.setStretch(1, 1)
        QWidget.setTabOrder(self.scrollArea, self.spinWindowLeft)
        QWidget.setTabOrder(self.spinWindowLeft, self.spinWindowTop)
        QWidget.setTabOrder(self.spinWindowTop, self.spinWindowWidth)
        QWidget.setTabOrder(self.spinWindowWidth, self.spinWindowHeight)
        QWidget.setTabOrder(self.spinWindowHeight, self.butFullFrame)
        QWidget.setTabOrder(self.butFullFrame, self.comboBinning)
        QWidget.setTabOrder(self.comboBinning, self.comboImageFormat)
        QWidget.setTabOrder(self.comboImageFormat, self.comboImageType)
        QWidget.setTabOrder(self.comboImageType, self.spinCount)
        QWidget.setTabOrder(self.spinCount, self.checkBroadcast)
        QWidget.setTabOrder(self.checkBroadcast, self.butExpose)
        QWidget.setTabOrder(self.butExpose, self.butAbort)

        self.retranslateUi(WidgetCamera)

        QMetaObject.connectSlotsByName(WidgetCamera)

    # setupUi

    def retranslateUi(self, WidgetCamera):
        WidgetCamera.setWindowTitle(QCoreApplication.translate("WidgetCamera", "Form", None))
        self.groupWindowing.setTitle(QCoreApplication.translate("WidgetCamera", "Window", None))
        self.label_2.setText(QCoreApplication.translate("WidgetCamera", "Top:", None))
        self.label_3.setText(QCoreApplication.translate("WidgetCamera", "Width:", None))
        self.label.setText(QCoreApplication.translate("WidgetCamera", "Left:", None))
        self.label_4.setText(QCoreApplication.translate("WidgetCamera", "Height:", None))
        self.butFullFrame.setText(QCoreApplication.translate("WidgetCamera", "Full Frame", None))
        self.groupBinning.setTitle(QCoreApplication.translate("WidgetCamera", "Binning", None))
        self.label_5.setText(QCoreApplication.translate("WidgetCamera", "XxY:", None))
        self.groupImageFormat.setTitle(QCoreApplication.translate("WidgetCamera", "Image format", None))
        self.label_10.setText(QCoreApplication.translate("WidgetCamera", "Format:", None))
        self.groupExposure.setTitle(QCoreApplication.translate("WidgetCamera", "Exposure", None))
        self.label_8.setText(QCoreApplication.translate("WidgetCamera", "Count:", None))
        self.labelImageType.setText(QCoreApplication.translate("WidgetCamera", "Type:", None))
        self.butExpose.setText(QCoreApplication.translate("WidgetCamera", "Expose", None))
        self.labelExpTime.setText(QCoreApplication.translate("WidgetCamera", "ExpTime:", None))
        self.checkBroadcast.setText(QCoreApplication.translate("WidgetCamera", "Broadcast", None))
        self.butAbort.setText(QCoreApplication.translate("WidgetCamera", "Abort", None))
        self.spinExpTime.setSuffix("")
        self.comboExpTimeUnit.setItemText(0, QCoreApplication.translate("WidgetCamera", "s", None))
        self.comboExpTimeUnit.setItemText(1, QCoreApplication.translate("WidgetCamera", "ms", None))
        self.comboExpTimeUnit.setItemText(2, QCoreApplication.translate("WidgetCamera", "\u00b5s", None))

        self.labelStatus.setText(QCoreApplication.translate("WidgetCamera", "IDLE", None))
        self.labelExposuresLeft.setText(QCoreApplication.translate("WidgetCamera", "IDLE", None))

    # retranslateUi
