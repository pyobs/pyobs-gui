# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'camerawidget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSpinBox, QToolButton,
    QVBoxLayout, QWidget)

from ..datadisplaywidget import DataDisplayWidget
from . import resources_rc

class Ui_CameraWidget(object):
    def setupUi(self, CameraWidget):
        if not CameraWidget.objectName():
            CameraWidget.setObjectName(u"CameraWidget")
        CameraWidget.resize(1014, 764)
        self.horizontalLayout_2 = QHBoxLayout(CameraWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.scrollArea = QScrollArea(CameraWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 294, 748))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy1)
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupWindowing = QGroupBox(self.scrollAreaWidgetContents)
        self.groupWindowing.setObjectName(u"groupWindowing")
        self.gridLayout_2 = QGridLayout(self.groupWindowing)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.spinWindowWidth = QSpinBox(self.groupWindowing)
        self.spinWindowWidth.setObjectName(u"spinWindowWidth")
        self.spinWindowWidth.setMinimum(1)
        self.spinWindowWidth.setMaximum(9999)

        self.gridLayout_2.addWidget(self.spinWindowWidth, 2, 1, 1, 1)

        self.label_2 = QLabel(self.groupWindowing)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_3 = QLabel(self.groupWindowing)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)

        self.label = QLabel(self.groupWindowing)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.spinWindowHeight = QSpinBox(self.groupWindowing)
        self.spinWindowHeight.setObjectName(u"spinWindowHeight")
        self.spinWindowHeight.setMinimum(1)
        self.spinWindowHeight.setMaximum(9999)

        self.gridLayout_2.addWidget(self.spinWindowHeight, 3, 1, 1, 1)

        self.label_4 = QLabel(self.groupWindowing)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)

        self.spinWindowLeft = QSpinBox(self.groupWindowing)
        self.spinWindowLeft.setObjectName(u"spinWindowLeft")
        self.spinWindowLeft.setMaximum(9999)

        self.gridLayout_2.addWidget(self.spinWindowLeft, 0, 1, 1, 1)

        self.spinWindowTop = QSpinBox(self.groupWindowing)
        self.spinWindowTop.setObjectName(u"spinWindowTop")
        self.spinWindowTop.setMaximum(9999)

        self.gridLayout_2.addWidget(self.spinWindowTop, 1, 1, 1, 1)

        self.butFullFrame = QPushButton(self.groupWindowing)
        self.butFullFrame.setObjectName(u"butFullFrame")

        self.gridLayout_2.addWidget(self.butFullFrame, 4, 0, 1, 2)


        self.verticalLayout.addWidget(self.groupWindowing)

        self.groupImageFormat = QGroupBox(self.scrollAreaWidgetContents)
        self.groupImageFormat.setObjectName(u"groupImageFormat")
        self.gridLayout_6 = QGridLayout(self.groupImageFormat)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_10 = QLabel(self.groupImageFormat)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_6.addWidget(self.label_10, 0, 0, 1, 1)

        self.comboImageFormat = QComboBox(self.groupImageFormat)
        self.comboImageFormat.setObjectName(u"comboImageFormat")

        self.gridLayout_6.addWidget(self.comboImageFormat, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupImageFormat)

        self.groupBinning = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBinning.setObjectName(u"groupBinning")
        self.gridLayout_3 = QGridLayout(self.groupBinning)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_5 = QLabel(self.groupBinning)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)

        self.comboBinning = QComboBox(self.groupBinning)
        self.comboBinning.setObjectName(u"comboBinning")

        self.gridLayout_3.addWidget(self.comboBinning, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBinning)

        self.groupGain = QGroupBox(self.scrollAreaWidgetContents)
        self.groupGain.setObjectName(u"groupGain")
        self.gridLayout = QGridLayout(self.groupGain)
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonSetGain = QToolButton(self.groupGain)
        self.buttonSetGain.setObjectName(u"buttonSetGain")
        icon = QIcon()
        icon.addFile(u":/resources/edit-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonSetGain.setIcon(icon)

        self.gridLayout.addWidget(self.buttonSetGain, 0, 3, 1, 1)

        self.textGain = QLineEdit(self.groupGain)
        self.textGain.setObjectName(u"textGain")
        self.textGain.setReadOnly(True)

        self.gridLayout.addWidget(self.textGain, 0, 2, 1, 1)

        self.label_11 = QLabel(self.groupGain)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout.addWidget(self.label_11, 0, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 1, 1, 1)

        self.label_13 = QLabel(self.groupGain)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout.addWidget(self.label_13, 1, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 1, 1, 1)

        self.textOffset = QLineEdit(self.groupGain)
        self.textOffset.setObjectName(u"textOffset")
        self.textOffset.setReadOnly(True)

        self.gridLayout.addWidget(self.textOffset, 1, 2, 1, 1)

        self.buttonSetOffset = QToolButton(self.groupGain)
        self.buttonSetOffset.setObjectName(u"buttonSetOffset")
        self.buttonSetOffset.setIcon(icon)

        self.gridLayout.addWidget(self.buttonSetOffset, 1, 3, 1, 1)


        self.verticalLayout.addWidget(self.groupGain)

        self.groupExpTime = QGroupBox(self.scrollAreaWidgetContents)
        self.groupExpTime.setObjectName(u"groupExpTime")
        self.gridLayout_5 = QGridLayout(self.groupExpTime)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_12 = QLabel(self.groupExpTime)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_5.addWidget(self.label_12, 0, 0, 1, 1)

        self.layoutExpTime = QHBoxLayout()
        self.layoutExpTime.setObjectName(u"layoutExpTime")
        self.spinExpTime = QDoubleSpinBox(self.groupExpTime)
        self.spinExpTime.setObjectName(u"spinExpTime")
        self.spinExpTime.setDecimals(3)
        self.spinExpTime.setMaximum(999.000000000000000)
        self.spinExpTime.setValue(1.000000000000000)

        self.layoutExpTime.addWidget(self.spinExpTime)

        self.comboExpTimeUnit = QComboBox(self.groupExpTime)
        self.comboExpTimeUnit.addItem("")
        self.comboExpTimeUnit.addItem("")
        self.comboExpTimeUnit.addItem("")
        self.comboExpTimeUnit.setObjectName(u"comboExpTimeUnit")
        self.comboExpTimeUnit.setMinimumContentsLength(2)

        self.layoutExpTime.addWidget(self.comboExpTimeUnit)

        self.layoutExpTime.setStretch(0, 1)

        self.gridLayout_5.addLayout(self.layoutExpTime, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupExpTime)

        self.groupExposure = QGroupBox(self.scrollAreaWidgetContents)
        self.groupExposure.setObjectName(u"groupExposure")
        self.gridLayout_4 = QGridLayout(self.groupExposure)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.labelImageType = QLabel(self.groupExposure)
        self.labelImageType.setObjectName(u"labelImageType")

        self.gridLayout_4.addWidget(self.labelImageType, 0, 0, 1, 1)

        self.spinCount = QSpinBox(self.groupExposure)
        self.spinCount.setObjectName(u"spinCount")
        self.spinCount.setMinimum(1)
        self.spinCount.setMaximum(9999)

        self.gridLayout_4.addWidget(self.spinCount, 1, 1, 1, 1)

        self.butAbort = QPushButton(self.groupExposure)
        self.butAbort.setObjectName(u"butAbort")
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        brush1 = QBrush(QColor(170, 0, 0, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush1)
        brush2 = QBrush(QColor(255, 0, 0, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, brush2)
        brush3 = QBrush(QColor(212, 0, 0, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, brush3)
        brush4 = QBrush(QColor(85, 0, 0, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, brush4)
        brush5 = QBrush(QColor(113, 0, 0, 255))
        brush5.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, brush5)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush)
        brush6 = QBrush(QColor(255, 255, 255, 255))
        brush6.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, brush6)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush6)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, brush)
        brush7 = QBrush(QColor(212, 127, 127, 255))
        brush7.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush7)
        brush8 = QBrush(QColor(255, 255, 220, 255))
        brush8.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, brush8)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, brush)
        brush9 = QBrush(QColor(0, 0, 0, 128))
        brush9.setStyle(Qt.BrushStyle.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush9)
#endif
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, brush2)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, brush3)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, brush4)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, brush5)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, brush6)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush6)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush7)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, brush8)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, brush)
        brush10 = QBrush(QColor(0, 0, 0, 128))
        brush10.setStyle(Qt.BrushStyle.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush10)
#endif
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, brush3)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, brush5)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, brush6)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, brush8)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, brush)
        brush11 = QBrush(QColor(0, 0, 0, 128))
        brush11.setStyle(Qt.BrushStyle.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush11)
#endif
        self.butAbort.setPalette(palette)

        self.gridLayout_4.addWidget(self.butAbort, 4, 0, 1, 2)

        self.label_8 = QLabel(self.groupExposure)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_4.addWidget(self.label_8, 1, 0, 1, 1)

        self.butExpose = QPushButton(self.groupExposure)
        self.butExpose.setObjectName(u"butExpose")
        palette1 = QPalette()
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush6)
        brush12 = QBrush(QColor(0, 85, 0, 255))
        brush12.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush12)
        brush13 = QBrush(QColor(0, 127, 0, 255))
        brush13.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, brush13)
        brush14 = QBrush(QColor(0, 106, 0, 255))
        brush14.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, brush14)
        brush15 = QBrush(QColor(0, 42, 0, 255))
        brush15.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, brush15)
        brush16 = QBrush(QColor(0, 56, 0, 255))
        brush16.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, brush16)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush6)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, brush6)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush6)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush12)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, brush)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush15)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, brush8)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, brush)
        brush17 = QBrush(QColor(255, 255, 255, 128))
        brush17.setStyle(Qt.BrushStyle.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush17)
#endif
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush6)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush12)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, brush13)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, brush14)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, brush15)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, brush16)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush6)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, brush6)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush6)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush12)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, brush)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush15)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, brush8)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, brush)
        brush18 = QBrush(QColor(255, 255, 255, 128))
        brush18.setStyle(Qt.BrushStyle.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush18)
#endif
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush15)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush12)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, brush13)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, brush14)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, brush15)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, brush16)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush15)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, brush6)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush15)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush12)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush12)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, brush)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush12)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, brush8)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, brush)
        brush19 = QBrush(QColor(255, 255, 255, 128))
        brush19.setStyle(Qt.BrushStyle.NoBrush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush19)
#endif
        self.butExpose.setPalette(palette1)

        self.gridLayout_4.addWidget(self.butExpose, 3, 0, 1, 2)

        self.checkBroadcast = QCheckBox(self.groupExposure)
        self.checkBroadcast.setObjectName(u"checkBroadcast")
        self.checkBroadcast.setChecked(True)

        self.gridLayout_4.addWidget(self.checkBroadcast, 2, 1, 1, 1)

        self.comboImageType = QComboBox(self.groupExposure)
        self.comboImageType.setObjectName(u"comboImageType")

        self.gridLayout_4.addWidget(self.comboImageType, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupExposure)

        self.verticalSpacer = QSpacerItem(20, 26, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.labelStatus = QLabel(self.scrollAreaWidgetContents)
        self.labelStatus.setObjectName(u"labelStatus")
        self.labelStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.labelStatus)

        self.progressExposure = QProgressBar(self.scrollAreaWidgetContents)
        self.progressExposure.setObjectName(u"progressExposure")
        self.progressExposure.setValue(0)
        self.progressExposure.setTextVisible(True)
        self.progressExposure.setInvertedAppearance(False)

        self.verticalLayout.addWidget(self.progressExposure)

        self.labelExposuresLeft = QLabel(self.scrollAreaWidgetContents)
        self.labelExposuresLeft.setObjectName(u"labelExposuresLeft")
        self.labelExposuresLeft.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.labelExposuresLeft)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout_2.addWidget(self.scrollArea)

        self.datadisplay = DataDisplayWidget(CameraWidget)
        self.datadisplay.setObjectName(u"datadisplay")

        self.horizontalLayout_2.addWidget(self.datadisplay)

        self.widgetSidebar = QWidget(CameraWidget)
        self.widgetSidebar.setObjectName(u"widgetSidebar")

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

        self.retranslateUi(CameraWidget)

        QMetaObject.connectSlotsByName(CameraWidget)
    # setupUi

    def retranslateUi(self, CameraWidget):
        CameraWidget.setWindowTitle(QCoreApplication.translate("CameraWidget", u"Form", None))
        self.groupWindowing.setTitle("")
        self.label_2.setText(QCoreApplication.translate("CameraWidget", u"Top:", None))
        self.label_3.setText(QCoreApplication.translate("CameraWidget", u"Width:", None))
        self.label.setText(QCoreApplication.translate("CameraWidget", u"Left:", None))
        self.label_4.setText(QCoreApplication.translate("CameraWidget", u"Height:", None))
        self.butFullFrame.setText(QCoreApplication.translate("CameraWidget", u"Full Frame", None))
        self.groupImageFormat.setTitle("")
        self.label_10.setText(QCoreApplication.translate("CameraWidget", u"Format:", None))
        self.groupBinning.setTitle("")
        self.label_5.setText(QCoreApplication.translate("CameraWidget", u"Binning:", None))
        self.groupGain.setTitle("")
        self.buttonSetGain.setText(QCoreApplication.translate("CameraWidget", u"...", None))
        self.label_11.setText(QCoreApplication.translate("CameraWidget", u"Gain:", None))
        self.label_13.setText(QCoreApplication.translate("CameraWidget", u"Offset:", None))
        self.buttonSetOffset.setText(QCoreApplication.translate("CameraWidget", u"...", None))
        self.groupExpTime.setTitle("")
        self.label_12.setText(QCoreApplication.translate("CameraWidget", u"ExpTime:", None))
        self.spinExpTime.setSuffix("")
        self.comboExpTimeUnit.setItemText(0, QCoreApplication.translate("CameraWidget", u"s", None))
        self.comboExpTimeUnit.setItemText(1, QCoreApplication.translate("CameraWidget", u"ms", None))
        self.comboExpTimeUnit.setItemText(2, QCoreApplication.translate("CameraWidget", u"\u00b5s", None))

        self.groupExposure.setTitle("")
        self.labelImageType.setText(QCoreApplication.translate("CameraWidget", u"Type:", None))
        self.butAbort.setText(QCoreApplication.translate("CameraWidget", u"Abort", None))
        self.label_8.setText(QCoreApplication.translate("CameraWidget", u"Count:", None))
        self.butExpose.setText(QCoreApplication.translate("CameraWidget", u"Expose", None))
        self.checkBroadcast.setText(QCoreApplication.translate("CameraWidget", u"Broadcast", None))
        self.labelStatus.setText(QCoreApplication.translate("CameraWidget", u"IDLE", None))
        self.labelExposuresLeft.setText(QCoreApplication.translate("CameraWidget", u"IDLE", None))
    # retranslateUi

