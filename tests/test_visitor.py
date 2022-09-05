"""Test cases for the visitor module."""


from patterncounter.parser import parse
from patterncounter.visitor import ReplaceVariables
from patterncounter.visitor import Visitor
from patterncounter.visitor import create_replace


def test_replace_variables_transformer() -> None:
    """It replaces a variable in Rule to a different name."""
    transformer = ReplaceVariables({"A": "D"})

    assert transformer.visit(parse("A")) == parse("D")
    assert transformer.visit(parse("[A]")) == parse("[D]")
    assert transformer.visit(parse("[X A]")) == parse("[X D]")
    assert transformer.visit(parse("[A A]")) == parse("[D D]")
    assert transformer.visit(parse("A -> B")) == parse("D -> B")
    assert transformer.visit(parse("A => B")) == parse("D => B")
    assert transformer.visit(parse("A B C")) == parse("D B C")
    assert transformer.visit(parse("A & B")) == parse("D & B")
    assert transformer.visit(parse("A (B | C)")) == parse("D (B | C)")
    assert transformer.visit(parse("(A | B) C")) == parse("(D | B) C")
    assert transformer.visit(parse("~A")) == parse("~D")
    assert transformer.visit(parse("^A")) == parse("^D")
    assert transformer.visit(parse("$A")) == parse("$D")


def test_simple_visitor() -> None:
    """It runs visitor."""
    visitor = Visitor()
    assert visitor.visit(parse("A")) == parse("A")
    assert visitor.visit(parse("[A]")) == parse("[A]")
    assert visitor.visit(parse("[X A]")) == parse("[X A]")
    assert visitor.visit(parse("[A A]")) == parse("[A A]")
    assert visitor.visit(parse("A -> B")) == parse("A -> B")
    assert visitor.visit(parse("A => B")) == parse("A => B")
    assert visitor.visit(parse("A B C")) == parse("A B C")
    assert visitor.visit(parse("A & B")) == parse("A & B")
    assert visitor.visit(parse("A (B | C)")) == parse("A (B | C)")
    assert visitor.visit(parse("(A | B) C")) == parse("(A | B) C")
    assert visitor.visit(parse("~A")) == parse("~A")
    assert visitor.visit(parse("^A")) == parse("^A")
    assert visitor.visit(parse("$A")) == parse("$A")


def test_create_replace() -> None:
    """It creates replacement rules for ReplaceVariables visitor."""
    assert create_replace({}, "A", "B") == {"A": "B", "InA": "InB", "OutA": "OutB"}
    assert create_replace({}, "A", "B", in_prefix="") == {"A": "B", "OutA": "OutB"}
    assert create_replace({}, "A", "B", out_prefix="") == {"A": "B", "InA": "InB"}
