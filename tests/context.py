"""Create context for the test files."""
import ast
import csv
import re
from unittest.mock import patch
import pytest
from configobj import ConfigObj, ConfigObjError
from contextlib import contextmanager
import keyboard
from MockReceiver import MockReceiver
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(sys.path)
from QUEST.ABX import ABX
from QUEST.GUI import StackedWindowGui
from QUEST.QEditGui import QEditGuiMain
from QUEST.Validator import validate_questionnaire, listify, string_to_list
from QUEST.tools import default_values, general_fields, page_fields, types, fields_per_type, player_buttons
from QUEST.PasswordEntry import PasswordEntry
from QUEST.PupilCoreButton import Button
from QUEST.AnswerCheckBox import make_answers as make_answers_cb
from QUEST.AnswerRadioButton import make_answers
from QUEST.Lines import QHLine
from QUEST.MUSHRA import MUSHRA
from QUEST.OSCButton import OSCButton
from QUEST.Player import Player
import QUEST.LabeledSlider as LabeledSlider
import QUEST.Slider as Slider
import QUEST.RadioMatrix as RadioMatrix
from QUEST.Image import Image
from test_helpers import *
