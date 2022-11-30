import logging
from typing import Any, Dict, Tuple
from PyQt5 import QtWidgets, QtCore

from pyobs.interfaces import ITemperatures
from pyobs.utils.time import Time
from .base import BaseWidget
from .qt.temperatureswidget_ui import Ui_TemperaturesWidget
from .temperaturesplotwidget import TemperaturesPlotWidget

log = logging.getLogger(__name__)


class TemperaturesWidget(QtWidgets.QWidget, BaseWidget, Ui_TemperaturesWidget):
    signal_update_gui = QtCore.pyqtSignal()

    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, update_func=self._update, update_interval=10, **kwargs)
        self.setupUi(self)

        # status
        self._temps: Dict[str, float] = {}

        # widgets
        self._widgets: Dict[str, QtWidgets.QLineEdit] = {}

        # plot
        self._plot_window = QtWidgets.QMainWindow()
        self._plot_widget = TemperaturesPlotWidget()
        self._plot_window.setCentralWidget(self._plot_widget)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    async def _update(self) -> None:
        # get temps
        if isinstance(self.module, ITemperatures):
            self._temps = await self.module.get_temperatures()
            self._plot_widget.add_data(Time.now(), self._temps)

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        if self._temps is not None:
            # enable myself
            self.setEnabled(True)

            # get layout
            layout = self.frame.layout()

            # loop temps
            for key in sorted(self._temps.keys()):
                value = self._temps[key]

                # does key widget exist?
                if key not in self._widgets:
                    # create widget
                    widget = QtWidgets.QLineEdit()
                    widget.setReadOnly(True)
                    widget.setAlignment(QtCore.Qt.AlignHCenter)

                    # add it to layout
                    layout.addRow(key + ":", widget)

                    # and to dict
                    self._widgets[key] = widget

                # set value
                self._widgets[key].setText("N/A" if value is None else "%.2f °C" % value)

            # now loop widgets and check, whether we need to delete some
            for key, widget in self._widgets.items():
                if key not in self._temps:
                    layout.removeRow(widget)

    def on_buttonPlotTemps_clicked(self) -> None:
        self._plot_window.show()
