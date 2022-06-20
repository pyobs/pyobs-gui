from PyQt5.QtGui import QIcon
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin

from compassmovewidget import CompassMoveWidget


class CompassMovePlugin(QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        super(CompassMovePlugin, self).__init__(parent)

        self.initialized = False

    def initialize(self, core):
        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def createWidget(self, parent):
        return CompassMoveWidget(parent)

    def name(self):
        return "CompassMoveWidget"

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
        return "compassmovewidget"
