"""Test cases for the counter module."""

from typing import cast

from patterncounter.counter import Bindings
from patterncounter.counter import TEnacted
from patterncounter.counter import TForwardref
from patterncounter.counter import Unbound
from patterncounter.counter import extract_metrics
from patterncounter.counter import possible_bindings
from patterncounter.parser import parse
from patterncounter.sequences import text_to_sequences


def test_possible_bindings() -> None:
    """It should find all the possible bindings for variable."""
    assert possible_bindings("X", {"A", "B", "C"}) == ("X", {"A", "B", "C"})
    assert possible_bindings("X:A, C", {"A", "B", "C"}) == ("X", {"A", "C"})
    assert possible_bindings("X~A, C", {"A", "B", "C"}) == ("X", {"B"})


def test_extract_simple() -> None:
    """It should be able to extract metrics from a simple sequence."""
    sequences = text_to_sequences("A -1 B -1 -2 A -1 -2")
    assert extract_metrics(sequences, [parse("A")]) == (
        {parse("A"): {0, 1}},
        Bindings([], {"A", "B"}, {}, {parse("A"): set()}, {}),
    )
    assert extract_metrics(sequences, [parse("B")]) == (
        {parse("B"): {0}},
        Bindings([], {"A", "B"}, {}, {parse("B"): set()}, {}),
    )


def test_extract_with_variable() -> None:
    """It should be extract with variable bindings."""
    sequences = text_to_sequences("A -1 B -1 -2 A -1 -2")
    assert extract_metrics(sequences, [parse("X")], ["X"]) == (
        {parse("A"): {0, 1}, parse("B"): {0}, parse("X"): {0, 1}},
        Bindings(
            ["X"],
            {"A", "B"},
            {
                (("X", "A"),): [(parse("X"), parse("A"))],
                (("X", "B"),): [(parse("X"), parse("B"))],
            },
            {
                parse("A"): {parse("X")},
                parse("B"): {parse("X")},
            },
            {
                (parse("X"), (("X", "A"),)): parse("A"),
                (parse("X"), (("X", "B"),)): parse("B"),
            },
        ),
    )


def test_extract_with_multiple_variables() -> None:
    """It should be extract with more than one variable."""
    sequences = text_to_sequences("A -1 B -1 -2 A -1 -2")
    assert extract_metrics(sequences, [parse("X Y")], ["X", "Y"]) == (
        {parse("(B A)"): {0}, parse("(X Y)"): {0}, parse("(A B)"): {0}},
        Bindings(
            ["X", "Y"],
            {"A", "B"},
            {
                (("X", "A"), ("Y", "B")): [(parse("X Y"), parse("A B"))],
                (("X", "B"), ("Y", "A")): [(parse("X Y"), parse("B A"))],
            },
            {
                parse("A B"): {parse("X Y")},
                parse("B A"): {parse("X Y")},
            },
            {
                (parse("X Y"), (("X", "A"), ("Y", "B"))): parse("A B"),
                (parse("X Y"), (("X", "B"), ("Y", "A"))): parse("B A"),
            },
        ),
    )


def test_extract_with_multiple_variables_intersect() -> None:
    """It should be extract with different operations."""
    sequences = text_to_sequences("A -1 B -1 -2 A -1 -2")
    assert extract_metrics(sequences, [parse("X & Y")], ["X", "Y"]) == (
        {parse("B & A"): set(), parse("X & Y"): set(), parse("A & B"): set()},
        Bindings(
            ["X", "Y"],
            {"A", "B"},
            {
                (("X", "A"), ("Y", "B")): [(parse("X & Y"), parse("A & B"))],
                (("X", "B"), ("Y", "A")): [(parse("X & Y"), parse("B & A"))],
            },
            {
                parse("A & B"): {parse("X & Y")},
                parse("B & A"): {parse("X & Y")},
            },
            {
                (parse("X & Y"), (("X", "A"), ("Y", "B"))): parse("A & B"),
                (parse("X & Y"), (("X", "B"), ("Y", "A"))): parse("B & A"),
            },
        ),
    )


def test_extract_slice() -> None:
    """It should be able to extract slice."""
    sequences = text_to_sequences("A -1 A B -1 -2 A -1 -2 A B -1 -2")
    assert extract_metrics(sequences, [parse("[A B]")]) == (
        {parse("[A B]"): {0, 2}},
        Bindings([], {"A", "B"}, {}, {parse("[A B]"): set()}, {}),
    )


def test_extract_slice_with_variable() -> None:
    """It should be able to extract slice with variable."""
    sequences = text_to_sequences("A -1 A B -1 -2 A -1 -2 A B -1 -2")
    assert extract_metrics(sequences, [parse("[A X]")], ["X"]) == (
        {parse("[A X]"): {0, 1, 2}, parse("[A A]"): {0, 1, 2}, parse("[A B]"): {0, 2}},
        Bindings(
            ["X"],
            {"A", "B"},
            {
                (("X", "A"),): [(parse("[A X]"), parse("[A A]"))],
                (("X", "B"),): [(parse("[A X]"), parse("[A B]"))],
            },
            {
                parse("[A A]"): {parse("[A X]")},
                parse("[A B]"): {parse("[A X]")},
            },
            {
                (parse("[A X]"), (("X", "A"),)): parse("[A A]"),
                (parse("[A X]"), (("X", "B"),)): parse("[A B]"),
            },
        ),
    )


def test_extract_slice_with_variable_filtering() -> None:
    """It should be able to extract slice with variable, filtering possibilites."""
    sequences = text_to_sequences("A -1 A B -1 -2 A -1 -2 A B -1 -2")
    assert extract_metrics(sequences, [parse("[A X]")], ["X~A"]) == (
        {parse("[A X]"): {0, 2}, parse("[A B]"): {0, 2}},
        Bindings(
            ["X~A"],
            {"A", "B"},
            cast(
                TEnacted,
                {
                    (("X", "B"),): [(parse("[A X]"), parse("[A B]"))],
                    (Unbound(),): [],
                },
            ),
            {
                parse("[A B]"): {parse("[A X]")},
            },
            {
                (parse("[A X]"), (("X", "B"),)): parse("[A B]"),
            },
        ),
    )


def test_extract_slice_with_multiple_variables() -> None:
    """It should be able to extract slice with multiple variables."""
    sequences = text_to_sequences("A -1 A B -1 -2 A -1 -2 A B -1 -2")
    assert extract_metrics(sequences, [parse("[Y X]")], ["X~A", "Y:A"]) == (
        {parse("[Y X]"): {0, 2}, parse("[A B]"): {0, 2}, parse("[A X]"): set()},
        Bindings(
            ["X~A", "Y:A"],
            {"A", "B"},
            cast(
                TEnacted,
                {
                    (("X", "B"), ("Y", "A")): [(parse("[Y X]"), parse("[A B]"))],
                    ((Unbound(), ("Y", "A"))): [(parse("[Y X]"), parse("[A X]"))],
                },
            ),
            {
                parse("[A B]"): {parse("[Y X]")},
                parse("[A X]"): {parse("[Y X]")},
            },
            cast(
                TForwardref,
                {
                    (parse("[Y X]"), (("X", "B"), ("Y", "A"))): parse("[A B]"),
                    (parse("[Y X]"), (Unbound(), ("Y", "A"))): parse("[A X]"),
                },
            ),
        ),
    )


def test_extract_slice_with_multiple_rules_and_variables() -> None:
    """It should be able to extract slice with multiple rules and variables."""
    sequences = text_to_sequences("A -1 A B -1 -2 A -1 -2 A B -1 -2")
    assert extract_metrics(sequences, [parse("[Y X]"), parse("Y")], ["X~A", "Y:A"]) == (
        {
            parse("[Y X]"): {0, 2},
            parse("[A B]"): {0, 2},
            parse("Y"): {0, 1, 2},
            parse("A"): {0, 1, 2},
            parse("[A X]"): set(),
        },
        Bindings(
            ["X~A", "Y:A"],
            {"A", "B"},
            cast(
                TEnacted,
                {
                    (("X", "B"), ("Y", "A")): [
                        (parse("[Y X]"), parse("[A B]")),
                        (parse("Y"), parse("A")),
                    ],
                    (Unbound(), ("Y", "A")): [
                        (parse("[Y X]"), parse("[A X]")),
                        (parse("Y"), parse("A")),
                    ],
                },
            ),
            {
                parse("[A B]"): {parse("[Y X]")},
                parse("A"): {parse("Y")},
                parse("[A X]"): {parse("[Y X]")},
            },
            cast(
                TForwardref,
                {
                    (parse("[Y X]"), (("X", "B"), ("Y", "A"))): parse("[A B]"),
                    (parse("Y"), (("X", "B"), ("Y", "A"))): parse("A"),
                    (parse("[Y X]"), (Unbound(), ("Y", "A"))): parse("[A X]"),
                    (parse("Y"), (Unbound(), ("Y", "A"))): parse("A"),
                },
            ),
        ),
    )


def test_extract_slice_with_rules_not_affected_by_variables() -> None:
    """It should be able to extract slice with rules not affected by variables."""
    sequences = text_to_sequences("A -1 A B -1 -2 A -1 -2 A B -1 -2")
    assert extract_metrics(sequences, [parse("[Y X]"), parse("A")], ["X~A", "Y:A"]) == (
        {
            parse("[Y X]"): {0, 2},
            parse("[A B]"): {0, 2},
            parse("A"): {0, 1, 2},
            parse("[A X]"): set(),
        },
        Bindings(
            ["X~A", "Y:A"],
            {"A", "B"},
            cast(
                TEnacted,
                {
                    (("X", "B"), ("Y", "A")): [
                        (parse("[Y X]"), parse("[A B]")),
                    ],
                    (Unbound(), ("Y", "A")): [
                        (parse("[Y X]"), parse("[A X]")),
                    ],
                },
            ),
            {
                parse("[A B]"): {parse("[Y X]")},
                parse("[A X]"): {parse("[Y X]")},
                parse("A"): set(),
            },
            cast(
                TForwardref,
                {
                    (parse("[Y X]"), (("X", "B"), ("Y", "A"))): parse("[A B]"),
                    (parse("[Y X]"), (Unbound(), ("Y", "A"))): parse("[A X]"),
                },
            ),
        ),
    )
