"""A matrix of questions with radiobuttons as answers using all one set of answer possibilities."""
import random

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFormLayout, QLabel, QHBoxLayout

from src.AnswerRadioButton import make_answers


class RadioMatrix(QWidget):
    """A matrix of questions with radiobuttons as answers using all one set of answer possibilities."""

    def __init__(self, questions, answers, qid, start_answer_id=0, parent=None, objectname=None, randomize=False):
        """
        Parameters
        ----------
        questions : str or list[str]
            list of questions/rows
        answers : str or list[str]
            answer possibilities
        qid : str
            id of the question
        start_answer_id : int, default=0
            first answer index in csv file (-1 is no answer)
        parent : QObject, optional
                    the page the button is on
        objectname : str, optional
            name of the object, if it is supposed to be styled individually
        randomize : bool, default=False
            if True, randomize the order of the questions
        """
        QWidget.__init__(self, parent=parent)
        if objectname is not None:
            self.setObjectName(objectname)
            self.name = objectname
        else:
            self.name = None
        self.id = qid

        if type(questions) is str:
            questions = [questions]
        if type(answers) is str:
            answers = [answers]

        if randomize is True:
            random.seed(self.parent().parent().start.__str__())  # uses starting time
            self.id_order = [i+1 for i in range(0, len(questions))]
            random.shuffle(self.id_order)
        else:
            self.id_order = [i+1 for i in range(0, len(questions))]

        layout = QFormLayout()
        headerlbl = QLabel("")
        headerlbl.setObjectName("MatrixHeader")
        header_layout = QHBoxLayout()
        for h in range(0, len(answers) - 1):
            lbl = QLabel()
            lbl.setText(answers[h])
            lbl.setAlignment(Qt.AlignHCenter)
            lbl.setObjectName("MatrixHeader")
            header_layout.addWidget(lbl)
            header_layout.addStretch()
        if len(answers) >= 1:
            lbl = QLabel()
            lbl.setText(answers[-1])
            lbl.setAlignment(Qt.AlignHCenter)
            lbl.setObjectName("MatrixHeader")
            header_layout.addWidget(lbl)
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        layout.addRow(headerlbl, header_widget)

        self.buttongroups = []
        self.questions = []
        for quest in self.id_order:
            bg_layout, bg = make_answers([""]*len(answers), self,
                                         qid+"_{0:02d}".format(quest) if len(questions) >= 10 else qid+"_{}".format(quest),
                                         self.name, start_answer_id, log=False)
            quest_label = QLabel(questions[quest-1])
            layout.addRow(quest_label, bg_layout)
            self.buttongroups.append(bg)
            self.questions.append(quest_label)

        self.setLayout(layout)
