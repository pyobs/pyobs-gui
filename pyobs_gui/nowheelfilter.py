from PySide6 import QtCore, QtWidgets  # type: ignore


class NoWheelWhenUnfocused(QtCore.QObject):
    """Application-wide event filter: a spin box/combo box/slider that doesn't have keyboard focus
    ignores mouse wheel events instead of changing its value, and forwards the wheel event to the
    nearest scrollable ancestor instead -- so scrolling a page that happens to pass the cursor over
    one of these controls scrolls the page, not the control underneath the cursor. Confirmed a real
    problem, not a hypothetical one: sending a wheel event to an unfocused QDoubleSpinBox changed
    its value before this filter existed (see
    ../specs/2026-09-14-stacked-widget-scroll-fallback.md, risk #1) -- became a live concern once
    stackedWidget started living inside a QScrollArea, where a normal "scroll the page" gesture can
    easily pass over a spin/combo box.

    Install once, on QApplication (see gui.py's GUI.new_event_loop()). Focusing the control
    (click or Tab) restores the normal wheel-changes-value behavior, same as before this filter
    existed -- this only changes what happens when the control merely has the mouse over it.
    """

    _WHEEL_ADJUSTABLE = (QtWidgets.QAbstractSpinBox, QtWidgets.QComboBox, QtWidgets.QAbstractSlider)

    def __init__(self) -> None:
        super().__init__()
        # re-entrancy guard: sendEvent() below re-enters this same app-wide filter (nested scroll
        # areas are common -- e.g. CameraWidget's own left-panel scrollArea sits between a spinbox
        # and the outer stackedWidgetScroll), and if the forwarded copy also lands on an unfocused
        # adjustable control, that's infinite recursion without this. While forwarding, every event
        # just passes through untouched instead of being re-evaluated.
        self._forwarding = False

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if self._forwarding:
            return False
        if (
            event.type() == QtCore.QEvent.Type.Wheel
            and isinstance(watched, self._WHEEL_ADJUSTABLE)
            and not watched.hasFocus()
        ):
            scroll_area = self._nearest_scroll_area(watched)
            if scroll_area is not None:
                self._forwarding = True
                try:
                    QtWidgets.QApplication.sendEvent(scroll_area.viewport(), event)
                finally:
                    self._forwarding = False
            return True  # swallow the original either way -- never let it reach the control itself
        return False

    @staticmethod
    def _nearest_scroll_area(widget: QtWidgets.QWidget) -> QtWidgets.QAbstractScrollArea | None:
        parent = widget.parentWidget()
        while parent is not None:
            if isinstance(parent, QtWidgets.QAbstractScrollArea):
                return parent
            parent = parent.parentWidget()
        return None
