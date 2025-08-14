"""Test if the string_to_list function in Validator.py is working correctly."""

from tests.context import string_to_list


def test_single_string():
    assert string_to_list("one") == ["one"]
    assert string_to_list('one') == ['one']
    assert string_to_list("[one]") == ["one"]
    assert string_to_list('[one]') == ['one']
    assert string_to_list("can't") == ["can't"]
    assert string_to_list("[can't]") == ["can't"]


def test_two_strings():
    assert string_to_list("one, two") == ["one", "two"]
    assert string_to_list('one, two') == ['one', 'two']
    assert string_to_list('["one", "two"]') == ["one", "two"]
    assert string_to_list("['one', 'two']") == ['one', 'two']
    assert string_to_list('["one", two]') == ["one", "two"]
    assert string_to_list("['one', two]") == ['one', 'two']
    assert string_to_list('[one, "two"]') == ["one", "two"]
    assert string_to_list("[one, 'two']") == ['one', 'two']
    assert string_to_list("one,two") == ["one", "two"]
    assert string_to_list('one,two') == ['one', 'two']
    assert string_to_list('["one","two"]') == ["one", "two"]
    assert string_to_list("['one','two']") == ['one', 'two']


def test_apostrophe():
    assert string_to_list("one, can't") == ['one', "can't"]
    assert string_to_list("[one, can't]") == ['one', "can't"]
    assert string_to_list("['one', can't]") == ['one', "can't"]
    assert string_to_list("can't, one") == ["can't", 'one']
    assert string_to_list("[can't, one]") == ["can't", 'one']
    assert string_to_list("[can't, 'one']") == ["can't", 'one']
    assert string_to_list("can't, that's, don't, ones'") == ["can't", "that's", "don't", "ones'"]
    assert string_to_list("[can't, that's, don't, ones']") == ["can't", "that's", "don't", "ones'"]


def test_quotes():
    assert string_to_list("except 'this' one") == ["except 'this' one"]
    assert string_to_list("[except 'this' one]") == ["except 'this' one"]
    assert string_to_list("except 'this'") == ["except 'this'"]
    assert string_to_list("[except 'this']") == ["except 'this'"]
    assert string_to_list('except "this" one') == ['except "this" one']
    assert string_to_list('[except "this" one]') == ['except "this" one']
    assert string_to_list('except "this"') == ['except "this"']
    assert string_to_list('[except "this"]') == ['except "this"']
    assert string_to_list("except 'this' one, two") == ["except 'this' one", "two"]
    assert string_to_list("[except 'this' one, two]") == ["except 'this' one", "two"]
    assert string_to_list("except 'this', two") == ["except 'this'", "two"]
    assert string_to_list("[except 'this', two]") == ["except 'this'", "two"]
    assert string_to_list('except "this" one, two') == ['except "this" one', "two"]
    assert string_to_list('[except "this" one, two]') == ['except "this" one', "two"]
    assert string_to_list('except "this", two') == ['except "this"', "two"]
    assert string_to_list('[except "this", two]') == ['except "this"', "two"]
    assert string_to_list("except 'this' one, 'two'") == ["except 'this' one", "two"]
    assert string_to_list("[except 'this' one, 'two']") == ["except 'this' one", "two"]
    assert string_to_list("except 'this', 'two'") == ["except 'this'", "two"]
    assert string_to_list("[except 'this', 'two']") == ["except 'this'", "two"]
    assert string_to_list('except "this" one, "two"') == ['except "this" one', "two"]
    assert string_to_list('[except "this" one, "two"]') == ['except "this" one', "two"]
    assert string_to_list('except "this", "two"') == ['except "this"', "two"]
    assert string_to_list('[except "this", "two"]') == ['except "this"', "two"]


# TODO this does not work, should it?
'''
def test_quotes_comma():
    assert string_to_list("except 'this, that' one") == ["except 'this, that' one"]
    assert string_to_list("[except 'this, that' one]") == ["except 'this, that' one"]
    assert string_to_list("except 'this, that'") == ["except 'this, that'"]
    assert string_to_list("[except 'this, that']") == ["except 'this, that'"]
    assert string_to_list('except "this, that" one') == ['except "this, that" one']
    assert string_to_list('[except "this, that" one]') == ['except "this, that" one']
    assert string_to_list('except "this, that"') == ['except "this, that"']
    assert string_to_list('[except "this, that"]') == ['except "this, that"']
    assert string_to_list("except 'this, that' one, two") == ["except 'this, that' one", "two"]
    assert string_to_list("[except 'this, that' one, two]") == ["except 'this, that' one", "two"]
    assert string_to_list("except 'this, that', two") == ["except 'this, that'", "two"]
    assert string_to_list("[except 'this, that', two]") == ["except 'this, that'", "two"]
    assert string_to_list('except "this, that" one, two') == ['except "this, that" one', "two"]
    assert string_to_list('[except "this, that" one, two]') == ['except "this, that" one', "two"]
    assert string_to_list('except "this, that", two') == ['except "this, that"', "two"]
    assert string_to_list('[except "this, that", two]') == ['except "this, that"', "two"]
    assert string_to_list("except 'this, that' one, 'two'") == ["except 'this, that' one", "two"]
    assert string_to_list("[except 'this, that' one, 'two']") == ["except 'this, that' one", "two"]
    assert string_to_list("except 'this, that', 'two'") == ["except 'this, that'", "two"]
    assert string_to_list("[except 'this, that', 'two']") == ["except 'this, that'", "two"]
    assert string_to_list('except "this, that" one, "two"') == ['except "this, that" one', "two"]
    assert string_to_list('[except "this, that" one, "two"]') == ['except "this, that" one', "two"]
    assert string_to_list('except "this, that", "two"') == ['except "this, that"', "two"]
    assert string_to_list('[except "this, that", "two"]') == ['except "this, that"', "two"]
'''
