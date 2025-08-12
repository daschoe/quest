"""Testing the behaviour of PasswordEntry.py + QEditGui.py"""

from tests.context import pytest, QEditGuiMain, PasswordEntry, QHBoxLayout, keyboard, QIntValidator, QDoubleValidator, QRegularExpressionValidator, QPalette, QTimer, open_config_file, StackedWindowGui, QTest, handle_dialog_p, handle_dialog_q, Qt, QFormLayout, QWidgetItem, fields_per_type, default_values, QCheckBox, QLineEdit, page_fields, listify, ConfigObj, general_fields, handle_dialog_error, validate_questionnaire, handle_dialog_no_save, find_row_by_label, handle_dialog, csv, re, os, mock_file


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file(os.path.join(os.getcwd(), "tests/pwtest.txt")))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui(os.path.join(os.getcwd(), "tests/pwtest.txt"))


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
    # change the question type to 'Password'
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
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "Password"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QWidgetItem):
            not_none_rows += 1
            assert layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in fields_per_type["Password"][0]
            assert str(type(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["Password"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()] == 'QPlainTextEdit'\
                   else fields_per_type["Password"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
            if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QLineEdit) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().text() == default_values[layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
            elif isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QCheckBox) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().isChecked() == default_values[
                    layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
        elif isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QHBoxLayout) and \
                gui_init.gui.pw_layout == layout.itemAt(row, QFormLayout.ItemRole.FieldRole):
            not_none_rows += 1
            assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).itemAt(1).widget().text() == default_values[
                layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
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
        if key in fields_per_type["Password"][0]:
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
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())
    pw_str = find_row_by_label(gui_load.gui.edit_layout, 'password_file')
    pwfile = gui_load.gui.edit_layout.itemAt(pw_str[0], QFormLayout.ItemRole.FieldRole).itemAt(pw_str[1]).widget().text()
    with open(pwfile) as f:
        passwords = f.read().splitlines()
    for child in run.Stack.currentWidget().children():
        if isinstance(child, PasswordEntry):
            assert child.passwords == passwords

    def handle_file_chooser():
        """Type filename."""
        keyboard.write("mock_pws_int.txt")
        keyboard.press("enter")

    pw_btn = gui_load.gui.edit_layout.itemAt(find_row_by_label(gui_load.gui.edit_layout, 'password_file_btn')[0], QFormLayout.ItemRole.FieldRole).itemAt(0).widget()
    QTimer.singleShot(100, handle_file_chooser)
    QTest.mouseClick(pw_btn, Qt.MouseButton.LeftButton)

    pwfile = gui_load.gui.edit_layout.itemAt(pw_str[0], QFormLayout.ItemRole.FieldRole).itemAt(pw_str[1]).widget().text()
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
    assert not error_found
    assert not warning_found
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())
    pw_str = find_row_by_label(gui_load.gui.edit_layout, 'password_file')
    pwfile = gui_load.gui.edit_layout.itemAt(pw_str[0], QFormLayout.ItemRole.FieldRole).itemAt(pw_str[1]).widget()
    answers_pos = find_row_by_label(gui_load.gui.edit_layout, 'policy')
    policy_cb = gui_load.gui.edit_layout.itemAt(answers_pos, QFormLayout.ItemRole.FieldRole).widget()
    assert policy_cb.currentText() == 'None'
    assert find_row_by_label(gui_load.gui.edit_layout, "min") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "max") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") is None
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/pwtest.txt"))
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, PasswordEntry):
            assert child.validator() is None
    test_gui.close()

    QTest.mouseClick(policy_cb, Qt.MouseButton.LeftButton, delay=1000)
    QTest.keyClick(policy_cb, Qt.Key.Key_Down, delay=1000)
    QTest.keyClick(policy_cb, Qt.Key.Key_Enter, delay=1000)
    assert policy_cb.currentText() == "int"
    policy_cb.clearFocus()
    gui_load.gui.setFocus()
    assert find_row_by_label(gui_load.gui.edit_layout, "min") == (answers_pos + 1, 1)
    assert find_row_by_label(gui_load.gui.edit_layout, "max") == (answers_pos + 1, 3)
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") is None
    min_b = find_row_by_label(gui_load.gui.edit_layout, "min")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(min_b[0], QFormLayout.ItemRole.FieldRole).itemAt(min_b[1]).widget(), '1000')
    gui_load.gui.edit_layout.itemAt(min_b[0], QFormLayout.ItemRole.FieldRole).itemAt(min_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(min_b[0], QFormLayout.ItemRole.FieldRole).itemAt(min_b[1]).widget().text() == '1000'
    max_b = find_row_by_label(gui_load.gui.edit_layout, "max")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(max_b[0], QFormLayout.ItemRole.FieldRole).itemAt(max_b[1]).widget(), '9999')
    gui_load.gui.edit_layout.itemAt(max_b[0], QFormLayout.ItemRole.FieldRole).itemAt(max_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(max_b[0], QFormLayout.ItemRole.FieldRole).itemAt(max_b[1]).widget().text() == '9999'
    gui_load.structure["Page 1"]["Question 1"]["password_file"] = os.path.join(os.getcwd(), "tests/mock_pws_int.txt")
    pwfile.setText(os.path.join(os.getcwd(), "tests/mock_pws_int.txt"))
    gui_load.gui.refresh_button.click()
    QTest.qWait(2000)
    assert gui_load.structure["Page 1"]["Question 1"]["policy"] == ['int', '1000', '9999']
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load.save() # have to enforce save since focus is lost somwhow....
    QTest.qWait(1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/pwtest.txt"))
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, PasswordEntry):
            assert isinstance(child.validator(), QIntValidator)
    test_gui.close()

    QTest.mouseClick(policy_cb, Qt.MouseButton.LeftButton, delay=1000)
    QTest.keyClick(policy_cb, Qt.Key.Key_Down, delay=1000)
    QTest.keyClick(policy_cb, Qt.Key.Key_Enter, delay=1000)
    assert policy_cb.currentText() == "double"
    assert find_row_by_label(gui_load.gui.edit_layout, "min") == (answers_pos + 1, 1)
    assert find_row_by_label(gui_load.gui.edit_layout, "max") == (answers_pos + 1, 3)
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") == (answers_pos + 1, 5)
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") is None
    min_b = find_row_by_label(gui_load.gui.edit_layout, "min")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(min_b[0], QFormLayout.ItemRole.FieldRole).itemAt(min_b[1]).widget(), '1')
    gui_load.gui.edit_layout.itemAt(min_b[0], QFormLayout.ItemRole.FieldRole).itemAt(min_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(min_b[0], QFormLayout.ItemRole.FieldRole).itemAt(min_b[1]).widget().text() == '1'
    max_b = find_row_by_label(gui_load.gui.edit_layout, "max")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(max_b[0], QFormLayout.ItemRole.FieldRole).itemAt(max_b[1]).widget(), '100')
    gui_load.gui.edit_layout.itemAt(max_b[0], QFormLayout.ItemRole.FieldRole).itemAt(max_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(max_b[0], QFormLayout.ItemRole.FieldRole).itemAt(max_b[1]).widget().text() == '100'
    dec_b = find_row_by_label(gui_load.gui.edit_layout, "dec")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(dec_b[0], QFormLayout.ItemRole.FieldRole).itemAt(dec_b[1]).widget(), '2')
    gui_load.gui.edit_layout.itemAt(dec_b[0], QFormLayout.ItemRole.FieldRole).itemAt(dec_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(dec_b[0], QFormLayout.ItemRole.FieldRole).itemAt(dec_b[1]).widget().text() == '2'
    gui_load.structure["Page 1"]["Question 1"]["password_file"] = os.path.join(os.getcwd(), "tests/mock_pws_double.txt")
    pwfile.setText(os.path.join(os.getcwd(), "tests/mock_pws_double.txt"))
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["policy"] == ['double', '1', '100', '2']
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load.save() # have to enforce save since focus is lost somwhow....
    QTest.qWait(1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/pwtest.txt"))
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, PasswordEntry):
            assert isinstance(child.validator(), QDoubleValidator)
    test_gui.close()

    QTest.mouseClick(policy_cb, Qt.MouseButton.LeftButton, delay=1000)
    QTest.keyClick(policy_cb, Qt.Key.Key_Down, delay=1000)
    QTest.keyClick(policy_cb, Qt.Key.Key_Enter, delay=1000)
    assert policy_cb.currentText() == "regex"
    assert find_row_by_label(gui_load.gui.edit_layout, "min") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "max") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") == (answers_pos + 1, 1)
    exp_b = find_row_by_label(gui_load.gui.edit_layout, "exp")
    QTest.keyClicks(gui_load.gui.edit_layout.itemAt(exp_b[0], QFormLayout.ItemRole.FieldRole).itemAt(exp_b[1]).widget(), '[A-Z]\\d')
    gui_load.gui.edit_layout.itemAt(exp_b[0], QFormLayout.ItemRole.FieldRole).itemAt(exp_b[1]).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(exp_b[0], QFormLayout.ItemRole.FieldRole).itemAt(exp_b[1]).widget().text() == '[A-Z]\\d'
    gui_load.structure["Page 1"]["Question 1"]["password_file"] = os.path.join(os.getcwd(), "tests/mock_pws_regex.txt")
    pwfile.setText(os.path.join(os.getcwd(), "tests/mock_pws_regex.txt"))
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["policy"] == ['regex', '[A-Z]\\d']
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load.save() # have to enforce save since focus is lost somwhow....
    QTest.qWait(2000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/pwtest.txt"))
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, PasswordEntry):
            assert isinstance(child.validator(), QRegularExpressionValidator)
    test_gui.close()

    QTest.mouseClick(policy_cb, Qt.MouseButton.LeftButton, delay=1000)
    QTest.keyClick(policy_cb, Qt.Key.Key_Up)
    QTest.keyClick(policy_cb, Qt.Key.Key_Up)
    QTest.keyClick(policy_cb, Qt.Key.Key_Up)
    QTest.keyClick(policy_cb, Qt.Key.Key_Enter, delay=1000)
    assert policy_cb.currentText() == 'None'
    assert find_row_by_label(gui_load.gui.edit_layout, "min") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "max") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") is None
    gui_load.structure["Page 1"]["Question 1"]["password_file"] = os.path.join(os.getcwd(), "tests/mock_pws.txt")
    pwfile.setText(os.path.join(os.getcwd(), "tests/mock_pws.txt"))
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load.save() # have to enforce save since focus is lost somwhow....
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    if os.path.exists("./tests/results/results_pw.csv"):
        os.remove("./tests/results/results_pw.csv")
    assert run.Stack.count() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)

    results = []
    with open('./tests/results/results_pw.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert results[0] == 'data_row_number'  # participant number
                assert results[1] == 'pw'
                assert results[2] == 'Start'
                assert results[3] == 'End'
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == ''
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    os.remove("./tests/results/results_pw.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_blocked(run, qtbot):
    with mock_file(r'./tests/results/results_pw.csv'):
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
                    assert results[1] == 'pw'
                    assert results[2] == 'Start'
                    assert results[3] == 'End'
        assert len(results) == 4
        assert results[0] == '-1'  # participant number unknown
        assert results[1] == ''
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
        os.remove(res_file)


# noinspection PyArgumentList
def test_execute_questionnaire_type_pw(run, qtbot):
    if os.path.exists("./tests/results/results_pw.csv"):
        os.remove("./tests/results/results_pw.csv")
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if isinstance(child, PasswordEntry):
            assert child.text() == ''
            QTest.keyClicks(child, "wrong", modifier=Qt.KeyboardModifier.NoModifier, delay=500)
            assert child.text() == 'wrong'
            assert not child.validate()
            assert child.toolTip() == "Invalid password."
            assert child.objectName() == 'required'
            # assert child.palette().color(QPalette.Text).name() == 'red'
            child.clear()
            QTest.keyClicks(child, "password", modifier=Qt.KeyboardModifier.NoModifier, delay=500)
            assert child.text() == 'password'
            assert child.validate()
            assert child.toolTip() == ""
            assert child.objectName() == ''

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)

    results = []
    with open('./tests/results/results_pw.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert results[0] == 'data_row_number'  # participant number
                assert results[1] == 'pw'
                assert results[2] == 'Start'
                assert results[3] == 'End'
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == 'password'
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    os.remove("./tests/results/results_pw.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_blocked(run, qtbot):
    with mock_file(r'./tests/results/results_pw.csv'):
        assert run.Stack.count() == 1
        for child in run.Stack.currentWidget().children():
            if isinstance(child, PasswordEntry):
                assert child.text() == ''
                QTest.keyClicks(child, "wrong", modifier=Qt.KeyboardModifier.NoModifier, delay=500)
                assert child.text() == 'wrong'
                assert not child.validate()
                assert child.toolTip() == "Invalid password."
                assert child.objectName() == 'required'
                # assert child.palette().color(QPalette.Text).name() == 'red'
                child.clear()
                QTest.keyClicks(child, "password", modifier=Qt.KeyboardModifier.NoModifier, delay=500)
                assert child.text() == 'password'
                assert child.validate()
                assert child.toolTip() == ""
                assert child.objectName() == ''
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
                    assert results[1] == 'pw'
                    assert results[2] == 'Start'
                    assert results[3] == 'End'
        assert len(results) == 4
        assert results[0] == '-1'  # participant number unknown
        assert results[1] == 'password'
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
        os.remove(res_file)


# noinspection PyArgumentList
def test_execute_questionnaire_type_wrong_pw(run, qtbot):
    if os.path.exists("./tests/results/results_pw.csv"):
        os.remove("./tests/results/results_pw.csv")
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if isinstance(child, PasswordEntry):
            assert child.text() == ''
            QTest.keyClicks(child, "wrong", modifier=Qt.KeyboardModifier.NoModifier, delay=500)
            assert child.text() == 'wrong'
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)
    for child in run.Stack.currentWidget().children():
        if isinstance(child, PasswordEntry):
            assert child.text() == 'wrong'
            assert child.toolTip() == "Invalid password."
            assert child.objectName() == 'required'
            assert child.palette().color(QPalette.Text).name() == '#ff0000'  # == red
            child.clear()
            QTest.keyClicks(child, "password", modifier=Qt.KeyboardModifier.NoModifier, delay=500)
            assert child.text() == 'password'
            assert child.validate()
            assert child.toolTip() == ""
            assert child.objectName() == ''

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)

    results = []
    with open('./tests/results/results_pw.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert results[0] == 'data_row_number'  # participant number
                assert results[1] == 'pw'
                assert results[2] == 'Start'
                assert results[3] == 'End'
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == 'password'
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    os.remove("./tests/results/results_pw.csv")
