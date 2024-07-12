"""
This class creates a set of radiobuttons.
"""
from PySide6.QtWidgets import QHBoxLayout, QRadioButton, QButtonGroup


def make_answers(answer, parent, qid, objectname=None, start_answer_id=0, log=True):
    """
    Create a set of radiobuttons based on the given array of answers.

    Parameters
    ----------
    answer : str or list[str]
        answer possibilities
    parent : QObject
                the page the button is on
    qid : str
        id of the question
    objectname : str, optional
        name of the object, if it is supposed to be styled individually
    start_answer_id : int, default=0
        first answer index in csv file (-1 is no answer)
    log : bool, default=True
        whether a log is written for this element (False for RadioMatix)

    Returns
    -------
    QHBoxLayout
        created layout including the checkboxes
    QButtonGroup
        group holding the created radiobutton objects, only one answer in this group can be chosen
    """
    hbox = QHBoxLayout()
    bg = QButtonGroup(hbox)
    cnt = start_answer_id
    if type(answer) is str:
        answer = [answer]  # to support questions with just one answer
    for a in range(0, len(answer)):
        rb = QRadioButton(answer[a])
        if objectname is not None:
            rb.setObjectName(objectname)
        if not log and a == 0:
            rb.setObjectName("RadioMatrixLeft")
        elif not log and a == len(answer) - 1:
            rb.setObjectName("RadioMatrixRight")
        hbox.addWidget(rb)
        bg.addButton(rb, cnt)
        cnt += 1
    if log:
        bg.buttonClicked.connect(lambda: parent.log(qid, bg))
    else:  # for RadioMatrix
        bg.buttonClicked.connect(lambda: parent.parent().log(qid, bg))
    return hbox, bg
