"""Defines functions for displaying results in a human-readable way."""
from __future__ import annotations

from itertools import combinations
from typing import Collection
from typing import Generator
from typing import Sequence
from typing import Tuple
from typing import TypeVar
from typing import Union
from typing import cast

from patterncounter.operators import Rule

from .counter import Bindings
from .counter import TRuleResult
from .counter import Unbound
from .sequences import Config
from .sequences import TSequence
from .sequences import sequence_to_text


Number = Union[int, float]


def divide(left: Number, right: Number) -> Number:
    """Divides numbers and return nan on division by zero."""
    try:
        return left / right
    except ZeroDivisionError:
        return float("nan")


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


def print_support(
    name: str,
    lines: Collection[int],
    sequences: Sequence[TSequence],
    config: Config,
    prefix: str = "",
) -> Number:
    """Print support for selected lines."""
    linenums = ""
    if config.show_lines:
        linenums = f" | {len(lines)} lines"
        if lines:
            linenums += f": {', '.join(map(str, lines))}"
    support = len(lines) / len(sequences)
    print(f"{prefix}Supp({name}) = {support}{linenums}")
    if config.show_text:
        for line in lines:
            showline = f"{line}: " if config.show_lines else ""
            print(f"{prefix}  {showline}{sequence_to_text(sequences[line], config)}")
    return support


def print_rules(
    sequences: Sequence[TSequence],
    rules: Sequence[Rule],
    result: TRuleResult,
    config: Config,
    prefix: str = "",
) -> None:
    """Print rules together and their possible association rules."""
    lines = set.intersection(*[result[rule] for rule in rules])
    if len(lines) == 0 and config.hide_support_zero:
        return
    int_sup = print_support(
        ", ".join(map(str, rules)), lines, sequences, config, prefix=prefix
    )

    for lhs, rhs in split_rules(rules):
        lines_lhs = set.intersection(*[result[rule] for rule in lhs])
        lines_rhs = set.intersection(*[result[rule] for rule in rhs])
        name_lhs = ", ".join(map(str, lhs))
        name_rhs = ", ".join(map(str, rhs))
        print(f"{prefix}Association Rule: {name_lhs} ==> {name_rhs}")
        lhs_sup = print_support(
            name_lhs, lines_lhs, sequences, config, prefix=prefix + "  "
        )
        rhs_sup = print_support(
            name_rhs, lines_rhs, sequences, config, prefix=prefix + "  "
        )
        conf = divide(int_sup, lhs_sup)
        lift = divide(conf, rhs_sup)
        print(f"{prefix}  Conf = {conf}")
        print(f"{prefix}  Lift = {lift}")


def display_patterns(
    sequences: Sequence[TSequence],
    rules: list[Rule],
    result: TRuleResult,
    bindings: Bindings,
    config: Config | None = None,
) -> None:
    """Displays patterns found by extract_metrics."""
    config = config or Config()
    print_rules(sequences, rules, result, config)

    for binds, replacements in bindings.enacted.items():
        if any(isinstance(bind, Unbound) for bind in binds):
            continue
        variables = "; ".join(
            f"{var} = {value}" for var, value in cast(Sequence[Tuple[str, str]], binds)
        )
        print(f"\n[BINDING: {variables}]")
        new_rules: list[Rule] = rules[:]
        for old, new in replacements:
            new_rules[rules.index(old)] = new
        print_rules(sequences, new_rules, result, config, prefix="  ")
