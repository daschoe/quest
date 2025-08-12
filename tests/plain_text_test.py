"""Testing the behaviour of Plain text + QEditGui.py"""

from tests.context import pytest, QEditGuiMain, QTimer, open_config_file, StackedWindowGui, QTest, QLabel, handle_dialog_p, handle_dialog_q, Qt, QFormLayout, QWidgetItem, fields_per_type, default_values, QCheckBox, QLineEdit, page_fields, listify, ConfigObj, general_fields, handle_dialog_error, validate_questionnaire, handle_dialog_no_save, find_row_by_label, handle_dialog, csv, re, os, mock_file


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file(os.path.join(os.getcwd(), "tests/pttest.txt")))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui(os.path.join(os.getcwd(), "tests/pttest.txt"))


# noinspection PyArgumentList
def test_create(gui_init, qtbot):
    # create a page
    assert gui_init.gui.page_add.isEnabled()
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_p)
    QTest.mouseClick(gui_init.gui.page_add, Qt.MouseButton.LeftButton, delay=1000)
    tv = gui_init.gui.treeview
    # create a question
    tv.setCurrentItem(tv.topLevelItem(0).child(0))  # .setSelected(True)
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
    # change the question type to 'Plain Text'
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
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "Plain Text"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QWidgetItem):
            not_none_rows += 1
            assert layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in fields_per_type["Plain Text"][0]
            assert str(type(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["Plain Text"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()] == 'QPlainTextEdit'\
                   else fields_per_type["Plain Text"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
            if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QLineEdit) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().text() == default_values[layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
            elif isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QCheckBox) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().isChecked() == default_values[
                    layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
    assert not_none_rows == len(fields_per_type["Plain Text"][0].keys())
    assert len(gui_init.undo_stack) == 10  # 2 for creating page & question, 8 for choosing Plain Text

    # Check structure
    structure = ConfigObj()  # {}
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    structure["Page 1"]["Question 1"] = {"type": "Plain Text"}
    for key, value in default_values.items():
        if key in fields_per_type["Plain Text"][0]:
            structure["Page 1"]["Question 1"][key] = value
    listify(gui_init.structure)
    listify(structure)

    QTimer.singleShot(150, handle_dialog_error)
    validate_questionnaire(gui_init.structure, suppress=True)
    QTimer.singleShot(150, handle_dialog_error)
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


def test_text(gui_load, qtbot):
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
    answers_pos = find_row_by_label(gui_load.gui.edit_layout, 'text')

    gui_load.gui.edit_layout.itemAt(answers_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(answers_pos, QFormLayout.ItemRole.FieldRole).widget().setPlainText("Some text.")
    assert gui_load.gui.edit_layout.itemAt(answers_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "Some text."
    gui_load.gui.edit_layout.itemAt(answers_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["text"] == "Some text."
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(answers_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(answers_pos, QFormLayout.ItemRole.FieldRole).widget().setPlainText("")
    assert gui_load.gui.edit_layout.itemAt(answers_pos, QFormLayout.ItemRole.FieldRole).widget().text() == ""
    gui_load.gui.edit_layout.itemAt(answers_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["text"] == ""
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert warning_found
    QTimer.singleShot(150, handle_dialog_no_save)
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if isinstance(child, QLabel):
            assert child.text() == "This is a test.\nDoes it work?"

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)

    results = []
    with open('./tests/results/results_pt.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert results[0] == 'data_row_number'  # participant number
                assert results[1] == 'Start'
                assert results[2] == 'End'
    assert len(results) == 3
    assert results[0] == '1'  # participant number
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[1])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    os.remove("./tests/results/results_pt.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_blocked(run, qtbot):
    with mock_file(r'./tests/results/results_pt.csv'):
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
                    assert results[1] == 'Start'
                    assert results[2] == 'End'
        assert len(results) == 3
        assert results[0] == '-1'  # participant number unknown
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[1])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
        os.remove(res_file)
