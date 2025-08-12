"""Testing the behaviour of Image.py + QEditGui.py"""

from context import pytest, QEditGuiMain, QTimer, open_config_file, StackedWindowGui, QTest, handle_dialog_p, handle_dialog_q, QHBoxLayout, keyboard, Qt, QFormLayout, QWidgetItem, fields_per_type, default_values, QCheckBox, QLineEdit, page_fields, listify, ConfigObj, general_fields, handle_dialog_error, validate_questionnaire, handle_dialog_no_save, find_row_by_label, handle_dialog, csv, re, os, mock_file, Image


@pytest.fixture
def gui_init():
    """Start GUI"""
    gui = QEditGuiMain()
    return gui


@pytest.fixture
def gui_load(gui_init):
    """Start GUI"""
    QTimer.singleShot(150, lambda: open_config_file("./test/imgtest.txt"))
    gui_init.load_file()
    return gui_init


@pytest.fixture
def run():
    """Execute the questionnaire."""
    return StackedWindowGui("./test/imgtest.txt")


# noinspection PyArgumentList
def test_create(gui_init, qtbot):
    # create a page
    assert gui_init.gui.page_add.isEnabled()
    QTest.qWait(500)

    QTimer.singleShot(100, handle_dialog_p)
    QTest.mouseClick(gui_init.gui.page_add, Qt.MouseButton.LeftButton, delay=1000)
    tv = gui_init.gui.treeview
    # create a question
    tv.setCurrentItem(tv.topLevelItem(0).child(0))
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
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Down)
    QTest.keyClick(gui_init.gui.questiontype, Qt.Key.Key_Enter)
    assert gui_init.gui.questiontype.currentText() == "Image"
    # check if the layout is correct, if all needed fields are loaded and have correct default values (if applicable)
    layout = gui_init.gui.edit_layout
    not_none_rows = 0
    for row in range(layout.rowCount()):
        if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QWidgetItem):
            not_none_rows += 1
            assert layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in fields_per_type["Image"][0]
            assert str(type(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget())).strip("'<>").rsplit(".", 1)[1] == \
                   'TextEdit' if fields_per_type["Image"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()] == 'QPlainTextEdit' else fields_per_type["Image"][0][layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
            if isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QLineEdit) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().text() == default_values[layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
            elif isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget(), QCheckBox) and layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text() in \
                    default_values:
                assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).widget().isChecked() == default_values[
                    layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
        elif isinstance(layout.itemAt(row, QFormLayout.ItemRole.FieldRole), QHBoxLayout) and \
                gui_init.gui.img_layout == layout.itemAt(row, QFormLayout.ItemRole.FieldRole):
            not_none_rows += 1
            assert layout.itemAt(row, QFormLayout.ItemRole.FieldRole).itemAt(1).widget().text() == default_values[
                layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().text()]
    assert not_none_rows == len(fields_per_type["Image"][0].keys())
    assert len(gui_init.undo_stack) == 14  # 2 for creating page & question, 12 for choosing Image

    # Check structure
    structure = ConfigObj()  # {}
    for key, value in default_values.items():
        if key in general_fields and value != "":
            structure[key] = value
    structure["Page 1"] = {}
    for key, value in default_values.items():
        if key in page_fields:
            structure["Page 1"][key] = value
    structure["Page 1"]["Question 1"] = {"type": "Image"}
    for key, value in default_values.items():
        if key in fields_per_type["Image"][0]:
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
def test_file(gui_load, qtbot):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(1))  # should be 'Image'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Image"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())
    img_str = find_row_by_label(gui_load.gui.edit_layout, 'image_file')
    imgfile = gui_load.gui.edit_layout.itemAt(img_str[0], QFormLayout.ItemRole.FieldRole).itemAt(img_str[1]).widget().text()
    assert imgfile == './src/Configs/Logo.png'

    def handle_file_chooser():
        """Type filename."""
        keyboard.write("Logo.png")
        keyboard.press("enter")

    img_btn = gui_load.gui.edit_layout.itemAt(find_row_by_label(gui_load.gui.edit_layout, 'image_file_btn')[0], QFormLayout.ItemRole.FieldRole).itemAt(0).widget()
    QTimer.singleShot(100, handle_file_chooser)
    QTest.mouseClick(img_btn, Qt.MouseButton.LeftButton)

    imgfile = gui_load.gui.edit_layout.itemAt(img_str[0], QFormLayout.ItemRole.FieldRole).itemAt(img_str[1]).widget().text()
    assert imgfile.endswith("Logo.png")

    QTimer.singleShot(150, handle_dialog_no_save)
    gui_load.close()


# noinspection PyArgumentList
def test_scale(gui_load, qtbot):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(1))  # should be 'Image'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Image"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())
    width_pos = find_row_by_label(gui_load.gui.edit_layout, 'width')
    height_pos = find_row_by_label(gui_load.gui.edit_layout, 'height')

    gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().insert("99")
    assert gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "99"
    gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["width"] == "99"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "99"
    assert gui_load.structure["Page 1"]["Image"]["width"] == "99"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().insert("99")
    assert gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "99"
    gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["height"] == "99"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "99"
    assert gui_load.structure["Page 1"]["Image"]["height"] == "99"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    QTest.qWait(2000)
    test_gui = StackedWindowGui("./test/imgtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Image):
            assert child.width() == 99
            assert child.height() == 99
    test_gui.close()

    #  -------- -1 ---------
    gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().insert("-1")
    assert gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "-1"
    gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["width"] == "-1"
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "-1"
    assert gui_load.structure["Page 1"]["Image"]["width"] == "-1"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found
    gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().insert("-1")
    assert gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "-1"
    gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["height"] == "-1"
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "-1"
    assert gui_load.structure["Page 1"]["Image"]["height"] == "-1"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    #  ---------0--------
    gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().insert("0")
    assert gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0"
    gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["width"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(width_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Image"]["width"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found
    gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().clear()
    gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().insert("0")
    assert gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0"
    gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["height"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(height_pos, QFormLayout.ItemRole.FieldRole).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Image"]["height"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    gui_load.structure["Page 1"]["Image"]["height"] = 100
    gui_load.structure["Page 1"]["Image"]["width"] = 250
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    QTest.qWait(2000)
    gui_load.close()
    os.remove("./test/results/results_img.csv")


# noinspection PyArgumentList
def test_move(gui_load, qtbot):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(1))  # should be 'Image'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Image"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())
    x_pos = find_row_by_label(gui_load.gui.edit_layout, 'x_pos')
    y_pos = find_row_by_label(gui_load.gui.edit_layout, 'y_pos')

    gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().clear()
    gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().insert("99")
    assert gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().text() == "99"
    gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["x_pos"] == "99"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().text() == "99"
    assert gui_load.structure["Page 1"]["Image"]["x_pos"] == "99"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().clear()
    gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().insert("99")
    assert gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().text() == "99"
    gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["y_pos"] == "99"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().text() == "99"
    assert gui_load.structure["Page 1"]["Image"]["y_pos"] == "99"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    QTest.qWait(2000)
    test_gui = StackedWindowGui("./test/imgtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Image):
            assert child.x() == 99
            assert child.y() == 99
    test_gui.close()

    #  -------- -1 ---------
    gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().clear()
    gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().insert("-1")
    assert gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().text() == "-1"
    gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["x_pos"] == "-1"
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().text() == "-1"
    assert gui_load.structure["Page 1"]["Image"]["x_pos"] == "-1"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found
    gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().clear()
    gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().insert("-1")
    assert gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().text() == "-1"
    gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["y_pos"] == "-1"
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().text() == "-1"
    assert gui_load.structure["Page 1"]["Image"]["y_pos"] == "-1"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found

    #  ---------0--------
    gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().clear()
    gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().insert("0")
    assert gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().text() == "0"
    gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["x_pos"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.load_preview()
    QTimer.singleShot(150, handle_dialog_error)
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(x_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(x_pos[1]).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Image"]["x_pos"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert error_found
    assert not warning_found
    gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().clear()
    gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().insert("0")
    assert gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().text() == "0"
    gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().editingFinished.emit()
    assert gui_load.structure["Page 1"]["Image"]["y_pos"] == "0"
    gui_load.gui.load_preview()
    gui_load.gui.refresh_button.click()
    assert gui_load.gui.edit_layout.itemAt(y_pos[0], QFormLayout.ItemRole.FieldRole).itemAt(y_pos[1]).widget().text() == "0"
    assert gui_load.structure["Page 1"]["Image"]["y_pos"] == "0"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found

    gui_load.structure["Page 1"]["Image"]["x_pos"] = 1800
    gui_load.structure["Page 1"]["Image"]["y_pos"] = 400
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    QTest.qWait(2000)
    gui_load.close()
    os.remove("./test/results/results_img.csv")


# noinspection PyArgumentList
def test_image_position(gui_load, qtbot, capfd):
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    tv = gui_load.gui.treeview
    tv.expandAll()
    tv.setCurrentItem(tv.topLevelItem(0).child(0).child(1))  # should be 'Image'
    assert len(tv.selectedItems()) == 1
    assert tv.selectedItems()[0].text(0) == "Image"

    rect = tv.visualItemRect(tv.currentItem())
    QTest.mouseClick(tv.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, rect.center())

    # --- free ---
    pos_pos = find_row_by_label(gui_load.gui.edit_layout, 'image_position')
    pos_cb = gui_load.gui.edit_layout.itemAt(pos_pos, QFormLayout.ItemRole.FieldRole).widget()
    assert pos_cb.currentText() == 'free'
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    test_gui = StackedWindowGui("./test/imgtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Image):
            assert child.x() == 1800
            assert child.y() == 400
    test_gui.close()

    # --- right ---
    QTest.mouseClick(pos_cb, Qt.MouseButton.LeftButton)
    QTest.keyClick(pos_cb, Qt.Key.Key_Up)
    QTest.keyClick(pos_cb, Qt.Key.Key_Enter)
    assert pos_cb.currentText() == "right"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Image"]["image_position"] == "right"
    gui_load.save()
    test_gui = StackedWindowGui("./test/imgtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Image):
            assert isinstance(child.parent().layout(), QHBoxLayout)
            assert child.parent().layout().indexOf(child) == 1
    test_gui.close()

    # --- left ---
    QTest.mouseClick(pos_cb, Qt.MouseButton.LeftButton)
    QTest.keyClick(pos_cb, Qt.Key.Key_Up)
    QTest.keyClick(pos_cb, Qt.Key.Key_Enter)
    assert pos_cb.currentText() == "left"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Image"]["image_position"] == "left"
    gui_load.save()
    test_gui = StackedWindowGui("./test/imgtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Image):
            assert isinstance(child.parent().layout(), QHBoxLayout)
            assert child.parent().layout().indexOf(child) == 0
    test_gui.close()

    # --- bottom ---
    QTest.mouseClick(pos_cb, Qt.MouseButton.LeftButton)
    QTest.keyClick(pos_cb, Qt.Key.Key_Up)
    QTest.keyClick(pos_cb, Qt.Key.Key_Enter)
    assert pos_cb.currentText() == "bottom"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Image"]["image_position"] == "bottom"
    gui_load.save()
    test_gui = StackedWindowGui("./test/imgtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Image):
            assert isinstance(child.parent().layout(), QFormLayout)
            assert child.parent().layout().getWidgetPosition(child)[0] == len(gui_load.structure["Page 1"].sections) - 1

    # --- top ---
    QTest.mouseClick(pos_cb, Qt.MouseButton.LeftButton)
    QTest.keyClick(pos_cb, Qt.Key.Key_Up)
    QTest.keyClick(pos_cb, Qt.Key.Key_Enter)
    assert pos_cb.currentText() == "top"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Image"]["image_position"] == "top"
    gui_load.save()
    test_gui = StackedWindowGui("./test/imgtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Image):
            assert isinstance(child.parent().layout(), QFormLayout)
            assert child.parent().layout().getWidgetPosition(child)[0] == 0
    test_gui.close()

    # --- here ---
    QTest.mouseClick(pos_cb, Qt.MouseButton.LeftButton)
    QTest.keyClick(pos_cb, Qt.Key.Key_Up)
    QTest.keyClick(pos_cb, Qt.Key.Key_Enter)
    assert pos_cb.currentText() == "here"
    QTimer.singleShot(150, handle_dialog_error)
    error_found, warning_found, warning_details = validate_questionnaire(gui_load.structure)
    assert not error_found
    assert not warning_found
    gui_load.gui.refresh_button.click()
    assert gui_load.structure["Page 1"]["Image"]["image_position"] == "here"
    gui_load.save()
    test_gui = StackedWindowGui("./test/imgtest.txt")
    for child in test_gui.Stack.currentWidget().children():
        if isinstance(child, Image):
            assert isinstance(child.parent().layout(), QFormLayout)
            assert child.parent().layout().getWidgetPosition(child)[0] == gui_load.structure["Page 1"].sections.index("Image")
    test_gui.close()

    QTest.mouseClick(pos_cb, Qt.MouseButton.LeftButton)
    QTest.keyClick(pos_cb, Qt.Key.Key_Down)
    QTest.keyClick(pos_cb, Qt.Key.Key_Down)
    QTest.keyClick(pos_cb, Qt.Key.Key_Down)
    QTest.keyClick(pos_cb, Qt.Key.Key_Down)
    QTest.keyClick(pos_cb, Qt.Key.Key_Down)
    QTest.keyClick(pos_cb, Qt.Key.Key_Enter)
    assert pos_cb.currentText() == 'free'
    gui_load.structure["Page 1"]["Image"]["x_pos"] = 1800
    gui_load.structure["Page 1"]["Image"]["y_pos"] = 400
    QTest.keyClicks(gui_load, 's', modifier=Qt.KeyboardModifier.ControlModifier, delay=1000)
    gui_load.save()
    os.remove("./test/results/results_img.csv")
    gui_load.close()


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction(run, qtbot):
    assert run.Stack.count() == 1
    for child in run.Stack.currentWidget().children():
        if isinstance(child, Image):
            assert child.width() == 250
            assert child.height() == 100
            assert child.x() == 1800
            assert child.y() == 400
    QTimer.singleShot(100, handle_dialog)
    QTest.mouseClick(run.forwardbutton, Qt.MouseButton.LeftButton)

    results = []
    with open('./test/results/results_img.csv', mode='r') as file:
        csv_file = csv.reader(file, delimiter=';')

        for lines in csv_file:
            results = lines
            if results[0].startswith('data'):
                assert results[0] == 'data_row_number'  # participant number
                assert results[1] == 'Start'
                assert results[2] == 'End'
    assert len(results) == 3
    assert results[0] == '1'  # participant number
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[1])  # timestamp
    assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
    os.remove("./test/results/results_img.csv")


# noinspection PyArgumentList
def test_execute_questionnaire_no_interaction_blocked(run, qtbot):
    with mock_file(r'./test/results/results_img.csv'):
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
                    assert results[1] == 'Start'
                    assert results[2] == 'End'
        assert len(results) == 3
        assert results[0] == '-1'  # participant number unknown
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[1])  # timestamp
        assert re.match(r'\d+-\d+-\d+ \d+:\d+:\d+.\d+', results[2])  # timestamp
        os.remove(res_file)
