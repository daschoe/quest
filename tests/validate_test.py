"""Test if the validate function in Validator.py is working correctly."""

from tests.context import pytest, QTimer, QTest, Qt, ConfigObj, validate_questionnaire, QApplication, QMessageBox, ConfigObjError


@pytest.fixture
def gui_init():
    """Start GUI"""
    if not QApplication.instance():
        gui = QApplication([])
    else:
        while QApplication.instance():
            QApplication.instance().shutdown()
        gui = QApplication([])
    return gui


text = ''


def test_global_settings(gui_init):
    # noinspection PyArgumentList
    def handle_dialog_error():
        """Click OK on dialog."""
        dialog = QApplication.activeModalWidget()
        global text
        text = dialog.detailedText()
        QTest.mouseClick(dialog.button(QMessageBox.StandardButton.Ok), Qt.MouseButton.LeftButton)

    structure = ConfigObj()
    structure["go_back"] = True
    structure["save_after"] = None
    # -------help-------
    structure["help_ip"] = "address"
    structure["help_port"] = "2000"
    structure["help_text"] = "Help"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid help IP(v4) found.\n") > -1
    structure["help_ip"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No help_ip found, but help port. Calling help will be disabled.\n"
    structure.pop("help_ip")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No help_ip found, but help port. Calling help will be disabled.\n"
    structure["help_ip"] = "127.0.0.1"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["help_port"] = "abcd"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid help port, could not be converted to a number 0-65535.\n") > -1
    structure["help_port"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No help_port found, but IP. Calling help will be disabled.\n"
    structure.pop("help_port")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No help_port found, but IP. Calling help will be disabled.\n"
    structure["help_port"] = -1
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid help port, could not be converted to a number 0-65535.\n") > -1
    structure["help_port"] = 65536
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid help port, could not be converted to a number 0-65535.\n") > -1
    structure["help_port"] = 3500
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure.pop("help_text")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No text given for the help button, but a connection. The external logging will still work.\n"
    structure["help_text"] = "HELP"
    structure.pop("help_ip")
    structure.pop("help_port")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No help connection given, but text. Calling help will be disabled.\n"
    structure.pop("help_text")
    # -------audio-------
    structure["audio_ip"] = "address"
    structure["audio_port"] = "2000"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid audio IP(v4) found.\n") > -1
    structure["audio_ip"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No audio_ip found, but audio port. Audio will be disabled.\n"
    structure.pop("audio_ip")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No audio_ip found, but audio port. Audio will be disabled.\n"
    structure["audio_ip"] = "127.0.0.1"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["audio_port"] = "abcd"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid audio port, could not be converted to a number 0-65535.\n") > -1
    structure["audio_port"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No audio_port found, but IP. Audio will be disabled.\n"
    structure.pop("audio_port")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No audio_port found, but IP. Audio will be disabled.\n"
    structure["audio_port"] = -1
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid audio port, could not be converted to a number 0-65535.\n") > -1
    structure["audio_port"] = 65536
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid audio port, could not be converted to a number 0-65535.\n") > -1
    structure["audio_port"] = 3500
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn

    structure["audio_recv_port"] = "abcd"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid audio receive port, could not be converted to a number 0-65535.\n") > -1
    structure["audio_recv_port"] = -1
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid audio receive port, could not be converted to a number 0-65535.\n") > -1
    structure["audio_recv_port"] = 65536
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid audio receive port, could not be converted to a number 0-65535.\n") > -1
    structure["audio_recv_port"] = 3500
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure.pop("audio_ip")
    structure.pop("audio_port")
    structure.pop("audio_recv_port")
    # -------video-------
    structure["video_ip"] = "address"
    structure["video_port"] = "2000"
    structure["video_player"] = "VLC"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid video IP(v4) found.\n") > -1
    structure["video_ip"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No video_ip found, but video port. Video will be disabled.\n"
    structure.pop("video_ip")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No video_ip found, but video port. Video will be disabled.\n"
    structure["video_ip"] = "127.0.0.1"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["video_port"] = "abcd"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid video port, could not be converted to a number 0-65535.\n") > -1
    structure["video_port"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No video_port found, but IP. Video will be disabled.\n"
    structure.pop("video_port")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No video_port found, but IP. Video will be disabled.\n"
    structure["video_port"] = -1
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid video port, could not be converted to a number 0-65535.\n") > -1
    structure["video_port"] = 65536
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid video port, could not be converted to a number 0-65535.\n") > -1
    structure["video_port"] = 3500
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["video_player"] = "None"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No video_player chosen, but IP and port. Video will be disabled.\n"
    structure.pop("video_player")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No video_player found, but IP and port. Video will be disabled.\n"
    structure["video_player"] = "abc"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid value for video_player.\n") > -1
    structure["video_player"] = "MadMapper"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure.pop("video_ip")
    structure.pop("video_port")
    structure.pop("video_player")
    # -------pupil-------
    structure["pupil_ip"] = "address"
    structure["pupil_port"] = "2000"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid pupil IP(v4) found.\n") > -1
    structure["pupil_ip"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No pupil_ip found, but pupil port. The connection to pupil will be disabled.\n"
    structure.pop("pupil_ip")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No pupil_ip found, but pupil port. The connection to pupil will be disabled.\n"
    structure["pupil_ip"] = "127.0.0.1"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["pupil_port"] = "abcd"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid pupil port, could not be converted to a number 0-65535.\n") > -1
    structure["pupil_port"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No pupil_port found, but IP. The connection to pupil will be disabled.\n"
    structure.pop("pupil_port")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No pupil_port found, but IP. The connection to pupil will be disabled.\n"
    structure["pupil_port"] = -1
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid pupil port, could not be converted to a number 0-65535.\n") > -1
    structure["pupil_port"] = 65536
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid pupil port, could not be converted to a number 0-65535.\n") > -1
    structure["pupil_port"] = 3500
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure.pop("pupil_ip")
    structure.pop("pupil_port")
    # ------navigation-------
    structure.pop("go_back")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No option for 'go_back' found, using False as default value.\n"
    structure["back_text"] = "back"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "Backwards navigation is not allowed but text for back button was set. The button will not be displayed.\n"
    structure["forward_text"] = "back"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[1] == "Text for forward and backward button are the same.\n"
    structure.pop("back_text")
    structure["send_text"] = "back"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "Text for forward and send button are the same.\n"
    structure.pop("forward_text")
    structure.pop("send_text")
    structure["go_back"] = "maybe"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("No valid value found for 'go_back'.\n") > -1
    structure["go_back"] = "false"
    # TODO Tests for pagecount_text?

    # -------global_osc-------
    structure["global_osc_ip"] = "address"
    structure["global_osc_send_port"] = "2000"
    structure["global_osc_recv_port"] = 5000
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid global_osc IP(v4) found.\n") > -1
    structure["global_osc_ip"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No global_osc_ip found, but global_osc_send_port. Sending over global OSC will be disabled.\n"
    structure.pop("global_osc_ip")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No global_osc_ip found, but global_osc_send_port. Sending over global OSC will be disabled.\n"
    structure["global_osc_ip"] = "127.0.0.1"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["global_osc_send_port"] = "abcd"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid global_osc_send_port, could not be converted to a number 0-65535.\n") > -1
    structure["global_osc_send_port"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No global_osc_send_port found, but IP. Sending over global will be disabled.\n"
    structure.pop("global_osc_send_port")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No global_osc_send_port found, but IP. Sending over global will be disabled.\n"
    structure["global_osc_send_port"] = -1
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid global_osc_send_port, could not be converted to a number 0-65535.\n") > -1
    structure["global_osc_send_port"] = 65536
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid global_osc_send_port, could not be converted to a number 0-65535.\n") > -1
    structure["global_osc_send_port"] = 3500
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure.pop("global_osc_recv_port")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No global_osc_recv_port found, but IP. Receiving over global will be disabled.\n"

    structure["global_osc_recv_port"] = "abcd"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid global_osc_recv_port, could not be converted to a number 0-65535.\n") > -1
    structure["global_osc_recv_port"] = -1
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid global_osc_recv_port, could not be converted to a number 0-65535.\n") > -1
    structure["global_osc_recv_port"] = 65536
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid global_osc_recv_port, could not be converted to a number 0-65535.\n") > -1
    structure["global_osc_recv_port"] = 3500
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure.pop("global_osc_send_port")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "No global_osc_send_port found, but IP. Sending over global will be disabled.\n"
    structure.pop("global_osc_ip")
    structure.pop("global_osc_recv_port")

    # ------save message------
    structure["save_after"] = "5"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("The value given for 'save_after' is not the name of a page of this questionnaire.\n") > -1
    structure.pop("save_after")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    # assert det[0] == "No value for 'save_after' given, saving after the last page by default.\n"
    structure["save_after"] = None
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    # TODO test for having a page
    # no tests needed for save_message
    structure["answer_pos"] = "maybe"
    structure["answer_neg"] = "maybe"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "Text for positive and negative answer are the same.\n"
    structure.pop("answer_pos")
    structure.pop("answer_neg")
    # ------save file-------
    structure["delimiter"] = "none"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid delimiter found. It can only have one character.\n") > -1
    structure["delimiter"] = "\t"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure.pop("delimiter")
    structure["filepath_results"] = "A://some/weird/path/res.txt"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert warn
    assert det[0] == "Path for results file does not exist. It will be created.\n"
    assert -1 <= text.find("Invalid drive name for results file path.\n") > -1
    structure["filepath_results"] = "./tests/results/results.csv"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["filepath_results"] = "./tests/results/new/results.csv"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "Path for results file does not exist. It will be created.\n"
    structure.pop("filepath_results")
    # ------style------
    structure["button_fade"] = "ten"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("'button_fade' could not be converted to a non-negative number.\n") > -1
    structure["button_fade"] = -5
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("'button_fade' could not be converted to a non-negative number.\n") > -1
    structure["button_fade"] = "600"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["stylesheet"] = "A://B/C/D.css"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid stylesheet path.\n") > -1
    structure["stylesheet"] = "./Images/RadioChecked.svg"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid file for stylesheet, it has to be *.qss.\n") > -1
    structure["stylesheet"] = "./stylesheets/minimal.qss"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["randomization"] = "random"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid randomization option.\n") > -1
    structure["randomization"] = "None"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["randomization"] = "from file"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Randomization 'from file' chosen, but no file given.\n") > -1
    structure["randomization_file"] = "A://B/C/D.css"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid randomization_file path.\n") > -1
    structure["randomization_file"] = "./Images/RadioChecked.svg"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Invalid file for randomization, it has to be *.txt or *.csv.\n") > -1
    structure["randomization_file"] = "./Configs/all_question_types.txt"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find("Contents of randomization_file invalid.\n") > -1
    structure["randomization_file"] = os.path.join(os.getcwd(), "tests/random.txt")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure.pop("randomization")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "Randomization_file found, but no option for randomization.\n"

    gui_init.exit()


def test_page_settings(gui_init):
    structure = ConfigObj()
    structure["go_back"] = True
    structure["save_after"] = None
    structure["Page"] = {}
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "There are no questions on page Page.\n"
    structure["Page"]["Question"] = {"type": "HLine"}
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    # title and description are just text and do not need tests
    structure["Page"]["pupil_on_next"] = "this page is done"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == "Incomplete connection to pupil given. The connection to pupil will be disabled.\n"
    structure["pupil_ip"] = "127.0.0.1"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[1] == "Incomplete connection to pupil given. The connection to pupil will be disabled.\n"
    structure.pop("pupil_ip")
    structure["pupil_port"] = 9000
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[1] == "Incomplete connection to pupil given. The connection to pupil will be disabled.\n"
    structure["pupil_ip"] = "127.0.0.1"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure.pop("pupil_ip")
    structure.pop("pupil_port")
    structure["Page"].pop("pupil_on_next")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    # TODO own test for randomgroup

    gui_init.exit()


def test_multiple_pages():
    with pytest.raises(ConfigObjError):
        ConfigObj(os.path.join(os.getcwd(), "tests/doubled_sections.txt"))


def test_question_settings(gui_init):
    # noinspection PyArgumentList
    def handle_dialog_error():
        """Click OK on dialog."""
        dialog = QApplication.activeModalWidget()
        global text
        text = dialog.detailedText()
        QTest.mouseClick(dialog.button(QMessageBox.StandardButton.Ok), Qt.MouseButton.LeftButton)

    structure = ConfigObj()
    structure["go_back"] = True
    structure["save_after"] = None
    structure["Page"] = {}
    structure["Page"]["Question"] = {}
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'There are no attributes for question "Question" on page "Page".\n'

    # ------id------
    structure["Page"]["Question"]["id"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No ID was given for question "Question" on page "Page".\n') > -1
    structure["Page"]["Question"]["type"] = "HLine"
    structure["Page"]["Question"].pop("id")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["type"] = "Check"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert warn  # from the question type
    assert -1 <= text.find('No ID was given for question "Question" on page "Page".\n') > -1
    structure["Page"]["Question"].pop("type")
    structure["Page"]["Question"].pop("text")
    structure["Page"]["Question"].pop("answers")
    structure["Page"]["Question"]["id"] = "some id"
    structure["Page"]["Question2"] = {"id": "some id"}
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('ID "some id" already used in question "Question" on page "Page". Found again in question "Question2" on page "Page".\n') > -1
    structure["Page"].pop("Question2")
    structure["Page2"] = {"Question": {"id": "some id"}}
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'ID "some id" already used in question "Question" on page "Page". Found again in question "Question" on page "Page2".\n') > -1
    structure.pop("Page2")

    # ------x------
    structure["Page"]["Question"]["x"] = "something"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid value found for "x" for question "Question" on page "Page".\n') > -1
    structure["Page"]["Question"]["x"] = True
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["type"] = "ABX"
    structure["Page"]["Question"]["start_cues"] = [1, 2]
    structure["Page"]["Question"]["track"] = 1
    structure["Page"]["Question"].pop("x")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No option for "x" found for question "Question" on page "Page", using False as default value.\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------play_once------
    structure["Page"]["Question"]["play_once"] = "something"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid value found for "play_once" for question "Question" on page "Page".\n') > -1
    structure["Page"]["Question"]["play_once"] = True
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["type"] = "Player"
    structure["Page"]["Question"]["start_cue"] = 1
    structure["Page"]["Question"]["track"] = 1
    structure["Page"]["Question"].pop("play_once")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No option for "play_once" found for question "Question" on page "Page", using False by default.\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------required------
    structure["Page"]["Question"]["required"] = "something"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid value found for "required" for question "Question" on page "Page".\n') > -1
    structure["Page"]["Question"]["required"] = True
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"].pop("required")

    # ------labelled------
    structure["Page"]["Question"]["labelled"] = "something"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid value found for "labelled" for question "Question" on page "Page".\n') > -1
    structure["Page"]["Question"]["labelled"] = True
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["type"] = "Slider"
    structure["Page"]["Question"]["min"] = 1
    structure["Page"]["Question"]["max"] = 10
    structure["Page"]["Question"]["step"] = 1
    structure["Page"]["Question"]["start"] = 10
    structure["Page"]["Question"].pop("labelled")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No option for "labelled" found for question "Question" on page "Page", setting it to False.\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------question_above------
    structure["Page"]["Question"]["question_above"] = "something"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid value found for "question_above" for question "Question" on page "Page".\n') > -1
    structure["Page"]["Question"]["question_above"] = True
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"] = {'id': 'id'}

    # ------text------
    structure["Page"]["Question"]["text"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No text was given for question "Question" on page "Page".\n'
    structure["Page"]["Question"]["type"] = "Plain Text"
    structure["Page"]["Question"].pop("text")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No text was given for question "Question" on page "Page".\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------answers------
    structure["Page"]["Question"]["answers"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No answer possibilities were given for question "Question" on page "Page".\n'
    structure["audio_ip"] = "127.0.0.1"
    structure["audio_port"] = 8000
    structure["Page"]["Question"]["type"] = "ABX"
    structure["Page"]["Question"]["start_cues"] = [1, 2]
    structure["Page"]["Question"]["track"] = 1
    structure["Page"]["Question"]["x"] = False
    structure["Page"]["Question"]["text"] = "Some text."
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["answers"] = "1"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Please give two answer options for the ABX type question "Question" on page "Page" or leave this field empty.\n')
    structure["Page"]["Question"]["answers"] = ["1", "b", "c"]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'Please give two answer options for the ABX type question "Question" on page "Page" or leave this field empty.\n')
    structure["Page"]["Question"]["answers"] = ["1", "2"]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["answers"] = ("1", "2")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"] = {'id': 'id', "type": "Radio", "text": "some text"}
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No answer possibilities were given for question "Question" on page "Page".\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------start_answer_id------
    structure["Page"]["Question"]["start_answer_id"] = -1
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('The start answer ID in question "Question" on page "Page" can not have a negative value.\n')
    structure["Page"]["Question"]["start_answer_id"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('The start answer ID in question "Question" on page "Page" could not be interpreted as an integer.\n')
    structure["Page"]["Question"] = {'id': 'id'}

    # ------min------
    structure["Page"]["Question"]["min"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No minimum value found for the slider in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["min"] = 1.5
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["min"] = "ten"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('The minimum value found for the slider in question "Question" on page "Page" could not be interpreted as an integer.\n')
    structure["Page"]["Question"]["type"] = "Slider"
    structure["Page"]["Question"]["max"] = 10
    structure["Page"]["Question"]["start"] = 10
    structure["Page"]["Question"]["step"] = 1
    structure["Page"]["Question"]["labelled"] = False
    structure["Page"]["Question"]["text"] = "some text"
    structure["Page"]["Question"].pop("min")
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No minimum value was given for the slider in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["min"] = 20
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"] = {'id': 'id'}

    # ------max------
    structure["Page"]["Question"]["max"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No maximum value found for the slider in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["max"] = "ten"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('The maximum value found for the slider in question "Question" on page "Page" could not be interpreted as an integer.\n')
    structure["Page"]["Question"]["type"] = "Slider"
    structure["Page"]["Question"]["min"] = 10
    structure["Page"]["Question"]["step"] = 0.1
    structure["Page"]["Question"]["start"] = 10
    structure["Page"]["Question"]["labelled"] = False
    structure["Page"]["Question"]["text"] = "some text"
    structure["Page"]["Question"].pop("max")
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No maximum value was given for the slider in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["max"] = 0
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["max"] = 0.1
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["max"] = 10
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Maximum and Minimum value for the slider in question "Question" on page "Page" are the same.\n')
    structure["Page"]["Question"] = {'id': 'id'}

    # ------start------
    structure["Page"]["Question"]["start"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No starting value found for the slider in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["start"] = "ten"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'The starting value found for the slider in question "Question" on page "Page" could not be interpreted as an integer.\n')
    structure["Page"]["Question"]["type"] = "Slider"
    structure["Page"]["Question"]["max"] = 10
    structure["Page"]["Question"]["min"] = 0
    structure["Page"]["Question"]["step"] = 0.5
    structure["Page"]["Question"]["labelled"] = False
    structure["Page"]["Question"]["text"] = "some text"
    structure["Page"]["Question"].pop("start")
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No starting value was given for the slider in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["start"] = 0
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["start"] = 0.5
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"] = {'id': 'id'}

    # ------step------
    structure["Page"]["Question"]["step"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No step value found for the slider in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["step"] = "ten"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'The step value found for the slider in question "Question" on page "Page" could not be interpreted as a number.\n')
    structure["Page"]["Question"]["type"] = "Slider"
    structure["Page"]["Question"]["max"] = 1.5
    structure["Page"]["Question"]["min"] = 0.5
    structure["Page"]["Question"]["start"] = 0.1
    structure["Page"]["Question"]["labelled"] = False
    structure["Page"]["Question"]["text"] = "some text"
    structure["Page"]["Question"].pop("step")
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No step value was given for the slider in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["step"] = 0
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('The step value found for the slider in question "Question" on page "Page" needs to be bigger than 0.\n')
    structure["Page"]["Question"]["step"] = 2
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'The step value for the slider in question "Question" on page "Page" is bigger than the range.\n')
    structure["Page"]["Question"]["step"] = 0.5
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"] = {'id': 'id'}

    # ------label------
    structure["Page"]["Question"]["type"] = "Slider"
    structure["Page"]["Question"]["max"] = 10
    structure["Page"]["Question"]["min"] = 0
    structure["Page"]["Question"]["step"] = 1
    structure["Page"]["Question"]["labelled"] = False
    structure["Page"]["Question"]["text"] = "some text"
    structure["Page"]["Question"]["start"] = 0
    structure["Page"]["Question"]["label"] = "some label"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["labelled"] = True
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('The number of given labels does not match the number of ticks for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["label"] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["label"] = [[1, 2, "test"]]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid format for labels for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["label"] = [[-1, "no"], [11, "out"]]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Tick value outside of slider range found for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["label"] = [[5, "no"], [5, "out"]]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Double definition of tick labels found for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["label"] = [["null", "no"]]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('A label tick for the slider in question "Question" on page "Page" could not be interpreted as a number.\n')
    structure["Page"]["Question"]["label"] = [[0, "negativ"], [10, "positiv"]]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"] = {'id': 'id'}

    # ------policy------
    structure["Page"]["Question"]["policy"] = "something"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Invalid policy type in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["something"]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Invalid policy type in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = "None"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["policy"] = "int"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Policy type "int" takes two arguments, a different amount was given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["int", 1, 2, 3]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Policy type "int" takes two arguments, a different amount was given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["int", "", 2]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No minimum value was given for the policy in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["int", "ab", 2]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'Minimum value given for the policy in question "Question" on page "Page" could not be converted to a valid number.\n')
    structure["Page"]["Question"]["policy"] = ["int", 1, "ab"]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'Maximum value given for the policy in question "Question" on page "Page" could not be converted to a valid number.\n')
    structure["Page"]["Question"]["policy"] = ["int", 1, ""]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No maximum value was given for the policy in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["int", 1, 100]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["policy"] = "double"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Policy type "double" takes three arguments, a different amount was given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["double", 1, 2, 3, 4]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Policy type "double" takes two arguments, a different amount was given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["double", "", 2, 3]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'No minimum value was given for the policy in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["double", "ab", 2, 3]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'Minimum value given for the policy in question "Question" on page "Page" could not be converted to a valid number.\n')
    structure["Page"]["Question"]["policy"] = ["double", 1, "ab", 3]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'Maximum value given for the policy in question "Question" on page "Page" could not be converted to a valid number.\n')
    structure["Page"]["Question"]["policy"] = ["double", 1, "", 3]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No maximum value was given for the policy in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["double", 1, 2, "ab"]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'Number of decimals given for the policy in question "Question" on page "Page" could not be converted to a valid number.\n')
    structure["Page"]["Question"]["policy"] = ["double", 1, 2, ""]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No number of decimals was given for the policy in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["double", 1, 100, 3]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["policy"] = "regex"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Policy type "regex" takes one argument, a different amount was given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["regex", "some", 67]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Policy type "regex" takes one argument, a different amount was given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["regex", ""]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'No regex was given for the policy in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["regex", "[.*"]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'An invalid regex was given for the policy in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["policy"] = ["regex", "[A-Z]\\d"]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"] = {'id': 'id'}

    # ------start_cue------
    structure["Page"]["Question"]["start_cue"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No start cue was given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["start_cue"] = [12]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Start cue given in question "Question" on page "Page" could not be converted to a number.\n')
    structure["Page"]["Question"]["start_cue"] = 12
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["type"] = "Player"
    structure["Page"]["Question"].pop("start_cue")
    structure["Page"]["Question"]["track"] = 1
    structure["Page"]["Question"]["play_once"] = False
    structure["Page"]["Question"]["buttons"] = ["Play"]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No start cue was given in question "Question" on page "Page".\n')
    structure["Page"]["Question"] = {'id': 'id'}

    # ------end_cue------
    structure["Page"]["Question"]["end_cue"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No end cue was given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["end_cue"] = [12]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('End cue given in question "Question" on page "Page" could not be converted to a number.\n')
    structure["Page"]["Question"]["end_cue"] = 12
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["start_cue"] = 12
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('The same cue (12) was used as start- and end-cue for one condition in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["end_cue"] = 14
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"] = {'id': 'id'}

    # ------track------
    structure["Page"]["Question"]["track"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No track(s) was given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["track"] = [1]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["track"] = 1
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["track"] = -1
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Track given for question "Question" on page "Page" needs to be greater than 0.\n')
    structure["Page"]["Question"]["type"] = "Player"
    structure["Page"]["Question"].pop("track")
    structure["Page"]["Question"]["start_cue"] = 1
    structure["Page"]["Question"]["play_once"] = False
    structure["Page"]["Question"]["buttons"] = ["Play"]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No track(s) was given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["track"] = [1, [1, 1]]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'Tracks given for question "Question" on page "Page" need to be one or more integers, not lists.\n')
    structure["Page"]["Question"] = {'id': 'id'}
    structure["Page"]["Question"]["type"] = "ABX"
    structure["Page"]["Question"]["start_cues"] = [1, 2]
    structure["Page"]["Question"]["text"] = "some text"
    structure["Page"]["Question"]["x"] = False
    structure["Page"]["Question"]["track"] = 1
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["track"] = [1]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["track"] = [1, -1]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Track given for question "Question" on page "Page" needs to be greater than 0.\n')
    structure["Page"]["Question"]["track"] = [1, [1, 2]]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Tracks given for question "Question" on page "Page" need to be one or more integers, not lists.\n')
    structure["Page"]["Question"] = {'id': 'id'}
    structure["Page"]["Question"]["type"] = "MUSHRA"
    structure["Page"]["Question"]["start_cues"] = [1, 2]
    structure["Page"]["Question"]["end_cues"] = [3, 4]
    structure["Page"]["Question"]["text"] = "some text"
    structure["Page"]["Question"]["track"] = 1
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["track"] = [1]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["track"] = [1, 1, 2]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('The number of tracks given does not equal the number of cues given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["track"] = [1, 2]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["track"] = [1, [1, 2]]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["track"] = [[1, 2], [1, 2, -3]]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Track given for question "Question" on page "Page" needs to be greater than 0.\n')
    structure["Page"]["Question"] = {'id': 'id'}

    # ------crossfade------
    structure["Page"]["Question"]["crossfade"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid value found for "crossfade" for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["crossfade"] = True
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["crossfade"] = 0
    assert not err
    assert not warn
    structure["Page"]["Question"] = {'id': 'id'}

    # ------buttons------
    structure["Page"]["Question"]["buttons"] = []
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No buttons are displayed for the player in question "Question" on page "Page". It will play when this page is loaded.\n'
    structure["Page"]["Question"]["buttons"] = ["Pause"]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No Play button is displayed for the player in question "Question" on page "Page". It will play when this page is loaded.\n'
    structure["Page"]["Question"]["buttons"] = "Stop"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No Play button is displayed for the player in question "Question" on page "Page". It will play when this page is loaded.\n'
    structure["Page"]["Question"]["buttons"] = "Reverse"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Invalid value found for "buttons" for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["buttons"] = ["Skip"]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Invalid value found for "buttons" for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["type"] = "Player"
    structure["Page"]["Question"]["track"] = 1
    structure["Page"]["Question"]["start_cue"] = 1
    structure["Page"]["Question"]["play_once"] = False
    structure["Page"]["Question"].pop("buttons")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No buttons are displayed for the player in question "Question" on page "Page". It will play when this page is loaded.\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------start_cues------
    structure["Page"]["Question"]["start_cues"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No start cues were given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["start_cues"] = ["abc"]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Start cues given for question "Question" on page "Page" could not be converted to a list of number.\n')
    structure["Page"]["Question"]["start_cues"] = "abc"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'Start cues given for question "Question" on page "Page" could not be converted to a list of number.\n')
    structure["Page"]["Question"]["type"] = "ABX"
    structure["Page"]["Question"]["start_cues"] = 14
    structure["Page"]["Question"]["track"] = 1
    structure["Page"]["Question"]["text"] = "Some text"
    structure["Page"]["Question"]["x"] = False
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('There should be exactly 2 start_cues for AB(X)-tests, but 1 were given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["start_cues"] = [1, 2, 3]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'There should be exactly 2 start_cues for AB(X)-tests, but 1 were given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["start_cues"] = [1, 2]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"].pop("start_cues")
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No start cues were given for question "Question" on page "Page".\n')
    structure["Page"]["Question"] = {'id': 'id'}
    structure["Page"]["Question"]["type"] = "MUSHRA"
    structure["Page"]["Question"]["end_cues"] = [3, 4]
    structure["Page"]["Question"]["text"] = "some text"
    structure["Page"]["Question"]["track"] = 1
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No start cues were given for question "Question" on page "Page".\n')
    structure["Page"]["Question"] = {'id': 'id'}

    # ------end_cues------
    structure["Page"]["Question"]["end_cues"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No end cues were given in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["end_cues"] = ["abc"]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'End cues given for question "Question" on page "Page" could not be converted to a list of number.\n')
    structure["Page"]["Question"]["end_cues"] = "abc"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'End cues given for question "Question" on page "Page" could not be converted to a list of number.\n')
    structure["Page"]["Question"] = {'id': 'id'}
    structure["Page"]["Question"]["type"] = "MUSHRA"
    structure["Page"]["Question"]["start_cues"] = [3, 4]
    structure["Page"]["Question"]["text"] = "some text"
    structure["Page"]["Question"]["track"] = 1
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No end cues were given for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["end_cues"] = [4, 4]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('The same cue (4) was used as start- and end-cue for one condition in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["end_cues"] = [1, 2, 3]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'The number of start- and end-cues in question "Question" on page "Page" does not match.\n')
    structure["Page"]["Question"] = {'id': 'id'}

    # ------xfade------
    structure["Page"]["Question"]["xfade"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid value found for "xfade" for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["start_cues"] = [1, 1, 2]
    structure["Page"]["Question"]["end_cues"] = [2, 2, 2]
    structure["Page"]["Question"]["track"] = [1, 2, 3]
    structure["Page"]["Question"]["xfade"] = True
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Xfade is only applicable if all start- and end-markers are the same each in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["start_cues"] = [1, 1, 1]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["track"] = [1, 1, 1]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('For xfade stimuli need to be placed on different tracks in question "Question" on page "Page".\n')
    structure["Page"]["Question"]["track"] = 2
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('For xfade stimuli need to be placed on different tracks in question "Question" on page "Page".\n')
    structure["Page"]["Question"] = {'id': 'id'}

    # ------inscription------
    structure["Page"]["Question"]["inscription"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No inscription for the button in question "Question" on page "Page".\n'
    structure["Page"]["Question"]["inscription"] = "None"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'Internally used inscription "None" used in question "Question" on page "Page".\n'
    structure["Page"]["Question"].pop("inscription")
    structure["pupil_ip"] = "127.0.0.1"
    structure["pupil_port"] = 50500
    structure["Page"]["Question"]["type"] = "Button"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No inscription for the button in question "Question" on page "Page".\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------objectName------
    structure["Page"]["Question"]["objectName"] = "required"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'The objectName in question "Question" on page "Page" uses a predefined name.\n'
    structure["Page"]["Question"]["objectName"] = "headline"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'The objectName in question "Question" on page "Page" uses a predefined name.\n'
    structure["Page"]["Question"]["objectName"] = "SliderHeader"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'The objectName in question "Question" on page "Page" uses a predefined name.\n'
    structure["Page"]["Question"].pop("objectName")

    # ------timer------
    structure["Page"]["Question"]["timer"] = "ten"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('The timer in question "Question" on page "Page" needs to be a numeric value.\n')
    structure["Page"]["Question"]["timer"] = -20
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'The timer in question "Question" on page "Page" needs to be greater than or equal to 0. Setting it to 0 by default.\n'
    structure["Page"]["Question"].pop("timer")

    # ------password_file------
    structure["Page"]["Question"]["password_file"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No password_file found for question "Question" on page "Page".\n'
    structure["Page"]["Question"]["password_file"] = "./invalid/path.txt"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid password_file for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["type"] = "Password"
    structure["Page"]["Question"]["text"] = "text"
    structure["Page"]["Question"].pop("password_file")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No password_file found for question "Question" on page "Page".\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------button_texts------
    structure["Page"]["Question"]["x"] = False
    structure["Page"]["Question"]["button_texts"] = [1, 1, 1]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Please give no, two or three (if option X is used) button_texts for the ABX type question "Question" on page "Page".\n')
    structure["Page"]["Question"]["x"] = True
    structure["Page"]["Question"]["button_texts"] = [1, 1, 1]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["button_texts"] = [1, 1]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'Please give no, two or three (if option X is used) button_texts for the ABX type question "Question" on page "Page".\n')
    structure["Page"]["Question"]["button_texts"] = "sth"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find(
        'Please give no, two or three (if option X is used) button_texts for the ABX type question "Question" on page "Page".\n')
    structure["Page"]["Question"] = {'id': 'id'}

    # ------randomize------
    structure["Page"]["Question"]["randomize"] = "not bool"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid value found for "randomize" for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["type"] = "Matrix"
    structure["Page"]["Question"]["text"] = "some text"
    structure["Page"]["Question"]["answers"] = "some answer"
    structure["Page"]["Question"]["questions"] = "something"
    structure["Page"]["Question"].pop("randomize")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No option for "randomize" found for question "Question" on page "Page".\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------questions------
    structure["Page"]["Question"]["questions"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No questions for the matrix in question "Question" on page "Page" found.\n'
    structure["Page"]["Question"]["questions"] = []
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No questions for the matrix in question "Question" on page "Page" found.\n'
    structure["Page"]["Question"]["type"] = "Matrix"
    structure["Page"]["Question"]["text"] = "some text"
    structure["Page"]["Question"]["answers"] = "some answer"
    structure["Page"]["Question"]["randomize"] = False
    structure["Page"]["Question"].pop("questions")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No questions for the matrix in question "Question" on page "Page" found.\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------width------
    structure["Page"]["Question"]["width"] = "ten"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Invalid value for width for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["width"] = -20
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Width needs to be bigger than 0 for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["width"] = 300
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"].pop("width")
    structure["Page"]["Question"] = {'id': 'id'}

    # ------height------
    structure["Page"]["Question"]["height"] = "ten"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Invalid value for height for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["height"] = -20
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Height needs to be bigger than 0 for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["height"] = 300
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"].pop("height")
    structure["Page"]["Question"] = {'id': 'id'}

    # ------x_pos------
    structure["Page"]["Question"]["x_pos"] = "ten"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Invalid value for x position for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["x_pos"] = -20
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('X position needs to be bigger or equal to 0 for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["x_pos"] = 300
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"].pop("x_pos")
    structure["Page"]["Question"]["type"] = "Image"
    structure["Page"]["Question"]["image_file"] = "/tests/Logo.png"
    structure["Page"]["Question"]["image_position"] = "free"
    structure["Page"]["Question"]["y_pos"] = 300
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No x position given for the question "Question" on page "Page".\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------y_pos------
    structure["Page"]["Question"]["y_pos"] = "ten"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Invalid value for y position for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["y_pos"] = -20
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Y position needs to be bigger or equal to 0 for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["y_pos"] = 300
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"].pop("y_pos")
    structure["Page"]["Question"]["type"] = "Image"
    structure["Page"]["Question"]["image_file"] = "/tests/Logo.png"
    structure["Page"]["Question"]["image_position"] = "free"
    structure["Page"]["Question"]["x_pos"] = 300
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No y position given for the question "Question" on page "Page".\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------image_file------
    structure["Page"]["Question"]["image_file"] = ""
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No image_file found for question "Question" on page "Page".\n'
    structure["Page"]["Question"]["image_file"] = "./invalid/path.txt"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid image_file for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["type"] = "Image"
    structure["Page"]["Question"]["image_position"] = "here"
    structure["Page"]["Question"].pop("image_file")
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'No image_file found for question "Question" on page "Page".\n'
    structure["Page"]["Question"] = {'id': 'id'}

    # ------image_position------
    structure["Page"]["Question"]["image_position"] = "everywhere"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Invalid image position found for question "Question" on page "Page".\n')
    structure["Page"]["Question"]["image_position"] = "free"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'Image "Question" on page "Page" is chosen to be positioned freely, but no coordinates were given.\n'
    structure["Page"]["Question"]["type"] = "Image"
    structure["Page"]["Question"]["image_file"] = "/tests/Logo.png"
    structure["Page"]["Question"].pop("image_position")
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No image_position found for question "Question" on page "Page".\n')
    structure["Page"]["Question"] = {'id': 'id'}

    # ------receiver------
    structure["Page"]["Question"]["receiver"] = ["ip", 3000]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid IP address given for the receiver in question "Question" on page "Page".') > -1
    structure["Page"]["Question"]["receiver"] = ["", 3000]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No valid IP address given for the receiver in question "Question" on page "Page".') > -1
    structure["Page"]["Question"]["receiver"] = ["127.0.0.1", ""]
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('Invalid receiver port in question "Question" on page "Page", could not be converted to a number 0-65535.') > -1
    structure["Page"]["Question"]["receiver"] = ["127.0.0.1", 800]
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"]["receiver"] = "audio"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('The receiver of question "Question" on page "Page" needs to have the format (IP, Port).') > -1
    structure["Page"]["Question"].pop("receiver")
    structure["Page"]["Question"]["type"] = "OSCButton"
    structure["Page"]["Question"]["address"] = "/msg"
    structure["Page"]["Question"]["value"] = 0
    structure["Page"]["Question"]["inscription"] = "Text"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No receiver found for question "Question" on page "Page".\n') > -1
    structure["Page"]["Question"] = {'id': 'id'}

    # ------address------
    structure["Page"]["Question"]["address"] = ""
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No OSC-address for question "Question" on page "Page" was given.\n') > -1
    structure["Page"]["Question"]["address"] = "message"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert warn
    assert det[0] == 'The OSC-address of question "Question" on page "Page" should start with "/".\n'
    structure["Page"]["Question"]["address"] = "/audio"
    err, warn, det = validate_questionnaire(structure, True)
    assert not err
    assert not warn
    structure["Page"]["Question"].pop("address")
    structure["Page"]["Question"]["type"] = "OSCButton"
    structure["Page"]["Question"]["receiver"] = ["127.0.0.1", 8000]
    structure["Page"]["Question"]["value"] = 0
    structure["Page"]["Question"]["inscription"] = "Text"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No OSC-address for question "Question" on page "Page" was given.\n') > -1
    structure["Page"]["Question"] = {'id': 'id'}

    # ------value------
    structure["Page"]["Question"]["type"] = "OSCButton"
    structure["Page"]["Question"]["receiver"] = ["127.0.0.1", 8000]
    structure["Page"]["Question"]["address"] = "/message"
    structure["Page"]["Question"]["inscription"] = "Text"
    QTimer.singleShot(150, handle_dialog_error)
    err, warn, det = validate_questionnaire(structure, True)
    assert err
    assert not warn
    assert -1 <= text.find('No value for question "Question" on page "Page" was given.\n') > -1
    structure["Page"]["Question"] = {'id': 'id'}

    gui_init.exit()
