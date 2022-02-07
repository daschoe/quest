"""Some functions that get used in each test file."""
import os

import keyboard
import psutil
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QMessageBox, QLineEdit, QWidgetItem, QHBoxLayout

PUPIL_PATH = "C:\Program Files (x86)\Pupil-Labs\Pupil v3.4.0\Pupil Capture v3.4.0\pupil_capture.exe"


def handle_dialog_p():
    """Set page name in popup dialog."""
    dialog = QApplication.activeModalWidget()
    dialog.findChild(QLineEdit).setText("Page 1")
    dialog.accept()


def handle_dialog_q():
    """Set question name in popup dialog."""
    dialog = QApplication.activeModalWidget()
    dialog.findChild(QLineEdit).setText("Question 1")
    dialog.accept()


def handle_dialog():
    """Click 'Yes' on save dialog."""
    dialog = QApplication.activeModalWidget()
    QTest.mouseClick(dialog.buttons()[0], Qt.LeftButton)


def handle_dialog_no_save():
    """Click 'No' on save dialog."""
    dialog = QApplication.activeModalWidget()
    QTest.mouseClick(dialog.buttons()[1], Qt.LeftButton)


def handle_dialog_error():
    """Click 'OK' on error dialog."""
    dialog = QApplication.activeModalWidget()
    #print(dialog.detailedText())
    QTest.mouseClick(dialog.button(QMessageBox.Ok), Qt.LeftButton)


def handle_dialog_warning():
    """Click 'Yes' on dialog and execute questionnaire."""
    dialog = QApplication.activeModalWidget()
    QTest.mouseClick(dialog.button(QMessageBox.Yes), Qt.LeftButton)


def open_config_file(conf_name):
    """Type filename."""
    QTest.qWait(50)
    dialog = QApplication.activeModalWidget()
    print("dir", dialog.directory().dirName())
    if dialog.directory().dirName() != "test":
        dialog.setDirectory(dialog.directory().path() + "\\test")
        print("dir now", dialog.directory().dirName())
    fp = conf_name.split("/")
    QTest.qWait(50)
    keyboard.write(fp[-1])
    keyboard.press("enter")
    print(dialog.selectedFiles())


def find_row_by_label(layout, label):
    """
    Search for row with label in QFormLayout

    Parameters
    ----------
    layout: QFormLayout
        QFormLayout to be searched
    label: str
        label of the field

    Returns
    -------
    int
        row of the field
    """
    for row in range(layout.rowCount()):
        if type(layout.itemAt(row, 1)) == QWidgetItem and layout.itemAt(row, 0).widget().text() == label:
            return row
        elif type(layout.itemAt(row, 1)) == QHBoxLayout:
            for child in range(layout.itemAt(row, 1).count()):
                if type(layout.itemAt(row, 1).itemAt(child)) == QWidgetItem and \
                        layout.itemAt(row, 1).itemAt(child).widget().objectName() == label:
                    return row, child


def open_pupil():
    """Checks if Pupil Capture is open and if not starts it."""
    if "pupil_capture.exe" not in (i.name() for i in psutil.process_iter()):
        os.startfile(PUPIL_PATH)  # subprocess.call([PUPIL_PATH]) ?
