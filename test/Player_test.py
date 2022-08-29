"""Testing the behaviour of Player.py + QEditGui.py"""
# TODO how to test messages to REAPER

from context import *


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


@pytest.fixture
def run():
    """Execute the questionnaire."""
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
        if type(layout.itemAt(row, 1)) == QWidgetItem and layout.itemAt(row, 0).widget().text() == label:
            return row
        elif type(layout.itemAt(row, 1)) == QHBoxLayout:
            if layout.itemAt(row, 0).widget().text() == label:
                return row


# noinspection PyArgumentList
def test_create(gui_init, qtbot):
    # create a page
    assert gui_init.gui.page_add.isEnabled() == True
    QTest.qWait(500)

    QTimer.singleShot(200, handle_dialog_p)
    QTest.mouseClick(gui_init.gui.page_add, Qt.LeftButton, delay=1)
    tv = gui_init.gui.treeview
    # create a question
    tv.setCurrentItem(tv.topLevelItem(0).child(0))  # .setSelected(True)
    assert gui_init.gui.question_add.isEnabled() == True
    QTest.qWait(500)

    QTimer.singleShot(200, handle_dialog_q)
    QTest.mouseClick(gui_init.gui.question_add, Qt.LeftButton, delay=1)
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
    QTest.mouseClick(gui_init.gui.questiontype, Qt.LeftButton)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "Player"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if type(layout.itemAt(row, 1)) == QWidgetItem:
            not_none_rows += 1
            assert layout.itemAt(row, 0).widget().text() in fields_per_type["Player"][0].keys()
            assert str(type(layout.itemAt(row, 1).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["Player"][0][layout.itemAt(row, 0).widget().text()] == 'QPlainTextEdit'\
                   else fields_per_type["Player"][0][layout.itemAt(row, 0).widget().text()]
            if type(layout.itemAt(row, 1).widget()) == QLineEdit and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().text() == default_values[layout.itemAt(row, 0).widget().text()]
            elif type(layout.itemAt(row, 1).widget()) == QCheckBox and layout.itemAt(row, 0).widget().text() in \
                    default_values:
                assert layout.itemAt(row, 1).widget().isChecked() == default_values[
                    layout.itemAt(row, 0).widget().text()]
        elif type(layout.itemAt(row, 1)) == QHBoxLayout:
            not_none_rows += 1
            for cbs in range(layout.itemAt(row, 1).count()):
                assert layout.itemAt(row, 1).itemAt(cbs).widget().isChecked() == True

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
        if key in fields_per_type["Player"][0].keys():
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
    assert error_found == False
    assert warning_found == False
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(0))  # should be 'Question 1'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Question 1"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())
    sc_pos = find_row_by_label(gui_load.gui.edit_layout, 'start_cue')

    # try to set it as string
    gui_load.gui.edit_layout.itemAt(sc_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, 1).widget().setText("one")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, 1).widget().text() == "one"
    gui_load.gui.edit_layout.itemAt(sc_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cue"] == "one"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(sc_pos, 1).widget().text() == "one"
    assert gui_load.structure["Page 1"]["Question 1"]["start_cue"] == "one"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # try to set it as list
    gui_load.gui.edit_layout.itemAt(sc_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(sc_pos, 1).widget().setText("1,2")
    assert gui_load.gui.edit_layout.itemAt(sc_pos, 1).widget().text() == "1,2"
    gui_load.gui.edit_layout.itemAt(sc_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["start_cue"] == "1,2"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(sc_pos, 1).widget().text() == "1,2"
    assert gui_load.structure["Page 1"]["Question 1"]["start_cue"] == "1,2"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False
    QTimer.singleShot(150, handle_dialog_no_save)
    gui_load.close()


def test_end_cue(gui_load, qtbot):
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

    # try to set it as string
    gui_load.structure["Page 1"]["Question 1"]["end_cue"] = "one"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cue"] == "one"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # try to set it as list
    gui_load.structure["Page 1"]["Question 1"]["end_cue"] = "1,2"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cue"] == "1,2"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # try to set it same as start_cue
    gui_load.structure["Page 1"]["Question 1"]["end_cue"] = "1"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cue"] == "1"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # set value
    gui_load.structure["Page 1"]["Question 1"]["end_cue"] = "2"
    gui_load.gui.load_preview()
    # QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["end_cue"] == "2"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.close()


def test_track(gui_load, qtbot):
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
    track_pos = find_row_by_label(gui_load.gui.edit_layout, 'track')

    # try to set it as string
    gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().setText("one")
    assert gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().text() == "one"
    gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "one"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().text() == "one"
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "one"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # set it as list (shouldn't work as audio_tracks = 1 by default)
    gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().setText("1,2")
    assert gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().text() == "1,2"
    gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1,2"
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().text() == "1,2"
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == [1, 2]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False
    # but it works when audio_tracks is >= max(track)
    gui_load.structure["audio_tracks"] = 2
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.structure["audio_tracks"] = 1

    # set it as any number <= audio_tracks
    gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().setText("1")
    assert gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().text() == "1"
    gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == "1"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(track_pos, 1).widget().text() == "1"
    assert gui_load.structure["Page 1"]["Question 1"]["track"] == '1'
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTimer.singleShot(150, handle_dialog_no_save)
    gui_load.close()


# noinspection PyArgumentList
def test_play_once(gui_load, qtbot):
    if os.path.exists("./test/results/results_pl.csv"):
        os.remove("./test/results/results_pl.csv")

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
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center(), delay=1)
    po_pos = find_row_by_label(gui_load.gui.edit_layout, 'play_once')

    # set play_once to true
    assert gui_load.gui.edit_layout.itemAt(po_pos, 1).widget().isChecked() == False
    gui_load.gui.edit_layout.itemAt(po_pos, 1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(po_pos, 1).widget().isChecked() == True
    assert gui_load.structure["Page 1"]["Question 1"]["play_once"] == True
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier, delay=1)
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            assert child.play_button.isEnabled() == True
            assert child.pause_button.isEnabled() == False
            assert child.stop_button.isEnabled() == False
            child.play_button.click()
            assert child.play_button.isEnabled() == False
            assert child.pause_button.isEnabled() == True
            assert child.stop_button.isEnabled() == True
            child.pause_button.click()  # pause
            assert child.play_button.isEnabled() == False
            assert child.pause_button.isEnabled() == True
            assert child.stop_button.isEnabled() == True
            child.pause_button.click()  # unpause
            assert child.play_button.isEnabled() == False
            assert child.pause_button.isEnabled() == True
            assert child.stop_button.isEnabled() == True
            child.stop_button.click()  # stop
            assert child.play_button.isEnabled() == False
            assert child.pause_button.isEnabled() == False
            assert child.stop_button.isEnabled() == False
    test_gui.close()

    # reset file
    assert gui_load.gui.edit_layout.itemAt(po_pos, 1).widget().isChecked() == True
    gui_load.gui.edit_layout.itemAt(po_pos, 1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(po_pos, 1).widget().isChecked() == False
    assert gui_load.structure["Page 1"]["Question 1"]["play_once"] == False
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            assert child.play_button.isEnabled() == True
            assert child.pause_button.isEnabled() == False
            assert child.stop_button.isEnabled() == False
            child.play_button.click()
            QTest.qWait(100)
            assert child.play_button.isEnabled() == True
            assert child.pause_button.isEnabled() == True
            assert child.stop_button.isEnabled() == True
            child.pause_button.click()  # pause
            assert child.play_button.isEnabled() == True
            assert child.pause_button.isEnabled() == True
            assert child.stop_button.isEnabled() == True
            child.pause_button.click()  # unpause
            assert child.play_button.isEnabled() == True
            assert child.pause_button.isEnabled() == True
            assert child.stop_button.isEnabled() == True
            child.stop_button.click()  # stop
            assert child.play_button.isEnabled() == True
            assert child.pause_button.isEnabled() == False
            assert child.stop_button.isEnabled() == False
    test_gui.close()

    os.remove("./test/results/results_pl.csv")
    gui_load.close()


# noinspection PyArgumentList
@pytest.mark.pupil
def test_pupil(gui_load, qtbot, capfd):
    open_pupil()
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
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center(), delay=1)
    pupil_pos = find_row_by_label(gui_load.gui.edit_layout, 'pupil')

    assert gui_load.gui.edit_layout.itemAt(pupil_pos, 1).widget().text() == ''
    assert "pupil" not in gui_load.structure["Page 1"]["Question 1"].keys()

    # try to set pupil annotation text without setting global pupil ip/port
    gui_load.gui.edit_layout.itemAt(pupil_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(pupil_pos, 1).widget().setText("Custom Annotation")
    gui_load.gui.edit_layout.itemAt(pupil_pos, 1).widget().editingFinished.emit()
    # QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.load_preview()
    # QTimer.singleShot(200, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["pupil"] == "Custom Annotation"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == True

    # set pupil ip/port
    gui_load.structure["pupil_ip"] = "127.0.0.1"
    gui_load.structure["pupil_port"] = 50020
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier, delay=1)
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            child.play_button.click()
            QTest.qWait(1000)
            assert child.playing == True
            out, err = capfd.readouterr()
            assert out.index("Trigger {'topic': 'annotation', 'label': 'Custom Annotation', 'timestamp':") != -1
            assert out.endswith(", 'duration': 1} Message forwarded.\n") == True
            QTest.qWait(2000)

    QTest.qWait(3000)
    QTimer.singleShot(2000, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=150)
    QTest.qWait(3000)
    test_gui.close()
    os.remove("./test/results/results_pl.csv")

    # reset file
    gui_load.structure.pop("pupil_ip")
    gui_load.structure.pop("pupil_port")
    gui_load.gui.edit_layout.itemAt(pupil_pos, 1).widget().clear()
    gui_load.gui.edit_layout.itemAt(pupil_pos, 1).widget().editingFinished.emit()
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert "pupil" not in gui_load.structure["Page 1"]["Question 1"].keys()
    QTimer.singleShot(250, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier, delay=1)
    gui_load.close()


# noinspection PyArgumentList
def test_timer_and_two_pages(gui_load2, qtbot):
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
    QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center(), delay=1)
    time_pos = find_row_by_label(gui_load2.gui.edit_layout, 'timer')

    # set timer value
    assert gui_load2.gui.edit_layout.itemAt(time_pos, 1).widget().text() == ''
    gui_load2.gui.edit_layout.itemAt(time_pos, 1).widget().setText("one")
    gui_load2.gui.edit_layout.itemAt(time_pos, 1).widget().editingFinished.emit()
    assert gui_load2.gui.edit_layout.itemAt(time_pos, 1).widget().text() == 'one'
    assert gui_load2.structure["Page 1"]["Question 1"]["timer"] == 'one'
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert error_found == True
    assert warning_found == False
    gui_load2.gui.edit_layout.itemAt(time_pos, 1).widget().clear()
    assert gui_load2.gui.edit_layout.itemAt(time_pos, 1).widget().text() == ''
    gui_load2.gui.edit_layout.itemAt(time_pos, 1).widget().setText("1000")
    gui_load2.gui.edit_layout.itemAt(time_pos, 1).widget().editingFinished.emit()
    assert gui_load2.gui.edit_layout.itemAt(time_pos, 1).widget().text() == '1000'
    assert gui_load2.structure["Page 1"]["Question 1"]["timer"] == '1000'
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert error_found == False
    assert warning_found == False
    gui_load2.gui.refresh_button.click()
    QTest.keyClicks(gui_load2, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pltest2.txt")
    assert test_gui.Stack.count() == 2
    hidden = None
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QLineEdit:
            hidden = child
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            assert child.play_button.isEnabled() == True
            assert hidden.isHidden() == True
            assert hidden.isVisible() == False
            child.play_button.click()
            QTest.qWait(1111)
            assert child.play_button.isEnabled() == True
            assert child.timer.remainingTime() <= 0
            assert hidden.isHidden() == False
            assert hidden.isVisible() == True

    test_gui.close()

    # stop during playback
    test_gui = StackedWindowGui("./test/pltest2.txt")
    assert test_gui.Stack.count() == 2
    hidden = None
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QLineEdit:
            hidden = child
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            assert child.play_button.isEnabled() == True
            assert hidden.isHidden() == True
            assert hidden.isVisible() == False
            child.play_button.click()
            QTest.qWait(500)
            child.stop_button.click()
            assert hidden.isHidden() == True
            assert hidden.isVisible() == False
            QTest.qWait(700)
            assert hidden.isHidden() == True
            assert hidden.isVisible() == False
            # assert child.timer.remainingTime() <= 500
            assert child.countdown > 0
            assert child.countdown == 1000
            child.play_button.click()
            assert child.timer.remainingTime() >= 900  # timer is restarted
            QTest.qWait(500)
            assert hidden.isHidden() == True
            assert hidden.isVisible() == False
            QTest.qWait(700)
            assert child.timer.remainingTime() <= 0
            assert hidden.isHidden() == False
            assert hidden.isVisible() == True
    test_gui.close()

    # pause and resume during playback
    test_gui = StackedWindowGui("./test/pltest2.txt")
    assert test_gui.Stack.count() == 2
    hidden = None
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QLineEdit:
            hidden = child
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            assert child.play_button.isEnabled() == True
            assert hidden.isHidden() == True
            assert hidden.isVisible() == False
            child.play_button.click()
            QTest.qWait(500)
            child.pause_button.click()
            assert hidden.isHidden() == True
            assert hidden.isVisible() == False
            QTest.qWait(700)
            assert hidden.isHidden() == True
            assert hidden.isVisible() == False
            # assert child.timer.remainingTime() <= 500
            # assert child.timer.remainingTime() > 0
            assert child.countdown > 0
            assert child.countdown <= 500
            child.play_button.click()
            assert child.timer.remainingTime() <= 500  # timer is not restarted
            assert child.timer.remainingTime() > 0
            QTest.qWait(700)
            assert child.timer.remainingTime() <= 0
            assert hidden.isHidden() == False
            assert hidden.isVisible() == True
    test_gui.close()

    # reset file
    os.remove("./test/results/results_pl.csv")
    gui_load2.gui.edit_layout.itemAt(time_pos, 1).widget().clear()
    gui_load2.gui.edit_layout.itemAt(time_pos, 1).widget().editingFinished.emit()
    assert gui_load2.structure["Page 1"]["Question 1"]["timer"] == ''
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load2.structure)
    assert error_found == False
    assert warning_found == False
    gui_load2.gui.refresh_button.click()
    assert "timer" not in gui_load2.structure["Page 1"]["Question 1"].keys()
    QTest.keyClicks(gui_load2, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pltest2.txt")
    assert test_gui.Stack.count() == 2
    hidden = None
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == QLineEdit:
            hidden = child
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            assert child.play_button.isEnabled() == True
            assert hidden.isHidden() == False
            assert hidden.isVisible() == True
            child.play_button.click()
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')
        for lines in csv_file:
            results = lines
    assert len(results) == 5
    assert lines[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+]', lines[1])  # list of duration
    assert lines[2] == ''  # text field
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[4])  # timestamp
    os.remove("./test/results/results_pl.csv")
    gui_load2.close()


# noinspection PyArgumentList
def test_play_button_text(gui_load, qtbot):
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
    gui_load.structure["Page 1"]["Question 1"]["play_button_text"] = "Click me"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Question 1"]["play_button_text"] == "Click me"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    gui_load.gui.refresh_button.click()
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            assert child.play_button.text() == "Click me"

    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()

    # reset file
    gui_load.structure["Page 1"]["Question 1"].pop("play_button_text")
    assert "play_button_text" not in gui_load.structure["Page 1"]["Question 1"].keys()
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)

    os.remove("./test/results/results_pl.csv")
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    assert run.Stack.count() == 1

    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton)

    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert lines[0] == 'data_row_number'  # participant number
                assert lines[1] == 'pl'
                assert lines[2] == 'Start'
                assert lines[3] == 'End'
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert lines[1] == '[]'  # not played yet
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_pl.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_blocked(run, qtbot):
    with mock_file(r'./test/results/results_pl.csv'):
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
                    assert lines[1] == 'pl'
                    assert lines[2] == 'Start'
                    assert lines[3] == 'End'
        assert len(results) == 4
        assert lines[0] == '-1'  # participant number unknown
        assert lines[1] == '[]'  # not played yet
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
        os.remove(res_file)


# noinspection PyArgumentList
def test_execute_questionnaire(run, qtbot):
    if os.path.exists("./test/results/results_pl.csv"):
        os.remove("./test/results/results_pl.csv")
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if type(child) == Player:
            child.playing = False
            child.play_button.click()

    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.LeftButton, delay=1)

    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+]', lines[1])  # list of duration
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_pl.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_blocked(run, qtbot):
    with mock_file(r'./test/results/results_pl.csv'):
        assert run.Stack.count() == 1
        for child in run.Stack.currentWidget().children():
            if type(child) == Player:
                child.playing = False
                child.play_button.click()
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
                    assert lines[1] == 'pl'
                    assert lines[2] == 'Start'
                    assert lines[3] == 'End'
        assert len(results) == 4
        assert lines[0] == '-1'  # participant number unknown
        assert re.match(r'\[\d.\d+]', lines[1])
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
        os.remove(res_file)


# noinspection PyArgumentList
def test_buttons(gui_load, qtbot):
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
    btn_pos = find_row_by_label(gui_load.gui.edit_layout, 'buttons')

    for btn in range(gui_load.gui.edit_layout.itemAt(btn_pos, 1).count()):
        assert gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(btn).widget().isChecked() == True
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == player_buttons

    # try to add a non-defined button
    gui_load.structure["Page 1"]["Question 1"]["buttons"].append("Record")
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == True
    assert warning_found == False

    # no button chosen -> warning plus autoplay on load
    for btn in range(gui_load.gui.edit_layout.itemAt(btn_pos, 1).count()):
        gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(btn).widget().click()
        assert gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(btn).widget().isChecked() == False
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == []
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == True
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    QTimer.singleShot(150, handle_dialog_warning)
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            assert child.buttons == []
            assert child.playing == True

    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+]', lines[1])  # list of duration
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_pl.csv")

    # just stop button
    gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(2).widget().click()
    assert gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(2).widget().isChecked() == True
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == ["Stop"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == True
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    QTimer.singleShot(150, handle_dialog_warning)
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            assert child.buttons == ["Stop"]
            assert child.playing == True
            assert child.stop_button.isEnabled() == True
            assert child.stop_button is not None
            child.stop_button.click()
            assert child.playing == False
            assert child.stop_button.isEnabled() == False
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')
        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+]', lines[1])  # list of duration
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_pl.csv")

    # stop and pause
    gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(1).widget().isChecked() == True
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == ["Pause", "Stop"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == True
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    QTimer.singleShot(150, handle_dialog_warning)
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            assert child.buttons == ["Pause", "Stop"]
            assert child.playing == True
            assert child.pause_button.isEnabled() == True
            assert child.pause_button.isChecked() == False
            assert child.pause_button is not None
            assert child.stop_button.isEnabled() == True
            assert child.stop_button is not None
            child.pause_button.click()
            assert child.playing == False
            assert child.pause_button.isEnabled() == True
            assert child.pause_button.isChecked() == True
            assert child.pause_button is not None
            assert child.stop_button.isEnabled() == True
            assert child.stop_button is not None
            child.pause_button.click()
            assert child.playing == True
            assert child.pause_button.isEnabled() == True
            assert child.pause_button.isChecked() == False
            assert child.pause_button is not None
            assert child.stop_button.isEnabled() == True
            assert child.stop_button is not None
            child.stop_button.click()
            assert child.playing == False
            assert child.pause_button.isEnabled() == False
            assert child.stop_button.isEnabled() == False
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')
        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+, \d.\d+]', lines[1])  # list of duration
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_pl.csv")

    # just play button
    gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(2).widget().click()
    assert gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(2).widget().isChecked() == False
    gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(1).widget().click()
    assert gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(1).widget().isChecked() == False
    gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(0).widget().click()
    assert gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(0).widget().isChecked() == True
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == ["Play"]
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    test_gui = StackedWindowGui("./test/pltest.txt")
    assert test_gui.Stack.count() == 1
    for child in test_gui.Stack.currentWidget().children():
        if type(child) == Player:
            assert child.buttons == ["Play"]
            assert child.playing == False
            assert child.play_button is not None
            child.play_button.click()
            assert child.playing == True
            child.play_button.click()
    QTimer.singleShot(200, handle_dialog)
    QTest.mouseClick(test_gui.forwardbutton, Qt.LeftButton, delay=1)
    test_gui.close()
    results = []
    with open('./test/results/results_pl.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')
        for lines in csv_file:
            results = lines
    assert len(results) == 4
    assert lines[0] == '1'  # participant number
    assert re.match(r'\[\d.\d+, \d.\d+]', lines[1])  # list of duration
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[2])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', lines[3])  # timestamp
    os.remove("./test/results/results_pl.csv")

    # reset file
    for btn in range(gui_load.gui.edit_layout.itemAt(btn_pos, 1).count()):
        if not gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(btn).widget().isChecked():
            gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(btn).widget().click()
        assert gui_load.gui.edit_layout.itemAt(btn_pos, 1).itemAt(btn).widget().isChecked() == True
    assert gui_load.structure["Page 1"]["Question 1"]["buttons"] == player_buttons
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTest.keyClicks(gui_load, 's', modifier=Qt.ControlModifier)
    gui_load.close()


def test_video(gui_load, qtbot):
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
    vid_pos = find_row_by_label(gui_load.gui.edit_layout, 'video')

    assert gui_load.gui.edit_layout.itemAt(vid_pos, 1).widget().text() == ''
    vid_path = "./some_video.mp4"
    gui_load.gui.edit_layout.itemAt(vid_pos, 1).widget().setText(vid_path)
    gui_load.gui.edit_layout.itemAt(vid_pos, 1).widget().editingFinished.emit()
    assert gui_load.gui.edit_layout.itemAt(vid_pos, 1).widget().text() == vid_path
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == True

    # set video ip/port
    gui_load.structure["video_ip"] = "127.0.0.1"
    gui_load.structure["video_port"] = 5005
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found == False
    assert warning_found == False
    QTimer.singleShot(150, handle_dialog_no_save)
    gui_load.close()
    # TODO
