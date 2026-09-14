from PySide6 import QtCore, QtWidgets  # type: ignore


class MoveStack(QtWidgets.QStackedWidget):
    """QStackedWidget sizes itself to the largest of all its pages by default, so
    TelescopeWidget's coordinate-type stack (RA/Dec, Alt/Az, Orbit Elements, ...) reserves width
    for its widest page even when a narrower one is shown -- and every new coordinate-type page
    added in the future raises that floor further, permanently, for every module using this
    widget. Size to the current page instead; call updateGeometry() after switching pages so the
    new size actually takes effect."""

    def sizeHint(self) -> QtCore.QSize:
        current = self.currentWidget()
        return current.sizeHint() if current is not None else super().sizeHint()

    def minimumSizeHint(self) -> QtCore.QSize:
        current = self.currentWidget()
        return current.minimumSizeHint() if current is not None else super().minimumSizeHint()
