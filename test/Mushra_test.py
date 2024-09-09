"""Testing the behaviour of MUSHRA.py + QEditGui.py"""
import time
from context import pytest, MUSHRA, QPoint, QEditGuiMain, QTimer, open_config_file, StackedWindowGui, QTest, handle_dialog_p, handle_dialog_q, Qt, QFormLayout, QWidgetItem, fields_per_type, default_values, QCheckBox, QLineEdit, page_fields, listify, ConfigObj, general_fields, handle_dialog_error, validate_questionnaire, handle_dialog_no_save, handle_dialog, csv, re, os, mock_file, MockReceiver, QHBoxLayout
THREAD = None


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file("./test/mrtest.txt"))
    gui_init.load_file()
    return gui_init


def prepare_listeners(structure):
    """Set up the listeners for Reaper"""
    global THREAD
    print("setting up thread....")
    THREAD = MockReceiver(int(structure["audio_port"]))
    QTest.qWait(1000)
    THREAD.start()
    QTest.qWait(3000)


@pytest.fixture
def run():
    """Execute the questionnaire."""
    global THREAD
    structure = ConfigObj("./test/osctest.txt")
    port = int(structure["Page 1"]["Question 1"]["receiver"][1])
    print("setting up thread....")
    # if thread is None or (thread is not None and thread.port != port):
    THREAD = MockReceiver(port)
    QTest.qWait(1000)
    THREAD.start()
    QTest.qWait(1000)
    # elif thread is not None and not thread.is_alive():
    #    thread.start()
    # start_server(port)
    return StackedWindowGui("./test/mrtest.txt")


def find_row_by_label(layout, label):
    """
    Search for row with label in QFormLayout

    Parameters
    ----------
    layout: QFormLayout
        QFormLayout to be searched
    label: str
        label of the field

    Returns
    -------
    int
        row of the field
    """
    for row in range(layout.rowCount()):
        if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QWidgetItem) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() == label:
            return row
        elif isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QHBoxLayout):
            if layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() == label:
                return row


# noinspection PyArgumentList
def test_create(gui_init, qtbot):
    # create a page
    assert gui_init.gui.page_add.isEnabled()
    QTest.qWait(500)

    QTimer.singleShot(200, handle_dialog_p)
    QTest.mouseClick(gui_init.gui.page_add, Qt.MouseButton.LeftButton, delay=1000)
    tv = gui_init.gui.treeview
    # create a question
    tv.setCurrentItem(tv.topLevelItem(0).child(0))
    assert gui_init.gui.question_add.isEnabled()
    QTest.qWait(500)

    QTimer.singleShot(200, handle_dialog_q)
    QTest.mouseClick(gui_init.gui.question_add, Qt.MouseButton.LeftButton, delay=1000)
    assert tv.itemAt(0, 0).text(0) == "<new questionnaire>"
    assert tv.topLevelItemCount() == 1
    assert tv.topLevelItem(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).childCount() == 1
    assert tv.topLevelItem(0).child(0).text(0) == "Page 1"
    assert tv.topLevelItem(0).child(0).child(0).childCount() == 0
    assert tv.topLevelItem(0).child(0).child(0).text(0) == "Question 1"
    assert len(gui_init.undo_stack) == 2
    # change the question type to 'MUSHRA'
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
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "MUSHRA"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QWidgetItem):
            not_none_rows += 1
            assert layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in fields_per_type["MUSHRA"][0]
            assert str(type(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["MUSHRA"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()] == 'QPlainTextEdit'\
                   else fields_per_type["MUSHRA"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
            if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QLineEdit) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().text() == default_values[layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
            elif isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QCheckBox) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().isChecked() == default_values[
                    layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
        elif isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QHBoxLayout):
            not_none_rows += 1
            for cbs in range(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).count()):
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).itemAt(cbs).widget().isChecked()

    assert not_none_rows == len(fields_per_type["MUSHRA"][0].keys())
    assert len(gui_init.undo_stack) == 8  # 2 for creating page & question, 6 for choosing MUSHRA

    # Check structure
    structure = ConfigObj()  # {}
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    structure["Page 1"]["Question 1"] = {"type": "MUSHRA"}
    for key, value in default_values.items():
        if key in fields_per_type["MUSHRA"][0]:
            structure["Page 1"]["Question 1"][key] = value
    listify(gui_init.structure)
    listify(structure)

    QTimer.singleShot(200, handle_dialog_error)
    validate_questionnaire(gui_init.structure, suppress=True)
    QTimer.singleShot(200, handle_dialog_error)
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

    # try to set it as string
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "one"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one"
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "one"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # set it as list shorter than end_cues
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1,2")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,2"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "1,2"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,2"
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == (1, 2)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found  # len(start_cues)==2, len(end_cues)==3
    assert not warning_found
    gui_load.structure["Page 1"]["Question 1"]["start_cues"] = [1, 2, 3]
    gui_load.save()
    gui_load.close()


def test_end_cues(gui_load, qtbot):
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

    # try to set it as string
    gui_load.structure["Page 1"]["Question 1"]["end_cues"] = "one"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cues"] == "one"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # try to set it as list shorter than start_cues
    gui_load.structure["Page 1"]["Question 1"]["end_cues"] = "1,2"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cues"] == (1, 2)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # try to set it same as start_cues
    end_pos = find_row_by_label(gui_load.gui.edit_layout, 'end_cues')
    gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().setText("5, 2, 6")
    assert gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "5, 2, 6"
    gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    gui_load.structure["Page 1"]["Question 1"]["end_cues"] = "5, 2, 6"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cues"] == (5, 2, 6)
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found
    
    gui_load.structure["Page 1"]["Question 1"]["end_cues"] = (4, 5, 6)
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
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

    # try to set it as string
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "one"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one"
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "one"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # set it as list (shouldn't work as audio_tracks = 4 by default)
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1,2,3,4,5")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,2,3,4,5"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1,2,3,4,5"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,2,3,4,5"
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == [1, 2, 3, 4, 5]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found
    # but it works when audio_tracks is >= max(track)
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1,2,3")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,2,3"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1,2,3"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,2,3"
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == [1, 2, 3]
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    # only one -> all the same track
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1"
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == '1'
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    # len(start/end_cues)>len(track)>1 -> error
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1,1")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,1"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1,1"
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,1"
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == [1, 1]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found
    
    gui_load.structure["Page 1"]["Question 1"]["track"] = [1, 1, 1]
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load.close()


# noinspection PyArgumentList
def test_xfade(gui_load, qtbot):
    if os.path.exists("./test/results/results_mr.csv"):
        os.remove("./test/results/results_mr.csv")

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
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center(), delay=1000)
    x_pos = find_row_by_label(gui_load.gui.edit_layout, 'xfade')
    start_pos = find_row_by_label(gui_load.gui.edit_layout, 'start_cues')
    end_pos = find_row_by_label(gui_load.gui.edit_layout, 'end_cues')
    track_pos = find_row_by_label(gui_load.gui.edit_layout, 'track')

    # set xfade to true
    assert not gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["xfade"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found  # start and end need to be the same for all cues
    assert not warning_found
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1,1,1")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,1,1"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "1,1,1"
    gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().setText("2,2,2")
    assert gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "2,2,2"
    gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cues"] == "2,2,2"
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found  # need to change tracks from all 1
    assert not warning_found
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1,1,2")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,1,2"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1,1,2"
    gui_load.gui.refresh_button.click()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/mrtest.txt"))
    test_gui = StackedWindowGui("./test/mrtest.txt")
    assert test_gui.Stack.count() == 1
    time.sleep(1)
    assert THREAD.message_stack[-1] == ("/action", MUSHRA.loop_off_command)
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, MUSHRA):
            assert child.loop_button.isEnabled()
            assert not child.loop_button.isChecked()
            assert child.xfade.isEnabled()
            assert not child.xfade.isChecked()
            assert not child.pause_button.isEnabled()
            assert not child.stop_button.isEnabled()
            child.refbutton.click()
            time.sleep(5)
            assert THREAD.message_stack[-6] == ('/track/1/mute', 0.0)
            assert THREAD.message_stack[-3] == ("/action", 40161)
            assert THREAD.message_stack[-1] == ("/play", 1.0)
            assert THREAD.message_stack[-2] == ("/stop", 0.0)
            assert not child.loop_button.isEnabled()
            assert not child.loop_button.isChecked()
            child.stop_button.click()
            time.sleep(5)
            assert THREAD.message_stack[-1] == ("/play", 0.0)
            assert THREAD.message_stack[-2] == ("/stop", 1.0)
            assert child.loop_button.isEnabled()
            assert not child.loop_button.isChecked()
            child.loop_button.click()
            time.sleep(5)
            assert THREAD.message_stack[-1] == ('/action', MUSHRA.loop_on_command)
            assert child.loop_button.isEnabled()
            assert child.loop_button.isChecked()
            for sl, btn in enumerate(child.buttons):
                btn.click()  # starts each stimulus
                assert not child.loop_button.isEnabled()
                assert child.loop_button.isChecked()
                time.sleep(5)
                assert THREAD.message_stack[-9] == (f'/track/{sl + 1}/mute', 0.0)
                assert THREAD.message_stack[-6] == ("/action", 40162)
                assert THREAD.message_stack[-5] == ("/action", 40223)
                assert THREAD.message_stack[-4] == ("/action", 40161)
                assert THREAD.message_stack[-3] == ("/action", 40222)
                assert THREAD.message_stack[-1] == ("/play", 1.0)
                assert THREAD.message_stack[-2] == ("/stop", 0.0)
                bb = child.sliders[sl].rect()
                QTest.mouseClick(child.sliders[sl], Qt.MouseButton.LeftButton, pos=QPoint(bb.center().x(), int(bb.bottom() - 0.1 * (sl + 1) * bb.bottom())))
            child.stop_button.click()
            assert child.loop_button.isEnabled()
            assert child.loop_button.isChecked()
            child.loop_button.click()
            assert child.loop_button.isEnabled()
            assert not child.loop_button.isChecked()
    test_gui.close()
    THREAD.stop(0.1)
    QTest.qWait(1000)

    # reset file
    assert gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert not gui_load.gui.edit_layout.itemAt(x_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    assert not gui_load.structure["Page 1"]["Question 1"]["xfade"]
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1,2,3")
    assert gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,2,3"
    gui_load.gui.edit_layout.itemAt(start_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cues"] == "1,2,3"
    gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().setText("4,5,6")
    assert gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "4,5,6"
    gui_load.gui.edit_layout.itemAt(end_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cues"] == "4,5,6"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1,1,1")
    assert gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,1,1"
    gui_load.gui.edit_layout.itemAt(track_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1,1,1"
    gui_load.gui.refresh_button.click()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)

    os.remove("./test/results/results_mr.csv")
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    assert run.Stack.count() == 1
    assert THREAD.message_stack[-1] == ("/action", MUSHRA.loop_off_command)

    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)

    results = []
    with open('./test/results/results_mr.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert results[0] == 'data_row_number'  # participant number
                assert results[1] == 'mr'
                assert results[2] == 'mr_1'
                assert results[3] == 'mr_2'
                assert results[4] == 'Start'
                assert results[5] == 'End'
    assert len(results) == 6
    assert results[0] == '1'  # participant number
    assert results[1] == '[[], [], []]'  # no stimulus played yet
    assert results[2] == '100'  # default slider value
    assert results[3] == '100'  # default slider value
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[4])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[5])  # timestamp
    os.remove("./test/results/results_mr.csv")
    THREAD.stop(0.1)
    QTest.qWait(1000)


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_blocked(run, qtbot):
    with mock_file(r'./test/results/results_mr.csv'):
        assert run.Stack.count() == 1
        assert THREAD.message_stack[-1] == ("/action", MUSHRA.loop_off_command)
        QTimer.singleShot(100, handle_dialog)
        QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)
        res_file = None
        for file in os.listdir("./test/results/"):
            if file.find("_backup_"):
                res_file = f'./test/results/{file}'
        results = []
        with open(res_file, mode='r') as file:
            csv_file = csv.reader(file, delimiter=';')

            for lines in csv_file:
                results = lines
                if results[0].startswith('data'):
                    assert results[0] == 'data_row_number'  # participant number
                    assert results[1] == 'mr'
                    assert results[2] == 'mr_1'
                    assert results[3] == 'mr_2'
                    assert results[4] == 'Start'
                    assert results[5] == 'End'
        assert len(results) == 6
        assert results[0] == '-1'  # participant number unknown
        assert results[1] == '[[], [], []]'  # no stimulus played yet
        assert results[2] == '100'  # default slider value
        assert results[3] == '100'  # default slider value
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[4])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[5])  # timestamp
        os.remove(res_file)
        THREAD.stop(0.1)
        QTest.qWait(1000)


# noinspection PyArgumentList
def test_execute_questionnaire(run, qtbot):
    if os.path.exists("./test/results/results_mr.csv"):
        os.remove("./test/results/results_mr.csv")
    assert run.Stack.count() == 1
    assert THREAD.message_stack[-1] == ("/action", MUSHRA.loop_off_command)
    for child in run.Stack.currentWidget().children():
        if isinstance(child, MUSHRA):
            assert not child.conditionsUseSameMarker
            assert not hasattr(child, 'xfade')
            assert not child.playing
            child.refbutton.click()
            for sl in range(len(child.buttons)):
                assert not child.sliders[sl].isEnabled()
            for sl, btn in enumerate(child.buttons):
                btn.click()  # starts each stimulus
                QTest.qWait(500)
                bb = child.sliders[sl].rect()
                QTest.mouseClick(child.sliders[sl], Qt.MouseButton.LeftButton, pos=QPoint(bb.center().x(), int(bb.bottom() - 0.1 * (sl + 1) * bb.bottom())))

    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)

    results = []
    with open('./test/results/results_mr.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 6
    assert results[0] == '1'  # participant number
    assert re.match(r'\[\[\d.\d+], \[\d.\d+], \[\d.\d+]]', results[1])  # list of durations
    assert int(results[2]) < int(results[3])
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[4])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[5])  # timestamp
    os.remove("./test/results/results_mr.csv")
    THREAD.stop(0.1)
    QTest.qWait(1000)


# noinspection PyArgumentList
def test_execute_questionnaire_blocked(run, qtbot):
    with mock_file(r'./test/results/results_mr.csv'):
        assert run.Stack.count() == 1
        assert THREAD.message_stack[-1] == ("/action", MUSHRA.loop_off_command)
        for child in run.Stack.currentWidget().children():
            if isinstance(child, MUSHRA):
                assert not child.conditionsUseSameMarker
                assert not hasattr(child, 'xfade')
                assert not child.playing
                child.refbutton.click()
                for sl in range(len(child.buttons)):
                    assert not child.sliders[sl].isEnabled()
                for sl, btn in enumerate(child.buttons):
                    btn.click()  # starts each stimulus
                    QTest.qWait(500)
                    bb = child.sliders[sl].rect()
                    QTest.mouseClick(child.sliders[sl], Qt.MouseButton.LeftButton, pos=QPoint(bb.center().x(), int(bb.bottom() - 0.1 * (sl + 1) * bb.bottom())))
        QTimer.singleShot(100, handle_dialog)
        QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)
        res_file = None
        for file in os.listdir("./test/results/"):
            if file.find("_backup_"):
                res_file = f'./test/results/{file}'
        results = []
        with open(res_file, mode='r') as file:
            csv_file = csv.reader(file, delimiter=';')

            for lines in csv_file:
                results = lines
                if results[0].startswith('data'):
                    assert results[0] == 'data_row_number'  # participant number
                    assert results[1] == 'mr'
                    assert results[2] == 'mr_1'
                    assert results[3] == 'mr_2'
                    assert results[4] == 'Start'
                    assert results[5] == 'End'
        assert len(results) == 6
        assert results[0] == '-1'  # participant number unknown
        assert re.match(r'\[\[\d.\d+], \[\d.\d+], \[\d.\d+]]', results[1])  # list of durations
        assert int(results[2]) < int(results[3])
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[4])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[5])  # timestamp
        os.remove(res_file)
        THREAD.stop(0.1)
        QTest.qWait(1000)
