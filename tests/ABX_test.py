"""Testing the behaviour of ABX.py + QEditGui.py"""

from tests.context import pytest, QEditGuiMain, QTimer, open_config_file, StackedWindowGui, QTest, handle_dialog_p, handle_dialog_q, Qt, types, QFormLayout, QWidgetItem, fields_per_type, default_values, QCheckBox, QLineEdit, page_fields, listify, ConfigObj, general_fields, handle_dialog_error, validate_questionnaire, handle_dialog_no_save, find_row_by_label, handle_dialog, csv, re, os, mock_file, ABX, ast


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file(os.path.join(os.getcwd(), "tests/abxtest.txt")))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui(os.path.join(os.getcwd(), "tests/abxtest.txt"))


@pytest.fixture
def run2():
    """Execute the questionnaire."""
    return StackedWindowGui(os.path.join(os.getcwd(), "tests/abxtest2.txt"))


# noinspection PyArgumentList
def test_create(gui_init, qtbot):
    # create a page
    assert gui_init.gui.page_add.isEnabled()
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_p)
    QTest.mouseClick(gui_init.gui.page_add, Qt.MouseButton.LeftButton, delay=1000)
    tv = gui_init.gui.treeview
    # create a question
    tv.setCurrentItem(tv.topLevelItem(0).child(0))
    assert gui_init.gui.question_add.isEnabled()
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_q)
    QTest.mouseClick(gui_init.gui.question_add, Qt.MouseButton.LeftButton, delay=1000)
    assert tv.itemAt(0, 0).text(0) == "<new questionnaire>"
    assert tv.topLevelItemCount() == 1
    assert tv.topLevelItem(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).text(0) == "Page 1"
    assert tv.topLevelItem(0).child(0).child(0).childCount() == 0
    assert tv.topLevelItem(0).child(0).child(0).text(0) == "Question 1"
    assert len(gui_init.undo_stack) == 2
    # change the question type to 'ABX'
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"
    QTest.mouseClick(gui_init.gui.questiontype, Qt.MouseButton.LeftButton)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Enter)
    gui_init.gui.questiontype.setCurrentIndex(types.index("ABX"))
    assert gui_init.gui.questiontype.currentText() == "ABX"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QWidgetItem):
            not_none_rows += 1
            assert layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in fields_per_type["ABX"][0]
            assert str(type(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   fields_per_type["ABX"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
            if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QLineEdit) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().text() == default_values[layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
            elif isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QCheckBox) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().isChecked() == default_values[
                    layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
    assert not_none_rows == len(fields_per_type["ABX"][0].keys())
    assert len(gui_init.undo_stack) == 12  # 2 for creating page & question, 10 for choosing ABX

    # Check structure
    structure = ConfigObj()
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    structure["Page 1"]["Question 1"] = {"type": "ABX"}
    for key, value in default_values.items():
        if key in fields_per_type["ABX"][0]:
            structure["Page 1"]["Question 1"][key] = value
    listify(gui_init.structure)
    listify(structure)

    QTimer.singleShot(100, handle_dialog_error)
    validate_questionnaire(gui_init.structure, suppress=True)
    QTimer.singleShot(100, handle_dialog_error)
    validate_questionnaire(structure, suppress=True)
    assert gui_init.structure == structure

    # save file comparison
    structure.encoding = "utf-8"
    structure.filename = "./tmp_e.txt"
    structure.write()
    gui_init.structure.filename = "./tmp_a.txt"
    gui_init.structure.encoding = "utf-8"
    gui_init.structure.write()
    with open("./tmp_e.txt") as fe:
        temp_e = fe.readlines()
    with open("./tmp_a.txt") as fa:
        temp_a = fa.readlines()
    assert temp_a == temp_e
    QTimer.singleShot(150, handle_dialog_no_save)
    gui_init.close()


def test_button_texts(gui_load, qtbot):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())
    labels_pos = find_row_by_label(gui_load.gui.edit_layout, 'button_texts')
    x_pos = find_row_by_label(gui_load.gui.edit_layout, "x")

    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("only one")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "only one"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["button_texts"] == "only one"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["button_texts"] == "1"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one, two, too many")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one, two, too many"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["button_texts"] == "one, two, too many"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["button_texts"] == ""
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    # ABX
    gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["x"]

    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one, two")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one, two"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["button_texts"] == "one, two"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one, two, three, too many")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one, two, three, too many"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["button_texts"] == "one, two, three, too many"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one, two, not too many")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one, two, not too many"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["button_texts"] == "one, two, not too many"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["button_texts"] == ""
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTimer.singleShot(150, handle_dialog_no_save)
    gui_load.close()


def test_answers(gui_load, qtbot):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())
    ans_pos = find_row_by_label(gui_load.gui.edit_layout, 'answers')
    button_pos = find_row_by_label(gui_load.gui.edit_layout, 'button_texts')
    x_pos = find_row_by_label(gui_load.gui.edit_layout, "x")

    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().setText("only one")
    assert gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "only one"
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == "only one"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1")
    assert gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1"
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == "1"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one, two, too many")
    assert gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one, two, too many"
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == "one, two, too many"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # ABX
    gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["x"]
    gui_load.gui.edit_layout.itemAt(button_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(button_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["button_texts"] == ""

    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().setText("only one")
    assert gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "only one"
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == "only one"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one, two, too many")
    assert gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one, two, too many"
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == "one, two, too many"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one, two")
    assert gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one, two"
    gui_load.gui.edit_layout.itemAt(ans_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == "one, two"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTimer.singleShot(150, handle_dialog_no_save)
    gui_load.close()


def test_x(gui_load, qtbot):
    # If the string is one of  ``True``, ``On``, ``Yes``, or ``1`` it returns
    #         ``True``.
    #
    # If the string is one of  ``False``, ``Off``, ``No``, or ``0`` it returns
    #         ``False``.
    #
    # It is not case sensitive.
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.structure["Page 1"]["Question 1"]["x"] = True
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.structure["Page 1"]["Question 1"]["x"] = False
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.structure["Page 1"]["Question 1"]["x"] = "True"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.structure["Page 1"]["Question 1"]["x"] = "False"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.structure["Page 1"]["Question 1"]["x"] = 1
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.structure["Page 1"]["Question 1"]["x"] = 0
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.structure["Page 1"]["Question 1"]["x"] = "true"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.structure["Page 1"]["Question 1"]["x"] = "false"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.structure["Page 1"]["Question 1"]["x"] = 123
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found
    gui_load.close()


def test_start_cues(gui_load, qtbot):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())
    sc_pos = find_row_by_label(gui_load.gui.edit_layout, 'start_cues')
    button_pos = find_row_by_label(gui_load.gui.edit_layout, 'button_texts')
    x_pos = find_row_by_label(gui_load.gui.edit_layout, "x")

    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "1"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1, 2, 3")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1, 2, 3"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "1, 2, 3"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == ""
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1, 2")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1, 2"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "1, 2"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("'1', 2")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "'1', 2"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "'1', 2"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1, '2'")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1, '2'"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "1, '2'"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    # ABX
    gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["x"]
    gui_load.gui.edit_layout.itemAt(button_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(button_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["button_texts"] == ""

    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "1"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1, 2, 3")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1, 2, 3"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "1, 2, 3"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("'1', 2")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "'1', 2"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "'1', 2"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTimer.singleShot(150, handle_dialog_no_save)
    gui_load.close()


def test_track(gui_load, qtbot):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())
    track_pos = find_row_by_label(gui_load.gui.edit_layout, 'track')
    button_pos = find_row_by_label(gui_load.gui.edit_layout, 'button_texts')
    x_pos = find_row_by_label(gui_load.gui.edit_layout, "x")

    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1, 2, 3")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1, 2, 3"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1, 2, 3"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == ""
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1, 2")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1, 2"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1, 2"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("'1', 2")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "'1', 2"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "'1', 2"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("'1','2'")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "'1','2'"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "'1','2'"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1,'2'")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,'2'"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1,'2'"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    # ABX
    gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["x"]
    gui_load.gui.edit_layout.itemAt(button_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(button_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["button_texts"] == ""

    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1, 2, 3")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1, 2, 3"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1, 2, 3"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("'1',2")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "'1',2"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "'1',2"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTimer.singleShot(150, handle_dialog_no_save)
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    assert run.Stack.count() == 1
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)

    results = []
    with open('./tests/results/results_abx.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 7
    assert results[0] == '1'  # participant number
    assert results[2] == '-1'  # no answer given in button group
    assert results[3] == '[]'  # first element not played
    assert results[4] == '[]'  # second element not played
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[5])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[6])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_blocked(run, qtbot):
    with mock_file(r'./tests/results/results_abx.csv'):
        assert run.Stack.count() == 1
        QTimer.singleShot(100, handle_dialog)
        QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)
        res_file = None
        for file in os.listdir("./tests/results/"):
            if file.find("_backup_"):
                res_file = f'./tests/results/{file}'
        results = []
        with open(res_file, mode='r') as file:
            csv_file = csv.reader(file, delimiter=';')

            for lines in csv_file:
                results = lines
                if results[0].startswith('data'):
                    assert results[0] == 'data_row_number'  # participant number
                    assert results[1] == '1_order'
                    assert results[2] == '1_answer'
                    assert results[3] == '1_duration_A'
                    assert results[4] == '1_duration_B'
                    assert results[5] == 'Start'
                    assert results[6] == 'End'
        assert len(results) == 7
        assert results[0] == '-1'  # participant number unknown
        assert results[2] == '-1'  # no answer given in button group
        assert results[3] == '[]'  # first element not played
        assert results[4] == '[]'  # second element not played
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[5])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[6])  # timestamp
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire_ab(run, qtbot):
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if isinstance(child, ABX):
            QTest.mouseClick(child.a_button.play_button, Qt.MouseButton.LeftButton)
            QTest.qWait(1000)
            QTest.mouseClick(child.b_button.play_button, Qt.MouseButton.LeftButton)
            QTest.qWait(500)
            QTest.mouseClick(child.a_button.play_button, Qt.MouseButton.LeftButton)
            QTest.mouseClick(child.answer.button(0), Qt.MouseButton.LeftButton, delay=1000)

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)

    results = []
    with open('./tests/results/results_abx.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert results[0] == 'data_row_number'  # participant number
                assert results[1] == '1_order'
                assert results[2] == '1_answer'
                assert results[3] == '1_duration_A'
                assert results[4] == '1_duration_B'
                assert results[5] == 'Start'
                assert results[6] == 'End'
    assert len(results) == 7
    assert results[0] == '1'  # participant number
    assert results[2] == '0'  # first answer given in button group
    assert len(ast.literal_eval(results[3])) == 2  # first element played twice
    assert float(ast.literal_eval(results[3])[0]) > 1.0
    assert len(ast.literal_eval(results[4])) == 1  # second element played once
    assert float(ast.literal_eval(results[4])[0]) > 0.5
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[5])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[6])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire_blocked(run, qtbot):
    with mock_file(r'./tests/results/results_abx.csv'):
        assert run.Stack.count() == 1
        for child in run.Stack.currentWidget().children():
            if isinstance(child, ABX):
                QTest.mouseClick(child.a_button.play_button, Qt.MouseButton.LeftButton)
                QTest.qWait(1000)
                QTest.mouseClick(child.b_button.play_button, Qt.MouseButton.LeftButton)
                QTest.qWait(500)
                QTest.mouseClick(child.a_button.play_button, Qt.MouseButton.LeftButton)
                QTest.mouseClick(child.answer.button(0), Qt.MouseButton.LeftButton, delay=1000)
        QTimer.singleShot(100, handle_dialog)
        QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)
        res_file = None
        for file in os.listdir("./tests/results/"):
            if file.find("_backup_"):
                res_file = f'./tests/results/{file}'
        results = []
        with open(res_file, mode='r') as file:
            csv_file = csv.reader(file, delimiter=';')

            for lines in csv_file:
                results = lines
                if results[0].startswith('data'):
                    assert results[0] == 'data_row_number'  # participant number
                    assert results[1] == '1_order'
                    assert results[2] == '1_answer'
                    assert results[3] == '1_duration_A'
                    assert results[4] == '1_duration_B'
                    assert results[5] == 'Start'
                    assert results[6] == 'End'
        assert len(results) == 7
        assert results[0] == '-1'  # participant number unknown
        assert results[2] == '0'  # first answer given in button group
        assert len(ast.literal_eval(results[3])) == 2  # first element played twice
        assert float(ast.literal_eval(results[3])[0]) > 1.0
        assert len(ast.literal_eval(results[4])) == 1  # second element played once
        assert float(ast.literal_eval(results[4])[0]) > 0.5
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[5])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[6])  # timestamp
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_x(run2, qtbot):
    assert run2.Stack.count() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run2.forwardbutton, Qt.MouseButton.LeftButton)

    results = []
    with open('./tests/results/results_abx.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 8
    assert results[0] == '1'  # participant number
    assert results[2] == '-1'  # no answer given in button group
    assert results[3] == '[]'  # first element not played
    assert results[4] == '[]'  # second element not played
    assert results[5] == '[]'  # x not played
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[6])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[7])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_x_blocked(run2, qtbot):
    with mock_file(r'./tests/results/results_abx.csv'):
        assert run2.Stack.count() == 1
        QTimer.singleShot(100, handle_dialog)
        QTest.mouseClick(run2.forwardbutton, Qt.MouseButton.LeftButton)
        res_file = None
        for file in os.listdir("./tests/results/"):
            if file.find("_backup_"):
                res_file = f'./tests/results/{file}'
        results = []
        with open(res_file, mode='r') as file:
            csv_file = csv.reader(file, delimiter=';')

            for lines in csv_file:
                results = lines
                if results[0].startswith('data'):
                    assert results[0] == 'data_row_number'  # participant number
                    assert results[1] == '1_order'
                    assert results[2] == '1_answer'
                    assert results[3] == '1_duration_A'
                    assert results[4] == '1_duration_B'
                    assert results[5] == '1_duration_X'
                    assert results[6] == 'Start'
                    assert results[7] == 'End'
        assert len(results) == 8
        assert results[0] == '-1'  # participant number unknown
        assert results[2] == '-1'  # no answer given in button group
        assert results[3] == '[]'  # first element not played
        assert results[4] == '[]'  # second element not played
        assert results[5] == '[]'  # x not played
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[6])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[7])  # timestamp
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire_abx(run2, qtbot):
    assert run2.Stack.count() == 1
    for child in run2.Stack.currentWidget().children():
        if isinstance(child, ABX):
            QTest.mouseClick(child.x_button.play_button, Qt.MouseButton.LeftButton)
            QTest.qWait(500)
            QTest.mouseClick(child.a_button.play_button, Qt.MouseButton.LeftButton)
            QTest.qWait(1000)
            QTest.mouseClick(child.x_button.play_button, Qt.MouseButton.LeftButton)
            QTest.qWait(500)
            QTest.mouseClick(child.b_button.play_button, Qt.MouseButton.LeftButton)
            QTest.qWait(500)
            QTest.mouseClick(child.x_button.play_button, Qt.MouseButton.LeftButton)
            QTest.qWait(500)
            QTest.mouseClick(child.b_button.play_button, Qt.MouseButton.LeftButton)
            QTest.qWait(2000)
            QTest.mouseClick(child.answer.button(0), Qt.MouseButton.LeftButton, delay=1000)

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run2.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)

    results = []
    with open('./tests/results/results_abx.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert results[0] == 'data_row_number'  # participant number
                assert results[1] == '1_order'
                assert results[2] == '1_answer'
                assert results[3] == '1_duration_A'
                assert results[4] == '1_duration_B'
                assert results[5] == '1_duration_X'
                assert results[6] == 'Start'
                assert results[7] == 'End'
    assert len(results) == 8
    assert results[0] == '1'  # participant number
    assert results[2] == '0'  # first answer given in button group
    assert len(ast.literal_eval(results[3])) == 1  # first element played once
    assert len(ast.literal_eval(results[4])) == 2  # second element played twice
    assert len(ast.literal_eval(results[5])) == 3  # third (x) element played three times
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[6])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[7])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire_abx_blocked(run2, qtbot):
    with mock_file(r'./tests/results/results_abx.csv'):
        assert run2.Stack.count() == 1
        for child in run2.Stack.currentWidget().children():
            if isinstance(child, ABX):
                QTest.mouseClick(child.x_button.play_button, Qt.MouseButton.LeftButton)
                QTest.qWait(500)
                QTest.mouseClick(child.a_button.play_button, Qt.MouseButton.LeftButton)
                QTest.qWait(1000)
                QTest.mouseClick(child.x_button.play_button, Qt.MouseButton.LeftButton)
                QTest.qWait(500)
                QTest.mouseClick(child.b_button.play_button, Qt.MouseButton.LeftButton)
                QTest.qWait(500)
                QTest.mouseClick(child.x_button.play_button, Qt.MouseButton.LeftButton)
                QTest.qWait(500)
                QTest.mouseClick(child.b_button.play_button, Qt.MouseButton.LeftButton)
                QTest.qWait(2000)
                QTest.mouseClick(child.answer.button(0), Qt.MouseButton.LeftButton, delay=1000)
        QTimer.singleShot(100, handle_dialog)
        QTest.mouseClick(run2.forwardbutton, Qt.MouseButton.LeftButton)
        res_file = None
        for file in os.listdir("./tests/results/"):
            if file.find("_backup_"):
                res_file = f'./tests/results/{file}'
        results = []
        with open(res_file, mode='r') as file:
            csv_file = csv.reader(file, delimiter=';')

            for lines in csv_file:
                results = lines
                if results[0].startswith('data'):
                    assert results[0] == 'data_row_number'  # participant number
                    assert results[1] == '1_order'
                    assert results[2] == '1_answer'
                    assert results[3] == '1_duration_A'
                    assert results[4] == '1_duration_B'
                    assert results[5] == '1_duration_X'
                    assert results[6] == 'Start'
                    assert results[7] == 'End'
        assert len(results) == 8
        assert results[0] == '-1'  # participant number unknown
        assert results[2] == '0'  # first answer given in button group
        assert len(ast.literal_eval(results[3])) == 1  # first element played once
        assert len(ast.literal_eval(results[4])) == 2  # second element played twice
        assert len(ast.literal_eval(results[5])) == 3  # third (x) element played three times
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[6])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[7])  # timestamp
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
