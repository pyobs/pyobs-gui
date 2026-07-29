import os
from collections import deque
from typing import Any, Deque, Dict, Tuple, TYPE_CHECKING
from PySide6 import QtWidgets, QtGui, QtCore  # type: ignore
import logging

os.environ["QT_API"] = "PySide6"
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.dates import DateFormatter

from pyobs.interfaces import IWeather, WeatherState, WeatherSensorReading
from pyobs.utils.enums import WeatherSensors
from .qt.weatherwidget_ui import Ui_WeatherWidget
from .base import BaseWidget

if TYPE_CHECKING:
    from pyobs.utils.time import Time


log = logging.getLogger(__name__)

# how many samples to keep per sensor for the history plot
_HISTORY_LENGTH = 200


# label and display order for known sensors; anything else reported by the module is ignored
SENSOR_LABELS: Dict[WeatherSensors, str] = {
    WeatherSensors.TEMPERATURE: "Temp.",
    WeatherSensors.HUMIDITY: "Rel. humid.",
    WeatherSensors.DEWPOINT: "Dew point",
    WeatherSensors.PRESSURE: "Press.",
    WeatherSensors.WINDDIR: "Wind dir",
    WeatherSensors.WINDSPEED: "Wind speed",
    WeatherSensors.PARTICLES: "Particles",
    WeatherSensors.RAIN: "Rain",
    WeatherSensors.SKYTEMP: "Rel. sky temp.",
    WeatherSensors.SKYMAG: "Sky mag.",
}


class WidgetCurrentSensor(QtWidgets.QFrame):  # type: ignore
    def __init__(self, label: str, unit: str, **kwargs: Any):
        QtWidgets.QFrame.__init__(self, **kwargs)

        # create layout
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # font
        font1 = QtGui.QFont("Times", 8, QtGui.QFont.Weight.Normal)
        font2 = QtGui.QFont("Times", 12, QtGui.QFont.Weight.Bold)

        # add label
        self._label = QtWidgets.QLabel(label)
        self._label.setFont(font1)
        self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        # add value
        self._value = QtWidgets.QLabel()
        self._value.setFont(font2)
        self._value.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._value)

        # add unit
        self._unit: QtWidgets.QLabel | None
        if unit is not None:
            self._unit = QtWidgets.QLabel(unit)
            self._unit.setFont(font1)
            self._unit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self._unit)
        else:
            self._unit = None

    def set_value(self, value: str) -> None:
        self._value.setText(value)

    def set_good(self, good: bool | None) -> None:
        # which colour?
        if good is None:
            stylesheet = ""
        else:
            stylesheet = "QLabel {color: " + ("lime" if good else "red") + ";}"

        # set colour
        self._label.setStyleSheet(stylesheet)
        self._value.setStyleSheet(stylesheet)
        if self._unit is not None:
            self._unit.setStyleSheet(stylesheet)


class WeatherWidget(BaseWidget, Ui_WeatherWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # weather info
        self._time: "Time | None" = None
        self._good: bool | None = None
        self._readings: Dict[WeatherSensors, WeatherSensorReading] = {}
        self._current_widgets: Dict[str, WidgetCurrentSensor] = {}
        self._history: Dict[WeatherSensors, "Deque[Tuple[Time, float]]"] = {}

        # add plot
        self.figure = plt.figure()
        layout = QtWidgets.QVBoxLayout(self.framePlot)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.framePlot.setLayout(layout)

        # before first update, disable myself
        self.setEnabled(False)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IWeather, self._on_weather_state)

    def _on_weather_state(self, state: WeatherState) -> None:
        self._time = state.time
        self._good = state.good
        self._readings = {r.sensor: r for r in state.readings}
        for reading in state.readings:
            if reading.value is not None:
                self._history.setdefault(reading.sensor, deque(maxlen=_HISTORY_LENGTH)).append(
                    (reading.time, reading.value)
                )
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        # enable myself
        self.setEnabled(True)

        layout = self.frameCurrent.layout()

        # did the set of reported sensors change?
        current_sensors = set(self._readings.keys())
        shown_sensors = set(self._current_widgets.keys()) - {"time"}
        if {s.value for s in current_sensors} != shown_sensors:
            # remove all widgets from frameCurrent
            for w in self._current_widgets.values():
                w.setParent(None)
            self._current_widgets = {}

            # add time
            self._current_widgets["time"] = WidgetCurrentSensor("Time", "")
            layout.addWidget(self._current_widgets["time"])

            # loop known sensor types in display order
            for sensor, label in SENSOR_LABELS.items():
                if sensor in current_sensors:
                    widget = WidgetCurrentSensor(label, self._readings[sensor].unit)
                    self._current_widgets[sensor.value] = widget
                    layout.addWidget(widget)

        # set time
        if self._time is not None:
            self._current_widgets["time"].set_value(self._time.strftime("%Y-%m-%d\n%H:%M:%S"))
        else:
            self._current_widgets["time"].set_value("")

        # set values
        for sensor in SENSOR_LABELS:
            if sensor in self._readings:
                reading = self._readings[sensor]
                format = "%d" if sensor == WeatherSensors.RAIN else "%.2f"
                s = "N/A" if reading.value is None else format % reading.value
                widget = self._current_widgets[sensor.value]
                widget.set_value(s)
                widget.set_good(self._good)

        self._plot_history()

    def _plot_history(self) -> None:
        # one stacked subplot per sensor that has history, in the same order as the current-value
        # tiles; the sensor set (and therefore the subplot count) can change at runtime, so the
        # figure is rebuilt from scratch rather than reusing fixed axes
        sensors = [s for s in SENSOR_LABELS if self._history.get(s)]

        self.figure.clear()
        if not sensors:
            self.canvas.draw()
            return

        axes = self.figure.subplots(len(sensors), 1, sharex=True)
        if len(sensors) == 1:
            axes = [axes]
        for ax, sensor in zip(axes, sensors, strict=True):
            times, values = zip(*self._history[sensor], strict=True)
            ax.plot([t.to_datetime() for t in times], values, color="tab:blue")
            ax.set_ylabel(SENSOR_LABELS[sensor], fontsize="small")
            ax.grid(linestyle=":", alpha=0.5)
            ax.set_axisbelow(True)
        axes[-1].xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        self.figure.autofmt_xdate()
        self.figure.tight_layout()
        self.canvas.draw()


__all__ = ["WeatherWidget"]
