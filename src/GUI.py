"""
GUI application, main entry point.
"""
import argparse
# -*- coding: utf-8 -*-
import csv
import datetime
import os
import socket
import sys
import threading
import time

import zmq
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QStackedWidget, QApplication, \
    QMessageBox, QScrollArea, QButtonGroup, QCheckBox, QLineEdit, QPlainTextEdit, QSlider, QDesktopWidget, QSizePolicy
from configobj import ConfigObj
from ping3 import ping
from pythonosc import udp_client, osc_server
from pythonosc.dispatcher import Dispatcher

from src.LabeledSlider import LabeledSlider
from src.MUSHRA import MUSHRA
from src.MessageBox import ResizeMessageBox
from src.Page import Page
from src.PasswordEntry import PasswordEntry
from src.Player import Player
from src.PupilCoreButton import Button
from src.RadioMatrix import RadioMatrix
from src.Slider import Slider
from src.Validator import listify, validate_questionnaire
from src.Video import *
from src.ABX import ABX
from src.OSCButton import OSCButton
from src.randomization import *

TIMEOUT = 0.5  # TODO change this to your liking
VERSION = "1.0.6"


class StackedWindowGui(QWidget):
    """
    Main frame of GUI, consisting of multiple pages.
    """

    def __init__(self, file, popup=True, preview=False):
        """
        Parameters
        ----------
        file : str
            file/path to the questionnaire config file
        popup : bool, default=True
            if True, opens a new window for the questionnaire
        preview : bool, default=False
            if True, some features like timer and randomization are invalidated

        Raises
        ------
        FileNotFoundError
            if a file is not found or has a wrong format
        """
        super(StackedWindowGui, self).__init__()
        self.popup = popup
        self.preview = preview
        # default values
        self.go_back = True
        back_text = "Zurück"
        self.forward_text = "Weiter"
        self.send_text = "Absenden"
        self.answer_pos = "Ja"
        self.answer_neg = "Nein"
        self.save_message = "Sind Sie bereit den Fragebogen zu beenden und somit Ihre Angaben zu speichern?"
        self.pagecount_text = "Seite {} von {}"
        self.filepath_results = './results/results.csv'
        self.filepath_log = './results/log_{}_{}.txt'.format(self.get_participant_number(), datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        self.log = ''
        self.delimiter = ';'
        self.audio_ip = None
        self.audio_port = None
        self.audio_recv_port = None
        self.audio_tracks = 0
        self.video_ip = None
        self.video_port = None
        self.video_player = None
        self.pupil_ip = None
        self.pupil_port = None
        self.help_ip = None
        self.help_port = None
        self.help_text = "Hilfe"
        self.rand = None
        stylesheet = './stylesheets/minimal.qss'
        self.button_fade = 100
        self.saved = False
        self.tooltip_not_all_answered = 'Bitte beantworten Sie alle Fragen.'
        self.connection_lost_title = "Internet Verbindung verloren"
        self.connection_lost_text = "Bitte melden Sie sich beim betreuenden Mitarbeiter."
        self.global_play_state = None
        self.global_osc_message = None
        self.global_osc_ip = None
        self.global_osc_send_port = None
        self.global_osc_recv_port = None
        self.stop_initiated = False

        if not os.path.isfile(file):
            raise FileNotFoundError("File {} does not exist.".format(file))
        else:
            print("Loading {}".format(file))

        structure = ConfigObj(file)  # reads the config file into a nested dict, this is all the magic
        error_found, warning_found, warning_det = validate_questionnaire(listify(structure), True)
        if not error_found:
            ans_continue = QMessageBox.Yes
            if warning_found and popup:
                msg = ResizeMessageBox()
                msg.setWindowTitle("Validation Result")
                msg.setSizeGripEnabled(True)
                msg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                msg.setIcon(QMessageBox.Warning)
                msg.setText("The validation detected incomplete info. Do you want to continue?")
                warning_string = ""
                for warn in warning_det:
                    warning_string += warn + "\n"
                msg.setDetailedText(warning_string)
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setDefaultButton(QMessageBox.No)
                ans_continue = msg.exec_()
            if ans_continue == QMessageBox.Yes or not popup:
                for key in structure:
                    #  Style properties
                    if key == "stylesheet":
                        stylesheet = structure[key]
                    elif key == "button_fade":
                        self.button_fade = structure.as_int(key)
                    #  Navigation
                    elif key == "go_back":
                        self.go_back = structure.as_bool(key)
                    elif key == "back_text":
                        back_text = structure[key]
                    elif key == "forward_text":
                        self.forward_text = structure[key]
                    elif key == "save_after":
                        self.save_after = structure[key]
                        self.sections = structure.sections
                    elif key == "send_text":
                        self.send_text = structure[key]
                    elif key == "answer_pos":
                        self.answer_pos = structure[key]
                    elif key == "answer_neg":
                        self.answer_neg = structure[key]
                    elif key == "save_message":
                        self.save_message = structure[key]
                    elif key == "pagecount_text":
                        self.pagecount_text = structure[key]
                    #  Saving
                    elif key == "filepath_results":
                        self.filepath_results = structure[key]
                    elif key == "delimiter":
                        self.delimiter = structure[key]
                    #  audio, video, biofeedback
                    elif key == "audio_ip" and structure[key] != "":
                        self.audio_ip = structure[key]
                    elif key == "audio_port" and structure[key] != "":
                        self.audio_port = structure.as_int(key)
                    elif key == "audio_recv_port" and structure[key] != "":
                        self.audio_recv_port = structure.as_int(key)
                    elif key == "video_ip" and structure[key] != "":
                        self.video_ip = structure[key]
                    elif key == "video_port" and structure[key] != "":
                        self.video_port = structure.as_int(key)
                    elif key == "video_player" and structure[key] != "":
                        self.video_player = structure[key]
                    elif key == "pupil_ip" and structure[key] != "":
                        self.pupil_ip = structure[key]
                    elif key == "pupil_port" and structure[key] != "":
                        self.pupil_port = structure[key]
                    elif key == "help_ip" and structure[key] != "":
                        self.help_ip = structure[key]
                    elif key == "help_port" and structure[key] != "":
                        self.help_port = structure.as_int(key)
                    elif key == "help_text" and structure[key] != "":
                        self.help_text = structure[key]
                    # special stuff
                    elif key == "randomization" and structure[key] != "":
                        self.rand = structure[key]
                    elif key == "randomization_file" and structure[key] != "":
                        self.rand_file = structure[key]
                    elif key == "global_osc_ip" and structure[key] != "":
                        self.global_osc_ip = structure[key]
                    elif key == "global_osc_send_port" and structure[key] != "":
                        self.global_osc_send_port = structure.as_int(key)
                    elif key == "global_osc_recv_port" and structure[key] != "":
                        self.global_osc_recv_port = structure.as_int(key)

                #  Set up client/server connections
                if self.popup and not self.preview and self.video_ip is not None and self.video_port is not None and self.video_player is not None:
                    self.video_client = udp_client.SimpleUDPClient(self.video_ip, self.video_port)
                    if self.video_player == "MadMapper":
                        self.video_player_commands = madmapper
                    elif self.video_player == "VLC":
                        self.video_player_commands = vlc
                    else:
                        self.video_player_commands = None
                else:
                    self.video_client = None
                    self.video_player_commands = None
                if self.popup and not self.preview and self.help_ip is not None and self.help_port is not None:
                    self.help_client = udp_client.SimpleUDPClient(self.help_ip, self.help_port)
                    response = ping(self.help_ip, timeout=TIMEOUT)
                    if response is None:
                        msg = QMessageBox()
                        msg.setWindowTitle(self.connection_lost_title)
                        msg.setSizeGripEnabled(True)
                        msg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                        msg.setIcon(QMessageBox.Information)
                        msg.setText("No connection to {}.".format(self.help_ip))
                        msg.exec_()
                else:
                    self.help_client = None
                if self.popup and not self.preview and self.global_osc_ip is not None and self.global_osc_send_port is not None:
                    self.global_osc_client = udp_client.SimpleUDPClient(self.global_osc_ip, self.global_osc_send_port)
                else:
                    self.global_osc_client = None
                if self.popup and not self.preview and self.global_osc_ip is not None and self.global_osc_recv_port is not None:
                    #self.global_osc_client = udp_client.SimpleUDPClient(self.global_osc_ip, self.global_osc_send_port)
                    self.global_osc_server = threading.Thread(target=self.osc_listener_default, args=[self.global_osc_recv_port])
                    self.global_osc_server.daemon = True
                    self.global_osc_server.start()
                else:
                    #self.global_osc_client = None
                    self.global_osc_server = None
                no_zmq_connection = False
                if popup and not self.preview and self.pupil_ip is not None and self.pupil_port is not None:
                    self.ctx = zmq.Context()
                    self.pupil_remote = zmq.Socket(self.ctx, zmq.REQ)
                    self.pupil_remote.setsockopt(zmq.RCVTIMEO, 2000)
                    self.pupil_remote.connect('tcp://' + self.pupil_ip + ':' + self.pupil_port)
                    print("Connect to pupil "+'tcp://' + self.pupil_ip + ':' + self.pupil_port)
                    self.pupil_remote.send_string("v")
                    retries_left = 3
                    success = False
                    while retries_left > 0 and not success:
                        if (self.pupil_remote.poll(2500) & zmq.POLLIN) != 0:
                            _ = self.pupil_remote.recv_string()
                            success = True
                        if not success:
                            retries_left -= 1
                            print("No response from pupil capture...")
                            self.pupil_remote.setsockopt(zmq.LINGER, 0)
                            self.pupil_remote.close()
                            if retries_left == 0 and self.popup:
                                msg = QMessageBox()
                                msg.setWindowTitle("Error")
                                msg.setIcon(QMessageBox.Critical)
                                msg.setText("No connection with Pupil Capture possible!")
                                msg.exec_()
                                no_zmq_connection = True
                            if not no_zmq_connection:
                                self.pupil_remote = zmq.Socket(self.ctx, zmq.REQ)
                else:
                    self.pupil_remote = None
                if not no_zmq_connection:
                    if self.popup and not self.preview and self.audio_ip is not None and self.audio_port is not None:
                        self.audio_client = udp_client.SimpleUDPClient(self.audio_ip, self.audio_port)
                        self.audio_client.send_message("/action", MUSHRA.unsolo_all)
                        self.audio_client.send_message("/action", MUSHRA.loop_off_command)
                        self.audio_client.send_message("/action", 40341)  # mute all
                        self.audio_client.send_message("/action", 40297)  # unselect all
                        if self.audio_recv_port is not None:
                            self.audio_server = threading.Thread(target=self.osc_listener_reaper, args=[self.audio_recv_port])
                            self.audio_server.daemon = True
                            self.audio_server.start()
                        else:
                            self.audio_server = None
                    else:
                        self.audio_client = None
                        self.audio_server = None
                    self.filepath_log = '{}/log_{}_{}.txt'.format(self.filepath_results.rsplit("/", 1)[0], self.get_participant_number(), datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                    if popup and not self.preview:
                        print(self.filepath_log)

                    if not os.path.isfile(stylesheet):
                        raise FileNotFoundError("File {} does not exist.".format(stylesheet))
                    else:
                        with open(stylesheet, 'r') as css_file:
                            self.css_data = css_file.read().replace('\n', '')
                        self.setStyleSheet(self.css_data)  # no need to catch errors as if nonesense is set a default fallback is used internally

                    self.prev_index = 0
                    self.saved = False

                    self.start = datetime.datetime.now()
                    self.log = "{} - Started GUI".format(self.start.replace(microsecond=0).__str__())

                    self.Stack = QStackedWidget(self)
                    self.random_groups = []
                    random_pages = []
                    last_group = 0
                    for page in structure.sections:
                        if "randomgroup" in structure[page].keys() and not self.preview:
                            if (structure[page]["randomgroup"] != last_group) and (len(random_pages) > 0):
                                if self.rand == "balanced latin square":
                                    squares = balanced_latin_squares(len(random_pages))
                                    self.random_groups.append(len(random_pages))
                                elif self.rand == "from file":
                                    squares = order_from_file(self.rand_file)
                                if (self.get_participant_number() - 1) >= len(squares):
                                    order = squares[(self.get_participant_number() - 1) % len(squares)]
                                else:
                                    order = squares[self.get_participant_number() - 1]
                                # print(order)
                                if popup:
                                    for o in order:
                                        self.Stack.addWidget(random_pages[o - 1])
                                else:
                                    self.Stack.addWidget(Page(structure[page], page, parent=self))
                                random_pages = []
                            last_group = structure[page]["randomgroup"]
                            random_pages.append(Page(structure[page], page, parent=self))
                        else:
                            if len(random_pages) > 0:
                                if self.rand == "balanced latin square":
                                    squares = balanced_latin_squares(len(random_pages))
                                    self.random_groups.append(len(random_pages))
                                elif self.rand == "from file":
                                    squares = order_from_file(self.rand_file)
                                if not popup:
                                    order = squares[0]
                                else:
                                    if (self.get_participant_number() - 1) >= len(squares):
                                        order = squares[(self.get_participant_number() - 1) % len(squares)]
                                    else:
                                        order = squares[self.get_participant_number() - 1]
                                # print(order)
                                if popup:
                                    for o in order:
                                        self.Stack.addWidget(random_pages[o - 1])
                                else:
                                    self.Stack.addWidget(Page(structure[page], page, parent=self))
                            self.Stack.addWidget(Page(structure[page], page, parent=self))
                            random_pages = []
                    if len(random_pages) > 0 and popup:
                        if self.rand == "balanced latin square":
                            squares = balanced_latin_squares(len(random_pages))
                            self.random_groups.append(len(random_pages))
                        elif self.rand == "from file":
                            squares = order_from_file(self.rand_file)
                        if (self.get_participant_number() - 1) >= len(squares):
                            order = squares[(self.get_participant_number() - 1) % len(squares)]
                        else:
                            order = squares[self.get_participant_number() - 1]
                        # print(order)
                        if popup:
                            for o in order:
                                self.Stack.addWidget(random_pages[o - 1])
                    elif len(random_pages) > 0 and not popup:
                        for page in range(len(random_pages)):
                            self.Stack.addWidget(random_pages[page])

                    self.Stack.currentChanged[int].connect(self.on_current_changed)

                    self.navigation = QHBoxLayout()
                    if self.go_back:
                        self.backbutton = QPushButton(back_text, None)
                        self.backbutton.setEnabled(False)
                        self.backbutton.clicked.connect(self.prev_page)
                    self.forwardbutton = QPushButton(self.forward_text, None)
                    self.forwardbutton.clicked.connect(self.next_page)
                    if self.Stack.count() == 1 or self.Stack.currentIndex() == self.sections.index(self.save_after):
                        self.forwardbutton.setText(self.send_text)
                    if self.pagecount_text.count('{') == 2:
                        self.page_label = QLabel(self.pagecount_text.format(self.Stack.currentIndex() + 1, self.Stack.count()), None)
                    elif self.pagecount_text.count('{') == 1:
                        self.page_label = QLabel(self.pagecount_text.format(self.Stack.currentIndex() + 1), None)
                    else:
                        self.page_label = QLabel(self.pagecount_text, None)
                    self.navigation.addWidget(self.page_label)
                    self.navigation.addStretch()
                    if self.help_client is not None:
                        self.help_button = QPushButton(self.help_text)
                        self.help_button.clicked.connect(lambda: self.help_client.send_message("/help_request", ""))
                        self.help_button.clicked.connect(self.__click_animation)
                        self.navigation.addWidget(self.help_button)
                        self.navigation.addStretch()
                    elif (self.preview or not self.popup) and self.help_ip is not None and self.help_port is not None:
                        self.help_button = QPushButton(self.help_text)
                        self.navigation.addWidget(self.help_button)
                        self.navigation.addStretch()
                    if self.go_back and (self.Stack.count() > 1):
                        self.navigation.addWidget(self.backbutton)
                    self.navigation.addWidget(self.forwardbutton)
                    self.nav = QWidget(self)
                    self.nav.setLayout(self.navigation)

                    outerlayout = QVBoxLayout(self)
                    scroll = QScrollArea(self)
                    outerlayout.addWidget(scroll)
                    scroll.setWidgetResizable(True)
                    layout = QWidget(scroll)
                    l_layout = QVBoxLayout(layout)
                    layout.setLayout(l_layout)
                    l_layout.addWidget(self.Stack)
                    l_layout.addWidget(self.nav)
                    scroll.setWidget(layout)

                    self.Stack.currentChanged[int].connect(lambda: scroll.verticalScrollBar().setValue(0))
                    self.Stack.currentChanged[int].connect(lambda: scroll.horizontalScrollBar().setValue(0))
                    self.setLayout(outerlayout)
                    if self.popup and not self.preview:
                        self.showFullScreen()
                        if self.width() <= QDesktopWidget().availableGeometry().width():
                            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                        if self.height() <= QDesktopWidget().availableGeometry().height():
                            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                        self.show()
                        self.on_current_changed(0)
                    else:
                        self.disconnect_nav()
                        for page in range(self.Stack.count()):
                            self.disconnect_all(self.Stack.widget(page).layout())
                            for p in self.Stack.widget(page).players:
                                self.disconnect_all(p.layout())
                        if self.preview and self.popup:
                            self.showFullScreen()
                            if self.width() <= QDesktopWidget().availableGeometry().width():
                                scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                            if self.height() <= QDesktopWidget().availableGeometry().height():
                                scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                            self.show()

    def osc_listener_reaper(self, port):
        """ Handle the listening of messages from Reaper.

            Parameters
            ----------
            port : int
                the port to listen on
        """
        ip = socket.gethostbyname(socket.gethostname())
        print("Listening on {}:{}".format(ip, port))
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self.play_state)
        server = osc_server.OSCUDPServer((ip, port), dispatcher)
        server.serve_forever()

    def osc_listener_default(self, port):
        """ Handle the listening of messages from any source.

            Parameters
            ----------
            port : int
                the port to listen on
        """
        ip = socket.gethostbyname(socket.gethostname())
        print("Listening on {}:{}".format(ip, port))
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self.osc_reply)  # Funktion, die ausgeführt wird
        server = osc_server.OSCUDPServer((ip, port), dispatcher)
        server.serve_forever()

    def osc_reply(self, address, args):
        """Monitor the incoming OSC messages from the default OSC listener.

            Parameters
            ----------
            address : string
                OSC address of the message
            args : tuple
                value(s) of the message
        """
        print("Received", args)
        self.global_osc_message = args
        self.log += "\n{} - Received {} from global OSC".format(datetime.datetime.now().replace(microsecond=0).__str__(), self.global_osc_message)

    def play_state(self, address, args):
        """ Monitor the play state given by Reaper.
            Reaper will ping back any of the commands with either 0.0 or 1.0.

            Parameters
            ----------
            address : string
                OSC address of the message
            args : tuple
                value(s) of the message
        """
        if address in ["/play", "/pause", "/stop"]:
            if address == "/play" and args[0] == 1.0:
                self.global_play_state = "PLAY"
            elif address == "/pause" and args[0] == 1.0:
                self.global_play_state = "PAUSE"
            elif address == "/stop" and args[0] == 1.0:
                self.global_play_state = "STOP"
                if not self.stop_initiated:
                    for player in self.Stack.currentWidget().players:
                        if player.playing and ((type(player) is Player and (player.timer is None or player.timer.remainingTime() == 0)) or type(player) is MUSHRA):
                            player.stop_button.setEnabled(False)
                            player.playing = False
                else:
                    self.stop_initiated = False
        elif address.find("/track/") > -1 and int(address.split("/")[2]) > self.audio_tracks:
            self.audio_tracks = address.split("/")[2]
            print("Changed audio_tracks to", self.audio_tracks)

    def disconnect_all(self, layout):
        """ Disconnect all widgets from their function for preview.

            Parameters
            ----------
            layout : QLayout
                the layout holding widgets to disconnect
        """
        for i in range(layout.count()):
            child = layout.itemAt(i)
            if child.widget():
                try:
                    if type(child.widget()) == LabeledSlider:
                        child.widget().sl.disconnect()
                    if type(child.widget()) == Button:
                        child.widget().button.disconnect()
                    child.widget().disconnect()
                except TypeError:
                    pass
            if child.layout() is not None:
                self.disconnect_all(child.layout())

    def disconnect_nav(self):
        """Disconnect the navigation."""
        self.forwardbutton.disconnect()
        if self.go_back:
            self.backbutton.disconnect()
        if self.help_client is not None:
            self.help_button.disconnect()

    def __click_animation(self):
        __btn = self.sender()
        __btn.setDown(True)
        QTimer.singleShot(self.button_fade, lambda: __btn.setDown(False))

    def next_page(self):
        """Handling of the forward button linking.\n
        - It is checked whether all required questions were answered -> if not the next page will not load
        - If a `PasswordEntry` is on the page, it will be validated against the file of valid passwords
        - If any type of music/video player is on the page, its playback will be stopped
        - When the last page is reached, run the save data dialog
        - Check the internet connection when any type of player is used
        - When a player has a timer and didn't finish running, don't go to the next page
        """
        for player in self.Stack.currentWidget().players:  # stop current player
            if player.playing and ((type(player) is Player and (player.timer is None or player.timer.remainingTime() == 0)) or type(player) is MUSHRA):
                player.stop()
                if type(player) is MUSHRA:
                    self.audio_client.send_message("/action", MUSHRA.unsolo_all)
        # check for required questions
        not_all_answered = False
        for quest in self.Stack.currentWidget().required.keys():
            if self.Stack.currentWidget().required[quest][0]:
                ans = self.Stack.currentWidget().evaluationvars[quest]
                if ((type(ans) is QButtonGroup) and (ans.checkedId() == -1)) or \
                        ((type(ans) is QCheckBox) and not ans.isChecked()) or \
                        ((type(ans) is QLineEdit or type(ans) is PasswordEntry) and (len(ans.text()) == 0)) or \
                        ((type(ans) is QPlainTextEdit) and (len(ans.toPlainText()) == 0)) or \
                        (((type(ans) is Slider) or (type(ans) is LabeledSlider)) and (ans.value() == -1)) or \
                        ((type(ans) is list) and (len(ans) == 0)
                         and not self.Stack.currentWidget().required[quest][3]) or \
                        ((type(ans) is list) and (type(ans[0]) is list) and (0 in (len(x) for x in ans))
                         and not self.Stack.currentWidget().required[quest][3]) or \
                        ((type(ans) is bool) and not ans) or \
                        (type(ans) is ABX and ([] in self.Stack.currentWidget().required[quest][3] or ans.answer.checkedId() == -1) or \
                         (type(ans) is RadioMatrix) and (-1 in [bg.checkedId() for bg in ans.buttongroups])) or \
                        ((type(ans) is OSCButton or type(ans) is Button) and not ans.used):
                    not_all_answered = True
                    if (type(self.Stack.currentWidget().required[quest][1]) is QLabel) or \
                            (type(self.Stack.currentWidget().required[quest][1]) is QPushButton):
                        self.Stack.currentWidget().required[quest][1].setObjectName("required")
                        self.Stack.currentWidget().required[quest][1].setStyleSheet(self.css_data)
                    elif type(ans) is ABX:
                        if ans.answer.checkedId() == -1:
                            ans.label.setObjectName("required")
                        else:
                            ans.label.setObjectName(str() if self.Stack.currentWidget().required[quest][2] is None else self.Stack.currentWidget().required[quest][2])
                        if not ans.a_button.duration:
                            self.Stack.currentWidget().required[quest][1][0].play_button.setObjectName("required")
                        else:
                            self.Stack.currentWidget().required[quest][1][0].play_button.setObjectName(
                                str() if self.Stack.currentWidget().required[quest][2] is None else
                                self.Stack.currentWidget().required[quest][2])
                        if not ans.b_button.duration:
                            self.Stack.currentWidget().required[quest][1][1].play_button.setObjectName("required")
                        else:
                            self.Stack.currentWidget().required[quest][1][1].play_button.setObjectName(
                                str() if self.Stack.currentWidget().required[quest][2] is None else
                                self.Stack.currentWidget().required[quest][2])
                        if ans.x_button is not None and ans.x_button.duration == []:
                            self.Stack.currentWidget().required[quest][1][2].play_button.setObjectName("required")
                            self.Stack.currentWidget().required[quest][1][2].play_button.setStyleSheet(self.css_data)
                        elif ans.x_button is not None and len(ans.x_button.duration) >= 1:
                            self.Stack.currentWidget().required[quest][1][2].play_button.setObjectName(
                                str() if self.Stack.currentWidget().required[quest][2] is None else
                                self.Stack.currentWidget().required[quest][2])
                            self.Stack.currentWidget().required[quest][1][2].play_button.setStyleSheet(self.css_data)

                        ans.label.setStyleSheet(self.css_data)
                        self.Stack.currentWidget().required[quest][1][0].play_button.setStyleSheet(self.css_data)
                        self.Stack.currentWidget().required[quest][1][1].play_button.setStyleSheet(self.css_data)
                    elif type(ans) is RadioMatrix:
                        for q in range(0, len(ans.questions)):
                            not_answered = False
                            if ans.buttongroups[q].checkedId() == -1:
                                self.Stack.currentWidget().required[quest][1][q].setObjectName("required")
                                self.Stack.currentWidget().required[quest][1][q].setStyleSheet(self.css_data)
                            else:
                                self.Stack.currentWidget().required[quest][1][q].setObjectName(
                                    str() if self.Stack.currentWidget().required[quest][2] is None else
                                    self.Stack.currentWidget().required[quest][2])
                                self.Stack.currentWidget().required[quest][1][q].setStyleSheet(self.css_data)
                    else:  # MUSHRA
                        for b in range(0, len(self.Stack.currentWidget().required[quest][1])):
                            if len(ans[b]) < 1:
                                self.Stack.currentWidget().required[quest][1][b].setObjectName("required")
                                self.Stack.currentWidget().required[quest][1][b].setStyleSheet(self.css_data)
                            else:
                                self.Stack.currentWidget().required[quest][1][b].setObjectName(str() if self.Stack.currentWidget().required[quest][2] is None else self.Stack.currentWidget().required[quest][2])
                                self.Stack.currentWidget().required[quest][1][b].setStyleSheet(self.css_data)
                else:
                    if type(self.Stack.currentWidget().required[quest][1]) is QLabel:
                        if len(self.Stack.currentWidget().required[quest]) <= 2:
                            self.Stack.currentWidget().required[quest][1].setObjectName(str())
                        else:
                            self.Stack.currentWidget().required[quest][1].setObjectName(str() if self.Stack.currentWidget().required[quest][2] is None else self.Stack.currentWidget().required[quest][2])
                        self.Stack.currentWidget().required[quest][1].setStyleSheet(self.css_data)
                    elif type(self.Stack.currentWidget().required[quest][1]) is QPushButton:
                        self.Stack.currentWidget().required[quest][1].setObjectName(str() if self.Stack.currentWidget().required[quest][2] is None else self.Stack.currentWidget().required[quest][2])
                        self.Stack.currentWidget().required[quest][1].setStyleSheet(self.css_data)
                    elif type(ans) is ABX:
                        if ans.answer.checkedId() != -1:
                            ans.label.setObjectName(str() if self.Stack.currentWidget().required[quest][2] is None else self.Stack.currentWidget().required[quest][2])
                            ans.label.setStyleSheet(self.css_data)
                        if len(ans.a_button.duration) >= 1:
                            self.Stack.currentWidget().required[quest][1][0].play_button.setObjectName(str() if self.Stack.currentWidget().required[quest][2] is None else self.Stack.currentWidget().required[quest][2])
                            self.Stack.currentWidget().required[quest][1][0].play_button.setStyleSheet(self.css_data)
                        if len(ans.b_button.duration) >= 1:
                            self.Stack.currentWidget().required[quest][1][1].play_button.setObjectName(str() if self.Stack.currentWidget().required[quest][2] is None else self.Stack.currentWidget().required[quest][2])
                            self.Stack.currentWidget().required[quest][1][1].play_button.setStyleSheet(self.css_data)
                        if ans.x_button is not None and len(ans.x_button.duration) >= 1:
                            self.Stack.currentWidget().required[quest][1][2].play_button.setObjectName(str() if self.Stack.currentWidget().required[quest][2] is None else self.Stack.currentWidget().required[quest][2])
                            self.Stack.currentWidget().required[quest][1][2].play_button.setStyleSheet(self.css_data)
                    elif type(ans) is RadioMatrix:
                        for q in range(0, len(ans.questions)):
                            if ans.buttongroups[q].checkedId() != -1:
                                self.Stack.currentWidget().required[quest][1][q].setObjectName(
                                    str() if self.Stack.currentWidget().required[quest][2] is None else
                                    self.Stack.currentWidget().required[quest][2])
                                self.Stack.currentWidget().required[quest][1][q].setStyleSheet(self.css_data)
                    else:  # MUSHRA
                        for b in range(0, len(self.Stack.currentWidget().required[quest][1])):
                            if len(ans[b]) >= 1:
                                self.Stack.currentWidget().required[quest][1][b].setObjectName(str() if self.Stack.currentWidget().required[quest][2] is None else self.Stack.currentWidget().required[quest][2])
                                self.Stack.currentWidget().required[quest][1][b].setStyleSheet(self.css_data)
        timer_running = False
        pw_valid = True
        for child in self.Stack.currentWidget().children():
            if type(child) is PasswordEntry:
                pw_valid = child.validate()
                child.setStyleSheet(self.css_data)
            elif type(child) is Player:
                if child.timer is not None and child.countdown > 0:
                    timer_running = True
        if not not_all_answered and pw_valid and not timer_running:
            self.forwardbutton.setToolTip(None)
            self.log += self.Stack.currentWidget().page_log
            self.Stack.currentWidget().page_log = ""
            if self.global_osc_server is not None:
                self.Stack.currentWidget().set_osc_message(self.global_osc_message)
            i = self.Stack.currentIndex() + 1
            if i + 1 <= self.Stack.count():
                self.log += "\n{} - Changed to Page {}".format(datetime.datetime.now().replace(microsecond=0).__str__(), i + 1)
            if self.go_back and (i == 1) and (self.Stack.count() > 1) and not self.saved:  # enable going back at page 2
                self.backbutton.setEnabled(True)
            if i == self.sections.index(self.save_after)+1:
                answer = self.continue_message()
                if answer == QMessageBox.AcceptRole:
                    if self.video_client is not None:
                        self.video_client.send_message(self.video_player_commands['blue_screen'][0] if 'blue_screen' in self.video_player_commands.keys() else self.video_player_commands["stop"][0],
                                                       self.video_player_commands['blue_screen'][1] if 'blue_screen' in self.video_player_commands.keys() else self.video_player_commands["stop"][1])
                    if not self.preview:
                        self.collect_and_save_data()
                    self.saved = True
                    self.Stack.setCurrentIndex(i)
                    if self.Stack.currentIndex() == self.Stack.count()-1:
                        self.forwardbutton.setEnabled(False)
                    else:
                        self.forwardbutton.setText(self.forward_text)
                    if self.go_back:
                        self.backbutton.setEnabled(False)
            if self.pupil_remote is not None and self.Stack.currentWidget().pupil_on_next is not None:
                self.Stack.currentWidget().pupil_func.send_trigger(self.Stack.currentWidget().pupil_func.new_trigger(self.Stack.currentWidget().pupil_on_next))

            # change the page
            if i <= self.Stack.count() - 1:  # normal pages in the middle
                self.Stack.setCurrentIndex(i)
            if i == self.sections.index(self.save_after):
                self.forwardbutton.setText(self.send_text)
            if len(self.Stack.currentWidget().players) > 0 or len(self.Stack.currentWidget().findChildren(Button)) > 0:
                self.is_connected()
            if i + 1 == self.Stack.count() and i != self.sections.index(self.save_after):
                self.forwardbutton.setEnabled(False)
            self.global_osc_message = None
        else:
            self.forwardbutton.setToolTip(self.tooltip_not_all_answered)

    def prev_page(self):
        """
        Handling of the back button linking.
        """
        for player in self.Stack.currentWidget().players:
            if player.playing and ((type(player) is Player and (player.timer is None or player.timer.remainingTime() == 0)) or type(player) is MUSHRA):
                player.stop()
        self.forwardbutton.setText(self.forward_text)
        i = self.Stack.currentIndex() - 1
        self.log += "\n{} - Changed to Page {}".format(datetime.datetime.now().replace(microsecond=0).__str__(), i + 1)
        if i > 0:
            self.Stack.setCurrentIndex(i)
            self.forwardbutton.setEnabled(True)
        elif i == 0:
            self.Stack.setCurrentIndex(i)
            self.backbutton.setEnabled(False)

    def on_current_changed(self, index):
        """
        Update items displayed on all pages.

        Parameters
        ----------
        index : int
            index of the new page
        """
        if self.pagecount_text.count('{') == 2:
            self.page_label.setText(self.pagecount_text.format(index + 1, self.Stack.count()))
        elif self.pagecount_text.count('{') == 1:
            self.page_label.setText(self.pagecount_text.format(index + 1))
        else:
            self.page_label = QLabel(self.pagecount_text, None)
        if not self.preview and (len(self.Stack.widget(self.prev_index).players) > 0) and (len(self.Stack.widget(index).players) == 0):
            if self.video_client is not None:
                self.video_client.send_message(self.video_player_commands['black_screen'][0] if 'black_screen' in self.video_player_commands.keys() else self.video_player_commands["stop"][0],
                                               self.video_player_commands['black_screen'][1] if 'black_screen' in self.video_player_commands.keys() else self.video_player_commands["stop"][1])
        self.prev_index = index

        for player in self.Stack.currentWidget().players:
            if type(player) == Player and (player.buttons == [] or "Play" not in player.buttons) and not self.preview and self.popup:
                player.play()

        if self.help_client is not None:
            help_str = str(index + 1)
            if len(self.Stack.currentWidget().players) > 0:
                for player in self.Stack.currentWidget().players:
                    help_str += '\tmarker:'+str(player.start_cue if type(player) != MUSHRA else player.start_cues)+' track:'+str(player.track if type(player) != MUSHRA else player.tracks)
            self.help_client.send_message("/page", help_str)

    def closeEvent(self, event):
        """
        Reimplement the closeEvent() event handler to save progress.
        """
        if not self.saved and not self.preview:
            self.collect_and_save_data()
        #if self.global_osc_server is not None:
        #    self.global_osc_server.shutdown()
        self.close()

    def continue_message(self):
        """
        Message box showing up at the end of the questionnaire, to confirm saving.

        Returns
        -------
        QMessageBox.ButtonRole
            value of the button clicked (True if it is supposed to be saved)
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(self.save_message)
        msg.setWindowFlags(Qt.CustomizeWindowHint)  # removes title bar
        msg.addButton(self.answer_pos, QMessageBox.AcceptRole)
        msg.addButton(self.answer_neg, QMessageBox.RejectRole)
        msg.setStyleSheet(self.css_data)
        retval = msg.exec_()
        return retval

    def collect_and_save_data(self):
        """Collect the values from all questions and write them to a .csv file for further processing.\n
        If the csv-file is opened in some application, a backup is saved instead.
        """
        # Stop responding to input
        self.disconnect_all(self.Stack.currentWidget().layout())
        for p in self.Stack.currentWidget().players:
            self.disconnect_all(p.layout())

        # Stop pupil
        if self.pupil_remote is not None:
            try:
                self.pupil_remote.send_string("r")
                self.pupil_remote.recv_string()
            except zmq.ZMQError:
                print("Couldn't connect with Pupil Capture!")

        try:
            fields = {"data_row_number": self.get_participant_number()}
        except PermissionError:  # file is open and can't be read
            fields = {"data_row_number": -1}
        for s in range(0, self.Stack.count()):
            if self.Stack.widget(s).evaluationvars is not None:
                for qid, ans in self.Stack.widget(s).evaluationvars.items():
                    if type(ans) is ABX:
                        fields[qid + "_order"] = ans.order
                        fields[qid + "_answer"] = ans.answer.checkedId()
                        fields[qid + "_duration_A"] = ans.a_button.duration
                        fields[qid + "_duration_B"] = ans.b_button.duration
                        if ans.x_button is not None:
                            fields[qid + "_duration_X"] = ans.x_button.duration
                    elif type(ans) is RadioMatrix:
                        for pqid in range(len(ans.id_order)):
                            if len(ans.questions) >= 10:
                                fields[qid + "_{0:02d}".format(ans.id_order[pqid])] = ans.buttongroups[pqid].checkedId()
                            else:
                                fields[qid + "_{}".format(ans.id_order[pqid])] = ans.buttongroups[pqid].checkedId()
                        fields[qid + "_order"] = ans.id_order
                    else:
                        if type(ans) is QButtonGroup:
                            fields[qid] = ans.checkedId()
                        elif type(ans) is QCheckBox:
                            fields[qid] = ans.isChecked()
                        elif type(ans) is QLineEdit or type(ans) is PasswordEntry:
                            if type(ans.validator()) == QDoubleValidator:
                                ans.setText(ans.text().replace(",", "."))
                            fields[qid] = ans.text()
                        elif type(ans) is QPlainTextEdit:
                            fields[qid] = ans.toPlainText().replace("\n", " ")
                        elif (type(ans) is Slider) or (type(ans) is LabeledSlider) or (type(ans) is QSlider):
                            fields[qid] = ans.value()
                        elif (type(ans) is Button) or type(ans) is OSCButton:
                            fields[qid] = ans.used
                        else:
                            fields[qid] = ans
        if self.rand == "balanced latin square":
            fields["Order"] = []
            for rg in self.random_groups:
                if not fields["data_row_number"] == -1:
                    fields["Order"].append(balanced_latin_squares(rg)[(self.get_participant_number()-1) % len(balanced_latin_squares(rg))])
                else:
                    fields["Order"] = "unknown"
        elif self.rand == "from file":
            fields["Order"] = order_from_file(self.rand_file)[self.get_participant_number()-1]

        end = datetime.datetime.now()
        self.log += "\n{} - Finished Questionnaire".format(end.replace(microsecond=0).__str__())
        fields["Start"] = self.start.__str__()
        fields["End"] = end.__str__()

        path = self.filepath_log.rsplit("/", 1)
        if not os.path.exists(self.filepath_log):
            if path[0] != "." and path[0] != [".."]:
                os.makedirs(path[0] + "/", exist_ok=True)
        log_file = open(self.filepath_log, 'w')
        log_file.write(self.log)
        log_file.close()

        path = self.filepath_results.rsplit("/", 1)
        if not os.path.exists(self.filepath_results):
            if path[0] != "." and path[0] != [".."]:
                os.makedirs(path[0] + "/", exist_ok=True)
            with open(self.filepath_results, "w+", newline='', encoding='utf_8') as csvfile:
                writer = csv.writer(csvfile, delimiter=self.delimiter)
                header = fields.keys()
                writer.writerow(header)

        try:
            headers = []
            with open(self.filepath_results, 'r', newline='', encoding='utf_8') as f:
                d_reader = csv.DictReader(f, delimiter=self.delimiter)
                headers = d_reader.fieldnames
                print(headers)
            time.sleep(2)
            with open(self.filepath_results, "a", newline='', encoding='utf_8') as csvfile:
                writer = csv.writer(csvfile, delimiter=self.delimiter)
                row = []
                print(headers)
                for field in range(0, len(headers)):
                    row.append(fields[headers[field]])
                writer.writerow(row)
        except (PermissionError, KeyError):
            print("Can not access results file, saving backup!")
            try:
                participant_number = self.get_participant_number()
            except PermissionError:  # file can't be read
                participant_number = "unknown"
            self.filepath_results = path[0]+"/"+str(participant_number)+"_backup_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".csv"
            print("Backup file: {}".format(self.filepath_results))
            with open(self.filepath_results, "w+", newline='', encoding='utf_8') as csvfile:
                writer = csv.writer(csvfile, delimiter=self.delimiter)
                header = list(fields.keys())
                writer.writerow(header)
                row = []
                for field in range(0, len(header)):
                    row.append(fields[header[field]])
                writer.writerow(row)

        print("DONE")
        self.saved = True
        if self.help_client is not None:
            self.help_client.send_message("/questionnaire_finished", "")

    def get_participant_number(self):
        """
        Get the number for the next participant according to how many rows the csv-file already has.

        Returns
        -------
        int
            continuous number for participant
        """
        if os.path.exists(self.filepath_results):
            with open(self.filepath_results, "r") as csvfile:
                reader = csv.reader(csvfile)
                participant_number = sum(1 for _ in reader)
        else:
            participant_number = 1
        return participant_number

    def is_connected(self):
        """Check the internet connection."""
        if self.audio_ip is not None:
            host = self.audio_ip
            response = ping(host, timeout=TIMEOUT)
            if response is None:
                if self.help_client is not None:
                    self.help_client.send_message("/connection_lost", "")
                msg = QMessageBox()
                msg.setWindowTitle(self.connection_lost_title)
                msg.setSizeGripEnabled(True)
                msg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                msg.setIcon(QMessageBox.Information)
                msg.setText(self.connection_lost_text)
                msg.exec_()
        if self.video_ip is not None:
            host = self.video_ip
            response = ping(host, timeout=TIMEOUT)
            if response is None:
                if self.help_client is not None:
                    self.help_client.send_message("/connection_lost", "")
                msg = QMessageBox()
                msg.setWindowTitle(self.connection_lost_title)
                msg.setSizeGripEnabled(True)
                msg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                msg.setIcon(QMessageBox.Information)
                msg.setText(self.connection_lost_text)
                msg.exec_()
        if self.pupil_ip is not None:
            host = self.pupil_ip
            response = ping(host, timeout=TIMEOUT)
            if response is None:
                if self.help_client is not None:
                    self.help_client.send_message("/connection_lost", "")
                msg = QMessageBox()
                msg.setWindowTitle(self.connection_lost_title)
                msg.setSizeGripEnabled(True)
                msg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                msg.setIcon(QMessageBox.Information)
                msg.setText(self.connection_lost_text)
                msg.exec_()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='filename of the questionnaire file', required=True, type=str)
    args = parser.parse_args()

    app = QApplication(sys.argv)
    ex = StackedWindowGui(args.file)
    sys.exit(app.exec_())
