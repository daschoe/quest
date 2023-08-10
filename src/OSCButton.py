"""
This class creates a button with additional functionality to interact by sending an OSC command.
"""
import datetime
from ping3 import ping
from pythonosc import udp_client

from PyQt5.QtCore import QTimer, QObject
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QMessageBox, QSizePolicy, QLineEdit, QPlainTextEdit

from src.PasswordEntry import PasswordEntry
TIMEOUT = 0.5


class OSCButton(QWidget):
    """Button with custom functionality for interacting by sending an OSC command.

    Attributes
    ----------
    inscription : str
        the text displayed on the button
    address : str
        address for the OSC command
    value: str or int
        value to send over OSC
    parent : QObject
        the page the button is on
    qid : str
        id of the question
    receiver : (str, int),
        IP + Port of the receiver
    objectname : str, optional
        name of the object, if it is supposed to be styled individually
    """

    def __init__(self, inscription, address, value, parent, qid, receiver, objectname=None):
        """
            Create a button.

            Parameters
            ----------
            inscription : str
                the text displayed on the button
            address : str
                command to send
            value : str or int
                value to send
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
        self.address = address
        self.value = value
        if self.value.startswith("id:"):
            var = self.value[2:].strip(' :')
            skip = False
            for s in range(0, self.parent().parent().count()):
                if not skip and self.parent().parent().widget(s).evaluationvars is not None and \
                        var in self.parent().parent().widget(s).evaluationvars:
                    self.value = self.parent().parent().widget(s).evaluationvars[var]
                    if type(self.value) is QLineEdit or type(self.value) is PasswordEntry:
                        if type(self.value.validator()) == QDoubleValidator:
                            self.value.setText(self.value.text().replace(",", "."))
                        self.value = self.value.text()
                    elif type(self.value) is QPlainTextEdit:
                        self.value = self.value.toPlainText().replace("\n", " ")
                if not skip and self.parent().parent().widget(s) == self.parent():
                    skip = True

        try:  # try to send float if possible
            self.value = float(self.value)
        except ValueError:
            self.value = str(self.value)
        if objectname is not None:
            self.setObjectName(objectname)
            self.name = objectname
        else:
            self.name = None
        if (receiver[0] == self.parent().parent().audio_ip) and (receiver[1] == self.parent().parent().audio_port):
            self.osc_client = self.parent().parent().audio_client
        elif (receiver[0] == self.parent().parent().video_ip) and (receiver[1] == self.parent().parent().video_port):
            self.osc_client = self.parent().parent().video_client
        elif (receiver[0] == self.parent().parent().help_ip) and (receiver[1] == self.parent().parent().help_port):
            self.osc_client = self.parent().parent().help_client
        elif (receiver[0] == self.parent().parent().global_osc_ip) and (receiver[1] == self.parent().parent().global_osc_send_port):
            self.osc_client = self.parent().parent().global_osc_client
        else:
            self.osc_client = udp_client.SimpleUDPClient(receiver[0], int(receiver[1]))
        response = ping(receiver[0], timeout=TIMEOUT)
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
            self.button.clicked.connect(lambda: self.osc_client.send_message(address, self.value))
            self.button.clicked.connect(self.set_used)
            self.button.clicked.connect(self.log)
            self.button.clicked.connect(self.__click_animation)
            self.setLayout(layout)

    def set_used(self):
        """Mark self as clicked."""
        self.used = True

    def get_used(self):
        """ Get the status if the button has been clicked.

        Returns
        -------
        bool
        """
        return self.used

    def __click_animation(self):
        __btn = self.sender()
        __btn.setDown(True)
        QTimer.singleShot(self.button_fade, lambda: __btn.setDown(False))

    def log(self):
        """Log Action"""
        self.parent().page_log += "\n\t{} - Pressed OSC-Button {} ".format(datetime.datetime.now().replace(microsecond=0).__str__(), self.id)
