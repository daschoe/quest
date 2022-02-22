"""Testing the behaviour of PasswordEntry.py + QEditGui.py"""

from context import *


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file("./test/pwtest.txt"))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui("./test/pwtest.txt")


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
    # change the question type to 'Password'
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
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "Password"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if type(layout.itemAt(row, 1)) == QWidgetItem:
            not_none_rows += 1
            assert layout.itemAt(row, 0).widget().text() in fields_per_type["Password"][0].keys()
            assert str(type(layout.itemAt(row, 1).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["Password"][0][layout.itemAt(row, 0).widget().text()] == 'QPlainTextEdit'\
                   else fields_per_type["Password"][0][layout.itemAt(row, 0).widget().text()]
            if type(layout.itemAt(row, 1).widget()) == QLineEdit and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().text() == default_values[layout.itemAt(row, 0).widget().text()]
            elif type(layout.itemAt(row, 1).widget()) == QCheckBox and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().isChecked() == default_values[
                    layout.itemAt(row, 0).widget().text()]
        elif type(layout.itemAt(row, 1)) == QHBoxLayout and \
                gui_init.gui.pw_layout == layout.itemAt(row, 1):
            not_none_rows += 1
            assert layout.itemAt(row, 1).itemAt(1).widget().text() == default_values[
                layout.itemAt(row, 0).widget().text()]
    assert not_none_rows == len(fields_per_type["Password"][0].keys())
    assert len(gui_init.undo_stack) == 11  # 2 for creating page & question, 9 for choosing Password

    # Check structure
    structure = ConfigObj()  # {}
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    structure["Page 1"]["Question 1"] = {"type": "Password"}
    for key, value in default_values.items():
        if key in fields_per_type["Password"][0].keys():
            structure["Page 1"]["Question 1"][key] = value
    listify(gui_init.structure)
    listify(structure)

    QTimer.singleShot(100, handle_dialog_error)
    validate_questionnaire(gui_init.structure, suppress=True)
    QTimer.singleShot(100, handle_dialog_error)
    validate_questionnaire(structure, suppress=True)

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
def test_password_file(gui_load, run, qtbot):
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"
    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    pw_str = find_row_by_label(gui_load.gui.edit_layout, 'password_file')
    pwfile = gui_load.gui.edit_layout.itemAt(pw_str[0], 1).itemAt(pw_str[1]).widget().text()
    with open(pwfile) as f:
        passwords = f.read().splitlines()
    for child in run.Stack.currentWidget().children():
        if type(child) == PasswordEntry:
            assert child.passwords == passwords

    def handle_file_chooser():
        """Type filename."""
        keyboard.write("mock_pws_int.txt")
        keyboard.press("enter")

    pw_btn = gui_load.gui.edit_layout.itemAt(find_row_by_label(gui_load.gui.edit_layout, 'password_file_btn')[0], 1).itemAt(0).widget()
    QTimer.singleShot(100, handle_file_chooser)
    QTest.mouseClick(pw_btn, Qt.MouseButton.LeftButton)

    pwfile = gui_load.gui.edit_layout.itemAt(pw_str[0], 1).itemAt(pw_str[1]).widget().text()
    assert pwfile.endswith("mock_pws_int.txt")
    with open(pwfile) as f:
        passwords = f.read().splitlines()
        assert passwords is not None
    QTimer.singleShot(150, handle_dialog_no_save)
    gui_load.close()


# noinspection PyArgumentList
def test_policy(gui_load, qtbot):
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
    pw_str = find_row_by_label(gui_load.gui.edit_layout, 'password_file')
    pwfile = gui_load.gui.edit_layout.itemAt(pw_str[0], 1).itemAt(pw_str[1]).widget()
    answers_pos = find_row_by_label(gui_load.gui.edit_layout, 'policy')
    policy_cb = gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget()
    assert policy_cb.currentText() == 'None'
    assert find_row_by_label(gui_load.gui.edit_layout, "min") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "max") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") is None
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pwtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == PasswordEntry:
            assert child.validator() is None
    test_gui.close()

    QTest.mouseClick(policy_cb, Qt.LeftButton)
    QTest.keyClick(policy_cb, Qt.Key_Down)
    QTest.keyClick(policy_cb, Qt.Key_Enter)
    assert policy_cb.currentText() == "int"
    assert find_row_by_label(gui_load.gui.edit_layout, "min") == (answers_pos+1, 1)
    assert find_row_by_label(gui_load.gui.edit_layout, "max") == (answers_pos+1, 3)
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") is None
    min_b = find_row_by_label(gui_load.gui.edit_layout, "min")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(min_b[0], 1).itemAt(min_b[1]).widget(), '1000')
    gui_load.gui.edit_layout.itemAt(min_b[0], 1).itemAt(min_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(min_b[0], 1).itemAt(min_b[1]).widget().text() == '1000'
    max_b = find_row_by_label(gui_load.gui.edit_layout, "max")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(max_b[0], 1).itemAt(max_b[1]).widget(), '9999')
    gui_load.gui.edit_layout.itemAt(max_b[0], 1).itemAt(max_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(max_b[0], 1).itemAt(max_b[1]).widget().text() == '9999'
    gui_load.structure["Page 1"]["Question 1"]["password_file"] = "./test/mock_pws_int.txt"
    pwfile.setText("./test/mock_pws_int.txt")
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["policy"] == ['int', '1000', '9999']
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pwtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == PasswordEntry:
            assert type(child.validator()) == QIntValidator
    test_gui.close()

    QTest.mouseClick(policy_cb, Qt.LeftButton)
    QTest.keyClick(policy_cb, Qt.Key_Down)
    QTest.keyClick(policy_cb, Qt.Key_Enter)
    assert policy_cb.currentText() == "double"
    assert find_row_by_label(gui_load.gui.edit_layout, "min") == (answers_pos+1, 1)
    assert find_row_by_label(gui_load.gui.edit_layout, "max") == (answers_pos+1, 3)
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") == (answers_pos+1, 5)
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") is None
    min_b = find_row_by_label(gui_load.gui.edit_layout, "min")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(min_b[0], 1).itemAt(min_b[1]).widget(), '1')
    gui_load.gui.edit_layout.itemAt(min_b[0], 1).itemAt(min_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(min_b[0], 1).itemAt(min_b[1]).widget().text() == '1'
    max_b = find_row_by_label(gui_load.gui.edit_layout, "max")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(max_b[0], 1).itemAt(max_b[1]).widget(), '100')
    gui_load.gui.edit_layout.itemAt(max_b[0], 1).itemAt(max_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(max_b[0], 1).itemAt(max_b[1]).widget().text() == '100'
    dec_b = find_row_by_label(gui_load.gui.edit_layout, "dec")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(dec_b[0], 1).itemAt(dec_b[1]).widget(), '2')
    gui_load.gui.edit_layout.itemAt(dec_b[0], 1).itemAt(dec_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(dec_b[0], 1).itemAt(dec_b[1]).widget().text() == '2'
    gui_load.structure["Page 1"]["Question 1"]["password_file"] = "./test/mock_pws_double.txt"
    pwfile.setText("./test/mock_pws_double.txt")
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["policy"] == ['double', '1', '100', '2']
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pwtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == PasswordEntry:
            assert type(child.validator()) == QDoubleValidator
    test_gui.close()

    QTest.mouseClick(policy_cb, Qt.LeftButton)
    QTest.keyClick(policy_cb, Qt.Key_Down)
    QTest.keyClick(policy_cb, Qt.Key_Enter)
    assert policy_cb.currentText() == "regex"
    assert find_row_by_label(gui_load.gui.edit_layout, "min") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "max") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") == (answers_pos + 1, 1)
    exp_b = find_row_by_label(gui_load.gui.edit_layout, "exp")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(exp_b[0], 1).itemAt(exp_b[1]).widget(), '[A-Z]\\d')
    gui_load.gui.edit_layout.itemAt(exp_b[0], 1).itemAt(exp_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(exp_b[0], 1).itemAt(exp_b[1]).widget().text() == '[A-Z]\\d'
    gui_load.structure["Page 1"]["Question 1"]["password_file"] = "./test/mock_pws_regex.txt"
    pwfile.setText("./test/mock_pws_regex.txt")
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["policy"] == ['regex', '[A-Z]\\d']
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pwtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == PasswordEntry:
            assert type(child.validator()) == QRegExpValidator
    test_gui.close()

    QTest.mouseClick(policy_cb, Qt.LeftButton)
    QTest.keyClick(policy_cb, Qt.Key_Up)
    QTest.keyClick(policy_cb, Qt.Key_Up)
    QTest.keyClick(policy_cb, Qt.Key_Up)
    QTest.keyClick(policy_cb, Qt.Key_Enter)
    assert policy_cb.currentText() == 'None'
    assert find_row_by_label(gui_load.gui.edit_layout, "min") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "max") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") is None
    gui_load.structure["Page 1"]["Question 1"]["password_file"] = "./test/mock_pws.txt"
    pwfile.setText("./test/mock_pws.txt")
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    if os.path.exists("./test/results/results_pw.csv"):
        os.remove("./test/results/results_pw.csv")
    assert run.Stack.count() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_pw.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'pw'
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == ''
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_pw.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_type_pw(run, qtbot):
    if os.path.exists("./test/results/results_pw.csv"):
        os.remove("./test/results/results_pw.csv")
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if type(child) is PasswordEntry:
            assert child.text() == ''
            QTest.keyClicks(child, "wrong", modifier=Qt.NoModifier, delay=1)
            assert child.text() == 'wrong'
            assert child.validate() == False
            assert child.toolTip() == "Invalid password."
            assert child.objectName() == 'required'
            # assert child.palette().color(6).name() == 'red'
            child.clear()
            QTest.keyClicks(child, "password", modifier=Qt.NoModifier, delay=1)
            assert child.text() == 'password'
            assert child.validate() == True
            assert child.toolTip() == ""
            assert child.objectName() == ''

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_pw.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'pw'
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == 'password'
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_pw.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_type_wrong_pw(run, qtbot):
    if os.path.exists("./test/results/results_pw.csv"):
        os.remove("./test/results/results_pw.csv")
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if type(child) is PasswordEntry:
            assert child.text() == ''
            QTest.keyClicks(child, "wrong", modifier=Qt.NoModifier, delay=1)
            assert child.text() == 'wrong'
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)
    for child in run.Stack.currentWidget().children():
        if type(child) is PasswordEntry:
            assert child.text() == 'wrong'
            assert child.toolTip() == "Invalid password."
            assert child.objectName() == 'required'
            assert child.palette().color(6).name() == '#ff0000'  # == red
            child.clear()
            QTest.keyClicks(child, "password", modifier=Qt.NoModifier, delay=1)
            assert child.text() == 'password'
            assert child.validate() == True
            assert child.toolTip() == ""
            assert child.objectName() == ''

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_pw.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'pw'
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == 'password'
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_pw.csv")
