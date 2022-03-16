"""Create context for the test files."""
import ast
import csv
import re
from unittest.mock import patch
import pytest
from configobj import ConfigObj, ConfigObjError
import keyboard
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QRegExpValidator
from PyQt5.QtCore import QTimer, QPoint
from PyQt5.QtWidgets import QCheckBox, QLabel, QRadioButton, QFormLayout, QButtonGroup, QPlainTextEdit

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