from PyQt5.QtGui import QIcon
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin

from camerawidget import CameraWidget


class CameraPlugin(QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        super(CameraPlugin, self).__init__(parent)

        self.initialized = False

    def initialize(self, core):
        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def createWidget(self, parent):
        return CameraWidget(parent)

    def name(self):
        return "CameraWidget"

    def group(self):
        return "pyobs Widgets"

    def icon(self):
        return QIcon()

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def isContainer(self):
        return False

    def includeFile(self):
        return "camerawidget"
