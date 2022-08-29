"""Testing the behaviour of OSCButton.py + QEditGui.py"""
# TODO how to test osc messages
from context import *


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file("./test/osctest.txt"))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui("./test/osctest.txt")


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
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "OSCButton"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if type(layout.itemAt(row, 1)) == QWidgetItem:
            not_none_rows += 1
            assert layout.itemAt(row, 0).widget().text() in fields_per_type["OSCButton"][0].keys()
            assert str(type(layout.itemAt(row, 1).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["OSCButton"][0][layout.itemAt(row, 0).widget().text()] == 'QPlainTextEdit'\
                   else fields_per_type["OSCButton"][0][layout.itemAt(row, 0).widget().text()]
            if type(layout.itemAt(row, 1).widget()) == QLineEdit and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().text() == default_values[layout.itemAt(row, 0).widget().text()]
            elif type(layout.itemAt(row, 1).widget()) == QCheckBox and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().isChecked() == default_values[
                    layout.itemAt(row, 0).widget().text()]
    assert not_none_rows == len(fields_per_type["OSCButton"][0].keys())
    assert len(gui_init.undo_stack) == 15  # 2 for creating page & question, 13 for choosing OSCButton

    # Check structure
    structure = ConfigObj()  # {}
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    structure["Page 1"]["Question 1"] = {"type": "OSCButton"}
    for key, value in default_values.items():
        if key in fields_per_type["OSCButton"][0].keys():
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
def test_inscription(gui_load, qtbot):
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
    test_gui = StackedWindowGui("./test/osctest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == OSCButton:
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
    test_gui = StackedWindowGui("./test/osctest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == OSCButton:
            assert child.button.text() == ""
            child.button.click()
            QTest.qWait(1000)
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
    test_gui = StackedWindowGui("./test/osctest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == OSCButton:
            assert child.button.text() == "None"
            child.button.click()
            QTest.qWait(500)
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    # reset file
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().setText("Send message")
    assert gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().text() == "Send message"
    gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["inscription"] == "Send message"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(ins_pos, 1).widget().text() == "Send message"
    assert gui_load.structure["Page 1"]["Question 1"]["inscription"] == "Send message"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)

    os.remove("./test/results/results_osc.csv")
    gui_load.close()


# noinspection PyArgumentList
def test_address(gui_load, qtbot):
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
    adr_pos = find_row_by_label(gui_load.gui.edit_layout, 'address')

    # change text to without / -> warning
    gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().setText("send")
    assert gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().text() == "send"
    gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["address"] == "send"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().text() == "send"
    assert gui_load.structure["Page 1"]["Question 1"]["address"] == "send"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == True
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    QTimer.singleShot(150, handle_dialog_warning)
    test_gui = StackedWindowGui("./test/osctest.txt")
    assert test_gui.Stack.count() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    #  empty address -> error
    gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().setText("")
    assert gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().text() == ""
    gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["address"] == ""
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().text() == ""
    #assert gui_load.structure["Page 1"]["Question 1"]["address"] == "" #TODO??
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # reset file
    gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().setText("/message")
    assert gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().text() == "/message"
    gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["address"] == "/message"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(adr_pos, 1).widget().text() == "/message"
    assert gui_load.structure["Page 1"]["Question 1"]["address"] == "/message"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)

    os.remove("./test/results/results_osc.csv")
    gui_load.close()


# noinspection PyArgumentList
def test_value(gui_load, qtbot):
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
    val_pos = find_row_by_label(gui_load.gui.edit_layout, 'value')

    # change text
    gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().setText("send")
    assert gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().text() == "send"
    gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["value"] == "send"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().text() == "send"
    assert gui_load.structure["Page 1"]["Question 1"]["value"] == "send"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/osctest.txt")
    assert test_gui.Stack.count() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    #  empty value
    gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["value"] == ""
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().text() == ""
    #assert gui_load.structure["Page 1"]["Question 1"]["address"] == "" #TODO??
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # reset file
    gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().setText("Hello world!")
    assert gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().text() == "Hello world!"
    gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["value"] == "Hello world!"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(val_pos, 1).widget().text() == "Hello world!"
    assert gui_load.structure["Page 1"]["Question 1"]["value"] == "Hello world!"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)

    os.remove("./test/results/results_osc.csv")
    gui_load.close()


# noinspection PyArgumentList
def test_receiver(gui_load, qtbot):
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
    rec_pos = find_row_by_label(gui_load.gui.edit_layout, 'receiver')
    rec_cb = gui_load.gui.edit_layout.itemAt(rec_pos, 1).widget().layout().itemAt(0).widget()
    rec_ip = gui_load.gui.edit_layout.itemAt(rec_pos, 1).widget().layout().itemAt(1).widget().layout().itemAt(1).widget()
    rec_port = gui_load.gui.edit_layout.itemAt(rec_pos, 1).widget().layout().itemAt(1).widget().layout().itemAt(3).widget()

    QTest.mouseClick(rec_cb, Qt.LeftButton)
    QTest.keyClick(rec_cb, Qt.Key_Down)
    QTest.keyClick(rec_cb, Qt.Key_Enter)
    assert rec_cb.currentText() == "audio"
    assert rec_ip.isEnabled() == False
    assert rec_ip.text() == gui_load.structure["audio_ip"]
    assert rec_port.isEnabled() == False
    assert rec_port.text() == gui_load.structure["audio_port"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["receiver"] == ["127.0.0.1", "8000"]
    '''
    QTest.mouseClick(rec_cb, Qt.LeftButton)
    QTest.keyClick(rec_cb, Qt.Key_Down)
    QTest.keyClick(rec_cb, Qt.Key_Enter)
    assert rec_cb.currentText() == "help"
    assert rec_ip.isEnabled() == False
    assert rec_ip.text() == gui_load.structure["help_ip"]
    assert rec_port.isEnabled() == False
    assert rec_port.text() == gui_load.structure["help_port"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["receiver"] == ["", ""]
    '''
    QTest.mouseClick(rec_cb, Qt.LeftButton)
    QTest.keyClick(rec_cb, Qt.Key_Down)
    QTest.keyClick(rec_cb, Qt.Key_Enter)
    assert rec_cb.currentText() == "video"
    assert rec_ip.isEnabled() == False
    assert rec_ip.text() == gui_load.structure["video_ip"]
    assert rec_port.isEnabled() == False
    assert rec_port.text() == gui_load.structure["video_port"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["receiver"] == ["127.0.0.1", "5005"]

    # TODO test actual sending
    # revert file
    QTest.mouseClick(rec_cb, Qt.LeftButton)
    QTest.keyClick(rec_cb, Qt.Key_Up)
    QTest.keyClick(rec_cb, Qt.Key_Up)
    QTest.keyClick(rec_cb, Qt.Key_Up)
    QTest.keyClick(rec_cb, Qt.Key_Enter)
    assert rec_cb.currentText() == "<new>"
    assert rec_ip.isEnabled()
    assert rec_ip.text() == ""
    assert rec_port.isEnabled()
    assert rec_port.text() == ""
    rec_ip.clear()
    rec_ip.setText("127.0.0.1")
    assert rec_ip.text() == "127.0.0.1"
    rec_ip.editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["receiver"] == ["127.0.0.1", ""]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False
    rec_port.clear()
    rec_port.setText("8000")
    assert rec_port.text() == "8000"
    rec_port.editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["receiver"] == ["127.0.0.1", "8000"]
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["receiver"] == ["127.0.0.1", "8000"]
    gui_load.save()
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    if os.path.exists("./test/results/results_osc.csv"):
        os.remove("./test/results/results_osc.csv")
    assert run.Stack.count() == 1

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_osc.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'osc'
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == 'False'  # button not clicked
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_osc.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_blocked(run, qtbot):
    with mock_file(r'./test/results/results_osc.csv'):
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
                    assert lines[1] == 'osc'
                    assert lines[2] == 'Start'
                    assert lines[3] == 'End'
        assert len(results) == 4
        assert lines[0] == '-1'  # participant number unknown
        assert lines[1] == 'False'  # button not clicked
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
        os.remove(res_file)


# noinspection PyArgumentList
def test_execute_questionnaire(run, qtbot):
    if os.path.exists("./test/results/results_osc.csv"):
        os.remove("./test/results/results_osc.csv")
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if type(child) is OSCButton:
            child.button.click()

    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_osc.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'osc'
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == 'True'  # button was clicked
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_osc.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_blocked(run, qtbot):
    with mock_file(r'./test/results/results_osc.csv'):
        assert run.Stack.count() == 1
        for child in run.Stack.currentWidget().children():
            if type(child) is OSCButton:
                child.button.click()
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
                    assert lines[1] == 'osc'
                    assert lines[2] == 'Start'
                    assert lines[3] == 'End'
        assert len(results) == 4
        assert lines[0] == '-1'  # participant number unknown
        assert lines[1] == 'True'  # button not clicked
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
        os.remove(res_file)
