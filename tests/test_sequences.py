"""Test cases for the sequences module."""

from patterncounter.sequences import in_out_sequence
from patterncounter.sequences import text_to_sequences


def test_text_to_sequences_single_interval() -> None:
    """Create"s sequences from single interval."""
    assert text_to_sequences("A -1 -2") == [[["A"]]]


def test_text_to_sequences_multiple_intervals() -> None:
    """Creates sequences from multiple intervals."""
    assert text_to_sequences("A -1 B -1 -2") == [[["A"], ["B"]]]


def test_text_to_sequences_multiple_lines() -> None:
    """Creates sequences from multiple lines."""
    assert text_to_sequences("A -1 B -1 -2 A -1 -2") == [[["A"], ["B"]], [["A"]]]


def test_text_to_sequences_multiple_elements() -> None:
    """Creates sequence with multiple elements within interval."""
    assert text_to_sequences("A B -1 B -1 -2") == [[["A", "B"], ["B"]]]


def test_text_to_sequences_empty_intervals() -> None:
    """Creates sequences when the interval is empty."""
    assert text_to_sequences("A B -1 -1 B -1 -2") == [[["A", "B"], [], ["B"]]]
    assert text_to_sequences("A B -1 -1 -2") == [[["A", "B"], []]]
    assert text_to_sequences("-1 A -1 -2") == [[[], ["A"]]]
    assert text_to_sequences("-1 -2") == [[[]]]


def test_in_out_sequence() -> None:
    """It adds In and Out elements to a Sequence."""
    assert in_out_sequence([["A"]]) == ([["A", "InA"]], {"A"})
    assert in_out_sequence([["A"]], in_prefix="") == ([["A"]], {"A"})
    assert in_out_sequence([["A"], []]) == ([["A", "InA"], ["OutA"]], {"A"})
    assert in_out_sequence([["A"], []], out_prefix="") == ([["A", "InA"], []], {"A"})

    assert in_out_sequence([["A"], ["A"]]) == ([["A", "InA"], ["A"]], {"A"})
    assert in_out_sequence([["A"], ["A", "B"]]) == (
        [["A", "InA"], ["A", "B", "InB"]],
        {"A", "B"},
    )
    assert in_out_sequence([["A"], ["B"]]) == (
        [["A", "InA"], ["B", "InB", "OutA"]],
        {"A", "B"},
    )
    assert in_out_sequence([["A"], ["B"], ["A"]]) == (
        [["A", "InA"], ["B", "InB", "OutA"], ["A", "InA", "OutB"]],
        {"A", "B"},
    )
    assert in_out_sequence([["A"], [], ["A"]]) == (
        [["A", "InA"], ["OutA"], ["A", "InA"]],
        {"A"},
    )
    assert in_out_sequence([[], ["A"]]) == ([[], ["A", "InA"]], {"A"})
    assert in_out_sequence([[], ["A"], ["A"]]) == ([[], ["A", "InA"], ["A"]], {"A"})
