import logging

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

from pyobs_gui.basewidget import BaseWidget

from pyobs.interfaces import IStoppable, IAltAz, IRaDec, ILatLon

log = logging.getLogger(__name__)


class WidgetStoppable(QtWidgets.QWidget):
    """Simple widget for any Module implementing the IStoppable interface."""
    def __init__(self, module, comm, parent=None):
        super().__init__(parent=parent)
        self.module = module

        # build GUI
        layout = QtWidgets.QVBoxLayout(self)
        self.running = QtWidgets.QCheckBox("Is running")
        self.running.toggled.connect(self.on_toggle)
        layout.addWidget(self.running)

    def _update(self):
        self.running.setChecked(self.module.is_running().wait())

    def on_toggle(self, running):
        if running:
            self.module.start()
        else:
            self.module.stop()


class WidgetCoordinates(QtWidgets.QWidget):
    """
    Simple widget for any Module implementing any of the coordinate
    interfaces like IAltAz.

    Support IAltAz, IRaDec and ILatLon
    """
    def __init__(self, module, comm, parent=None):
        super().__init__(parent=parent)
        self.module = module
        self.comm = comm

        coordtypes = [(IAltAz, "move_altaz", "get_altaz",
                       "Horizontal (Alt, Az) in deg"),
                      (IRaDec, "move_radec", "get_readec",
                       "Equatorial (Ra, Dec) in deg"),
                      (ILatLon, "move_latlon", "get_latlon",
                       "Geographic (Lat, Lon) in deg")]

        # create widgets
        self.edittargetcoord = QtWidgets.QLineEdit("")
        self.cmbcoordtype = QtWidgets.QComboBox()
        self.cmbcoordtype.setEditable(False)
        self.btnmovetotarget = QtWidgets.QPushButton("Move to target")
        self.btnmovetotarget.clicked.connect(self.on_move_to_target)

        frmcurrentcoord = QtWidgets.QGroupBox("Current position")
        lytcurrentcoord = QtWidgets.QFormLayout(frmcurrentcoord)

        self.interfaces = {}
        for Interface, setter, getter, name in coordtypes:
            if isinstance(self.module, Interface):
                setterfn = getattr(self.module, setter)
                getterfn = getattr(self.module, getter)
                lblcurrentcoord = QtWidgets.QLabel("")
                lytcurrentcoord.addRow(name, lblcurrentcoord)
                self.interfaces[name] = setterfn, getterfn, lblcurrentcoord
                self.cmbcoordtype.addItem(name)

        # build GUI
        layout = QtWidgets.QFormLayout(self)
        layout.addRow(frmcurrentcoord)
        layout.addRow(self.cmbcoordtype, self.edittargetcoord)
        layout.addRow(self.btnmovetotarget)

    def _update(self):
        for name, (_, getter, lbl) in self.interfaces.items():
            lbl.setText("{:.3f}, {:.3f}".format(*getter().wait()))

    def on_move_to_target(self):
        coordstr = self.edittargetcoord.text()
        coords = [float(x) for x in coordstr.split(",")]
        coordtype = self.cmbcoordtype.currentText()
        setter = self.interfaces[coordtype][0]
        setter(coords[0], coords[1]).wait()


class GenericWidget(BaseWidget):
    """
    A container widget of all subwidgets for the Interfaces a module
    implements.
    """

    @staticmethod
    def create(module, comm):
        """
        Convenience method to build a Generic widget containing all subwidgets
        for the Interfaces the module implements.

        TODO: why can't this be done in the constructor?
        """
        genericwidgets = [(IStoppable, WidgetStoppable),
                          ((IAltAz, IRaDec, ILatLon), WidgetCoordinates)]

        widgets = [widget(module, comm)
                   for Interface, widget in genericwidgets
                   if isinstance(module, Interface)]
        if not widgets:
            return None

        return GenericWidget(module, comm, widgets)

    def __init__(self, module, comm, widgets, parent=None):
        BaseWidget.__init__(self, parent=parent, update_func=self._update)
        self.module = module
        self.comm = comm
        self.widgets = widgets

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        for w in self.widgets:
            layout.addWidget(w)

        layout.addWidget

    def _update(self):
        for w in self.widgets:
            w._update()
