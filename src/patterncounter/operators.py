"Defines operators for finding patterns"
from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import List, Generator, Tuple
from itertools import product

class Rule(metaclass=ABCMeta):
    """Base operator with Python operator overloads"""

    @abstractmethod
    def find_positions(self, sequence: List[List[str]], start: int=0) -> Generator[Tuple[int, int], None, None]:
        """Generates position for matching elements"""
        pass

    def check(self, sequence: List[List[str]]) -> bool:
        """Checks if operator matches a pattern"""
        for _ in self.find_positions(sequence):
            return True
        return False

    def __and__(self, other: Rule) -> And:
        return And(self, other)
    
    def __or__(self, other: Rule) -> Or:
        return Or(self, other)
    
    def __invert__(self) -> Not:
        return Not(self)
    
    def __xor__(self, other: Rule) -> Intersect:
        return Intersect(self, other)

    def __rshift__(self, other: Rule) -> Sequence:
        return Sequence(self, other)


class Slice(Rule):
    """Slice operator for finding a slice of sequential elements"""

    def __init__(self, element: str, open_first: bool=False, open_last: bool=False):
        self.element = element
        self.subrules: List[Rule] = []
        self.open_first = int(open_first)
        self.open_last = int(open_last) 
        
    def find_positions(self, sequence: List[List[str]], start: int=0) -> Generator[Tuple[int, int], None, None]:
        first = None
        for i, moment in enumerate(sequence):
            if first is None and self.element in moment:
                first = i
            elif first is not None and self.element not in moment:
                if all(rule.check(sequence[first + self.open_first:i - self.open_last]) for rule in self.subrules):
                    yield (first + start, i - 1 + start)
                first = None
        if first is not None:
            if all(rule.check(sequence[first + self.open_first:-self.open_last or None]) for rule in self.subrules):
                yield (first + start, len(sequence) -1 + start)
            
    def __lshift__(self, other: Rule) -> Slice:
        self.subrules.append(other)
        return self
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Slice) and (self.element, self.subrules, self.open_first, self.open_last) == (other.element, other.subrules, other.open_first, other.open_last)


class Has(Rule):
    """Has operator for finding elements in the sequence"""
    def __init__(self, element: str):
        self.element = element
        
    def find_positions(self, sequence: List[List[str]], start: int=0) -> Generator[Tuple[int, int], None, None]:
        for i, moment in enumerate(sequence):
            if self.element in moment:
                yield (i + start, i + start)
                
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Has) and self.element == other.element


class Sequence(Rule):
    """Sequence operator for finding sequences of rules"""
    def __init__(self, *rules: Rule, same: bool=False):
        self.rules = rules
        self.same = same
    
    def find_positions(self, sequence: List[List[str]], start: int=0) -> Generator[Tuple[int, int], None, None]:
        rule_pos = [
            rule.find_positions(sequence, start)
            for rule in self.rules
        ]
        for positions in product(*rule_pos):
            it = iter(positions)
            next(it)
            for first, second in zip(positions, it):
                if first[-1] >= second[0] and (not self.same or first[-1] > second[0]):
                    break
            else:
                yield (positions[0][0], positions[-1][-1])

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Sequence) and (self.rules, self.same) == (other.rules, other.same)

               
class And(Rule):
    """And operator for combining rules"""
    
    def __init__(self, *rules: Rule):
        self.rules = rules
        
    def find_positions(self, sequence: List[List[str]], start: int=0) -> Generator[Tuple[int, int], None, None]:
        rule_pos = [
            list(rule.find_positions(sequence, start))
            for rule in self.rules
        ]
        if all(rule_pos):
            minimum = min(pos[0] for rule in rule_pos for pos in rule)
            maximum = max(pos[-1] for rule in rule_pos for pos in rule)
            yield (minimum, maximum)
        
    def __eq__(self, other: object) -> bool:
        return isinstance(other, And) and self.rules == other.rules


class Or(Rule):
    """Or operator for combining rules"""

    def __init__(self, *rules: Rule):
        self.rules = rules
        
    def find_positions(self, sequence: List[List[str]], start: int=0) -> Generator[Tuple[int, int], None, None]:
        rule_pos = [
            list(rule.find_positions(sequence, start))
            for rule in self.rules
        ]
        if any(rule_pos):
            minimum = min(pos[0] for rule in rule_pos for pos in rule)
            maximum = max(pos[-1] for rule in rule_pos for pos in rule)
            yield (minimum, maximum)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Or) and self.rules == other.rules

        
class Not(Rule):
    """Not operator for inverting rules"""

    def __init__(self, rule: Rule):
        self.rule = rule
        
    def find_positions(self, sequence: List[List[str]], start: int=0) -> Generator[Tuple[int, int], None, None]:
        for _ in self.rule.find_positions(sequence, start):
            return
        yield (start, len(sequence) + start - 1)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Not) and self.rule == other.rule


class Intersect(Rule):
    """Intersect operator for intersecting rules"""

    def __init__(self, *rules: Rule):
        self.rules = rules
        
    def find_positions(self, sequence: List[List[str]], start: int=0) -> Generator[Tuple[int, int], None, None]:
        rule_pos = [
            list(rule.find_positions(sequence, start))
            for rule in self.rules
        ]
        for positions in product(*rule_pos):
            sets = [set(range(pos[0], pos[-1] + 1)) for pos in positions]
            inter = sorted(list(set.intersection(*sets)))
            if not inter:
                continue
            it = iter(inter)
            start = last = next(it)
            for element in it:
                if element != last + 1:
                    yield (start, last)
                    start = element
                last = element
            yield (start, last)
            
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Intersect) and self.rules == other.rules


class First(Rule):
    """First operator for checking if rule appears in the first position of sequence"""

    def __init__(self, rule: Rule):
        self.rule = rule
        
    def find_positions(self, sequence: List[List[str]], start: int=0) -> Generator[Tuple[int, int], None, None]:
        for pos in self.rule.find_positions(sequence, start):
            if pos[0] == start:
                yield pos
                
    def __eq__(self, other: object) -> bool:
        return isinstance(other, First) and self.rule == other.rule


class Last(Rule):
    """Last operator to check if rule appears in the last position of sequence"""
    def __init__(self, rule: Rule):
        self.rule = rule
        
    def find_positions(self, sequence: List[List[str]], start: int=0) -> Generator[Tuple[int, int], None, None]:
        for pos in self.rule.find_positions(sequence, start):
            if pos[-1] == len(sequence) + start - 1:
                yield pos

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Last) and self.rule == other.rule
