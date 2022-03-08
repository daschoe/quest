"""A question type to display an image in the questionnaire."""

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel


class Image(QLabel):
    """An Image to display"""

    def __init__(self, file, x=None, y=None, width=None, height=None, parent=None, objectname=None):
        """
        An image defined in size and position.

        Parameters
        ----------
        file : str
            image file to display
        x : int, opt
            x coordinate of top left corner (to the right)
        y : int, opt
            y coordinate of top left corner (down)
        width : int, optional
            width in display
        height : int, optional
            height of display
        parent : QObject
                the page the image is on
        objectname : str, optional
            name of the object, if it is supposed to be styled individually
        """
        QLabel.__init__(self, parent=parent)

        if objectname is not None:
            self.setObjectName(objectname)
            self.name = objectname
        else:
            self.name = None
            self.setStyleSheet("QLabel{margin: 0; padding: 0;}")

        pixmap = QPixmap(file)
        if width is None:
            width = pixmap.width()
        if height is None:
            height = pixmap.height()
        pixmap = pixmap.scaled(int(width), int(height))
        self.setPixmap(pixmap)
        self.setFixedWidth(int(width))
        self.setFixedHeight(int(height))
        if x is not None and y is not None:
            self.move(int(x), int(y))
