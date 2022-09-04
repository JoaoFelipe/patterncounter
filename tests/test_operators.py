"""Test cases for the operators module"""
from patterncounter.operators import Has, Slice, And, Sequence
from patterncounter.operators import First, Last, Not, Or, Intersect


def test_has_operator() -> None:
    """Has searches strings in sequences"""
    assert list(Has("A").find_positions([["B"], ["C"]])) == []
    assert list(Has("A").find_positions([["A"], ["B"], ["C"]])) == [(0, 0)]
    assert list(Has("A").find_positions([["B"], ["A"], ["C"]])) == [(1, 1)]
    assert list(Has("A").find_positions([["B"], ["C"], ["A"]])) == [(2, 2)]
    assert list(Has("A").find_positions([["A"], ["B"], ["A"], ["C"], ["A"]])) == [(0, 0), (2, 2), (4, 4)]
    assert list(Has("A").find_positions([["A", "B"], ["C"]])) == [(0, 0)]
    assert list(Has("A").find_positions([["B"], ["A", "C"]])) == [(1, 1)]


def test_slice_operator() -> None:
    """Slice searches sequential slices in sequences"""
    assert list(Slice("A").find_positions([["B"], ["C"]])) == []
    assert list(Slice("A").find_positions([["A"], ["B"], ["C"]])) == [(0, 0)]
    assert list(Slice("A").find_positions([["B"], ["A"], ["C"]])) == [(1, 1)]
    assert list(Slice("A").find_positions([["B"], ["C"], ["A"]])) == [(2, 2)]
    assert list(Slice("A").find_positions([["A"], ["B"], ["A"], ["C"], ["A"]])) == [(0, 0), (2, 2), (4, 4)]
    assert list(Slice("A").find_positions([["A", "B"], ["C"]])) == [(0, 0)]
    assert list(Slice("A").find_positions([["B"], ["A", "C"]])) == [(1, 1)]
    assert list(Slice("A").find_positions([["A"], ["A", "B"], ["C"]])) == [(0, 1)]
    assert list(Slice("A").find_positions([["A"], ["A", "B"], ["A", "C"]])) == [(0, 2)]
    assert list(Slice("A").find_positions([["X"], ["A", "B"], ["A", "C"]])) == [(1, 2)]


def test_slice_nested_operator() -> None:
    """Slice supports nesting operators"""
    assert list((Slice("A") << Has("B")).find_positions([["B"], ["C"]])) == []
    assert list((Slice("A") << Has("B")).find_positions([["A"], ["B"], ["C"]])) == []
    assert list((Slice("A") << Has("B")).find_positions([["A", "B"], ["C"]])) == [(0, 0)]
    assert list((Slice("A") << Has("B")).find_positions([["B"], ["A", "C"]])) == []
    assert list((Slice("A") << Has("B")).find_positions([["A"], ["A", "B"], ["C"]])) == [(0, 1)]
    assert list((Slice("A") << Has("B")).find_positions([["A"], ["A", "B"], ["A", "C"]])) == [(0, 2)]
    assert list((Slice("A") << Has("B")).find_positions([["X"], ["A", "B"], ["A", "C"]])) == [(1, 2)]


def test_slice_nested_operator_open_first() -> None:
    """Slice with open first parenthesis and nested search"""
    assert list((Slice("A", open_first=True) << Has("B")).find_positions([["A", "B"], ["C"]])) == []
    assert list((Slice("A", open_first=True) << Has("B")).find_positions([["A"], ["A", "B"], ["C"]])) == [(0, 1)]
    assert list((Slice("A", open_first=True) << Has("B")).find_positions([["A", "B"], ["A",], ["C"]])) == []
    assert list((Slice("A", open_first=True) << Has("B")).find_positions([["A"], ["A", "B"], ["A", "C"]])) == [(0, 2)]
    assert list((Slice("A", open_first=True) << Has("B")).find_positions([["X"], ["A", "B"], ["A", "C"]])) == []
    assert list((Slice("A", open_first=True) << Has("B")).find_positions([["X"], ["A", "B"], ["A", "B", "C"]])) == [(1, 2)]


def test_slice_nested_operator_open_last() -> None:
    """Slice with open last parenthesis and nested search"""
    assert list((Slice("A", open_last=True) << Has("B")).find_positions([["A", "B"], ["C"]])) == []
    assert list((Slice("A", open_last=True) << Has("B")).find_positions([["A"], ["A", "B"], ["C"]])) == []
    assert list((Slice("A", open_last=True) << Has("B")).find_positions([["A", "B"], ["A",], ["C"]])) == [(0, 1)]
    assert list((Slice("A", open_last=True) << Has("B")).find_positions([["A"], ["A", "B"], ["A", "C"]])) == [(0, 2)]
    assert list((Slice("A", open_last=True) << Has("B")).find_positions([["X"], ["A", "B"], ["A", "C"]])) == [(1, 2)]
    assert list((Slice("A", open_last=True) << Has("B")).find_positions([["X"], ["A", "B"], ["A", "B", "C"]])) == [(1, 2)]


def test_slice_nested_operator_open_both() -> None:
    """Slice with open first and last parentheses and nested search"""
    assert list((Slice("A", open_first=True, open_last=True) << Has("B")).find_positions([["A", "B"], ["C"]])) == []
    assert list((Slice("A", open_first=True, open_last=True) << Has("B")).find_positions([["A"], ["A", "B"], ["C"]])) == []
    assert list((Slice("A", open_first=True, open_last=True) << Has("B")).find_positions([["A", "B"], ["A",], ["C"]])) == []
    assert list((Slice("A", open_first=True, open_last=True) << Has("B")).find_positions([["A"], ["A", "B"], ["A", "C"]])) == [(0, 2)]
    assert list((Slice("A", open_first=True, open_last=True) << Has("B")).find_positions([["X"], ["A", "B"], ["A", "C"]])) == []
    assert list((Slice("A", open_first=True, open_last=True) << Has("B")).find_positions([["X"], ["A", "B"], ["A", "B", "C"]])) == []


def test_sequence_operator() -> None:
    """Sequence searches sequential elements in sequences (it doesn't need to be consecutive)"""
    assert list(Sequence(Has("A"), Has("B")).find_positions([["B"], ["C"]])) == []
    assert list(Sequence(Has("A"), Has("B")).find_positions([["A"], ["B"], ["C"]])) == [(0, 1)]
    assert list(Sequence(Has("A"), Has("B")).find_positions([["B"], ["A"], ["C"]])) == []
    assert list(Sequence(Has("A"), Has("C")).find_positions([["A"], ["B"], ["A"], ["C"], ["A"]])) == [(0, 3), (2, 3)]
    assert list(Sequence(Has("A"), Has("C")).find_positions([["A", "B"], ["C"]])) == [(0, 1)]
    assert list(Sequence(Has("A"), Has("B")).find_positions([["A", "B"], ["C"]])) == []
    assert list(Sequence(Has("A"), Has("B")).find_positions([["B"], ["A", "C"]])) == []
    assert list(Sequence(Has("A"), Has("B")).find_positions([["A"], ["A", "B"], ["C"]])) == [(0, 1)]
    assert list(Sequence(Has("A"), Has("B")).find_positions([["A"], ["A", "B"], ["A", "C"]])) == [(0, 1)]
    assert list(Sequence(Has("A"), Has("B")).find_positions([["X"], ["A", "B"], ["A", "C"]])) == []


def test_same_sequence_operator() -> None:
    """Same Sequence allows to find sequential elements within the same group"""
    assert list(Sequence(Has("A"), Has("B"), same=True).find_positions([["B"], ["C"]])) == []
    assert list(Sequence(Has("A"), Has("B"), same=True).find_positions([["A"], ["B"], ["C"]])) == [(0, 1)]
    assert list(Sequence(Has("A"), Has("B"), same=True).find_positions([["B"], ["A"], ["C"]])) == []
    assert list(Sequence(Has("A"), Has("C"), same=True).find_positions([["A"], ["B"], ["A"], ["C"], ["A"]])) == [(0, 3), (2, 3)]
    assert list(Sequence(Has("A"), Has("C"), same=True).find_positions([["A", "B"], ["C"]])) == [(0, 1)]
    assert list(Sequence(Has("A"), Has("B"), same=True).find_positions([["A", "B"], ["C"]])) == [(0, 0)]
    assert list(Sequence(Has("A"), Has("B"), same=True).find_positions([["B"], ["A", "C"]])) == []
    assert list(Sequence(Has("A"), Has("B"), same=True).find_positions([["A"], ["A", "B"], ["C"]])) == [(0, 1), (1, 1)]
    assert list(Sequence(Has("A"), Has("B"), same=True).find_positions([["A"], ["A", "B"], ["A", "C"]])) == [(0, 1), (1, 1)]
    assert list(Sequence(Has("A"), Has("B"), same=True).find_positions([["X"], ["A", "B"], ["A", "C"]])) == [(1, 1)]


def test_slice_with_nested_sequence_operator() -> None:
    """Slices can have nested sequences"""
    assert list((Slice("A") << Sequence(Has("B"), Has("C"))).find_positions([["B"], ["C"]])) == []
    assert list((Slice("A") << Sequence(Has("B"), Has("C"))).find_positions([["A"], ["B"], ["C"]])) == []
    assert list((Slice("A") << Sequence(Has("B"), Has("C"))).find_positions([["A", "B"], ["C"]])) == []
    assert list((Slice("A") << Sequence(Has("B"), Has("C"))).find_positions([["B"], ["A", "C"]])) == []
    assert list((Slice("A") << Sequence(Has("B"), Has("C"))).find_positions([["A"], ["A", "B"], ["C"]])) == []
    assert list((Slice("A") << Sequence(Has("B"), Has("C"))).find_positions([["A"], ["A", "B"], ["A", "C"]])) == [(0, 2)]
    assert list((Slice("A") << Sequence(Has("B"), Has("C"))).find_positions([["X"], ["A", "B"], ["A", "C"]])) == [(1, 2)]


def test_and_operator() -> None:
    """And requires all of its rules to be true"""
    assert list((Has("A") & Has("B")).find_positions([["B"], ["C"]])) == []
    assert list((Has("A") & Has("B")).find_positions([["A"], ["B"], ["C"]])) == [(0, 1)]
    assert list((Has("A") & Has("B")).find_positions([["B"], ["A"], ["C"]])) == [(0, 1)]
    assert list((Has("A") & Has("B")).find_positions([["B"], ["C"], ["A"]])) == [(0, 2)]
    assert list((Has("A") & Has("B")).find_positions([["A"], ["B"], ["A"], ["C"], ["A"]])) == [(0, 4)]
    assert list((Has("A") & Has("B")).find_positions([["A", "B"], ["C"]])) == [(0, 0)]
    assert list((Has("A") & Has("B")).find_positions([["B"], ["A", "C"]])) == [(0, 1)]


def test_or_operator() -> None:
    """Or requires any of its rules to be true"""
    assert list((Has("A") | Has("B")).find_positions([["X"], ["C"]])) == []
    assert list((Has("A") | Has("B")).find_positions([["B"], ["C"]])) == [(0, 0)]
    assert list((Has("A") | Has("B")).find_positions([["A"], ["B"], ["C"]])) == [(0, 1)]
    assert list((Has("A") | Has("B")).find_positions([["B"], ["A"], ["C"]])) == [(0, 1)]
    assert list((Has("A") | Has("B")).find_positions([["B"], ["C"], ["A"]])) == [(0, 2)]
    assert list((Has("A") | Has("B")).find_positions([["A"], ["B"], ["A"], ["C"], ["A"]])) == [(0, 4)]
    assert list((Has("A") | Has("B")).find_positions([["A", "B"], ["C"]])) == [(0, 0)]
    assert list((Has("A") | Has("B")).find_positions([["B"], ["A", "C"]])) == [(0, 1)]


def test_not_operator() -> None:
    """Not inverts the rule"""
    assert list((~Has("A")).find_positions([["B"], ["C"]])) == [(0, 1)]
    assert list((~Has("A")).find_positions([["A"], ["B"], ["C"]])) == []
    assert list((~Slice("A")).find_positions([["B"], ["C"]])) == [(0, 1)]
    assert list((~Slice("A")).find_positions([["A"], ["A", "B"], ["C"]])) == []
    assert list((~(Slice("A") << Has("B"))).find_positions([["B"], ["A", "C"]])) == [(0, 1)]
    assert list((~(Slice("A") << Has("B"))).find_positions([["A"], ["A", "B"], ["C"]])) == []
    assert list((~Sequence(Has("A"), Has("B"))).find_positions([["A"], ["B"], ["C"]])) == []
    assert list((~Sequence(Has("A"), Has("B"))).find_positions([["B"], ["A"], ["C"]])) == [(0, 2)]
    assert list((~Sequence(Has("A"), Has("C"), same=True)).find_positions([["A", "B"], ["C"]])) == []
    assert list((Slice("A") << ~Has("B")).find_positions([["A"], ["B"], ["C"]])) == [(0, 0)]
    assert list((Slice("A") << ~Has("B")).find_positions([["A"], ["A", "B"], ["A"], ["C"], ["A"]])) == [(4, 4)]
    assert list((~(Has("A") & Has("B"))).find_positions([["B"], ["C"]])) == [(0, 1)]
    assert list((~Has("A") & Has("B")).find_positions([["B"], ["C"]])) == [(0, 1)]
    assert list((~(Has("A") | Has("B"))).find_positions([["X"], ["C"]])) == [(0, 1)]
    assert list((~Has("C") | Has("B")).find_positions([["B"], ["C"]])) == [(0, 0)]


def test_intersect_operator() -> None:
    """Intersect requires rules to occur in the same locations"""
    assert list((Has("A") ^ Has("B")).find_positions([["A"], ["B"], ["C"]])) == []
    assert list((Has("A") ^ Has("B")).find_positions([["A", "B"], ["C"]])) == [(0, 0)]
    assert list((Slice("A") ^ Has("B")).find_positions([["A"], ["A", "B"], ["C"]])) == [(1, 1)]
    assert list((Slice("A") ^ Has("A")).find_positions([["A"], ["A", "B"], ["C"]])) == [(0, 0), (1, 1)]
    assert list((Slice("A") ^ Slice("B")).find_positions([["A"], ["A", "B"], ["A", "B"], ["B", "C"], ["A"]])) == [(1, 2)]


def test_first_operator() -> None:
    """First requires rule to be at the start of sequence or group"""
    assert list(First(Has("A")).find_positions([["A"], ["B"], ["C"]])) == [(0, 0)]
    assert list(First(Has("A")).find_positions([["B"], ["A"], ["C"]])) == []
    assert list(First(Slice("A")).find_positions([["A"], ["B"], ["C"]])) == [(0, 0)]
    assert list(First(Slice("A")).find_positions([["B"], ["A"], ["C"]])) == []
    assert list((Slice("A") << First(Has("B"))).find_positions([["A", "B"], ["C"]])) == [(0, 0)]
    assert list((Slice("A") << First(Has("B"))).find_positions([["A", "B"], ["A", "B", "C"], ["C"]])) == [(0, 1)]
    assert list((Slice("A") << First(Has("B"))).find_positions([["A"], ["A", "B"], ["C"]])) == []


def test_last_operator() -> None:
    """Last requires rule to be at the end of sequence or group"""
    assert list(Last(Has("A")).find_positions([["A"], ["B"], ["C"]])) == []
    assert list(Last(Has("A")).find_positions([["B"], ["C"], ["A"]])) == [(2, 2)]
    assert list(Last(Slice("A")).find_positions([["A"], ["B"], ["C"]])) == []
    assert list(Last(Slice("C")).find_positions([["B"], ["A"], ["C"]])) == [(2, 2)]
    assert list((Slice("A") << Last(Has("B"))).find_positions([["A", "B"], ["C"]])) == [(0, 0)]
    assert list((Slice("A") << Last(Has("B"))).find_positions([["A", "B"], ["A", "B", "C"], ["C"]])) == [(0, 1)]
    assert list((Slice("A") << Last(Has("B"))).find_positions([["A", "B"], ["A"], ["C"]])) == []


def test_equality() -> None:
    """All operators should define __equals__ method"""
    assert Has("A") == Has("A")
    assert Slice("A") == Slice("A")
    assert Slice("A") << Has("B") == Slice("A") << Has("B")
    assert Slice("A", open_first=True, open_last=True) != Slice("A")
    assert Slice("A", open_first=True, open_last=True) == Slice("A", open_first=True, open_last=True)
    assert Sequence(Has("A"), Has("B")) == Sequence(Has("A"), Has("B")) 
    assert Sequence(Has("A"), Has("B"), same=True) != Sequence(Has("A"), Has("B")) 
    assert Sequence(Has("A"), Has("B"), same=True) == Sequence(Has("A"), Has("B"), same=True) 
    assert And(Has("A"), Has("B")) == And(Has("A"), Has("B")) 
    assert Or(Has("A"), Has("B")) == Or(Has("A"), Has("B")) 
    assert Not(Has("A")) == Not(Has("A"))
    assert Intersect(Has("A"), Has("B")) == Intersect(Has("A"), Has("B"))
    assert First(Has("A")) == First(Has("A"))
    assert Last(Has("A")) == Last(Has("A"))
