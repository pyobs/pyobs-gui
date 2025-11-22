# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'videowidget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..datadisplaywidget import DataDisplayWidget


class Ui_VideoWidget(object):
    def setupUi(self, VideoWidget):
        if not VideoWidget.objectName():
            VideoWidget.setObjectName("VideoWidget")
        VideoWidget.resize(618, 610)
        self.horizontalLayout_2 = QHBoxLayout(VideoWidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tabWidget = QTabWidget(VideoWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabLiveView = QWidget()
        self.tabLiveView.setObjectName("tabLiveView")
        self.horizontalLayout = QHBoxLayout(self.tabLiveView)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QFrame(self.tabLiveView)
        self.frame.setObjectName("frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupExposure = QGroupBox(self.frame)
        self.groupExposure.setObjectName("groupExposure")
        self.formLayout = QFormLayout(self.groupExposure)
        self.formLayout.setObjectName("formLayout")
        self.spinExpTime = QDoubleSpinBox(self.groupExposure)
        self.spinExpTime.setObjectName("spinExpTime")
        self.spinExpTime.setDecimals(6)
        self.spinExpTime.setMaximum(999.000000000000000)
        self.spinExpTime.setValue(1.000000000000000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinExpTime)

        self.labelExpTime = QLabel(self.groupExposure)
        self.labelExpTime.setObjectName("labelExpTime")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelExpTime)

        self.verticalLayout_2.addWidget(self.groupExposure)

        self.groupGain = QGroupBox(self.frame)
        self.groupGain.setObjectName("groupGain")
        self.gridLayout = QGridLayout(self.groupGain)
        self.gridLayout.setObjectName("gridLayout")
        self.label_11 = QLabel(self.groupGain)
        self.label_11.setObjectName("label_11")

        self.gridLayout.addWidget(self.label_11, 0, 0, 1, 1)

        self.spinGain = QDoubleSpinBox(self.groupGain)
        self.spinGain.setObjectName("spinGain")

        self.gridLayout.addWidget(self.spinGain, 0, 1, 1, 1)

        self.verticalLayout_2.addWidget(self.groupGain)

        self.verticalSpacer = QSpacerItem(20, 340, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

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
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
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
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        brush1 = QBrush(QColor(0, 85, 0, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush1)
        brush2 = QBrush(QColor(0, 127, 0, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, brush2)
        brush3 = QBrush(QColor(0, 106, 0, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, brush3)
        brush4 = QBrush(QColor(0, 42, 0, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, brush4)
        brush5 = QBrush(QColor(0, 56, 0, 255))
        brush5.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, brush5)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush)
        brush6 = QBrush(QColor(0, 0, 0, 255))
        brush6.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush6)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, brush6)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush4)
        brush7 = QBrush(QColor(255, 255, 220, 255))
        brush7.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, brush7)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, brush6)
        brush8 = QBrush(QColor(255, 255, 255, 128))
        brush8.setStyle(Qt.BrushStyle.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush8)
        # endif
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, brush2)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, brush3)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, brush4)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, brush5)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush6)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, brush6)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush4)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, brush7)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, brush6)
        brush9 = QBrush(QColor(255, 255, 255, 128))
        brush9.setStyle(Qt.BrushStyle.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush9)
        # endif
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, brush3)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, brush5)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, brush6)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, brush7)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, brush6)
        brush10 = QBrush(QColor(255, 255, 255, 128))
        brush10.setStyle(Qt.BrushStyle.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush10)
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
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush6)
        brush11 = QBrush(QColor(170, 0, 0, 255))
        brush11.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush11)
        brush12 = QBrush(QColor(255, 0, 0, 255))
        brush12.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, brush12)
        brush13 = QBrush(QColor(212, 0, 0, 255))
        brush13.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, brush13)
        brush14 = QBrush(QColor(85, 0, 0, 255))
        brush14.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, brush14)
        brush15 = QBrush(QColor(113, 0, 0, 255))
        brush15.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, brush15)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush6)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, brush)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush6)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush11)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, brush6)
        brush16 = QBrush(QColor(212, 127, 127, 255))
        brush16.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush16)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, brush7)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, brush6)
        brush17 = QBrush(QColor(0, 0, 0, 128))
        brush17.setStyle(Qt.BrushStyle.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush17)
        # endif
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush6)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush11)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, brush12)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, brush13)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, brush14)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, brush15)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush6)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, brush)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush6)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush11)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, brush6)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush16)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, brush7)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, brush6)
        brush18 = QBrush(QColor(0, 0, 0, 128))
        brush18.setStyle(Qt.BrushStyle.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush18)
        # endif
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush14)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush11)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, brush12)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, brush13)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, brush14)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, brush15)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush14)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, brush)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush14)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush11)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush11)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, brush6)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush11)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, brush7)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, brush6)
        brush19 = QBrush(QColor(0, 0, 0, 128))
        brush19.setStyle(Qt.BrushStyle.NoBrush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush19)
        # endif
        self.buttonAbort.setPalette(palette1)

        self.gridLayout_5.addWidget(self.buttonAbort, 4, 0, 1, 2)

        self.verticalLayout.addWidget(self.groupExposure_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.labelExposuresLeft = QLabel(self.frame_2)
        self.labelExposuresLeft.setObjectName("labelExposuresLeft")
        self.labelExposuresLeft.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.labelExposuresLeft)

        self.horizontalLayout_3.addWidget(self.frame_2)

        self.datadisplay = DataDisplayWidget(self.tabFitsImage)
        self.datadisplay.setObjectName("datadisplay")

        self.horizontalLayout_3.addWidget(self.datadisplay)

        self.tabWidget.addTab(self.tabFitsImage, "")

        self.horizontalLayout_2.addWidget(self.tabWidget)

        self.retranslateUi(VideoWidget)

        self.tabWidget.setCurrentIndex(1)

        QMetaObject.connectSlotsByName(VideoWidget)

    # setupUi

    def retranslateUi(self, VideoWidget):
        VideoWidget.setWindowTitle(QCoreApplication.translate("VideoWidget", "Form", None))
        self.groupExposure.setTitle("")
        self.spinExpTime.setSuffix(QCoreApplication.translate("VideoWidget", " s", None))
        self.labelExpTime.setText(QCoreApplication.translate("VideoWidget", "ExpTime:", None))
        self.groupGain.setTitle("")
        self.label_11.setText(QCoreApplication.translate("VideoWidget", "Gain:", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabLiveView), QCoreApplication.translate("VideoWidget", "Live View", None)
        )
        self.groupExposure_2.setTitle(QCoreApplication.translate("VideoWidget", "Exposure", None))
        self.labelImageType.setText(QCoreApplication.translate("VideoWidget", "Type:", None))
        self.label_9.setText(QCoreApplication.translate("VideoWidget", "Count:", None))
        self.checkBroadcast.setText(QCoreApplication.translate("VideoWidget", "Broadcast", None))
        self.buttonGrabImage.setText(QCoreApplication.translate("VideoWidget", "Grab image", None))
        self.buttonAbort.setText(QCoreApplication.translate("VideoWidget", "Abort sequence", None))
        self.labelExposuresLeft.setText(QCoreApplication.translate("VideoWidget", "IDLE", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabFitsImage), QCoreApplication.translate("VideoWidget", "FITS Image", None)
        )

    # retranslateUi
