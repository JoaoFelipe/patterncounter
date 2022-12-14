"""Test cases for the parser module."""
import pytest

from patterncounter.operators import And
from patterncounter.operators import First
from patterncounter.operators import Has
from patterncounter.operators import Last
from patterncounter.operators import Not
from patterncounter.operators import Sequence
from patterncounter.operators import Slice
from patterncounter.parser import parse


def test_simple_elements() -> None:
    """It supports simple elements."""
    assert parse("A") == Has("A")
    assert parse("[A]") == Slice("A")
    assert parse("{A]") == Slice("A", open_first=True)
    assert parse("{A}") == Slice("A", open_first=True, open_last=True)


def test_implicit_and() -> None:
    """It supports implicit and."""
    assert parse("A B") == Has("A") & Has("B")
    assert parse("A B C") == And(Has("A"), Has("B"), Has("C"))


def test_unary_operators() -> None:
    """It supports unary operators (^First, $Last, ~Not)."""
    assert parse("^A") == First(Has("A"))
    assert parse("$A") == Last(Has("A"))
    assert parse("~A") == Not(Has("A"))


def test_binary_operators() -> None:
    """It supports binary operators.

    Or: A | B
    Intersection: A & B
    Sequence: A -> B
    Same Sequence: A => B
    """
    assert parse("A | B") == Has("A") | Has("B")
    assert parse("A|B") == Has("A") | Has("B")
    assert parse("A & B") == Has("A") ^ Has("B")
    assert parse("A -> B") == Has("A") >> Has("B")
    assert parse("A->B") == Has("A") >> Has("B")
    assert parse("A => B") == Sequence(Has("A"), Has("B"), same=True)


def test_binary_mixing() -> None:
    """It supports mixing binary operators with unary operators."""
    assert parse("A | ~B") == Has("A") | Not(Has("B"))
    assert parse("~A | B") == Not(Has("A")) | Has("B")
    assert parse("A => ~B") == Sequence(Has("A"), Not(Has("B")), same=True)


def test_binary_sequence() -> None:
    """It supports a sequence of binary operators."""
    assert parse("A | B | C") == Has("A") | (Has("B") | Has("C"))
    assert parse("A | B | C | D") == Has("A") | (Has("B") | (Has("C") | Has("D")))
    assert parse("A | B | ~C | D") == Has("A") | (Has("B") | (Not(Has("C")) | Has("D")))
    assert parse("A | B E | ~C | D") == Has("A") | (
        (Has("B") & Has("E")) | (Not(Has("C")) | Has("D"))
    )


def test_slice_matching() -> None:
    """It supports matching elements within slices."""
    assert parse("{A B}") == Slice("A", open_first=True, open_last=True) << Has("B")
    assert parse("[A B]") == Slice("A") << Has("B")


def test_slice_operations() -> None:
    """It supports operations inside slices."""
    assert parse("[A B | C]") == Slice("A") << (Has("B") | Has("C"))
    assert parse("[A B C]") == Slice("A") << (Has("B") & Has("C"))
    assert parse("[A InB C]") == Slice("A") << (Has("InB") & Has("C"))


def test_parenthesis() -> None:
    """It supports parenthesis with nested operations."""
    assert parse("[A (B C)]") == Slice("A") << (Has("B") & Has("C"))
    assert parse("[A ~(B C)]") == Slice("A") << Not(Has("B") & Has("C"))
    assert parse("[A ~(B | C)]") == Slice("A") << Not(Has("B") | Has("C"))
    assert parse("[A ~^(B | C)]") == Slice("A") << Not(First(Has("B") | Has("C")))


def test_sequential_groups() -> None:
    """It supports sequences of distinct groups."""
    assert parse("[A B] -> [B]") == Sequence((Slice("A") << Has("B")), Slice("B"))
    assert parse("[A B] -> (B & C)") == Sequence(
        (Slice("A") << Has("B")), (Has("B") ^ Has("C"))
    )


def test_invalid_binary_operator() -> None:
    """It does not support starting with a binary operator."""
    with pytest.raises(ValueError) as exc_info:
        parse("A |")
    assert str(exc_info.value) == "Invalid syntax: operator split mismatch"


def test_invalid_unary_operator() -> None:
    """It does not support ending with an unary operator."""
    with pytest.raises(ValueError) as exc_info:
        parse("A ~")
    assert str(exc_info.value) == "Invalid syntax: invalid operator position"


def test_invalid_opening_parenthesis() -> None:
    """It does not support extra opening parenthesis."""
    with pytest.raises(ValueError) as exc_info:
        parse("((A)")
    assert str(exc_info.value) == "Invalid syntax: unclosed group/slice"


def test_invalid_closing_parenthesis() -> None:
    """It does not support extra closing parenthesis."""
    with pytest.raises(ValueError) as exc_info:
        parse("(A))")
    assert str(exc_info.value) == "Invalid syntax: extra ) found"


def test_invalid_first_element() -> None:
    """It does not support having an operator as first slice element."""
    with pytest.raises(ValueError) as exc_info:
        parse("[~A]")
    assert (
        str(exc_info.value)
        == "Invalid syntax: operator not supported as first element of slice"
    )
