from typing import Dict, Any, TYPE_CHECKING, List, Union

from pyobs.object import create_object

if TYPE_CHECKING:
    from pyobs_gui.basewidget import BaseWidget


class WidgetsMixin:
    def __init__(self):
        """Mixin for child widgets."""
        self._widgets_mixin: List[WidgetsMixin] = []

    def create_widget(self, config: Union[Dict[str, Any], type], **kwargs: Any) -> 'BaseWidget':
        """Creates new widget.

        Args:
            config: Config to create widget from.

        Returns:
            New widget.
        """
        from pyobs_gui.basewidget import BaseWidget

        # create it
        if isinstance(config, dict):
            widget = create_object(config, vfs=self.vfs, comm=self.comm, observer=self.observer, **kwargs)
        elif isinstance(config, type):
            widget = config(vfs=self.vfs, comm=self.comm, observer=self.observer, **kwargs)
        else:
            raise ValueError('Wrong type.')

        # check and return widget
        if isinstance(widget, BaseWidget):
            self._widgets_mixin.append(widget)
            return widget
        else:
            raise ValueError('Invalid widget.')

    async def open(self):
        """Open all widgets."""
        for widget in self._widgets_mixin:
            await widget.open()


__all__ = ['WidgetsMixin']
