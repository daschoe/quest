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

    def __init__(self, minimum, maximum, start, step=1, orientation=Qt.Horizontal, labels=None, parent=None, objectname=None):
        """

        Parameters
        ----------
        minimum : int
            minimal value of the slider range
        maximum : int
            maximal value of the slider range
        start : int
            default position of the slider's handle, if outside minimum/maximum, it is set to the nearest value
        step : int, default=1
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

        levels = range(int((maximum-minimum)/step)+1) if minimum < maximum \
            else range((int((maximum-minimum)/step)*-1+1))
        if labels is not None:
            if not isinstance(labels, (tuple, list)):
                raise TypeError("<labels> is a list or tuple.")
            if len(labels) != len(levels) and not isinstance(labels[0], (tuple, list)):
                raise ValueError("Size of <labels> doesn't match levels.")
            if not isinstance(labels[0], (tuple, list)):
                self.levels = list(zip(levels, labels))
            else:
                new_labels = [""] * len(levels)
                for pair in labels:
                    new_labels[int(abs(pair[0]-minimum)/step)] = pair[1]
                self.levels = list(zip(levels, new_labels))
        else:
            labels = self.create_range(minimum, maximum, step)
            # levels = range(minimum, maximum + step, step) if minimum < maximum \
            #    else range(minimum, maximum + step * -1, step * -1)
            self.levels = list(zip(levels, map(str, labels)))

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
        self.sl.prepare_slider(minimum, maximum, start, step, tickpos=QtWidgets.QSlider.TicksBelow if orientation == Qt.Horizontal else QtWidgets.QSlider.TicksLeft)

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
            if type(v_str) != str:
                v_str = str(v_str)
            rect = painter.drawText(QRect(), Qt.TextDontPrint | Qt.TextDontClip, v_str)
            rect.setHeight(int(rect.height()*1.5))

            if self.sl.orientation() == Qt.Horizontal:
                # I assume the offset is half the length of slider, therefore + length//2
                x_loc = QStyle.sliderPositionFromValue(self.sl.minimum(), self.sl.maximum(), v, available, self.sl.invertedAppearance()) + length // 2

                # left bound of the text = center - half of text width + L_margin
                left = x_loc - int(rect.width() / 2) + self.left_margin
                bottom = self.rect().bottom() - int(self.rect().height()/6)

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
                y_loc = QStyle.sliderPositionFromValue(self.sl.minimum(), self.sl.maximum(), v, available, upsideDown=True)  # , self.sl.invertedAppearance() todo

                bottom = y_loc + length // 2 + rect.height() // 2 + self.top_margin - 3
                # there is a 3 px offset that I can't attribute to any metric

                left = self.left_margin - rect.width()
                if left <= 0:
                    self.left_margin = rect.width() + 2
                    self.layout.setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

            pos = QPoint(left, bottom)
            painter.drawText(pos, str(v_str))

    def create_range(self, minimum, maximum, step):
        """
        Create a range with floats.

        Parameters
        ----------
        minimum : int
            minimum value
        maximum : int
            maximum value
        step : float
            stepwidth

        Returns
        -------
        list<int>
            created range
        """
        vals = []
        if int(step) == float(step) and int(minimum) == float(minimum) and int(maximum) == float(maximum):
            step = int(step)
            minimum = int(minimum)
            maximum = int(maximum)
            vals = range(minimum, maximum + step, step) if minimum < maximum else range(minimum, maximum - step, -1 * step)
        else:
            tmp = None
            minimum = float(minimum)
            if minimum > maximum:
                tmp = minimum
                minimum = maximum
                maximum = tmp
            while minimum <= maximum:
                if int(minimum) == float(minimum):
                    vals.append(int(minimum))
                else:
                    vals.append(round(minimum, str(step)[::-1].find('.')) if round(minimum, str(step)[::-1].find('.')) != -0.0 else 0.0)
                minimum += step
            if tmp is not None:
                vals.reverse()
        return vals
