"""Validation of questionnaire text files."""

import ast
import re
from os import path

from PySide6.QtGui import QIntValidator, QDoubleValidator, QRegularExpressionValidator, QValidator
from PySide6.QtWidgets import QSizePolicy, QMessageBox
from PySide6.QtCore import QRegularExpression

from src.MessageBox import ResizeMessageBox
from src.tools import fields_per_type, player_buttons, policy_possibilities, randomize_options, image_positions, video_player


def validate_passwords(file, policy):
    """ Check if the passwords of a given password-file are possible to be written with the validator of the input field.

    Parameters
    ----------
    file : str
        password file
    policy : list
        policy description

    Returns
    -------
    bool
        True if all passwords can be typed with the validator, False otherwise
    """
    if policy[0] == "int":
        validator = QIntValidator(int(policy[1]), int(policy[2]))
    elif policy[0] == "double":
        validator = QDoubleValidator(int(policy[1]), int(policy[2]), int(policy[3]))
    elif policy[0] == "regex":
        validator = QRegularExpressionValidator(QRegularExpression(policy[1]))
    else:
        # policy[0] == "None":
        return True
    with open(file) as f:
        passwords = f.read().splitlines()
    for password in passwords:
        res = validator.validate(password, 0)
        if res[0] != QValidator.State.Acceptable:
            return False
    return True


def validate_random(file):
    """ Check if a given random_order-file has a valid format.

        Parameters
        ----------
        file : str
            random_order file

        Returns
        -------
        bool
            True if all orders have the same length >1 and same page numbers, False otherwise
        """
    with open(file) as f:
        orders = f.read().splitlines()
    order_len = len(orders[0].split(","))
    if order_len == 1:
        return False
    for row in range(1, len(orders)):
        if len(orders[row].split(",")) != order_len or len(orders[row].split(",")) == 1:
            return False
    pages = set()
    for row in range(0, len(orders)):
        orders[row] = orders[row].split(",")
        for entry in range(0, len(orders[row])):
            orders[row][entry] = int(orders[row][entry])
            if row == 0:
                pages.add(orders[row][entry])
            elif orders[row][entry] not in pages:
                return False
        for page in pages:
            if page not in orders[row]:
                return False
    return True


def listify(structure, status=None, status_duration=None):
    """Convert strings to lists of strings/integers for certain fields.

    Parameters
    ----------
    structure : ConfigObj
        holds the structure of the questionnaire to go through.
    status : QStatusBar, optional
        instance of QStatusBar to display an error.
    status_duration : int, optional
        duration for displaying the status message.

    Returns
    -------
    ConfigObj
        the given structure with converted strings.

    Raises
    ------
    SyntaxError
        If there is a problem with converting a string to a list.
    ValueError
        If there is a problem with converting a string to a list, e.g. odd number of quotation marks.
    """
    if status is not None:
        status.clearMessage()
    for page in structure.sections:
        for quest in structure[page].sections:
            try:
                if "start_cues" in structure[page][quest].keys() and "," in structure[page][quest]["start_cues"]:
                    structure[page][quest]["start_cues"] = ast.literal_eval(structure[page][quest]["start_cues"])
            except (ValueError, SyntaxError):
                if status is not None:
                    status.showMessage("Invalid value found in a 'start_cues' field.\n", status_duration)
            try:
                if "end_cues" in structure[page][quest].keys() and "," in structure[page][quest]["end_cues"]:
                    structure[page][quest]["end_cues"] = ast.literal_eval(structure[page][quest]["end_cues"])
            except (ValueError, SyntaxError):
                if status is not None:
                    status.showMessage("Invalid value found in a 'end-cues' field.\n", status_duration)

            if "label" in structure[page][quest].keys() and ("," in structure[page][quest]["label"] or
                                                             "[" in structure[page][quest]["label"] or
                                                             "]" in structure[page][quest]["label"] or
                                                             isinstance(structure[page][quest]["label"], list)):
                sublist = False
                lblcpy = structure[page][quest]["label"]
                labels = []
                try:
                    if isinstance(lblcpy, str):
                        if lblcpy[0] == "[" and lblcpy[1] == "[" and lblcpy[-1] == "]" and lblcpy[-2] == "]":
                            lblcpy = lblcpy.strip(' "')[1:-1]
                        elif lblcpy.count("[") == 1 and lblcpy.count("]") == 1 and lblcpy.count(",") == 0:
                            lblcpy = lblcpy.strip(' []"')
                        lblcpy = lblcpy.split(",")
                    for _, lblc in enumerate(lblcpy):
                        if isinstance(lblc, str):
                            if '[' in lblc:  # t is list:
                                if ('[' in lblc) and (']' not in lblc):
                                    sublist = True
                                if ',' not in lblc:
                                    labels.append([float(lblc.strip(" '][").strip('"'))])
                                else:
                                    if len(lblc.split(",")) == 2:
                                        entry = lblc.split(",")
                                        labels.append([float(entry[0].strip(" '[]").strip('"')), entry[1].strip(" '[]").strip('"')])
                                    else:
                                        labels[-1].append(float(entry.strip(" '[]").strip('"')))
                            elif sublist:
                                if ']' in lblc:
                                    sublist = False
                                    labels[-1].append(lblc.strip(" ]['").strip('"'))
                                else:
                                    labels[-1].append(float(lblc))
                            elif not sublist:
                                labels.append(lblc.strip(" '[]").strip('"'))
                        else:
                            if isinstance(lblc, list) or isinstance(lblc, tuple):
                                if len(lblc) == 2:
                                    labels.append([float(lblc[0]), lblc[1]])
                                else:
                                    labels[-1].append(lblc)
                    structure[page][quest]["label"] = labels
                except (ValueError, SyntaxError) as e:
                    if status is not None:
                        status.showMessage(f'Invalid value found in a "label" field: {e}', status_duration)

            if "track" in structure[page][quest].keys() and ("," in structure[page][quest]["track"] or
                                                             "[" in structure[page][quest]["track"] or
                                                             "]" in structure[page][quest]["track"] or
                                                             isinstance(structure[page][quest]["track"], list)):
                sublist = False
                trackscpy = structure[page][quest]["track"]
                tracks = []
                try:
                    if isinstance(trackscpy, str):
                        if trackscpy[0] == "[" and trackscpy[-1] == "]":
                            trackscpy = trackscpy.strip(" []")
                        trackscpy = trackscpy.split(",")
                    for _, tcpy in enumerate(trackscpy):
                        if isinstance(tcpy, str):
                            if '[' in tcpy:  # t is list:
                                if ('[' in tcpy) and (']' not in tcpy):
                                    sublist = True
                                if ',' not in tcpy:
                                    tracks.append([int(tcpy.strip(" ']["))])
                                else:
                                    tracks.append([])
                                    for entry in tcpy.split(","):
                                        tracks[-1].append(int(entry.strip(" '[]")))
                            elif sublist:
                                if ']' in tcpy:
                                    sublist = False
                                    tracks[-1].append(int(tcpy.strip(" ]['")))
                                else:
                                    tracks[-1].append(int(tcpy))
                            elif not sublist:
                                tracks.append(int(tcpy.strip(" '")))
                        else:
                            if isinstance(tcpy, list):
                                tracks.append([])
                                for _, tcpys in enumerate(tcpy):
                                    tracks[-1].append(int(tcpys))
                            else:
                                tracks.append(tcpy)
                    structure[page][quest]["track"] = tracks
                except (ValueError, SyntaxError) as e:
                    if status is not None:
                        status.showMessage(f'Invalid value found in a "track" field: {e}', status_duration)
            try:
                if "answers" in structure[page][quest].keys():
                    if "," in structure[page][quest]["answers"]:
                        structure[page][quest]["answers"] = ast.literal_eval(structure[page][quest]["answers"])
                    elif isinstance(structure[page][quest]["answers"], str):
                        structure[page][quest]["answers"] = structure[page][quest]["answers"].strip("[] ")
                    else:  # list-like
                        for entry in range(len(structure[page][quest]["answers"])):
                            if isinstance(entry, str):
                                structure[page][quest]["answers"][entry] = structure[page][quest]["answers"][entry].strip("[] ")
                if "button_texts" in structure[page][quest].keys():
                    if "," in structure[page][quest]["button_texts"]:
                        structure[page][quest]["button_texts"] = ast.literal_eval(
                            structure[page][quest]["button_texts"])
                    elif isinstance(structure[page][quest]["button_texts"], str):
                        structure[page][quest]["button_texts"] = structure[page][quest]["button_texts"].strip("[] ")
                    else:  # list-like
                        for entry in range(len(structure[page][quest]["button_texts"])):
                            structure[page][quest]["button_texts"][entry] = structure[page][quest]["button_texts"][entry].strip("[] ")
                if "header" in structure[page][quest].keys():
                    if "," in structure[page][quest]["header"]:
                        structure[page][quest]["header"] = ast.literal_eval(structure[page][quest]["header"])
                    elif isinstance(structure[page][quest]["header"], str):
                        structure[page][quest]["header"] = structure[page][quest]["header"].strip("[] ")
                    else:  # list-like
                        for entry in range(len(structure[page][quest]["header"])):
                            structure[page][quest]["header"][entry] = structure[page][quest]["header"][entry].strip("[] ")
                if "questions" in structure[page][quest].keys():
                    if "," in structure[page][quest]["questions"]:
                        structure[page][quest]["questions"] = ast.literal_eval(structure[page][quest]["questions"])
                    elif isinstance(structure[page][quest]["questions"], str):
                        structure[page][quest]["questions"] = structure[page][quest]["questions"].strip("[] ")
                    else:  # list-like
                        for entry in range(len(structure[page][quest]["questions"])):
                            structure[page][quest]["questions"][entry] = structure[page][quest]["questions"][entry].strip("[] ")
            except (ValueError, SyntaxError):
                if "answers" in structure[page][quest].keys() and "," in structure[page][quest]["answers"]:
                    structure[page][quest]["answers"] = string_to_list(structure[page][quest]["answers"])
                if "button_texts" in structure[page][quest].keys() and "," in structure[page][quest]["button_texts"]:
                    structure[page][quest]["button_texts"] = string_to_list(structure[page][quest]["button_texts"])
                if "header" in structure[page][quest].keys() and "," in structure[page][quest]["header"]:
                    structure[page][quest]["header"] = string_to_list(structure[page][quest]["header"])
                if "label" in structure[page][quest].keys() and "," in structure[page][quest]["label"]:
                    structure[page][quest]["label"] = string_to_list(structure[page][quest]["label"])
                if "questions" in structure[page][quest].keys() and "," in structure[page][quest]["questions"]:
                    structure[page][quest]["questions"] = string_to_list(structure[page][quest]["questions"])

    for key in structure.keys():
        if structure[key] == "":
            structure.pop(key)
    for page in structure.sections:
        for key in structure[page].keys():
            if structure[page][key] == "" and key != "title":
                structure[page].pop(key)
        for quest in structure[page].sections:
            for key in structure[page][quest].keys():
                if structure[page][quest][key] == "":
                    structure[page][quest].pop(key)

    return structure


def string_to_list(string):
    """convert a string to a list of strings

    Parameters
    ----------
    string : str
        string to be converted

    Returns
    -------
    list[str]
        formatted list
    """
    if string.find(',') == -1:  # single string
        return [string.strip('[] ')]
    else:
        result = []
        string = string.strip('[] ')
        while len(string) > 0:
            string = string.strip(' ')
            if string.startswith('"'):
                next_quote = string.find('"', 1)
                result.append(string[1:next_quote])
                string = string[next_quote + 2:]
            elif string.startswith("'"):
                next_quote = string.find("'", 1)
                result.append(string[1:next_quote])
                string = string[next_quote + 2:]
            else:
                next_comma = string.find(',')
                if next_comma == -1:
                    result.append(string)
                    string = ''
                else:
                    result.append(string[0:next_comma])
                string = string[next_comma + 1:]
        return result


def validate_questionnaire(structure, suppress=False):
    """Check the questionnaire structure for duplicates in answer IDs.

    Parameters
    ----------
    structure : ConfigObj
        holds the structure of the questionnaire to go through.
    suppress : bool, default=False
        If True, no popup will appear for warnings and no errors.

    Returns
    -------
    tuple
        error_found : bool
            Whether errors were found.
        warning_found : bool
            Whether warnings were found.
        warning_details : str
            The text of warnings.

    Raises
    ------
    ValueError
        If an unexpected or unwanted value occurs.
    """
    ids = {}
    error_found = False
    warning_found = False
    error_details = []
    warning_details = []
    ip_mask = "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}"

    if "audio_ip" in structure.keys():
        if structure["audio_ip"] != "":
            match = re.match(ip_mask, structure["audio_ip"])
            if match is None or match.span()[1] < len(structure["audio_ip"]):
                error_found = True
                error_details.append("Invalid audio IP(v4) found.\n")
        elif "audio_port" in structure.keys():
            warning_found = True
            warning_details.append("No audio_ip found, but audio port. Audio will be disabled.\n")
    elif "audio_port" in structure.keys() and structure["audio_port"] != "":
        warning_found = True
        warning_details.append("No audio_ip found, but audio port. Audio will be disabled.\n")

    if "audio_port" in structure.keys():
        if structure["audio_port"] != "":
            try:
                int(structure["audio_port"])
                if int(structure["audio_port"]) < 0 or int(structure["audio_port"]) > 65535:
                    raise ValueError
            except ValueError:
                error_found = True
                error_details.append("Invalid audio port, could not be converted to a number 0-65535.\n")
        elif "audio_ip" in structure.keys():
            warning_found = True
            warning_details.append("No audio_port found, but IP. Audio will be disabled.\n")
    elif "audio_ip" in structure.keys() and structure["audio_ip"] != "":
        warning_found = True
        warning_details.append("No audio_port found, but IP. Audio will be disabled.\n")

    if "audio_recv_port" in structure.keys():
        if structure["audio_recv_port"] != "":
            try:
                int(structure["audio_recv_port"])
                if int(structure["audio_recv_port"]) < 0 or int(structure["audio_recv_port"]) > 65535:
                    raise ValueError
            except ValueError:
                error_found = True
                error_details.append("Invalid audio receive port, could not be converted to a number 0-65535.\n")

    if "video_ip" in structure.keys():
        if structure["video_ip"] != "":
            match = re.match(ip_mask, structure["video_ip"])
            if match is None or match.span()[1] < len(structure["video_ip"]):
                error_found = True
                error_details.append("Invalid video IP(v4) found.\n")
        elif "video_port" in structure.keys():
            warning_found = True
            warning_details.append("No video_ip found, but video port. Video will be disabled.\n")
    elif "video_port" in structure.keys() and structure["video_port"] != "":
        warning_found = True
        warning_details.append("No video_ip found, but video port. Video will be disabled.\n")

    if "video_port" in structure.keys():
        if structure["video_port"] != "":
            try:
                int(structure["video_port"])
                if int(structure["video_port"]) < 0 or int(structure["video_port"]) > 65535:
                    raise ValueError
            except ValueError:
                error_found = True
                error_details.append("Invalid video port, could not be converted to a number 0-65535.\n")
        elif "video_ip" in structure.keys():
            warning_found = True
            warning_details.append("No video_port found, but IP. Video will be disabled.\n")
    elif "video_ip" in structure.keys() and structure["video_ip"] != "":
        warning_found = True
        warning_details.append("No video_port found, but IP. Video will be disabled.\n")

    if "video_player" in structure.keys():
        if structure["video_player"] not in video_player:
            error_found = True
            error_details.append("Invalid value for video_player.\n")
        elif "video_ip" in structure.keys() and "video_ip" in structure.keys() and structure["video_player"] == "None":
            warning_found = True
            warning_details.append("No video_player chosen, but IP and port. Video will be disabled.\n")
    elif "video_ip" in structure.keys() and "video_ip" in structure.keys():
        warning_found = True
        warning_details.append("No video_player found, but IP and port. Video will be disabled.\n")

    if "pupil_ip" in structure.keys():
        if structure["pupil_ip"] != "":
            match = re.match(ip_mask, structure["pupil_ip"])
            if match is None or match.span()[1] < len(structure["pupil_ip"]):
                error_found = True
                error_details.append("Invalid pupil IP(v4) found.\n")
        elif "pupil_port" in structure.keys():
            warning_found = True
            warning_details.append("No pupil_ip found, but pupil port. The connection to pupil will be disabled.\n")
    elif "pupil_port" in structure.keys() and structure["pupil_port"] != "":
        warning_found = True
        warning_details.append("No pupil_ip found, but pupil port. The connection to pupil will be disabled.\n")

    if "pupil_port" in structure.keys():
        if structure["pupil_port"] != "":
            try:
                int(structure["pupil_port"])
                if int(structure["pupil_port"]) < 0 or int(structure["pupil_port"]) > 65535:
                    raise ValueError
            except ValueError:
                error_found = True
                error_details.append("Invalid pupil port, could not be converted to a number 0-65535.\n")
        elif "pupil_ip" in structure.keys():
            warning_found = True
            warning_details.append("No pupil_port found, but IP. The connection to pupil will be disabled.\n")
    elif "pupil_ip" in structure.keys() and structure["pupil_ip"] != "":
        warning_found = True
        warning_details.append("No pupil_port found, but IP. The connection to pupil will be disabled.\n")

    if "help_ip" in structure.keys():
        if structure["help_ip"] != "":
            match = re.match(ip_mask, structure["help_ip"])
            if match is None or match.span()[1] < len(structure["help_ip"]):
                error_found = True
                error_details.append("Invalid help IP(v4) found.\n")
        elif "help_port" in structure.keys():
            warning_found = True
            warning_details.append("No help_ip found, but help port. Calling help will be disabled.\n")
    elif "help_port" in structure.keys() and structure["help_port"] != "":
        warning_found = True
        warning_details.append("No help_ip found, but help port. Calling help will be disabled.\n")

    if "help_port" in structure.keys():
        if structure["help_port"] != "":
            try:
                int(structure["help_port"])
                if int(structure["help_port"]) < 0 or int(structure["help_port"]) > 65535:
                    raise ValueError
            except ValueError:
                error_found = True
                error_details.append("Invalid help port, could not be converted to a number 0-65535.\n")
        elif "help_ip" in structure.keys():
            warning_found = True
            warning_details.append("No help_port found, but IP. Calling help will be disabled.\n")
    elif "help_ip" in structure.keys() and structure["help_ip"] != "":
        warning_found = True
        warning_details.append("No help_port found, but IP. Calling help will be disabled.\n")

    if "help_text" in structure.keys() and "help_ip" not in structure.keys() and "help_port" not in structure.keys():
        warning_found = True
        warning_details.append("No help connection given, but text. Calling help will be disabled.\n")
    elif "help_text" not in structure.keys() and "help_ip" in structure.keys() and "help_port" in structure.keys():
        warning_found = True
        warning_details.append("No text given for the help button, but a connection. The external logging will still work.\n")

    if "global_osc_ip" in structure.keys():
        if structure["global_osc_ip"] != "":
            match = re.match(ip_mask, structure["global_osc_ip"])
            if match is None or match.span()[1] < len(structure["global_osc_ip"]):
                error_found = True
                error_details.append("Invalid global_osc IP(v4) found.\n")
        elif "global_osc_send_port" in structure.keys():
            warning_found = True
            warning_details.append("No global_osc_ip found, but global_osc_send_port. Sending over global OSC will be disabled.\n")
        elif "global_osc_recv_port" in structure.keys():
            warning_found = True
            warning_details.append("No global_osc_ip found, but global_osc_recv_port. Receiving over global OSC will be disabled.\n")
    elif "global_osc_send_port" in structure.keys() and structure["global_osc_send_port"] != "":
        warning_found = True
        warning_details.append("No global_osc_ip found, but global_osc_send_port. Sending over global OSC will be disabled.\n")
    elif "global_osc_recv_port" in structure.keys() and structure["global_osc_recv_port"] != "":
        warning_found = True
        warning_details.append("No global_osc_ip found, but global_osc_recv_port. Receiving over global OSC will be disabled.\n")

    if "global_osc_send_port" in structure.keys():
        if structure["global_osc_send_port"] != "":
            try:
                int(structure["global_osc_send_port"])
                if int(structure["global_osc_send_port"]) < 0 or int(structure["global_osc_send_port"]) > 65535:
                    raise ValueError
            except ValueError:
                error_found = True
                error_details.append("Invalid global_osc_send_port, could not be converted to a number 0-65535.\n")
        elif "global_osc_ip" in structure.keys():
            warning_found = True
            warning_details.append("No global_osc_send_port found, but IP. Sending over global will be disabled.\n")
    elif "global_osc_ip" in structure.keys() and structure["global_osc_ip"] != "":
        warning_found = True
        warning_details.append("No global_osc_send_port found, but IP. Sending over global will be disabled.\n")

    if "global_osc_recv_port" in structure.keys():
        if structure["global_osc_recv_port"] != "":
            try:
                int(structure["global_osc_recv_port"])
                if int(structure["global_osc_recv_port"]) < 0 or int(structure["global_osc_recv_port"]) > 65535:
                    raise ValueError
            except ValueError:
                error_found = True
                error_details.append("Invalid global_osc_recv_port, could not be converted to a number 0-65535.\n")
        elif "global_osc_ip" in structure.keys():
            warning_found = True
            warning_details.append("No global_osc_recv_port found, but IP. Receiving over global will be disabled.\n")
    elif "global_osc_ip" in structure.keys() and structure["global_osc_ip"] != "":
        warning_found = True
        warning_details.append("No global_osc_recv_port found, but IP. Receiving over global will be disabled.\n")

    if "go_back" in structure.keys():
        try:
            _ = structure.as_bool("go_back")
        except ValueError:
            error_found = True
            error_details.append("No valid value found for 'go_back'.\n")
            # structure["go_back"] = False  # default value
    else:
        structure["go_back"] = False
        warning_found = True
        warning_details.append("No option for 'go_back' found, using False as default value.\n")

    if "back_text" in structure.keys():
        if "go_back" not in structure.keys() or not structure.as_bool("go_back"):
            warning_found = True
            warning_details.append(
                "Backwards navigation is not allowed but text for back button was set. The button will not be displayed.\n")
        if "forward_text" in structure.keys() and structure["back_text"] == structure["forward_text"]:
            warning_found = True
            warning_details.append("Text for forward and backward button are the same.\n")

    if "send_text" in structure.keys() and "forward_text" in structure.keys() and structure["send_text"] == structure["forward_text"]:
        warning_found = True
        warning_details.append("Text for forward and send button are the same.\n")

    if "answer_pos" in structure.keys() and "answer_neg" in structure.keys() and structure["answer_pos"] == structure["answer_neg"]:
        warning_found = True
        warning_details.append("Text for positive and negative answer are the same.\n")

    if "delimiter" in structure.keys() and (len(structure["delimiter"]) > 1):
        error_found = True
        error_details.append("Invalid delimiter found. It can only have one character.\n")

    if "filepath_results" in structure.keys():
        if not path.exists(path.dirname(structure["filepath_results"])):
            warning_found = True
            warning_details.append("Path for results file does not exist. It will be created.\n")
            drives = [chr(x) + ":" for x in range(65, 91) if
                      path.exists(chr(x) + ":")]  # TODO this works only for windows?
            if len(path.splitdrive(structure["filepath_results"])[0]) > 0 and \
                    path.splitdrive(structure["filepath_results"])[0] not in drives:
                error_found = True
                error_details.append("Invalid drive name for results file path.\n")

    if "stylesheet" in structure.keys():
        if not path.exists(structure["stylesheet"]):
            error_found = True
            error_details.append("Invalid stylesheet path.\n")
        elif not structure["stylesheet"].endswith(".qss"):
            error_found = True
            error_details.append("Invalid file for stylesheet, it has to be *.qss.\n")

    if "randomization" in structure.keys():
        if structure["randomization"] not in randomize_options:
            error_found = True
            error_details.append("Invalid randomization option.\n")
    elif "randomization_file" in structure.keys() and "randomization" not in structure.keys():
        warning_found = True
        warning_details.append("Randomization_file found, but no option for randomization.\n")

    if "randomization_file" in structure.keys():
        if not path.exists(structure["randomization_file"]):
            error_found = True
            error_details.append("Invalid randomization_file path.\n")
        elif not (structure["randomization_file"].endswith(".txt") or structure["randomization_file"].endswith(".csv")):
            error_found = True
            error_details.append("Invalid file for randomization, it has to be *.txt or *.csv.\n")
        else:  # valid filepath
            if not validate_random(structure["randomization_file"]):
                error_found = True
                error_details.append("Contents of randomization_file invalid.\n")
    elif "randomization_file" not in structure.keys() and "randomization" in structure.keys() and structure["randomization"] == "from file":
        error_found = True
        error_details.append("Randomization 'from file' chosen, but no file given.\n")

    if "button_fade" in structure.keys():
        if structure["button_fade"] != "":
            try:
                int(structure["button_fade"])
                if int(structure["button_fade"]) < 0:
                    raise ValueError
            except ValueError:
                error_found = True
                error_details.append("'button_fade' could not be converted to a non-negative number.\n")

    if "save_after" in structure.keys() and structure["save_after"] not in structure.sections and structure["save_after"] is not None:
        error_found = True
        error_details.append("The value given for 'save_after' is not the name of a page of this questionnaire.\n")
    elif "save_after" not in structure.keys() and len(structure.sections) > 0:
        warning_found = True
        warning_details.append("No value for 'save_after' given, saving after the last page by default.\n")
        structure["save_after"] = structure.sections[-1] if len(structure.sections) > 0 else None

    for page in structure.sections:
        if not structure[page].sections:
            warning_found = True
            warning_details.append(f'There are no questions on page {page}.\n')

        if "pupil_on_next" in structure[page].keys():
            if structure[page]["pupil_on_next"] == '' or structure[page]["pupil_on_next"] == 'None':
                structure[page]["pupil_on_next"] = None
            if ("pupil_ip" not in structure.keys() or structure["pupil_ip"] == '') or \
                    ("pupil_port" not in structure.keys() or structure["pupil_port"] == ''):
                warning_found = True
                warning_details.append("Incomplete connection to pupil given. The connection to pupil will be disabled.\n")

        if "randomgroup" in structure[page].keys() and ("randomization" not in structure.keys() or ("randomization" in structure.keys() and structure["randomization"] == "None")):
            error_found = True
            error_details.append("Using randomgroup, but no randomization option was chosen.\n")

        for quest in structure[page].sections:
            if structure[page][quest] == {}:
                warning_found = True
                warning_details.append(f'There are no attributes for question "{quest}" on page "{page}".\n')

            if "id" in structure[page][quest].keys():
                if structure[page][quest]["id"] == "":
                    error_found = True
                    error_details.append(f'No ID was given for question "{quest}" on page "{page}".\n')
                elif structure[page][quest]["id"] not in ids:
                    ids[structure[page][quest]["id"]] = (page, quest)
                else:
                    error_found = True
                    error_details.append(
                        f'ID "{structure[page][quest]["id"]}" already used in question "{ids[structure[page][quest]["id"]][1]}" on page "{ids[structure[page][quest]["id"]][0]}". Found again in question "{quest}" on page "{page}".\n')
            elif "id" not in structure[page][quest].keys() and "type" in structure[page][quest].keys() and "id" in fields_per_type[structure[page][quest]["type"]][0].keys():
                error_found = True
                error_details.append(f'No ID was given for question "{quest}" on page "{page}".\n')

            if "x" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("x")
                except ValueError:
                    error_found = True
                    error_details.append(f'No valid value found for "x" for question "{quest}" on page "{page}".\n')
                    structure[page][quest]["x"] = False  # This happens so the rest of the routine  where x is referenced does not have to catch errors
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX" and "x" not in structure[page][quest].keys():
                structure[page][quest]["x"] = False
                warning_found = True
                warning_details.append(f'No option for "x" found for question "{quest}" on page "{page}", using False as default value.\n')

            if "play_once" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("play_once")
                except ValueError:
                    error_found = True
                    error_details.append(f'No valid value found for "play_once" for question "{quest}" on page "{page}".\n')
                    structure[page][quest]["play_once"] = False
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Player" and "play_once" not in structure[page][quest].keys():
                structure[page][quest]["play_once"] = False
                warning_found = True
                warning_details.append(f'No option for "play_once" found for question "{quest}" on page "{page}", using False by default.\n')

            if "required" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("required")
                except ValueError:
                    error_found = True
                    error_details.append(f'No valid value found for "required" for question "{quest}" on page "{page}".\n')
                    structure[page][quest]["required"] = False  # default value

            if "labelled" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("labelled")
                except ValueError:
                    error_found = True
                    error_details.append(f'No valid value found for "labelled" for question "{quest}" on page "{page}".\n')
                    structure[page][quest]["labelled"] = False  # default value
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Slider" and "labelled" not in structure[page][quest].keys():
                structure[page][quest]["labelled"] = False
                warning_found = True
                warning_details.append(f'No option for "labelled" found for question "{quest}" on page "{page}", setting it to False.\n')

            if "question_above" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("question_above")
                except ValueError:
                    error_found = True
                    error_details.append(f'No valid value found for "question_above" for question "{quest}" on page "{page}".\n')
                    structure[page][quest]["question_above"] = False  # default value

            if "text" in structure[page][quest].keys() and structure[page][quest]["text"] == "":
                warning_found = True
                warning_details.append(f'No text was given for question "{quest}" on page "{page}".\n')
            elif "text" not in structure[page][quest].keys() and "type" in structure[page][quest].keys() and \
                    "text" in fields_per_type[structure[page][quest]["type"]][0].keys():
                structure[page][quest]["text"] = ""
                warning_found = True
                warning_details.append(f'No text was given for question "{quest}" on page "{page}".\n')

            if "answers" in structure[page][quest].keys():
                if structure[page][quest]["answers"] == "" and ("type" not in structure[page][quest].keys() or ("type" in structure[page][quest].keys() and not structure[page][quest]["type"] == "ABX")):
                    warning_found = True
                    warning_details.append(f'No answer possibilities were given for question "{quest}" on page "{page}".\n')
                if "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX":
                    if ((not isinstance(structure[page][quest]["answers"], list) and not isinstance(structure[page][quest]["answers"], tuple)) and
                        structure[page][quest]["answers"] != "") or \
                            (isinstance(structure[page][quest]["answers"], (list, tuple)) and len(structure[page][quest]["answers"]) != 2):
                        error_found = True
                        error_details.append(f'Please give two answer options for the ABX type question "{quest}" on page "{page}" or leave this field empty.\n')
                elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "AFC":
                    if ((not isinstance(structure[page][quest]["answers"], list) and not isinstance(structure[page][quest]["answers"], tuple)) and structure[page][quest]["answers"] != "") or (isinstance(structure[page][quest]["answers"], (list, tuple)) and len(structure[page][quest]["answers"]) != structure[page][quest].as_int("number_of_choices")):
                        error_found = True
                        error_details.append(f'Please give as many answer options for the AFC type question "{quest}" as number_of_choices on page "{page}" or leave this field empty.\n')
            elif "type" in structure[page][quest].keys() and \
                    (structure[page][quest]["type"] == "Radio" or structure[page][quest]["type"] == "Check" or
                     structure[page][quest]["type"] == "Matrix") and "answers" not in structure[page][quest].keys():
                structure[page][quest]["answers"] = ""
                warning_found = True
                warning_details.append(f'No answer possibilities were given for question "{quest}" on page "{page}".\n')

            if "start_answer_id" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["start_answer_id"])
                    if int(structure[page][quest]["start_answer_id"]) < 0:
                        error_found = True
                        error_details.append(f'The start answer ID in question "{quest}" on page "{page}" can not have a negative value.\n')
                except ValueError:
                    error_found = True
                    error_details.append(f'The start answer ID in question "{quest}" on page "{page}" could not be interpreted as an integer.\n')

            if "min" in structure[page][quest].keys():
                if structure[page][quest]["min"] == "":
                    error_found = True
                    error_details.append(f'No minimum value was given for the slider in question "{quest}" on page "{page}".\n')
                else:
                    try:
                        float(structure[page][quest]["min"])
                    except ValueError:
                        error_found = True
                        error_details.append(f'The minimum value found for the slider in question "{quest}" on page "{page}" could not be interpreted as a number.\n')
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Slider" and "min" not in structure[page][quest].keys():
                error_found = True
                error_details.append(f'No minimum value was given for the slider in question "{quest}" on page "{page}".\n')

            if "max" in structure[page][quest].keys():
                if structure[page][quest]["max"] == "":
                    error_found = True
                    error_details.append(f'No maximum value was given for the slider in question "{quest}" on page "{page}".\n')
                else:
                    try:
                        float(structure[page][quest]["max"])
                    except ValueError:
                        error_found = True
                        error_details.append(f'The maximum value found for the slider in question "{quest}" on page "{page}" could not be interpreted as a number.\n')
                try:
                    if "min" in structure[page][quest].keys() and round(float(structure[page][quest]["max"]) - float(structure[page][quest]["min"]), 3) == 0.0:
                        error_found = True
                        error_details.append(f'Maximum and Minimum value for the slider in question "{quest}" on page "{page}" are the same.\n')
                except ValueError:
                    pass
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Slider" and \
                    "max" not in structure[page][quest].keys():
                error_found = True
                error_details.append(f'"No maximum value was given for the slider in question "{quest}" on page "{page}".\n')

            if "start" in structure[page][quest].keys():
                if structure[page][quest]["start"] == "":
                    error_found = True
                    error_details.append(f'No starting value was given for the slider in question "{quest}" on page "{page}".\n')
                else:
                    try:
                        float(structure[page][quest]["start"])
                        if "min" in structure[page][quest].keys() and "max" in structure[page][quest].keys():
                            if float(structure[page][quest]["min"]) < float(structure[page][quest]["max"]):
                                if float(structure[page][quest]["start"]) < float(structure[page][quest]["min"]):
                                    structure[page][quest]["start"] = float(structure[page][quest]["min"]) if float(structure[page][quest]["min"]) != int(structure[page][quest]["min"]) or float(structure[page][quest]["step"]) != int(structure[page][quest]["step"]) else int(structure[page][quest]["min"])
                                elif float(structure[page][quest]["start"]) > float(structure[page][quest]["max"]):
                                    structure[page][quest]["start"] = float(structure[page][quest]["max"]) if float(structure[page][quest]["max"]) != int(structure[page][quest]["max"]) or float(structure[page][quest]["step"]) != int(structure[page][quest]["step"]) else int(structure[page][quest]["max"])
                            else: # decreasing numbers
                                if float(structure[page][quest]["start"]) > float(structure[page][quest]["min"]):
                                    structure[page][quest]["start"] = float(structure[page][quest]["min"]) if float(structure[page][quest]["min"]) != int(structure[page][quest]["min"]) or float(structure[page][quest]["step"]) != int(structure[page][quest]["step"]) else int(structure[page][quest]["min"])
                                elif float(structure[page][quest]["start"]) < float(structure[page][quest]["max"]):
                                    structure[page][quest]["start"] = float(structure[page][quest]["max"]) if float(structure[page][quest]["max"]) != int(structure[page][quest]["max"]) or float(structure[page][quest]["step"]) != int(structure[page][quest]["step"]) else int(structure[page][quest]["max"])
                    except ValueError:
                        error_found = True
                        error_details.append(f'The starting value found for the slider in question "{quest}" on page "{page}" could not be interpreted as a number.\n')
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Slider" and \
                    "start" not in structure[page][quest].keys():
                error_found = True
                error_details.append(f'No starting value was given for the slider in question "{quest}" on page "{page}".\n')

            if "step" in structure[page][quest].keys():
                if structure[page][quest]["step"] == "":
                    error_found = True
                    error_details.append(f'No step value was given for the slider in question "{quest}" on page "{page}".\n')
                else:
                    try:
                        if float(structure[page][quest]["step"]) <= 0:
                            error_found = True
                            error_details.append(f'The step value found for the slider in question "{quest}" on page "{page}" needs to be bigger than 0.\n')
                    except ValueError:
                        error_found = True
                        error_details.append(f'The step value found for the slider in question "{quest}" on page "{page}" could not be interpreted as a number.\n')
                try:
                    if "min" in structure[page][quest].keys() and "max" in structure[page][quest].keys() \
                            and abs(float(structure[page][quest]["max"]) - float(structure[page][quest]["min"])) < float(structure[page][quest]["step"]):
                        error_found = True
                        error_details.append(f'The step value for the slider in question "{quest}" on page "{page}" is bigger than the range.\n')
                except ValueError:
                    pass
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Slider" and "step" not in structure[page][quest].keys():
                error_found = True
                error_details.append(f'No step value was given for the slider in question "{quest}" on page "{page}".\n')

            if "label" in structure[page][quest].keys() and "labelled" in structure[page][quest].keys() and \
                    structure[page][quest].as_bool("labelled"):
                if not isinstance(structure[page][quest]["label"][0], list) and not isinstance(structure[page][quest]["label"][0], tuple):
                    if len(structure[page][quest]["label"]) != (float(structure[page][quest]["max"]) - float(structure[page][quest]["min"])) / float(structure[page][quest]["step"]) + 1:
                        error_found = True
                        error_details.append(f'The number of given labels does not match the number of ticks for question "{quest}" on page "{page}".\n')
                elif len(structure[page][quest]["label"][0]) != 2:
                    error_found = True
                    error_details.append(f'No valid format for labels for question "{quest}" on page "{page}".\n')
                else:  # list / tuple of single pairs
                    tick = []
                    try:
                        for pair in structure[page][quest]["label"]:
                            tick.append(float(pair[0]))
                            if not (float(structure[page][quest]["max"]) <= float(pair[0]) <= float(structure[page][quest]["min"]) or
                                    float(structure[page][quest]["max"]) >= float(pair[0]) >= float(structure[page][quest]["min"])):
                                error_found = True
                                error_details.append(f'Tick value outside of slider range found for question "{quest}" on page "{page}".\n')
                        if len(tick) != len(set(tick)):
                            error_found = True
                            error_details.append(f'Double definition of tick labels found for question "{quest}" on page "{page}".\n')
                    except ValueError:
                        error_found = True
                        error_details.append(f'A label tick for the slider in question "{quest}" on page "{page}" could not be interpreted as a number.\n')

            if "policy" in structure[page][quest].keys():
                if structure[page][quest]["policy"] == "None" or structure[page][quest]["policy"] == "[None]":
                    structure[page][quest]["policy"] = ["None"]
                if (isinstance(structure[page][quest]["policy"], str) and structure[page][quest]["policy"] not in policy_possibilities) or \
                        (isinstance(structure[page][quest]["policy"], list) and structure[page][quest]["policy"][0] not in policy_possibilities):
                    error_found = True
                    error_details.append(f'Invalid policy type in question "{quest}" on page "{page}".\n')
                if (isinstance(structure[page][quest]["policy"], str) and structure[page][quest]["policy"] == "int") or \
                        (isinstance(structure[page][quest]["policy"], list) and structure[page][quest]["policy"][0] == 'int' and len(structure[page][quest]["policy"]) != 3):
                    error_found = True
                    error_details.append(f'Policy type "int" takes two arguments, a different amount was given in question "{quest}" on page "{page}".\n')
                elif (isinstance(structure[page][quest]["policy"], str) and structure[page][quest]["policy"] == "double") or \
                        (isinstance(structure[page][quest]["policy"], list) and structure[page][quest]["policy"][0] == 'double' and len(structure[page][quest]["policy"]) != 4):
                    error_found = True
                    error_details.append(f'Policy type "double" takes three arguments, a different amount was given in question "{quest}" on page "{page}".\n')
                elif (isinstance(structure[page][quest]["policy"], str) and structure[page][quest]["policy"] == "regex") or \
                        (isinstance(structure[page][quest]["policy"], list) and structure[page][quest]["policy"][0] == 'regex' and len(structure[page][quest]["policy"]) != 2):
                    error_found = True
                    error_details.append(f'Policy type "regex" takes one argument, a different amount was given in question "{quest}" on page "{page}".\n')

                if (structure[page][quest]["policy"][0] == "int") or (structure[page][quest]["policy"][0] == "double"):
                    if structure[page][quest]["policy"][1] == "":
                        error_found = True
                        error_details.append(f'No minimum value was given for the policy in question "{quest}" on page "{page}".\n"')
                    else:
                        try:
                            if structure[page][quest]["policy"][0] == "int":
                                int(structure[page][quest]["policy"][1])
                            else:
                                float(structure[page][quest]["policy"][1])
                        except ValueError:
                            error_found = True
                            error_details.append(f'Minimum value given for the policy in question "{quest}" on page "{page}" could not be converted to a valid number.\n')
                    if structure[page][quest]["policy"][2] == "":
                        error_found = True
                        error_details.append(f'No maximum value was given for the policy in question "{quest}" on page "{page}".\n')
                    else:
                        try:
                            if structure[page][quest]["policy"][0] == "int":
                                int(structure[page][quest]["policy"][2])
                            else:
                                float(structure[page][quest]["policy"][2])
                        except ValueError:
                            error_found = True
                            error_details.append(f'Maximum value given for the policy in question "{quest}" on page "{page}" could not be converted to a valid number.\n')
                if structure[page][quest]["policy"][0] == "double":
                    if structure[page][quest]["policy"][3] == "":
                        error_found = True
                        error_details.append(f'No number of decimals was given for the policy in question "{quest}" on page "{page}".\n')
                    else:
                        try:
                            int(structure[page][quest]["policy"][3])
                        except ValueError:
                            error_found = True
                            error_details.append(f'Number of decimals given for the policy in question "{quest}" on page "{page}" could not be converted to a number.\n')
                if structure[page][quest]["policy"][0] == "regex":
                    if structure[page][quest]["policy"][1] == "":
                        error_found = True
                        error_details.append(f'No regex was given for the policy in question "{quest}" on page "{page}".\n')
                    else:
                        try:
                            re.compile(str(structure[page][quest]["policy"][1]))
                        except re.error:
                            error_found = True
                            error_details.append(f'An invalid regex was given for the policy in question "{quest}" on page "{page}".\n')

            if "start_cue" in structure[page][quest].keys():
                if structure[page][quest]["start_cue"] == "":
                    error_found = True
                    error_details.append(f'No start cue was given in question "{quest}" on page "{page}".\n')
                else:
                    try:
                        int(structure[page][quest]["start_cue"])
                    except (ValueError, TypeError):
                        error_found = True
                        error_details.append(f'Start cue given in question "{quest}" on page "{page}" could not be converted to a number.\n')
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Player" \
                    and "start_cue" not in structure[page][quest].keys():
                error_found = True
                error_details.append(f'No start cue was given in question "{quest}" on page "{page}".\n')

            if "end_cue" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["end_cue"])
                    if "start_cue" in structure[page][quest].keys() and structure[page][quest]["start_cue"] == structure[page][quest]["end_cue"]:
                        error_found = True
                        error_details.append(f'The same cue ({structure[page][quest]["start_cue"]}) was used as start- and end-cue for one condition in question "{quest}" on page "{page}".\n')
                except (ValueError, TypeError):
                    error_found = True
                    error_details.append(f'End cue given in question "{quest}" on page "{page}" could not be converted to a number.\n')

            if "track" in structure[page][quest].keys():
                if structure[page][quest]["track"] == "":
                    error_found = True
                    error_details.append(f'No track(s) was given for question "{quest}" on page "{page}".\n')
                else:
                    try:
                        if isinstance(structure[page][quest]["track"], (list, tuple)):
                            if "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX" and (
                                    len(structure[page][quest]["track"]) > 2 or len(structure[page][quest]["track"]) < 1):
                                error_found = True
                                error_details.append(f'There should be 1 or 2 tracks for AB(X)-tests, but {len(structure[page][quest]["track"])} were given in question "{quest}" on page "{page}".\n')
                            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "MUSHRA" and \
                                    len(structure[page][quest]["track"]) != len(structure[page][quest]["start_cues"]) and \
                                    len(structure[page][quest]["track"]) > 1:
                                error_found = True
                                error_details.append(f'The number of tracks given does not equal the number of cues given in question "{quest}" on page "{page}".\n')

                            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX" and len(structure[page][quest]["track"]) == 1:
                                structure[page][quest]["track"].append(structure[page][quest]["track"][0])
                            for entry in range(len(structure[page][quest]["track"])):
                                if isinstance(structure[page][quest]["track"][entry], str):
                                    if isinstance(structure[page][quest]["track"], tuple):
                                        structure[page][quest]["track"] = list(structure[page][quest]["track"])
                                    structure[page][quest]["track"][entry] = structure[page][quest]["track"][entry].strip("' \"")
                                    int(structure[page][quest]["track"][entry])
                                    if int(structure[page][quest]["track"][entry]) < 1:
                                        error_found = True
                                        error_details.append(f'Tracks given for question "{quest}" on page "{page}" needs to be greater than 0.\n')
                                elif isinstance(structure[page][quest]["track"][entry], list):
                                    if "type" in structure[page][quest].keys() and structure[page][quest]["type"] != "MUSHRA":
                                        error_found = True
                                        error_details.append(f'Tracks given for question "{quest}" on page "{page}" need to be one or more integers, not lists.\n')
                                    for entry2 in range(len(structure[page][quest]["track"][entry])):
                                        if not isinstance(structure[page][quest]["track"][entry][entry2], int):
                                            structure[page][quest]["track"][entry][entry2] = structure[page][quest]["track"][entry][entry2].strip("' \"")
                                        int(structure[page][quest]["track"][entry][entry2])
                                        if int(structure[page][quest]["track"][entry][entry2]) < 1:
                                            error_found = True
                                            error_details.append(f'Tracks given for question "{quest}" on page "{page}" needs to be greater than 0.\n')
                                else:  # int
                                    if structure[page][quest]["track"][entry] < 1:
                                        error_found = True
                                        error_details.append(f'Track given for question "{quest}" on page "{page}" needs to be greater than 0.\n')
                        else:
                            int(structure[page][quest]["track"])

                            if int(structure[page][quest]["track"]) < 1:
                                error_found = True
                                error_details.append(f'Track given for question "{quest}" on page "{page}" needs to be greater than 0.\n')
                            if "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX":
                                structure[page][quest]["track"] = [structure[page][quest]["track"], structure[page][quest]["track"]]
                    except ValueError:
                        error_found = True
                        error_details.append(f'Track(s) given for question "{quest}" on page "{page}" could not be converted to a number or list of numbers.\n')
            elif "type" in structure[page][quest].keys() and \
                    (structure[page][quest]["type"] == "Player" or structure[page][quest]["type"] == "MUSHRA" or
                     structure[page][quest]["type"] == "ABX" or structure[page][quest]["type"] == "AFC") \
                    and "track" not in structure[page][quest].keys():
                error_found = True
                error_details.append(f'No track(s) was given for question "{quest}" on page "{page}".\n')

            if "buttons" in structure[page][quest].keys():
                if len(structure[page][quest]["buttons"]) == 0:
                    warning_found = True
                    warning_details.append(f'No buttons are displayed for the player in question "{quest}" on page "{page}". It will play when this page is loaded.\n')
                else:
                    try:
                        if isinstance(structure[page][quest]["buttons"], (list, tuple)):
                            for button in structure[page][quest]["buttons"]:
                                if button not in player_buttons:
                                    raise ValueError
                            if "Play" not in structure[page][quest]["buttons"]:
                                warning_found = True
                                warning_details.append(f'No Play button is displayed for the player in question "{quest}" on page "{page}". It will play when this page is loaded.\n')
                        elif isinstance(structure[page][quest]["buttons"], str):
                            if structure[page][quest]["buttons"] not in player_buttons:
                                raise ValueError
                            elif "Play" != structure[page][quest]["buttons"]:
                                warning_found = True
                                warning_details.append(f'No Play button is displayed for the player in question "{quest}" on page "{page}". It will play when this page is loaded.\n')
                        else:
                            raise ValueError
                    except ValueError:
                        error_found = True
                        error_details.append(f'Invalid value found for "buttons" for question "{quest}" on page "{page}".\n')
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Player" and "buttons" not in structure[page][quest].keys():
                warning_found = True
                warning_details.append(f'No buttons are displayed for the player in question "{quest}" on page "{page}". It will play when this page is loaded.\n')

            if "start_cues" in structure[page][quest].keys():
                if structure[page][quest]["start_cues"] == "":
                    error_found = True
                    error_details.append(f'No start cues were given for question "{quest}" on page "{page}".\n')
                else:
                    try:
                        if isinstance(structure[page][quest]["start_cues"], (list, tuple)):
                            for entry in range(len(structure[page][quest]["start_cues"])):
                                if isinstance(structure[page][quest]["start_cues"][entry], str):
                                    if isinstance(structure[page][quest]["start_cues"], tuple):
                                        structure[page][quest]["start_cues"] = list(structure[page][quest]["start_cues"])
                                    structure[page][quest]["start_cues"][entry] = structure[page][quest]["start_cues"][entry].strip("' \"")
                                    int(structure[page][quest]["start_cues"][entry])
                            if "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX" and (len(structure[page][quest]["start_cues"]) != 2):
                                error_found = True
                                error_details.append(f'There should be exactly 2 start_cues for AB(X)-tests, but {1 if isinstance(structure[page][quest]["start_cues"], int) else len(structure[page][quest]["start_cues"])} were given in question "{quest}" on page "{page}".\n')
                        else:
                            int(structure[page][quest]["start_cues"])
                            if structure[page][quest]["type"] == "ABX":
                                error_found = True
                                error_details.append(f'There should be exactly 2 start_cues for AB(X)-tests, but {1 if isinstance(structure[page][quest]["start_cues"], int) else len(structure[page][quest]["start_cues"])} were given in question "{quest}" on page "{page}".\n')

                    except ValueError:
                        error_found = True
                        error_details.append(f'Start cues given for question "{quest}" on page "{page}" could not be converted to a list of numbers.\n')
            elif "type" in structure[page][quest].keys() and (structure[page][quest]["type"] == "MUSHRA" or
                                                              structure[page][quest]["type"] == "ABX" or
                                                              structure[page][quest]["type"] == "AFC") \
                    and "start_cues" not in structure[page][quest].keys():
                error_found = True
                error_details.append(f'No start cues were given for question "{quest}" on page "{page}".\n')

            if "end_cues" in structure[page][quest].keys():
                if structure[page][quest]["end_cues"] == "":
                    error_found = True
                    error_details.append(f'No end cues were given for question "{quest}" on page "{page}".\n')
                else:
                    try:
                        if isinstance(structure[page][quest]["end_cues"], (list, tuple)):
                            for entry in range(len(structure[page][quest]["end_cues"])):
                                if isinstance(structure[page][quest]["end_cues"][entry], str):
                                    if isinstance(structure[page][quest]["end_cues"], tuple):
                                        structure[page][quest]["end_cues"] = list(structure[page][quest]["end_cues"])
                                    structure[page][quest]["end_cues"][entry] = structure[page][quest]["end_cues"][entry].strip("' \"")
                                    int(structure[page][quest]["end_cues"][entry])
                        else:
                            int(structure[page][quest]["end_cues"])
                    except ValueError:
                        error_found = True
                        error_details.append(f'End cues given for question "{quest}" on page "{page}" could not be converted to a list of numbers.\n')
                    if "start_cues" not in structure[page][quest].keys() or len(structure[page][quest]["end_cues"]) != len(structure[page][quest]["start_cues"]):
                        error_found = True
                        error_details.append(f'The number of start- and end-cues in question "{quest}" on page "{page}" does not match.\n')
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "MUSHRA" and "end_cues" not in structure[page][quest].keys():
                error_found = True
                error_details.append(f'No end cues were given for question "{quest}" on page "{page}".\n')

            if "start_cues" in structure[page][quest].keys() and "end_cues" in structure[page][quest].keys():
                if isinstance(structure[page][quest]["end_cues"], (list, tuple)) and isinstance(structure[page][quest]["start_cues"], (list, tuple)) and (
                        len(structure[page][quest]["start_cues"]) == len(structure[page][quest]["end_cues"])):
                    for entry in range(len(structure[page][quest]["start_cues"])):
                        if int(structure[page][quest]["start_cues"][entry]) == int(structure[page][quest]["end_cues"][entry]):
                            error_found = True
                            error_details.append(f'The same cue ({structure[page][quest]["start_cues"][entry]}) was used as start- and end-cue for one condition in question "{quest}" on page "{page}".\n')

            if "xfade" in structure[page][quest].keys():
                try:
                    if structure[page][quest].as_bool("xfade"):
                        all_same_marker = True
                        for sc in structure[page][quest]["start_cues"]:
                            if int(sc) != int(structure[page][quest]["start_cues"][0]):
                                all_same_marker = False
                        if "end_cues" not in structure[page][quest].keys(): 
                            error_found = True
                            error_details.append(f'No end cues were given for question "{quest}" on page "{page}".\n')
                        else:
                            for ec in structure[page][quest]["end_cues"]:
                                if int(ec) != int(structure[page][quest]["end_cues"][0]):
                                    all_same_marker = False
                        if not all_same_marker:
                            error_found = True
                            error_details.append(f'Xfade is only applicable if all start- and end-markers are the same each in question "{quest}" on page "{page}".\n')
                        if isinstance(structure[page][quest]["track"], (int, str)) or \
                                (isinstance(structure[page][quest]["track"], (list, tuple)) and
                                 (isinstance(structure[page][quest]["track"][0], list) and len(set(structure[page][quest]["track"][0])) == 1 or len(set(structure[page][quest]["track"])) == 1)):
                            error_found = True
                            error_details.append(f'For xfade stimuli need to be placed on different tracks in question "{quest}" on page "{page}".\n')
                except ValueError:
                    error_found = True
                    error_details.append(f'No valid value found for "xfade" for question "{quest}" on page "{page}".\n')
                    structure[page][quest]["xfade"] = False  # This happens so the rest of the routine where xfade is referenced does not have to catch errors

            if "crossfade" in structure[page][quest].keys():
                try:
                    structure[page][quest].as_bool("crossfade")
                except ValueError:
                    error_found = True
                    error_details.append(f'No valid value found for "crossfade" for question "{quest}" on page "{page}".\n')
                    structure[page][quest]["crossfade"] = False  # This happens so the rest of the routine where crossfade is referenced does not have to catch errors

            if "inscription" in structure[page][quest].keys():
                if structure[page][quest]["inscription"] == "":
                    warning_found = True
                    warning_details.append(f'No inscription for the button in question "{quest}" on page "{page}".\n')
                elif structure[page][quest]["inscription"] == "None":
                    warning_found = True
                    warning_details.append(f'Internally used inscription "None" used in question "{quest}" on page "{page}".\n')
            elif "type" in structure[page][quest].keys() and (structure[page][quest]["type"] == "Button"
                                                              or structure[page][quest]["type"] == "OSCButton") and \
                    "inscription" not in structure[page][quest].keys():
                structure[page][quest]["inscription"] = ""
                warning_found = True
                warning_details.append(f'No inscription for the button in question "{quest}" on page "{page}".\n')

            if "type" in structure[page][quest].keys() and structure[page][quest]["type"] is not None:
                if structure[page][quest]["type"] == "Button" and (
                        "pupil_ip" not in structure.keys() or "pupil_port" not in structure.keys() or
                        structure["pupil_ip"] == "" or structure["pupil_port"] == ""):
                    warning_found = True
                    warning_details.append("This questionnaire uses Pupil Core, but no valid address is set.\n")
                if structure[page][quest]["type"] == "MUSHRA" and ("audio_ip" not in structure.keys() or
                                                                   "audio_port" not in structure.keys() or
                                                                   structure["audio_ip"] == "" or
                                                                   structure["audio_port"] == ""):
                    warning_found = True
                    warning_details.append("This questionnaire uses MUSHRA, but no valid address for an audio-application is set.\n")
                if (structure[page][quest]["type"] == "Player" or structure[page][quest]["type"] == "ABX" or
                    structure[page][quest]["type"] == "AFC") and \
                        ("audio_ip" not in structure.keys() or "audio_port" not in structure.keys() or
                         structure["audio_ip"] == "" or structure["audio_port"] == ""):
                    warning_found = True
                    warning_details.append("This questionnaire uses an audio player, but no valid address for an audio-application is set.\n")
                if structure[page][quest]["type"] == "Player" and "video" in structure[page][quest].keys() \
                        and ("video_ip" not in structure.keys() or "video_port" not in structure.keys() or
                             structure["video_ip"] == "" or structure["video_port"] == ""):
                    warning_found = True
                    warning_details.append(f'This questionnaire uses a video in question "{quest}" on page "{page}", but no valid address for a video-application is set.\n')
                if (structure[page][quest]["type"] == "Button" or "pupil" in structure[page][quest].keys() and structure[page][quest]["pupil"] != "") and \
                        ("pupil_ip" not in structure.keys() or "pupil_port" not in structure.keys() or
                         structure["pupil_ip"] == "" or structure["pupil_port"] == ""):
                    warning_found = True
                    warning_details.append("This questionnaire uses Pupil Core, but no valid address is set.\n")

            if "objectName" in structure[page][quest].keys() and structure[page][quest]["objectName"] != "":
                if structure[page][quest]["objectName"] == "required" or \
                        structure[page][quest]["objectName"] == "headline" or \
                        structure[page][quest]["objectName"] == "SliderHeader":
                    warning_found = True
                    warning_details.append(f'The objectName in question "{quest}" on page "{page}" uses a predefined name.\n')

            if "timer" in structure[page][quest].keys() and structure[page][quest]["timer"] != "":
                try:
                    if int(structure[page][quest]["timer"]) < 0:
                        warning_found = True
                        warning_details.append(f'The timer in question "{quest}" on page "{page}" needs to be greater than or equal to 0. Setting it to 0 by default.\n')
                        structure[page][quest]["timer"] = 0
                except ValueError:
                    error_found = True
                    error_details.append(f'The timer in question "{quest}" on page "{page}" needs to be a numeric value.\n')

            if "password_file" in structure[page][quest].keys():
                if structure[page][quest]["password_file"] == "":
                    warning_found = True
                    warning_details.append(f'No password_file found for question "{quest}" on page "{page}".\n')
                elif not path.isfile(structure[page][quest]["password_file"]):
                    error_found = True
                    error_details.append(f'No valid password_file for question "{quest}" on page "{page}".\n')
                elif not validate_passwords(structure[page][quest]["password_file"], structure[page][quest]["policy"]):
                    warning_found = True
                    warning_details.append(f'Passwords in file do not match policy of field for question "{quest}" on page "{page}".\n')
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Password" and \
                    "password_file" not in structure[page][quest].keys():
                structure[page][quest]["password_file"] = ""
                warning_found = True
                warning_details.append(f'No password_file found for question "{quest}" on page "{page}".\n')

            if "button_texts" in structure[page][quest].keys():
                if (not isinstance(structure[page][quest]["button_texts"], list) and not isinstance(structure[page][quest]["button_texts"], tuple) and
                        structure[page][quest]["button_texts"] != "") or \
                        (isinstance(structure[page][quest]["button_texts"], (list, tuple)) and
                        ((len(structure[page][quest]["button_texts"]) != 2 and not structure[page][quest].as_bool("x")) or
                        (len(structure[page][quest]["button_texts"]) != 3 and structure[page][quest].as_bool("x")))):
                    error_found = True
                    error_details.append(f'Please give no, two or three (if option X is used) button_texts for the ABX type question "{quest}" on page "{page}".\n')

            if "randomize" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("randomize")
                except ValueError:
                    error_found = True
                    error_details.append(f'No valid value found for "randomize" for question "{quest}" on page "{page}".\n')
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Matrix" and \
                    "randomize" not in structure[page][quest].keys():
                structure[page][quest]["randomize"] = False
                warning_found = True
                warning_details.append(f'No option for "randomize" found for question "{quest}" on page "{page}".\n')

            if "questions" in structure[page][quest].keys():
                if structure[page][quest]["questions"] == "" or len(structure[page][quest]["questions"]) == 0:
                    warning_found = True
                    warning_details.append(f'No questions for the matrix in question "{quest}" on page "{page}" found.\n')
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Matrix" and \
                    "questions" not in structure[page][quest].keys():
                structure[page][quest]["questions"] = ""
                warning_found = True
                warning_details.append(f'No questions for the matrix in question "{quest}" on page "{page}" found.\n')

            if "image_file" in structure[page][quest].keys():
                if structure[page][quest]["image_file"] == "":
                    warning_found = True
                    warning_details.append(f'No image_file found for question "{quest}" on page "{page}".\n')
                elif not path.isfile(structure[page][quest]["image_file"]):
                    error_found = True
                    error_details.append(f'No valid image_file for question "{quest}" on page "{page}".\n')
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Image" and \
                    "image_file" not in structure[page][quest].keys():
                structure[page][quest]["image_file"] = ""
                warning_found = True
                warning_details.append(f'No image_file found for question "{quest}" on page "{page}".\n')

            if "image_position" in structure[page][quest].keys():
                if structure[page][quest]["image_position"] not in image_positions:
                    error_found = True
                    error_details.append(f'Invalid image position found for question "{quest}" on page "{page}".\n')
                elif structure[page][quest]["image_position"] == "free" and ("x_pos" not in structure[page][quest].keys() and "y_pos" not in structure[page][quest].keys()):
                    warning_found = True
                    warning_details.append(f'Image "{quest}" on page "{page}" is chosen to be positioned freely, but no coordinates were given.\n')
                    structure[page][quest]["x_pos"] = 0 if "x_pos" not in structure[page][quest].keys() else structure[page][quest]["x_pos"]
                    structure[page][quest]["y_pos"] = 0 if "y_pos" not in structure[page][quest].keys() else structure[page][quest]["y_pos"]
            elif "image_position" not in structure[page][quest].keys() and "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Image":
                error_found = True
                error_details.append(f'No image_position found for question "{quest}" on page "{page}".\n')

            if "width" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["width"])
                    if int(structure[page][quest]["width"]) <= 0:
                        error_found = True
                        error_details.append(f'Width needs to be bigger than 0 for question "{quest}" on page "{page}".\n')
                except ValueError:
                    error_found = True
                    error_details.append(f'Invalid value for width for question "{quest}" on page "{page}".\n')

            if "height" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["height"])
                    if int(structure[page][quest]["height"]) <= 0:
                        error_found = True
                        error_details.append(f'Height needs to be bigger than 0 for question "{quest}" on page "{page}".\n')
                except ValueError:
                    error_found = True
                    error_details.append(f'Height value for width for question "{quest}" on page "{page}".\n')

            if "x_pos" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["x_pos"])
                    if int(structure[page][quest]["x_pos"]) < 0:
                        error_found = True
                        error_details.append(f'X position needs to be bigger or equal to 0 for question "{quest}" on page "{page}".\n')
                except ValueError:
                    error_found = True
                    error_details.append(f'Invalid value for x position for question "{quest}" on page "{page}".\n')
            elif "image_position" in structure[page][quest].keys() and structure[page][quest]["image_position"] == "free":
                warning_found = True
                warning_details.append(f'No x position given for the question "{quest}" on page "{page}".\n')
                structure[page][quest]["x_pos"] = 0

            if "y_pos" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["y_pos"])
                    if int(structure[page][quest]["y_pos"]) < 0:
                        error_found = True
                        error_details.append(f'Y position needs to be bigger or equal to than 0 for question "{quest}" on page "{page}".\n')
                except ValueError:
                    error_found = True
                    error_details.append(f'Invalid value for y position for question "{quest}" on page "{page}".\n')
            elif "image_position" in structure[page][quest].keys() and structure[page][quest]["image_position"] == "free":
                warning_found = True
                warning_details.append(f'No y position given for the question "{quest}" on page "{page}".\n')
                structure[page][quest]["y_pos"] = 0

            if "address" in structure[page][quest].keys():
                if structure[page][quest]["address"] == "":
                    error_found = True
                    error_details.append(f'No OSC-address for question "{quest}" on page "{page}" was given.\n')
                elif not structure[page][quest]["address"].startswith("/"):
                    warning_found = True
                    warning_details.append(f'The OSC-address of question "{quest}" on page "{page}" should start with "/".\n')
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "OSCButton" and \
                    "address" not in structure[page][quest].keys():
                error_found = True
                error_details.append(f'No OSC-address for question "{quest}" on page "{page}" was given.\n')

            if "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "OSCButton" and \
                    "value" not in structure[page][quest].keys():
                error_found = True
                error_details.append(f'No value for question "{quest}" on page "{page}" was given.\n')

            if "receiver" in structure[page][quest].keys():
                if not isinstance(structure[page][quest]["receiver"], list) and not isinstance(structure[page][quest]["receiver"], tuple):
                    error_found = True
                    error_details.append(f'The receiver of question "{quest}" on page "{page}" needs to have the format (IP, Port).\n')
                elif len(structure[page][quest]["receiver"]) > 0:
                    match = re.match(ip_mask, structure[page][quest]["receiver"][0])
                    if match is None or match.span()[1] < len(structure[page][quest]["receiver"][0]):
                        error_found = True
                        error_details.append(f'No valid IP address given for the receiver in question "{quest}" on page "{page}".\n')
                    try:
                        int(structure[page][quest]["receiver"][1])
                        if int(structure[page][quest]["receiver"][1]) < 0 or int(structure[page][quest]["receiver"][1]) > 65535:
                            raise ValueError
                    except ValueError:
                        error_found = True
                        error_details.append(f'Invalid receiver port in question "{quest}" on page "{page}", could not be converted to a number 0-65535.\n')
                else:
                    error_found = True
                    error_details.append(f'The receiver of question "{quest}" on page "{page}" has not been given an IP and a port.\n')
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "OSCButton" and \
                    "receiver" not in structure[page][quest].keys():
                print("No OSC Receiver")
                error_found = True
                error_details.append(f'No receiver found for question "{quest}" on page "{page}".\n')

    # remove duplicate errors/warnings
    warning_details = list(dict.fromkeys(warning_details))
    error_details = list(dict.fromkeys(error_details))
    msg = ResizeMessageBox()
    msg.setWindowTitle("Validation Result")
    msg.setSizeGripEnabled(True)
    msg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    if not error_found and not warning_found and not suppress:
        msg.setIcon(QMessageBox.Information)
        msg.setText("The validation was successful and no errors were found.\n")
    elif warning_found and not error_found and not suppress:
        msg.setIcon(QMessageBox.Warning)
        msg.setText("The validation detected incomplete info.\n")
        warning_string = ""
        for warn in warning_details:
            warning_string += warn + "\n"
        msg.setDetailedText(warning_string)
    elif error_found:
        msg.setIcon(QMessageBox.Critical)
        msg.setText("The validation detected errors.\n")
        error_string = "------Errors:------\n"
        for error in error_details:
            error_string += error + "\n"
        if warning_found:
            error_string += "\n------Warnings:------\n"
            for warn in warning_details:
                error_string += warn + "\n"
        msg.setDetailedText(error_string)
    if not suppress or error_found:
        msg.exec()
    return error_found, warning_found, warning_details
