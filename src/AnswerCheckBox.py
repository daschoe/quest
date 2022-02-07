"""
This class creates a set of checkboxes.
"""
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox


def make_answers(answer, objectname=None):
    """
    Create a set of checkboxes based on the given array of answers.

    Parameters
    ----------
    answer : str or list[str]
        answer possibilities
    objectname : str, optional
                name of the object, if it is supposed to be styled individually

    Returns
    -------
    QHBoxLayout
        created layout including the checkboxes
    list[QCheckBox]
        list of the created checkbox-objects
    """
    hbox = QHBoxLayout()
    list_of_cb = []
    if type(answer) is str:
        answer = [answer]  # to support questions with just one answer
    for a in range(0, len(answer)):
        cb = QCheckBox()
        if objectname is not None:
            cb.setObjectName(objectname)
        cb.setText(answer[a] + " ")
        list_of_cb.append(cb)
        hbox.addWidget(cb)
    return hbox, list_of_cb
