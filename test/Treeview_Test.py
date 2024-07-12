"""Testing the behaviour of Tree.py + QEditGui.py
Ref how to auto-dialog: https://stackoverflow.com/a/59148220
"""

from context import *


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


def test_create(gui_init, qtbot):
    tv = gui_init.gui.treeview
    assert tv.itemAt(0, 0).text(0) == "<new questionnaire>"
    assert tv.topLevelItemCount() == 1
    assert tv.topLevelItem(0).childCount() == 0
    assert len(gui_init.undo_stack) == 0
    structure = {}
    for key, value in default_values.items():
        if key in general_fields:
            structure[key] = value
    assert gui_init.structure == structure


# noinspection PyArgumentList
def test_add_page(gui_init, qtbot):
    tv = gui_init.gui.treeview
    assert gui_init.gui.page_add.isEnabled() == True
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_p)
    QTest.mouseClick(gui_init.gui.page_add, Qt.MouseButton.LeftButton, delay=1)
    assert tv.itemAt(0, 0).text(0) == "<new questionnaire>"
    assert tv.topLevelItemCount() == 1
    assert tv.topLevelItem(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).childCount() == 0
    assert tv.topLevelItem(0).child(0).text(0) == "Page 1"
    assert len(gui_init.undo_stack) == 1
    structure = ConfigObj()  # {}
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    listify(gui_init.structure)
    listify(structure)
    QTimer.singleShot(150, handle_dialog_error)
    validate_questionnaire(gui_init.structure, suppress=True)
    QTimer.singleShot(100, handle_dialog_error)
    validate_questionnaire(structure, suppress=True)
    assert gui_init.structure == structure


def test_load_file(gui_init, qtbot):
    QTimer.singleShot(150, lambda: open_config_file("./test/onepage.txt"))
    gui_init.load_file()
    tv = gui_init.gui.treeview
    assert tv.itemAt(0, 0).text(0) == "onepage.txt"
    assert tv.topLevelItemCount() == 1
    assert tv.topLevelItem(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).childCount() == 0
    assert len(gui_init.undo_stack) == 0


# noinspection PyArgumentList
def test_add_page_add_question(gui_init, qtbot):
    assert gui_init.gui.page_add.isEnabled() == True
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_p)
    QTest.mouseClick(gui_init.gui.page_add, Qt.MouseButton.LeftButton, delay=1)
    tv = gui_init.gui.treeview
    tv.setCurrentItem(tv.topLevelItem(0).child(0))
    assert gui_init.gui.question_add.isEnabled() == True
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_q)
    QTest.mouseClick(gui_init.gui.question_add, Qt.MouseButton.LeftButton, delay=1)
    assert tv.itemAt(0, 0).text(0) == "<new questionnaire>"
    assert tv.topLevelItemCount() == 1
    assert tv.topLevelItem(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).text(0) == "Page 1"
    assert tv.topLevelItem(0).child(0).child(0).childCount() == 0
    assert tv.topLevelItem(0).child(0).child(0).text(0) == "Question 1"
    assert len(gui_init.undo_stack) == 2


# noinspection PyArgumentList
def test_add_question_after_load(gui_init, qtbot):
    QTimer.singleShot(150, lambda: open_config_file("./test/onepage.txt"))
    gui_init.load_file()
    tv = gui_init.gui.treeview
    tv.setCurrentItem(tv.topLevelItem(0).child(0))
    assert gui_init.gui.question_add.isEnabled() == True
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_q)
    QTest.mouseClick(gui_init.gui.question_add, Qt.MouseButton.LeftButton, delay=1)
    assert tv.itemAt(0, 0).text(0) == "onepage.txt"
    assert tv.topLevelItemCount() == 1
    assert tv.topLevelItem(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).text(0) == "Section"
    assert tv.topLevelItem(0).child(0).child(0).childCount() == 0
    assert tv.topLevelItem(0).child(0).child(0).text(0) == "Question 1"
    assert len(gui_init.undo_stack) == 1


# noinspection PyArgumentList
def test_add_page_after_load(gui_init, qtbot):
    QTimer.singleShot(150, lambda: open_config_file("./test/onepage.txt"))
    gui_init.load_file()
    tv = gui_init.gui.treeview
    tv.setCurrentItem(tv.topLevelItem(0))
    assert gui_init.gui.page_add.isEnabled() == True
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_p)
    QTimer.singleShot(200, handle_dialog_sa)
    QTest.mouseClick(gui_init.gui.page_add, Qt.MouseButton.LeftButton, delay=1)

    assert tv.itemAt(0, 0).text(0) == "onepage.txt"
    assert tv.topLevelItemCount() == 1
    assert tv.topLevelItem(0).childCount() == 2
    assert tv.topLevelItem(0).child(0).childCount() == 0
    assert tv.topLevelItem(0).child(0).text(0) == "Section"
    assert len(gui_init.undo_stack) == 1
