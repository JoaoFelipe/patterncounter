"""Defines operators for finding patterns."""
from __future__ import annotations

from abc import ABCMeta
from abc import abstractmethod
from itertools import product
from typing import Generator


class Rule(metaclass=ABCMeta):
    """Base operator with Python operator overloads."""

    @abstractmethod
    def find_positions(
        self, sequence: list[list[str]], start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""

    def check(self, sequence: list[list[str]]) -> bool:
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
        self, sequence: list[list[str]], start: int = 0
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


class Has(Rule):
    """Has operator for finding elements in the sequence."""

    def __init__(self, element: str):
        """Initializes Has."""
        self.element = element

    def find_positions(
        self, sequence: list[list[str]], start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        for i, moment in enumerate(sequence):
            if self.element in moment:
                yield (i + start, i + start)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Has) and self.element == other.element


class Sequence(Rule):
    """Sequence operator for finding sequences of rules."""

    def __init__(self, *rules: Rule, same: bool = False):
        """Initializes Sequence."""
        self.rules = rules
        self.same = same

    def find_positions(
        self, sequence: list[list[str]], start: int = 0
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

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Sequence) and (self.rules, self.same) == (
            other.rules,
            other.same,
        )


class And(Rule):
    """And operator for combining rules."""

    def __init__(self, *rules: Rule):
        """Initializes And."""
        self.rules = rules

    def find_positions(
        self, sequence: list[list[str]], start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        rule_pos = [list(rule.find_positions(sequence, start)) for rule in self.rules]
        if all(rule_pos):
            minimum = min(pos[0] for rule in rule_pos for pos in rule)
            maximum = max(pos[-1] for rule in rule_pos for pos in rule)
            yield (minimum, maximum)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, And) and self.rules == other.rules


class Or(Rule):
    """Or operator for combining rules."""

    def __init__(self, *rules: Rule):
        """Initializes Or."""
        self.rules = rules

    def find_positions(
        self, sequence: list[list[str]], start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        rule_pos = [list(rule.find_positions(sequence, start)) for rule in self.rules]
        if any(rule_pos):
            minimum = min(pos[0] for rule in rule_pos for pos in rule)
            maximum = max(pos[-1] for rule in rule_pos for pos in rule)
            yield (minimum, maximum)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Or) and self.rules == other.rules


class Not(Rule):
    """Not operator for inverting rules."""

    def __init__(self, rule: Rule):
        """Initializes Not."""
        self.rule = rule

    def find_positions(
        self, sequence: list[list[str]], start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        for _ in self.rule.find_positions(sequence, start):
            return
        yield (start, len(sequence) + start - 1)

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Not) and self.rule == other.rule


class Intersect(Rule):
    """Intersect operator for intersecting rules."""

    def __init__(self, *rules: Rule):
        """Initializes Intersect."""
        self.rules = rules

    def find_positions(
        self, sequence: list[list[str]], start: int = 0
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

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Intersect) and self.rules == other.rules


class First(Rule):
    """First operator for checking if rule appears in the first position of sequence."""

    def __init__(self, rule: Rule):
        """Initializes First."""
        self.rule = rule

    def find_positions(
        self, sequence: list[list[str]], start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        for pos in self.rule.find_positions(sequence, start):
            if pos[0] == start:
                yield pos

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, First) and self.rule == other.rule


class Last(Rule):
    """Last operator to check if rule appears in the last position of sequence."""

    def __init__(self, rule: Rule):
        """Initializes Last."""
        self.rule = rule

    def find_positions(
        self, sequence: list[list[str]], start: int = 0
    ) -> Generator[tuple[int, int], None, None]:
        """Generates position for matching elements."""
        for pos in self.rule.find_positions(sequence, start):
            if pos[-1] == len(sequence) + start - 1:
                yield pos

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Last) and self.rule == other.rule
