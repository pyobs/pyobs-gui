# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'datadisplaywidget.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QHBoxLayout,
    QHeaderView, QLineEdit, QSizePolicy, QSpacerItem,
    QTabWidget, QTableWidget, QTableWidgetItem, QToolButton,
    QVBoxLayout, QWidget)

class Ui_DataDisplayWidget(object):
    def setupUi(self, DataDisplayWidget):
        if not DataDisplayWidget.objectName():
            DataDisplayWidget.setObjectName(u"DataDisplayWidget")
        DataDisplayWidget.resize(512, 388)
        self.verticalLayout = QVBoxLayout(DataDisplayWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(DataDisplayWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabImage = QWidget()
        self.tabImage.setObjectName(u"tabImage")
        self.tabWidget.addTab(self.tabImage, "")
        self.tabFitsHeader = QWidget()
        self.tabFitsHeader.setObjectName(u"tabFitsHeader")
        self.verticalLayout_2 = QVBoxLayout(self.tabFitsHeader)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tableFitsHeader = QTableWidget(self.tabFitsHeader)
        self.tableFitsHeader.setObjectName(u"tableFitsHeader")
        self.tableFitsHeader.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableFitsHeader.setAlternatingRowColors(True)
        self.tableFitsHeader.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableFitsHeader.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableFitsHeader.horizontalHeader().setStretchLastSection(True)
        self.tableFitsHeader.verticalHeader().setVisible(False)

        self.verticalLayout_2.addWidget(self.tableFitsHeader)

        self.tabWidget.addTab(self.tabFitsHeader, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.checkAutoUpdate = QCheckBox(DataDisplayWidget)
        self.checkAutoUpdate.setObjectName(u"checkAutoUpdate")
        self.checkAutoUpdate.setChecked(True)

        self.horizontalLayout.addWidget(self.checkAutoUpdate)

        self.horizontalSpacer_2 = QSpacerItem(38, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.checkAutoSave = QCheckBox(DataDisplayWidget)
        self.checkAutoSave.setObjectName(u"checkAutoSave")

        self.horizontalLayout.addWidget(self.checkAutoSave)

        self.textAutoSavePath = QLineEdit(DataDisplayWidget)
        self.textAutoSavePath.setObjectName(u"textAutoSavePath")
        self.textAutoSavePath.setEnabled(False)

        self.horizontalLayout.addWidget(self.textAutoSavePath)

        self.butAutoSave = QToolButton(DataDisplayWidget)
        self.butAutoSave.setObjectName(u"butAutoSave")

        self.horizontalLayout.addWidget(self.butAutoSave)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.butSaveTo = QToolButton(DataDisplayWidget)
        self.butSaveTo.setObjectName(u"butSaveTo")
        icon = QIcon()
        icon.addFile(u":/resources/Crystal_Clear_device_floppy_unmount.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.butSaveTo.setIcon(icon)
        self.butSaveTo.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.butSaveTo)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(DataDisplayWidget)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DataDisplayWidget)
    # setupUi

    def retranslateUi(self, DataDisplayWidget):
        DataDisplayWidget.setWindowTitle(QCoreApplication.translate("DataDisplayWidget", u"Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabImage), QCoreApplication.translate("DataDisplayWidget", u"Image", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFitsHeader), QCoreApplication.translate("DataDisplayWidget", u"FITS header", None))
        self.checkAutoUpdate.setText(QCoreApplication.translate("DataDisplayWidget", u"Auto-update", None))
        self.checkAutoSave.setText(QCoreApplication.translate("DataDisplayWidget", u"Auto-save:", None))
        self.butAutoSave.setText(QCoreApplication.translate("DataDisplayWidget", u"...", None))
        self.butSaveTo.setText(QCoreApplication.translate("DataDisplayWidget", u"Save to...", None))
    # retranslateUi

