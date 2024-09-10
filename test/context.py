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
from src.ABX import ABX
from src.GUI import StackedWindowGui
from src.QEditGui import QEditGuiMain
from src.Validator import validate_questionnaire, listify, string_to_list
from src.tools import default_values, general_fields, page_fields, types, fields_per_type, player_buttons
from src.PasswordEntry import PasswordEntry
from src.PupilCoreButton import Button
from src.AnswerCheckBox import make_answers as make_answers_cb
from src.AnswerRadioButton import make_answers
from src.Lines import QHLine
from src.MUSHRA import MUSHRA
from src.OSCButton import OSCButton
from src.Player import Player
import src.LabeledSlider as LabeledSlider
import src.Slider as Slider
import src.RadioMatrix as RadioMatrix
from src.Image import Image
from test_helpers import *
