"""
This class creates a button with additional functionality to interact with PupilCore.
"""
import datetime
from time import time

import msgpack as serializer
import zmq
from PySide6.QtCore import QTimer
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLineEdit, QPlainTextEdit
from PasswordEntry import PasswordEntry


class Button(QWidget):
    """Button with custom functionality for interacting with Pupil Core."""

    def __init__(self, inscription, function, parent, qid, recording_name=None, objectname=None, annotation=None):
        """
            Create a button and connect to its functionality.

            Parameters
            ----------
            inscription : Union(str, None)
                the text displayed on the button, if None the Button will be invisible
            function : str
                shorthand hint for functionality
            parent : QObject
                the page the button is on
            qid : Union(str, None)
                id of the question, if None invisible Button that just triggers the function
            recording_name : str, optional
                name for the recording folder(?)
            objectname : str, optional
                name of the object, if it is supposed to be styled individually
            annotation : str, optional
                text for the annotation, "test" if None is given
        """
        QWidget.__init__(self, parent=parent)
        self.page = parent
        self.id = qid
        self.config_win = None
        if objectname is not None:
            self.setObjectName(objectname)
            self.name = objectname
        else:
            self.name = None
        if hasattr(self.page, "pupil_remote") and self.page.pupil_remote is not None:
            self.pupil_remote = self.page.pupil_remote
            self.ctx = self.page.ctx
            self.ip = self.page.pupil_ip
        elif hasattr(self.page.gui, "pupil_remote") and self.page.gui.pupil_remote is not None:
            self.pupil_remote = self.page.gui.pupil_remote
            self.ctx = self.page.gui.ctx
            self.ip = self.page.gui.pupil_ip
        else:
            self.pupil_remote = None
        self.recording_name = recording_name
        self.pub_socket = None
        if inscription is not None:
            layout = QHBoxLayout()
            self.button = QPushButton(inscription)
            self.button.setObjectName(self.objectName())
            self.button_fade = self.page.gui.button_fade
            layout.addWidget(self.button)
            self.used = False
            if function == "Calibration":
                raise NotImplementedError
            if function == "Recording":
                self.button.clicked.connect(self.start_recording)
            elif function == "Stop":
                self.button.clicked.connect(self.stop_recording)
            elif function == "Annotate":
                if self.page.gui.popup and not self.page.gui.preview:
                    self.setup_annotate()
                self.button.clicked.connect(lambda: self.send_trigger(self.new_trigger("test" if annotation is None else str(annotation))))
            self.button.clicked.connect(self.log)
            self.button.clicked.connect(lambda: self.__click_animation(self.button))
            self.setLayout(layout)
        elif function == "Annotate":  # the only function that needs setup
            self.setup_annotate()
        '''
        'R'  # start recording with auto generated session name
        'R rec_name'  # start recording named "rec_name"
        'r'  # stop recording
        'C'  # start currently selected calibration
        'c'  # stop currently selected calibration
        'T 1234.56'  # resets current Pupil time to given timestamp
        't'  # get current Pupil time; returns a float as string.
        'v'  # get the Pupil Core software version string
        '''

    def __click_animation(self, btn):
        __btn = btn
        __btn.setDown(True)
        QTimer.singleShot(self.button_fade, lambda: __btn.setDown(False))

    def start_recording(self):
        """
        Start the recording process of the pupil core tracking.

        Raises
        ------
        zmq.ZMQError, AttributeError
            If there are connection problems
        """
        self.used = True
        try:
            if self.recording_name is None:
                # print("just record...")
                self.pupil_remote.send_string('R')
            else:
                if self.recording_name.startswith("id:"):
                    # print("recording name starts with id")
                    var = self.recording_name[2:].strip(' :')
                    skip = False
                    for s in range(0, self.page.gui.count()):
                        if not skip and self.page.gui.widget(s).evaluationvars is not None and \
                                var in self.page.gui.widget(s).evaluationvars:
                            self.recording_name = self.page.gui.widget(s).evaluationvars[var]
                            if isinstance(self.recording_name, (QLineEdit, PasswordEntry)):
                                if isinstance(self.recording_name.validator(), QDoubleValidator):
                                    self.recording_name.setText(self.recording_name.text().replace(",", "."))
                                self.recording_name = self.recording_name.text()
                            elif isinstance(self.recording_name, QPlainTextEdit):
                                self.recording_name = self.recording_name.toPlainText().replace("\n", " ")
                        if not skip and self.page.gui.widget(s) == self.page:
                            skip = True
                print("Recording name:",self.recording_name)
                self.pupil_remote.send_string(f'R {self.recording_name}')
            print("Start recording...", self.pupil_remote.recv_string())
        except (zmq.ZMQError, AttributeError):
            print("Couldn't connect with Pupil Capture!")

    def stop_recording(self):
        """
        Stop the recording process of the pupil core tracking.

        Raises
        ------
        zmq.ZMQError, AttributeError
            If there are connection problems
        """
        self.used = True
        try:
            self.pupil_remote.send_string('r')
            print("Stop recording...", self.pupil_remote.recv_string())
        except (zmq.ZMQError, AttributeError):
            print("Couldn't connect with Pupil Capture!")

    def setup_annotate(self):
        """Put annotations in the recoding.

        Raises
        ------
        zmq.ZMQError, AttributeError
            If there are connection problems

        Notes
        -----
        Credits to: https://github.com/pupil-labs/pupil-helpers/blob/master/python/remote_annotations.py
        """
        try:
            # create and connect PUB socket to IPC
            self.pupil_remote.send_string("PUB_PORT")
            pub_port = self.pupil_remote.recv_string()
            self.pub_socket = zmq.Socket(self.ctx, zmq.PUB)
            # self.pub_socket.setsockopt(zmq.LINGER, 0)  # ____POLICY: set upon instantiations
            # self.pub_socket.setsockopt(zmq.RCVTIMEO, 2000)
            self.pub_socket.connect(f'tcp://{self.ip}:{pub_port}')
            # In order for the annotations to be correlated correctly with the rest of
            # the data it is required to change Pupil Capture's time base to this scripts
            # clock. We only set the time base once. Consider using Pupil Time Sync for
            # a more precise and long term time synchronization

            # Set Pupil Capture's time base to this scripts time. (Should be done before
            # starting the recording)

            self.pupil_remote.send_string(f'T {time()}')
            print("Annotate...", self.pupil_remote.recv_string())

            # Start the annotations plugin
            self.notify({"subject": "start_plugin", "name": "Annotation_Capture", "args": {}})
        except (zmq.ZMQError, AttributeError):
            print("Couldn't connect with Pupil Capture!")

    def notify(self, notification):
        """Sends ``notification`` to Pupil Core.

        Used as setup to start the Annotation Capture plugin.

        Parameters
        ----------
        notification : dict
            the notification to be sent, must include subject and name

        Returns
        -------
        str
            answer from Pupil Core
        """
        topic = "notify." + notification["subject"]
        payload = serializer.dumps(notification, use_bin_type=True)
        self.pupil_remote.send_string(topic, flags=zmq.SNDMORE)
        self.pupil_remote.send(payload)
        return self.pupil_remote.recv_string()

    def send_trigger(self, trigger):
        """Send a trigger with the current time
            The annotation will be saved to annotation.pldata if a
            recording is running. The Annotation_Player plugin will automatically
            retrieve, display and export all recorded annotations.

            Parameters
            ----------
            trigger : dict
                data to be sent, should include topic, label, timestamp, and duration

        """
        self.used = True
        if self.pub_socket is not None:
            payload = serializer.dumps(trigger, use_bin_type=True)
            try:
                self.pupil_remote.send_string(trigger["topic"], flags=zmq.SNDMORE)
                self.pupil_remote.send(payload)
                recv = self.pupil_remote.recv_string()
                print("Trigger", trigger, recv)  # this *somehow* makes the annotations work
            except zmq.ZMQError:
                print("Couldn't connect with Pupil Capture!")
                self.pub_socket.close()
                print("Connection to pupil closed.")
        else:
            print("Couldn't connect with Pupil Capture!")

    @staticmethod
    def new_trigger(label, duration=1):
        """Basic trigger structure

        Parameters
        ----------
        label : str
            text for the annotation
        duration : int, default=1
            time to display the annotation
        """
        return {
            "topic": "annotation",
            "label": label,
            "timestamp": time(),  # time.asctime(time.localtime()); for Pupil Core > v3.4.0 NEEDS to be of type float
            "duration": duration,
        }

    def log(self):
        """Log Action"""
        self.page.page_log += f'\n\t{str(datetime.datetime.now().replace(microsecond=0))} - Pressed Button {self.id}'
