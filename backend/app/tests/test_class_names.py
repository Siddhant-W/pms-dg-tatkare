import pytest

from app.services.class_names import ClassRef, parse_class


@pytest.mark.parametrize("raw, grade, division", [
    ("8-II", 8, 2),
    ("6-I", 6, 1),
    ("10-I", 10, 1),
    ("Class VIII-2", 8, 2),
    ("Class IX-1", 9, 1),
    ("class x-2", 10, 2),
    ("Class V-1", 5, 1),
    ("9B", 9, "B"),
    ("9 - a", 9, "A"),
    ("  7-II  ", 7, 2),
    ("Std 7-I", 7, 1),
])
def test_parses_both_spellings_to_the_same_structure(raw, grade, division):
    assert parse_class(raw) == ClassRef(grade, division)


def test_the_two_spellings_of_one_class_are_equal():
    # Timetable periods say "8-II"; class-teacher assignments say "Class VIII-2".
    assert parse_class("8-II") == parse_class("Class VIII-2")


def test_standard_only_names_have_no_division():
    assert parse_class("Class IX") == ClassRef(9, None)
    assert parse_class("7") == ClassRef(7, None)


@pytest.mark.parametrize("raw", [None, "", "   ", "Scout Guide", "P.T.", "13-I", "0-I", "Mathematics"])
def test_unrecognised_names_return_none(raw):
    assert parse_class(raw) is None


def test_label_is_canonical_and_same_standard_ignores_division():
    assert parse_class("Class VI-1").label == "6-I"
    assert parse_class("6-II").label == "6-II"
    assert parse_class("9B").label == "9-B"
    assert parse_class("6-I").same_standard(parse_class("Class VI-2"))
    assert not parse_class("6-I").same_standard(parse_class("7-I"))
