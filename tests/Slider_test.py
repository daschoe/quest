"""Testing the behaviour of AnswerSlider.py + QEditGui.py"""

from tests.context import pytest, QEditGuiMain, QTimer, open_config_file, StackedWindowGui, QTest, handle_dialog_p, handle_dialog_q, Qt, QFormLayout, QWidgetItem, fields_per_type, default_values, QLineEdit, page_fields, listify, ConfigObj, general_fields, handle_dialog_error, validate_questionnaire, handle_dialog_no_save, find_row_by_label, handle_dialog, csv, re, os, mock_file, Slider, LabeledSlider, QRadioButton


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file(os.path.join(os.getcwd(), "tests/sltest.txt")))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))


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
    # change the question type to 'Check'
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"
    QTest.mouseClick(gui_init.gui.questiontype, Qt.MouseButton.LeftButton)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "Slider"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QWidgetItem):
            not_none_rows += 1
            assert layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in fields_per_type["Slider"][0]
            assert str(type(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["Slider"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()] == \
                   'QPlainTextEdit' else fields_per_type["Slider"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
            if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QLineEdit) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().text() == \
                       str(default_values[layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()])
            elif isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QRadioButton) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().isChecked() == default_values[
                    layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
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
        if key in fields_per_type["Slider"][0]:
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
    assert not error_found
    assert not warning_found
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())
    labels_pos = find_row_by_label(gui_load.gui.edit_layout, 'label')
    cb_pos = find_row_by_label(gui_load.gui.edit_layout, 'labelled')

    # activate labels
    assert "label" not in gui_load.structure["Page 1"]["Question 1"].keys()
    assert not gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().isEnabled()
    gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().isEnabled()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert not error_found
    assert not warning_found
    assert "label" not in gui_load.structure["Page 1"]["Question 1"].keys()
    assert gui_load.structure["Page 1"]["Question 1"]["labelled"]
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, LabeledSlider.LabeledSlider):
            assert len(child.levels) == len(range(int(gui_load.structure["Page 1"]["Question 1"]["min"]),
                                                  int(gui_load.structure["Page 1"]["Question 1"]["max"]) + 1))
            assert child.levels[0][0] == child.sl.minimum()
            assert child.levels[0][1] == gui_load.structure["Page 1"]["Question 1"]["min"]
            assert child.levels[-1][0] == child.sl.maximum()
            assert child.levels[-1][1] == gui_load.structure["Page 1"]["Question 1"]["max"]
        elif isinstance(child, Slider.Slider):
            assert False
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()

    # adding too little labels -> error
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("only one")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "only one"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == "only one"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one, two, three")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one, two, three"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == "one, two, three"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == ["one", "two", "three"]
    assert error_found
    assert not warning_found

    # adding too many labels -> error
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one, two, three, four, five, six")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one, two, three, four, five, six"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == "one, two, three, four, five, six"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == ["one", "two", "three", "four", "five", "six"]
    assert error_found
    assert not warning_found

    # correct number of labels
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one, two, three, four, five")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one, two, three, four, five"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == "one, two, three, four, five"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == ["one", "two", "three", "four", "five"]
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, LabeledSlider.LabeledSlider):
            assert len(child.levels) == len(range(int(gui_load.structure["Page 1"]["Question 1"]["min"]),
                                                  int(gui_load.structure["Page 1"]["Question 1"]["max"]) + 1))
            assert child.levels[0][0] == child.sl.minimum()
            assert child.levels[0][1] == gui_load.structure["Page 1"]["Question 1"]["label"][0]
            assert child.levels[-1][0] == child.sl.maximum()
            assert child.levels[-1][1] == gui_load.structure["Page 1"]["Question 1"]["label"][-1]
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()

    # adding too many labels fields -> error
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("[0, two, three], [4, five, six]")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "[0, two, three], [4, five, six]"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == "[0, two, three], [4, five, six]"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # no number in first position -> error
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("[two, three]")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "[two, three]"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == "[two, three]"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # correct number of labels
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().setText("[0, null], [4, four]")
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "[0, null], [4, four]"
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == "[0, null], [4, four]"
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == [[0, "null"], [4, "four"]]
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, LabeledSlider.LabeledSlider):
            assert len(child.levels) == len(range(int(gui_load.structure["Page 1"]["Question 1"]["min"]),
                                                  int(gui_load.structure["Page 1"]["Question 1"]["max"]) + 1))
            assert child.levels[0][0] == child.sl.minimum()
            assert child.levels[0][1] == "null"
            assert child.levels[-1][0] == child.sl.maximum()
            assert child.levels[-1][1] == "four"
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()

    # disable labelled with label field filled
    gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert not gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    assert not gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().isEnabled()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert not error_found
    assert not warning_found
    # assert "label" not in gui_load.structure["Page 1"]["Question 1"].keys()  # they stay, they are just not loaded
    assert not gui_load.structure["Page 1"]["Question 1"]["labelled"]
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider):
            assert True
        elif isinstance(child, LabeledSlider.LabeledSlider):
            assert False

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().isEnabled()

    # reset to default
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    assert gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().text() == ""
    gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["label"] == ""
    if gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked():
        gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().click()
        assert not gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
        assert not gui_load.gui.edit_layout.itemAt(labels_pos, QFormLayout.ItemRole.FieldRole).widget().isEnabled()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert not error_found
    assert not warning_found
    assert "label" not in gui_load.structure["Page 1"]["Question 1"].keys()
    assert not gui_load.structure["Page 1"]["Question 1"]["labelled"]
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider):
            assert True
        elif isinstance(child, LabeledSlider.LabeledSlider):
            assert False

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    gui_load.close()


# noinspection PyArgumentList
def test_start(gui_load, qtbot):
    if os.path.exists("./tests/results/results_sl.csv"):
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

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
    start_pos = find_row_by_label(gui_load.gui.edit_layout, 'start')

    # try to put a string in -> error
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("zero")
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "zero"
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "zero"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # greater than max
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("99")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "99"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "99"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "99"  # TODO unschönes Verhalten -> gleich anders anzeigen?!
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == int(gui_load.structure["Page 1"]["Question 1"]["max"])
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider):
            assert child.value() == int(gui_load.structure["Page 1"]["Question 1"]["max"])

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == '4'  # initial value within bounds (min<max<start)->max
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

    # smaller than min
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("-1")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "-1"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "-1"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "-1"
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == int(gui_load.structure["Page 1"]["Question 1"]["min"])
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider):
            assert child.value() == int(gui_load.structure["Page 1"]["Question 1"]["min"])

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == str(int(gui_load.structure["Page 1"]["Question 1"]["start"]))  # initial value within bounds (start<min<max)->min
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

    # somewhere in between
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("2")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "2"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "2"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "2"
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "2"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider):
            assert child.value() == 2

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == '2'  # initial value within bounds
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
    
    # somewhere in between (negative range)
    gui_load.structure["Page 1"]["Question 1"]["min"] = 5
    gui_load.structure["Page 1"]["Question 1"]["max"] = 0
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("2")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "2"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "2"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "2"
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "2"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider):
            assert child.value() == 2

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == '2'  # initial value within bounds
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
    
    gui_load.structure["Page 1"]["Question 1"]["min"] = -1
    gui_load.structure["Page 1"]["Question 1"]["max"] = -6
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("-2")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "-2"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "-2"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "-2"
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "-2"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider):
            assert child.value() == -2

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == '-2'  # initial value within bounds
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
    

    # reset to default
    gui_load.structure["Page 1"]["Question 1"]["min"] = 0
    gui_load.structure["Page 1"]["Question 1"]["max"] = 4
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("0")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "0"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Question 1"]["start"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load.close()


# noinspection PyArgumentList
def test_step(gui_load, qtbot):
    if os.path.exists("./tests/results/results_sl.csv"):
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

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
    start_pos = find_row_by_label(gui_load.gui.edit_layout, 'step')

    # try to put a string in -> error
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("zero")
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "zero"
    assert gui_load.structure["Page 1"]["Question 1"]["step"] == "zero"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # greater than max+min -> error
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("10")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "10"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "10"
    assert gui_load.structure["Page 1"]["Question 1"]["step"] == "10"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # 0 -> error
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("0")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Question 1"]["step"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # greater than 1
    gui_load.structure["Page 1"]["Question 1"]["max"] = "5"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("2")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "2"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["step"] == "2"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "2"
    assert gui_load.structure["Page 1"]["Question 1"]["step"] == "2"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    #for child in test_gui.Stack.currentWidget().children():
    #    if isinstance(child, Slider.Slider):
    #        print(child.tickInterval())  # TODO is it possible to count the displayed ticks/steps?

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == '0'  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

    # smaller than 1
    gui_load.structure["Page 1"]["Question 1"]["max"] = "4"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("0.5")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0.5"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["step"] == "0.5"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0.5"
    assert gui_load.structure["Page 1"]["Question 1"]["step"] == '0.5'
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    #for child in test_gui.Stack.currentWidget().children():
    #    if isinstance(child, Slider.Slider):
    #        print(child.tickInterval())  # TODO is it possible to count the displayed ticks/steps?

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == '0.0'  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

    # reset to default
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().insert("1")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["step"] == "1"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1"
    assert gui_load.structure["Page 1"]["Question 1"]["step"] == "1"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load.close()


# noinspection PyArgumentList
def test_min(gui_load, qtbot):
    if os.path.exists("./tests/results/results_sl.csv"):
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

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
    min_pos = find_row_by_label(gui_load.gui.edit_layout, 'min')

    # try to put a string in -> error
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().insert("zero")
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "zero"
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "zero"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # min = max -> error
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().insert("4")
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "4"
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "4"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # greater than max
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().insert("9")
    assert gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "9"
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "9"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "9"
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "9"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider):
            assert child.minimum() == int((int(gui_load.structure["Page 1"]["Question 1"]["max"]) - int(gui_load.structure["Page 1"]["Question 1"]["min"])) / int(gui_load.structure["Page 1"]["Question 1"]["step"]))
            assert child._min == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.maximum() == 0
            assert child._max == int(gui_load.structure["Page 1"]["Question 1"]["max"])
            assert child.value() == gui_load.structure["Page 1"]["Question 1"]["start"]

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == '4'  # initial value < max < min -> max
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

    # with labels
    cb_pos = find_row_by_label(gui_load.gui.edit_layout, 'labelled')
    gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, LabeledSlider.LabeledSlider):
            assert len(child.levels) == len(range(int(gui_load.structure["Page 1"]["Question 1"]["min"]),
                                                  int(gui_load.structure["Page 1"]["Question 1"]["max"]) - 1, -1))
            assert child.levels[0][0] == child.sl.maximum()
            assert child.levels[0][1] == gui_load.structure["Page 1"]["Question 1"]["min"]
            assert child.levels[-1][0] == child.sl.maximum() - child.sl.minimum()
            assert child.levels[-1][1] == gui_load.structure["Page 1"]["Question 1"]["max"]
            assert child.sl.minimum() == int(gui_load.structure["Page 1"]["Question 1"]["max"]) - int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.sl._min == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.sl.maximum() == 0
            assert child.sl._max == int(gui_load.structure["Page 1"]["Question 1"]["max"])
        elif isinstance(child, Slider.Slider):
            assert False
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == '4'  # initial value < max < min -> max
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
    gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert not gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()

    # reset to default (min < max)
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().insert("0")
    assert gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0"
    gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "0"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(min_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Question 1"]["min"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)

    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider):
            assert child.minimum() == 0
            assert child._min == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.maximum() == int((int(gui_load.structure["Page 1"]["Question 1"]["max"]) - int(gui_load.structure["Page 1"]["Question 1"]["min"])) / int(gui_load.structure["Page 1"]["Question 1"]["step"])) if int(gui_load.structure["Page 1"]["Question 1"]["max"]) > int(gui_load.structure["Page 1"]["Question 1"]["min"]) else -1 * int((int(gui_load.structure["Page 1"]["Question 1"]["max"]) - int(gui_load.structure["Page 1"]["Question 1"]["min"])) / int(gui_load.structure["Page 1"]["Question 1"]["step"]))
            assert child._max == int(gui_load.structure["Page 1"]["Question 1"]["max"])
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == str(int(gui_load.structure["Page 1"]["Question 1"]["start"]))  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

    # initial value
    gui_load.structure["Page 1"]["Question 1"]["start"] = 0
    gui_load.save()
    gui_load.close()


# noinspection PyArgumentList
def test_max(gui_load, qtbot):
    if os.path.exists("./tests/results/results_sl.csv"):
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

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
    max_pos = find_row_by_label(gui_load.gui.edit_layout, 'max')

    # try to put a string in -> error
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().insert("zero")
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "zero"
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "zero"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # min = max -> error
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().insert("0")
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # smaller than min
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().insert("-5")
    assert gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "-5"
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "-5"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "-5"
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "-5"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider):
            assert child.invertedAppearance()
            assert child.minimum() == -5
            assert child._min == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.maximum() == 0
            assert child._max == int(gui_load.structure["Page 1"]["Question 1"]["max"])

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == str(gui_load.structure["Page 1"]["Question 1"]["start"])  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

    # with labels
    cb_pos = find_row_by_label(gui_load.gui.edit_layout, 'labelled')
    gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, LabeledSlider.LabeledSlider):
            assert len(child.levels) == len(range(int(gui_load.structure["Page 1"]["Question 1"]["min"]),
                                                  int(gui_load.structure["Page 1"]["Question 1"]["max"]) - 1, -1))
            assert child.levels[0][0] == child.sl.maximum()
            assert child.levels[0][1] == gui_load.structure["Page 1"]["Question 1"]["min"]
            assert child.levels[-1][0] == child.sl.maximum() - child.sl.minimum()
            assert child.levels[-1][1] == gui_load.structure["Page 1"]["Question 1"]["max"]
            assert child.sl.minimum() == -5
            assert child.sl._min == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.sl.maximum() == 0
            assert child.sl._max == int(gui_load.structure["Page 1"]["Question 1"]["max"])
        elif isinstance(child, Slider.Slider):
            assert False
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == str(gui_load.structure["Page 1"]["Question 1"]["start"])  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
    gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert not gui_load.gui.edit_layout.itemAt(cb_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()

    # reset to default (min < max)
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().insert("4")
    assert gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "4"
    gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "4"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(max_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "4"
    assert gui_load.structure["Page 1"]["Question 1"]["max"] == "4"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)

    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider):
            assert child.minimum() == 0
            assert child._min == int(gui_load.structure["Page 1"]["Question 1"]["min"])
            assert child.maximum() == int((int(gui_load.structure["Page 1"]["Question 1"]["max"]) - int(gui_load.structure["Page 1"]["Question 1"]["min"])) / int(gui_load.structure["Page 1"]["Question 1"]["step"])) if int(gui_load.structure["Page 1"]["Question 1"]["max"]) > int(gui_load.structure["Page 1"]["Question 1"]["min"]) else -1 * int((int(gui_load.structure["Page 1"]["Question 1"]["max"]) - int(gui_load.structure["Page 1"]["Question 1"]["min"])) / int(gui_load.structure["Page 1"]["Question 1"]["step"]))
            assert child._max == int(gui_load.structure["Page 1"]["Question 1"]["max"])
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')
        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == str(int(gui_load.structure["Page 1"]["Question 1"]["start"]))  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

    gui_load.structure["Page 1"]["Question 1"]["start"] = 0
    gui_load.save()
    gui_load.close()


# noinspection PyArgumentList
def test_text_position(gui_load, qtbot):
    if os.path.exists("./tests/results/results_sl.csv"):
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

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
    qa_pos = find_row_by_label(gui_load.gui.edit_layout, 'question_above')
    assert not gui_load.gui.edit_layout.itemAt(qa_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, QFormLayout):
            assert child.rowCount() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

    # change position to above
    gui_load.gui.edit_layout.itemAt(qa_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert gui_load.gui.edit_layout.itemAt(qa_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert not error_found
    assert not warning_found
    assert gui_load.structure["Page 1"]["Question 1"]["question_above"]
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, QFormLayout):
            assert child.rowCount() == 2

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
    # revert to original
    gui_load.gui.edit_layout.itemAt(qa_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert not gui_load.gui.edit_layout.itemAt(qa_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert not error_found
    assert not warning_found
    assert not gui_load.structure["Page 1"]["Question 1"]["question_above"]
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load.close()


# noinspection PyArgumentList
def test_header(gui_load, qtbot):
    if os.path.exists("./tests/results/results_sl.csv"):
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

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
    header_pos = find_row_by_label(gui_load.gui.edit_layout, 'header')
    assert gui_load.gui.edit_layout.itemAt(header_pos, QFormLayout.ItemRole.FieldRole).widget().text() == ''
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, QFormLayout):
            assert child.rowCount() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

    # add header
    gui_load.gui.edit_layout.itemAt(header_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    assert gui_load.gui.edit_layout.itemAt(header_pos, QFormLayout.ItemRole.FieldRole).widget().text() == ''
    gui_load.gui.edit_layout.itemAt(header_pos, QFormLayout.ItemRole.FieldRole).widget().setPlainText('one, "", "", "", four')
    gui_load.gui.edit_layout.itemAt(header_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(header_pos, QFormLayout.ItemRole.FieldRole).widget().text() == 'one, "", "", "", four'
    gui_load.structure = listify(gui_load.structure)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    assert gui_load.structure["Page 1"]["Question 1"]["header"] == ['one', "", "", "", 'four']
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui(os.path.join(os.getcwd(), "tests/sltest.txt"))
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, QFormLayout):
            assert child.rowCount() == 2

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]

    # revert to original
    gui_load.gui.edit_layout.itemAt(header_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(header_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(header_pos, QFormLayout.ItemRole.FieldRole).widget().text() == ''
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    gui_load.structure = listify(gui_load.structure)
    assert not error_found
    assert not warning_found
    assert "header" not in gui_load.structure["Page 1"]["Question 1"].keys()
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    if os.path.exists("./tests/results/results_sl.csv"):
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
    assert run.Stack.count() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)

    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert results[0] == 'data_row_number'  # participant number
                assert results[1] == 'sl'  # first row
                assert results[2] == 'Start'
                assert results[3] == 'End'
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == '0'  # initial value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_blocked(run, qtbot):
    with mock_file(r'./tests/results/results_sl.csv'):
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
                    assert results[1] == 'sl'  # first row
                    assert results[2] == 'Start'
                    assert results[3] == 'End'
        assert len(results) == 4
        assert results[0] == '-1'  # participant number unknown
        assert results[1] == '0'  # initial value
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire(run, qtbot):
    if os.path.exists("./tests/results/results_sl.csv"):
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if isinstance(child, Slider.Slider) or str(child.__class__)=="<class 'Slider.Slider'>":
            bb = child.rect()
            QTest.mouseClick(child, Qt.MouseButton.LeftButton, pos=bb.center())
            assert child.value() == int((child._max + child._min) / 2)

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)

    results = []
    with open('./tests/results/results_sl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == '2'  # middle of 0 and 4 is 2
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]


# noinspection PyArgumentList
def test_execute_questionnaire_blocked(run, qtbot):
    with mock_file(r'./tests/results/results_sl.csv'):
        assert run.Stack.count() == 1
        for child in run.Stack.currentWidget().children():
            if isinstance(child, Slider.Slider) or str(child.__class__)=="<class 'Slider.Slider'>":
                bb = child.rect()
                QTest.mouseClick(child, Qt.MouseButton.LeftButton, pos=bb.center())
                assert child.value() == int((child._max + child._min) / 2)
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
                    assert results[1] == 'sl'  # first row
                    assert results[2] == 'Start'
                    assert results[3] == 'End'
        assert len(results) == 4
        assert results[0] == '-1'  # participant number unknown
        assert results[1] == '2'
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
        [os.remove('./tests/results/'+fil) for fil in os.listdir('./tests/results/')]
