"""MUSHRA question unit"""
import datetime
from time import time

from PySide6.QtCore import Qt, QSignalMapper, QTimer
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QSizePolicy

from Slider import Slider


class MUSHRA(QWidget):
    """ MUSHRA question unit\n
    Command help for REAPER: https://wiki.cockos.com/wiki/index.php/Action_List_Reference\n
    Participants can rate different stimuli in comparison to each other and a reference.\n
    IMPORTANT: The REAPER commands below are different for every PC, you have to change them by hand!
    The scripts are available in the repository, refer to the wiki for further instructions.

    Attributes
    ----------
    loop_on_command : str
        REAPER command to set looped
    loop_off_command : str
        REAPER command to un-set looped
    mushra_play_on_stopped : str
        REAPER command needed to play a xfade stimuli after the player has stopped
    set_loop_start : int
        REAPER command to mark the beginning of a loop
    set_loop_end : int
        REAPER command to mark the end of a loop
    solo_track : int
        REAPER command to mute all other tracks than the one specified
    unsolo_all : int
        REAPER command to remove any solo-states
    """

    loop_on_command = "_RSa8eee394f75b27ef6bb9f0e15b6bee26d9363990"  # TODO this needs to be changed to your command
    loop_off_command = "_RS1a294fa76c361055992ccea256af42946825c67d"  # TODO this needs to be changed to your command
    mushra_play_on_stopped = "_RS85691a3ff5f25c9f0c1efcce666cdf8b1387f9e2"  # TODO this needs to be changed to your command

    set_loop_start = 40222
    set_loop_end = 40223
    solo_track = 41558
    unsolo_all = 41185

    def __init__(self, start_cues, end_cues, tracks, qid, allow_xfade=True, hidden_reference=False, random_order=False, parent=None, objectname=None):
        """
            Create the layout.

            Parameters
            ----------
            start_cues : list[int]
                cue/marker numbers where the playback should start, the first entry will be the reference
            end_cues : list[int]
                cue/marker numbers where the playback should stop, the first entry will be the reference
            tracks : list[int] or int or list[list[int]]
                list of active tracks per stimulus
            qid : str
                id of the question
            allow_xfade : bool, default=True
                if applicable allow a crossfade between stimuli if desired
            hidden_reference : bool, default=False
                if False, the reference will have an own button without a slider
            random_order : bool, default=False
                if True, the order of the stimuli will be randomized
            parent : QObject, optional
                widget/layout this widget is embedded in
            objectname : str, optional
                name of the object, if it is supposed to be styled individually
        """
        QWidget.__init__(self, parent=parent)
        self.page = parent
        self.audio_client = self.page.gui.audio_client
        self.audio_tracks = self.page.gui.audio_tracks
        self.button_fade = self.page.gui.button_fade
        if objectname is not None:
            self.setObjectName(objectname)
            self.name = objectname
        else:
            self.name = None
        self.id = qid
        self.start_cues = start_cues
        self.end_cues = end_cues
        if isinstance(tracks, str) and ("[" not in tracks and "]" not in tracks and "," not in tracks):
            tracks = [int(tracks)]
        self.tracks = tracks
        if self.audio_tracks < max(self.tracks):
            self.audio_tracks = max(self.tracks)
            self.page.gui.audio_tracks = max(self.tracks)
        self.start = 0
        self.end = 0
        self.looped = False
        self.duration = []
        self.playing = False
        self.paused = False
        self.current = -1
        self.last_sender = -1
        h = QHBoxLayout()
        self.sliders = []
        self.labels = []
        self.buttons = []
        self.slider_height = int(self.page.gui.height() * 2 / 3)
        mapper = QSignalMapper(self)
        self.conditionsUseSameMarker = False
        if allow_xfade:
            all_same_marker = True
            for cue in start_cues:
                if cue != start_cues[0]:
                    all_same_marker = False
            for cue in end_cues:
                if cue != end_cues[0]:
                    all_same_marker = False
            if all_same_marker:
                self.conditionsUseSameMarker = True

        for m in range(0, len(self.start_cues)):
            vbox = QVBoxLayout()

            if m == 0:
                height = self.slider_height
                labels = QVBoxLayout()
                labels.addWidget(QLabel(""))
                labels.addStretch(int(height / 10))
                l90 = QLabel("excellent")
                l90.setObjectName(self.objectName())
                l90.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                labels.addWidget(l90)
                labels.addStretch(int(height / 5))
                l70 = QLabel("good")
                l70.setObjectName(self.objectName())
                l70.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                labels.addWidget(l70)
                labels.addStretch(int(height / 5))
                l50 = QLabel("fair")
                l50.setObjectName(self.objectName())
                l50.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                labels.addWidget(l50)
                labels.addStretch(int(height / 5))
                l30 = QLabel("poor")
                l30.setObjectName(self.objectName())
                l30.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                labels.addWidget(l30)
                labels.addStretch(int(height / 5))
                l10 = QLabel("bad")
                l10.setObjectName(self.objectName())
                l10.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                labels.addWidget(l10)
                labels.addStretch(int(height / 10))
                self.refbutton = QPushButton("Reference")
                self.refbutton.setObjectName(self.objectName())
                self.refbutton.clicked.connect(lambda: self.play(0, self.refbutton))
                self.refbutton.clicked.connect(lambda: self.__click_animation(self.refbutton))
                labels.addWidget(self.refbutton)
                h.addItem(labels)
                h.addSpacing(5)
            else:
                slider = Slider(Qt.Orientation.Vertical, parent=parent)
                slider.setObjectName(self.objectName())
                slider.setMinimumHeight(self.slider_height)
                slider.prepare_slider(min_val=0, max_val=100, start=100, step=1, tick_interval=20, tickpos=QSlider.TickPosition.TicksLeft, sid=f'{self.id}_{len(self.sliders) + 1}')
                slider.setEnabled(False)
                self.sliders.append(slider)
                slider.mushra_stopped.connect(self.raise_log)
                lbl = QLabel(f'{slider.value()}')
                lbl.setObjectName(self.objectName())
                lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                self.labels.append(lbl)
                slider.valueChanged.connect(self.update_label)
                start_button = QPushButton(f'{m}')
                start_button.setObjectName(self.objectName())
                self.buttons.append(start_button)
                start_button.clicked.connect(mapper.map)
                start_button.clicked.connect(lambda: self.__click_animation(start_button))
                mapper.setMapping(start_button, m)
                sliderlayout = QVBoxLayout()
                sliderlayout.addWidget(slider)
                sliderlayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                vbox.addWidget(lbl)
                vbox.addItem(sliderlayout)
                vbox.addWidget(start_button)
                vbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            h.addItem(vbox)
            self.duration.append([])
        mapper.mappedInt.connect(self.play)
        player = QHBoxLayout()
        self.loop_button = QPushButton("Loop")
        self.loop_button.setObjectName(self.objectName())
        self.loop_button.setCheckable(True)
        self.loop_button.clicked.connect(self.loop)
        if self.audio_client is not None:
            self.audio_client.send_message("/action", self.loop_off_command)
        self.pause_button = QPushButton("Pause", None)
        self.pause_button.setEnabled(False)
        self.pause_button.setObjectName(self.objectName())
        self.pause_button.setCheckable(True)
        self.stop_button = QPushButton("Stop", None)
        self.stop_button.setObjectName(self.objectName())
        self.stop_button.setEnabled(False)
        if self.conditionsUseSameMarker:
            self.xfade = QPushButton("XFade")
            self.xfade.setObjectName(self.objectName())
            self.xfade.setCheckable(True)
            self.xfade.clicked.connect(self.fade)
        self.xfade_in_use = False
        self.pause_button.clicked.connect(self.pause)
        self.stop_button.clicked.connect(self.stop)
        player.addWidget(self.loop_button)
        if self.conditionsUseSameMarker:
            player.addWidget(self.xfade)
        player.addWidget(self.pause_button)
        player.addWidget(self.stop_button)
        player.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout()
        layout.addItem(h)
        layout.addItem(player)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setLayout(layout)

    def __click_animation(self, btn):
        __btn = btn
        __btn.setDown(True)
        QTimer.singleShot(self.button_fade, lambda: __btn.setDown(False))

    def fade(self):
        """Handle cross-fade."""
        if self.xfade.isChecked():
            self.xfade_in_use = True
            if not self.looped and self.playing:
                self.loop_button.setDisabled(True)
                self.audio_client.send_message("/action", self.loop_off_command)
        else:
            self.xfade_in_use = False
            if not self.loop_button.isEnabled():
                self.loop_button.setEnabled(True)
            if self.playing:
                self.audio_client.send_message("/action", self.unsolo_all)
                for i in range(1, self.audio_tracks + 1):
                    if len(self.tracks) < len(self.buttons) + 1:  # only one track
                        if i in self.tracks:  # single track
                            self.audio_client.send_message(f'/track/{i}/mute', 0)
                        else:
                            self.audio_client.send_message(f'/track/{i}/mute', 1)
                    elif (len(self.tracks) == len(self.buttons) + 1) and (
                            not isinstance(self.tracks[self.last_sender], list)):  # 1 track per button
                        if i == self.tracks[self.last_sender]:
                            self.audio_client.send_message(f'/track/{i}/mute', 0)
                        else:
                            self.audio_client.send_message(f'/track/{i}/mute', 1)
                    elif (len(self.tracks) == len(self.buttons) + 1) and (
                            not isinstance(self.tracks[self.last_sender], list)):  # more than one track per stimulus
                        if i in self.tracks[self.last_sender]:
                            self.audio_client.send_message(f'/track/{i}/mute', 0)
                        else:
                            self.audio_client.send_message(f'/track/{i}/mute', 1)

    def update_label(self):
        """Update the label above the slider that indicates the handle position, when the handle was moved."""
        for s, sli in enumerate(self.sliders):
            if self.labels[s].text() != str(sli.value()):
                self.labels[s].setText(f'{sli.value()}')
                self.labels[s].setFixedWidth(QLabel("100").maximumWidth())

    def raise_log(self, who):
        '''Make a log entry.

        Parameters
        ----------
        who : Slider
            The Slider whose signal that trigged a change in value.
        '''
        self.page.log(who, self.sliders[int(who.split('_')[1]) - 1])

    def loop(self):
        """Toggle looping."""
        self.looped = not self.looped
        if self.looped:
            self.loop_button.setChecked(True)
            self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Loop on {self.id}'
            self.audio_client.send_message("/action", self.loop_on_command)
        else:
            self.loop_button.setChecked(False)
            self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Loop off {self.id}'
            self.audio_client.send_message("/action", self.loop_off_command)

    def pause(self):
        """Pause the current playback and resume at that position of the playback."""
        if self.playing:
            self.playing = False
            self.paused = True
            self.audio_client.send_message("/pause", 1)
            self.pause_button.setChecked(True)
            self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Paused MUSHRA-player {self.id}'
            self.end = time()
            self.duration[self.current].append(self.end - self.start)
        else:
            self.playing = True
            self.paused = False
            self.audio_client.send_message("/pause", 1)
            self.pause_button.setChecked(False)
            self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Unpaused MUSHRA-player {self.id}'
            self.start = time()
            self.end = 0

    def play(self, cue=None, btn=None):
        """
            Start the playback of audio of the according stimulus.

            Parameters
            ----------
            cue : int, default=None
                index of the stimulus in the start/end cues array
            btn: QPushButton, default=None
                button which initiated play
        """
        if self.audio_tracks != self.page.gui.audio_tracks:
            self.audio_tracks = self.page.gui.audio_tracks
        for player in self.page.players:
            if player.playing and (not player == self and not self.conditionsUseSameMarker or (self.conditionsUseSameMarker and not self.xfade.isChecked())):
                player.stop()
        self.pause_button.setEnabled(True)
        self.pause_button.setChecked(False)
        self.stop_button.setEnabled(True)

        if self.paused and self.current == cue:
            # print("pause")
            self.audio_client.send_message("/pause", 1)
            self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Unpaused Player {self.id}'
        else:
            if btn != self.refbutton:
                if self.sender().sender() in self.buttons:
                    for s, sli in enumerate(self.sliders):
                        if s != self.buttons.index(self.sender().sender()):
                            sli.setEnabled(False)
                        else:
                            sli.setEnabled(True)

                sender = 0 if self.sender().sender() not in self.buttons else self.buttons.index(self.sender().sender()) + 1
            else:
                sender = 0

            self.audio_client.send_message("/action", 40297)  # unselect all
            if isinstance(self.tracks, list) and len(self.tracks) == len(self.buttons) + 1 and isinstance(self.tracks[sender], list):
                for t in self.tracks[sender]:
                    self.audio_client.send_message(f'/track/{t}/select', 1)  # add t to selection
            self.audio_client.send_message("/action", 40341)  # mute all
            if isinstance(self.tracks, int):
                self.audio_client.send_message(f'/track/{self.tracks}/mute', 0)
            elif isinstance(self.tracks, list) and len(self.tracks) < len(self.buttons) + 1:
                for t in self.tracks:
                    self.audio_client.send_message(f'/track/{t}/select', 1)  # add t to selection
                self.audio_client.send_message("/action", 40280)  # toggle mute for selected tracks
            elif isinstance(self.tracks[sender], int):
                self.audio_client.send_message(f'/track/{self.tracks[sender]}/mute', 0)
            else:
                self.audio_client.send_message("/action", 40280)  # toggle mute for selected tracks

            if self.conditionsUseSameMarker and self.xfade.isChecked() and not self.looped:
                self.loop_button.setDisabled(True)
                self.audio_client.send_message("/action", self.loop_off_command)
            if not self.conditionsUseSameMarker or (self.conditionsUseSameMarker and not self.xfade.isChecked()):
                if not self.loop_button.isEnabled():
                    self.loop_button.setEnabled(True)
                self.audio_client.send_message("/stop", 1)
                if self.looped:
                    if int(self.end_cues[cue]) < 10:
                        self.audio_client.send_message("/action", 40160 + int(self.end_cues[cue]))  # goto cue
                    elif int(self.end_cues[cue]) == 10:
                        self.audio_client.send_message("/action", 40160)  # goto cue
                    else:
                        self.audio_client.send_message("/action", 41240 + int(self.end_cues[cue]))  # goto cue
                    self.audio_client.send_message("/action", self.set_loop_end)  # end of loop
                    if int(self.start_cues[cue]) < 10:
                        self.audio_client.send_message("/action", 40160 + int(self.start_cues[cue]))  # goto cue
                    elif int(self.start_cues[cue]) == 10:
                        self.audio_client.send_message("/action", 40160)  # goto cue
                    else:
                        self.audio_client.send_message("/action", 41240 + int(self.start_cues[cue]))  # goto cue
                    self.audio_client.send_message("/action", self.set_loop_start)  # start of loop
                else:
                    if int(self.start_cues[cue]) < 10:
                        self.audio_client.send_message("/action", 40160 + int(self.start_cues[cue]))  # goto cue
                    elif int(self.start_cues[cue]) == 10:
                        self.audio_client.send_message("/action", 40160)  # goto cue
                    else:
                        self.audio_client.send_message("/action", 41240 + int(self.start_cues[cue]))  # goto cue
                self.audio_client.send_message("/play", 1)
            if self.conditionsUseSameMarker and self.xfade.isChecked() and not self.playing and not self.paused:
                if self.looped:
                    if int(self.end_cues[cue]) < 10:
                        self.audio_client.send_message("/action", 40160 + int(self.end_cues[cue]))  # goto cue
                    elif int(self.end_cues[cue]) == 10:
                        self.audio_client.send_message("/action", 40160)  # goto cue
                    else:
                        self.audio_client.send_message("/action", 41240 + int(self.end_cues[cue]))  # goto cue
                    self.audio_client.send_message("/action", self.set_loop_end)  # end of loop
                    if int(self.start_cues[cue]) < 10:
                        self.audio_client.send_message("/action", 40160 + int(self.start_cues[cue]))  # goto cue
                    elif int(self.start_cues[cue]) == 10:
                        self.audio_client.send_message("/action", 40160)  # goto cue
                    else:
                        self.audio_client.send_message("/action", 41240 + int(self.start_cues[cue]))  # goto cue
                    self.audio_client.send_message("/action", self.set_loop_start)  # start of loop
                else:
                    if int(self.start_cues[cue]) < 10:
                        self.audio_client.send_message("/action", 40160 + int(self.start_cues[cue]))  # goto cue
                    elif int(self.start_cues[cue]) == 10:
                        self.audio_client.send_message("/action", 40160)  # goto cue
                    else:
                        self.audio_client.send_message("/action", 41240 + int(self.start_cues[cue]))  # goto cue

            if self.conditionsUseSameMarker and self.xfade.isChecked() and not self.paused:
                if not self.playing:
                    if int(self.start_cues[cue]) < 10:
                        self.audio_client.send_message("/action", 40160 + int(self.start_cues[cue]))  # goto cue
                    elif int(self.start_cues[cue]) == 10:
                        self.audio_client.send_message("/action", 40160)  # goto cue
                    else:
                        self.audio_client.send_message("/action", 41240 + int(self.start_cues[cue]))  # goto cue
                self.audio_client.send_message("/action", self.mushra_play_on_stopped)
            elif self.conditionsUseSameMarker and self.xfade.isChecked() and self.paused:
                self.audio_client.send_message("/pause", 1)
                self.paused = False
            self.last_sender = sender
        if (self.start != 0) and self.playing:
            self.end = time()
            self.duration[self.current].append(self.end - self.start)
        self.current = cue
        self.start = time()
        self.end = 0
        self.playing = True
        self.paused = False
        self.loop_button.setDisabled(True)
        self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - (Re-)Started MUSHRA-player for cue {self.start_cues[cue]} {self.id}_{str(cue)}'

    def stop(self):
        """
            Stop the playback, calculate the time it played.
        """
        self.audio_client.send_message("/stop", 1)
        if self.playing:
            self.end = time()
            self.duration[self.current].append(self.end - self.start)
        if not self.loop_button.isEnabled():
            self.loop_button.setEnabled(True)
        self.start = 0
        self.playing = False
        self.paused = False
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.pause_button.setChecked(False)
        self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Stopped MUSHRA playback {self.id}'
