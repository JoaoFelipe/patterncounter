"""Defines operators for finding patterns."""
from __future__ import annotations

from abc import ABCMeta
from abc import abstractmethod
from itertools import product
from typing import Any
from typing import Generator
from typing import Iterable

from .sequences import TSequence
from .visitor import Visitor


def _show(rules: Iterable[Rule], sep: str) -> str:
    """Converts rules to repr with parentheses."""
    first, *rest = rules
    result = [repr(first), sep]
    if len(rest) == 1:
        result.append(repr(rest[0]))
    else:
        result.append("(")
        result.append(_show(rest, sep))
        result.append(")")
    return "".join(result)


class Rule(metaclass=ABCMeta):
    """Base operator with Python operator overloads."""

    @abstractmethod
    def find_positions(
        self, sequence: TSequence, start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""

    @abstractmethod
    def accept(self, visitor: Visitor) -> Any:
        """Visits rule."""

    def check(self, sequence: TSequence) -> bool:
        """Checks if operator matches a pattern."""
        for _ in self.find_positions(sequence):
            return True
        return False

    def __and__(self, other: Rule) -> And:
        """Rule & Rule --> Checks if both rules apply."""
        return And(self, other)

    def __or__(self, other: Rule) -> Or:
        """Rule | Rule --> Checks if either rules apply."""
        return Or(self, other)

    def __invert__(self) -> Not:
        """~Rule --> Inverts rule."""
        return Not(self)

    def __xor__(self, other: Rule) -> Intersect:
        """Rule ^ Rule --> Checks if rules apply at the same positions."""
        return Intersect(self, other)

    def __rshift__(self, other: Rule) -> Sequence:
        """Rule >> Rule --> Checks if second rule occurs after first."""
        return Sequence(self, other)


class Slice(Rule):
    """Slice operator for finding a slice of sequential elements."""

    def __init__(self, element: str, open_first: bool = False, open_last: bool = False):
        """Initializes Slice."""
        self.element = element
        self.subrules: list[Rule] = []
        self.open_first = int(open_first)
        self.open_last = int(open_last)

    def find_positions(
        self, sequence: TSequence, start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        first = None
        for i, moment in enumerate(sequence):
            if first is None and self.element in moment:
                first = i
            elif first is not None and self.element not in moment:
                if all(
                    rule.check(sequence[first + self.open_first : i - self.open_last])
                    for rule in self.subrules
                ):
                    yield (first + start, i - 1 + start)
                first = None
        if first is not None:
            if all(
                rule.check(sequence[first + self.open_first : -self.open_last or None])
                for rule in self.subrules
            ):
                yield (first + start, len(sequence) - 1 + start)

    def accept(self, visitor: Visitor) -> Any:
        """Visits rule."""
        return visitor.visit_slice(self)

    def __lshift__(self, other: Rule) -> Slice:
        """Rule << Rule. Checks rule inside slice."""
        self.subrules.append(other)
        return self

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Slice) and (
            self.element,
            self.subrules,
            self.open_first,
            self.open_last,
        ) == (other.element, other.subrules, other.open_first, other.open_last)

    def __repr__(self) -> str:
        """Represents rule."""
        result = []
        result.append("{" if self.open_first else "[")
        result.append(self.element)
        for rule in self.subrules:
            result.append(f" {rule!r}")
        result.append("}" if self.open_last else "]")
        return "".join(result)

    def __hash__(self) -> int:
        """Returns rule hash based on repr string."""
        return hash(repr(self))


class Has(Rule):
    """Has operator for finding elements in the sequence."""

    def __init__(self, element: str):
        """Initializes Has."""
        self.element = element

    def find_positions(
        self, sequence: TSequence, start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        for i, moment in enumerate(sequence):
            if self.element in moment:
                yield (i + start, i + start)

    def accept(self, visitor: Visitor) -> Any:
        """Visits rule."""
        return visitor.visit_has(self)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Has) and self.element == other.element

    def __repr__(self) -> str:
        """Represents rule."""
        return self.element

    def __hash__(self) -> int:
        """Returns rule hash based on repr string."""
        return hash(repr(self))


class Sequence(Rule):
    """Sequence operator for finding sequences of rules."""

    def __init__(self, *rules: Rule, same: bool = False):
        """Initializes Sequence."""
        self.rules: Iterable[Rule] = rules
        self.same = same

    def find_positions(
        self, sequence: TSequence, start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        rule_pos = [rule.find_positions(sequence, start) for rule in self.rules]
        for positions in product(*rule_pos):
            it = iter(positions)
            next(it)
            for first, second in zip(positions, it):
                if first[-1] >= second[0] and (not self.same or first[-1] > second[0]):
                    break
            else:
                yield (positions[0][0], positions[-1][-1])

    def accept(self, visitor: Visitor) -> Any:
        """Visits rule."""
        return visitor.visit_sequence(self)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Sequence) and (self.rules, self.same) == (
            other.rules,
            other.same,
        )

    def __repr__(self) -> str:
        """Represents rule."""
        return _show(self.rules, " => " if self.same else " -> ")

    def __hash__(self) -> int:
        """Returns rule hash based on repr string."""
        return hash(repr(self))


class And(Rule):
    """And operator for combining rules."""

    def __init__(self, *rules: Rule):
        """Initializes And."""
        self.rules: Iterable[Rule] = rules

    def find_positions(
        self, sequence: TSequence, start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        rule_pos = [list(rule.find_positions(sequence, start)) for rule in self.rules]
        if all(rule_pos):
            minimum = min(pos[0] for rule in rule_pos for pos in rule)
            maximum = max(pos[-1] for rule in rule_pos for pos in rule)
            yield (minimum, maximum)

    def accept(self, visitor: Any) -> Any:
        """Visits rule."""
        return visitor.visit_and(self)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, And) and self.rules == other.rules

    def __repr__(self) -> str:
        """Represents rule."""
        reprs = [repr(rule) for rule in self.rules]
        return f"({' '.join(reprs)})"

    def __hash__(self) -> int:
        """Returns rule hash based on repr string."""
        return hash(repr(self))


class Or(Rule):
    """Or operator for combining rules."""

    def __init__(self, *rules: Rule):
        """Initializes Or."""
        self.rules: Iterable[Rule] = rules

    def find_positions(
        self, sequence: TSequence, start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        rule_pos = [list(rule.find_positions(sequence, start)) for rule in self.rules]
        if any(rule_pos):
            minimum = min(pos[0] for rule in rule_pos for pos in rule)
            maximum = max(pos[-1] for rule in rule_pos for pos in rule)
            yield (minimum, maximum)

    def accept(self, visitor: Visitor) -> Any:
        """Visits rule."""
        return visitor.visit_or(self)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Or) and self.rules == other.rules

    def __repr__(self) -> str:
        """Represents rule."""
        return _show(self.rules, " | ")

    def __hash__(self) -> int:
        """Returns rule hash based on repr string."""
        return hash(repr(self))


class Not(Rule):
    """Not operator for inverting rules."""

    def __init__(self, rule: Rule):
        """Initializes Not."""
        self.rule = rule

    def find_positions(
        self, sequence: TSequence, start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        for _ in self.rule.find_positions(sequence, start):
            return
        yield (start, len(sequence) + start - 1)

    def accept(self, visitor: Visitor) -> Any:
        """Visits rule."""
        return visitor.visit_not(self)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Not) and self.rule == other.rule

    def __repr__(self) -> str:
        """Represents rule."""
        return f"~{self.rule!r}"

    def __hash__(self) -> int:
        """Returns rule hash based on repr string."""
        return hash(repr(self))


class Intersect(Rule):
    """Intersect operator for intersecting rules."""

    def __init__(self, *rules: Rule):
        """Initializes Intersect."""
        self.rules: Iterable[Rule] = rules

    def find_positions(
        self, sequence: TSequence, start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        rule_pos = [list(rule.find_positions(sequence, start)) for rule in self.rules]
        for positions in product(*rule_pos):
            minimum = start
            maximum = len(sequence) + start
            for pos in positions:
                if pos[-1] < minimum:
                    break
                if pos[0] > maximum:
                    break
                minimum = max(minimum, pos[0])
                maximum = min(maximum, pos[-1])
            else:
                yield (minimum, maximum)

    def accept(self, visitor: Visitor) -> Any:
        """Visits rule."""
        return visitor.visit_intersect(self)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Intersect) and self.rules == other.rules

    def __repr__(self) -> str:
        """Represents rule."""
        return _show(self.rules, " & ")

    def __hash__(self) -> int:
        """Returns rule hash based on repr string."""
        return hash(repr(self))


class First(Rule):
    """First operator for checking if rule appears in the first position of sequence."""

    def __init__(self, rule: Rule):
        """Initializes First."""
        self.rule = rule

    def find_positions(
        self, sequence: TSequence, start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        for pos in self.rule.find_positions(sequence, start):
            if pos[0] == start:
                yield pos

    def accept(self, visitor: Visitor) -> Any:
        """Visits rule."""
        return visitor.visit_first(self)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, First) and self.rule == other.rule

    def __repr__(self) -> str:
        """Represents rule."""
        return f"^{self.rule!r}"

    def __hash__(self) -> int:
        """Returns rule hash based on repr string."""
        return hash(repr(self))


class Last(Rule):
    """Last operator to check if rule appears in the last position of sequence."""

    def __init__(self, rule: Rule):
        """Initializes Last."""
        self.rule = rule

    def find_positions(
        self, sequence: TSequence, start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        for pos in self.rule.find_positions(sequence, start):
            if pos[-1] == len(sequence) + start - 1:
                yield pos

    def accept(self, visitor: Visitor) -> Any:
        """Visits rule."""
        return visitor.visit_last(self)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Last) and self.rule == other.rule

    def __repr__(self) -> str:
        """Represents rule."""
        return f"${self.rule!r}"

    def __hash__(self) -> int:
        """Returns rule hash based on repr string."""
        return hash(repr(self))
