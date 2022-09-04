"""Test cases for the operators module."""
from typing import Generator
from typing import List
from typing import Tuple

from patterncounter.operators import And
from patterncounter.operators import First
from patterncounter.operators import Has
from patterncounter.operators import Intersect
from patterncounter.operators import Last
from patterncounter.operators import Not
from patterncounter.operators import Or
from patterncounter.operators import Rule
from patterncounter.operators import Sequence
from patterncounter.operators import Slice


def find(rule: Rule, sequence: List[List[str]]) -> List[Tuple[int, int]]:
    """Convert find_positions results into a list."""
    return list(rule.find_positions(sequence))


def test_has_operator() -> None:
    """Has searches strings in sequences."""
    rule = Has("A")
    assert find(rule, [["B"], ["C"]]) == []
    assert find(rule, [["A"], ["B"], ["C"]]) == [(0, 0)]
    assert find(rule, [["B"], ["A"], ["C"]]) == [(1, 1)]
    assert find(rule, [["B"], ["C"], ["A"]]) == [(2, 2)]
    assert find(rule, [["A"], ["B"], ["A"], ["C"], ["A"]]) == [(0, 0), (2, 2), (4, 4)]
    assert find(rule, [["A", "B"], ["C"]]) == [(0, 0)]
    assert find(rule, [["B"], ["A", "C"]]) == [(1, 1)]


def test_slice_operator() -> None:
    """Slice searches sequential slices in sequences."""
    rule = Slice("A")
    assert find(rule, [["B"], ["C"]]) == []
    assert find(rule, [["A"], ["B"], ["C"]]) == [(0, 0)]
    assert find(rule, [["B"], ["A"], ["C"]]) == [(1, 1)]
    assert find(rule, [["B"], ["C"], ["A"]]) == [(2, 2)]
    assert find(rule, [["A"], ["B"], ["A"], ["C"], ["A"]]) == [(0, 0), (2, 2), (4, 4)]
    assert find(rule, [["A", "B"], ["C"]]) == [(0, 0)]
    assert find(rule, [["B"], ["A", "C"]]) == [(1, 1)]
    assert find(rule, [["A"], ["A", "B"], ["C"]]) == [(0, 1)]
    assert find(rule, [["A"], ["A", "B"], ["A", "C"]]) == [(0, 2)]
    assert find(rule, [["X"], ["A", "B"], ["A", "C"]]) == [(1, 2)]


def test_slice_nested_operator() -> None:
    """Slice supports nesting operators."""
    rule = Slice("A") << Has("B")
    assert find(rule, [["B"], ["C"]]) == []
    assert find(rule, [["A"], ["B"], ["C"]]) == []
    assert find(rule, [["A", "B"], ["C"]]) == [(0, 0)]
    assert find(rule, [["B"], ["A", "C"]]) == []
    assert find(rule, [["A"], ["A", "B"], ["C"]]) == [(0, 1)]
    assert find(rule, [["A"], ["A", "B"], ["A", "C"]]) == [(0, 2)]
    assert find(rule, [["X"], ["A", "B"], ["A", "C"]]) == [(1, 2)]


def test_slice_nested_operator_open_first() -> None:
    """Slice with open first parenthesis and nested search."""
    rule = Slice("A", open_first=True) << Has("B")
    assert find(rule, [["A", "B"], ["C"]]) == []
    assert find(rule, [["A"], ["A", "B"], ["C"]]) == [(0, 1)]
    assert find(rule, [["A", "B"], ["A"], ["C"]]) == []
    assert find(rule, [["A"], ["A", "B"], ["A", "C"]]) == [(0, 2)]
    assert find(rule, [["X"], ["A", "B"], ["A", "C"]]) == []
    assert find(rule, [["X"], ["A", "B"], ["A", "B", "C"]]) == [(1, 2)]


def test_slice_nested_operator_open_last() -> None:
    """Slice with open last parenthesis and nested search."""
    rule = Slice("A", open_last=True) << Has("B")
    assert find(rule, [["A", "B"], ["C"]]) == []
    assert find(rule, [["A"], ["A", "B"], ["C"]]) == []
    assert find(rule, [["A", "B"], ["A"], ["C"]]) == [(0, 1)]
    assert find(rule, [["A"], ["A", "B"], ["A", "C"]]) == [(0, 2)]
    assert find(rule, [["X"], ["A", "B"], ["A", "C"]]) == [(1, 2)]
    assert find(rule, [["X"], ["A", "B"], ["A", "B", "C"]]) == [(1, 2)]


def test_slice_nested_operator_open_both() -> None:
    """Slice with open first and last parentheses and nested search."""
    rule = Slice("A", open_first=True, open_last=True) << Has("B")
    assert find(rule, [["A", "B"], ["C"]]) == []
    assert find(rule, [["A"], ["A", "B"], ["C"]]) == []
    assert find(rule, [["A", "B"], ["A"], ["C"]]) == []
    assert find(rule, [["A"], ["A", "B"], ["A", "C"]]) == [(0, 2)]
    assert find(rule, [["X"], ["A", "B"], ["A", "C"]]) == []
    assert find(rule, [["X"], ["A", "B"], ["A", "B", "C"]]) == []


def test_sequence_operator() -> None:
    """Sequence searches sequential elements in sequences.

    It doesn't need to be consecutive.
    """
    rule = Sequence(Has("A"), Has("B"))
    assert find(rule, [["B"], ["C"]]) == []
    assert find(rule, [["A"], ["B"], ["C"]]) == [(0, 1)]
    assert find(rule, [["B"], ["A"], ["C"]]) == []
    assert find(rule, [["A", "B"], ["C"]]) == []
    assert find(rule, [["B"], ["A", "C"]]) == []
    assert find(rule, [["A"], ["A", "B"], ["C"]]) == [(0, 1)]
    assert find(rule, [["A"], ["A", "B"], ["A", "C"]]) == [(0, 1)]
    assert find(rule, [["X"], ["A", "B"], ["A", "C"]]) == []

    rule = Sequence(Has("A"), Has("C"))
    assert find(rule, [["A"], ["B"], ["A"], ["C"], ["A"]]) == [(0, 3), (2, 3)]
    assert find(rule, [["A", "B"], ["C"]]) == [(0, 1)]


def test_same_sequence_operator() -> None:
    """Same Sequence allows to find sequential elements within the same group."""
    rule = Sequence(Has("A"), Has("B"), same=True)
    assert find(rule, [["B"], ["C"]]) == []
    assert find(rule, [["A"], ["B"], ["C"]]) == [(0, 1)]
    assert find(rule, [["B"], ["A"], ["C"]]) == []
    assert find(rule, [["A", "B"], ["C"]]) == [(0, 0)]
    assert find(rule, [["B"], ["A", "C"]]) == []
    assert find(rule, [["A"], ["A", "B"], ["C"]]) == [(0, 1), (1, 1)]
    assert find(rule, [["A"], ["A", "B"], ["A", "C"]]) == [(0, 1), (1, 1)]
    assert find(rule, [["X"], ["A", "B"], ["A", "C"]]) == [(1, 1)]

    rule = Sequence(Has("A"), Has("C"), same=True)
    assert find(rule, [["A"], ["B"], ["A"], ["C"], ["A"]]) == [(0, 3), (2, 3)]
    assert find(rule, [["A", "B"], ["C"]]) == [(0, 1)]


def test_slice_with_nested_sequence_operator() -> None:
    """Slices can have nested sequences."""
    rule = Slice("A") << Sequence(Has("B"), Has("C"))
    assert find(rule, [["B"], ["C"]]) == []
    assert find(rule, [["A"], ["B"], ["C"]]) == []
    assert find(rule, [["A", "B"], ["C"]]) == []
    assert find(rule, [["B"], ["A", "C"]]) == []
    assert find(rule, [["A"], ["A", "B"], ["C"]]) == []
    assert find(rule, [["A"], ["A", "B"], ["A", "C"]]) == [(0, 2)]
    assert find(rule, [["X"], ["A", "B"], ["A", "C"]]) == [(1, 2)]


def test_and_operator() -> None:
    """And requires all of its rules to be true."""
    rule = Has("A") & Has("B")
    assert find(rule, [["B"], ["C"]]) == []
    assert find(rule, [["A"], ["B"], ["C"]]) == [(0, 1)]
    assert find(rule, [["B"], ["A"], ["C"]]) == [(0, 1)]
    assert find(rule, [["B"], ["C"], ["A"]]) == [(0, 2)]
    assert find(rule, [["A"], ["B"], ["A"], ["C"], ["A"]]) == [(0, 4)]
    assert find(rule, [["A", "B"], ["C"]]) == [(0, 0)]
    assert find(rule, [["B"], ["A", "C"]]) == [(0, 1)]


def test_or_operator() -> None:
    """Or requires any of its rules to be true."""
    rule = Has("A") | Has("B")
    assert find(rule, [["X"], ["C"]]) == []
    assert find(rule, [["B"], ["C"]]) == [(0, 0)]
    assert find(rule, [["A"], ["B"], ["C"]]) == [(0, 1)]
    assert find(rule, [["B"], ["A"], ["C"]]) == [(0, 1)]
    assert find(rule, [["B"], ["C"], ["A"]]) == [(0, 2)]
    assert find(rule, [["A"], ["B"], ["A"], ["C"], ["A"]]) == [(0, 4)]
    assert find(rule, [["A", "B"], ["C"]]) == [(0, 0)]
    assert find(rule, [["B"], ["A", "C"]]) == [(0, 1)]


def test_not_operator() -> None:
    """Not inverts the rule."""
    assert find(~Has("A"), [["B"], ["C"]]) == [(0, 1)]
    assert find(~Has("A"), [["A"], ["B"], ["C"]]) == []
    assert find(~Slice("A"), [["B"], ["C"]]) == [(0, 1)]
    assert find(~Slice("A"), [["A"], ["A", "B"], ["C"]]) == []
    assert find(~(Slice("A") << Has("B")), [["B"], ["A", "C"]]) == [(0, 1)]
    assert find(~(Slice("A") << Has("B")), [["A"], ["A", "B"], ["C"]]) == []
    assert find(~Sequence(Has("A"), Has("B")), [["A"], ["B"], ["C"]]) == []
    assert find(~Sequence(Has("A"), Has("B")), [["B"], ["A"], ["C"]]) == [(0, 2)]
    assert find(~Sequence(Has("A"), Has("C"), same=True), [["A", "B"], ["C"]]) == []
    assert find(Slice("A") << ~Has("B"), [["A"], ["B"], ["C"]]) == [(0, 0)]
    assert find(Slice("A") << ~Has("B"), [["A"], ["A", "B"], ["A"], ["C"], ["A"]]) == [
        (4, 4)
    ]
    assert find(~(Has("A") & Has("B")), [["B"], ["C"]]) == [(0, 1)]
    assert find(~Has("A") & Has("B"), [["B"], ["C"]]) == [(0, 1)]
    assert find(~(Has("A") | Has("B")), [["X"], ["C"]]) == [(0, 1)]
    assert find(~Has("C") | Has("B"), [["B"], ["C"]]) == [(0, 0)]


def test_intersect_operator() -> None:
    """Intersect requires rules to occur in the same locations."""
    assert find(Has("A") ^ Has("B"), [["A"], ["B"], ["C"]]) == []
    assert find(Has("A") ^ Has("B"), [["A", "B"], ["C"]]) == [(0, 0)]
    assert find(Slice("A") ^ Has("B"), [["A"], ["A", "B"], ["C"]]) == [(1, 1)]
    assert find(Slice("A") ^ Has("A"), [["A"], ["A", "B"], ["C"]]) == [(0, 0), (1, 1)]

    assert find(
        Slice("A") ^ Slice("B"), [["A"], ["A", "B"], ["A", "B"], ["B", "C"], ["A"]]
    ) == [(1, 2)]

    # Coverage
    class Temp(Rule):
        def find_positions(
            self, sequence: list[list[str]], start: int = 0
        ) -> Generator[tuple[int, int], None, None]:
            yield (0, 0)
            yield (2, 2)

    assert find(Intersect(Slice("A"), Temp()), [["A"], ["A"], ["A"]]) == [
        (0, 0),
        (2, 2),
    ]


def test_first_operator() -> None:
    """First requires rule to be at the start of sequence or group."""
    assert find(First(Has("A")), [["A"], ["B"], ["C"]]) == [(0, 0)]
    assert find(First(Has("A")), [["B"], ["A"], ["C"]]) == []
    assert find(First(Slice("A")), [["A"], ["B"], ["C"]]) == [(0, 0)]
    assert find(First(Slice("A")), [["B"], ["A"], ["C"]]) == []
    assert find(Slice("A") << First(Has("B")), [["A", "B"], ["C"]]) == [(0, 0)]
    assert find(
        Slice("A") << First(Has("B")), [["A", "B"], ["A", "B", "C"], ["C"]]
    ) == [(0, 1)]
    assert find(Slice("A") << First(Has("B")), [["A"], ["A", "B"], ["C"]]) == []


def test_last_operator() -> None:
    """Last requires rule to be at the end of sequence or group."""
    assert find(Last(Has("A")), [["A"], ["B"], ["C"]]) == []
    assert find(Last(Has("A")), [["B"], ["C"], ["A"]]) == [(2, 2)]
    assert find(Last(Slice("A")), [["A"], ["B"], ["C"]]) == []
    assert find(Last(Slice("C")), [["B"], ["A"], ["C"]]) == [(2, 2)]
    assert find(Slice("A") << Last(Has("B")), [["A", "B"], ["C"]]) == [(0, 0)]
    assert find(Slice("A") << Last(Has("B")), [["A", "B"], ["A", "B", "C"], ["C"]]) == [
        (0, 1)
    ]
    assert find(Slice("A") << Last(Has("B")), [["A", "B"], ["A"], ["C"]]) == []


def test_equality() -> None:
    """All operators should define __equals__ method."""
    assert Has("A") == Has("A")
    assert Slice("A") == Slice("A")
    assert Slice("A") << Has("B") == Slice("A") << Has("B")
    assert Slice("A", open_first=True, open_last=True) != Slice("A")
    assert Slice("A", open_first=True, open_last=True) == Slice(
        "A", open_first=True, open_last=True
    )
    assert Sequence(Has("A"), Has("B")) == Sequence(Has("A"), Has("B"))
    assert Sequence(Has("A"), Has("B"), same=True) != Sequence(Has("A"), Has("B"))
    assert Sequence(Has("A"), Has("B"), same=True) == Sequence(
        Has("A"), Has("B"), same=True
    )
    assert And(Has("A"), Has("B")) == And(Has("A"), Has("B"))
    assert Or(Has("A"), Has("B")) == Or(Has("A"), Has("B"))
    assert Not(Has("A")) == Not(Has("A"))
    assert Intersect(Has("A"), Has("B")) == Intersect(Has("A"), Has("B"))
    assert First(Has("A")) == First(Has("A"))
    assert Last(Has("A")) == Last(Has("A"))
