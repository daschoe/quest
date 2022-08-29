"""Testing the behaviour of PupilCoreButton.py + QEditGui.py"""

from context import *

recording_path = "C:\\Users\\Administrator\\recordings\\"  # TODO change to your path


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    open_pupil()
    QTimer.singleShot(150, lambda: open_config_file("./test/pbtest.txt"))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def gui_load2(gui_init):
    """Start GUI"""
    open_pupil()
    QTimer.singleShot(150, lambda: open_config_file("./test/pbtest2.txt"))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def run():
    """Execute the questionnaire."""
    open_pupil()
    return StackedWindowGui("./test/pbtest.txt")


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
    # change the question type to 'Button'
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
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "Button"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if type(layout.itemAt(row, 1)) == QWidgetItem:
            not_none_rows += 1
            assert layout.itemAt(row, 0).widget().text() in fields_per_type["Button"][0].keys()
            assert str(type(layout.itemAt(row, 1).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["Button"][0][layout.itemAt(row, 0).widget().text()] == 'QPlainTextEdit'\
                   else fields_per_type["Button"][0][layout.itemAt(row, 0).widget().text()]
            if type(layout.itemAt(row, 1).widget()) == QLineEdit and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().text() == default_values[layout.itemAt(row, 0).widget().text()]
            elif type(layout.itemAt(row, 1).widget()) == QCheckBox and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().isChecked() == default_values[
                    layout.itemAt(row, 0).widget().text()]
    assert not_none_rows == len(fields_per_type["Button"][0].keys())
    assert len(gui_init.undo_stack) == 9  # 2 for creating page & question, 7 for choosing Button

    # Check structure
    structure = ConfigObj()  # {}
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    structure["Page 1"]["Question 1"] = {"type": "Button"}
    for key, value in default_values.items():
        if key in fields_per_type["Button"][0].keys():
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
@pytest.mark.pupil
def test_inscription(gui_load, qtbot, capfd):
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
    ins_pos = find_row_by_label(gui_load.gui.edit_layout, 'inscription')

    # change text
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().setText("Click me")
    assert gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().text() == "Click me"
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["inscription"] == "Click me"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().text() == "Click me"
    assert gui_load.structure["Page 1"]["Question 1"]["inscription"] == "Click me"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pbtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Button:
            assert child.button.text() == "Click me"

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    #  empty inscription -> warning
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().setText("")
    assert gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().text() == ""
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["inscription"] == ""
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().text() == ""
    assert gui_load.structure["Page 1"]["Question 1"]["inscription"] == ""
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == True
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    QTimer.singleShot(500, handle_dialog_warning)
    test_gui = StackedWindowGui("./test/pbtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Button:
            assert child.button.text() == ""
            child.button.click()
            QTest.qWait(1000)
            out, err = capfd.readouterr()
            assert out.index("Trigger {'topic': 'annotation', 'label': 'test', 'timestamp':") != -1
            assert out.endswith(", 'duration': 1} Message forwarded.\n") == True
    QTimer.singleShot(1000, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    # predefined 'None'
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().setText("None")
    assert gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().text() == "None"
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["inscription"] == "None"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().text() == "None"
    assert gui_load.structure["Page 1"]["Question 1"]["inscription"] == "None"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == True
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    QTimer.singleShot(150, handle_dialog_warning)
    test_gui = StackedWindowGui("./test/pbtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Button:
            assert child.button.text() == "None"
            child.button.click()
            QTest.qWait(500)
            out, err = capfd.readouterr()
            assert out.index("Trigger {'topic': 'annotation', 'label': 'test', 'timestamp':") != -1
            assert out.endswith(", 'duration': 1} Message forwarded.\n") == True
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    # reset file
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().setText("Text")
    assert gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().text() == "Text"
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["inscription"] == "Text"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().text() == "Text"
    assert gui_load.structure["Page 1"]["Question 1"]["inscription"] == "Text"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)

    os.remove("./test/results/results_pb.csv")
    gui_load.close()


# noinspection PyArgumentList
@pytest.mark.pupil
def test_custom_annotation_text(gui_load, qtbot, capfd):
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

    # change text
    gui_load.structure["Page 1"]["Question 1"]["annotation"] = "Custom text"
    assert gui_load.structure["Page 1"]["Question 1"]["annotation"] == "Custom text"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["annotation"] == "Custom text"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["annotation"] == "Custom text"
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pbtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Button:
            child.button.click()
            out, err = capfd.readouterr()
            assert out.index("Trigger {'topic': 'annotation', 'label': 'Custom text', 'timestamp':") != -1
            assert out.endswith(", 'duration': 1} Message forwarded.\n") == True

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    gui_load.structure["Page 1"]["Question 1"].pop("annotation")
    assert "annotation" not in gui_load.structure["Page 1"]["Question 1"].keys()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    assert "annotation" not in gui_load.structure["Page 1"]["Question 1"].keys()
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    gui_load.close()


# noinspection PyArgumentList
@pytest.mark.pupil
def test_custom_recording_name(gui_load, qtbot, capfd):
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
    func_pos = find_row_by_label(gui_load.gui.edit_layout, 'function')
    func_cb = gui_load.gui.edit_layout.itemAt(func_pos, 1).widget()

    QTest.mouseClick(func_cb, Qt.LeftButton)
    QTest.keyClick(func_cb, Qt.Key_Down)
    QTest.keyClick(func_cb, Qt.Key_Enter)
    assert func_cb.currentText() == "Recording"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["function"] == "Recording"

    # change text
    gui_load.structure["Page 1"]["Question 1"]["recording_name"] = "MyRecording"
    assert gui_load.structure["Page 1"]["Question 1"]["recording_name"] == "MyRecording"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["recording_name"] == "MyRecording"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["recording_name"] == "MyRecording"
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pbtest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Button:
            child.button.click()
            out, err = capfd.readouterr()
            assert out.endswith("MyRecording\nStart recording... OK\n") == True

    test_gui.pupil_remote.send_string('r')
    print("Stop recording...", test_gui.pupil_remote.recv_string())

    QTimer.singleShot(500, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    assert os.path.exists(recording_path+"MyRecording") == True
    # os.remove(recording_path+"MyRecording")

    QTest.mouseClick(func_cb, Qt.LeftButton)
    QTest.keyClick(func_cb, Qt.Key_Up)
    QTest.keyClick(func_cb, Qt.Key_Enter)
    assert func_cb.currentText() == "Annotate"
    gui_load.structure["Page 1"]["Question 1"].pop("recording_name")
    assert "recording_name" not in gui_load.structure["Page 1"]["Question 1"].keys()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    assert "recording_name" not in gui_load.structure["Page 1"]["Question 1"].keys()
    gui_load.save()
    gui_load.close()


# noinspection PyArgumentList
@pytest.mark.pupil
def test_custom_recording_name_id(gui_load2, qtbot, capfd):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert error_found == False
    assert warning_found == False
    tv = gui_load2.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    func_pos = find_row_by_label(gui_load2.gui.edit_layout, 'function')
    func_cb = gui_load2.gui.edit_layout.itemAt(func_pos, 1).widget()

    assert func_cb.currentText() == "Recording"
    assert gui_load2.structure["Page 1"]["Question 1"]["function"] == "Recording"

    # change text
    gui_load2.structure["Page 1"]["Question 1"]["recording_name"] = "id:tf"
    assert gui_load2.structure["Page 1"]["Question 1"]["recording_name"] == "id:tf"
    gui_load2.gui.load_preview()
    gui_load2.gui.refresh_button.click()
    assert gui_load2.structure["Page 1"]["Question 1"]["recording_name"] == "id:tf"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert error_found == False
    assert warning_found == False
    gui_load2.gui.refresh_button.click()
    assert gui_load2.structure["Page 1"]["Question 1"]["recording_name"] == "id:tf"
    QTest.keyClicks(gui_load2, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pbtest2.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QLineEdit:
            # noinspection PyTypeChecker
            QTest.keyClicks(child, "test", Qt.NoModifier, delay=1)
            assert child.text() == "test"
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Button:
            child.button.click()
            out, err = capfd.readouterr()
            assert out.endswith("test\nStart recording... OK\n") == True

    test_gui.pupil_remote.send_string('r')
    print("Stop recording...", test_gui.pupil_remote.recv_string())

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    assert os.path.exists(recording_path+"test") == True
    # os.remove(recording_path+"test")

    gui_load2.structure["Page 1"]["Question 1"].pop("recording_name")
    assert "recording_name" not in gui_load2.structure["Page 1"]["Question 1"].keys()
    assert "recording_name" not in gui_load2.structure["Page 1"]["Question 1"].keys()
    gui_load2.save()
    gui_load2.close()


# noinspection PyArgumentList
@pytest.mark.pupil
def test_function(gui_load, qtbot, capfd):
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
    func_pos = find_row_by_label(gui_load.gui.edit_layout, 'function')
    func_cb = gui_load.gui.edit_layout.itemAt(func_pos, 1).widget()
    assert func_cb.currentText() == 'Annotate'
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pbtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Button:
            child.button.click()
            out, err = capfd.readouterr()
            assert out.index("Trigger {'topic': 'annotation', 'label': 'test', 'timestamp':") != -1
            assert out.endswith(", 'duration': 1} Message forwarded.\n") == True
            QTest.qWait(500)
    test_gui.close()

    QTest.mouseClick(func_cb, Qt.LeftButton)
    QTest.keyClick(func_cb, Qt.Key_Down)
    QTest.keyClick(func_cb, Qt.Key_Enter)
    assert func_cb.currentText() == "Recording"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["function"] == "Recording"
    gui_load.save()
    test_gui = StackedWindowGui("./test/pbtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Button:
            child.button.click()
            out, err = capfd.readouterr()
            assert out.endswith("Start recording... OK\n") == True
            QTest.qWait(500)
    test_gui.close()

    QTest.mouseClick(func_cb, Qt.LeftButton)
    QTest.keyClick(func_cb, Qt.Key_Down)
    QTest.keyClick(func_cb, Qt.Key_Enter)
    assert func_cb.currentText() == "Stop"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    gui_load.save()
    test_gui = StackedWindowGui("./test/pbtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Button:
            child.button.click()
            out, err = capfd.readouterr()
            assert out.endswith("Stop recording... OK\n") == True
            QTest.qWait(500)
    test_gui.close()

    QTest.mouseClick(func_cb, Qt.LeftButton)
    QTest.keyClick(func_cb, Qt.Key_Down)
    QTest.keyClick(func_cb, Qt.Key_Enter)
    assert func_cb.currentText() == "Calibration"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    gui_load.save()
    '''
    test_gui = StackedWindowGui("./test/pbtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Button:
            child.button.click()
            out, err = capfd.readouterr()
            assert out.endswith("Calibrate... OK\n") == True
            QTest.qWait(5000)
    test_gui.close()
    '''

    QTest.mouseClick(func_cb, Qt.LeftButton)
    QTest.keyClick(func_cb, Qt.Key_Up)
    QTest.keyClick(func_cb, Qt.Key_Up)
    QTest.keyClick(func_cb, Qt.Key_Up)
    QTest.keyClick(func_cb, Qt.Key_Enter)
    assert func_cb.currentText() == 'Annotate'
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    gui_load.save()
    os.remove("./test/results/results_pb.csv")
    gui_load.close()


# noinspection PyArgumentList
@pytest.mark.pupil
def test_execute_questionnaire_no_interaction(run, qtbot):
    if os.path.exists("./test/results/results_pb.csv"):
        os.remove("./test/results/results_pb.csv")
    assert run.Stack.count() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_pb.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'pb'
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == 'False'  # the button was not clicked
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_pb.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_blocked(run, qtbot):
    with mock_file(r'./test/results/results_pb.csv'):
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
                    assert lines[1] == 'pb'
                    assert lines[2] == 'Start'
                    assert lines[3] == 'End'
        assert len(results) == 4
        assert lines[0] == '-1'  # participant number unknown
        assert lines[1] == 'False'  # the button was not clicked
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
        os.remove(res_file)


# noinspection PyArgumentList
@pytest.mark.pupil
def test_execute_questionnaire(run, qtbot, capfd):
    if os.path.exists("./test/results/results_pb.csv"):
        os.remove("./test/results/results_pb.csv")
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if type(child) is Button:
            child.button.click()
            out, err = capfd.readouterr()
            assert out.startswith("Trigger {'topic': 'annotation', 'label': 'test', 'timestamp':") == True
            assert out.endswith(", 'duration': 1} Message forwarded.\n") == True

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_pb.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'pb'
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == 'True'  # button was clicked
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_pb.csv")


# noinspection PyArgumentList
@pytest.mark.pupil
def test_execute_questionnaire_blocked(run, qtbot, capfd):
    with mock_file(r'./test/results/results_pb.csv'):
        assert run.Stack.count() == 1
        for child in run.Stack.currentWidget().children():
            if type(child) is Button:
                child.button.click()
                out, err = capfd.readouterr()
                assert out.startswith("Trigger {'topic': 'annotation', 'label': 'test', 'timestamp':") == True
                assert out.endswith(", 'duration': 1} Message forwarded.\n") == True
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
                    assert lines[1] == 'pb'
                    assert lines[2] == 'Start'
                    assert lines[3] == 'End'
        assert len(results) == 4
        assert lines[0] == '-1'  # participant number unknown
        assert lines[1] == 'True'  # the button was not clicked
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
        os.remove(res_file)
