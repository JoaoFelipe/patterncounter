"""Defines a Visitor for an operator tree."""
from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING
from typing import Any
from typing import List
from typing import Tuple
from typing import TypeVar
from typing import cast


if TYPE_CHECKING:
    from .operators import And as TAnd
    from .operators import First as TFirst
    from .operators import Has as THas
    from .operators import Intersect as TIntersect
    from .operators import Last as TLast
    from .operators import Not as TNot
    from .operators import Or as TOr
    from .operators import Rule as TRule
    from .operators import Sequence as TSequence
    from .operators import Slice as TSlice
else:
    TAnd = TypeVar("And")
    TFirst = TypeVar("First")
    THas = TypeVar("Has")
    TIntersect = TypeVar("Intersect")
    TLast = TypeVar("Last")
    TNot = TypeVar("Not")
    TOr = TypeVar("Or")
    TRule = TypeVar("Rule")
    TSequence = TypeVar("Sequence")
    TSlice = TypeVar("Slice")


class Visitor:
    """Generic visitor for operators."""

    transforming = False

    def visit(self, rule: TRule) -> Any:
        """Visits generic rule."""
        return rule.accept(self)

    def visit_slice(self, slice: TSlice) -> Any:
        """Visits Slice operator."""
        subrules = [rule.accept(self) for rule in slice.subrules]
        if self.transforming:
            slice.subrules = cast(List[TRule], subrules)
        return slice

    def visit_has(self, has: THas) -> Any:
        """Visits Has operator."""
        return has

    def visit_sequence(self, sequence: TSequence) -> Any:
        """Visits Sequence operator."""
        rules = tuple(rule.accept(self) for rule in sequence.rules)
        if self.transforming:
            sequence.rules = cast(Tuple[TRule, ...], rules)
        return sequence

    def visit_and(self, and_: TAnd) -> Any:
        """Visits And operator."""
        rules = tuple(rule.accept(self) for rule in and_.rules)
        if self.transforming:
            and_.rules = cast(Tuple[TRule, ...], rules)
        return and_

    def visit_or(self, or_: TOr) -> Any:
        """Visits Or operator."""
        rules = tuple(rule.accept(self) for rule in or_.rules)
        if self.transforming:
            or_.rules = cast(Tuple[TRule, ...], rules)
        return or_

    def visit_not(self, not_: TNot) -> Any:
        """Visits Not operator."""
        rule = not_.rule.accept(self)
        if self.transforming:
            not_.rule = cast(TRule, rule)
        return not_

    def visit_intersect(self, intersect: TIntersect) -> Any:
        """Visits Intersect operator."""
        rules = tuple(rule.accept(self) for rule in intersect.rules)
        if self.transforming:
            intersect.rules = cast(Tuple[TRule, ...], rules)
        return intersect

    def visit_first(self, first: TFirst) -> Any:
        """Visits First operator."""
        rule = first.rule.accept(self)
        if self.transforming:
            first.rule = cast(TRule, rule)
        return first

    def visit_last(self, last: TLast) -> Any:
        """Visits Last operator."""
        rule = last.rule.accept(self)
        if self.transforming:
            last.rule = cast(TRule, rule)
        return last


class Trasnformer(Visitor):
    """Visitor that transforms rules."""

    transforming = True


class ReplaceVariables(Trasnformer):
    """Replaces variables in rules."""

    def __init__(self, replaces: dict[str, str]):
        """Initializes ReplaceVariables."""
        self.transforming = True
        self.replaces = replaces

    def visit(self, rule: TRule) -> Any:
        """Creates a copy of visited rule."""
        return super().visit(deepcopy(rule))

    def visit_has(self, has: THas) -> Any:
        """Visits Has to replace it."""
        for old, new in self.replaces.items():
            if has.element == old:
                has.element = new
                break
        return super().visit_has(has)

    def visit_slice(self, slice: TSlice) -> Any:
        """Visits Slice to replace it."""
        for old, new in self.replaces.items():
            if slice.element == old:
                slice.element = new
                break
        return super().visit_slice(slice)


def create_replace(
    replace: dict[str, str],
    old_name: str,
    new_name: str,
    in_prefix: str = "In",
    out_prefix: str = "Out",
) -> dict[str, str]:
    """Creates replace rules for ReplaceVariables."""
    replace[old_name] = new_name
    if in_prefix:
        replace[in_prefix + old_name] = in_prefix + new_name
    if out_prefix:
        replace[out_prefix + old_name] = out_prefix + new_name
    return replace
