"""Create context for the test files."""
import ast
import csv
import re
from unittest.mock import patch
import pytest
from configobj import ConfigObj, ConfigObjError
from contextlib import contextmanager
import keyboard
from tests.MockReceiver import MockReceiver
import portalocker
from pythonosc import osc_server, dispatcher
from PySide6.QtGui import QIntValidator, QDoubleValidator, QRegularExpressionValidator, QPalette
from PySide6.QtCore import QTimer, QPoint
from PySide6.QtWidgets import QCheckBox, QLabel, QRadioButton, QFormLayout, QButtonGroup, QPlainTextEdit
import asyncio


@contextmanager
def mock_file(filepath):
    """
    Mock that a file is opened in another application.

    Parameters
    ----------
    filepath : str
        file/path to the file to block
    """
    filepath = os.path.join(os.getcwd(), filepath)
    file = open(filepath, 'w')
    portalocker.lock(file, portalocker.LockFlags.EXCLUSIVE)
    yield filepath
    try:
        file.close()
        os.remove(filepath)
    except Exception as e:
        print(e)
        pass


import os
import sys
if os.path.join(os.getcwd().split("tests")[0],"QUEST") not in sys.path:
    sys.path.insert(0, os.path.join(os.getcwd().split("tests")[0],"QUEST"))
from ABX import ABX
from GUI import StackedWindowGui
from QEditGui import QEditGuiMain
from Validator import validate_questionnaire, listify, string_to_list
from tools import default_values, general_fields, page_fields, types, fields_per_type, player_buttons
from PasswordEntry import PasswordEntry
from PupilCoreButton import Button
from AnswerCheckBox import make_answers as make_answers_cb
from AnswerRadioButton import make_answers
from Lines import QHLine
from MUSHRA import MUSHRA
from OSCButton import OSCButton
from Player import Player
import QUEST.LabeledSlider as LabeledSlider
import QUEST.Slider as Slider
from QUEST.RadioMatrix import RadioMatrix
from Image import Image
from tests.test_helpers import *
