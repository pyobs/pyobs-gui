import logging
import os

from pyobs.interfaces import ICooling
from pyobs_gui.basewidget import BaseWidget
from .qt.widgetfitsheaders import Ui_WidgetFitsHeaders


log = logging.getLogger(__name__)


class WidgetFitsHeaders(BaseWidget, Ui_WidgetFitsHeaders):
    def __init__(self, module, comm, parent=None):
        BaseWidget.__init__(self, parent=parent)
        self.setupUi(self)
        self.module = module    # type: ICooling
        self.comm = comm        # type: Comm

        # this only works in Linux
        try:
            # set current username
            import pwd
            self.textUser.setText(pwd.getpwuid(os.getuid()).pw_name)
        except ModuleNotFoundError:
            pass

    def get_fits_headers(self) -> dict:
        """Returns FITS header for the current status of the telescope.

        Returns:
            Dictionary containing FITS headers.
        """
        return {
            'OBJECT': (self.textObject.text(), 'Observed object'),
            'PROPID': (self.textProject.text(), 'Proposal ID'),
            'USER': (self.textUser.text(), 'Name of user')
        }
