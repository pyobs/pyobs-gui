import logging
from typing import Any, Dict, cast
from PySide6 import QtWidgets, QtCore  # type: ignore

from pyobs.interfaces import ITemperatures, TemperaturesState
from pyobs.utils.time import Time
from .base import BaseWidget
from .qt.temperatureswidget_ui import Ui_TemperaturesWidget
from .temperaturesplotwidget import TemperaturesPlotWidget

log = logging.getLogger(__name__)


class TemperaturesWidget(BaseWidget, Ui_TemperaturesWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._temps: Dict[str, float] = {}

        # widgets
        self._widgets: Dict[str, QtWidgets.QLineEdit] = {}

        # plot
        self._plot_window = QtWidgets.QMainWindow()
        self._plot_widget = TemperaturesPlotWidget()
        self._plot_window.setCentralWidget(self._plot_widget)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonPlotTemps.clicked.connect(self.buttonPlotTemps_clicked)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, ITemperatures, self._on_temperatures_state)

    def _on_temperatures_state(self, state: TemperaturesState) -> None:
        self._temps = {t.name: t.value for t in state.readings}
        self._plot_widget.add_data(Time.now(), self._temps)
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        self.setEnabled(True)

        layout = cast("QtWidgets.QFormLayout", self.frame.layout())

        for key in sorted(self._temps.keys()):
            value = self._temps[key]

            if key not in self._widgets:
                widget = QtWidgets.QLineEdit()
                widget.setReadOnly(True)
                widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
                layout.addRow(key + ":", widget)
                self._widgets[key] = widget

            self._widgets[key].setText("N/A" if value is None else "%.2f °C" % value)

        for key, widget in self._widgets.items():
            if key not in self._temps:
                layout.removeRow(widget)

    @QtCore.Slot()  # type: ignore
    def buttonPlotTemps_clicked(self) -> None:
        self._plot_window.show()