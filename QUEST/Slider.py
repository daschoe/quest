""" Extended QSlider with additional functions.

The idea was to make it possible to click on the slider bar and the slider snaps to the nearest tick from the clicking
position - a function that's not possible with QSlider.
The functionality is adapted from: https://www.queryxchange.com/q/27_52689047/moving-qslider-to-mouse-click-position/
"""
from math import ceil
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QSlider, QStyle, QStyleOptionSlider


class Slider(QSlider):
    """ Extension of QSlider, which is responding better to a click.

    Attributes
    ----------
    strokewidth : int, default=1
        width of the tickmark strokes
    strokecolor: QColor, default=QColor("black")
        color of the tickmark strokes
    strokewidth_disabled : int, default=None
        width of the tickmark strokes when the slider is disabled
    strokecolor_disabled : QColor, default=None
        color of the tickmark strokes when the slider is disabled
    moving : boolean, default=False
        indicates if the handle is currently moving
    mushra_stopped : pyqtSignal
        indicates when the slider handle stopped moving, so that the value can be logged

    Notes
    -----
    The functionality is adapted from: https://www.queryxchange.com/q/27_52689047/moving-qslider-to-mouse-click-position/
    """
    strokewidth = 1
    strokecolor = QColor("black")
    strokewidth_disabled = None
    strokecolor_disabled = None
    moving = False
    mushra_stopped = Signal(str)
    moved = False
    mouse_down = False
    prev = None
    _min = None
    _max = None
    start = None
    step = None
    sid = None
    tick_dist = None

    def paintEvent(self, event):
        """
        Workaround to change the size of the slider to make it more usable for touch interfaces, but also draw the tick
        marks accordingly.
        Used this as a reference: https://stackoverflow.com/questions/27531542/tick-marks-disappear-on-styled-qslider

        Parameters
        ----------
        event : QPaintEvent
        """
        super(Slider, self).paintEvent(event)
        p = QPainter(self)
        pen = QPen()
        if self.isEnabled():
            pen.setWidth(self.strokewidth)
            pen.setColor(self.strokecolor)
        else:
            pen.setWidth(self.strokewidth_disabled)
            pen.setColor(self.strokecolor_disabled)
        p.setPen(pen)
        opt = QStyleOptionSlider()
        opt.initFrom(self)
        opt.orientation = self.orientation()

        groove = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderGroove, self)
        handle = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle, self)

        if self.tickPosition() != QSlider.TickPosition.NoTicks:
            for i in range(0, self.maximum() - self.minimum() + 1, self.tickInterval()):
                h = 10
                magic_height = 4
                if self.orientation() == Qt.Orientation.Horizontal:
                    x = round(i / (self.maximum() - self.minimum()) * self.width())
                    if x == 0:
                        x += ceil(0.5 * p.pen().width())
                        if p.pen().width() % 2 == 0:
                            x += 1
                    elif x >= self.width():
                        x = self.width() - ceil(0.5 * p.pen().width()) - 1
                    else:
                        x -= ceil(0.5 * p.pen().width())
                    if (self.tickPosition() == QSlider.TickPosition.TicksBothSides) or (self.tickPosition() == QSlider.TickPosition.TicksAbove):
                        y = groove.top() - ceil(0.5 * p.pen().width())
                        p.drawLine(x, y + h, x, y - magic_height)
                    if (self.tickPosition() == QSlider.TickPosition.TicksBothSides) or (self.tickPosition() == QSlider.TickPosition.TicksBelow):
                        y = groove.bottom()
                        if p.pen().width() > 1:
                            y += ceil(0.5 * p.pen().width())
                        p.drawLine(x, y + h, x, y - magic_height)
                elif self.orientation() == Qt.Orientation.Vertical:
                    y = round(i / (self.maximum() - self.minimum()) * groove.height())
                    if y == groove.height():  # lowest mark
                        y -= ceil(0.5 * p.pen().width()) - 1
                    elif y == 0:
                        y += ceil(0.5 * p.pen().width())
                        if p.pen().width() % 2 == 0:
                            y += 1
                    else:
                        y -= ceil(0.5 * p.pen().width())
                    if (self.tickPosition() == QSlider.TickPosition.TicksBothSides) or (self.tickPosition() == QSlider.TickPosition.TicksLeft):
                        x = groove.left() + handle.width()
                        if p.pen().width() > 1:
                            x -= ceil(0.5 * p.pen().width())
                        p.drawLine(x, y, x - magic_height, y)
                    if (self.tickPosition() == QSlider.TickPosition.TicksBothSides) or (self.tickPosition() == QSlider.TickPosition.TicksRight):
                        x = groove.right() - handle.width()
                        if p.pen().width() > 1:
                            x += ceil(0.5 * p.pen().width())
                        p.drawLine(x, y, x + magic_height, y)

    def mousePressEvent(self, event):
        """
        Override of the original function to enable snapping the slider to the cursor on clicking the slider bar.

        Parameters
        ----------
        event : QMouseEvent
            event that occurred, only presses of the left mouse button are of relevance here
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.orientation() == Qt.Orientation.Horizontal:
                self.blockSignals(True)
            val = self.pixel_pos_to_range_value(event.position())
            self.moved = True
            self.mouse_down = True
            if self.value() != val: # TODO?
                self.setValue(val)
                self.blockSignals(False)
                if self.orientation() == Qt.Orientation.Horizontal:
                    self.blockSignals(True)

    def mouseMoveEvent(self, event):
        """Drag slider handle event, snap handle to tick positions.

        Parameters
        ----------
        event : QMouseEvent
            event that occurred, only presses of the left mouse button are of relevance here
        """
        if self.mouse_down:
            if self.orientation() == Qt.Orientation.Horizontal:
                self.blockSignals(True)
            val = self.pixel_pos_to_range_value(event.position())
            if self.value() != val:
                self.setValue(val)
                self.moving = True

    def mouseReleaseEvent(self, event):
        """End of move event, populate new value.

        Parameters
        ----------
        event : QMouseEvent
            event that occurred, only presses of the left mouse button are of relevance here
        """
        if self.orientation() == Qt.Orientation.Horizontal:
            self.blockSignals(True)
        self.mouse_down = False
        if self.moving:
            val = self.pixel_pos_to_range_value(event.position())
            self.setValue(val)
            self.moving = False
            self.blockSignals(False)
            # print(f'New val {val} unblocked (move)')
            self.valueChanged.emit(val)
            self.mushra_stopped.emit(self.sid)
            if self.orientation() == Qt.Orientation.Horizontal:
                self.blockSignals(True)

    def keyPressEvent(self, event):
        """Register the previous value

        Parameters
        ----------
        event : QKeyEvent
            event that occurred, only presses of the arrow keys are relevant
        """
        if self.orientation() == Qt.Orientation.Horizontal:
            self.blockSignals(True)
        if event.key() in [Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right]:
            self.prev = self.value()
            super(Slider, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Keyboard press get released and the new value gets populated.

        Parameters
        ----------
        event : QKeyEvent
            event that occurred, only presses of the arrow keys are relevant
        """
        if self.orientation() == Qt.Orientation.Horizontal:
            self.blockSignals(True)
        if event.key() in [Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right]:
            super(Slider, self).keyReleaseEvent(event)
            if self.value() != self.prev:
                self.blockSignals(False)
                # print(f'New val {self.value()} unblocked (key)')
                self.valueChanged.emit(self.value())
                self.mushra_stopped.emit(self.sid)
                if self.orientation() == Qt.Orientation.Horizontal:
                    self.blockSignals(True)

    def value(self):
        """ Return the current value of the handle.

        Returns
        -------
        int or float : current handle position in the range
        """
        if not self.invertedAppearance():
            value = self.minimum() + self._min + super(Slider, self).value() * self.step
            if int(self.step) != float(self.step):  # float step size
                value = round(value, str(self.step)[::-1].find('.'))
            return value if int(self.step) != float(self.step) else int(value)
        value = self._min + super(Slider, self).value() * self.step  # super(Slider, self).value() #TODO float?TODO TODO TODO FALSCH!!!
        # print("new value", value)
        return value if int(self.step) != float(self.step) else int(value)

    def get_moved(self):
        """ Return whether the slider has been touched by the user.

        Returns
        -------
        boolean - if the slider handle has been moved
        """
        return self.moved

    def pixel_pos_to_range_value(self, pos):
        """
        Helper to move the slider to the cursor independently of the OS and stylesheet.

        Parameters
        ----------
        pos : QPoint
            position of the click of the event

        Returns
        -------
        int
            calculated value of the slider position for that click
        """
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle, self)

        if self.orientation() == Qt.Orientation.Horizontal:
            slider_length = sr.width()
            slider_min = gr.x()
            slider_max = gr.right() - slider_length + 1
        else:
            slider_length = sr.height()
            slider_min = gr.y()
            slider_max = gr.bottom() - slider_length + 1
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Orientation.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - slider_min, slider_max - slider_min, opt.upsideDown)

    def prepare_slider(self, min_val, max_val, start, step=1, tick_interval=1, tickpos=QSlider.TickPosition.TicksBelow, sid=None):
        """
        Set all parameters of the slider at once, to reduce repeating bulky code in the main gui class.

        Parameters
        ----------
        min_val : int
            minimum value on the tick scale
        max_val : int
            maximum value on the tick scale
        start : int
            default starting point of the slider, if outside of min_val and max_val, it will be set to the closest of them
        step :  int, default=1
            step size of slider
        tick_interval :  int, default=1
            distance between visible ticks of slider
        tickpos : QSlider.TickPosition, default=QSlider.TicksBelow
            position of tickmarks (if any), see also PySide6.QtWidgets.QSlider
        """
        self._min = min_val
        self._max = max_val
        self.step = step
        self.start = start
        self.prev = None
        if self.orientation() == Qt.Orientation.Horizontal:
            self.blockSignals(True)  # don't spam new values on move, click and release
        if self._min > self._max:
            self.setInvertedAppearance(True)
            self.setMaximum(0)
            self.setMinimum(int((max_val - min_val) / self.step))
        else:
            self.setMinimum(0)
            self.setMaximum(int((max_val - min_val) / self.step))
        self.setValue(round((self.start - self._min) / self.step))
        self.setTickInterval(tick_interval)
        # TODO self.tick_dist = int(tick_interval)
        self.setSingleStep(1)
        self.setTickPosition(tickpos)
        self.sid = sid

        if hasattr(self.parent(), "page_log"):  # awkward workaround to reference "Page"
            sheet = self.parent().parent().styleSheet()
            sheet = sheet[sheet.find("Slider::groove"):]
            sheet = sheet[:sheet.find("}")]
            width = 1
            color = QColor("black")
            if sheet.find("border-width:") > -1:
                width = sheet[sheet.find("border-width:") + len("border-width:"):sheet.find("px", sheet.find("border-width:"))].strip(" ")
            elif sheet.find("border:") > -1:
                border = sheet[sheet.find("border:") + len("border:"):sheet.find(";", sheet.find("border:"))].strip(" ")
                border = border.split(" ")
                for entry in border:
                    if entry.find("px") > -1:
                        width = entry.strip(" px")
            if sheet.find("border-color:") > -1:
                color = sheet[sheet.find("border-color:") + len("border-color:"):sheet.find(";", sheet.find("border-color:"))].strip(" ")
            elif sheet.find("border:") > -1:
                border = sheet[sheet.find("border:") + len("border:"):sheet.find(";", sheet.find("border:"))].strip(" ")
                border = border.split(" ")
                for entry in border:
                    if QColor.isValidColorName(entry):
                        color = entry
            self.strokewidth = int(width)
            self.strokecolor = QColor(color)

            sheet = self.parent().parent().styleSheet()
            sheet = sheet[sheet.find("Slider::groove:disabled"):]
            sheet = sheet[:sheet.find("}")]
            width_disabled = self.strokewidth
            color_disabled = self.strokecolor
            if sheet.find("border-width:") > -1:
                width_disabled = sheet[sheet.find("border-width:") + len("border-width:"):sheet.find("px", sheet.find(
                    "border-width:"))].strip(" ")
            elif sheet.find("border:") > -1:
                border = sheet[sheet.find("border:") + len("border:"):sheet.find(";", sheet.find("border:"))].strip(" ")
                border = border.split(" ")
                for entry in border:
                    if entry.find("px") > -1:
                        width_disabled = entry.strip(" px")
            if sheet.find("border-color:") > -1:
                color_disabled = sheet[sheet.find("border-color:") + len("border-color:"):sheet.find(";", sheet.find(
                    "border-color:"))].strip(" ")
            elif sheet.find("border:") > -1:
                border = sheet[sheet.find("border:") + len("border:"):sheet.find(";", sheet.find("border:"))].strip(" ")
                border = border.split(" ")
                for entry in border:
                    if QColor.isValidColorName(entry):
                        color_disabled = entry
            self.strokewidth_disabled = int(width_disabled)
            self.strokecolor_disabled = QColor(color_disabled)

        if self.objectName() != "":
            sheet = self.parent().parent().styleSheet()
            sheet = sheet[sheet.find(f'Slider#{self.objectName()}::groove'):]
            sheet = sheet[:sheet.find("}")]
            width = 1
            color = QColor("black")
            if sheet.find("border-width:") > -1:
                width = sheet[sheet.find("border-width:") + len("border-width:"):sheet.find("px", sheet.find("border-width:"))].strip(" ")
            elif sheet.find("border:") > -1:
                border = sheet[sheet.find("border:") + len("border:"):sheet.find(";", sheet.find("border:"))].strip(" ")
                border = border.split(" ")
                for entry in border:
                    if entry.find("px") > -1:
                        width = entry.strip(" px")
            if sheet.find("border-color:") > -1:
                color = sheet[sheet.find("border-color:") + len("border-color:"):sheet.find(";", sheet.find("border-color:"))].strip(" ")
            elif sheet.find("border:") > -1:
                border = sheet[sheet.find("border:") + len("border:"):sheet.find(";", sheet.find("border:"))].strip(" ")
                border = border.split(" ")
                for entry in border:
                    if QColor.isValidColorName(entry):
                        color = entry
            self.strokewidth = int(width)
            self.strokecolor = QColor(color)

            sheet = self.parent().parent().styleSheet()
            sheet = sheet[sheet.find(f'Slider#{self.objectName()}::groove:disabled'):]
            sheet = sheet[:sheet.find("}")]
            width_disabled = self.strokewidth
            color_disabled = self.strokecolor
            if sheet.find("border-width:") > -1:
                width_disabled = sheet[sheet.find("border-width:") + len("border-width:"):sheet.find("px", sheet.find("border-width:"))].strip(" ")
            elif sheet.find("border:") > -1:
                border = sheet[sheet.find("border:") + len("border:"):sheet.find(";", sheet.find("border:"))].strip(" ")
                border = border.split(" ")
                for entry in border:
                    if entry.find("px") > -1:
                        width_disabled = entry.strip(" px")
            if sheet.find("border-color:") > -1:
                color_disabled = sheet[sheet.find("border-color:") + len("border-color:"):sheet.find(";", sheet.find("border-color:"))].strip(" ")
            elif sheet.find("border:") > -1:
                border = sheet[sheet.find("border:") + len("border:"):sheet.find(";", sheet.find("border:"))].strip(" ")
                border = border.split(" ")
                for entry in border:
                    if QColor.isValidColorName(entry):
                        color_disabled = entry
            self.strokewidth_disabled = int(width_disabled)
            self.strokecolor_disabled = QColor(color_disabled)
