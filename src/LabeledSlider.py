""" Extended QSlider with additional functions.

This functionality is from: https://stackoverflow.com/questions/47494305/python-pyqt4-slider-with-tick-labels
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import QRect, QPoint, Qt, QObject
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QStyle, QStyleOptionSlider

from src.Slider import Slider


class LabeledSlider(QtWidgets.QWidget):
    """
    Extended QSlider with additional functions.

    This functionality is from: https://stackoverflow.com/questions/47494305/python-pyqt4-slider-with-tick-labels
    """

    def __init__(self, minimum, maximum, start, interval=1, orientation=Qt.Horizontal, labels=None, parent=None, objectname=None):
        """

        Parameters
        ----------
        minimum : int
            minimal value of the slider range
        maximum : int
            maximal value of the slider range
        start : int
            default position of the slider's handle, if outside minimum/maximum, it is set to the nearest value
        interval : int, default=1
            numerical distance between tick values
        orientation : Qt.Orientation, default=Qt.Horizontal
            orientation of the slider
        labels : list[str] or tuple[str], default=None
            labels for the individual ticks
        parent : QObject, optional
                the page the button is on
        objectname : str, optional
            name of the object, if it is supposed to be styled individually

        Raises
        ------
        TypeError
            if neither a list nor a tuple of strings is given as `labels`
        ValueError
            if the number of labels in `labels` doesn't match the range between `minimum` and `maximum`
            or if an invalid `orientation` is given
        """
        super(LabeledSlider, self).__init__(parent=parent)

        levels = range(minimum, maximum + interval, interval) if minimum < maximum \
            else range(minimum, maximum + interval*-1, interval*-1)
        if labels is not None:
            if not isinstance(labels, (tuple, list)):
                raise TypeError("<labels> is a list or tuple.")
            if len(labels) != len(levels):
                raise ValueError("Size of <labels> doesn't match levels.")
            self.levels = list(zip(levels, labels))
        else:
            levels = range(minimum, maximum + interval, interval) if minimum < maximum \
                else range(minimum, maximum + interval*-1, interval*-1)
            self.levels = list(zip(levels, map(str, levels)))

        if orientation == Qt.Horizontal:
            self.layout = QtWidgets.QVBoxLayout(self)
        elif orientation == Qt.Vertical:
            self.layout = QtWidgets.QHBoxLayout(self)
        else:
            raise ValueError("<orientation> wrong.")

        self.left_margin = 0
        self.top_margin = 0
        self.right_margin = 0
        self.bottom_margin = 0

        self.layout.setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

        self.sl = Slider(orientation, parent=parent)
        if objectname is not None:
            self.sl.setObjectName(objectname)
        self.sl.prepare_slider(minimum, maximum, start, tickpos=QtWidgets.QSlider.TicksBelow if orientation == Qt.Horizontal else QtWidgets.QSlider.TicksLeft)

        self.layout.addWidget(self.sl)

    def value(self):
        """
        Get the value of the slider according to the current handle position.
        Returns
        -------
        int
            current tick position of the handle
        """
        return self.sl.value()

    def paintEvent(self, event):
        """
        Paints the slider with ticks and tick-labels neatly.

        Parameters
        ----------
        event : QPaintEvent
        """
        super(LabeledSlider, self).paintEvent(event)

        style = self.sl.style()
        painter = QPainter(self)
        st_slider = QStyleOptionSlider()
        st_slider.initFrom(self.sl)
        st_slider.orientation = self.sl.orientation()

        length = style.pixelMetric(QStyle.PM_SliderLength, st_slider, self.sl)
        available = style.pixelMetric(QStyle.PM_SliderSpaceAvailable, st_slider, self.sl)

        for v, v_str in self.levels:

            # get the size of the label
            rect = painter.drawText(QRect(), Qt.TextDontPrint, v_str)

            if self.sl.orientation() == Qt.Horizontal:
                # I assume the offset is half the length of slider, therefore + length//2
                x_loc = QStyle.sliderPositionFromValue(self.sl.minimum(), self.sl.maximum(), v, available, self.sl.invertedAppearance()) + length // 2

                # left bound of the text = center - half of text width + L_margin
                left = x_loc - rect.width() // 2 + self.left_margin
                bottom = self.rect().bottom()

                # enlarge margins if clipping
                if v == self.sl.minimum():
                    if left <= 0:
                        self.left_margin = rect.width() // 2 - x_loc
                    if self.bottom_margin <= rect.height():
                        self.bottom_margin = rect.height()

                    self.layout.setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

                if v == self.sl.maximum() and rect.width() // 2 >= self.right_margin:
                    self.right_margin = rect.width() // 2
                    self.layout.setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

            else:
                y_loc = QStyle.sliderPositionFromValue(self.sl.minimum(), self.sl.maximum(), v, available, upsideDown=True) # , self.sl.invertedAppearance() todo

                bottom = y_loc + length // 2 + rect.height() // 2 + self.top_margin - 3
                # there is a 3 px offset that I can't attribute to any metric

                left = self.left_margin - rect.width()
                if left <= 0:
                    self.left_margin = rect.width() + 2
                    self.layout.setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

            pos = QPoint(left, bottom)
            painter.drawText(pos, v_str)
