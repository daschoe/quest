"""Testing the behaviour of AnswerSlider.py + QEditGui.py"""

from context import *


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file("./test/sltest.txt"))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui("./test/sltest.txt")


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
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "Slider"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if type(layout.itemAt(row, 1)) == QWidgetItem:
            not_none_rows += 1
            assert layout.itemAt(row, 0).widget().text() in fields_per_type["Slider"][0].keys()
            assert str(type(layout.itemAt(row, 1).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["Slider"][0][layout.itemAt(row, 0).widget().text()] == \
                   'QPlainTextEdit' else fields_per_type["Slider"][0][layout.itemAt(row, 0).widget().text()]
            if type(layout.itemAt(row, 1).widget()) == QLineEdit and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().text() == \
                       str(default_values[layout.itemAt(row, 0).widget().text()])
            elif type(layout.itemAt(row, 1).widget()) == QRadioButton and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().isChecked() == default_values[
                    layout.itemAt(row, 0).widget().text()]
    assert not_none_rows == len(fields_per_type["Slider"][0].keys())
    assert len(gui_init.undo_stack) == 6  # 2 for creating page & question, 4 for choosing Slider

    # Check structure
    structure = ConfigObj()  # {}
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    structure["Page 1"]["Question 1"] = {"type": "Slider"}
    for key, value in default_values.items():
        if key in fields_per_type["Slider"][0].keys():
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
def test_labels(gui_load, qtbot):
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
    labels_pos = find_row_by_label(gui_load.gui.edit_layout, 'label')
    cb_pos = find_row_by_label(gui_load.gui.edit_layout, 'labelled')

    # activate labels
    assert "label" not in gui_load.structure["Page 1"]["Question 1"].keys()
    assert gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().isEnabled() == False
    gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().isChecked() == True
    assert gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().isEnabled() == True
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    assert "label" not in gui_load.structure["Page 1"]["Question 1"].keys()
    assert gui_load.structure["Page 1"]["Question 1"]["labelled"] == True
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == LabeledSlider.LabeledSlider:
            assert len(child.levels) == len(range(int(gui_load.structure["Page 1"]["Question 1"]["min"]),
                                                  int(gui_load.structure["Page 1"]["Question 1"]["max"])+1))
            assert child.levels[0][0] == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.levels[0][1] == gui_load.structure["Page 1"]["Question 1"]["min"]
            assert child.levels[-1][0] == int(gui_load.structure["Page 1"]["Question 1"]["max"])
            assert child.levels[-1][1] == gui_load.structure["Page 1"]["Question 1"]["max"]
        elif type(child) == Slider.Slider:
            assert False
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    # adding too little labels -> error
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().setText("only one")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().text() == "only one"
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == "only one"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().setText("one, two, three")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().text() == "one, two, three"
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == "one, two, three"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == ["one", "two", "three"]
    assert error_found == True
    assert warning_found == False

    # adding too many labels -> error
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().setText("one, two, three, four, five, six")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().text() == "one, two, three, four, five, six"
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == "one, two, three, four, five, six"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == ["one", "two", "three", "four", "five", "six"]
    assert error_found == True
    assert warning_found == False

    # correct number of labels
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().setText("one, two, three, four, five")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().text() == "one, two, three, four, five"
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == "one, two, three, four, five"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == ["one", "two", "three", "four", "five"]
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == LabeledSlider.LabeledSlider:
            assert len(child.levels) == len(range(int(gui_load.structure["Page 1"]["Question 1"]["min"]),
                                                  int(gui_load.structure["Page 1"]["Question 1"]["max"]) + 1))
            assert child.levels[0][0] == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.levels[0][1] == gui_load.structure["Page 1"]["Question 1"]["label"][0]
            assert child.levels[-1][0] == int(gui_load.structure["Page 1"]["Question 1"]["max"])
            assert child.levels[-1][1] == gui_load.structure["Page 1"]["Question 1"]["label"][-1]
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    # disable labelled with label field filled
    gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().isChecked() == False
    assert gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().isEnabled() == False
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    # assert "label" not in gui_load.structure["Page 1"]["Question 1"].keys()  # they stay, they are just not loaded
    assert gui_load.structure["Page 1"]["Question 1"]["labelled"] == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier, delay=100)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Slider.Slider:
            assert True
        elif type(child) == LabeledSlider.LabeledSlider:
            assert False

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().isChecked() == True
    assert gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().isEnabled() == True

    # reset to default
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().clear()
    assert gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().text() == ""
    gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == ""
    if gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().isChecked():
        gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().click()
        assert gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().isChecked() == False
        assert gui_load.gui.edit_layout.itemAt(labels_pos, 1).widget().isEnabled() == False
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    assert "label" not in gui_load.structure["Page 1"]["Question 1"].keys()
    assert gui_load.structure["Page 1"]["Question 1"]["labelled"] == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier, delay=100)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Slider.Slider:
            assert True
        elif type(child) == LabeledSlider.LabeledSlider:
            assert False

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    gui_load.close()


# noinspection PyArgumentList
def test_start(gui_load, qtbot):
    if os.path.exists("./test/results/results_sl.csv"):
        os.remove("./test/results/results_sl.csv")

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
    start_pos = find_row_by_label(gui_load.gui.edit_layout, 'start')

    # try to put a string in -> error
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().insert("zero")
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().text() == "zero"
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "zero"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # greater than max
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().insert("99")
    assert gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().text() == "99"
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "99"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().text() == "99"
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "99"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False

    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Slider.Slider:
            assert child.value() == int(gui_load.structure["Page 1"]["Question 1"]["max"])

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '4'  # initial value within bounds (min<max<start)->max
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_sl.csv")

    # smaller than min
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().insert("-1")
    assert gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().text() == "-1"
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "-1"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().text() == "-1"
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "-1"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False

    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Slider.Slider:
            assert child.value() == int(gui_load.structure["Page 1"]["Question 1"]["min"])

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '0'  # initial value within bounds (start<min<max)->min
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_sl.csv")

    # somewhere in between
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().insert("2")
    assert gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().text() == "2"
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "2"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().text() == "2"
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "2"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False

    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Slider.Slider:
            assert child.value() == 2

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '2'  # initial value within bounds
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_sl.csv")

    # reset to default
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().insert("0")
    assert gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().text() == "0"
    gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "0"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, 1).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    gui_load.close()


# noinspection PyArgumentList
def test_min(gui_load, qtbot):
    if os.path.exists("./test/results/results_sl.csv"):
        os.remove("./test/results/results_sl.csv")

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
    min_pos = find_row_by_label(gui_load.gui.edit_layout, 'min')

    # try to put a string in -> error
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().insert("zero")
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().text() == "zero"
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "zero"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # min = max -> error
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().insert("4")
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().text() == "4"
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "4"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # greater than max
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().insert("9")
    assert gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().text() == "9"
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "9"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().text() == "9"
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "9"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False

    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Slider.Slider:
            assert child.minimum() == int(gui_load.structure["Page 1"]["Question 1"]["max"])
            assert child.maximum() == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.invertedAppearance() == True

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '4'  # initial value < max < min -> max
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_sl.csv")

    # with labels
    cb_pos = find_row_by_label(gui_load.gui.edit_layout, 'labelled')
    gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().isChecked() == True
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier, delay=100)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == LabeledSlider.LabeledSlider:
            assert len(child.levels) == len(range(int(gui_load.structure["Page 1"]["Question 1"]["min"]),
                                                  int(gui_load.structure["Page 1"]["Question 1"]["max"]) - 1, -1))
            assert child.levels[0][0] == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.levels[0][1] == gui_load.structure["Page 1"]["Question 1"]["min"]
            assert child.levels[-1][0] == int(gui_load.structure["Page 1"]["Question 1"]["max"])
            assert child.levels[-1][1] == gui_load.structure["Page 1"]["Question 1"]["max"]
            assert child.sl.minimum() == int(gui_load.structure["Page 1"]["Question 1"]["max"])
            assert child.sl.maximum() == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.sl.invertedAppearance() == True
        elif type(child) == Slider.Slider:
            assert False
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '4'  # initial value < max < min -> max
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_sl.csv")
    gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().isChecked() == False

    # reset to default (min < max)
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().insert("0")
    assert gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().text() == "0"
    gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "0"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(min_pos, 1).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)

    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Slider.Slider:
            assert child.minimum() == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.maximum() == int(gui_load.structure["Page 1"]["Question 1"]["max"])
            assert child.invertedAppearance() == False
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '0'  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_sl.csv")
    gui_load.close()


# noinspection PyArgumentList
def test_max(gui_load, qtbot):
    if os.path.exists("./test/results/results_sl.csv"):
        os.remove("./test/results/results_sl.csv")

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
    max_pos = find_row_by_label(gui_load.gui.edit_layout, 'max')

    # try to put a string in -> error
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().insert("zero")
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().text() == "zero"
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "zero"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # min = max -> error
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().insert("0")
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # smaller than min
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().insert("-5")
    assert gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().text() == "-5"
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "-5"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().text() == "-5"
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "-5"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False

    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Slider.Slider:
            assert child.minimum() == int(gui_load.structure["Page 1"]["Question 1"]["max"])
            assert child.maximum() == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.invertedAppearance() == True

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '0'  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_sl.csv")

    # with labels
    cb_pos = find_row_by_label(gui_load.gui.edit_layout, 'labelled')
    gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().isChecked() == True
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier, delay=100)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == LabeledSlider.LabeledSlider:
            assert len(child.levels) == len(range(int(gui_load.structure["Page 1"]["Question 1"]["min"]),
                                                  int(gui_load.structure["Page 1"]["Question 1"]["max"]) - 1, -1))
            assert child.levels[0][0] == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.levels[0][1] == gui_load.structure["Page 1"]["Question 1"]["min"]
            assert child.levels[-1][0] == int(gui_load.structure["Page 1"]["Question 1"]["max"])
            assert child.levels[-1][1] == gui_load.structure["Page 1"]["Question 1"]["max"]
            assert child.sl.minimum() == int(gui_load.structure["Page 1"]["Question 1"]["max"])
            assert child.sl.maximum() == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.sl.invertedAppearance() == True
        elif type(child) == Slider.Slider:
            assert False
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '0'  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_sl.csv")
    gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(cb_pos, 1).widget().isChecked() == False

    # reset to default (min < max)
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().insert("4")
    assert gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().text() == "4"
    gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "4"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(max_pos, 1).widget().text() == "4"
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "4"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)

    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Slider.Slider:
            assert child.minimum() == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.maximum() == int(gui_load.structure["Page 1"]["Question 1"]["max"])
            assert child.invertedAppearance() == False
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')
        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '0'  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_sl.csv")
    gui_load.close()


# noinspection PyArgumentList
def test_text_position(gui_load, qtbot):
    if os.path.exists("./test/results/results_sl.csv"):
        os.remove("./test/results/results_sl.csv")

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
    qa_pos = find_row_by_label(gui_load.gui.edit_layout, 'question_above')
    assert gui_load.gui.edit_layout.itemAt(qa_pos, 1).widget().isChecked() == False
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QFormLayout:
            assert child.rowCount() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    os.remove("./test/results/results_sl.csv")

    # change position to above
    gui_load.gui.edit_layout.itemAt(qa_pos, 1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(qa_pos, 1).widget().isChecked() == True
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    assert gui_load.structure["Page 1"]["Question 1"]["question_above"] == True
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QFormLayout:
            assert child.rowCount() == 2

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    os.remove("./test/results/results_sl.csv")
    # revert to original
    gui_load.gui.edit_layout.itemAt(qa_pos, 1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(qa_pos, 1).widget().isChecked() == False
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    assert gui_load.structure["Page 1"]["Question 1"]["question_above"] == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    gui_load.close()


# noinspection PyArgumentList
def test_header(gui_load, qtbot):
    if os.path.exists("./test/results/results_sl.csv"):
        os.remove("./test/results/results_sl.csv")

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
    header_pos = find_row_by_label(gui_load.gui.edit_layout, 'header')
    assert gui_load.gui.edit_layout.itemAt(header_pos, 1).widget().text() == ''
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QFormLayout:
            assert child.rowCount() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    os.remove("./test/results/results_sl.csv")

    # add header
    gui_load.gui.edit_layout.itemAt(header_pos, 1).widget().clear()
    assert gui_load.gui.edit_layout.itemAt(header_pos, 1).widget().text() == ''
    gui_load.gui.edit_layout.itemAt(header_pos, 1).widget().setPlainText('one, "", "", "", four')
    gui_load.gui.edit_layout.itemAt(header_pos, 1).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(header_pos, 1).widget().text() == 'one, "", "", "", four'
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    assert gui_load.structure["Page 1"]["Question 1"]["header"] == ['one', "", "", "", 'four']
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/sltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QFormLayout:
            assert child.rowCount() == 2

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    os.remove("./test/results/results_sl.csv")

    # revert to original
    gui_load.gui.edit_layout.itemAt(header_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(header_pos, 1).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(header_pos, 1).widget().text() == ''
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    assert "header" not in gui_load.structure["Page 1"]["Question 1"].keys()
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    if os.path.exists("./test/results/results_sl.csv"):
        os.remove("./test/results/results_sl.csv")
    assert run.Stack.count() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'sl'  # first row
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '0'  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_sl.csv")


# noinspection PyArgumentList
def test_execute_questionnaire(run, qtbot):
    if os.path.exists("./test/results/results_sl.csv"):
        os.remove("./test/results/results_sl.csv")
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if type(child) == Slider.Slider:
            bb = child.rect()
            QTest.mouseClick(child, Qt.LeftButton, pos=bb.center())
            assert child.value() == int((child.maximum()+child.minimum())/2)

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton, delay=1)

    results = []
    with open('./test/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '2'  # middle of 0 and 4 is 2
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_sl.csv")
