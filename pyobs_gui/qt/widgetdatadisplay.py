# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widgetdatadisplay.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_WidgetDataDisplay(object):
    def setupUi(self, WidgetDataDisplay):
        if not WidgetDataDisplay.objectName():
            WidgetDataDisplay.setObjectName("WidgetDataDisplay")
        WidgetDataDisplay.resize(512, 388)
        self.verticalLayout = QVBoxLayout(WidgetDataDisplay)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QTabWidget(WidgetDataDisplay)
        self.tabWidget.setObjectName("tabWidget")
        self.tabImage = QWidget()
        self.tabImage.setObjectName("tabImage")
        self.tabWidget.addTab(self.tabImage, "")
        self.tabFitsHeader = QWidget()
        self.tabFitsHeader.setObjectName("tabFitsHeader")
        self.verticalLayout_2 = QVBoxLayout(self.tabFitsHeader)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tableFitsHeader = QTableWidget(self.tabFitsHeader)
        self.tableFitsHeader.setObjectName("tableFitsHeader")
        self.tableFitsHeader.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableFitsHeader.setAlternatingRowColors(True)
        self.tableFitsHeader.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableFitsHeader.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableFitsHeader.horizontalHeader().setStretchLastSection(True)
        self.tableFitsHeader.verticalHeader().setVisible(False)

        self.verticalLayout_2.addWidget(self.tableFitsHeader)

        self.tabWidget.addTab(self.tabFitsHeader, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkAutoUpdate = QCheckBox(WidgetDataDisplay)
        self.checkAutoUpdate.setObjectName("checkAutoUpdate")
        self.checkAutoUpdate.setChecked(True)

        self.horizontalLayout.addWidget(self.checkAutoUpdate)

        self.horizontalSpacer_2 = QSpacerItem(38, 18, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.checkAutoSave = QCheckBox(WidgetDataDisplay)
        self.checkAutoSave.setObjectName("checkAutoSave")

        self.horizontalLayout.addWidget(self.checkAutoSave)

        self.textAutoSavePath = QLineEdit(WidgetDataDisplay)
        self.textAutoSavePath.setObjectName("textAutoSavePath")
        self.textAutoSavePath.setEnabled(False)

        self.horizontalLayout.addWidget(self.textAutoSavePath)

        self.butAutoSave = QToolButton(WidgetDataDisplay)
        self.butAutoSave.setObjectName("butAutoSave")

        self.horizontalLayout.addWidget(self.butAutoSave)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.butSaveTo = QToolButton(WidgetDataDisplay)
        self.butSaveTo.setObjectName("butSaveTo")
        icon = QIcon()
        icon.addFile(":/resources/Crystal_Clear_device_floppy_unmount.png", QSize(), QIcon.Normal, QIcon.Off)
        self.butSaveTo.setIcon(icon)
        self.butSaveTo.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.butSaveTo)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(WidgetDataDisplay)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(WidgetDataDisplay)

    # setupUi

    def retranslateUi(self, WidgetDataDisplay):
        WidgetDataDisplay.setWindowTitle(QCoreApplication.translate("WidgetDataDisplay", "Form", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabImage), QCoreApplication.translate("WidgetDataDisplay", "Image", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabFitsHeader),
            QCoreApplication.translate("WidgetDataDisplay", "FITS header", None),
        )
        self.checkAutoUpdate.setText(QCoreApplication.translate("WidgetDataDisplay", "Auto-update", None))
        self.checkAutoSave.setText(QCoreApplication.translate("WidgetDataDisplay", "Auto-save:", None))
        self.butAutoSave.setText(QCoreApplication.translate("WidgetDataDisplay", "...", None))
        self.butSaveTo.setText(QCoreApplication.translate("WidgetDataDisplay", "Save to...", None))

    # retranslateUi
