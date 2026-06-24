from typing import Self

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QLabel, QLineEdit, QSpinBox, QDoubleSpinBox

from .watchedlabel import WatchedLabel


class ModifiedMixin:
    """Mixin for QLineEdit, QSpinBox, QDoubleSpinBox subclasses."""

    committed = Signal(object)

    _NORMAL_STYLE = ""
    _MODIFIED_STYLE = "background-color: #ff0000;"

    def init_modified(self, label: WatchedLabel | None = None) -> Self:
        self._ref_label = label
        if label is not None:
            label.text_changed.connect(self._mark_modified)
        return self

    def _is_dirty(self) -> bool:
        if self._ref_label is None:
            return True
        ref = self._ref_label.text()
        return self._current_value_str() != ref

    def _current_value_str(self) -> str:
        raise NotImplementedError

    def _mark_modified(self, _=None):
        self.setStyleSheet(self._MODIFIED_STYLE if self._is_dirty() else self._NORMAL_STYLE)

    def _commit(self):
        self.setStyleSheet(self._NORMAL_STYLE)
        self.committed.emit(self)


class ModifiedLineEdit(ModifiedMixin, QLineEdit):
    committed = Signal(object)

    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        self.init_modified()
        self.textChanged.connect(self._mark_modified)
        self.returnPressed.connect(self._commit)

    def _current_value_str(self) -> str:
        return self.text()


class ModifiedSpinBox(ModifiedMixin, QSpinBox):
    committed = Signal(object)

    def __init__(self, parent=None):
        QSpinBox.__init__(self, parent)
        self.init_modified()
        self.valueChanged.connect(self._mark_modified)

    def _current_value_str(self) -> str:
        return str(self.value())

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._commit()
        else:
            super().keyPressEvent(event)


class ModifiedDoubleSpinBox(ModifiedMixin, QDoubleSpinBox):
    committed = Signal(object)

    def __init__(self, parent=None):
        QDoubleSpinBox.__init__(self, parent)
        self.init_modified()
        self.valueChanged.connect(self._mark_modified)

    def _current_value_str(self) -> str:
        return str(self.value())

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._commit()
        else:
            super().keyPressEvent(event)
