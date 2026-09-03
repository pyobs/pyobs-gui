# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'videograbwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

from ..datadisplaywidget import DataDisplayWidget

class Ui_VideoGrabWidget(object):
    def setupUi(self, VideoGrabWidget):
        if not VideoGrabWidget.objectName():
            VideoGrabWidget.setObjectName(u"VideoGrabWidget")
        VideoGrabWidget.resize(618, 530)
        self.horizontalLayout_3 = QHBoxLayout(VideoGrabWidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.frame_2 = QFrame(VideoGrabWidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupExposure_2 = QGroupBox(self.frame_2)
        self.groupExposure_2.setObjectName(u"groupExposure_2")
        self.gridLayout_5 = QGridLayout(self.groupExposure_2)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.labelImageType = QLabel(self.groupExposure_2)
        self.labelImageType.setObjectName(u"labelImageType")

        self.gridLayout_5.addWidget(self.labelImageType, 0, 0, 1, 1)

        self.label_9 = QLabel(self.groupExposure_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_5.addWidget(self.label_9, 1, 0, 1, 1)

        self.checkBroadcast = QCheckBox(self.groupExposure_2)
        self.checkBroadcast.setObjectName(u"checkBroadcast")
        self.checkBroadcast.setChecked(True)

        self.gridLayout_5.addWidget(self.checkBroadcast, 2, 1, 1, 1)

        self.buttonGrabImage = QPushButton(self.groupExposure_2)
        self.buttonGrabImage.setObjectName(u"buttonGrabImage")
        palette = QPalette()
        brush = QBrush(QColor(0, 85, 0, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush)
        brush1 = QBrush(QColor(255, 255, 255, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush)
        brush2 = QBrush(QColor(0, 42, 0, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush2)
        self.buttonGrabImage.setPalette(palette)

        self.gridLayout_5.addWidget(self.buttonGrabImage, 3, 0, 1, 2)

        self.spinCount = QSpinBox(self.groupExposure_2)
        self.spinCount.setObjectName(u"spinCount")
        self.spinCount.setMinimum(1)
        self.spinCount.setMaximum(9999)

        self.gridLayout_5.addWidget(self.spinCount, 1, 1, 1, 1)

        self.comboImageType = QComboBox(self.groupExposure_2)
        self.comboImageType.setObjectName(u"comboImageType")

        self.gridLayout_5.addWidget(self.comboImageType, 0, 1, 1, 1)

        self.buttonAbort = QPushButton(self.groupExposure_2)
        self.buttonAbort.setObjectName(u"buttonAbort")
        palette1 = QPalette()
        brush3 = QBrush(QColor(170, 0, 0, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush3)
        brush4 = QBrush(QColor(0, 0, 0, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush4)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush3)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush4)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush3)
        brush5 = QBrush(QColor(85, 0, 0, 255))
        brush5.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush5)
        self.buttonAbort.setPalette(palette1)

        self.gridLayout_5.addWidget(self.buttonAbort, 4, 0, 1, 2)


        self.verticalLayout.addWidget(self.groupExposure_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.labelExposuresLeft = QLabel(self.frame_2)
        self.labelExposuresLeft.setObjectName(u"labelExposuresLeft")
        self.labelExposuresLeft.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.labelExposuresLeft)


        self.horizontalLayout_3.addWidget(self.frame_2)

        self.datadisplay = DataDisplayWidget(VideoGrabWidget)
        self.datadisplay.setObjectName(u"datadisplay")

        self.horizontalLayout_3.addWidget(self.datadisplay)


        self.retranslateUi(VideoGrabWidget)

        QMetaObject.connectSlotsByName(VideoGrabWidget)
    # setupUi

    def retranslateUi(self, VideoGrabWidget):
        VideoGrabWidget.setWindowTitle(QCoreApplication.translate("VideoGrabWidget", u"Form", None))
        self.groupExposure_2.setTitle(QCoreApplication.translate("VideoGrabWidget", u"Exposure", None))
        self.labelImageType.setText(QCoreApplication.translate("VideoGrabWidget", u"Type:", None))
        self.label_9.setText(QCoreApplication.translate("VideoGrabWidget", u"Count:", None))
        self.checkBroadcast.setText(QCoreApplication.translate("VideoGrabWidget", u"Broadcast", None))
        self.buttonGrabImage.setText(QCoreApplication.translate("VideoGrabWidget", u"Grab image", None))
        self.buttonAbort.setText(QCoreApplication.translate("VideoGrabWidget", u"Abort sequence", None))
        self.labelExposuresLeft.setText(QCoreApplication.translate("VideoGrabWidget", u"IDLE", None))
    # retranslateUi

