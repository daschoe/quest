"""
A TextEdit editor that sends editingFinished events when the text was changed and focus is lost.
Original version (PyQt4): https://gist.github.com/hahastudio/4345418
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTextEdit


# noinspection PyUnresolvedReferences
class TextEdit(QTextEdit):
    """
    A modified QTextEdit field that sends editingFinished events when the text was changed and focus is lost.

    Attributes
    ----------
    editingFinished : pyqtSignal
        A signal that is emitted once the field lost focus and the text was modified.
    receivedFocus : pyqtSignal
        A signal that is emitted when the field was clicked.
    parent : QObject
        widget/layout this widget is embedded in

    Notes
    -----
    Original idea (PyQt4) by hahastudio [1]_

    .. [1] https://gist.github.com/hahastudio/4345418
    """

    editingFinished = Signal()
    receivedFocus = Signal()

    def __init__(self, parent=None):
        """

        Parameters
        ----------
        parent : QObject, opt
            widget/layout this widget is embedded in
        """
        super(TextEdit, self).__init__(parent)
        self._changed = False
        self.currentText = self.toPlainText()
        self.setTabChangesFocus(True)
        self.textChanged.connect(self._handle_text_changed)

    def focusInEvent(self, event):
        """The field is activated.

        Parameters
        ----------
        event : QFocusEvent
        """
        super(TextEdit, self).focusInEvent(event)
        self.receivedFocus.emit()
        self.currentText = self.toPlainText()

    def focusOutEvent(self, event):
        """Another field is activated.

        Parameters
        ----------
        event : QFocusEvent
        """
        if self.currentText != self.toPlainText():
            self.editingFinished.emit()
        super(TextEdit, self).focusOutEvent(event)

    def _handle_text_changed(self):
        self._changed = True

    def set_text_changed(self, state):
        """ The text has changed while the field was active.

        Parameters
        ----------
        state : bool
            True if the state has changed.
        """
        self._changed = state

    def text(self):
        """ Current text of the field.

        Returns
        -------
        str
            current text of the field
        """
        return self.toPlainText()
