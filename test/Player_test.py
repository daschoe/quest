"""Testing the behaviour of Player.py + QEditGui.py"""
import time
from context import pytest, QEditGuiMain, QTimer, open_config_file, StackedWindowGui, QTest, handle_dialog_p, handle_dialog_q, Qt, QFormLayout, QWidgetItem, fields_per_type, default_values, QCheckBox, QLineEdit, page_fields, listify, ConfigObj, general_fields, handle_dialog_error, validate_questionnaire, handle_dialog_no_save, handle_dialog, csv, re, os, mock_file, Player, QHBoxLayout, MockReceiver, player_buttons, handle_dialog_warning, open_pupil
thread_audio = None
thread_video = None


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file("./test/pltest.txt"))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def gui_load2(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file("./test/pltest2.txt"))
    gui_init.load_file()
    return gui_init


def prepare_listeners(structure):
    """Set up the listeners for audio & video."""
    global thread_video
    global thread_audio
    print("setting up thread....")
    thread_audio = MockReceiver(int(structure["audio_port"]))
    if "video_port" in structure.keys() and structure["video_port"] != "":
        thread_video = MockReceiver(int(structure["video_port"]))
        QTest.qWait(1000)
        thread_video.start()
    QTest.qWait(1000)
    thread_audio.start()
    QTest.qWait(3000)


@pytest.fixture
def run():
    """Execute the questionnaire."""
    prepare_listeners(ConfigObj("./test/pltest.txt"))
    return StackedWindowGui("./test/pltest.txt")


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
    tv.setCurrentItem(tv.topLevelItem(0).child(0))  # .setSelected(True)
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
    # change the question type to 'Player'
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"
    QTest.mouseClick(gui_init.gui.questiontype, Qt.MouseButton.LeftButton)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "Player"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QWidgetItem):
            not_none_rows += 1
            assert layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in fields_per_type["Player"][0]
            assert str(type(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["Player"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()] == 'QPlainTextEdit'\
                   else fields_per_type["Player"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
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

    assert not_none_rows == len(fields_per_type["Player"][0].keys())
    assert len(gui_init.undo_stack) == 7  # 2 for creating page & question, 5 for choosing Player

    # Check structure
    structure = ConfigObj()  # {}
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    structure["Page 1"]["Question 1"] = {"type": "Player"}
    for key, value in default_values.items():
        if key in fields_per_type["Player"][0]:
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


def test_start_cue(gui_load, qtbot):
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
    sc_pos = find_row_by_label(gui_load.gui.edit_layout, 'start_cue')

    # try to set it as string
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cue"] == "one"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "one"
    assert gui_load.structure["Page 1"]["Question 1"]["start_cue"] == "one"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # try to set it as list
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1,2")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,2"
    gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cue"] == "1,2"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(sc_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "1,2"
    assert gui_load.structure["Page 1"]["Question 1"]["start_cue"] == "1,2"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found
    gui_load.structure["Page 1"]["Question 1"]["start_cue"] = "1"
    gui_load.save()
    gui_load.close()


def test_end_cue(gui_load, qtbot):
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
    gui_load.structure["Page 1"]["Question 1"]["end_cue"] = "one"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cue"] == "one"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # try to set it as list
    gui_load.structure["Page 1"]["Question 1"]["end_cue"] = "1,2"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cue"] == "1,2"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # try to set it same as start_cue
    gui_load.structure["Page 1"]["Question 1"]["end_cue"] = "1"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cue"] == "1"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # set value
    gui_load.structure["Page 1"]["Question 1"]["end_cue"] = "2"
    gui_load.gui.load_preview()
    # QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cue"] == "2"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    gui_load.structure["Page 1"]["Question 1"]["end_cue"] = ""
    gui_load.save()
    gui_load.close()


# noinspection PyArgumentList
def test_play_once(gui_load, qtbot):
    if os.path.exists("./test/results/results_pl.csv"):
        os.remove("./test/results/results_pl.csv")

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
    po_pos = find_row_by_label(gui_load.gui.edit_layout, 'play_once')

    # set play_once to true
    assert not gui_load.gui.edit_layout.itemAt(po_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    gui_load.gui.edit_layout.itemAt(po_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert gui_load.gui.edit_layout.itemAt(po_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["play_once"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest.txt"))
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    time.sleep(5)
    assert thread_audio.message_stack[-1] == ("/action", 40297)
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            assert child.play_button.isEnabled()
            assert not child.pause_button.isEnabled()
            assert not child.stop_button.isEnabled()
            child.play_button.click()
            time.sleep(5)
            assert thread_audio.message_stack[-5] == ("/action", 40161)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/stop", 0.0)
            assert not child.play_button.isEnabled()
            assert child.pause_button.isEnabled()
            assert child.stop_button.isEnabled()
            child.pause_button.click()  # pause
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 0.0)
            assert thread_audio.message_stack[-2] == ("/pause", 1.0)
            assert thread_audio.message_stack[-3] == ("/stop", 1.0)
            assert not child.play_button.isEnabled()
            assert child.pause_button.isEnabled()
            assert child.stop_button.isEnabled()
            child.pause_button.click()  # unpause
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/pause", 0.0)
            assert thread_audio.message_stack[-3] == ("/stop", 0.0)
            assert not child.play_button.isEnabled()
            assert child.pause_button.isEnabled()
            assert child.stop_button.isEnabled()
            child.stop_button.click()  # stop
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 0.0)
            assert thread_audio.message_stack[-2] == ("/stop", 1.0)
            assert not child.play_button.isEnabled()
            assert not child.pause_button.isEnabled()
            assert not child.stop_button.isEnabled()
    test_gui.close()
    thread_audio.stop(0.1)
    QTest.qWait(1000)

    # reset file
    assert gui_load.gui.edit_layout.itemAt(po_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    gui_load.gui.edit_layout.itemAt(po_pos, QFormLayout.ItemRole.FieldRole).widget().click()
    assert not gui_load.gui.edit_layout.itemAt(po_pos, QFormLayout.ItemRole.FieldRole).widget().isChecked()
    assert not gui_load.structure["Page 1"]["Question 1"]["play_once"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest.txt"))
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            assert child.play_button.isEnabled()
            assert not child.pause_button.isEnabled()
            assert not child.stop_button.isEnabled()
            child.play_button.click()
            time.sleep(5)
            assert thread_audio.message_stack[-5] == ("/action", 40161)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/stop", 0.0)
            assert child.play_button.isEnabled()
            assert child.pause_button.isEnabled()
            assert child.stop_button.isEnabled()
            child.pause_button.click()  # pause
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 0.0)
            assert thread_audio.message_stack[-2] == ("/pause", 1.0)
            assert thread_audio.message_stack[-3] == ("/stop", 1.0)
            assert child.play_button.isEnabled()
            assert child.pause_button.isEnabled()
            assert child.stop_button.isEnabled()
            child.pause_button.click()  # unpause
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/pause", 0.0)
            assert thread_audio.message_stack[-3] == ("/stop", 0.0)
            assert child.play_button.isEnabled()
            assert child.pause_button.isEnabled()
            assert child.stop_button.isEnabled()
            child.stop_button.click()  # stop
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 0.0)
            assert thread_audio.message_stack[-2] == ("/stop", 1.0)
            assert child.play_button.isEnabled()
            assert not child.pause_button.isEnabled()
            assert not child.stop_button.isEnabled()
    test_gui.close()
    thread_audio.stop(0.1)
    QTest.qWait(1000)

    os.remove("./test/results/results_pl.csv")
    gui_load.close()


# noinspection PyArgumentList
def test_timer_and_two_pages(gui_load2, qtbot):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert not error_found
    assert not warning_found
    tv = gui_load2.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center(), delay=1000)
    time_pos = find_row_by_label(gui_load2.gui.edit_layout, 'timer')

    # set timer value
    assert gui_load2.gui.edit_layout.itemAt(time_pos, QFormLayout.ItemRole.FieldRole).widget().text() == ''
    gui_load2.gui.edit_layout.itemAt(time_pos, QFormLayout.ItemRole.FieldRole).widget().setText("one")
    gui_load2.gui.edit_layout.itemAt(time_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load2.gui.edit_layout.itemAt(time_pos, QFormLayout.ItemRole.FieldRole).widget().text() == 'one'
    assert gui_load2.structure["Page 1"]["Question 1"]["timer"] == 'one'
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert error_found
    assert not warning_found
    gui_load2.gui.edit_layout.itemAt(time_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    assert gui_load2.gui.edit_layout.itemAt(time_pos, QFormLayout.ItemRole.FieldRole).widget().text() == ''
    gui_load2.gui.edit_layout.itemAt(time_pos, QFormLayout.ItemRole.FieldRole).widget().setText("1000")
    gui_load2.gui.edit_layout.itemAt(time_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load2.gui.edit_layout.itemAt(time_pos, QFormLayout.ItemRole.FieldRole).widget().text() == '1000'
    assert gui_load2.structure["Page 1"]["Question 1"]["timer"] == '1000'
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert not error_found
    assert not warning_found
    gui_load2.gui.refresh_button.click()
    QTest.keyClicks(gui_load2, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest2.txt"))
    test_gui = StackedWindowGui("./test/pltest2.txt")
    assert test_gui.Stack.count() == 2
    hidden = None
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, QLineEdit):
            hidden = child
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            assert child.play_button.isEnabled()
            assert hidden.isHidden()
            assert not hidden.isVisible()
            child.play_button.click()
            QTest.qWait(2000)
            assert child.play_button.isEnabled()
            assert child.timer.remainingTime() <= 0
            assert not hidden.isHidden()
            assert hidden.isVisible()
            time.sleep(2)
            assert thread_audio.message_stack[-5] == ("/action", 40161)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/stop", 0.0)

    QTest.qWait(3000)
    test_gui.close()
    thread_audio.stop(0.1)
    QTest.qWait(5000)

    # stop during playback
    prepare_listeners(ConfigObj("./test/pltest2.txt"))
    test_gui = StackedWindowGui("./test/pltest2.txt")
    assert test_gui.Stack.count() == 2
    hidden = None
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, QLineEdit):
            hidden = child
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            assert child.play_button.isEnabled()
            assert hidden.isHidden()
            assert not hidden.isVisible()
            child.play_button.click()
            QTest.qWait(500)
            child.stop_button.click()
            assert hidden.isHidden()
            assert not hidden.isVisible()
            time.sleep(5)
            assert thread_audio.message_stack[-7] == ("/action", 40161)
            assert thread_audio.message_stack[-3] == ("/play", 1.0)
            assert thread_audio.message_stack[-4] == ("/stop", 0.0)
            assert thread_audio.message_stack[-1] == ("/play", 0.0)
            assert thread_audio.message_stack[-2] == ("/stop", 1.0)
            QTest.qWait(700)
            assert hidden.isHidden()
            assert not hidden.isVisible()
            # assert child.timer.remainingTime() <= 500
            assert child.countdown > 0
            assert child.countdown == 1000
            child.play_button.click()
            assert child.timer.remainingTime() >= 900  # timer is restarted
            QTest.qWait(500)
            assert hidden.isHidden()
            assert not hidden.isVisible()
            QTest.qWait(700)
            assert child.timer.remainingTime() <= 0
            assert not hidden.isHidden()
            assert hidden.isVisible()
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/stop", 0.0)
            # TODO in reality REAPER should ping back stop, but this doesn't work with the MockReceiver
    test_gui.close()
    thread_audio.stop(0.1)
    QTest.qWait(1000)

    # pause and resume during playback
    prepare_listeners(ConfigObj("./test/pltest2.txt"))
    test_gui = StackedWindowGui("./test/pltest2.txt")
    assert test_gui.Stack.count() == 2
    hidden = None
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, QLineEdit):
            hidden = child
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            assert child.play_button.isEnabled()
            assert hidden.isHidden()
            assert not hidden.isVisible()
            child.play_button.click()
            QTest.qWait(500)
            child.pause_button.click()
            assert hidden.isHidden()
            assert not hidden.isVisible()
            QTest.qWait(700)
            assert hidden.isHidden()
            assert not hidden.isVisible()
            time.sleep(5)
            assert thread_audio.message_stack[-8] == ("/action", 40161)
            assert thread_audio.message_stack[-4] == ("/play", 1.0)
            assert thread_audio.message_stack[-5] == ("/stop", 0.0)
            assert thread_audio.message_stack[-1] == ("/play", 0.0)
            assert thread_audio.message_stack[-2] == ("/pause", 1.0)
            assert thread_audio.message_stack[-3] == ("/stop", 1.0)
            # assert child.timer.remainingTime() <= 500
            # assert child.timer.remainingTime() > 0
            assert child.countdown > 0
            assert child.countdown <= 500
            child.play_button.click()
            assert child.timer.remainingTime() <= 500  # timer is not restarted
            assert child.timer.remainingTime() > 0
            QTest.qWait(700)
            assert child.timer.remainingTime() <= 0
            assert not hidden.isHidden()
            assert hidden.isVisible()
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/pause", 0.0)
            assert thread_audio.message_stack[-3] == ("/stop", 0.0)
    test_gui.close()
    thread_audio.stop(0.1)
    QTest.qWait(1000)

    # reset file
    os.remove("./test/results/results_pl.csv")
    gui_load2.gui.edit_layout.itemAt(time_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load2.gui.edit_layout.itemAt(time_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load2.structure["Page 1"]["Question 1"]["timer"] == ''
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert not error_found
    assert not warning_found
    gui_load2.gui.refresh_button.click()
    assert "timer" not in gui_load2.structure["Page 1"]["Question 1"].keys()
    QTest.keyClicks(gui_load2, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest2.txt"))
    test_gui = StackedWindowGui("./test/pltest2.txt")
    assert test_gui.Stack.count() == 2
    hidden = None
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, QLineEdit):
            hidden = child
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            assert child.play_button.isEnabled()
            assert not hidden.isHidden()
            assert hidden.isVisible()
            child.play_button.click()
            time.sleep(5)
            assert thread_audio.message_stack[-5] == ("/action", 40161)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/stop", 0.0)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')
        for lines in csv_file:
            results = lines
    assert len(results) == 5
    assert results[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+]', results[1])  # list of duration
    assert results[2] == ''  # text field
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[4])  # timestamp
    os.remove("./test/results/results_pl.csv")
    thread_audio.stop(0.1)
    QTest.qWait(1000)
    gui_load2.close()


# noinspection PyArgumentList
def test_play_button_text(gui_load, qtbot):
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

    # change text
    gui_load.structure["Page 1"]["Question 1"]["play_button_text"] = "Click me"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["play_button_text"] == "Click me"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest.txt"))
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            assert child.play_button.text() == "Click me"
    time.sleep(5)
    assert thread_audio.message_stack[-1] == ("/action", 40297)
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    thread_audio.stop(0.1)
    QTest.qWait(1000)

    # reset file
    gui_load.structure["Page 1"]["Question 1"].pop("play_button_text")
    assert "play_button_text" not in gui_load.structure["Page 1"]["Question 1"].keys()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)

    os.remove("./test/results/results_pl.csv")
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    assert run.Stack.count() == 1

    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)

    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert results[0] == 'data_row_number'  # participant number
                assert results[1] == 'pl'
                assert results[2] == 'Start'
                assert results[3] == 'End'
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert results[1] == '[]'  # not played yet
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    assert thread_audio.message_stack[-1] == ("/action", 40297)
    os.remove("./test/results/results_pl.csv")
    thread_audio.stop(0.1)
    QTest.qWait(1000)


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_blocked(run, qtbot):
    with mock_file(r'./test/results/results_pl.csv'):
        assert run.Stack.count() == 1
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
                    assert results[1] == 'pl'
                    assert results[2] == 'Start'
                    assert results[3] == 'End'
        assert len(results) == 4
        assert results[0] == '-1'  # participant number unknown
        assert results[1] == '[]'  # not played yet
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
        assert thread_audio.message_stack[-1] == ("/action", 40297)
        os.remove(res_file)
        thread_audio.stop(0.1)
        QTest.qWait(1000)


# noinspection PyArgumentList
def test_execute_questionnaire(run, qtbot):
    if os.path.exists("./test/results/results_pl.csv"):
        os.remove("./test/results/results_pl.csv")
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if isinstance(child, Player):
            child.playing = False
            child.play_button.click()
            time.sleep(5)

            assert thread_audio.message_stack[-5] == ("/action", 40161)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/stop", 0.0)

    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)

    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+]', results[1])  # list of duration
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    os.remove("./test/results/results_pl.csv")
    thread_audio.stop(0.1)
    QTest.qWait(1000)


# noinspection PyArgumentList
def test_execute_questionnaire_blocked(run, qtbot):
    with mock_file(r'./test/results/results_pl.csv'):
        assert run.Stack.count() == 1
        for child in run.Stack.currentWidget().children():
            if isinstance(child, Player):
                child.playing = False
                child.play_button.click()
                time.sleep(5)
                assert thread_audio.message_stack[-5] == ("/action", 40161)
                assert thread_audio.message_stack[-1] == ("/play", 1.0)
                assert thread_audio.message_stack[-2] == ("/stop", 0.0)
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
                    assert results[1] == 'pl'
                    assert results[2] == 'Start'
                    assert results[3] == 'End'
        assert len(results) == 4
        assert results[0] == '-1'  # participant number unknown
        assert re.match(r'\[\d.\d+]', results[1])
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
        os.remove(res_file)
        thread_audio.stop(0.1)
        QTest.qWait(1000)


# noinspection PyArgumentList
def test_buttons(gui_load, qtbot):
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
    btn_pos = find_row_by_label(gui_load.gui.edit_layout, 'buttons')

    for btn in range(gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).count()):
        assert gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(btn).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == player_buttons

    # try to add a non-defined button
    gui_load.structure["Page 1"]["Question 1"]["buttons"].append("Record")
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    # no button chosen -> warning plus autoplay on load
    for btn in range(gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).count()):
        gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(btn).widget().click()
        assert not gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(btn).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == []
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest.txt"))
    QTest.qWait(2000)
    QTimer.singleShot(150, handle_dialog_warning)
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            assert child.buttons == []
            assert child.playing
    time.sleep(5)
    assert thread_audio.message_stack[-5] == ("/action", 40161)
    assert thread_audio.message_stack[-1] == ("/play", 1.0)
    assert thread_audio.message_stack[-2] == ("/stop", 0.0)
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    thread_audio.stop(0.1)
    QTest.qWait(1000)
    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+]', results[1])  # list of duration
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    os.remove("./test/results/results_pl.csv")

    # just stop button
    gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(2).widget().click()
    assert gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(2).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == ["Stop"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest.txt"))
    QTest.qWait(3000)
    QTimer.singleShot(150, handle_dialog_warning)
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    time.sleep(5)
    assert thread_audio.message_stack[-5] == ("/action", 40161)
    assert thread_audio.message_stack[-1] == ("/play", 1.0)
    assert thread_audio.message_stack[-2] == ("/stop", 0.0)
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            assert child.buttons == ["Stop"]
            assert child.playing
            assert child.stop_button.isEnabled()
            assert child.stop_button is not None
            child.stop_button.click()
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 0.0)
            assert thread_audio.message_stack[-2] == ("/stop", 1.0)
            assert not child.playing
            assert not child.stop_button.isEnabled()
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    thread_audio.stop(0.1)
    QTest.qWait(1000)
    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')
        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+]', results[1])  # list of duration
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    os.remove("./test/results/results_pl.csv")

    # stop and pause
    gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(1).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == ["Pause", "Stop"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest.txt"))
    QTimer.singleShot(150, handle_dialog_warning)
    test_gui = StackedWindowGui("./test/pltest.txt")
    time.sleep(5)
    assert thread_audio.message_stack[-5] == ("/action", 40161)
    assert thread_audio.message_stack[-1] == ("/play", 1.0)
    assert thread_audio.message_stack[-2] == ("/stop", 0.0)
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            assert child.buttons == ["Pause", "Stop"]
            assert child.playing
            assert child.pause_button.isEnabled()
            assert not child.pause_button.isChecked()
            assert child.pause_button is not None
            assert child.stop_button.isEnabled()
            assert child.stop_button is not None
            child.pause_button.click()
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 0.0)
            assert thread_audio.message_stack[-2] == ("/pause", 1.0)
            assert thread_audio.message_stack[-3] == ("/stop", 1.0)
            assert not child.playing
            assert child.pause_button.isEnabled()
            assert child.pause_button.isChecked()
            assert child.pause_button is not None
            assert child.stop_button.isEnabled()
            assert child.stop_button is not None
            child.pause_button.click()
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/pause", 0.0)
            assert thread_audio.message_stack[-3] == ("/stop", 0.0)
            assert child.playing
            assert child.pause_button.isEnabled()
            assert not child.pause_button.isChecked()
            assert child.pause_button is not None
            assert child.stop_button.isEnabled()
            assert child.stop_button is not None
            child.stop_button.click()
            time.sleep(5)
            assert thread_audio.message_stack[-1] == ("/play", 0.0)
            assert thread_audio.message_stack[-2] == ("/stop", 1.0)
            assert not child.playing
            assert not child.pause_button.isEnabled()
            assert not child.stop_button.isEnabled()
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    thread_audio.stop(0.1)
    QTest.qWait(1000)
    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')
        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+, \d.\d+]', results[1])  # list of duration
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    os.remove("./test/results/results_pl.csv")

    # just play button
    gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(2).widget().click()
    assert not gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(2).widget().isChecked()
    gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(1).widget().click()
    assert not gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(1).widget().isChecked()
    gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(0).widget().click()
    assert gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(0).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == ["Play"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest.txt"))
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            assert child.buttons == ["Play"]
            assert not child.playing
            assert child.play_button is not None
            child.play_button.click()
            time.sleep(5)
            assert thread_audio.message_stack[-5] == ("/action", 40161)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/stop", 0.0)
            assert child.playing
            child.play_button.click()
            time.sleep(5)
            assert thread_audio.message_stack[-5] == ("/action", 40161)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/stop", 0.0)
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    thread_audio.stop(0.1)
    QTest.qWait(1000)
    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')
        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert results[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+, \d.\d+]', results[1])  # list of duration
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[3])  # timestamp
    os.remove("./test/results/results_pl.csv")

    # reset file
    for btn in range(gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).count()):
        if not gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(btn).widget().isChecked():
            gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(btn).widget().click()
        assert gui_load.gui.edit_layout.itemAt(btn_pos, QFormLayout.ItemRole.FieldRole).itemAt(btn).widget().isChecked()
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == player_buttons
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load.close()


def test_video(gui_load2, qtbot):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert not error_found
    assert not warning_found
    tv = gui_load2.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())
    vid_pos = find_row_by_label(gui_load2.gui.edit_layout, 'video')

    assert gui_load2.gui.edit_layout.itemAt(vid_pos, QFormLayout.ItemRole.FieldRole).widget().text() == ''
    vid_path = "./some_video.mp4"
    gui_load2.gui.edit_layout.itemAt(vid_pos, QFormLayout.ItemRole.FieldRole).widget().setText(vid_path)
    gui_load2.gui.edit_layout.itemAt(vid_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load2.gui.edit_layout.itemAt(vid_pos, QFormLayout.ItemRole.FieldRole).widget().text() == vid_path
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert not error_found
    assert warning_found

    # set video ip/port
    gui_load2.structure["video_ip"] = "127.0.0.1"
    gui_load2.structure["video_port"] = 5005
    gui_load2.structure["video_player"] = "VLC"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert not error_found
    assert not warning_found

    gui_load2.gui.refresh_button.click()
    QTest.keyClicks(gui_load2, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest2.txt"))
    test_gui = StackedWindowGui("./test/pltest2.txt")
    assert test_gui.Stack.count() == 2
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            child.play_button.click()
            QTest.qWait(500)
            child.pause_button.click()
            QTest.qWait(500)
            child.play_button.click()
    QTest.qWait(2000)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    assert thread_video.message_stack[-6] == ("/vlc_start", './some_video.mp4')
    assert thread_video.message_stack[-5] == ("/vlc_pause", 1)
    assert thread_video.message_stack[-4] == ("/vlc_play", 1)
    assert thread_video.message_stack[-3] == ("/vlc_stop", 1)
    assert thread_video.message_stack[-2] == ("/vlc_still", 1)
    assert thread_video.message_stack[-1] == ("/vlc_finish", 1)
    print(thread_video.message_stack)
    thread_audio.stop(0.1)
    thread_video.stop(0.1)
    QTest.qWait(1000)
    os.remove("./test/results/results_pl.csv")

    # MadMapper
    gui_load2.structure["video_player"] = "MadMapper"
    gui_load2.gui.refresh_button.click()
    QTest.keyClicks(gui_load2, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest2.txt"))
    test_gui = StackedWindowGui("./test/pltest2.txt")
    assert test_gui.Stack.count() == 2
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            child.play_button.click()
            QTest.qWait(500)
            child.pause_button.click()
            QTest.qWait(500)
            child.play_button.click()
    QTest.qWait(2000)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=1000)
    test_gui.close()
    print(thread_video.message_stack)  # the reply is a bis fucked up since it is configured for Reaper
    assert thread_video.message_stack[0] == ("/medias/selected/position_sec", 0.0)
    assert thread_video.message_stack[1] == ('/cues/Bank-1/scenes/by_name/./some_video.mp4', 1)
    assert thread_video.message_stack[3] == ("/play", 1)
    assert thread_video.message_stack[5] == ("/pause", 1)
    assert thread_video.message_stack[8] == ("/play", 1)
    assert thread_video.message_stack[13] == ("/pause", 1)  # equals stop
    thread_audio.stop(0.1)
    thread_video.stop(0.1)
    QTest.qWait(1000)
    os.remove("./test/results/results_pl.csv")

    gui_load2.structure.pop("video_ip")
    gui_load2.structure.pop("video_port")
    gui_load2.structure.pop("video_player")
    gui_load2.structure["Page 1"]["Question 1"].pop("video")
    QTest.keyClicks(gui_load2, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load2.close()


# noinspection PyArgumentList
@pytest.mark.pupil
def test_pupil(gui_load, qtbot, capfd):
    open_pupil()
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
    pupil_pos = find_row_by_label(gui_load.gui.edit_layout, 'pupil')

    assert gui_load.gui.edit_layout.itemAt(pupil_pos, QFormLayout.ItemRole.FieldRole).widget().text() == ''
    assert "pupil" not in gui_load.structure["Page 1"]["Question 1"].keys()

    # try to set pupil annotation text without setting global pupil ip/port
    gui_load.gui.edit_layout.itemAt(pupil_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(pupil_pos, QFormLayout.ItemRole.FieldRole).widget().setText("Custom Annotation")
    gui_load.gui.edit_layout.itemAt(pupil_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    # QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    # QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["pupil"] == "Custom Annotation"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert warning_found

    # set pupil ip/port
    gui_load.structure["pupil_ip"] = "127.0.0.1"
    gui_load.structure["pupil_port"] = 50020
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    prepare_listeners(ConfigObj("./test/pltest.txt"))
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Player):
            child.play_button.click()
            time.sleep(5)
            assert thread_audio.message_stack[-5] == ("/action", 40161)
            assert thread_audio.message_stack[-1] == ("/play", 1.0)
            assert thread_audio.message_stack[-2] == ("/stop", 0.0)
            QTest.qWait(1000)
            assert child.playing
            out, err = capfd.readouterr()
            print(out, err)
            assert out.index("Trigger {'topic': 'annotation', 'label': 'Custom Annotation', 'timestamp':") != -1
            assert out.endswith(", 'duration': 1} Message forwarded.\n")
            QTest.qWait(2000)

    QTest.qWait(3000)
    QTimer.singleShot(2000, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.MouseButton.LeftButton, delay=150)
    QTest.qWait(3000)
    test_gui.close()
    thread_audio.stop(0.1)
    QTest.qWait(1000)
    os.remove("./test/results/results_pl.csv")

    # reset file
    gui_load.structure.pop("pupil_ip")
    gui_load.structure.pop("pupil_port")
    gui_load.gui.edit_layout.itemAt(pupil_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(pupil_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert "pupil" not in gui_load.structure["Page 1"]["Question 1"].keys()
    QTimer.singleShot(250, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.qWait(2000)
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    QTest.qWait(1000)
    gui_load.close()
