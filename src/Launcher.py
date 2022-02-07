"""
Main entry point for the project.
"""
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QFileDialog, QMessageBox

from src.GUI import StackedWindowGui
from src.QEditGui import QEditGuiMain


class Launcher(QWidget):
    """Simple window displaying the different options to use the software."""

    def __init__(self):
        super(Launcher, self).__init__()
        layout = QHBoxLayout()
        quest_edit = QPushButton("Questionnaire Editor")
        quest_edit.clicked.connect(self.run_questionnaire_editor)
        style_edit = QPushButton("Stylesheet Editor")
        style_edit.setDisabled(True)
        run_quest = QPushButton("Run Questionnaire")
        run_quest.clicked.connect(self.run_questionnaire)
        help_about = QPushButton("Help")
        help_about.clicked.connect(self.show_info)
        layout.addWidget(quest_edit)
        layout.addWidget(style_edit)
        layout.addWidget(run_quest)
        layout.addWidget(help_about)
        self.questionnaire_window = None
        self.setStyleSheet("QPushButton {padding: 7px; margin: 3px; }")
        self.setLayout(layout)
        self.setWindowTitle("QUEST")
        self.show()

    def run_questionnaire(self):
        """Get questionnaire file and run the GUI."""
        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("Text files (*.txt)")
        dlg.setStyle(self.style())

        if dlg.exec_():
            file = dlg.selectedFiles()[0]
            self.questionnaire_window = StackedWindowGui(file)

    def run_questionnaire_editor(self):
        """Run the questionnaire editor GUI."""
        editgui = QEditGuiMain(self)
        editgui.show()

    @staticmethod
    def show_info():
        """Display basic information about the software and a link to the wiki."""
        msg = QMessageBox()
        msg.setWindowTitle("Help / About")
        msg.setIcon(QMessageBox.Information)
        msg.setText("This software was created by Daphne Schössow.")
        msg.setInformativeText("For detailed instructions on how to use this software, "
                               "have a look at the <a href=https://gitlab.uni-hannover.de/da.schoessow/quest/-/wikis/overview>wiki</a> of this project at gitlab. "
                               "For further problems, feature request, or feedback create an issue at gitlab or contact <a href=mailto:daphne.schoessow@ikt.uni-hannover.de> via mail</a>.")
        msg.exec_()


if __name__ == '__main__':
    app = QApplication([])
    ex = Launcher()
    sys.exit(app.exec_())
