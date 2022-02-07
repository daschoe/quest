"""Customized MessageBox such that the errors and warnings are more easily readable."""

from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QMessageBox, QTextEdit


class ResizeMessageBox(QMessageBox):
    """ Self-resizing MessageBox.
    From https://stackoverflow.com/a/9969700
    """
    def __init__(self):
        super(ResizeMessageBox, self).__init__()

    def resizeEvent(self, event):
        """ Resize the details' field if necessary.

        Parameters
        ----------
        event : QResizeEvent
        """
        super(ResizeMessageBox, self).resizeEvent(event)
        details_box = self.findChild(QTextEdit)
        if details_box is not None:
            details_box.setFixedSize(details_box.sizeHint().width()*2, details_box.sizeHint().height())
