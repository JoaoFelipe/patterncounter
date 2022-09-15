"""Main counter. Counts patterns from sequence."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from itertools import product
from typing import Any
from typing import Callable
from typing import Collection
from typing import Dict
from typing import Generator
from typing import List
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import TypeVar
from typing import Union
from typing import cast

from .operators import Rule
from .sequences import TSequence
from .sequences import in_out_sequence
from .visitor import ReplaceVariables
from .visitor import create_replace


def possible_bindings(variable: str, all_names: set[str]) -> tuple[str, set[str]]:
    """Finds possible bindings for variable based on all names that exist in db."""
    if ":" in variable:
        varname, values = variable.split(":")
        user_input = {value.strip() for value in values.split(",")}
        return varname, user_input & all_names
    elif "~" in variable:
        varname, values = variable.split("~")
        user_input = {value.strip() for value in values.split(",")}
        return varname, all_names - user_input
    else:
        return variable, all_names


def create_in_out_sequences(
    sequences: Sequence[TSequence], in_prefix: str, out_prefix: str
) -> tuple[Sequence[tuple[int, TSequence, set[str]]], set[str]]:
    """Transforms list of sequences into a list with In and Out prefixes."""
    all_names = set()
    new_sequences = []
    for i, seq in enumerate(sequences):
        new_seq, names = in_out_sequence(seq, in_prefix, out_prefix)
        all_names |= names
        new_sequences.append((i, new_seq, names))
    return new_sequences, all_names


class Unbound:
    """Represents an unbound variable."""

    def __getitem__(self, index: int) -> Unbound | int:
        """Item accessor. Returns itself in pos 0 or a unique number in pos 1."""
        return cast(Sequence[Union[Unbound, int]], [self, id(self)])[index]

    def __hash__(self) -> int:
        """Same hash as True."""
        return hash(True)

    def __eq__(self, other: object) -> bool:
        """Equals to any other Unbound instance."""
        return isinstance(other, Unbound)


TBinding = Union[Tuple[str, str], Unbound]
TBindingSeq = Sequence[TBinding]
TEnacted = Dict[TBindingSeq, Sequence[Tuple[Rule, Rule]]]
TBackref = Dict[Rule, Set[Rule]]
TForwardref = Dict[Tuple[Rule, TBindingSeq], Rule]


class Bindings:
    """Stores bindings created during extract_metrics application."""

    def __init__(
        self,
        variables: Sequence[str],
        all_names: set[str],
        enacted: TEnacted | None = None,
        backref: TBackref | None = None,
        forwardref: TForwardref | None = None,
        unique: bool = True,
        in_prefix: str = "In",
        out_prefix: str = "Out",
    ):
        """Initializes bindings store."""
        self.all_bindings = dict(
            [possible_bindings(var, all_names) for var in variables]
        )
        self.enacted = enacted or {}
        self.backref = backref or defaultdict(set)
        self.forwardref = forwardref or {}
        self.unique = unique
        self.in_prefix = in_prefix
        self.out_prefix = out_prefix

    def sequence_bindings(
        self, sequence_names: set[str], rules: Sequence[Rule]
    ) -> Generator[tuple[Rule, Rule], None, None]:
        """Generates rule replaces for a given sequence/line."""
        binding_options: Sequence[TBindingSeq] = [
            [(var, bind) for bind in varnames & sequence_names] or [Unbound()]
            for var, varnames in self.all_bindings.items()
        ]
        if not binding_options:
            return

        for bindings in product(*binding_options):
            if self.unique and len({bind[-1] for bind in bindings}) != len(bindings):
                continue
            replacements = self.enacted.get(bindings)
            if not replacements:
                replaces: dict[str, str] = {}
                for old, new in bindings:
                    if isinstance(old, Unbound):
                        continue
                    create_replace(
                        replaces,
                        old,
                        new,
                        in_prefix=self.in_prefix,
                        out_prefix=self.out_prefix,
                    )
                transformer = ReplaceVariables(replaces)
                replacements = []
                for rule in rules:
                    new_rule = transformer.visit(rule)
                    if new_rule != rule:
                        replacements.append((rule, new_rule))
                        self.forwardref[(rule, bindings)] = new_rule
                        self.backref[new_rule].add(rule)
                self.enacted[bindings] = replacements
            yield from replacements

    def __eq__(self, other: object) -> bool:
        """Checks equality."""
        return isinstance(other, Bindings) and (
            self.all_bindings,
            self.enacted,
            self.backref,
            self.forwardref,
            self.unique,
            self.in_prefix,
            self.out_prefix,
        ) == (
            other.all_bindings,
            other.enacted,
            other.backref,
            other.forwardref,
            other.unique,
            other.in_prefix,
            other.out_prefix,
        )


TRuleResult = Dict[Rule, Set[int]]


def extract_metrics(
    sequences: Sequence[TSequence],
    original_rules: Sequence[Rule],
    variables: Sequence[str] | None = None,
    in_prefix: str = "In",
    out_prefix: str = "Out",
    progress: Callable[[Any], Any] = lambda x: x,
) -> tuple[TRuleResult, Bindings]:
    """Find patterns in sequences using the defined rules and variables."""
    variables = variables or []
    new_sequences, all_names = create_in_out_sequences(sequences, in_prefix, out_prefix)

    bindings = Bindings(
        variables, all_names, in_prefix=in_prefix, out_prefix=out_prefix
    )

    rule_result: TRuleResult = defaultdict(set)
    for rule in original_rules:
        rule_result[rule]

    for i, seq, names in progress(new_sequences):
        rules = set(original_rules)
        for old_rule, new_rule in bindings.sequence_bindings(names, original_rules):
            if old_rule in rules:
                rules.remove(old_rule)
            rules.add(new_rule)
            rule_result[new_rule]

        for rule in rules:
            if rule.check(seq):
                rule_result[rule].add(i)
                for old_rule in bindings.backref[rule]:
                    rule_result[old_rule].add(i)
    return rule_result, bindings


Number = Union[int, float]


@dataclass
class AssociationItem:
    """Represents an Association Rule side."""

    name: str
    lines: Collection[int]
    support: Number


@dataclass
class AssociationRule:
    """Represents an Association Rule."""

    lhs: AssociationItem
    rhs: AssociationItem
    confidence: Number
    lift: Number


TPatternList = List[Tuple[AssociationItem, List[AssociationRule], TBindingSeq]]
T = TypeVar("T")


def split_rules(
    rules: Sequence[T],
) -> Generator[tuple[Sequence[T], Sequence[T]], None, None]:
    """Generates all possibilities of lhs -> rhs for list of rules."""
    all_indexes = range(len(rules))
    for size in range(1, len(rules)):
        for indexes in combinations(all_indexes, size):
            lhs = [rules[i] for i in all_indexes if i in indexes]
            rhs = [rules[i] for i in all_indexes if i not in indexes]
            yield (lhs, rhs)


def divide(left: Number, right: Number) -> Number:
    """Divides numbers and return nan on division by zero."""
    try:
        return left / right
    except ZeroDivisionError:
        return float("nan")


def mine_rules(
    sequences: Sequence[TSequence],
    rules: Sequence[Rule],
    result: TRuleResult,
) -> tuple[AssociationItem, list[AssociationRule]]:
    """Mines rules and association rules from result."""
    lines = set.intersection(*[result[rule] for rule in rules])
    int_item = AssociationItem(
        ", ".join(map(str, rules)), lines, len(lines) / len(sequences)
    )
    association_rules = []

    for lhs, rhs in split_rules(rules):
        lines_lhs = set.intersection(*[result[rule] for rule in lhs])
        lines_rhs = set.intersection(*[result[rule] for rule in rhs])
        lhs_item = AssociationItem(
            ", ".join(map(str, lhs)), lines_lhs, len(lines_lhs) / len(sequences)
        )
        rhs_item = AssociationItem(
            ", ".join(map(str, rhs)), lines_rhs, len(lines_rhs) / len(sequences)
        )
        conf = divide(int_item.support, lhs_item.support)
        lift = divide(conf, rhs_item.support)
        association_rules.append(AssociationRule(lhs_item, rhs_item, conf, lift))

    return int_item, association_rules


def mine_patterns(
    sequences: Sequence[TSequence],
    rules: list[Rule],
    result: TRuleResult,
    bindings: Bindings,
) -> TPatternList:
    """Mines patterns from rules and results."""
    item, association_rules = mine_rules(sequences, rules, result)
    patterns: TPatternList = [(item, association_rules, [])]

    for binds, replacements in bindings.enacted.items():
        if any(isinstance(bind, Unbound) for bind in binds):
            continue
        new_rules: list[Rule] = rules[:]
        for old, new in replacements:
            new_rules[rules.index(old)] = new
        item, association_rules = mine_rules(sequences, new_rules, result)
        patterns.append((item, association_rules, binds))
    return patterns
