"""
This class creates a Slider.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget

from src.LabeledSlider import LabeledSlider
from src.Slider import Slider


def make_answers(labelled, qid, smin, smax, sstart=0, sstep=1, tiv=1, header=None, label=None, parent=None, objectname=""):
    """
        Create a slider based on the given parameters.

        Parameters
        ----------<
        labelled : bool
            if True each tick gets a numerical label; if False no tick labels are used.
        qid : str
            id of the question
        smin : int
            the lowest tick value
        smax : int
            the highest tick value
        sstart : int, default=0
            starting position of handle (if <smin, smin is chosen, if >smax, smax is chosen)
        sstep : int, default=1
            difference between two successive values
        tiv : int, default=1
            difference between two successive tick labels
        header : list[str], optional
            array of strings to put above the slider
        label : list[str]
            label to use for tick marks (if labelled=True)
        parent : QObject
                the page the button is on
        objectname : str, optional
            name of the object, if it is supposed to be styled individually

        Returns
        -------
        QVBoxLayout or LabeledSlider or Slider
            the layout including the slider and the header or the slider object itself
        LabeledSlider or Slider
            the slider object itself
    """
    if labelled:
        tiv = sstep  # TODO integrieren
        slider = LabeledSlider(minimum=smin, maximum=smax, start=sstart, step=sstep, tick_interval=tiv, labels=label, parent=parent, objectname=objectname)
        slider.sl.valueChanged.connect(lambda: parent.log(qid, slider))
    else:
        slider = Slider(Qt.Orientation.Horizontal, parent=parent)
        if objectname != "":
            slider.setObjectName(objectname)
        slider.prepare_slider(min_val=smin, max_val=smax, start=sstart, step=sstep, sid=qid)
        slider.valueChanged.connect(lambda: parent.log(qid, slider))
    if header is not None:
        layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        for h in range(0, len(header) - 1):
            lbl = QLabel()
            lbl.setText(header[h])
            lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            lbl.setObjectName("SliderHeader")
            header_layout.addWidget(lbl)
            header_layout.addStretch()
        lbl = QLabel()
        lbl.setText(header[-1])
        lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        lbl.setObjectName("SliderHeader")
        header_layout.addWidget(lbl)
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget)
        layout.addWidget(slider)
        return layout, slider
    else:
        return slider, slider
