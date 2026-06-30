from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel


class WatchedLabel(QLabel):
    text_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLabel {
                #background-color: black;
                #color: white;
                border: 0;
                border-radius: 3px;
                padding: 2px 4px;
            }
        """)

    def setText(self, text: str):
        super().setText(text)
        self.text_changed.emit(text)
