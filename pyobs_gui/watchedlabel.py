from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel


class WatchedLabel(QLabel):
    text_changed = Signal(str)

    def setText(self, text: str):
        super().setText(text)
        self.text_changed.emit(text)
