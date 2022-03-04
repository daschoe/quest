"""
This class creates a button with additional functionality to interact by sending an OSC command.
"""
import datetime
from ping3 import ping
from pythonosc import udp_client

from PyQt5.QtCore import QTimer, QObject
from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QMessageBox, QSizePolicy


class OSCButton(QWidget):
    """Button with custom functionality for interacting by sending an OSC command.

    Attributes
    ----------
    inscription : str
        the text displayed on the button
    function : (str, int)
        string for the OSC command
    parent : QObject
        the page the button is on
    qid : str
        id of the question
    receiver : (str, int),
        IP + Port of the receiver
    objectname : str, optional
        name of the object, if it is supposed to be styled individually
    """

    def __init__(self, inscription, function, parent, qid, receiver, objectname=None):
        """
            Create a button.

            Parameters
            ----------
            inscription : str
                the text displayed on the button
            function : (str, int)
                command to send
            parent : QObject
                the page the button is on
            qid : str
                id of the question
            receiver : (str, int)
                IP + Port of the receiver
            objectname : str, optional
                name of the object, if it is supposed to be styled individually
        """
        QWidget.__init__(self, parent=parent)
        self.id = qid
        self.used = False
        if objectname is not None:
            self.setObjectName(objectname)
            self.name = objectname
        else:
            self.name = None

        self.osc_client = udp_client.SimpleUDPClient(receiver[0], receiver[1])
        response = ping(receiver[0], timeout=self.parent().parent().TIMEOUT)
        if response is None:
            msg = QMessageBox()
            msg.setWindowTitle(self.parent().parent().connection_lost_title)
            msg.setSizeGripEnabled(True)
            msg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            msg.setIcon(QMessageBox.Information)
            msg.setText("No connection to {}.".format(receiver[0]))
            msg.exec_()

        if inscription is not None:
            layout = QHBoxLayout()
            self.button = QPushButton(inscription)
            self.button.setObjectName(self.objectName())
            self.button_fade = self.parent().parent().button_fade
            layout.addWidget(self.button)
            self.button.clicked.connect(lambda: self.osc_client.send_message(function[0], function[1]))
            self.button.clicked.connect(self.set_used)
            self.button.clicked.connect(self.log)
            self.button.clicked.connect(self.__click_animation)
            self.setLayout(layout)

    def set_used(self):
        self.used = True

    def __click_animation(self):
        __btn = self.sender()
        __btn.setDown(True)
        QTimer.singleShot(self.button_fade, lambda: __btn.setDown(False))

    def log(self):
        """Log Action"""
        self.parent().page_log += "\n\t{} - Pressed OSC-Button {} ".format(datetime.datetime.now().replace(microsecond=0).__str__(), self.id)
