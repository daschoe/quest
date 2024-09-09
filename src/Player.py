"""
Audio/Video Player Control
"""
import datetime
from time import time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QStyle, QFormLayout

from src.PupilCoreButton import Button
from src.tools import player_buttons
from src.Video import madmapper, vlc


class Player(QWidget):
    """Multi-Media player unit."""

    def __init__(self, start_cue, track, qid, video=None, parent=None, end_cue=None,
                 displayed_buttons=player_buttons, icons=False, pupil=None, objectname=None, timer=None,
                 play_button_text=None, play_once=False, crossfade=False):
        """Create the layout of the player.

        Parameters
        ----------
        start_cue : int
            cue/marker number on which to start playing (e.g. in REAPER)
        track : Union(int, list of int)
            active tracks (e.g. in REAPER)
        video : str, optional
            filename+path / scene name to the video which should be played.
        qid : str
            id of the question
        parent : QObject, optional
            widget/layout this widget is embedded in
        end_cue : int, optional
            cue/marker on which to stop playing (e.g. in REAPER); might be removed in future versions
        displayed_buttons : list of str, default=["Play", "Pause", "Stop"]
            list of buttons which should be displayed
        icons : bool, optional, default=False
            if True, icons according to the functionality are displayed on the buttons
        pupil : str, optional
            annotation text to send to Pupil Core when the play button is clicked
        objectname : str, optional
            name of the object, if it is supposed to be styled individually
        timer : int, optional
            time in msec after which succeeding questions on the page are displayed
        play_button_text : str, optional
            alternate text for the play button
        play_once : bool, default=False
            if True makes it possible to play the stimuli only one time
        crossfade : bool, default=False
            if True successively started players with the same start_cue will crossfade and not restart
        """
        QWidget.__init__(self, parent=parent)
        self.page = parent
        self.gui = self.page.parent()  # self.parent??
        self.audio_client = self.gui.audio_client
        self.audio_tracks = self.gui.audio_tracks
        self.video_client = self.gui.video_client
        video_player = self.gui.video_player
        if video_player == "MadMapper":
            self.video_player = madmapper
        elif video_player == "VLC":
            self.video_player = vlc
        else:
            self.video_player = None
        if pupil is not None and not self.gui.preview:
            self.pupil_func = Button(None, "Annotate", parent, qid)
            self.pupil_message = pupil
        else:
            self.pupil_func = None

        self.button_fade = self.gui.button_fade
        self.crossfade = crossfade
        self.play_once = play_once

        if objectname is not None:
            self.setObjectName(objectname)
            self.name = objectname
        else:
            self.name = None
        self.id = qid
        self.start_cue = start_cue
        self.end_cue = end_cue
        if timer is not None:
            self.countdown = int(timer)
            self.timer = QTimer()
            self.timer.timeout.connect(self.timer_done)
        else:
            self.timer = None
        if isinstance(displayed_buttons, str):
            self.buttons = [displayed_buttons]  # to support just one button
        else:
            self.buttons = displayed_buttons
        if isinstance(track, str):
            track = [int(track)]
        else:
            for _, tra in enumerate(track):
                tra = int(tra)
        self.track = track
        self.video = video
        self.start = 0
        self.end = 0
        self.duration = []
        self.playing = False
        self.paused = False
        layout = QHBoxLayout()
        if "Play" in self.buttons:
            self.play_button = QPushButton("Play" if play_button_text is None else play_button_text, None)
            if icons:
                self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self.play_button.setEnabled(True)
            self.play_button.clicked.connect(self.play)
            self.play_button.clicked.connect(lambda: self.__click_animation(self.play_button))
            self.play_button.setObjectName(self.objectName())
            layout.addWidget(self.play_button)
        if "Pause" in self.buttons:
            self.pause_button = QPushButton("Pause", None)
            if icons:
                self.pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.pause_button.setEnabled(False)
            self.pause_button.setCheckable(True)
            self.pause_button.clicked.connect(self.pause)
            self.pause_button.setObjectName(self.objectName())
            layout.addWidget(self.pause_button)
        if "Stop" in self.buttons:
            self.stop_button = QPushButton("Stop", None)
            if icons:
                self.stop_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
            self.stop_button.setEnabled(False)
            self.stop_button.clicked.connect(self.stop)
            self.stop_button.setObjectName(self.objectName())
            layout.addWidget(self.stop_button)
        self.setLayout(layout)

    def __click_animation(self, btn):
        __btn = btn
        if not self.play_once and self.button_fade > 0:
            __btn.setDown(True)
            QTimer.singleShot(self.button_fade, lambda: __btn.setDown(False))

    def play(self):
        """Start the playback of audio (and video) of the stimulus."""
        previous_start = None
        for player in (self.page.players if str(type(self.page)) == "<class 'src.Page.Page'>" else self.gui.players):
            if player.playing and not player == self:
                if self.crossfade and player.crossfade:
                    previous_start = player.start_cue
                    self.start = player.start
                    player.stop_button.setEnabled(False)
                    player.playing = False
                    if self.video != player.video:
                        # TODO how to handle video during crossfade
                        if (self.video is not None) and (self.video_client is not None):
                            self.video_client.send_message(self.video_player["stop"][0], self.video_player["stop"][1])
                else:
                    player.stop()
                    if (self.video is not None) and (self.video_client is not None):
                        self.video_client.send_message(self.video_player["stop"][0], self.video_player["stop"][1])
        if "Stop" in self.buttons:
            self.stop_button.setEnabled(True)
        if "Pause" in self.buttons:
            self.pause_button.setEnabled(True)
            self.pause_button.setChecked(False)

        if self.paused:
            self.audio_client.send_message("/pause", 1)
            if (self.video is not None) and (self.video_client is not None):
                self.video_client.send_message(self.video_player["unpause"][0], self.video_player["unpause"][1])
            self.pause_button.setChecked(False)
            if str(type(self.page)) == "<class 'src.Page.Page'>":
                self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Unpaused Player {self.id}'
            else:
                self.gui.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Unpaused Player {self.id}'
        else:
            for i in range(1, self.audio_tracks + 1):
                if i in self.track:
                    self.audio_client.send_message(f'/track/{i}/mute', 0)
                else:
                    self.audio_client.send_message(f'/track/{i}/mute', 1)
            if not self.crossfade or (self.crossfade and self.start_cue != previous_start):
                if int(self.start_cue) < 10:
                    self.audio_client.send_message("/action", 40160 + int(self.start_cue))  # goto cue
                elif int(self.start_cue) == 10:
                    self.audio_client.send_message("/action", 40160)  # goto cue
                else:
                    self.audio_client.send_message("/action", 41240 + int(self.start_cue))  # goto cue
                self.gui.stop_initiated = True
                self.audio_client.send_message("/stop", 1)
                self.audio_client.send_message("/play", 1)
            elif self.crossfade and self.start_cue == previous_start and self.gui.global_play_state == "STOP":
                self.audio_client.send_message("/play", 1)
            if (self.video is not None) and (self.video_client is not None):
                if "select" in self.video_player:
                    self.video_client.send_message(self.video_player["reset"][0], self.video_player["reset"][1])
                    self.video_client.send_message(self.video_player["select"][0].format(self.video), self.video_player["select"][1])
                    self.video_client.send_message(self.video_player["play"][0], self.video_player["play"][1])
                else:
                    self.video_client.send_message(self.video_player["play"][0], self.video_player["play"][1].format(self.video))

            if str(type(self.page)) == "<class 'src.Page.Page'>":
                self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - (Re-)Started Player {self.id}'
            else:
                self.gui.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - (Re-)Started Player {self.id}'
        if (self.start != 0) and self.playing:
            self.end = time()
            self.duration.append(self.end - self.start)

        self.start = time()
        self.end = 0
        self.playing = True
        self.paused = False

        if self.pupil_func is not None:
            self.pupil_func.send_trigger(self.pupil_func.new_trigger(self.pupil_message))
        if self.timer is not None:
            self.timer.start(self.countdown)

        if self.play_once and "Play" in self.buttons:
            self.play_button.setEnabled(False)

    def timer_done(self):
        """Show the following elements on this page after the timer is finished."""
        self.timer.stop()
        self.countdown = 0
        player_found = False
        for item in range(self.page.layout().rowCount()):
            if player_found and self.page.layout().itemAt(item, QFormLayout.ItemRole.FieldRole).widget() is None:
                if isinstance(self.page.layout().itemAt(item, QFormLayout.ItemRole.FieldRole), QHBoxLayout):
                    for box in range(self.page.layout().itemAt(item, QFormLayout.ItemRole.FieldRole).count()):
                        self.page.layout().itemAt(item, QFormLayout.ItemRole.FieldRole).itemAt(box).widget().show()
                if self.page.layout().itemAt(item, QFormLayout.ItemRole.LabelRole) is not None:
                    self.page.layout().itemAt(item, QFormLayout.ItemRole.LabelRole).widget().show()
            if player_found and self.page.layout().itemAt(item, QFormLayout.ItemRole.FieldRole).widget() is not None:
                if self.page.layout().itemAt(item, QFormLayout.ItemRole.LabelRole) is not None:
                    self.page.layout().itemAt(item, QFormLayout.ItemRole.LabelRole).widget().show()
                self.page.layout().itemAt(item, QFormLayout.ItemRole.FieldRole).widget().show()
                if isinstance(self.page.layout().itemAt(item, QFormLayout.ItemRole.FieldRole).widget(), Player) and self.page.layout().itemAt(item, QFormLayout.ItemRole.FieldRole).widget() != self:
                    player_found = False
            if self.page.layout().itemAt(item, QFormLayout.ItemRole.FieldRole).widget() == self:
                player_found = True
        # self.stop() # not needed anymore

    def pause(self):
        """Pause the current playback and resume at that position."""
        if self.playing:
            self.playing = False
            self.audio_client.send_message("/pause", 1)
            if (self.video is not None) and (self.video_client is not None):
                self.video_client.send_message(self.video_player["pause"][0], self.video_player["pause"][1])
            self.pause_button.setChecked(True)
            if str(type(self.page)) == "<class 'src.Page.Page'>":
                self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Paused Player {self.id}'
            else:
                self.gui.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Paused Player {self.id}'
            self.end = time()
            self.duration.append(self.end - self.start)
            self.paused = True
            if self.timer is not None and self.countdown > self.timer.remainingTime():
                self.countdown = self.timer.remainingTime()
                self.timer.stop()
        else:
            self.playing = True
            self.audio_client.send_message("/pause", 1)
            if (self.video is not None) and (self.video_client is not None):
                self.video_client.send_message(self.video_player["unpause"][0], self.video_player["unpause"][1])
            self.pause_button.setChecked(False)
            if str(type(self.page)) == "<class 'src.Page.Page'>":
                self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Unpaused Player {self.id}'
            else:
                self.gui.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Unpaused Player {self.id}'
            self.start = time()
            self.end = 0
            self.paused = False
            if self.timer is not None:
                self.timer.start(self.countdown)

    def stop(self):
        """Stop the playback."""
        self.audio_client.send_message("/stop", 1)
        if (self.video is not None) and (self.video_client is not None) and not self.paused:
            self.video_client.send_message(self.video_player["stop"][0], self.video_player["stop"][1])
        self.end = time()
        self.duration.append(self.end - self.start)
        self.start = 0

        if "Stop" in self.buttons:
            self.stop_button.setEnabled(False)
        if "Play" in self.buttons:
            if self.play_once:
                self.play_button.setEnabled(False)
            else:
                self.play_button.setEnabled(True)
        if "Pause" in self.buttons:
            self.pause_button.setEnabled(False)
            self.pause_button.setChecked(False)
        if str(type(self.page)) == "<class 'src.Page.Page'>":
            self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Stopped Player {self.id}'
            # self.gui.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Stopped Player {self.id}'
        if self.timer is not None and self.timer.remainingTime() > 0 and self.countdown > 0:
            self.timer.stop()
        self.playing = False
        self.paused = False
        self.gui.stop_initiated = True
