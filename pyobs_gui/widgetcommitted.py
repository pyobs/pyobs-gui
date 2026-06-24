from PySide6.QtWidgets import QLineEdit, QSpinBox, QDoubleSpinBox, QLabel
from PySide6.QtCore import Signal, QObject, QEvent, Qt


class WidgetCommitted(QObject):
    """
    Companion object attached to a widget. Emits `committed` when the
    user presses Enter after modifying the value.
    """

    committed = Signal(object)  # emits the widget itself

    _NORMAL_STYLE = ""
    _MODIFIED_STYLE = "background-color: #ffcccc;"

    def __init__(self, widget: QObject, label: QLabel = None):
        super().__init__(widget)
        self._widget = widget
        self._label = label

        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(self._mark_modified)
            widget.returnPressed.connect(self._commit)

        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.valueChanged.connect(self._mark_modified)
            widget.installEventFilter(self)

    def _is_dirty(self) -> bool:
        if self._label is None:
            return True
        w = self._widget
        ref = self._label.text()
        if isinstance(w, QLineEdit):
            return w.text() != ref
        elif isinstance(w, QDoubleSpinBox):
            try:
                return w.value() != float(ref)
            except ValueError:
                return True
        elif isinstance(w, QSpinBox):
            try:
                return w.value() != int(ref)
            except ValueError:
                return True
        return True

    def _mark_modified(self, _=None):
        if self._is_dirty():
            self._widget.setStyleSheet(self._MODIFIED_STYLE)
        else:
            self._widget.setStyleSheet(self._NORMAL_STYLE)

    def _commit(self):
        self._widget.setStyleSheet(self._NORMAL_STYLE)
        self.committed.emit(self._widget)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self._commit()
                return True
        return False
