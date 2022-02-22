"""Testing the behaviour of AnswerTextField.py + QEditGui.py"""

from context import *


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file("./test/tftest.txt"))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui("./test/tftest.txt")


# noinspection PyArgumentList
def test_create(gui_init, qtbot):
    # create a page
    assert gui_init.gui.page_add.isEnabled() == True
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_p)
    QTest.mouseClick(gui_init.gui.page_add, Qt.LeftButton, delay=1)
    tv = gui_init.gui.treeview
    # create a question
    tv.setCurrentItem(tv.topLevelItem(0).child(0))
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
    # change the question type to 'Text'
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"
    QTest.mouseClick(gui_init.gui.questiontype, Qt.LeftButton)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "Text"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if type(layout.itemAt(row, 1)) == QWidgetItem:
            not_none_rows += 1
            assert layout.itemAt(row, 0).widget().text() in fields_per_type["Text"][0].keys()
            assert str(type(layout.itemAt(row, 1).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["Text"][0][layout.itemAt(row, 0).widget().text()] == 'QPlainTextEdit'\
                   else fields_per_type["Text"][0][layout.itemAt(row, 0).widget().text()]
            if type(layout.itemAt(row, 1).widget()) == QLineEdit and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().text() == default_values[layout.itemAt(row, 0).widget().text()]
            elif type(layout.itemAt(row, 1).widget()) == QCheckBox and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().isChecked() == default_values[
                    layout.itemAt(row, 0).widget().text()]
        elif type(layout.itemAt(row, 1)) == QHBoxLayout and layout.itemAt(row, 1).count() > 0:
            not_none_rows += 1
            assert layout.itemAt(row, 0).widget().text() in fields_per_type["Text"][0].keys()
            for cnt in range(layout.itemAt(row, 1).count()):
                if type(layout.itemAt(row, 1).itemAt(cnt).widget()) == QRadioButton:
                    assert layout.itemAt(row, 1).itemAt(cnt).widget().group().checkedId() + 1 == \
                           default_values[layout.itemAt(row, 0).widget().text()]
    assert not_none_rows == len(fields_per_type["Text"][0].keys())
    assert len(gui_init.undo_stack) == 7  # 2 for creating page & question, 5 for choosing Text

    # Check structure
    structure = ConfigObj()  # {}
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    structure["Page 1"]["Question 1"] = {"type": "Text"}
    for key, value in default_values.items():
        if key in fields_per_type["Text"][0].keys():
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
    answers_pos = find_row_by_label(gui_load.gui.edit_layout, 'policy')
    policy_cb = gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget()
    assert policy_cb.currentText() == 'None'
    assert find_row_by_label(gui_load.gui.edit_layout, "min") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "max") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") is None
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/tftest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QLineEdit:
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
    hboxes = gui_load.gui.edit_layout.findChildren(QHBoxLayout)
    hbox = None
    for box in hboxes:
        if type(box.itemAt(1).widget()) == QLineEdit:
            hbox = box
    QTest.keyClicks(hbox.itemAt(1).widget(), '1')
    hbox.itemAt(1).widget().editingFinished.emit()
    assert hbox.itemAt(1).widget().text() == '1'
    QTest.keyClicks(hbox.itemAt(3).widget(), '100')
    hbox.itemAt(3).widget().editingFinished.emit()
    assert hbox.itemAt(3).widget().text() == '100'
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["policy"] == ['int', '1', '100']
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/tftest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QLineEdit:
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
    hboxes = gui_load.gui.edit_layout.findChildren(QHBoxLayout)
    for box in hboxes:
        if type(box.itemAt(1).widget()) == QLineEdit:
            hbox = box
    QTest.keyClicks(hbox.itemAt(1).widget(), '1')
    hbox.itemAt(1).widget().editingFinished.emit()
    assert hbox.itemAt(1).widget().text() == '1'
    QTest.keyClicks(hbox.itemAt(3).widget(), '100')
    hbox.itemAt(3).widget().editingFinished.emit()
    assert hbox.itemAt(3).widget().text() == '100'
    QTest.keyClicks(hbox.itemAt(5).widget(), '2')
    hbox.itemAt(5).widget().editingFinished.emit()
    assert hbox.itemAt(5).widget().text() == '2'
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["policy"] == ['double', '1', '100', '2']
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/tftest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QLineEdit:
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
    hboxes = gui_load.gui.edit_layout.findChildren(QHBoxLayout)
    for box in hboxes:
        if type(box.itemAt(1).widget()) == QLineEdit:
            hbox = box
    QTest.keyClicks(hbox.itemAt(1).widget(), '[A-Z]')
    hbox.itemAt(1).widget().editingFinished.emit()
    assert hbox.itemAt(1).widget().text() == '[A-Z]'
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["policy"] == ['regex', '[A-Z]']
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/tftest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QLineEdit:
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
    assert gui_load.structure["Page 1"]["Question 1"]["size"] == '1'
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    gui_load.save()
    gui_load.close()
    QTest.qWait(500)


# noinspection PyArgumentList
def test_policy_enable(gui_load, qtbot):
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
    answers_pos = find_row_by_label(gui_load.gui.edit_layout, 'policy')
    policy_cb = gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget()
    assert policy_cb.currentText() == 'None'
    assert find_row_by_label(gui_load.gui.edit_layout, "min") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "max") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") is None

    hboxes = gui_load.gui.edit_layout.findChildren(QHBoxLayout)
    hbox = None
    for box in hboxes:
        if box.count() > 0 and type(box.itemAt(0).widget()) == QRadioButton:
            hbox = box
    assert type(hbox.itemAt(1).widget()) == QRadioButton
    assert hbox.findChild(QButtonGroup).checkedId() == 0
    assert hbox.itemAt(1).widget().isChecked() == False
    hbox.itemAt(1).widget().click()
    assert hbox.itemAt(1).widget().isChecked() == True
    assert hbox.findChild(QButtonGroup).checkedId() == 1
    assert policy_cb.currentText() == 'None'
    assert policy_cb.isEnabled() == False

    hbox.itemAt(0).widget().click()
    assert hbox.itemAt(0).widget().isChecked() == True
    assert policy_cb.currentText() == 'None'
    assert policy_cb.isEnabled() == True
    QTest.mouseClick(policy_cb, Qt.LeftButton)
    QTest.keyClick(policy_cb, Qt.Key_Down)
    QTest.keyClick(policy_cb, Qt.Key_Enter)
    assert policy_cb.currentText() == "int"
    assert find_row_by_label(gui_load.gui.edit_layout, "min") == (answers_pos + 1, 1)
    assert find_row_by_label(gui_load.gui.edit_layout, "max") == (answers_pos + 1, 3)
    assert find_row_by_label(gui_load.gui.edit_layout, "dec") is None
    assert find_row_by_label(gui_load.gui.edit_layout, "exp") is None

    hbox.itemAt(1).widget().click()
    assert hbox.itemAt(1).widget().isChecked() == True
    assert hbox.findChild(QButtonGroup).checkedId() == 1
    assert policy_cb.currentText() == 'None'
    assert policy_cb.isEnabled() == False

    hbox.itemAt(0).widget().click()
    assert hbox.itemAt(0).widget().isChecked() == True
    assert hbox.findChild(QButtonGroup).checkedId() == 0
    assert policy_cb.currentText() == 'None'
    assert policy_cb.isEnabled() == True
    assert gui_load.structure["Page 1"]["Question 1"]["size"] == 1
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    gui_load.save()
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    if os.path.exists("./test/results/results_tf.csv"):
        os.remove("./test/results/results_tf.csv")
    assert run.Stack.count() == 1
    found_le = False
    found_te = False
    for child in run.Stack.currentWidget().children():
        if type(child) == QLineEdit:
            found_le = True
        elif type(child) == QPlainTextEdit:
            found_te = True
    assert found_le == True
    assert found_te == False

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_tf.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'tf'
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == ''
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_tf.csv")


# noinspection PyArgumentList
def test_execute_questionnaire(run, qtbot):
    if os.path.exists("./test/results/results_tf.csv"):
        os.remove("./test/results/results_tf.csv")
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if type(child) is QLineEdit:
            assert child.text() == ''
            QTest.keyClicks(child, "texttext", modifier=Qt.NoModifier, delay=1)
            assert child.text() == 'texttext'

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_tf.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'tf'
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == 'texttext'
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_tf.csv")


# noinspection PyArgumentList
def test_execute_textedit(gui_load, qtbot):
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
    answers_pos = find_row_by_label(gui_load.gui.edit_layout, 'policy')
    policy_cb = gui_load.gui.edit_layout.itemAt(answers_pos, 1).widget()
    hboxes = gui_load.gui.edit_layout.findChildren(QHBoxLayout)
    hbox = None
    for box in hboxes:
        if box.count() > 0 and type(box.itemAt(0).widget()) == QRadioButton:
            hbox = box
    assert type(hbox.itemAt(1).widget()) == QRadioButton
    assert hbox.findChild(QButtonGroup).checkedId() == 0
    assert hbox.itemAt(1).widget().isChecked() == False
    hbox.itemAt(1).widget().click()
    assert hbox.itemAt(1).widget().isChecked() == True
    assert hbox.findChild(QButtonGroup).checkedId() == 1
    assert policy_cb.currentText() == 'None'
    assert policy_cb.isEnabled() == False

    if os.path.exists("./test/results/results_tf.csv"):
        os.remove("./test/results/results_tf.csv")
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/tftest.txt")

    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) is QPlainTextEdit:
            assert child.toPlainText() == ''
            QTest.keyClicks(child, "texttext", modifier=Qt.NoModifier, delay=1)
            assert child.toPlainText() == 'texttext'

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_tf.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'tf'
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == 'texttext'
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_tf.csv")

    assert hbox.findChild(QButtonGroup).checkedId() == 1
    assert hbox.itemAt(1).widget().isChecked() == True
    hbox.itemAt(0).widget().click()
    assert hbox.itemAt(0).widget().isChecked() == True
    assert hbox.findChild(QButtonGroup).checkedId() == 0
    assert policy_cb.currentText() == 'None'
    assert policy_cb.isEnabled() == True
    gui_load.gui.refresh_button.click()
    assert hbox.itemAt(0).widget().isChecked() == True
    assert hbox.findChild(QButtonGroup).checkedId() == 0
    assert policy_cb.currentText() == 'None'
    assert policy_cb.isEnabled() == True
    assert gui_load.structure['Page 1']['Question 1']['size'] == 1
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    gui_load.save()
    gui_load.close()
