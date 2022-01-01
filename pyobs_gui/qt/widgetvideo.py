# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widgetvideo.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_WidgetVideo(object):
    def setupUi(self, WidgetVideo):
        if not WidgetVideo.objectName():
            WidgetVideo.setObjectName("WidgetVideo")
        WidgetVideo.resize(618, 610)
        self.horizontalLayout_2 = QHBoxLayout(WidgetVideo)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tabWidget = QTabWidget(WidgetVideo)
        self.tabWidget.setObjectName("tabWidget")
        self.tabLiveView = QWidget()
        self.tabLiveView.setObjectName("tabLiveView")
        self.horizontalLayout = QHBoxLayout(self.tabLiveView)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QFrame(self.tabLiveView)
        self.frame.setObjectName("frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupExposure = QGroupBox(self.frame)
        self.groupExposure.setObjectName("groupExposure")
        self.formLayout = QFormLayout(self.groupExposure)
        self.formLayout.setObjectName("formLayout")
        self.spinExpTime = QDoubleSpinBox(self.groupExposure)
        self.spinExpTime.setObjectName("spinExpTime")
        self.spinExpTime.setDecimals(5)
        self.spinExpTime.setMaximum(999.000000000000000)
        self.spinExpTime.setValue(1.000000000000000)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.spinExpTime)

        self.labelExpTime = QLabel(self.groupExposure)
        self.labelExpTime.setObjectName("labelExpTime")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.labelExpTime)

        self.verticalLayout_2.addWidget(self.groupExposure)

        self.verticalSpacer = QSpacerItem(20, 340, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.horizontalLayout.addWidget(self.frame)

        self.frameLiveView = QWidget(self.tabLiveView)
        self.frameLiveView.setObjectName("frameLiveView")
        self.verticalLayout_4 = QVBoxLayout(self.frameLiveView)
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.horizontalLayout.addWidget(self.frameLiveView)

        self.horizontalLayout.setStretch(1, 1)
        self.tabWidget.addTab(self.tabLiveView, "")
        self.tabFitsImage = QWidget()
        self.tabFitsImage.setObjectName("tabFitsImage")
        self.horizontalLayout_3 = QHBoxLayout(self.tabFitsImage)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.frame_2 = QFrame(self.tabFitsImage)
        self.frame_2.setObjectName("frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupExposure_2 = QGroupBox(self.frame_2)
        self.groupExposure_2.setObjectName("groupExposure_2")
        self.gridLayout_5 = QGridLayout(self.groupExposure_2)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.labelImageType = QLabel(self.groupExposure_2)
        self.labelImageType.setObjectName("labelImageType")

        self.gridLayout_5.addWidget(self.labelImageType, 0, 0, 1, 1)

        self.label_9 = QLabel(self.groupExposure_2)
        self.label_9.setObjectName("label_9")

        self.gridLayout_5.addWidget(self.label_9, 1, 0, 1, 1)

        self.checkBroadcast = QCheckBox(self.groupExposure_2)
        self.checkBroadcast.setObjectName("checkBroadcast")
        self.checkBroadcast.setChecked(True)

        self.gridLayout_5.addWidget(self.checkBroadcast, 2, 1, 1, 1)

        self.buttonGrabImage = QPushButton(self.groupExposure_2)
        self.buttonGrabImage.setObjectName("buttonGrabImage")
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
        self.buttonGrabImage.setPalette(palette)

        self.gridLayout_5.addWidget(self.buttonGrabImage, 3, 0, 1, 2)

        self.spinCount = QSpinBox(self.groupExposure_2)
        self.spinCount.setObjectName("spinCount")
        self.spinCount.setMinimum(1)
        self.spinCount.setMaximum(9999)

        self.gridLayout_5.addWidget(self.spinCount, 1, 1, 1, 1)

        self.comboImageType = QComboBox(self.groupExposure_2)
        self.comboImageType.setObjectName("comboImageType")

        self.gridLayout_5.addWidget(self.comboImageType, 0, 1, 1, 1)

        self.buttonAbort = QPushButton(self.groupExposure_2)
        self.buttonAbort.setObjectName("buttonAbort")
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
        self.buttonAbort.setPalette(palette1)

        self.gridLayout_5.addWidget(self.buttonAbort, 4, 0, 1, 2)

        self.verticalLayout.addWidget(self.groupExposure_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.labelExposuresLeft = QLabel(self.frame_2)
        self.labelExposuresLeft.setObjectName("labelExposuresLeft")
        self.labelExposuresLeft.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.labelExposuresLeft)

        self.horizontalLayout_3.addWidget(self.frame_2)

        self.frameImageGrabber = QWidget(self.tabFitsImage)
        self.frameImageGrabber.setObjectName("frameImageGrabber")
        self.verticalLayout_5 = QVBoxLayout(self.frameImageGrabber)
        self.verticalLayout_5.setObjectName("verticalLayout_5")

        self.horizontalLayout_3.addWidget(self.frameImageGrabber)

        self.horizontalLayout_3.setStretch(1, 1)
        self.tabWidget.addTab(self.tabFitsImage, "")

        self.horizontalLayout_2.addWidget(self.tabWidget)

        self.retranslateUi(WidgetVideo)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(WidgetVideo)

    # setupUi

    def retranslateUi(self, WidgetVideo):
        WidgetVideo.setWindowTitle(QCoreApplication.translate("WidgetVideo", "Form", None))
        self.groupExposure.setTitle(QCoreApplication.translate("WidgetVideo", "Exposure", None))
        self.spinExpTime.setSuffix(QCoreApplication.translate("WidgetVideo", " s", None))
        self.labelExpTime.setText(QCoreApplication.translate("WidgetVideo", "ExpTime:", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabLiveView), QCoreApplication.translate("WidgetVideo", "Live View", None)
        )
        self.groupExposure_2.setTitle(QCoreApplication.translate("WidgetVideo", "Exposure", None))
        self.labelImageType.setText(QCoreApplication.translate("WidgetVideo", "Type:", None))
        self.label_9.setText(QCoreApplication.translate("WidgetVideo", "Count:", None))
        self.checkBroadcast.setText(QCoreApplication.translate("WidgetVideo", "Broadcast", None))
        self.buttonGrabImage.setText(QCoreApplication.translate("WidgetVideo", "Grab image", None))
        self.buttonAbort.setText(QCoreApplication.translate("WidgetVideo", "Abort sequence", None))
        self.labelExposuresLeft.setText(QCoreApplication.translate("WidgetVideo", "IDLE", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabFitsImage), QCoreApplication.translate("WidgetVideo", "FITS Image", None)
        )

    # retranslateUi
