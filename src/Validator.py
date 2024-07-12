"""Validation of questionnaire text files."""

import ast
import re
from os import path

from configobj import ConfigObj
from PySide6.QtGui import QIntValidator, QDoubleValidator, QRegularExpressionValidator
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
        if res[0] != 2:
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
                                                             type(structure[page][quest]["label"]) == list):
                sublist = False
                lblcpy = structure[page][quest]["label"]
                labels = []
                try:
                    if type(lblcpy) == str:
                        if lblcpy[0] == "[" and lblcpy[1] == "[" and lblcpy[-1] == "]" and lblcpy[-2] == "]":
                            lblcpy = lblcpy.strip(' "')[1:-1]
                        elif lblcpy.count("[") == 1 and lblcpy.count("]") == 1 and lblcpy.count(",") == 0:
                            lblcpy = lblcpy.strip(' []"')
                        lblcpy = lblcpy.split(",")
                    for t in range(0, len(lblcpy)):
                        if type(lblcpy[t]) == str:
                            if '[' in lblcpy[t]:  # t is list:
                                if ('[' in lblcpy[t]) and (']' not in lblcpy[t]):
                                    sublist = True
                                if ',' not in lblcpy[t]:
                                    labels.append([float(lblcpy[t].strip(" '][").strip('"'))])
                                else:
                                    if len(lblcpy[t].split(",")) == 2:
                                        entry = lblcpy[t].split(",")
                                        labels.append([float(entry[0].strip(" '[]").strip('"')), entry[1].strip(" '[]").strip('"')])
                                    else:
                                        labels[-1].append(float(entry.strip(" '[]").strip('"')))
                            elif sublist:
                                if ']' in lblcpy[t]:
                                    sublist = False
                                    labels[-1].append(lblcpy[t].strip(" ]['").strip('"'))
                                else:
                                    labels[-1].append(float(lblcpy[t]))
                            elif not sublist:
                                labels.append(lblcpy[t].strip(" '[]").strip('"'))
                        else:
                            if type(lblcpy[t]) == list or type(lblcpy[t]) == tuple:
                                if len(lblcpy[t]) == 2:
                                    labels.append([float(lblcpy[t][0]), lblcpy[t][1]])
                                else:
                                    labels[-1].append(lblcpy[t])
                    structure[page][quest]["label"] = labels
                except (ValueError, SyntaxError) as e:
                    if status is not None:
                        status.showMessage("Invalid value found in a 'label' field: {}".format(e), status_duration)

            if "track" in structure[page][quest].keys() and ("," in structure[page][quest]["track"] or
                                                             "[" in structure[page][quest]["track"] or
                                                             "]" in structure[page][quest]["track"] or
                                                             type(structure[page][quest]["track"]) == list):
                sublist = False
                trackscpy = structure[page][quest]["track"]
                tracks = []
                try:
                    if type(trackscpy) == str:
                        if trackscpy[0] == "[" and trackscpy[-1] == "]":
                            trackscpy = trackscpy.strip(" []")
                        trackscpy = trackscpy.split(",")
                    for t in range(0, len(trackscpy)):
                        if type(trackscpy[t]) == str:
                            if '[' in trackscpy[t]:  # t is list:
                                if ('[' in trackscpy[t]) and (']' not in trackscpy[t]):
                                    sublist = True
                                if ',' not in trackscpy[t]:
                                    tracks.append([int(trackscpy[t].strip(" ']["))])
                                else:
                                    tracks.append([])
                                    for entry in trackscpy[t].split(","):
                                        tracks[-1].append(int(entry.strip(" '[]")))
                            elif sublist:
                                if ']' in trackscpy[t]:
                                    sublist = False
                                    tracks[-1].append(int(trackscpy[t].strip(" ]['")))
                                else:
                                    tracks[-1].append(int(trackscpy[t]))
                            elif not sublist:
                                tracks.append(int(trackscpy[t].strip(" '")))
                        else:
                            if type(trackscpy[t]) == list:
                                tracks.append([])
                                for s in range(len(trackscpy[t])):
                                    tracks[-1].append(int(trackscpy[t][s]))
                            else:
                                tracks.append(trackscpy[t])
                    structure[page][quest]["track"] = tracks
                except (ValueError, SyntaxError) as e:
                    if status is not None:
                        status.showMessage("Invalid value found in a 'track' field: {}".format(e), status_duration)
            try:
                if "answers" in structure[page][quest].keys():
                    if "," in structure[page][quest]["answers"]:
                        structure[page][quest]["answers"] = ast.literal_eval(structure[page][quest]["answers"])
                    elif type(structure[page][quest]["answers"]) == str:
                        structure[page][quest]["answers"] = structure[page][quest]["answers"].strip("[] ")
                    else:  # list-like
                        for entry in range(len(structure[page][quest]["answers"])):
                            if type(entry) == str:
                                structure[page][quest]["answers"][entry] = structure[page][quest]["answers"][
                                    entry].strip("[] ")
                if "button_texts" in structure[page][quest].keys():
                    if "," in structure[page][quest]["button_texts"]:
                        structure[page][quest]["button_texts"] = ast.literal_eval(
                            structure[page][quest]["button_texts"])
                    elif type(structure[page][quest]["button_texts"]) == str:
                        structure[page][quest]["button_texts"] = structure[page][quest]["button_texts"].strip("[] ")
                    else:  # list-like
                        for entry in range(len(structure[page][quest]["button_texts"])):
                            structure[page][quest]["button_texts"][entry] = structure[page][quest]["button_texts"][
                                entry].strip("[] ")
                if "header" in structure[page][quest].keys():
                    if "," in structure[page][quest]["header"]:
                        structure[page][quest]["header"] = ast.literal_eval(structure[page][quest]["header"])
                    elif type(structure[page][quest]["header"]) == str:
                        structure[page][quest]["header"] = structure[page][quest]["header"].strip("[] ")
                    else:  # list-like
                        for entry in range(len(structure[page][quest]["header"])):
                            structure[page][quest]["header"][entry] = structure[page][quest]["header"][entry].strip(
                                "[] ")
                if "questions" in structure[page][quest].keys():
                    if "," in structure[page][quest]["questions"]:
                        structure[page][quest]["questions"] = ast.literal_eval(structure[page][quest]["questions"])
                    elif type(structure[page][quest]["questions"]) == str:
                        structure[page][quest]["questions"] = structure[page][quest]["questions"].strip("[] ")
                    else:  # list-like
                        for entry in range(len(structure[page][quest]["questions"])):
                            structure[page][quest]["questions"][entry] = structure[page][quest]["questions"][
                                entry].strip("[] ")
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


def validate_questionnaire(structure, suppress=False) -> (bool, bool, str):
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
                error_details.append("Invalid audio port, couldn't be converted to a number 0-65535.\n")
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
                error_details.append("Invalid audio receive port, couldn't be converted to a number 0-65535.\n")

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
                error_details.append("Invalid video port, couldn't be converted to a number 0-65535.\n")
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
                error_details.append("Invalid pupil port, couldn't be converted to a number 0-65535.\n")
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
                error_details.append("Invalid help port, couldn't be converted to a number 0-65535.\n")
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
                error_details.append("Invalid global_osc_send_port, couldn't be converted to a number 0-65535.\n")
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
                error_details.append("Invalid global_osc_recv_port, couldn't be converted to a number 0-65535.\n")
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

    if "send_text" in structure.keys() and "forward_text" in structure.keys() and structure["send_text"] == structure[
        "forward_text"]:
        warning_found = True
        warning_details.append("Text for forward and send button are the same.\n")

    if "answer_pos" in structure.keys() and "answer_neg" in structure.keys() and structure["answer_pos"] == structure[
        "answer_neg"]:
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
            warning_details.append("There are no questions on page {}.\n".format(page))

        if "pupil_on_next" in structure[page].keys():
            if structure[page]["pupil_on_next"] == '' or structure[page]["pupil_on_next"] == 'None':
                structure[page]["pupil_on_next"] = None
            if ("pupil_ip" not in structure.keys() or structure["pupil_ip"] == '') or \
                    ("pupil_port" not in structure.keys() or structure["pupil_port"] == ''):
                warning_found = True
                warning_details.append("Incomplete connection to pupil given. The connection to pupil will be disabled.\n")

        if "randomgroup" in structure[page].keys() and ("randomization" not in structure.keys() or \
            ("randomization" in structure.keys() and structure["randomization"] == "None")):
            error_found = True
            error_details.append("Using randomgroup, but no randomization option was chosen.\n")

        for quest in structure[page].sections:
            if structure[page][quest] == {}:
                warning_found = True
                warning_details.append("There are no attributes for question '{}' on page '{}'.\n".format(quest, page))

            if "id" in structure[page][quest].keys():
                if structure[page][quest]["id"] == "":
                    error_found = True
                    error_details.append("No ID was given for question '{}' on page '{}'.\n".format(quest, page))
                elif structure[page][quest]["id"] not in ids.keys():
                    ids[structure[page][quest]["id"]] = (page, quest)
                else:
                    error_found = True
                    error_details.append(
                        "ID '{}' already used in question '{}' on page '{}'. Found again in question '{}' on page '{}'.\n".format(
                            structure[page][quest]["id"], ids[structure[page][quest]["id"]][1],
                            ids[structure[page][quest]["id"]][0], quest, page))
            elif "id" not in structure[page][quest].keys() and "type" in structure[page][quest].keys() and \
                    "id" in fields_per_type[structure[page][quest]["type"]][0].keys():
                error_found = True
                error_details.append("No ID was given for question '{}' on page '{}'.\n".format(quest, page))

            if "x" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("x")
                except ValueError:
                    error_found = True
                    error_details.append(
                        "No valid value found for 'x' for question '{}' on page '{}'.\n".format(quest, page))
                    structure[page][quest][
                        "x"] = False  # This happens so the rest of the routine  where x is referenced doesn't have to catch errors
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX" and \
                    "x" not in structure[page][quest].keys():
                structure[page][quest]["x"] = False
                warning_found = True
                warning_details.append(
                    "No option for 'x' found for question '{}' on page '{}', using False as default value.\n".format(quest, page))

            if "play_once" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("play_once")
                except ValueError:
                    error_found = True
                    error_details.append(
                        "No valid value found for 'play_once' for question '{}' on page '{}'.\n".format(quest, page))
                    structure[page][quest]["play_once"] = False
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Player" and \
                    "play_once" not in structure[page][quest].keys():
                structure[page][quest]["play_once"] = False
                warning_found = True
                warning_details.append(
                    "No option for 'play_once' found for question '{}' on page '{}', using False by default.\n".format(
                        quest, page))

            if "required" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("required")
                except ValueError:
                    error_found = True
                    error_details.append(
                        "No valid value found for 'required' for question '{}' on page '{}'.\n".format(quest, page))
                    structure[page][quest]["required"] = False  # default value

            if "labelled" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("labelled")
                except ValueError:
                    error_found = True
                    error_details.append(
                        "No valid value found for 'labelled' for question '{}' on page '{}'.\n".format(quest, page))
                    structure[page][quest]["labelled"] = False  # default value
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Slider" and \
                    "labelled" not in structure[page][quest].keys():
                structure[page][quest]["labelled"] = False
                warning_found = True
                warning_details.append(
                    "No option for 'labelled' found for question '{}' on page '{}', setting it to False.\n".format(
                        quest, page))

            if "question_above" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("question_above")
                except ValueError:
                    error_found = True
                    error_details.append(
                        "No valid value found for 'question_above' for question '{}' on page '{}'.\n".format(quest,
                                                                                                             page))
                    structure[page][quest]["question_above"] = False  # default value

            if "text" in structure[page][quest].keys() and structure[page][quest]["text"] == "":
                warning_found = True
                warning_details.append("No text was given for question '{}' on page '{}'.\n".format(quest, page))
            elif "text" not in structure[page][quest].keys() and "type" in structure[page][quest].keys() and \
                    "text" in fields_per_type[structure[page][quest]["type"]][0].keys():
                structure[page][quest]["text"] = ""
                warning_found = True
                warning_details.append("No text was given for question '{}' on page '{}'.\n".format(quest, page))

            if "answers" in structure[page][quest].keys():
                if structure[page][quest]["answers"] == "" and ("type" not in structure[page][quest].keys() or
                                                                ("type" in structure[page][quest].keys() and not structure[page][quest]["type"] == "ABX")):
                    warning_found = True
                    warning_details.append(
                        "No answer possibilities were given for question '{}' on page '{}'.\n".format(quest, page))
                if "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX":
                    if ((type(structure[page][quest]["answers"]) != list and type(
                            structure[page][quest]["answers"]) != tuple) and structure[page][quest]["answers"] != "") or \
                            ((type(structure[page][quest]["answers"]) == list or type(
                                structure[page][quest]["answers"]) == tuple) and len(
                                structure[page][quest]["answers"]) != 2):
                        error_found = True
                        error_details.append(
                            "Please give two answer options for the ABX type question '{}' on page '{}' or leave this field empty.\n".format(
                                quest, page))
                elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "AFC":
                    if ((type(structure[page][quest]["answers"]) != list and type(
                            structure[page][quest]["answers"]) != tuple) and structure[page][quest]["answers"] != "") or \
                            ((type(structure[page][quest]["answers"]) == list or type(
                                structure[page][quest]["answers"]) == tuple) and len(
                                structure[page][quest]["answers"]) != structure[page][quest].as_int(
                                "number_of_choices")):
                        error_found = True
                        error_details.append(
                            "Please give as many answer options for the AFC type question '{}' as number_of_choices on page '{}' or leave this field empty.\n".format(
                                quest, page))
            elif "type" in structure[page][quest].keys() and \
                    (structure[page][quest]["type"] == "Radio" or structure[page][quest]["type"] == "Check" or
                     structure[page][quest]["type"] == "Matrix") and "answers" not in structure[page][quest].keys():
                structure[page][quest]["answers"] = ""
                warning_found = True
                warning_details.append(
                    "No answer possibilities were given for question '{}' on page '{}'.\n".format(quest, page))

            if "start_answer_id" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["start_answer_id"])
                    if int(structure[page][quest]["start_answer_id"]) < 0:
                        error_found = True
                        error_details.append(
                            "The start answer ID in question '{}' on page '{}' can't have a negative value.\n".format(
                                quest, page))
                except ValueError:
                    error_found = True
                    error_details.append(
                        "The start answer ID in question '{}' on page '{}' couldn't be interpreted as an integer.\n".format(
                            quest, page))

            if "min" in structure[page][quest].keys():
                if structure[page][quest]["min"] == "":
                    error_found = True
                    error_details.append(
                        "No minimum value was given for the slider in question '{}' on page '{}'.\n".format(quest,
                                                                                                            page))
                else:
                    try:
                        float(structure[page][quest]["min"])
                    except ValueError:
                        error_found = True
                        error_details.append(
                            "The minimum value found for the slider in question '{}' on page '{}' couldn't be interpreted as a number.\n".format(
                                quest, page))
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Slider" and \
                    "min" not in structure[page][quest].keys():
                error_found = True
                error_details.append(
                    "No minimum value was given for the slider in question '{}' on page '{}'.\n".format(quest, page))

            if "max" in structure[page][quest].keys():
                if structure[page][quest]["max"] == "":
                    error_found = True
                    error_details.append(
                        "No maximum value was given for the slider in question '{}' on page '{}'.\n".format(quest,
                                                                                                            page))
                else:
                    try:
                        float(structure[page][quest]["max"])
                    except ValueError:
                        error_found = True
                        error_details.append(
                            "The maximum value found for the slider in question '{}' on page '{}' couldn't be interpreted as a number.\n".format(
                                quest, page))
                try:
                    if "min" in structure[page][quest].keys() and round(float(structure[page][quest]["max"]) - float(structure[page][quest]["min"]), 3) == 0.0:
                        error_found = True
                        error_details.append(
                            "Maximum and Minimum value for the slider in question '{}' on page '{}' are the same.\n".format(
                                quest, page))
                except ValueError:
                    pass
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Slider" and \
                    "max" not in structure[page][quest].keys():
                error_found = True
                error_details.append(
                    "No maximum value was given for the slider in question '{}' on page '{}'.\n".format(quest, page))

            if "start" in structure[page][quest].keys():
                if structure[page][quest]["start"] == "":
                    error_found = True
                    error_details.append(
                        "No starting value was given for the slider in question '{}' on page '{}'.\n".format(quest,
                                                                                                             page))
                else:
                    try:
                        float(structure[page][quest]["start"])
                        if "min" in structure[page][quest].keys() and "max" in structure[page][quest].keys():
                            if float(structure[page][quest]["start"]) < float(structure[page][quest]["min"]) < float(structure[page][quest]["max"]) or \
                                    float(structure[page][quest]["start"]) > float(structure[page][quest]["min"]) > float(structure[page][quest]["max"]):
                                structure[page][quest]["start"] = float(structure[page][quest]["min"])
                            elif float(structure[page][quest]["start"]) > float(structure[page][quest]["max"]) < float(structure[page][quest]["min"]) or \
                                    float(structure[page][quest]["start"]) < float(structure[page][quest]["max"]) < float(structure[page][quest]["min"]):
                                structure[page][quest]["start"] = float(structure[page][quest]["max"])
                    except ValueError:
                        error_found = True
                        error_details.append(
                            "The starting value found for the slider in question '{}' on page '{}' couldn't be interpreted as a number.\n".format(
                                quest, page))
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Slider" and \
                    "start" not in structure[page][quest].keys():
                error_found = True
                error_details.append(
                    "No starting value was given for the slider in question '{}' on page '{}'.\n".format(quest, page))

            if "step" in structure[page][quest].keys():
                if structure[page][quest]["step"] == "":
                    error_found = True
                    error_details.append(
                        "No step value was given for the slider in question '{}' on page '{}'.\n".format(quest,
                                                                                                            page))
                else:
                    try:
                        if float(structure[page][quest]["step"]) <= 0:
                            error_found = True
                            error_details.append(
                                "The step value found for the slider in question '{}' on page '{}' needs to be bigger than 0.\n".format(
                                    quest, page))
                    except ValueError:
                        error_found = True
                        error_details.append(
                            "The step value found for the slider in question '{}' on page '{}' couldn't be interpreted as a number.\n".format(
                                quest, page))
                try:
                    if "min" in structure[page][quest].keys() and "max" in structure[page][quest].keys() \
                            and abs(float(structure[page][quest]["max"]) - float(structure[page][quest]["min"])) < float(structure[page][quest]["step"]):
                        error_found = True
                        error_details.append(
                            "The step value for the slider in question '{}' on page '{}' is bigger than the range.\n".format(
                                quest, page))
                except ValueError:
                    pass
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Slider" and \
                    "step" not in structure[page][quest].keys():
                error_found = True
                error_details.append(
                    "No step value was given for the slider in question '{}' on page '{}'.\n".format(quest, page))

            if "label" in structure[page][quest].keys() and "labelled" in structure[page][quest].keys() and \
                    structure[page][quest].as_bool("labelled"):
                if type(structure[page][quest]["label"][0]) != list and type(structure[page][quest]["label"][0]) != tuple:
                    if len(structure[page][quest]["label"]) != (float(structure[page][quest]["max"]) - float(
                            structure[page][quest]["min"])) / float(structure[page][quest]["step"]) + 1:
                        error_found = True
                        error_details.append(
                            "The number of given labels doesn't match the number of ticks for question '{}' on page '{}'.\n".format(
                                quest, page))
                elif len(structure[page][quest]["label"][0]) != 2:
                    error_found = True
                    error_details.append("No valid format for labels for question '{}' on page '{}'.\n".format(quest, page))
                else:  # list / tuple of single pairs
                    tick = []
                    try:
                        for pair in structure[page][quest]["label"]:
                            tick.append(float(pair[0]))
                            if not (float(structure[page][quest]["max"]) <= float(pair[0]) <= float(structure[page][quest]["min"]) or
                                    float(structure[page][quest]["max"]) >= float(pair[0]) >= float(structure[page][quest]["min"])):
                                error_found = True
                                error_details.append("Tick value outside of slider range found for question '{}' on page '{}'.\n".format(quest, page))
                        if len(tick) != len(set(tick)):
                            error_found = True
                            error_details.append("Double definition of tick labels found for question '{}' on page '{}'.\n".format(quest, page))
                    except ValueError:
                        error_found = True
                        error_details.append(
                            "A label tick for the slider in question '{}' on page '{}' couldn't be interpreted as a number.\n".format(
                                quest, page))

            if "policy" in structure[page][quest].keys():
                if structure[page][quest]["policy"] == "None" or structure[page][quest]["policy"] == "[None]":
                    structure[page][quest]["policy"] = ["None"]
                if (type(structure[page][quest]["policy"]) == str and structure[page][quest]["policy"] not in policy_possibilities) or \
                        (type(structure[page][quest]["policy"]) == list and structure[page][quest]["policy"][0] not in policy_possibilities):
                    error_found = True
                    error_details.append("Invalid policy type in question '{}' on page '{}'.\n".format(quest, page))
                if (type(structure[page][quest]["policy"]) == str and structure[page][quest]["policy"] == "int") or \
                        (type(structure[page][quest]["policy"]) == list and structure[page][quest]["policy"][0] == 'int' and len(structure[page][quest]["policy"]) != 3):
                    error_found = True
                    error_details.append("Policy type 'int' takes two arguments, a different amount was given in question '{}' on page '{}'.\n".format(quest, page))
                elif (type(structure[page][quest]["policy"]) == str and structure[page][quest]["policy"] == "double") or \
                        (type(structure[page][quest]["policy"]) == list and structure[page][quest]["policy"][0] == 'double' and len(structure[page][quest]["policy"]) != 4):
                    error_found = True
                    error_details.append("Policy type 'double' takes three arguments, a different amount was given in question '{}' on page '{}'.\n".format(quest, page))
                elif (type(structure[page][quest]["policy"]) == str and structure[page][quest]["policy"] == "regex") or \
                        (type(structure[page][quest]["policy"]) == list and structure[page][quest]["policy"][0] == 'regex' and len(structure[page][quest]["policy"]) != 2):
                    error_found = True
                    error_details.append("Policy type 'regex' takes one argument, a different amount was given in question '{}' on page '{}'.\n".format(quest, page))

                if (structure[page][quest]["policy"][0] == "int") or (structure[page][quest]["policy"][0] == "double"):
                    if structure[page][quest]["policy"][1] == "":
                        error_found = True
                        error_details.append(
                            "No minimum value was given for the policy in question '{}' on page '{}'.\n".format(quest,
                                                                                                                page))
                    else:
                        try:
                            if structure[page][quest]["policy"][0] == "int":
                                int(structure[page][quest]["policy"][1])
                            else:
                                float(structure[page][quest]["policy"][1])
                        except ValueError:
                            error_found = True
                            error_details.append(
                                "Minimum value given for the policy in question '{}' on page '{}' couldn't be converted to a valid number.\n".format(
                                    quest, page))
                    if structure[page][quest]["policy"][2] == "":
                        error_found = True
                        error_details.append(
                            "No maximum value was given for the policy in question '{}' on page '{}'.\n".format(quest,
                                                                                                                page))
                    else:
                        try:
                            if structure[page][quest]["policy"][0] == "int":
                                int(structure[page][quest]["policy"][2])
                            else:
                                float(structure[page][quest]["policy"][2])
                        except ValueError:
                            error_found = True
                            error_details.append(
                                "Maximum value given for the policy in question '{}' on page '{}' couldn't be converted to a valid number.\n".format(
                                    quest, page))
                if structure[page][quest]["policy"][0] == "double":
                    if structure[page][quest]["policy"][3] == "":
                        error_found = True
                        error_details.append(
                            "No number of decimals was given for the policy in question '{}' on page '{}'.\n".format(
                                quest, page))
                    else:
                        try:
                            int(structure[page][quest]["policy"][3])
                        except ValueError:
                            error_found = True
                            error_details.append(
                                "Number of decimals given for the policy in question '{}' on page '{}' couldn't be converted to a number.\n".format(
                                    quest, page))
                if structure[page][quest]["policy"][0] == "regex":
                    if structure[page][quest]["policy"][1] == "":
                        error_found = True
                        error_details.append(
                            "No regex was given for the policy in question '{}' on page '{}'.\n".format(quest, page))
                    else:
                        try:
                            re.compile(str(structure[page][quest]["policy"][1]))
                        except re.error:
                            error_found = True
                            error_details.append(
                                "An invalid regex was given for the policy in question '{}' on page '{}'.\n".format(
                                    quest, page))

            if "start_cue" in structure[page][quest].keys():
                if structure[page][quest]["start_cue"] == "":
                    error_found = True
                    error_details.append(
                        "No start cue was given in question '{}' on page '{}'.\n".format(quest, page))
                else:
                    try:
                        int(structure[page][quest]["start_cue"])
                    except (ValueError, TypeError):
                        error_found = True
                        error_details.append(
                            "Start cue given in question '{}' on page '{}' couldn't be converted to a number.\n".format(
                                quest, page))
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Player" \
                    and "start_cue" not in structure[page][quest].keys():
                error_found = True
                error_details.append(
                    "No start cue was given in question '{}' on page '{}'.\n".format(quest, page))

            if "end_cue" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["end_cue"])
                    if "start_cue" in structure[page][quest].keys() and structure[page][quest]["start_cue"] == structure[page][quest]["end_cue"]:
                        error_found = True
                        error_details.append(
                            "The same cue ({}) was used as start- and end-cue for one condition in question '{}' on page '{}'.\n".format(
                                structure[page][quest]["start_cue"], quest, page))
                except (ValueError, TypeError):
                    error_found = True
                    error_details.append(
                        "End cue given in question '{}' on page '{}' couldn't be converted to a number.\n".format(
                            quest, page))

            if "track" in structure[page][quest].keys():
                if structure[page][quest]["track"] == "":
                    error_found = True
                    error_details.append(
                        "No track(s) was given for question '{}' on page '{}'.\n".format(quest, page))
                else:
                    try:
                        if type(structure[page][quest]["track"]) == list or \
                                type(structure[page][quest]["track"]) == tuple:
                            if "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX" and (
                                    len(structure[page][quest]["track"]) > 2 or len(structure[page][quest]["track"]) < 1):
                                error_found = True
                                error_details.append(
                                    "There should be 1 or 2 tracks for AB(X)-tests, but {} were given in question '{}' on page '{}'.\n".format(
                                        len(structure[page][quest]["track"]), quest, page))
                            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "MUSHRA" and \
                                    len(structure[page][quest]["track"]) != len(structure[page][quest]["start_cues"]) and \
                                    len(structure[page][quest]["track"]) > 1:
                                error_found = True
                                error_details.append(
                                    "The number of tracks given doesn't equal the number of cues given in question '{}' on page '{}'.\n".format(
                                        quest, page))

                            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX" and len(structure[page][quest]["track"]) == 1:
                                structure[page][quest]["track"].append(structure[page][quest]["track"][0])
                            for entry in range(len(structure[page][quest]["track"])):
                                if type(structure[page][quest]["track"][entry]) == str:
                                    if type(structure[page][quest]["track"]) == tuple:
                                        structure[page][quest]["track"] = list(structure[page][quest]["track"])
                                    structure[page][quest]["track"][entry] = structure[page][quest]["track"][
                                        entry].strip("' \"")
                                    int(structure[page][quest]["track"][entry])
                                    if int(structure[page][quest]["track"][entry]) < 1:
                                        error_found = True
                                        error_details.append(
                                            "Tracks given for question '{}' on page '{}' needs to be greater than 0.\n".format(
                                                quest, page))
                                elif type(structure[page][quest]["track"][entry]) == list:
                                    if "type" in structure[page][quest].keys() and structure[page][quest]["type"] != "MUSHRA":
                                        error_found = True
                                        error_details.append("Tracks given for question '{}' on page '{}' need to be one or more integers, not lists.\n".format(
                                                quest, page))
                                    for entry2 in range(len(structure[page][quest]["track"][entry])):
                                        if type(structure[page][quest]["track"][entry][entry2]) != int:
                                            structure[page][quest]["track"][entry][entry2] = \
                                                structure[page][quest]["track"][entry][entry2].strip("' \"")
                                        int(structure[page][quest]["track"][entry][entry2])
                                        if int(structure[page][quest]["track"][entry][entry2]) < 1:
                                            error_found = True
                                            error_details.append(
                                                "Tracks given for question '{}' on page '{}' needs to be greater than 0.\n".format(
                                                    quest, page))
                                else:  # int
                                    if structure[page][quest]["track"][entry] < 1:
                                        error_found = True
                                        error_details.append(
                                            "Track given for question '{}' on page '{}' needs to be greater than 0.\n".format(
                                                quest, page))
                        else:
                            int(structure[page][quest]["track"])

                            if int(structure[page][quest]["track"]) < 1:
                                error_found = True
                                error_details.append(
                                    "Track given for question '{}' on page '{}' needs to be greater than 0.\n".format(
                                        quest, page))
                            if "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX":
                                structure[page][quest]["track"] = [structure[page][quest]["track"],
                                                                   structure[page][quest]["track"]]
                    except ValueError:
                        error_found = True
                        error_details.append(
                            "Track(s) given for question '{}' on page '{}' couldn't be converted to a number or list of numbers.\n".format(
                                quest, page))
            elif "type" in structure[page][quest].keys() and \
                    (structure[page][quest]["type"] == "Player" or structure[page][quest]["type"] == "MUSHRA" or
                     structure[page][quest]["type"] == "ABX" or structure[page][quest]["type"] == "AFC") \
                    and "track" not in structure[page][quest].keys():
                error_found = True
                error_details.append(
                    "No track(s) was given for question '{}' on page '{}'.\n".format(quest, page))

            if "buttons" in structure[page][quest].keys():
                if len(structure[page][quest]["buttons"]) == 0:
                    warning_found = True
                    warning_details.append(
                        "No buttons are displayed for the player in question '{}' on page '{}'. It will play when this page is loaded.\n".format(
                            quest, page))
                else:
                    try:
                        if type(structure[page][quest]["buttons"]) is list or type(
                                structure[page][quest]["buttons"]) is tuple:
                            for button in structure[page][quest]["buttons"]:
                                if button not in player_buttons:
                                    raise ValueError
                            if "Play" not in structure[page][quest]["buttons"]:
                                warning_found = True
                                warning_details.append(
                                    "No Play button is displayed for the player in question '{}' on page '{}'. It will play when this page is loaded.\n".format(
                                        quest, page))
                        elif type(structure[page][quest]["buttons"]) is str:
                            if structure[page][quest]["buttons"] not in player_buttons:
                                raise ValueError
                            elif "Play" != structure[page][quest]["buttons"]:
                                warning_found = True
                                warning_details.append(
                                    "No Play button is displayed for the player in question '{}' on page '{}'. It will play when this page is loaded.\n".format(
                                        quest, page))
                        else:
                            raise ValueError
                    except ValueError:
                        error_found = True
                        error_details.append(
                            "Invalid value found for 'buttons' for question '{}' on page '{}'.\n".format(quest, page))
            elif "type" in structure[page][quest].keys() and structure[page][quest][
                "type"] == "Player" and "buttons" not in structure[page][quest].keys():
                warning_found = True
                warning_details.append(
                    "No buttons are displayed for the player in question '{}' on page '{}'. It will play when this page is loaded.\n".format(
                        quest, page))

            if "start_cues" in structure[page][quest].keys():
                if structure[page][quest]["start_cues"] == "":
                    error_found = True
                    error_details.append(
                        "No start cues were given for question '{}' on page '{}'.\n".format(quest, page))
                else:
                    try:
                        if type(structure[page][quest]["start_cues"]) == list or \
                                type(structure[page][quest]["start_cues"]) == tuple:
                            for entry in range(len(structure[page][quest]["start_cues"])):
                                if type(structure[page][quest]["start_cues"][entry]) == str:
                                    if type(structure[page][quest]["start_cues"]) == tuple:
                                        structure[page][quest]["start_cues"] = list(structure[page][quest]["start_cues"])
                                    structure[page][quest]["start_cues"][entry] = structure[page][quest]["start_cues"][entry].strip("' \"")
                                    int(structure[page][quest]["start_cues"][entry])
                            if "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "ABX" and (len(structure[page][quest]["start_cues"]) != 2):
                                error_found = True
                                error_details.append(
                                    "There should be exactly 2 start_cues for AB(X)-tests, but {} were given in question '{}' on page '{}'.\n".format(
                                        1 if type(structure[page][quest]["start_cues"]) == int else len(
                                            structure[page][quest]["start_cues"]), quest, page))
                        else:
                            int(structure[page][quest]["start_cues"])
                            if structure[page][quest]["type"] == "ABX":
                                error_found = True
                                error_details.append(
                                    "There should be exactly 2 start_cues for AB(X)-tests, but {} were given in question '{}' on page '{}'.\n".format(
                                        1 if type(structure[page][quest]["start_cues"]) == int else len(
                                            structure[page][quest]["start_cues"]), quest, page))
                    except ValueError:
                        error_found = True
                        error_details.append(
                            "Start cues given for question '{}' on page '{}' couldn't be converted to a list of numbers.\n".format(
                                quest, page))
            elif "type" in structure[page][quest].keys() and (structure[page][quest]["type"] == "MUSHRA" or
                                                              structure[page][quest]["type"] == "ABX" or
                                                              structure[page][quest]["type"] == "AFC") \
                    and "start_cues" not in structure[page][quest].keys():
                error_found = True
                error_details.append("No start cues were given for question '{}' on page '{}'.\n".format(quest, page))

            if "end_cues" in structure[page][quest].keys():
                if structure[page][quest]["end_cues"] == "":
                    error_found = True
                    error_details.append("No end cues were given for question '{}' on page '{}'.\n".format(quest, page))
                else:
                    try:
                        if type(structure[page][quest]["end_cues"]) == list or type(
                                structure[page][quest]["end_cues"]) == tuple:
                            for entry in range(len(structure[page][quest]["end_cues"])):
                                if type(structure[page][quest]["end_cues"][entry]) == str:
                                    if type(structure[page][quest]["end_cues"]) == tuple:
                                        structure[page][quest]["end_cues"] = list(structure[page][quest]["end_cues"])
                                    structure[page][quest]["end_cues"][entry] = structure[page][quest]["end_cues"][
                                        entry].strip("' \"")
                                    int(structure[page][quest]["end_cues"][entry])
                        else:
                            int(structure[page][quest]["end_cues"])
                    except ValueError:
                        error_found = True
                        error_details.append(
                            "End cues given for question '{}' on page '{}' couldn't be converted to a list of numbers.\n".format(
                                quest, page))
                    if "start_cues" not in structure[page][quest].keys() or \
                            len(structure[page][quest]["end_cues"]) != len(structure[page][quest]["start_cues"]):
                        error_found = True
                        error_details.append(
                            "The number of start- and end-cues in question '{}' on page '{}' doesn't match.\n".format(
                                quest, page))
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "MUSHRA" \
                    and "end_cues" not in structure[page][quest].keys():
                error_found = True
                error_details.append(
                    "No end cues were given for question '{}' on page '{}'.\n".format(quest, page))

            if "start_cues" in structure[page][quest].keys() and "end_cues" in structure[page][quest].keys():
                if (type(structure[page][quest]["end_cues"]) == list or type(
                        structure[page][quest]["end_cues"]) == tuple) and (
                        type(structure[page][quest]["start_cues"]) == list or
                        type(structure[page][quest]["start_cues"]) == tuple) and (
                        len(structure[page][quest]["start_cues"]) == len(structure[page][quest]["end_cues"])):
                    for entry in range(len(structure[page][quest]["start_cues"])):
                        if int(structure[page][quest]["start_cues"][entry]) == int(
                                structure[page][quest]["end_cues"][entry]):
                            error_found = True
                            error_details.append(
                                "The same cue ({}) was used as start- and end-cue for one condition in question '{}' on page '{}'.\n".format(
                                    structure[page][quest]["start_cues"][entry], quest, page))

            if "xfade" in structure[page][quest].keys():
                try:
                    if structure[page][quest].as_bool("xfade"):
                        all_same_marker = True
                        for sc in structure[page][quest]["start_cues"]:
                            if int(sc) != int(structure[page][quest]["start_cues"][0]):
                                all_same_marker = False
                        for ec in structure[page][quest]["end_cues"]:
                            if int(ec) != int(structure[page][quest]["end_cues"][0]):
                                all_same_marker = False
                        if not all_same_marker:
                            error_found = True
                            error_details.append(
                                "Xfade is only applicable if all start- and end-markers are the same each in question '{}' on page '{}'.\n".format(
                                    quest, page))
                        if (type(structure[page][quest]["track"]) == int or type(structure[page][quest]["track"]) == str) or \
                                ((type(structure[page][quest]["track"]) == list or type(structure[page][quest]["track"]) == tuple) and \
                                 (type(structure[page][quest]["track"][0]) == list and len(set(structure[page][quest]["track"][0])) == 1 or len(set(structure[page][quest]["track"])) == 1)):
                            error_found = True
                            error_details.append(
                                "For xfade stimuli need to be placed on different tracks in question '{}' on page '{}'.\n".format(
                                    quest, page))
                except ValueError:
                    error_found = True
                    error_details.append(
                        "No valid value found for 'xfade' for question '{}' on page '{}'.\n".format(quest, page))
                    structure[page][quest][
                        "xfade"] = False  # This happens so the rest of the routine where xfade is referenced doesn't have to catch errors

            if "crossfade" in structure[page][quest].keys():
                try:
                    structure[page][quest].as_bool("crossfade")
                except ValueError:
                    error_found = True
                    error_details.append(
                        "No valid value found for 'crossfade' for question '{}' on page '{}'.\n".format(quest, page))
                    structure[page][quest]["crossfade"] = False  # This happens so the rest of the routine where crossfade is referenced doesn't have to catch errors

            if "inscription" in structure[page][quest].keys():
                if structure[page][quest]["inscription"] == "":
                    warning_found = True
                    warning_details.append(
                        "No inscription for the button in question '{}' on page '{}'.\n".format(quest, page))
                elif structure[page][quest]["inscription"] == "None":
                    warning_found = True
                    warning_details.append(
                        "Internally used inscription 'None' used in question '{}' on page '{}'.\n".format(quest, page))
            elif "type" in structure[page][quest].keys() and (structure[page][quest]["type"] == "Button"
                                                              or structure[page][quest]["type"] == "OSCButton") and \
                    "inscription" not in structure[page][quest].keys():
                structure[page][quest]["inscription"] = ""
                warning_found = True
                warning_details.append(
                    "No inscription for the button in question '{}' on page '{}'.\n".format(quest, page))

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
                    warning_details.append(
                        "This questionnaire uses MUSHRA, but no valid address for an audio-application is set.\n")
                if (structure[page][quest]["type"] == "Player" or structure[page][quest]["type"] == "ABX" or
                    structure[page][quest]["type"] == "AFC") and \
                        ("audio_ip" not in structure.keys() or "audio_port" not in structure.keys() or
                         structure["audio_ip"] == "" or structure["audio_port"] == ""):
                    warning_found = True
                    warning_details.append(
                        "This questionnaire uses an audio player, but no valid address for an audio-application is set.\n")
                if structure[page][quest]["type"] == "Player" and "video" in structure[page][quest].keys() \
                        and ("video_ip" not in structure.keys() or "video_port" not in structure.keys() or
                             structure["video_ip"] == "" or structure["video_port"] == ""):
                    warning_found = True
                    warning_details.append(
                        "This questionnaire uses a video in question '{}' on page '{}', but no valid address for a video-application is set.\n".format(
                            quest, page))
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
                    warning_details.append(
                        "The objectName in question '{}' on page '{}' uses a predefined name.\n".format(quest, page))

            if "timer" in structure[page][quest].keys() and structure[page][quest]["timer"] != "":
                try:
                    if int(structure[page][quest]["timer"]) < 0:
                        warning_found = True
                        warning_details.append(
                            "The timer in question '{}' on page '{}' needs to be greater than or equal to 0. Setting it to 0 by default.\n".format(quest, page))
                        structure[page][quest]["timer"] = 0
                except ValueError:
                    error_found = True
                    error_details.append(
                        "The timer in question '{}' on page '{}' needs to be a numeric value.\n".format(quest, page))

            if "password_file" in structure[page][quest].keys():
                if structure[page][quest]["password_file"] == "":
                    warning_found = True
                    warning_details.append(
                        "No password_file found for question '{}' on page '{}'.\n".format(quest, page))
                elif not path.isfile(structure[page][quest]["password_file"]):
                    error_found = True
                    error_details.append(
                        "No valid password_file for question '{}' on page '{}'.\n".format(quest, page))
                elif not validate_passwords(structure[page][quest]["password_file"], structure[page][quest]["policy"]):
                    warning_found = True
                    warning_details.append(
                        "Passwords in file do not match policy of field for question '{}' on page '{}'.\n".format(quest,
                                                                                                                  page))
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Password" and \
                    "password_file" not in structure[page][quest].keys():
                structure[page][quest]["password_file"] = ""
                warning_found = True
                warning_details.append(
                    "No password_file found for question '{}' on page '{}'.\n".format(quest, page))

            if "button_texts" in structure[page][quest].keys():
                if ((type(structure[page][quest]["button_texts"]) != list and type(
                        structure[page][quest]["button_texts"]) != tuple) and structure[page][quest][
                        "button_texts"] != "") or \
                        ((type(structure[page][quest]["button_texts"]) == list or type(
                            structure[page][quest]["button_texts"]) == tuple) and
                         ((len(structure[page][quest]["button_texts"]) != 2 and structure[page][quest].as_bool(
                             "x") == False) or
                          (len(structure[page][quest]["button_texts"]) != 3 and structure[page][quest].as_bool(
                              "x") == True))):
                    error_found = True
                    error_details.append(
                        "Please give no, two or three (if option X is used) button_texts for the ABX type question '{}' on page '{}'.\n".format(
                            quest, page))

            if "randomize" in structure[page][quest].keys():
                try:
                    _ = structure[page][quest].as_bool("randomize")
                except ValueError:
                    error_found = True
                    error_details.append(
                        "No valid value found for 'randomize' for question '{}' on page '{}'.\n".format(quest, page))
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Matrix" and \
                    "randomize" not in structure[page][quest].keys():
                structure[page][quest]["randomize"] = False
                warning_found = True
                warning_details.append(
                    "No option for 'randomize' found for question '{}' on page '{}'.\n".format(quest, page))

            if "questions" in structure[page][quest].keys():
                if structure[page][quest]["questions"] == "" or len(structure[page][quest]["questions"]) == 0:
                    warning_found = True
                    warning_details.append(
                        "No questions for the matrix in question '{}' on page '{}' found.\n".format(quest, page))
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Matrix" and \
                    "questions" not in structure[page][quest].keys():
                structure[page][quest]["questions"] = ""
                warning_found = True
                warning_details.append(
                    "No questions for the matrix in question '{}' on page '{}' found.\n".format(quest, page))

            if "image_file" in structure[page][quest].keys():
                if structure[page][quest]["image_file"] == "":
                    warning_found = True
                    warning_details.append(
                        "No image_file found for question '{}' on page '{}'.\n".format(quest, page))
                elif not path.isfile(structure[page][quest]["image_file"]):
                    error_found = True
                    error_details.append(
                        "No valid image_file for question '{}' on page '{}'.\n".format(quest, page))
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Image" and \
                    "image_file" not in structure[page][quest].keys():
                structure[page][quest]["image_file"] = ""
                warning_found = True
                warning_details.append(
                    "No image_file found for question '{}' on page '{}'.\n".format(quest, page))

            if "image_position" in structure[page][quest].keys():
                if structure[page][quest]["image_position"] not in image_positions:
                    error_found = True
                    error_details.append("Invalid image position found for question '{}' on page '{}'.\n".format(quest, page))
                elif structure[page][quest]["image_position"] == "free" and ("x_pos" not in structure[page][quest].keys() and "y_pos" not in structure[page][quest].keys()):
                    warning_found = True
                    warning_details.append("Image '{}' on page '{}' is chosen to be positioned freely, but no coordinates were given.\n".format(quest, page))
                    structure[page][quest]["x_pos"] = 0 if "x_pos" not in structure[page][quest].keys() else structure[page][quest]["x_pos"]
                    structure[page][quest]["y_pos"] = 0 if "y_pos" not in structure[page][quest].keys() else structure[page][quest]["y_pos"]
            elif "image_position" not in structure[page][quest].keys() and "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "Image":
                error_found = True
                error_details.append("No image_position found for question '{}' on page '{}'.\n".format(quest, page))

            if "width" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["width"])
                    if int(structure[page][quest]["width"]) <= 0:
                        error_found = True
                        error_details.append("Width needs to be bigger than 0 for question '{}' on page '{}'.\n".format(quest, page))
                except ValueError:
                    error_found = True
                    error_details.append("Invalid value for width for question '{}' on page '{}'.\n".format(quest, page))

            if "height" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["height"])
                    if int(structure[page][quest]["height"]) <= 0:
                        error_found = True
                        error_details.append("Height needs to be bigger than 0 for question '{}' on page '{}'.\n".format(quest, page))
                except ValueError:
                    error_found = True
                    error_details.append("Height value for width for question '{}' on page '{}'.\n".format(quest, page))

            if "x_pos" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["x_pos"])
                    if int(structure[page][quest]["x_pos"]) < 0:
                        error_found = True
                        error_details.append("X position needs to be bigger or equal to 0 for question '{}' on page '{}'.\n".format(quest, page))
                except ValueError:
                    error_found = True
                    error_details.append("Invalid value for x position for question '{}' on page '{}'.\n".format(quest, page))
            elif "image_position" in structure[page][quest].keys() and structure[page][quest]["image_position"] == "free":
                warning_found = True
                warning_details.append("No x position given for the question '{}' on page '{}'.\n".format(quest, page))
                structure[page][quest]["x_pos"] = 0

            if "y_pos" in structure[page][quest].keys():
                try:
                    int(structure[page][quest]["y_pos"])
                    if int(structure[page][quest]["y_pos"]) < 0:
                        error_found = True
                        error_details.append("Y position needs to be bigger or equal to than 0 for question '{}' on page '{}'.\n".format(quest, page))
                except ValueError:
                    error_found = True
                    error_details.append("Invalid value for y position for question '{}' on page '{}'.\n".format(quest, page))
            elif "image_position" in structure[page][quest].keys() and structure[page][quest]["image_position"] == "free":
                warning_found = True
                warning_details.append("No y position given for the question '{}' on page '{}'.\n".format(quest, page))
                structure[page][quest]["y_pos"] = 0

            if "address" in structure[page][quest].keys():
                if structure[page][quest]["address"] == "":
                    error_found = True
                    error_details.append(
                        "No OSC-address for question '{}' on page '{}' was given.\n".format(quest, page))
                elif not structure[page][quest]["address"].startswith("/"):
                    warning_found = True
                    warning_details.append("The OSC-address of question '{}' on page '{}' should start with '/'.\n".format(quest, page))
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "OSCButton" and \
                    "address" not in structure[page][quest].keys():
                error_found = True
                error_details.append("No OSC-address for question '{}' on page '{}' was given.\n".format(quest, page))

            if "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "OSCButton" and \
                    "value" not in structure[page][quest].keys():
                error_found = True
                error_details.append("No value for question '{}' on page '{}' was given.\n".format(quest, page))

            if "receiver" in structure[page][quest].keys():
                if type(structure[page][quest]["receiver"]) is not list and type(structure[page][quest]["receiver"]) is not tuple:
                    error_found = True
                    error_details.append("The receiver of question '{}' on page '{}' needs to have the format (IP, Port).\n".format(quest, page))
                elif len(structure[page][quest]["receiver"]) > 0:
                    match = re.match(ip_mask, structure[page][quest]["receiver"][0])
                    if match is None or match.span()[1] < len(structure[page][quest]["receiver"][0]):
                        error_found = True
                        error_details.append("No valid IP address given for the receiver in question '{}' on page '{}'.\n".format(quest, page))
                    try:
                        int(structure[page][quest]["receiver"][1])
                        if int(structure[page][quest]["receiver"][1]) < 0 or int(structure[page][quest]["receiver"][1]) > 65535:
                            raise ValueError
                    except ValueError:
                        error_found = True
                        error_details.append("Invalid receiver port in question '{}' on page '{}', couldn't be converted to a number 0-65535.\n".format(quest, page))
            elif "type" in structure[page][quest].keys() and structure[page][quest]["type"] == "OSCButton" and \
                    "receiver" not in structure[page][quest].keys():
                error_found = True
                error_details.append("No receiver found for question '{}' on page '{}'.\n".format(quest, page))

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
