"""
This class creates a set of checkboxes.
"""
import datetime
from PySide6.QtWidgets import QHBoxLayout, QCheckBox


def make_answers(answer, qid, objectname=None, parent=None):
    """
    Create a set of checkboxes based on the given array of answers.

    Parameters
    ----------
    answer : str or list[str]
        answer possibilities
    qid : str
        id of the question
    objectname : str, optional
        name of the object, if it is supposed to be styled individually
    parent : QObject
        the page the question is on

    Returns
    -------
    QHBoxLayout
        created layout including the checkboxes
    list[QCheckBox]
        list of the created checkbox-objects
    """
    hbox = QHBoxLayout()
    list_of_cb = []
    if isinstance(answer, str):
        answer = [answer]  # to support questions with just one answer
    for a, answ in enumerate(answer):
        cb = CheckBox(f'{qid}_{a}', parent)
        if objectname is not None:
            cb.setObjectName(objectname)
        cb.setText(f'{answ} ')
        list_of_cb.append(cb)
        hbox.addWidget(cb)
    return hbox, list_of_cb


class CheckBox(QCheckBox):
    """Create a CheckBox with own ID"""
    def __init__(self, cid, parent=None):
        """Create a CheckBox with own ID

        Parameters
        ----------
        cid : str
            unique id of the CheckBox
        parent : QObject
            the page the question is on
        """
        QCheckBox.__init__(self, parent=parent)
        self.id = cid
        self.page = parent
        self.toggled.connect(self.log)

    def log(self):
        """Create a log entry."""
        print(f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Toggled {self.id} to {self.isChecked()}')
        self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Toggled {self.id} to {self.isChecked()}'
