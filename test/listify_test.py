"""Test if the listify function in Validator.py is working correctly."""

from context import *


# fields: "answers", "button_texts", "header", "label", "questions"

def test_single_string_load():
    structure = ConfigObj("./test/listify.txt")
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['answers'] == 'answer'
    assert structure['Page 1']['Question 1']['button_texts'] == 'button'
    assert structure['Page 1']['Question 1']['header'] == 'head'
    assert structure['Page 1']['Question 1']['label'] == 'label'
    assert structure['Page 1']['Question 1']['questions'] == 'quest'


def test_single_string():
    structure = ConfigObj("./test/listify.txt")
    structure['Page 1']['Question 1']['answers'] = 'answer'
    structure['Page 1']['Question 1']['button_texts'] = 'button'
    structure['Page 1']['Question 1']['header'] = 'head'
    structure['Page 1']['Question 1']['label'] = 'label'
    structure['Page 1']['Question 1']['questions'] = 'quest'
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['answers'] == 'answer'
    assert structure['Page 1']['Question 1']['button_texts'] == 'button'
    assert structure['Page 1']['Question 1']['header'] == 'head'
    assert structure['Page 1']['Question 1']['label'] == 'label'
    assert structure['Page 1']['Question 1']['questions'] == 'quest'


def test_single_string_list():
    structure = ConfigObj("./test/listify.txt")
    structure['Page 1']['Question 1']['answers'] = '[answer]'
    structure['Page 1']['Question 1']['button_texts'] = '[button]'
    structure['Page 1']['Question 1']['header'] = '[head]'
    structure['Page 1']['Question 1']['label'] = '[label]'
    structure['Page 1']['Question 1']['questions'] = '[quest]'
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['answers'] == 'answer'
    assert structure['Page 1']['Question 1']['button_texts'] == 'button'
    assert structure['Page 1']['Question 1']['header'] == 'head'
    assert structure['Page 1']['Question 1']['label'] == ['label']
    assert structure['Page 1']['Question 1']['questions'] == 'quest'


def test_single_string_wanted_apostrophe():
    structure = ConfigObj("./test/listify.txt")
    structure['Page 1']['Question 1']['answers'] = "can't"
    structure['Page 1']['Question 1']['button_texts'] = "can't"
    structure['Page 1']['Question 1']['header'] = "can't"
    structure['Page 1']['Question 1']['label'] = "can't"
    structure['Page 1']['Question 1']['questions'] = "can't"
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['answers'] == "can't"
    assert structure['Page 1']['Question 1']['button_texts'] == "can't"
    assert structure['Page 1']['Question 1']['header'] == "can't"
    assert structure['Page 1']['Question 1']['label'] == "can't"
    assert structure['Page 1']['Question 1']['questions'] == "can't"


def test_single_string_wanted_apostrophe_list():
    structure = ConfigObj("./test/listify.txt")
    structure['Page 1']['Question 1']['answers'] = "[can't]"
    structure['Page 1']['Question 1']['button_texts'] = "[can't]"
    structure['Page 1']['Question 1']['header'] = "[can't]"
    structure['Page 1']['Question 1']['label'] = "[can't]"
    structure['Page 1']['Question 1']['questions'] = "[can't]"
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['answers'] == "can't"
    assert structure['Page 1']['Question 1']['button_texts'] == "can't"
    assert structure['Page 1']['Question 1']['header'] == "can't"
    assert structure['Page 1']['Question 1']['label'] == ["can't"]
    assert structure['Page 1']['Question 1']['questions'] == "can't"


def test_single_string_wanted_apostrophe_list_preformatted():
    structure = ConfigObj("./test/listify.txt")
    structure['Page 1']['Question 1']['answers'] = ["can't"]
    structure['Page 1']['Question 1']['button_texts'] = ["can't"]
    structure['Page 1']['Question 1']['header'] = ["can't"]
    structure['Page 1']['Question 1']['label'] = ["can't"]
    structure['Page 1']['Question 1']['questions'] = ["can't"]
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['answers'] == ["can't"]
    assert structure['Page 1']['Question 1']['button_texts'] == ["can't"]
    assert structure['Page 1']['Question 1']['header'] == ["can't"]
    assert structure['Page 1']['Question 1']['label'] == ["can't"]
    assert structure['Page 1']['Question 1']['questions'] == ["can't"]


def test_list_as_one_string():
    structure = ConfigObj("./test/listify.txt")
    structure['Page 1']['Question 1']['answers'] = '[answer1, answer2]'
    structure['Page 1']['Question 1']['button_texts'] = '[button1, button2]'
    structure['Page 1']['Question 1']['header'] = '[head1, head2]'
    structure['Page 1']['Question 1']['label'] = '[label1, label2]'
    structure['Page 1']['Question 1']['questions'] = '[quest1, quest2]'
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['answers'] == ['answer1', 'answer2']
    assert structure['Page 1']['Question 1']['button_texts'] == ['button1', 'button2']
    assert structure['Page 1']['Question 1']['header'] == ['head1', 'head2']
    assert structure['Page 1']['Question 1']['label'] == ['label1', 'label2']
    assert structure['Page 1']['Question 1']['questions'] == ['quest1', 'quest2']


def test_list_as_list_of_strings():
    structure = ConfigObj("./test/listify.txt")
    structure['Page 1']['Question 1']['answers'] = '["answer1", "answer2"]'
    structure['Page 1']['Question 1']['button_texts'] = '["button1", "button2"]'
    structure['Page 1']['Question 1']['header'] = '["head1", "head2"]'
    structure['Page 1']['Question 1']['label'] = '[1, "label2"]'
    structure['Page 1']['Question 1']['questions'] = '["quest1", "quest2"]'
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['answers'] == ['answer1', 'answer2']
    assert structure['Page 1']['Question 1']['button_texts'] == ['button1', 'button2']
    assert structure['Page 1']['Question 1']['header'] == ['head1', 'head2']
    assert structure['Page 1']['Question 1']['label'] == [[1.0, 'label2']] # sublist pairs with number as 0 entry
    assert structure['Page 1']['Question 1']['questions'] == ['quest1', 'quest2']


def test_list_as_list_of_strings_preformatted():
    structure = ConfigObj("./test/listify.txt")
    structure['Page 1']['Question 1']['answers'] = ["answer1", "answer2"]
    structure['Page 1']['Question 1']['button_texts'] = ["button1", "button2"]
    structure['Page 1']['Question 1']['header'] = ["head1", "head2"]
    structure['Page 1']['Question 1']['label'] = ["label1", "label2"]
    structure['Page 1']['Question 1']['questions'] = ["quest1", "quest2"]
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['answers'] == ['answer1', 'answer2']
    assert structure['Page 1']['Question 1']['button_texts'] == ['button1', 'button2']
    assert structure['Page 1']['Question 1']['header'] == ['head1', 'head2']
    assert structure['Page 1']['Question 1']['label'] == ['label1', 'label2']
    assert structure['Page 1']['Question 1']['questions'] == ['quest1', 'quest2']


def test_list_one_apostrophe():
    structure = ConfigObj("./test/listify.txt")
    structure['Page 1']['Question 1']['answers'] = "can't, answer"
    structure['Page 1']['Question 1']['button_texts'] = "can't, answer"
    structure['Page 1']['Question 1']['header'] = "can't, answer"
    structure['Page 1']['Question 1']['label'] = "can't, answer"
    structure['Page 1']['Question 1']['questions'] = "can't, answer"
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['answers'] == ["can't", "answer"]
    assert structure['Page 1']['Question 1']['button_texts'] == ["can't", "answer"]
    assert structure['Page 1']['Question 1']['header'] == ["can't", "answer"]
    assert structure['Page 1']['Question 1']['label'] == ["can't", "answer"]
    assert structure['Page 1']['Question 1']['questions'] == ["can't", "answer"]


def test_list_one_apostrophe_with_brackets():
    structure = ConfigObj("./test/listify.txt")
    structure['Page 1']['Question 1']['answers'] = "[can't, answer]"
    structure['Page 1']['Question 1']['button_texts'] = "[can't, answer]"
    structure['Page 1']['Question 1']['header'] = "[can't, answer]"
    structure['Page 1']['Question 1']['label'] = "[can't, answer]"
    structure['Page 1']['Question 1']['questions'] = "[can't, answer]"
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['answers'] == ["can't", "answer"]
    assert structure['Page 1']['Question 1']['button_texts'] == ["can't", "answer"]
    assert structure['Page 1']['Question 1']['header'] == ["can't", "answer"]
    assert structure['Page 1']['Question 1']['label'] == ["can't", "answer"]
    assert structure['Page 1']['Question 1']['questions'] == ["can't", "answer"]


def test_sublists():
    structure = ConfigObj("./test/listify.txt")
    structure['Page 1']['Question 1']['label'] = "[-1, -], [0, ~], [1,+]"
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['label'] == [[-1, '-'], [0, '~'], [1, '+']]
    structure['Page 1']['Question 1']['label'] = ["[-1, -]", "[0, ~]", "[1,+]"]
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['label'] == [[-1, '-'], [0, '~'], [1, '+']]
    structure['Page 1']['Question 1']['label'] = "[[-1, '-'], [0, '~'], [1,'+']]"
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['label'] == [[-1, '-'], [0, '~'], [1, '+']]
    structure['Page 1']['Question 1']['label'] = "[[-1, -], [0, ~], [1,+]]"
    structure = listify(structure)
    assert structure['Page 1']['Question 1']['label'] == [[-1, '-'], [0, '~'], [1, '+']]