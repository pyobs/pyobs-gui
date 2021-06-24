# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetvideo.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WidgetVideo(object):
    def setupUi(self, WidgetVideo):
        WidgetVideo.setObjectName("WidgetVideo")
        WidgetVideo.resize(1069, 771)
        self.verticalLayout = QtWidgets.QVBoxLayout(WidgetVideo)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(WidgetVideo)
        self.tabWidget.setObjectName("tabWidget")
        self.tabLiveView = QtWidgets.QWidget()
        self.tabLiveView.setObjectName("tabLiveView")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tabLiveView)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget.addTab(self.tabLiveView, "")
        self.tabFitsImage = QtWidgets.QWidget()
        self.tabFitsImage.setObjectName("tabFitsImage")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tabFitsImage)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tabWidget.addTab(self.tabFitsImage, "")
        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi(WidgetVideo)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(WidgetVideo)

    def retranslateUi(self, WidgetVideo):
        _translate = QtCore.QCoreApplication.translate
        WidgetVideo.setWindowTitle(_translate("WidgetVideo", "Form"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabLiveView), _translate("WidgetVideo", "Live View"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFitsImage), _translate("WidgetVideo", "FITS Image"))
