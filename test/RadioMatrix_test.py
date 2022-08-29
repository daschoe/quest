"""Testing the behaviour of RadioMatrix.py + QEditGui.py"""

from context import *


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file("./test/rmtest.txt"))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def gui_load_2(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file("./test/rm_two_pages.txt"))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui("./test/rmtest.txt")


@pytest.fixture
def run_2():
    """Execute the questionnaire."""
    return StackedWindowGui("./test/rm_two_pages.txt")


# noinspection PyArgumentList
def test_create(gui_init, qtbot):
    # create a page
    assert gui_init.gui.page_add.isEnabled() == True
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_p)
    QTest.mouseClick(gui_init.gui.page_add, Qt.LeftButton, delay=1)
    tv = gui_init.gui.treeview
    # create a question
    tv.setCurrentItem(tv.topLevelItem(0).child(0))  # .setSelected(True)
    assert gui_init.gui.question_add.isEnabled() == True
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_q)
    QTest.mouseClick(gui_init.gui.question_add, Qt.LeftButton, delay=1)
    assert tv.itemAt(0, 0).text(0) == "<new questionnaire>"
    assert tv.topLevelItemCount() == 1
    assert tv.topLevelItem(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).text(0) == "Page 1"
    assert tv.topLevelItem(0).child(0).child(0).childCount() == 0
    assert tv.topLevelItem(0).child(0).child(0).text(0) == "Question 1"
    assert len(gui_init.undo_stack) == 2
    # change the question type to 'Check'
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"
    QTest.mouseClick(gui_init.gui.questiontype, Qt.LeftButton)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "Matrix"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if type(layout.itemAt(row, 1)) == QWidgetItem:
            not_none_rows += 1
            assert layout.itemAt(row, 0).widget().text() in fields_per_type["Matrix"][0].keys()
            assert str(type(layout.itemAt(row, 1).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["Matrix"][0][layout.itemAt(row, 0).widget().text()] == \
                   'QPlainTextEdit' else fields_per_type["Matrix"][0][layout.itemAt(row, 0).widget().text()]
            if type(layout.itemAt(row, 1).widget()) == QLineEdit and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().text() == \
                       str(default_values[layout.itemAt(row, 0).widget().text()])
            elif type(layout.itemAt(row, 1).widget()) == QRadioButton and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().isChecked() == default_values[
                    layout.itemAt(row, 0).widget().text()]
    assert not_none_rows == len(fields_per_type["Matrix"][0].keys())
    assert len(gui_init.undo_stack) == 13  # 2 for creating page & question, 11 for choosing Matrix

    # Check structure
    structure = ConfigObj()  # {}
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    structure["Page 1"]["Question 1"] = {"type": "Matrix"}
    for key, value in default_values.items():
        if key in fields_per_type["Matrix"][0].keys():
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


# noinspection PyArgumentList
def test_answers(gui_load, qtbot):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    answers_pos = find_row_by_label(gui_load.gui.edit_layout, 'answers')

    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().setPlainText("[only one]")
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == "[only one]"
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == "[only one]"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == "[only one]"
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == "only one"  # listify already ran
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in child.buttongroups:
                assert len(bg.buttons()) == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    '''
    QTest.qWait(1000) # TODO
    for child in gui_load.gui.preview_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in child.buttongroups:
                assert len(bg.buttons()) == 1
    '''

    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().setPlainText("only one")
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == "only one"
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == "only one"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in child.buttongroups:
                assert len(bg.buttons()) == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    '''
    for child in gui_load.gui.preview_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in child.buttongroups:
                assert len(bg.buttons()) == 1
    '''

    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().setPlainText("[one, two, three]")
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == "[one, two, three]"
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == "[one, two, three]"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == ["one", "two", "three"]
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in child.buttongroups:
                assert len(bg.buttons()) == 3

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    '''
    for child in gui_load.gui.preview_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in child.buttongroups:
                assert len(bg.buttons()) == 3
    '''

    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().setPlainText("")
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == ""
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == ""
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == True
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)

    QTimer.singleShot(150, handle_dialog_warning)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in child.buttongroups:
                assert len(bg.buttons()) == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    '''
    for child in gui_load.gui.preview_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in child.buttongroups:
                assert len(bg.buttons()) == 1
    '''

    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().setPlainText("1, 2, 3, 4, 5")
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == "1, 2, 3, 4, 5"
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == "1, 2, 3, 4, 5"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    assert gui_load.structure["Page 1"]["Question 1"]["answers"] == (1, 2, 3, 4, 5)
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in child.buttongroups:
                assert len(bg.buttons()) == 5

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    gui_load.close()


# noinspection PyArgumentList
def test_start_id(gui_load, qtbot):
    if os.path.exists("./test/results/results_rm.csv"):
        os.remove("./test/results/results_rm.csv")

    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    answers_pos = find_row_by_label(gui_load.gui.edit_layout, 'start_answer_id')

    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().insert("99")
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == "99"
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_answer_id"] == "99"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == "99"
    assert gui_load.structure["Page 1"]["Question 1"]["start_answer_id"] == "99"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False

    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in range(len(child.buttongroups)):
                child.buttongroups[bg].buttons()[bg].click()

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_rm.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 6
    assert lines[0] == '1'  # participant number
    assert lines[1] == '99'  # first button in first row clicked, id starts with 99
    assert lines[2] == '100'  # second button in second row clicked, id starts with 99
    assert lines[3] == '[1, 2]'  # order
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[4])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[5])  # timestamp
    os.remove("./test/results/results_rm.csv")

    #  -------- -1 ---------
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    answers_pos = find_row_by_label(gui_load.gui.edit_layout, 'start_answer_id')

    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().insert("-1")
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == "-1"
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_answer_id"] == "-1"
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == "-1"
    assert gui_load.structure["Page 1"]["Question 1"]["start_answer_id"] == "-1"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    #  ---------0--------
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    answers_pos = find_row_by_label(gui_load.gui.edit_layout, 'start_answer_id')

    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().insert("0")
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == "0"
    gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_answer_id"] == "0"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Question 1"]["start_answer_id"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False

    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in range(len(child.buttongroups)):
                child.buttongroups[bg].buttons()[bg].click()

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)

    results = []
    with open('./test/results/results_rm.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 6
    assert lines[0] == '1'  # participant number
    assert lines[1] == '0'  # first button in first row clicked, id starts with 0
    assert lines[2] == '1'  # second button in second row clicked, id starts with 0
    assert lines[3] == '[1, 2]'  # order
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[4])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[5])  # timestamp
    os.remove("./test/results/results_rm.csv")
    gui_load.close()


# noinspection PyArgumentList
def test_questions(gui_load, qtbot):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    quest_pos = find_row_by_label(gui_load.gui.edit_layout, 'questions')

    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().setPlainText("[only one]")
    assert gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().text() == "[only one]"
    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["questions"] == "[only one]"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().text() == "[only one]"
    assert gui_load.structure["Page 1"]["Question 1"]["questions"] == "only one"  # listify already ran
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            assert len(child.buttongroups) == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().setPlainText("only one")
    assert gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().text() == "only one"
    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["questions"] == "only one"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            assert len(child.buttongroups) == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().setPlainText("[one, two, three]")
    assert gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().text() == "[one, two, three]"
    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["questions"] == "[one, two, three]"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    assert gui_load.structure["Page 1"]["Question 1"]["questions"] == ["one", "two", "three"]
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            assert len(child.buttongroups) == 3

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().setPlainText("")
    assert gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().text() == ""
    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["questions"] == ""
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == True
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)

    QTimer.singleShot(150, handle_dialog_warning)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            assert len(child.buttongroups) == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().setPlainText("I like it very much., I don't like it at all.")
    assert gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().text() == "I like it very much., I don't like it at all."
    gui_load.gui.edit_layout.itemAt(quest_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["questions"] == "I like it very much., I don't like it at all."
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    assert gui_load.structure["Page 1"]["Question 1"]["questions"] == ["I like it very much.", "I don't like it at all."]
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rmtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            assert len(child.buttongroups) == 2

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    if os.path.exists("./test/results/results_rm.csv"):
        os.remove("./test/results/results_rm.csv")
    assert run.Stack.count() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_rm.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'rm_1'  # first row
                assert lines[2] == 'rm_2'  # second row
                assert lines[3] == 'rm_order'  # second row
                assert lines[4] == 'Start'
                assert lines[5] == 'End'
    assert len(results) == 6
    assert lines[0] == '1'  # participant number
    assert lines[1] == '-1'  # no radiobutton checked
    assert lines[2] == '-1'  # no radiobutton checked
    assert lines[3] == '[1, 2]'  # order
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[4])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[5])  # timestamp
    os.remove("./test/results/results_rm.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_blocked(run, qtbot):
    with mock_file(r'./test/results/results_rm.csv'):
        assert run.Stack.count() == 1
        QTimer.singleShot(100, handle_dialog)
        QTest.mouseClick(run.forwardbutton, Qt.LeftButton)
        res_file = None
        for file in os.listdir("./test/results/"):
            if file.find("_backup_"):
                res_file = "./test/results/{}".format(file)
        results = []
        with open(res_file, mode='r') as file:
            csv_file = csv.reader(file, delimiter=';')

            for lines in csv_file:
                results = lines
                if results[0].startswith('data'):
                    assert lines[0] == 'data_row_number'  # participant number
                    assert lines[1] == 'rm_1'  # first row
                    assert lines[2] == 'rm_2'  # second row
                    assert lines[3] == 'rm_order'  # second row
                    assert lines[4] == 'Start'
                    assert lines[5] == 'End'
        assert len(results) == 6
        assert lines[0] == '-1'  # participant number unknown
        assert lines[1] == '-1'  # no radiobutton checked
        assert lines[2] == '-1'  # no radiobutton checked
        assert lines[3] == '[1, 2]'  # order
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[4])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[5])  # timestamp
        os.remove(res_file)


# noinspection PyArgumentList
def test_execute_questionnaire(run, qtbot):
    if os.path.exists("./test/results/results_rm.csv"):
        os.remove("./test/results/results_rm.csv")
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in range(len(child.buttongroups)):
                child.buttongroups[bg].button(bg).click()

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton, delay=1)

    results = []
    with open('./test/results/results_rm.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 6
    assert lines[0] == '1'  # participant number
    assert lines[1] == '0'  # first button in first row clicked, id starts with 0
    assert lines[2] == '1'  # second button in second row clicked, id starts with 0
    assert lines[3] == '[1, 2]'  # order
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[4])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[5])  # timestamp
    os.remove("./test/results/results_rm.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_blocked(run, qtbot):
    with mock_file(r'./test/results/results_rm.csv'):
        assert run.Stack.count() == 1
        for child in run.Stack.currentWidget().children():
            if type(child) == RadioMatrix.RadioMatrix:
                for bg in range(len(child.buttongroups)):
                    child.buttongroups[bg].button(bg).click()
        QTimer.singleShot(100, handle_dialog)
        QTest.mouseClick(run.forwardbutton, Qt.LeftButton)
        res_file = None
        for file in os.listdir("./test/results/"):
            if file.find("_backup_"):
                res_file = "./test/results/{}".format(file)
        results = []
        with open(res_file, mode='r') as file:
            csv_file = csv.reader(file, delimiter=';')

            for lines in csv_file:
                results = lines
                if results[0].startswith('data'):
                    assert lines[0] == 'data_row_number'  # participant number
                    assert lines[1] == 'rm_1'  # first row
                    assert lines[2] == 'rm_2'  # second row
                    assert lines[3] == 'rm_order'  # second row
                    assert lines[4] == 'Start'
                    assert lines[5] == 'End'
        assert len(results) == 6
        assert lines[0] == '-1'  # participant number unknown
        assert lines[1] == '0'
        assert lines[2] == '1'
        assert lines[3] == '[1, 2]'  # order
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[4])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[5])  # timestamp
        os.remove(res_file)


# noinspection PyArgumentList
def test_two_pages(run_2, qtbot):
    if os.path.exists("./test/results/results_rm.csv"):
        os.remove("./test/results/results_rm.csv")
    assert run_2.Stack.count() == 2

    QTest.mouseClick(run_2.forwardbutton, Qt.LeftButton)
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run_2.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_rm.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'rm_1'  # first row
                assert lines[2] == 'rm_2'  # second row
                assert lines[3] == 'rm_order'  # second row
                assert lines[4] == 'rm2_1'  # first row
                assert lines[5] == 'rm2_2'  # second row
                assert lines[6] == 'rm2_order'  # second row
                assert lines[7] == 'Start'
                assert lines[8] == 'End'
    assert len(results) == 9
    assert lines[0] == '1'  # participant number
    assert lines[1] == '-1'  # no radiobutton checked
    assert lines[2] == '-1'  # no radiobutton checked
    assert lines[3] == '[1, 2]'  # order
    assert lines[4] == '-1'  # no radiobutton checked
    assert lines[5] == '-1'  # no radiobutton checked
    assert lines[6] == '[1, 2]'  # order
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[7])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[8])  # timestamp
    os.remove("./test/results/results_rm.csv")


# noinspection PyArgumentList
def test_randomize(gui_load_2, qtbot):
    if os.path.exists("./test/results/results_rm.csv"):
        os.remove("./test/results/results_rm.csv")

    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load_2.structure)
    assert error_found == False
    assert warning_found == False
    tv = gui_load_2.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    answers_pos = find_row_by_label(gui_load_2.gui.edit_layout, 'randomize')

    gui_load_2.gui.edit_layout.itemAt(answers_pos, 1).widget().click()
    assert gui_load_2.gui.edit_layout.itemAt(answers_pos, 1).widget().isChecked() == True
    assert gui_load_2.structure["Page 1"]["Question 1"]["randomize"] == True
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load_2.structure)
    assert error_found == False
    assert warning_found == False

    tv.setCurrentItem(tv.topLevelItem(0).child(1).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    answers_pos = find_row_by_label(gui_load_2.gui.edit_layout, 'randomize')

    gui_load_2.gui.edit_layout.itemAt(answers_pos, 1).widget().click()
    assert gui_load_2.gui.edit_layout.itemAt(answers_pos, 1).widget().isChecked() == True
    assert gui_load_2.structure["Page 2"]["Question 1"]["randomize"] == True
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load_2.structure)
    assert error_found == False
    assert warning_found == False

    QTest.keyClicks(gui_load_2, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rm_two_pages.txt")
    assert test_gui.Stack.count() == 2
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in range(len(child.buttongroups)):
                child.buttongroups[bg].buttons()[bg].click()
            questions1 = child.questions
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in range(len(child.buttongroups)):
                child.buttongroups[bg].buttons()[bg].click()
            questions2 = child.questions
    for quest in range(len(questions1)):
        assert questions2[quest].text() == questions1[quest].text()

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_rm.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 9
    assert lines[0] == '1'  # participant number
    assert lines[1] == lines[4]
    assert lines[2] == lines[5]
    assert lines[3] == lines[6]  # order
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[7])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[8])  # timestamp
    os.remove("./test/results/results_rm.csv")

    #  --set to False --
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load_2.structure)
    assert error_found == False
    assert warning_found == False
    tv = gui_load_2.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    answers_pos = find_row_by_label(gui_load_2.gui.edit_layout, 'randomize')

    gui_load_2.gui.edit_layout.itemAt(answers_pos, 1).widget().click()
    assert gui_load_2.gui.edit_layout.itemAt(answers_pos, 1).widget().isChecked() == False
    assert gui_load_2.structure["Page 1"]["Question 1"]["randomize"] == False
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load_2.structure)
    assert error_found == False
    assert warning_found == False

    tv.setCurrentItem(tv.topLevelItem(0).child(1).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    answers_pos = find_row_by_label(gui_load_2.gui.edit_layout, 'randomize')

    gui_load_2.gui.edit_layout.itemAt(answers_pos, 1).widget().click()
    assert gui_load_2.gui.edit_layout.itemAt(answers_pos, 1).widget().isChecked() == False
    assert gui_load_2.structure["Page 2"]["Question 1"]["randomize"] == False
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load_2.structure)
    assert error_found == False
    assert warning_found == False

    QTest.keyClicks(gui_load_2, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/rm_two_pages.txt")
    assert test_gui.Stack.count() == 2
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in range(len(child.buttongroups)):
                child.buttongroups[bg].buttons()[bg].click()
            questions1 = child.questions
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == RadioMatrix.RadioMatrix:
            for bg in range(len(child.buttongroups)):
                child.buttongroups[bg].buttons()[bg].click()
            questions2 = child.questions
    for quest in range(len(questions1)):
        assert questions2[quest].text() == questions1[quest].text()

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_rm.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 9
    assert lines[0] == '1'  # participant number
    assert lines[1] == lines[4]
    assert lines[2] == lines[5]
    assert lines[3] == lines[6]  # order
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[7])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[8])  # timestamp
    os.remove("./test/results/results_rm.csv")
    gui_load_2.close()
