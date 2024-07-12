"""A question type to easily create an AB(X) test"""

from random import shuffle

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel

from src.AnswerRadioButton import make_answers as radio
from src.Player import Player


class ABX(QWidget):
    """AB(X) question type"""

    def __init__(self, start_cues, tracks, text, qid, answers=None, button_texts=None, parent=None, objectname=None, x=False):
        """
        Create the layout of the question.\n
        The order of A and B is randomized (->double-blind).

        Parameters
        ----------
        start_cues : list[int]
            marker/cue values to start the playback at (REAPER)
        tracks : int or list[int]
            active tracks for each start cue
        text : str
            text of the question
        qid : str
            id of the question
        answers : list[str], optional
            customizable answer possibilities, if none are given the defaults are "A" and "B"
        button_texts : list[str], optional
            customizable button labels, if none are given the defaults are "A", "B" and "X"
        parent : QObject
                the page the button is on
        objectname : str, optional
            name of the object, if it is supposed to be styled individually
        x : boolean, default=False
            If the option x is True, the first entry in start_cues/tracks is chosen as reference.
        """
        QWidget.__init__(self, parent=parent)
        if answers is None:
            answers = ["A", "B"]
        if button_texts is None:
            button_texts = ["A", "B", "X"]
        player_layout = QHBoxLayout()
        question_layout = QVBoxLayout()
        if objectname is not None:
            self.setObjectName(objectname)
            self.name = objectname
        else:
            self.name = None
        stimuli = []
        for cue_no in range(len(start_cues)):
            stimuli.append((int(start_cues[cue_no]), tracks[cue_no]))
        shuffle(stimuli)
        self.page = parent

        self.a_button = Player(stimuli[0][0], [stimuli[0][1]], parent=self.page, qid=qid + "_A", displayed_buttons=["Play"],
                               objectname=objectname, play_button_text=button_texts[0])
        player_layout.addWidget(self.a_button)
        self.b_button = Player(stimuli[1][0], [stimuli[1][1]], parent=self.page, qid=qid + "_B", displayed_buttons=["Play"],
                               objectname=objectname, play_button_text=button_texts[1])
        player_layout.addWidget(self.b_button)
        if x:
            self.x_button = Player(int(start_cues[0]), [tracks[0]], parent=self.page, qid=qid + "_X", displayed_buttons=["Play"],
                                   objectname=objectname, play_button_text=button_texts[2])
            player_layout.addWidget(self.x_button)
        else:
            self.x_button = None

        question_layout.addItem(player_layout)
        answer_layout = QFormLayout()
        radio_layout, self.answer = radio(answers, self.page, qid, objectname)
        self.label = QLabel(text)
        answer_layout.addRow(self.label, radio_layout)
        question_layout.addItem(answer_layout)
        self.setLayout(question_layout)
        if x:
            stimuli.append((int(start_cues[0]), tracks[0]))
        self.order = stimuli
