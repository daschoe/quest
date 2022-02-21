"""GUI of the visual questionnaire editor"""

import copy
import os
from collections import deque
from os.path import basename

import configobj
from PyQt5 import sip
from PyQt5.QtCore import Qt, QModelIndex, QPoint
from PyQt5.QtGui import QCloseEvent, QKeySequence
from PyQt5.QtWidgets import QApplication, QTreeWidgetItem, QWidget, QHBoxLayout, QGroupBox, QSplitter, QFileDialog, \
    QMainWindow, QAction, QLabel, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QGridLayout, QComboBox, QCheckBox, \
    QRadioButton, QButtonGroup, QMenu, QInputDialog, QMessageBox, QLayout, QScrollArea
from configobj import ConfigObj, ConfigObjError
from fpdf import FPDF

from src.GUI import StackedWindowGui
from src.TextEdit import TextEdit
from src.Tree import Tree
from src.Validator import validate_questionnaire, listify
from src.tools import *


class QEditGuiMain(QMainWindow):
    """ Main Window, adds menu bar and status bar

    Attributes
    ----------
    parent : QObject, optional
        widget/layout this widget is embedded in
    """

    # noinspection PyTypeChecker
    def __init__(self, parent=None):
        """

        Parameters
        ----------
        parent : QObject, optional
            widget/layout this widget is embedded in
        """
        QWidget.__init__(self, parent)
        menu = self.menuBar()
        file = menu.addMenu("File")
        new = QAction("New", self)
        new.setShortcut(QKeySequence("Ctrl+N"))
        file.addAction(new)
        new.triggered.connect(self.new_file)
        load = QAction("Load", self)
        file.addAction(load)
        load.triggered.connect(self.load_file)
        save = QAction("Save", self)
        save.triggered.connect(self.save)
        save.setShortcut(QKeySequence("Ctrl+S"))
        file.addAction(save)
        save_as = QAction("Save as...", self)
        save_as.triggered.connect(self.saveas)
        file.addAction(save_as)
        validate = QAction("Validate Questionnaire", self)
        validate.triggered.connect(
            lambda: validate_questionnaire(listify(self.structure, self.status, self.status_duration)))
        validate.setShortcut(QKeySequence("Ctrl+Q"))
        file.addAction(validate)
        export = QAction("Export GUI to .pdf", self)
        export.triggered.connect(self.export)
        file.addAction(export)
        quit_editor = QAction("Quit", self)
        file.addAction(quit_editor)
        quit_editor.triggered.connect(self.quit_editor)

        editor = menu.addMenu("Editor")
        self.load_preview = QAction("GUI preview on load", self)
        self.load_preview.setCheckable(True)
        editor.addAction(self.load_preview)

        self.gui = EditGui()

        copyaction = QAction("Copy selected page/question", self)
        copyaction.triggered.connect(lambda: self.gui.copy(self.gui.current_item, None))
        copyaction.setShortcut(QKeySequence("Ctrl+C"))
        editor.addAction(copyaction)
        self.pasteaction = QAction("Paste", self)
        self.pasteaction.triggered.connect(self.gui.paste)
        self.pasteaction.setEnabled(False)
        self.pasteaction.setShortcut(QKeySequence("Ctrl+V"))
        editor.addAction(self.pasteaction)
        self.undoaction = QAction("Undo", self)
        self.undoaction.setEnabled(False)
        self.undoaction.setShortcut(QKeySequence("Ctrl+Z"))
        self.undoaction.triggered.connect(self.undo)
        editor.addAction(self.undoaction)
        self.redoaction = QAction("Redo", self)
        self.redoaction.triggered.connect(self.redo)
        self.redoaction.setEnabled(False)
        self.redoaction.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        editor.addAction(self.redoaction)

        self.structure = None
        self.filename = None
        self.initial_structure = None
        self.undo_stack = deque()
        self.redo_stack = deque()
        self.new_file()
        self.status = self.statusBar()
        self.status_duration = 2000
        self.setCentralWidget(self.gui)
        self.setWindowTitle("Questionnaire Editor")
        self.move(0, 0)
        # self.showMaximized()
        self.show()

    @staticmethod
    def unsaved_message():
        """
        Message box showing up whenever unsaved changes might be lost on close/load/new.

        Returns
        -------
        QMessageBox.ButtonRole
            value of the button clicked (True if it is supposed to be saved)
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("The questionnaire file has changed. Do you want to save it?")
        msg.setWindowFlags(Qt.CustomizeWindowHint)  # removes title bar
        msg.addButton("Yes", QMessageBox.AcceptRole)
        msg.addButton("No", QMessageBox.RejectRole)
        retval = msg.exec_()
        return retval

    def closeEvent(self, a0):
        """Check for unsaved changes before quitting. (When the red x is pressed.)

        Parameters
        ----------
        a0 : QCloseEvent
        """
        self.quit_editor()

    def quit_editor(self):
        """Check for unsaved changes before quitting."""
        if self.initial_structure is not None and self.initial_structure != copy.deepcopy(
                dict(listify(self.structure))) and len(self.undo_stack) > 0 \
                and not (
                self.initial_structure == copy.deepcopy(dict(listify(self.structure))) and len(self.undo_stack) == 0):
            if self.unsaved_message() == QMessageBox.AcceptRole:
                self.save()
        self.close()

    def export(self):
        """Export GUI to pdf by taking screenshots of every page and combining them."""
        if self.filename is None:
            self.structure.filename = "./tmp.txt"
            self.structure.encoding = "utf-8"
            self.structure.write()
        self.status.showMessage("Exporting to pdf...", self.status_duration)
        exgui = StackedWindowGui(self.structure.filename, preview=True)
        pdf = FPDF()
        for page in range(exgui.Stack.count()):
            exgui.Stack.setCurrentIndex(page)
            if page + 1 == exgui.Stack.count():  # last page
                exgui.forwardbutton.setText(exgui.send_text)
            p = exgui.grab()
            w = p.width()
            h = p.height()
            p.save("./Page_{}.png".format(page))
            if w > h:
                pdf.add_page(orientation='L')
                pdf.image("./Page_{}.png".format(page), x=0, y=0, w=297)
            else:
                pdf.add_page(orientation='P')
                pdf.image("./Page_{}.png".format(page), x=0, y=0, h=297)
        exgui.close()
        file = QFileDialog().getSaveFileName(self, caption="Save PDF-File", filter="pdf files (*.pdf)")[0]
        if file is not None and file != "":
            pdf.output(file, "F")
            self.status.showMessage("Export finished.", self.status_duration)
        else:
            self.status.showMessage("Export aborted.", self.status_duration)
        for page in range(exgui.Stack.count()):
            os.remove("./Page_{}.png".format(page))
        if self.structure.filename == "./tmp.txt":
            os.remove("./tmp.txt")

    def new_file(self):
        """Create a new file structure."""
        if self.initial_structure is not None and self.initial_structure != copy.deepcopy(
                dict(listify(self.structure))) and len(self.undo_stack) > 0 \
                and not (
                self.initial_structure == copy.deepcopy(dict(listify(self.structure))) and len(self.undo_stack) == 0):
            if self.unsaved_message() == QMessageBox.AcceptRole:
                self.save()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.gui.create_tree()
        self.filename = None
        self.gui.clear_layout(self.gui.edit_layout)
        self.gui.clear_layout(self.gui.prev_widget)
        self.gui.preview_gui = None
        self.structure = ConfigObj()
        for field in general_fields:
            if field in default_values:
                self.structure[field] = default_values[field]
        self.initial_structure = copy.deepcopy(dict(self.structure))

    def load_file(self):
        """Get questionnaire file and run the GUI.

        Raises
        ------
        ConfigObjError
            if an invalid file is selected
        """
        if self.initial_structure is not None and (
                self.initial_structure != copy.deepcopy(dict(listify(self.structure))) and len(self.undo_stack) > 0) \
                and not (
                self.initial_structure == copy.deepcopy(dict(listify(self.structure))) and len(self.undo_stack) == 0):
            if self.unsaved_message() == QMessageBox.AcceptRole:
                self.save()
        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("Text files (*.txt)")
        dlg.setStyle(self.style())
        if dlg.exec_():
            file = dlg.selectedFiles()[0]
            self.filename = file
            try:
                self.status.clearMessage()
                self.structure = ConfigObj(file)
                self.initial_structure = copy.deepcopy(dict(self.structure))
                self.gui.create_tree(self.structure)
                self.undoaction.setEnabled(False)
                self.redoaction.setEnabled(False)
                self.undo_stack.clear()
                self.redo_stack.clear()
            except ConfigObjError:
                self.status.showMessage("Tried to load a file with an invalid structure.", self.status_duration)
            if self.load_preview.isChecked():
                try:
                    self.gui.load_preview(file)
                except ConfigObjError:
                    self.status.showMessage(
                        "Invalid structure for GUI. Please check issues by validating the questionnaire.",
                        self.status_duration)
        dlg.deleteLater()

    def save(self):
        """Save current structure with current name."""
        self.structure = listify(self.structure, self.status, self.status_duration)
        if self.structure.filename is None or self.structure.filename == "./tmp.txt":
            self.saveas()
        else:
            self.structure.filename = self.filename
            self.structure.encoding = "utf-8"
            self.structure.write()
            self.initial_structure = copy.deepcopy(dict(self.structure))
            self.status.clearMessage()
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.status.showMessage("Saved structure.", self.status_duration)

    def saveas(self):
        """Save current structure as .txt file."""
        self.structure = listify(self.structure, self.status, self.status_duration)
        file = QFileDialog().getSaveFileName(self, caption="Save File", filter="Text files (*.txt)")[0]
        if file != "":
            self.filename = file
            self.structure.filename = file
            self.structure.encoding = "utf-8"
            self.structure.write()
            self.initial_structure = copy.deepcopy(dict(self.structure))
            self.status.clearMessage()
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.status.showMessage("Saved structure as {}".format(file), self.status_duration)
            self.gui.treeview.topLevelItem(0).setText(0, os.path.basename(file))
        else:
            self.status.clearMessage()
            self.status.showMessage("Save aborted.", self.status_duration)

    def undo(self):
        """Reset structure to the state before the last action."""
        self.redo_stack.append(copy.deepcopy(dict(self.structure)))
        self.redoaction.setEnabled(True)
        self.structure = ConfigObj(self.undo_stack.pop())
        self.gui.create_tree(self.structure)
        if self.load_preview.isChecked() or self.gui.automatic_refresh.isChecked():
            self.gui.load_preview()

        if len(self.undo_stack) == 0:
            self.undoaction.setEnabled(False)
        self.gui.treeview.expandAll()

    def redo(self):
        """Take back an undo-action."""
        self.undo_stack.append(copy.deepcopy(dict(self.structure)))
        self.undoaction.setEnabled(True)
        self.structure = ConfigObj(self.redo_stack.pop())
        self.gui.create_tree(self.structure)
        if self.load_preview.isChecked() or self.gui.automatic_refresh.isChecked():
            self.gui.load_preview()

        if len(self.redo_stack) == 0:
            self.redoaction.setEnabled(False)
        self.gui.treeview.expandAll()


class EditGui(QWidget):
    """Core of the window, actual GUI.
        The window is split into three components: a tree-view of the questionnaire structure,
        details for the selected object, and a preview of the questionnaire GUI.
    """

    def __init__(self):
        super(EditGui, self).__init__()
        layout = QHBoxLayout()
        structure_view = QGroupBox("Structure")
        struct_layout = QVBoxLayout()
        splitter = QSplitter()
        edit = QGroupBox("Edit")
        self.edit_layout = QFormLayout(edit)
        self.treeview = Tree(self)
        self.treeview.clicked.connect(self.show_details)
        self.treeview.itemSelectionChanged.connect(self.change_active_buttons)
        self.treeview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeview.customContextMenuRequested.connect(self.open_tree_menu)
        self.treeview.tree_changed.connect(self.update_structure)
        self.treeview.error_message.connect(self.set_status_message)
        self.create_tree()
        self.current_item = None
        self.copied = [None, None]
        struct_layout.addWidget(self.treeview)
        structure_view.setLayout(struct_layout)
        # reusable fields
        self.questiontype = QComboBox()
        self.questiontype.addItems(types)
        self.questiontype.setToolTip(tooltips["type"])
        self.questiontype.hide()
        self.questiontype.activated.connect(self.update_val)
        self.qss_filechooser = QPushButton("Choose file...")
        self.qss_filechooser.hide()
        self.qss_filechooser.setToolTip(tooltips["stylesheet"])
        self.qss_filechooser.clicked.connect(self.choose_qss)
        self.qss_filename = QLabel("")
        self.qss_filename.hide()
        self.policy_layout = QHBoxLayout()
        self.pw_layout = QHBoxLayout()
        self.pw_file = QLabel("")
        self.pw_file.setObjectName("password_file")
        self.rand_filechooser = QPushButton("Choose file...")
        self.rand_filechooser.hide()
        self.rand_filechooser.setToolTip(tooltips["randomization_file"])
        self.rand_filechooser.clicked.connect(self.choose_randfile)
        self.rand_file = QLabel("")
        self.rand_file.setObjectName("randomization_file")
        preview = QGroupBox("Preview")
        self.preview_gui = None
        self.prev_layout = QVBoxLayout(preview)

        button_layout = QGridLayout()
        self.page_add = QPushButton("Add Page")
        self.page_add.clicked.connect(self.add_page)
        self.page_add.setShortcut(QKeySequence("Ctrl+A"))
        self.page_remove = QPushButton("Remove Page")
        self.page_remove.clicked.connect(lambda: self.remove_page(self.treeview.currentItem()))
        self.page_remove.setShortcut(QKeySequence("Ctrl+X"))
        self.page_rename = QPushButton("Rename Page")
        self.page_rename.clicked.connect(lambda: self.rename_page(self.treeview.currentItem()))
        self.question_add = QPushButton("Add Question")
        self.question_add.setShortcut(QKeySequence("Ctrl+A"))
        self.question_add.clicked.connect(lambda: self.add_question(self.treeview.currentItem()))
        self.question_remove = QPushButton("Remove Question")
        self.question_remove.setShortcut(QKeySequence("Ctrl+X"))
        self.question_remove.clicked.connect(lambda: self.remove_question(self.treeview.currentItem()))
        self.question_rename = QPushButton("Rename Question")
        self.question_rename.clicked.connect(lambda: self.rename_question(self.treeview.currentItem()))
        self.button_copy = QPushButton("Copy")
        self.button_copy.clicked.connect(lambda: self.copy(self.current_item, None))
        self.button_paste = QPushButton("Paste")
        self.button_paste.clicked.connect(self.paste)
        self.buttons = [self.page_add, self.page_remove, self.page_rename, self.question_add, self.question_remove,
                        self.question_rename, self.button_copy, self.button_paste]
        for button in self.buttons:
            if button != self.page_add:
                button.setEnabled(False)
        button_layout.addWidget(self.page_add, 0, 0)
        button_layout.addWidget(self.page_remove, 0, 1)
        button_layout.addWidget(self.page_rename, 0, 2)
        button_layout.addWidget(self.question_add, 1, 0)
        button_layout.addWidget(self.question_remove, 1, 1)
        button_layout.addWidget(self.question_rename, 1, 2)
        button_layout.addWidget(self.button_copy, 2, 0)
        button_layout.addWidget(self.button_paste, 2, 1)
        struct_layout.addLayout(button_layout)

        p_widget = QWidget()
        self.prev_widget = QHBoxLayout()
        self.prev_widget.addWidget(p_widget)
        self.prev_layout.addLayout(self.prev_widget)
        self.prev_refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh Preview")
        self.refresh_button.clicked.connect(self.load_preview)
        self.prev_refresh_layout.addWidget(self.refresh_button, alignment=Qt.AlignRight | Qt.AlignBottom)
        self.automatic_refresh = QCheckBox("automatic refresh")
        self.prev_refresh_layout.addWidget(self.automatic_refresh)
        self.prev_layout.addLayout(self.prev_refresh_layout)

        scroll = QScrollArea()
        scroll.setWidget(edit)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea{border: 1px solid transparent;}")
        splitter.addWidget(structure_view)
        splitter.addWidget(scroll)
        splitter.addWidget(preview)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def choose_qss(self):
        """Choose an existing qss/css file as stylesheet."""
        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("QSS/CSS files (*.qss *.css)")
        dlg.setStyle(self.style())
        if dlg.exec_():
            self.qss_filename.setText(dlg.selectedFiles()[0])
            if self.parent().structure["stylesheet"] != self.qss_filename.text():
                self.parent().undo_stack.append(copy.deepcopy(dict(self.parent().structure)))
                self.parent().undoaction.setEnabled(True)
                self.parent().redo_stack.clear()
                self.parent().redoaction.setEnabled(False)
                self.parent().structure["stylesheet"] = self.qss_filename.text()
            if self.automatic_refresh.isChecked():
                self.load_preview()

    def choose_pwfile(self):
        """Choose an existing txt file as password file."""
        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("Password files (*.txt)")
        dlg.setStyle(self.style())
        if dlg.exec_():
            self.pw_file.setText(dlg.selectedFiles()[0])
            page = self.treeview.selectedItems()[0].parent().text(0)
            question = self.treeview.selectedItems()[0].text(0)
            if self.parent().structure[page][question]["password_file"] != self.pw_file.text():
                self.parent().undo_stack.append(copy.deepcopy(dict(self.parent().structure)))
                self.parent().undoaction.setEnabled(True)
                self.parent().redo_stack.clear()
                self.parent().redoaction.setEnabled(False)
                self.parent().structure[page][question]["password_file"] = self.pw_file.text()

    def choose_randfile(self):
        """Choose an existing txt file as randomization order file."""
        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("Randomization files (*.txt *.csv)")
        dlg.setStyle(self.style())
        if dlg.exec_():
            self.rand_file.setText(dlg.selectedFiles()[0])
            if self.parent().structure["randomization_file"] != self.rand_file.text():
                self.parent().undo_stack.append(copy.deepcopy(dict(self.parent().structure)))
                self.parent().undoaction.setEnabled(True)
                self.parent().redo_stack.clear()
                self.parent().redoaction.setEnabled(False)
                self.parent().structure["randomization_file"] = self.rand_file.text()

    def load_preview(self, file=None):
        """(Re-)Load the GUI preview

        Parameters
        ----------
        file : str, optional, default=None
            name/path of the config file, use None for previewing an unsaved structure.
        """
        error_found, _, _ = validate_questionnaire(
            listify(self.parent().structure, self.parent().status, self.parent().status_duration), suppress=True)
        if not error_found:
            self.clear_layout(self.prev_widget)
            if file is None or not file:
                if not file and (self.parent().structure.filename is None or file == "./tmp.txt" or
                                 self.parent().structure.filename == "./tmp.txt"):
                    self.parent().structure.filename = "./tmp.txt"
                    self.parent().structure.encoding = "utf-8"
                    self.parent().structure.write()
                    file = "./tmp.txt"
                else:
                    file = self.parent().structure.filename
            self.preview_gui = StackedWindowGui(file, popup=False, preview=True)
            if self.preview_gui.layout() is not None:
                if "stylesheet" in self.parent().structure.keys():
                    with open(self.parent().structure["stylesheet"], 'r') as css_file:
                        css_data = css_file.read().replace('\n', '')
                else:
                    with open("stylesheets/minimal.qss", 'r') as css_file:
                        css_data = css_file.read().replace('\n', '')
                p_widget = QWidget()
                p_widget.setLayout(self.preview_gui.layout())
                p_widget.setStyleSheet(css_data)
                self.prev_widget.addWidget(p_widget)

                if self.current_item is not None and self.current_item.parent() is None:
                    pass
                elif self.current_item is not None and self.current_item.parent().parent() is None:
                    self.preview_gui.Stack.setCurrentIndex(
                        self.parent().structure.sections.index(self.current_item.text(0)))
                elif self.current_item is not None and self.current_item.parent().parent().parent() is None:
                    self.preview_gui.Stack.setCurrentIndex(
                        self.parent().structure.sections.index(self.current_item.parent().text(0)))

            if file == "./tmp.txt":
                os.remove(file)

    def set_status_message(self, message):
        """Forward a message from the internal structure to the status bar of the GUI.

        Parameters
        ----------
        message : str
            The message to be displayed.
        """
        self.parent().status.showMessage(message, self.parent().status_duration)

    def change_active_buttons(self):
        """Switch the enabled buttons for changing the structure according to what structural part is currently selected."""
        if (len(self.treeview.selectedItems()) == 0) or (self.treeview.selectedItems()[0].parent() is None):  # root
            for button in self.buttons:
                if button == self.page_add or (button == self.button_paste and self.copied[1] == "page"):
                    button.setEnabled(True)
                else:
                    button.setEnabled(False)
        elif (self.treeview.selectedItems()[0].parent() is not None) and (
                self.treeview.selectedItems()[0].parent().parent() is None):  # page
            for button in self.buttons:
                if (button == self.page_remove) or (button == self.page_rename) or (button == self.question_add) or (
                        button == self.button_copy) or (button == self.button_paste and self.copied[1] is not None):
                    button.setEnabled(True)
                else:
                    button.setEnabled(False)
        else:
            for button in self.buttons:
                if (button == self.question_remove) or (button == self.question_rename) or (
                        button == self.button_copy) or (button == self.button_paste and self.copied[1] == "question"):
                    button.setEnabled(True)
                else:
                    button.setEnabled(False)

    def create_tree(self, structure=None):
        """Create the tree structure from the config file.

        Parameters
        ----------
        structure : ConfigObj, None
            the current structure of the questionnaire
        """
        self.treeview.takeTopLevelItem(0)  # clears the tree
        self.clear_layout(self.edit_layout)
        if structure is not None:
            root = QTreeWidgetItem(self.treeview, [basename(structure.filename) if structure.filename is not None else "<new questionnaire>"])
            for sec in structure.sections:
                page = QTreeWidgetItem(root, [sec])
                for q in structure[sec].sections:
                    quest = QTreeWidgetItem(page, [q])
                    quest.setFlags(quest.flags() & ~Qt.ItemIsDropEnabled)
            self.treeview.addTopLevelItem(root)
        else:
            root = QTreeWidgetItem(self.treeview, ["<new questionnaire>"])
            self.treeview.addTopLevelItem(root)
        self.current_item = None

    def show_details(self, val, reload=False):
        """Display all key/value pairs for the selected questionnaire/page/question.

        Parameters
        ----------
        val : QModelIndex
            The selected item.
        reload : bool, default=False
            Set to True if the details of this item need to be reloaded, e.g. on creation of a new item or a change in question type.
        """
        if reload or self.current_item is None or (
                self.current_item is not None and (self.current_item.text(0) != val.data()) or (
                val.parent().data() is not None and self.current_item.parent().text(0) != val.parent().data())):
            self.clear_layout(self.edit_layout)
            if val.parent().data() is None:  # root
                if self.parent().structure:
                    for field in general_fields:
                        if field not in self.parent().structure.keys() and field in default_values:
                            self.parent().structure[field] = default_values[field]
                        if field == "go_back":
                            val_field = QCheckBox("")
                            val_field.toggled.connect(self.update_val)
                            val_field.setChecked(True if ((self.parent().structure[field] == "True") or (
                                    type(self.parent().structure["go_back"]) is bool and self.parent().structure["go_back"])) else False)
                        elif field == "save_message":
                            val_field = TextEdit(self.parent().structure[field] if field in self.parent().structure.keys() else "")
                            val_field.editingFinished.connect(self.edit_done)
                        elif field == "save_after":
                            val_field = QComboBox()
                            val_field.setObjectName("save_after")
                            current_pages = self.parent().structure.sections
                            val_field.activated.connect(self.update_val)
                            if current_pages:
                                val_field.addItems(current_pages)
                                selected = current_pages.index(self.parent().structure[field]) if (field in self.parent().structure.keys() and self.parent().structure[field] in current_pages) else -1
                                val_field.setCurrentIndex(selected if selected > -1 else len(current_pages)-1)
                                self.parent().structure[field] = val_field.currentText()
                        elif field == "stylesheet":
                            val_field = QHBoxLayout()
                            if field in self.parent().structure.keys():
                                self.qss_filename.setText(self.parent().structure[field])
                            val_field.addWidget(self.qss_filechooser)
                            val_field.addWidget(self.qss_filename)
                            self.qss_filechooser.show()
                            self.qss_filename.show()
                        elif field == "randomization":
                            val_field = QComboBox()
                            val_field.addItems(randomize_options)
                            val_field.setCurrentIndex(randomize_options.index(self.parent().structure[field]))
                            val_field.activated.connect(self.update_val)
                            if val_field.currentText() == "from file":
                                self.rand_filechooser.setEnabled(True)
                            else:
                                self.rand_filechooser.setEnabled(False)
                        elif field == "randomization_file":
                            val_field = QHBoxLayout()
                            if field in self.parent().structure.keys():
                                self.rand_file.setText(self.parent().structure[field])
                            val_field.addWidget(self.rand_filechooser)
                            val_field.addWidget(self.rand_file)
                            self.rand_filechooser.show()
                            self.rand_file.show()
                            if self.parent().structure["randomization"] == "from file":
                                self.rand_filechooser.setEnabled(True)
                            else:
                                self.rand_filechooser.setEnabled(False)
                        else:
                            val_field = QLineEdit("")
                            if field in self.parent().structure.keys():
                                val_field.setText(str(self.parent().structure[field]))
                            val_field.editingFinished.connect(self.edit_done)
                            if field == "back_text" and (("go_back" in self.parent().structure.keys()) and
                                                         ((self.parent().structure["go_back"] == "False") or (
                                    type(self.parent().structure["go_back"]) is bool and not self.parent().structure["go_back"]))):
                                val_field.setDisabled(True)
                        self.edit_layout.addRow(QLabel(field), val_field)
                        if type(val_field) != QHBoxLayout:
                            val_field.setToolTip(tooltips[field])
            elif (val.parent().data() is not None) and (val.parent().parent().data() is None):  # page
                if self.parent().structure[val.data()]:
                    for k in page_fields:
                        val_field = None
                        if k == "title" or k == "randomgroup" or k == "pupil_on_next":
                            val_field = QLineEdit(self.parent().structure[val.data()][k] if k in self.parent().structure[val.data()] else "")
                            val_field.editingFinished.connect(self.edit_done)
                        elif k == "description":
                            val_field = TextEdit(self.parent().structure[val.data()][k] if k in self.parent().structure[val.data()] else "")
                            val_field.editingFinished.connect(self.edit_done)
                        if val_field is not None:
                            self.edit_layout.addRow(QLabel(k), val_field)
                            val_field.setToolTip(tooltips[k])
                if self.preview_gui is not None and self.preview_gui.layout() is not None:
                    self.preview_gui.Stack.setCurrentIndex(self.parent().structure.sections.index(val.data()))
            else:  # question
                question_data = self.parent().structure[val.parent().data()][val.data()]
                for k in question_data.keys():
                    if k == "type":
                        self.edit_layout.addRow(QLabel("type"), self.questiontype)
                        self.questiontype.setCurrentIndex(types.index(question_data[k]))
                        self.questiontype.show()
                        for field in fields_per_type[question_data[k]][0]:
                            if "type" != field:
                                val_field = QLabel()
                                if fields_per_type[question_data[k]][0][field] == "QLineEdit":
                                    if field not in question_data.keys():
                                        val_field = QLineEdit("")
                                    else:
                                        val_field = QLineEdit(str(question_data[field]))
                                    val_field.editingFinished.connect(self.edit_done)
                                elif fields_per_type[question_data[k]][0][field] == "QPushButton":
                                    if field == "password_file":
                                        val_field = QPushButton("Choose file...")
                                        val_field.setObjectName("password_file_btn")
                                        val_field.clicked.connect(self.choose_pwfile)
                                        self.pw_file.show()
                                        self.pw_file.setText("" if field not in question_data.keys() else question_data[field])
                                        self.pw_layout.addWidget(val_field)
                                        self.pw_layout.addWidget(self.pw_file)
                                elif fields_per_type[question_data[k]][0][field] == "QPlainTextEdit":
                                    if field not in question_data.keys():
                                        val_field = TextEdit("")
                                    else:
                                        val_field = TextEdit(str(question_data[field]))
                                    val_field.editingFinished.connect(self.edit_done)
                                    if (field == "label") and ((question_data["labelled"] == "False") or (
                                            type(question_data["labelled"]) is bool and not question_data["labelled"])):
                                        val_field.setDisabled(True)
                                elif fields_per_type[question_data[k]][0][field] == "QComboBox":
                                    val_field = QComboBox()
                                    val_field.activated.connect(self.update_val)
                                    if field == "function":
                                        val_field.addItems(function_possibilites)
                                        val_field.setCurrentIndex(function_possibilites.index(question_data[field]))
                                        self.clear_layout(self.policy_layout)
                                        if question_data[field] == "Annotate":
                                            self.policy_layout.addWidget(QLabel("annotation"))
                                            ann_field = QLineEdit(str(question_data["annotation"]) if "annotation" in question_data.keys() else "")
                                            ann_field.setObjectName("anno")
                                            self.policy_layout.addWidget(ann_field)
                                            ann_field.editingFinished.connect(self.edit_done)
                                        elif question_data[field] == "Recording":
                                            self.policy_layout.addWidget(QLabel("recording_name"))
                                            ann_field = QLineEdit(str(question_data["recording_name"]) if "recording_name" in question_data.keys() else "")
                                            ann_field.setObjectName("rec")
                                            self.policy_layout.addWidget(ann_field)
                                            ann_field.editingFinished.connect(self.edit_done)
                                        else:
                                            self.clear_layout(self.policy_layout)
                                            self.edit_layout.removeRow(self.policy_layout)
                                    if field == "policy":
                                        val_field.addItems(policy_possibilities)
                                        val_field.setObjectName("policy")
                                        if (("policy" not in question_data.keys()) or (
                                                question_data["policy"] == "None") or (question_data["policy"] == "[None]") or (question_data["policy"] == ["None"])) \
                                                and (question_data["type"] == "Text"):
                                            val_field.setCurrentIndex(0)  # "None"
                                            if question_data.as_int("size") > 1:
                                                val_field.setDisabled(True)  # Multi-line doesn't support policies
                                            self.clear_layout(self.policy_layout)
                                            self.edit_layout.removeRow(self.policy_layout)
                                        else:
                                            val_field.setCurrentIndex(policy_possibilities.index(question_data[field][0]))
                                            self.clear_layout(self.policy_layout)
                                            if (question_data[field][0] == "int") or (question_data[field][0] == "double"):
                                                self.policy_layout.addWidget(QLabel("min:"))
                                                min_field = QLineEdit(question_data[field][1])
                                                min_field.setObjectName("min")
                                                self.policy_layout.addWidget(min_field)
                                                min_field.editingFinished.connect(self.edit_done)
                                                self.policy_layout.addWidget(QLabel("max:"))
                                                max_field = QLineEdit(question_data[field][2])
                                                max_field.setObjectName("max")
                                                self.policy_layout.addWidget(max_field)
                                                max_field.editingFinished.connect(self.edit_done)
                                            if question_data[field][0] == "double":
                                                dec_field = QLineEdit(question_data[field][3])
                                                dec_field.setObjectName("dec")
                                                self.policy_layout.addWidget(dec_field)
                                                dec_field.editingFinished.connect(self.edit_done)
                                            elif question_data[field][0] == "regex":
                                                self.policy_layout.addWidget(QLabel("expression:"))
                                                exp_field = QLineEdit(question_data[field][1])
                                                exp_field.setObjectName("exp")
                                                self.policy_layout.addWidget(exp_field)
                                                exp_field.editingFinished.connect(self.edit_done)
                                elif fields_per_type[question_data[k]][0][field] == "QCheckBox":
                                    if field == "buttons":
                                        val_field = QHBoxLayout()
                                        bg = QButtonGroup(val_field)
                                        bg.setExclusive(False)
                                        for a in player_buttons:
                                            cb = QCheckBox(a)
                                            if field in question_data:
                                                cb.setChecked(True if a in question_data[field] else False)
                                            else:
                                                cb.setChecked(True if a in default_values[field] else False)
                                            val_field.addWidget(cb)
                                            bg.addButton(cb, player_buttons.index(a))
                                            bg.buttonClicked.connect(self.update_val)
                                    else:
                                        val_field = QCheckBox()
                                        val_field.toggled.connect(self.update_val)
                                        if field in question_data:
                                            val_field.setChecked(question_data.as_bool(field))
                                        else:
                                            val_field.setChecked(False)
                                elif fields_per_type[question_data[k]][0][field] == "QRadioButton":
                                    val_field = QHBoxLayout()
                                    bg = QButtonGroup(val_field)
                                    if field == "size":
                                        cnt = 0
                                        for a in ["single-line", "multi-line"]:
                                            rb = QRadioButton(a)
                                            val_field.addWidget(rb)
                                            if (a == "single-line" and (
                                                    (question_data[field] == "1") or (question_data[field] == 1))) or \
                                                    (a == "multi-line" and int(question_data[field]) > 1):
                                                rb.setChecked(True)
                                            bg.addButton(rb, cnt)
                                            bg.buttonClicked.connect(self.update_val)
                                            cnt += 1
                                if type(val_field) != QHBoxLayout:
                                    val_field.setToolTip(tooltips[field])
                                if field == "policy" or field == "annotation" or field == "recording_name" or field == "function":
                                    self.edit_layout.addRow(QLabel(field), val_field)
                                    self.edit_layout.addRow(self.policy_layout)
                                elif field == "password_file":
                                    self.edit_layout.addRow("password_file", self.pw_layout)
                                else:
                                    self.edit_layout.addRow(QLabel(field), val_field)
                if self.preview_gui is not None:
                    self.preview_gui.Stack.setCurrentIndex(self.parent().structure.sections.index(val.parent().data()))
            self.current_item = self.treeview.currentItem()

    def update_val(self, new_val):
        """Change the value of the current/edited field to new_val"""
        if self.sender().parent() is not None:
            if (len(self.parent().undo_stack) > 0 and self.parent().undo_stack[-1] != copy.deepcopy(
                    dict(self.parent().structure))) or len(self.parent().undo_stack) == 0:
                self.parent().undo_stack.append(copy.deepcopy(dict(self.parent().structure)))
                self.parent().undoaction.setEnabled(True)
                self.parent().redo_stack.clear()
                self.parent().redoaction.setEnabled(False)
            if type(self.sender()) is QButtonGroup:
                lbl = self.sender().parent().parent().layout().labelForField(self.sender().parent().layout()).text()
                new_val = self.sender().checkedId()
                if lbl == "size":
                    if self.sender().checkedId():  # multiline
                        pos = \
                            self.sender().parent().parent().layout().getLayoutPosition(self.sender().parent().layout())[0] + 1
                        self.sender().parent().parent().layout().itemAt(pos, 1).widget().setEnabled(False)
                        self.sender().parent().parent().layout().itemAt(pos, 1).widget().setCurrentIndex(0)
                        self.clear_layout(self.policy_layout)
                    else:
                        pos = \
                            self.sender().parent().parent().layout().getLayoutPosition(self.sender().parent().layout())[0] + 1
                        self.sender().parent().parent().layout().itemAt(pos, 1).widget().setEnabled(True)
                        self.parent().structure[self.treeview.currentItem().parent().text(0)][self.treeview.currentItem().text(0)]["policy"] = \
                            self.sender().parent().parent().layout().itemAt(pos, 1).widget().currentText()
                    self.parent().structure[self.treeview.currentItem().parent().text(0)][self.treeview.currentItem().text(0)]["policy"] = ["None"]
                    new_val += 1
                elif lbl == "buttons":
                    new_val = []
                    for btn in self.sender().buttons():
                        if btn.isChecked():
                            new_val.append(player_buttons[self.sender().buttons().index(btn)])
            else:
                lbl = self.sender().parent().layout().labelForField(self.sender()).text()
            if type(self.sender()) is QCheckBox:
                if (lbl == "go_back") or (lbl == "labelled"):
                    if new_val:
                        pos = self.sender().parent().layout().getWidgetPosition(self.sender())[0] + 1
                        self.sender().parent().layout().itemAt(pos, 1).widget().setEnabled(True)
                    else:
                        pos = self.sender().parent().layout().getWidgetPosition(self.sender())[0] + 1
                        self.sender().parent().layout().itemAt(pos, 1).widget().setEnabled(False)
            elif type(self.sender()) is QComboBox:
                if lbl == "policy":
                    new_val = [self.sender().currentText()]
                    self.clear_layout(self.policy_layout)
                    if (self.sender().currentText() == "int") or (self.sender().currentText() == "double"):
                        self.policy_layout.addWidget(QLabel("min:"))
                        min_field = QLineEdit("")
                        min_field.setObjectName("min")
                        self.policy_layout.addWidget(min_field)
                        min_field.editingFinished.connect(self.edit_done)
                        self.policy_layout.addWidget(QLabel("max:"))
                        max_field = QLineEdit("")
                        max_field.setObjectName("max")
                        self.policy_layout.addWidget(max_field)
                        max_field.editingFinished.connect(self.edit_done)
                        new_val.append("")
                        new_val.append("")
                    if self.sender().currentText() == "double":
                        self.policy_layout.addWidget(QLabel("decimals:"))
                        dec_field = QLineEdit("")
                        dec_field.setObjectName("dec")
                        self.policy_layout.addWidget(dec_field)
                        dec_field.editingFinished.connect(self.edit_done)
                        new_val.append("")
                    elif self.sender().currentText() == "regex":
                        self.policy_layout.addWidget(QLabel("expression:"))
                        exp_field = QLineEdit("")
                        exp_field.setObjectName("exp")
                        self.policy_layout.addWidget(exp_field)
                        exp_field.editingFinished.connect(self.edit_done)
                        new_val.append("")
                elif lbl == "function":
                    new_val = self.sender().currentText()
                    self.clear_layout(self.policy_layout)
                    if self.sender().currentText() == "Annotate":
                        self.policy_layout.addWidget(QLabel("annotation:"))
                        ann_field = QLineEdit("")
                        ann_field.setObjectName("anno")
                        self.policy_layout.addWidget(ann_field)
                        ann_field.editingFinished.connect(self.edit_done)
                    elif self.sender().currentText() == "Recording":
                        self.policy_layout.addWidget(QLabel("recording_name:"))
                        ann_field = QLineEdit("")
                        ann_field.setObjectName("rec")
                        self.policy_layout.addWidget(ann_field)
                        ann_field.editingFinished.connect(self.edit_done)
                elif lbl == "randomization":
                    new_val = self.sender().currentText()
                    if new_val == "from file":
                        self.rand_filechooser.setEnabled(True)
                    else:
                        self.rand_filechooser.setEnabled(False)
                elif lbl == "save_after":
                    new_val = self.sender().currentText()
                else:
                    lbl = lbl.lower()
                    new_val = self.sender().currentText()
                    # add all needed fields for the new type, keep values of fields if already present
                    for field in fields_per_type[new_val][0].keys():
                        if field in default_values.keys() and \
                                field not in self.parent().structure[self.treeview.currentItem().parent().text(0)][self.treeview.currentItem().text(0)]:
                            self.parent().structure[self.treeview.currentItem().parent().text(0)][self.treeview.currentItem().text(0)][field] = default_values[field]
                    # remove no longer valid fields
                    for field in self.parent().structure[self.treeview.currentItem().parent().text(0)][self.treeview.currentItem().text(0)].keys():
                        if field not in fields_per_type[new_val][0].keys():
                            self.parent().structure[self.treeview.currentItem().parent().text(0)][self.treeview.currentItem().text(0)].pop(field)

            # update the value just changed
            if (self.treeview.currentItem().text(0).find(".txt") > -1) or \
                    (self.treeview.currentItem().text(0) == '<new questionnaire>'):  # general
                self.parent().structure[lbl] = new_val
            elif (self.treeview.currentItem().parent().text(0).find(".txt") > -1) or \
                    (self.treeview.currentItem().parent().text(0) == '<new questionnaire>'):  # page
                self.parent().structure[self.treeview.currentItem().text(0)][lbl] = new_val
            else:  # question
                self.parent().structure[self.treeview.currentItem().parent().text(0)][
                    self.treeview.currentItem().text(0)][lbl] = new_val
            # print(self.treeview.currentItem().text(0), lbl, ":", new_val)
            if lbl == "type":  # Reload
                self.show_details(self.treeview.indexFromItem(self.treeview.currentItem()), True)
            if self.automatic_refresh.isChecked():
                self.load_preview()
            if str(self.parent().undo_stack[-1]) == str(copy.deepcopy(dict(self.parent().structure))):
                self.parent().undo_stack.pop()  # remove accidental doubles (happen at ButtonGroups answers)

    def edit_done(self):
        """Is called when an edited LineEdit loses focus. Handy as it doesn't trigger at each changed character."""
        self.parent().undo_stack.append(copy.deepcopy(dict(self.parent().structure)))
        self.parent().undoaction.setEnabled(True)
        self.parent().redo_stack.clear()
        self.parent().redoaction.setEnabled(False)
        if self.sender().objectName() == "":
            lbl = self.sender().parent().layout().labelForField(self.sender()).text()
            new_val = self.sender().text()
            if (self.treeview.currentItem().text(0).find(".txt") > -1) or \
                    (self.treeview.currentItem().text(0) == '<new questionnaire>'):  # general
                self.parent().structure[lbl] = new_val
            elif (self.treeview.currentItem().parent().text(0).find(".txt") > -1) or \
                    (self.treeview.currentItem().parent().text(0) == '<new questionnaire>'):  # page
                self.parent().structure[self.treeview.currentItem().text(0)][lbl] = new_val
            else:  # question
                self.parent().structure[self.treeview.currentItem().parent().text(0)][self.treeview.currentItem().text(0)][lbl] = new_val
        else:
            if self.sender().objectName() in ["min", "max", "dec", "exp"]:
                lbl = "policy"
                new_val = self.parent().structure[self.treeview.currentItem().parent().text(0)][self.treeview.currentItem().text(0)][lbl]
                if self.sender().objectName() == "min":
                    new_val[1] = self.sender().text() if len(new_val) > 1 else new_val.append(self.sender().text())
                elif self.sender().objectName() == "max":
                    new_val[2] = self.sender().text() if len(new_val) > 2 else new_val.append(self.sender().text())
                elif self.sender().objectName() == "dec":
                    new_val[3] = self.sender().text() if len(new_val) > 3 else new_val.append(self.sender().text())
                elif self.sender().objectName() == "exp":
                    new_val[1] = self.sender().text() if len(new_val) > 1 else new_val.append(self.sender().text())
            elif self.sender().objectName() == "anno":
                new_val = self.sender().text()
                self.parent().structure[self.treeview.currentItem().parent().text(0)][
                    self.treeview.currentItem().text(0)]["annotation"] = new_val
            elif self.sender().objectName() == "rec":
                new_val = self.sender().text()
                self.parent().structure[self.treeview.currentItem().parent().text(0)][
                    self.treeview.currentItem().text(0)]["recording_name"] = new_val
        if self.automatic_refresh.isChecked():
            self.load_preview()

    def clear_layout(self, layout):
        """Remove everythong from the layout, so that contents can be changed.

        Parameters
        ----------
        layout : QLayout
            the layout to be cleared
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() and (not child.widget() == self.questiontype) and \
                    (not child.widget() == self.qss_filechooser) and (not child.widget() == self.qss_filename)\
                    and (not child.widget() == self.pw_file) and \
                    (not child.widget() == self.rand_file) and (not child.widget() == self.rand_filechooser):
                child.widget().deleteLater()
            elif child.widget() == self.questiontype:
                self.questiontype.hide()
            elif child.widget() == self.qss_filechooser:
                self.qss_filechooser.hide()
            elif child.widget() == self.qss_filename:
                self.qss_filename.hide()
            elif child.widget() == self.pw_file:
                self.pw_file.hide()
            elif child.widget() == self.rand_file:
                self.rand_file.hide()
            elif child.widget() == self.rand_filechooser:
                self.rand_filechooser.hide()
            elif child.layout() is not None:
                self.clear_layout(child.layout())

    def open_tree_menu(self, position):
        """Create appropirate context menu in treeview after right-clicking it.

        Parameters
        ----------
        position : QPoint
            coordinated where the mouse-click happened.
        """
        indexes = self.treeview.selectedIndexes()
        level = None
        menu = None
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1
            menu = QMenu()
        if self.treeview.itemAt(position) is not None:
            if level == 0:
                add_page = QAction("Add page", self)
                add_page.triggered.connect(self.add_page)
                add_page.setShortcut(QKeySequence("Ctrl+A"))
                menu.addAction(add_page)
                paste_page = QAction("Paste page")
                paste_page.setShortcut(QKeySequence("Ctrl+V"))
                if self.copied[1] != "page":
                    paste_page.setEnabled(False)
                paste_page.triggered.connect(lambda: self.paste(self.treeview.itemAt(position)))
                menu.addAction(paste_page)
            elif level == 1:
                add_question = QAction("Add question", self)
                add_question.triggered.connect(lambda: self.add_question(self.treeview.itemAt(position)))
                add_question.setShortcut(QKeySequence("Ctrl+A"))
                menu.addAction(add_question)
                rem_page = QAction("Remove page")
                rem_page.triggered.connect(lambda: self.remove_page(self.treeview.itemAt(position)))
                rem_page.setShortcut(QKeySequence("Ctrl+X"))
                menu.addAction(rem_page)
                rename_page = QAction("Rename page")
                rename_page.triggered.connect(lambda: self.rename_page(self.treeview.itemAt(position)))
                menu.addAction(rename_page)
                cpy_page = QAction("Copy page with questions")
                cpy_page.setShortcut(QKeySequence("Ctrl+C"))
                cpy_page.triggered.connect(lambda: self.copy(self.treeview.itemAt(position), "page"))
                menu.addAction(cpy_page)
                paste_page = QAction("Paste")
                paste_page.setShortcut(QKeySequence("Ctrl+V"))
                if self.copied[1] is None:
                    paste_page.setEnabled(False)
                paste_page.triggered.connect(lambda: self.paste(self.treeview.itemAt(position)))
                menu.addAction(paste_page)
            elif level == 2:
                rem_question = QAction("Remove question")
                rem_question.triggered.connect(lambda: self.remove_question(self.treeview.itemAt(position)))
                rem_question.setShortcut(QKeySequence("Ctrl+X"))
                menu.addAction(rem_question)
                rename_question = QAction("Rename question")
                rename_question.triggered.connect(lambda: self.rename_question(self.treeview.itemAt(position)))
                menu.addAction(rename_question)
                cpy_quest = QAction("Copy question")
                cpy_quest.triggered.connect(lambda: self.copy(self.treeview.itemAt(position), "question"))
                cpy_quest.setShortcut(QKeySequence("Ctrl+C"))
                menu.addAction(cpy_quest)
                paste_quest = QAction("Paste question")
                paste_quest.setShortcut(QKeySequence("Ctrl+V"))
                if self.copied[1] != "question":
                    paste_quest.setEnabled(False)
                paste_quest.triggered.connect(lambda: self.paste(self.treeview.itemAt(position)))
                menu.addAction(paste_quest)
            if menu is not None:
                menu.exec_(self.treeview.viewport().mapToGlobal(position))

    def copy(self, node, copy_type):
        """Copy a page or question.

        Parameters
        ----------
        node : QTreeWidgetItem
            selected object in the tree
        copy_type : str, None
            reffering to what is copied (page or question)
        """
        if copy_type == "page":
            self.copied = [self.parent().structure[node.text(0)], "page"]
        elif copy_type == "question":
            self.copied = [self.parent().structure[node.parent().text(0)][node.text(0)], copy_type]
        elif copy_type is None:  # Initialized through top-menu
            if node is None or (node is not None and node.parent() is None):
                self.set_status_message("Nothing selected to copy.")
            elif node.text(0) in self.parent().structure.sections:  # is page
                self.copied = [self.parent().structure[node.text(0)], "page"]
            elif node is not None and node.parent() is not None:  # is question
                self.copied = [self.parent().structure[node.parent().text(0)][node.text(0)], "question"]
        self.button_paste.setEnabled(True)
        self.parent().pasteaction.setEnabled(True)

    # noinspection PyTypeChecker
    def paste(self, item=None):
        """Paste copied page/question into the tree.

        Parameters
        ----------
        item : QTreeWidgetItem, default=None
            clicked on object in the tree
        """
        pasted = False
        before = copy.deepcopy(dict(self.parent().structure))
        if self.copied[0] is not None:
            if item is None or type(item) is bool:
                item = self.current_item
            if item is not None:
                if (item.parent() is None and self.copied[1] != "page") or (item.parent() is not None and item.text(0) not in self.parent().structure.sections and self.copied[1] != "question"):
                    self.set_status_message("Can't paste here.")
                elif item.parent() is not None and item.text(0) not in self.parent().structure.sections and self.copied[1] == "question":
                    self.add_question(item.parent(), self.copied[0])
                    pasted = True
                elif item.parent() is None and self.copied[1] == "page":
                    self.add_page(self.copied[0])
                    pasted = True
                elif item.parent() is not None and item.text(0) in self.parent().structure.sections and self.copied[1] == "question":
                    self.add_question(item, self.copied[0])
                    pasted = True
                elif item.parent() is not None and item.text(0) in self.parent().structure.sections and self.copied[1] == "page":
                    self.add_page(self.copied[0])
                    pasted = True
        if pasted:
            self.parent().undo_stack.append(before)
            self.parent().undoaction.setEnabled(True)
            self.parent().redo_stack.clear()
            self.parent().redoaction.setEnabled(False)

    def add_page(self, data=None):
        """Add a new page to the questionnaire stucture.

        Parameters
        ----------
        data : configobj.Section, default=None
            not None when adding a page by copy+paste
        """
        text, ok = QInputDialog.getText(self, "New page", "Name of the new page:", QLineEdit.Normal)
        if ok and text not in self.parent().structure.keys() and text != '':
            self.treeview.expandItem(self.treeview.itemAt(0, 0))
            if data is None or type(data) != configobj.Section:
                self.parent().undo_stack.append(
                    copy.deepcopy(dict(self.parent().structure)))
                self.parent().undoaction.setEnabled(True)
                self.parent().redo_stack.clear()
                self.parent().redoaction.setEnabled(False)
                new_page = {}
                page = QTreeWidgetItem(self.treeview.itemAt(0, 0), [text])
                for field in page_fields:
                    new_page[field] = ""
                self.parent().structure[text] = new_page
                if "save_after" not in self.parent().structure.keys() or self.parent().structure["save_after"] is None:
                    self.parent().structure["save_after"] = text
            else:
                page = QTreeWidgetItem(self.treeview.itemAt(0, 0), self.treeview.currentItem())
                page.setText(0, text)
                self.parent().structure[text] = {}  # data
                for key in data.keys():
                    if key not in data.sections:
                        self.parent().structure[text][key] = data[key]
                    else:
                        self.parent().structure[text][key] = copy.deepcopy(dict(data[key]))
                for quest in data.sections:
                    _ = QTreeWidgetItem(page, [quest])
                self.update_structure()
            self.treeview.setCurrentItem(page)
            self.show_details(self.treeview.indexFromItem(page))
            if self.automatic_refresh.isChecked() and (data is None or type(data) != configobj.Section):
                self.load_preview()
        elif text in self.parent().structure.keys():
            if text in general_fields:
                self.set_status_message(
                    "Cannot create page named {}. A general field is already named that.".format(text))
            else:
                self.set_status_message("Page {} already exists.".format(text))
        else:
            self.set_status_message("Add page aborted.")

    def add_question(self, page, data=None):
        """Add a new question to the questionnaire stucture.

        Parameters
        ----------
        page: QTreeWidgetItem
            the page on which the question will be
        data : configObj.Section, default=None
            not None when adding a page by copy+paste
        """
        text, ok = QInputDialog.getText(self, "New question", "Name of the new question:", QLineEdit.Normal)
        if ok and text not in self.parent().structure[page.text(0)].keys() and text != '':
            self.treeview.expandItem(page)
            if data is None:
                self.parent().undo_stack.append(copy.deepcopy(dict(self.parent().structure)))
                self.parent().undoaction.setEnabled(True)
                self.parent().redo_stack.clear()
                self.parent().redoaction.setEnabled(False)
                self.parent().structure[page.text(0)][text] = {}
                quest = QTreeWidgetItem(page, [text])
                quest.setFlags(quest.flags() & ~Qt.ItemIsDropEnabled)
                new_question = {"type": "HLine"}
                self.parent().structure[page.text(0)][text] = new_question
            else:
                quest = QTreeWidgetItem(page, self.treeview.currentItem())
                quest.setText(0, text)
                quest.setFlags(quest.flags() & ~Qt.ItemIsDropEnabled)
                new_question = data.copy()
                self.parent().structure[page.text(0)][text] = new_question  # data
                self.update_structure()
            self.treeview.setCurrentItem(quest)
            self.show_details(self.treeview.indexFromItem(quest), True)
            if self.automatic_refresh.isChecked() and data is None:
                self.load_preview()
        elif text in self.parent().structure[page.text(0)].keys():
            if text in page_fields:
                self.set_status_message(
                    "Cannot create question named {}. A general field is already named that.".format(text))
            else:
                self.set_status_message("Question {} already exists.".format(text))
        else:
            self.set_status_message("Add question aborted.")

    def remove_page(self, item):
        """Remove a page from the structure.

        Parameters
        ----------
        item : QTreeWidgetItem
            the page to be removed
        """
        self.parent().undo_stack.append(copy.deepcopy(dict(self.parent().structure)))
        self.parent().undoaction.setEnabled(True)
        self.parent().redo_stack.clear()
        self.parent().redoaction.setEnabled(False)
        self.parent().structure.pop(item.text(0))
        if "save_after" in self.parent().structure.keys() and self.parent().structure["save_after"] == item.text(0):
            self.parent().structure["save_after"] = None
        sip.delete(item)  # delete AFTER last ref!
        self.treeview.clearSelection()
        self.current_item = None
        self.clear_layout(self.edit_layout)
        if self.automatic_refresh.isChecked():
            self.load_preview()

    def remove_question(self, item):
        """Remove a question from the structure.

        Parameters
        ----------
        item : QTreeWidgetItem
            the question to be removed
        """
        self.parent().undo_stack.append(copy.deepcopy(dict(self.parent().structure)))
        self.parent().undoaction.setEnabled(True)
        self.parent().redo_stack.clear()
        self.parent().redoaction.setEnabled(False)
        self.parent().structure[item.parent().text(0)].pop(item.text(0))
        sip.delete(item)  # delete AFTER last ref!
        self.clear_layout(self.edit_layout)
        self.treeview.clearSelection()
        self.current_item = None
        if self.automatic_refresh.isChecked():
            self.load_preview()

    def rename_page(self, item):
        """Change the name of a page.

        Parameters
        ----------
        item : QTreeWidgetItem
            the page to be renamed
        """
        text, ok = QInputDialog.getText(self, "Rename page", "New name for the page:", QLineEdit.Normal)
        if ok and text not in self.parent().structure.keys() and text != '':
            self.parent().undo_stack.append(copy.deepcopy(dict(self.parent().structure)))
            self.parent().undoaction.setEnabled(True)
            self.parent().redo_stack.clear()
            self.parent().redoaction.setEnabled(False)
            self.parent().structure.rename(item.text(0), text)
            self.treeview.setCurrentItem(item)
            self.treeview.currentItem().setText(0, text)
            self.show_details(self.treeview.indexFromItem(item))
        elif text in self.parent().structure.keys():
            if text in general_fields:
                self.set_status_message(
                    "Cannot rename page to {}. A general field is already named that.".format(text))
            else:
                self.set_status_message("Page {} already exists.".format(text))
        else:
            self.set_status_message("Add page aborted.")

    def rename_question(self, item):
        """Change the name of a question.

        Parameters
        ----------
        item : QTreeWidgetItem
            the question to be renamed
        """
        text, ok = QInputDialog.getText(self, "Rename question", "New name for the question:", QLineEdit.Normal)
        if ok and text not in self.parent().structure[item.parent().text(0)].keys() and text != '':
            self.parent().undo_stack.append(copy.deepcopy(dict(self.parent().structure)))
            self.parent().undoaction.setEnabled(True)
            self.parent().redo_stack.clear()
            self.parent().redoaction.setEnabled(False)
            self.parent().structure[item.parent().text(0)].rename(item.text(0), text)
            self.treeview.setCurrentItem(item)
            self.treeview.currentItem().setText(0, text)
            self.show_details(self.treeview.indexFromItem(item))
        elif text in self.parent().structure[item.parent().text(0)].keys():
            if text in page_fields:
                self.set_status_message(
                    "Cannot rename question to {}. A general field is already named that.".format(text))
            else:
                self.set_status_message("Question {} already exists.".format(text))
        else:
            self.set_status_message("Add question aborted.")

    def update_structure(self):
        """Update the internal (config) structure, when the visual tree model has been manipulated."""
        self.parent().undo_stack.append(copy.deepcopy(dict(self.parent().structure)))
        self.parent().undoaction.setEnabled(True)
        self.parent().redo_stack.clear()
        self.parent().redoaction.setEnabled(False)
        root = self.treeview.invisibleRootItem()
        child_count = root.childCount()
        pages = []
        questions = []
        for i in range(child_count):
            item = root.child(i)
            for j in range(item.childCount()):
                item2 = item.child(j)
                node_name = item2.text(0)
                pages.append(node_name)
                questions.append([])
                for k in range(item2.childCount()):
                    item3 = item2.child(k)
                    node_name = item3.text(0)
                    questions[j].append(node_name)

        dict_cpy = self.parent().structure.dict()

        if pages != self.parent().structure.sections:
            # TODO Testcases
            for page_no in range(len(pages)):
                if page_no < len(self.parent().structure.sections):
                    if pages[page_no] != self.parent().structure.sections[page_no]:
                        self.parent().structure.pop(self.parent().structure.sections[page_no])
                        while (page_no < len(self.parent().structure.sections)) and (
                                pages[page_no] != self.parent().structure.sections[page_no]):
                            self.parent().structure.pop(self.parent().structure.sections[page_no])
                else:
                    break
            for page_no in range(len(self.parent().structure.sections), len(pages)):
                self.parent().structure[pages[page_no]] = dict_cpy[pages[page_no]]
            if self.automatic_refresh.isChecked():
                self.load_preview()
            # print("new", self.parent().structure.sections)
        else:
            # TODO Testcases
            removed_question = None
            for page in range(len(self.parent().structure.sections)):
                if self.parent().structure[pages[page]].sections != questions[page]:
                    if len(questions[page]) < len(self.parent().structure[pages[page]].sections):
                        # question was moved from here
                        # print(self.parent().structure[pages[page]].sections, questions[page])
                        diff = []
                        for other_page in self.parent().structure[pages[page]].sections:
                            if other_page not in questions[page]:
                                diff.append(other_page)
                        # print("diff", diff)
                        removed_question = [dict_cpy[pages[page]][diff[0]]]
                        # print("Removing", pages[page], diff[0])
                        self.parent().structure[pages[page]].pop(diff[0])
                        # print("new", self.parent().structure[pages[page]].sections)
                    elif len(questions[page]) == len(self.parent().structure[pages[page]].sections):
                        # page-internal reorder
                        for quest_no in range(len(questions[page])):
                            if quest_no < len(self.parent().structure[pages[page]].sections):
                                if questions[page][quest_no] != self.parent().structure[pages[page]].sections[quest_no]:
                                    # print("Removing", pages[page], self.parent().structure[pages[page]].sections[quest_no])
                                    self.parent().structure[pages[page]].pop(self.parent().structure[pages[page]].sections[quest_no])
                                    while (quest_no < len(self.parent().structure[pages[page]].sections)) and (
                                            questions[page][quest_no] != self.parent().structure[pages[page]].sections[quest_no]):
                                        # print("Removing", pages[page],self.parent().structure[pages[page]].sections[quest_no])
                                        self.parent().structure[pages[page]].pop(self.parent().structure[pages[page]].sections[quest_no])
                            else:
                                break
                        for quest_no in range(len(self.parent().structure[pages[page]].sections), len(questions[page])):
                            self.parent().structure[pages[page]][questions[page][quest_no]] = dict_cpy[pages[page]][questions[page][quest_no]]
                        # print("new", self.parent().structure[pages[page]].sections)
                    else:
                        # new question inserted!
                        # print(len(questions[page]), ">", len(self.parent().structure[pages[page]].sections))
                        for quest_no in range(len(questions[page])):
                            if quest_no < len(self.parent().structure[pages[page]].sections):
                                if questions[page][quest_no] != self.parent().structure[pages[page]].sections[quest_no]:
                                    # print("Removing", pages[page],self.parent().structure[pages[page]].sections[quest_no])
                                    self.parent().structure[pages[page]].pop(self.parent().structure[pages[page]].sections[quest_no])
                                    while (quest_no < len(self.parent().structure[pages[page]].sections)) and (
                                            questions[page][quest_no] != self.parent().structure[pages[page]].sections[quest_no]):
                                        # print("Removing...", pages[page],self.parent().structure[pages[page]].sections[quest_no])
                                        self.parent().structure[pages[page]].pop(self.parent().structure[pages[page]].sections[quest_no])
                            else:
                                break
                        for quest_no in range(len(self.parent().structure[pages[page]].sections), len(questions[page])):
                            if questions[page][quest_no] in dict_cpy[pages[page]].keys():  # fetch questions that have been in this section before
                                # print("Reading...", questions[page][quest_no], dict_cpy[pages[page]][questions[page][quest_no]])
                                self.parent().structure[pages[page]][questions[page][quest_no]] = dict_cpy[pages[page]][questions[page][quest_no]]
                            elif removed_question is not None:  # it has moved here and already been removed from the other page
                                # print("Adding", questions[page][quest_no], removed_question)
                                self.parent().structure[pages[page]][questions[page][quest_no]] = removed_question[0]
                            else:
                                # it's the question moved here, it's not been processed yet
                                diff = []
                                for other_page in range(len(self.parent().structure.sections)):
                                    if len(self.parent().structure[self.parent().structure.sections[other_page]].sections) > len(questions[other_page]):
                                        # find the page it's came from
                                        diff = [self.parent().structure.sections[other_page]]
                                        # print("other page:", diff)
                                        # print(self.parent().structure[diff[0]])
                                        # print("sec", self.parent().structure[diff[0]].sections)
                                        # print("new quests",questions[other_page])
                                        for other_sections in self.parent().structure[self.parent().structure.sections[other_page]].sections:
                                            # print("e2", other_sections)
                                            if other_sections not in questions[other_page]:  # find the question removed
                                                # print("diff found", other_sections)
                                                diff.append(self.parent().structure[self.parent().structure.sections[other_page]][other_sections])
                                # print("Adding", questions[page][quest_no], diff[1])
                                self.parent().structure[pages[page]][questions[page][quest_no]] = diff[1]  # append here
                                # print("New structure after adding:", self.parent().structure.sections, self.parent().structure[pages[page]].sections)
                        # print("new!!!", self.parent().structure[pages[page]].sections)
            if self.automatic_refresh.isChecked():
                self.load_preview()


if __name__ == '__main__':
    app = QApplication([])
    ex = QEditGuiMain()
    app.exec_()
