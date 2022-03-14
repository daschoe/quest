"""
Creates a structured page.
"""
import datetime

from PyQt5.QtCore import QSignalMapper, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QFormLayout, QButtonGroup, QCheckBox, QLineEdit, QPlainTextEdit, \
    QHBoxLayout

from src.ABX import ABX
from src.AnswerCheckBox import make_answers as mac
from src.AnswerRadioButton import make_answers as mar
from src.AnswerSlider import make_answers as mas
from src.AnswerTextField import make_answers as matf
from src.Lines import QHLine
from src.MUSHRA import MUSHRA
from src.OSCButton import OSCButton
from src.PasswordEntry import PasswordEntry
from src.Player import Player
from src.PupilCoreButton import Button
from src.RadioMatrix import RadioMatrix


class Page(QWidget):
    """
    Structure for a basic page layout.

    Attributes
    ----------
    structure : ConfigObj
        questionnaire structure
    parent : QObject, optional
         widget/layout this widget is embedded in
    """

    def __init__(self, structure, parent=None):
        """

        Parameters
        ----------
        structure : ConfigObj
            questionnaire structure
        parent : QObject, optional
             widget/layout this widget is embedded in
        """
        QWidget.__init__(self, parent=parent)

        self.questions = structure.sections
        if "description" in structure.keys():
            self.description = structure["description"]
        else:
            self.description = None
        self.evaluationvars = {}
        self.players = []
        self.required = {}
        self.page_log = ""

        if "pupil_on_next" in structure.keys() and structure["pupil_on_next"] is not None and \
                structure["pupil_on_next"] != "" and not self.parent().preview:
            self.pupil_func = Button(None, "Annotate", parent, None)
            self.pupil_on_next = structure["pupil_on_next"]
        else:
            self.pupil_on_next = None

        layout = QFormLayout(self)

        if structure["title"] != "":
            header = QLabel(structure["title"])
            header.setObjectName("headline")
            layout.addRow(header)
        if self.description is not None:
            lbl = QLabel(self.description)
            lbl.setWordWrap(True)
            layout.addRow(lbl)
        if structure["title"] != "" or self.description is not None:  # don't add a line if nothing is there
            layout.addRow(QHLine())

        for quest in self.questions:
            if "type" not in structure[quest].keys() or structure[quest]["type"] == "Plain Text":
                lbl = QLabel(structure[quest]["text"])
                lbl.setWordWrap(True)
                if "objectName" in structure[quest].keys():
                    lbl.setObjectName(structure[quest]["objectName"])
                layout.addRow(lbl)
            elif structure[quest]["type"] == "HLine":
                layout.addRow(QHLine(objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None))
            elif structure[quest]["type"] == "Button":
                button = Button(structure[quest]["inscription"], structure[quest]["function"], self,
                                structure[quest]["id"], recording_name=structure[quest]["recording_name"] if "recording_name" in structure[quest].keys() else None,
                                objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None,
                                annotation=structure[quest]["annotation"] if "annotation" in structure[quest].keys() else None)
                layout.addRow(button)
                # self.evaluationvars[structure[quest]["id"]] = button.used
                self.required[structure[quest]["id"]] = [True if ("required" in structure[quest].keys()) and (
                    structure[quest].as_bool("required")) else False, button.button, button.name, button.used]
            elif structure[quest]["type"] == "OSCButton":
                oscbutton = OSCButton(structure[quest]["inscription"], structure[quest]["address"],
                                   structure[quest]["value"], self, structure[quest]["id"], structure[quest]["receiver"],
                                   objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None)
                layout.addRow(oscbutton)
                self.required[structure[quest]["id"]] = [True if ("required" in structure[quest].keys()) and (
                    structure[quest].as_bool("required")) else False, oscbutton.button, oscbutton.name, oscbutton.used]
            elif structure[quest]["type"] == "Player":
                player = Player(structure[quest].as_int("start_cue"), structure[quest]["track"], qid=structure[quest]["id"],
                                video=structure[quest]["video"] if "video" in structure[quest].keys() else None,
                                parent=self, end_cue=structure[quest].as_int("end_cue") if "end_cue" in structure[quest].keys() else None,
                                displayed_buttons=structure[quest]["buttons"] if "buttons" in structure[quest].keys()
                                else ["Play", "Pause", "Stop"], pupil=structure[quest]["pupil"] if ("pupil" in structure[quest].keys() and structure[quest]["pupil"] != "") else None,
                                objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None,
                                timer=structure[quest]["timer"] if "timer" in structure[quest].keys() else None,
                                play_once=structure[quest].as_bool("play_once") if "play_once" in structure[quest].keys() else False,
                                play_button_text=structure[quest]["play_button_text"] if "play_button_text" in structure[quest].keys() else None)
                layout.addRow(player)
                self.evaluationvars[structure[quest]["id"]] = player.duration
                self.players.append(player)
                self.required[structure[quest]["id"]] = [True if ("required" in structure[quest].keys()) and (
                    structure[quest].as_bool("required")) else False, player.play_button if "Play" in player.buttons else None, player.name, player.playing]
            elif structure[quest]["type"] == "MUSHRA":
                if "xfade" in structure[quest].keys():
                    mr = MUSHRA(structure[quest]["start_cues"], structure[quest]["end_cues"], structure[quest]["track"],
                                structure[quest]["id"], structure[quest].as_bool("xfade"), parent=self,
                                objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None)
                else:
                    mr = MUSHRA(structure[quest]["start_cues"], structure[quest]["end_cues"], structure[quest]["track"],
                                qid=structure[quest]["id"], parent=self,
                                objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None)
                layout.addRow(mr)
                self.evaluationvars[structure[quest]["id"]] = mr.duration
                for sl in range(0, len(mr.sliders)):
                    self.evaluationvars[structure[quest]["id"] + "_{}".format(sl + 1)] = mr.sliders[sl]
                self.players.append(mr)
                self.required[structure[quest]["id"]] = [True if ("required" in structure[quest].keys()) and (
                    structure[quest].as_bool("required")) else False, [mr.refbutton] + mr.buttons, mr.name, mr.playing]
            elif structure[quest]["type"] == "Radio":
                ans_layout, bg = mar(structure[quest]["answers"], self, structure[quest]["id"],
                                     objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None,
                                     start_answer_id=structure[quest].as_int("start_answer_id") if "start_answer_id" in structure[quest].keys() else 0)
                lbl = QLabel(structure[quest]["text"])
                layout.addRow(lbl, ans_layout)
                self.evaluationvars[structure[quest]["id"]] = bg
                self.required[structure[quest]["id"]] = [True if ("required" in structure[quest].keys()) and (
                    structure[quest].as_bool("required")) else False, lbl]
            elif structure[quest]["type"] == "Check":
                ans_layout, cvars = mac(structure[quest]["answers"],
                                        objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None)
                lbl = QLabel(structure[quest]["text"])
                layout.addRow(lbl, ans_layout)
                cbmapper = QSignalMapper(self)
                for c in range(0, len(cvars)):
                    self.evaluationvars[structure[quest]["id"] + "_{}".format(c)] = cvars[c]
                    self.required[structure[quest]["id"] + "_{}".format(c)] = [
                        True if ("required" in structure[quest].keys()) and (
                            structure[quest].as_bool("required")) else False, lbl]
                    cvars[c].toggled.connect(cbmapper.map)
                    cbmapper.setMapping(cvars[c], structure[quest]["id"] + "_{}".format(c))
                cbmapper.mapped[str].connect(self.log)
            elif structure[quest]["type"] == "Text":
                txt = matf(structure[quest].as_int("size"), structure[quest]["id"],
                           structure[quest]["policy"] if "policy" in structure[quest].keys() else None, self,
                           objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None)
                lbl = QLabel(structure[quest]["text"])
                layout.addRow(lbl, txt)
                self.evaluationvars[structure[quest]["id"]] = txt
                self.required[structure[quest]["id"]] = [True if ("required" in structure[quest].keys()) and (
                    structure[quest].as_bool("required")) else False, lbl]
            elif structure[quest]["type"] == "Password":
                pw = PasswordEntry(structure[quest]["password_file"], structure[quest]["id"],
                                   structure[quest]["policy"] if "policy" in structure[quest].keys() else None, self,
                                   objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None)
                lbl = QLabel(structure[quest]["text"])
                layout.addRow(lbl, pw)
                self.evaluationvars[structure[quest]["id"]] = pw
                self.required[structure[quest]["id"]] = [True if ("required" in structure[quest].keys()) and (
                    structure[quest].as_bool("required")) else False, lbl]
            elif structure[quest]["type"] == "Slider":
                ans_layout, slider = mas(structure[quest].as_bool("labelled"), structure[quest]["id"],
                                         structure[quest].as_int("min"), structure[quest].as_int("max"),
                                         structure[quest].as_int("start"),
                                         structure[quest]["header"] if "header" in structure[quest].keys() else None,
                                         structure[quest]["label"] if "label" in structure[quest].keys() else None,
                                         self,
                                         objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None)
                lbl = QLabel(structure[quest]["text"])
                if ("question_above" in structure[quest].keys()) and structure[quest].as_bool("question_above"):
                    layout.addRow(lbl)
                    layout.addRow(ans_layout)
                else:
                    if "header" in structure[quest].keys():
                        headerlbl = QLabel("")
                        headerlbl.setObjectName("SliderHeader")
                        layout.addRow(headerlbl, ans_layout.itemAt(0).widget())
                        layout.addRow(lbl, ans_layout.itemAt(1).widget())
                    else:
                        layout.addRow(lbl, ans_layout)
                self.evaluationvars[structure[quest]["id"]] = slider
                self.required[structure[quest]["id"]] = [True if ("required" in structure[quest].keys()) and (
                    structure[quest].as_bool("required")) else False, lbl]
            elif structure[quest]["type"] == "ABX":
                abx = ABX(structure[quest]["start_cues"], structure[quest]["track"], structure[quest]["text"],
                          structure[quest]["id"],
                          structure[quest]["answers"] if ("answers" in structure[quest].keys() and not structure[quest]["answers"] == "") else None,
                          button_texts=structure[quest]["button_texts"] if "button_texts" in structure[quest].keys() else None,
                          parent=self,
                          objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None,
                          x=True if ("x" in structure[quest].keys()) and (structure[quest].as_bool("x")) else False)
                layout.addRow(abx)
                self.evaluationvars[structure[quest]["id"]] = abx
                self.players.append(abx.a_button)
                self.players.append(abx.b_button)
                if abx.x_button is not None:
                    self.players.append(abx.x_button)
                self.required[structure[quest]["id"]] = [True if ("required" in structure[quest].keys()) and (
                    structure[quest].as_bool("required")) else False, [abx.a_button, abx.b_button] if abx.x_button is None else [abx.a_button, abx.b_button, abx.x_button], abx.name, [abx.a_button.playing, abx.b_button.playing] if abx.x_button is None else [abx.a_button.playing, abx.b_button.playing, abx.x_button.playing]]
            elif structure[quest]["type"] == "Matrix":
                matrix = RadioMatrix(structure[quest]["questions"], structure[quest]["answers"], structure[quest]["id"],
                                     structure[quest].as_int("start_answer_id"), parent=self,
                                     objectname=structure[quest]["objectName"] if "objectName" in structure[quest].keys() else None,
                                     randomize=structure[quest].as_bool("randomize") if "randomize" in structure[quest].keys() else False)
                layout.addRow(matrix)
                self.evaluationvars[structure[quest]["id"]] = matrix
                self.required[structure[quest]["id"]] = [True if ("required" in structure[quest].keys()) and (
                    structure[quest].as_bool("required")) else False, matrix.questions, matrix.name]
            else:
                raise ValueError("Unknown type for question {}. Found {}. Supported types are: HLine, Player, MUSHRA, "
                                 "Radio, Check, Text, Slider, Button".format(structure[quest]["id"], structure[quest]["type"]))

        if len(self.players) > 0 and self.parent().popup and not self.parent().preview:
            for p in self.players:
                if type(p) == Player and p.timer is not None:
                    player_found = False
                    for item in range(self.layout().rowCount()):
                        if player_found and self.layout().itemAt(item, 1).widget() is None:
                            if type(self.layout().itemAt(item, 1)) is QHBoxLayout:
                                for box in range(self.layout().itemAt(item, 1).count()):
                                    sp = self.layout().itemAt(item, 1).itemAt(box).widget().sizePolicy()
                                    sp.setRetainSizeWhenHidden(True)
                                    self.layout().itemAt(item, 1).itemAt(box).widget().setSizePolicy(sp)
                                    self.layout().itemAt(item, 1).itemAt(box).widget().hide()
                            if self.layout().itemAt(item, 0) is not None:
                                sp = self.layout().itemAt(item, 0).widget().sizePolicy()
                                sp.setRetainSizeWhenHidden(True)
                                self.layout().itemAt(item, 0).widget().setSizePolicy(sp)
                                self.layout().itemAt(item, 0).widget().hide()
                        if player_found and self.layout().itemAt(item, 1).widget() is not None:
                            if self.layout().itemAt(item, 0) is not None:
                                sp = self.layout().itemAt(item, 0).widget().sizePolicy()
                                sp.setRetainSizeWhenHidden(True)
                                self.layout().itemAt(item, 0).widget().setSizePolicy(sp)
                                self.layout().itemAt(item, 0).widget().hide()
                            sp = self.layout().itemAt(item, 1).widget().sizePolicy()
                            sp.setRetainSizeWhenHidden(True)
                            self.layout().itemAt(item, 1).widget().setSizePolicy(sp)
                            self.layout().itemAt(item, 1).widget().hide()
                        if self.layout().itemAt(item, 1).widget() == p:
                            player_found = True
        layout.setLabelAlignment(Qt.AlignVCenter)
        layout.setRowWrapPolicy(QFormLayout.WrapLongRows)  # automatic line breaks in text

    def log(self, qid):
        """Log changes

        Parameters
        ----------
        qid : str
            id of the element that raised a log
        """
        print("Log raised", qid, type(self.sender()))
        if type(self.sender()) is QLineEdit or type(self.sender()) is PasswordEntry:
            self.page_log += "\n\t{} - Changed {} to {}".format(datetime.datetime.now().replace(microsecond=0).__str__(),
                                                                qid, self.sender().text())
        elif type(self.sender()) is QPlainTextEdit:
            self.page_log += "\n\t{} - Changed {} to {}".format(datetime.datetime.now().replace(microsecond=0).__str__(),
                                                                qid, self.sender().toPlainText())
        elif type(self.sender()) is QButtonGroup:
            self.page_log += "\n\t{} - Changed {} to {}".format(datetime.datetime.now().replace(microsecond=0).__str__(),
                                                                qid, self.sender().checkedId())
        elif type(self.sender()) is QCheckBox:
            self.page_log += "\n\t{} - Changed {} to {}".format(datetime.datetime.now().replace(microsecond=0).__str__(),
                                                                qid, self.sender().isChecked())
        elif (type(self.sender()) is QSignalMapper) and (type(self.sender().sender()) is QCheckBox):  # QCheckBox
            self.page_log += "\n\t{} - Changed {} to {}".format(datetime.datetime.now().replace(microsecond=0).__str__(),
                                                                qid, self.sender().sender().isChecked())
        else:  # Slider
            self.page_log += "\n\t{} - Changed {} to {}".format(datetime.datetime.now().replace(microsecond=0).__str__(),
                                                                qid, self.sender().value())

    def get_key(self, val):
        """ function to return key for any value

        Parameters
        ----------
        val : str
            value to look up

        Returns
        -------
        str
            key or "key doesn't exist"
        """
        for key, value in self.evaluationvars.items():
            if val == value:
                return key

        return "key doesn't exist"
