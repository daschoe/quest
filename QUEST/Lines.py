""" Helper to create lines.

These classes are used to create neat lines in PySide6, which can be used e.g. as separators.
The idea is adapted from:
https://stackoverflow.com/questions/5671354/how-to-programmatically-make-a-horizontal-line-in-qt
"""

from PySide6.QtWidgets import QFrame


class QHLine(QFrame):
    """
    Creates a horizontal line, spanning the whole layout component.
    """

    def __init__(self, objectname=None):
        """
        Parameters
        ----------
        objectname : str, optional
                name of the object, if it is supposed to be styled individually
        """
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        if objectname is not None:
            self.setObjectName(objectname)


class QVLine(QFrame):
    """
    Creates a vertical line, spanning the whole layout component.
    """

    def __init__(self, objectname=None):
        """
        Parameters
        ----------
        objectname : str, optional
                name of the object, if it is supposed to be styled individually
        """
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        if objectname is not None:
            self.setObjectName(objectname)
