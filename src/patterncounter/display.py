"""Defines functions for displaying results in a human-readable way."""
from __future__ import annotations

import csv
import sys
from typing import Sequence
from typing import Tuple
from typing import cast

from .counter import AssociationItem
from .counter import AssociationRule
from .counter import Number
from .counter import TPatternList
from .sequences import Config
from .sequences import TSequence
from .sequences import sequence_to_text


def print_support(
    item: AssociationItem,
    sequences: Sequence[TSequence],
    config: Config,
    prefix: str = "",
) -> None:
    """Print support for selected lines."""
    linenums = ""
    if config.show_lines:
        linenums = f" | {len(item.lines)} lines"
        if item.lines:
            linenums += f": {', '.join(map(str, item.lines))}"
    print(f"{prefix}Supp({item.name}) = {item.support}{linenums}")
    if config.show_text:
        for line in item.lines:
            showline = f"{line}: " if config.show_lines else ""
            print(f"{prefix}  {showline}{sequence_to_text(sequences[line], config)}")


def print_rules(
    int_item: AssociationItem,
    association_rules: list[AssociationRule],
    sequences: Sequence[TSequence],
    config: Config,
    prefix: str = "",
) -> None:
    """Print rules together and their possible association rules."""
    if config.hide_support_zero and int_item.support == 0:
        return
    print_support(int_item, sequences, config, prefix=prefix)

    for arule in association_rules:
        print(f"{prefix}Association Rule: {arule.lhs.name} ==> {arule.rhs.name}")
        print_support(arule.lhs, sequences, config, prefix=prefix + "  ")
        print_support(arule.rhs, sequences, config, prefix=prefix + "  ")
        print(f"{prefix}  Conf = {arule.confidence}")
        print(f"{prefix}  Lift = {arule.lift}")


def display_patterns(
    sequences: Sequence[TSequence],
    patterns: TPatternList,
    config: Config | None = None,
    default_prefix: str = "",
) -> None:
    """Displays patterns found by mine_patterns."""
    config = config or Config()
    for item, association_rules, binds in patterns:
        prefix = default_prefix
        if binds:
            if config.hide_bindings:
                continue
            variables = "; ".join(
                f"{var} = {value}"
                for var, value in cast(Sequence[Tuple[str, str]], binds)
            )
            print(f"\n{default_prefix}[BINDING: {variables}]")
            prefix += "  "

        print_rules(item, association_rules, sequences, config, prefix=prefix)


def create_single_row(
    config: Config,
    name: str,
    support: str | Number,
    line_count: str | Number,
    lines: str,
    bindings: str,
    source: str,
) -> list[str | Number]:
    """Create row for patterns csv."""
    row: list[str | Number] = [name, support]
    if config.show_lines:
        row.append(line_count)
    if config.show_text:
        row.append(lines)
    row.append(bindings)
    if source:
        row.append(source)
    return row


def display_single_rule_csv(
    patterns: TPatternList,
    first: bool = True,
    source: str = "",
    config: Config | None = None,
) -> None:
    """Displays patterns of a single rule found by mine_patterns as csv."""
    config = config or Config()
    writer = csv.writer(sys.stdout)
    if first:
        writer.writerow(
            create_single_row(
                config,
                "Name",
                "Support",
                "Line Count",
                "Lines",
                "Bindings",
                "Source" if source else "",
            )
        )
    for item, _, binds in patterns:
        if config.hide_support_zero and item.support == 0:
            continue
        variables = ""
        if binds:
            if config.hide_bindings:
                continue
            variables = "; ".join(
                f"{var} = {value}"
                for var, value in cast(Sequence[Tuple[str, str]], binds)
            )
        writer.writerow(
            create_single_row(
                config,
                item.name,
                item.support,
                len(item.lines),
                "; ".join(map(str, item.lines)),
                variables,
                source,
            )
        )


def create_multiple_row(
    config: Config,
    lhs: str,
    rhs: str,
    lhs_support: str | Number,
    rhs_support: str | Number,
    rule_support: str | Number,
    lhs_line_count: str | Number,
    rhs_line_count: str | Number,
    rule_line_count: str | Number,
    confidence: str | Number,
    lift: str | Number,
    lhs_lines: str,
    rhs_lines: str,
    rule_lines: str,
    bindings: str,
    source: str,
) -> list[str | Number]:
    """Create row for association rules csv."""
    row: list[str | Number] = [lhs, rhs, lhs_support, rhs_support, rule_support]
    if config.show_lines:
        row += [lhs_line_count, rhs_line_count, rule_line_count]
    row += [confidence, lift]
    if config.show_text:
        row += [lhs_lines, rhs_lines, rule_lines]
    row.append(bindings)
    if source:
        row.append(source)
    return row


def display_multiple_rule_csv(
    patterns: TPatternList,
    first: bool = True,
    source: str = "",
    config: Config | None = None,
) -> None:
    """Displays patterns of multiple rules found by mine_patterns as csv."""
    config = config or Config()
    writer = csv.writer(sys.stdout)
    if first:
        writer.writerow(
            create_multiple_row(
                config,
                "LHS",
                "RHS",
                "LHS Support",
                "RHS Support",
                "LHS ==> RHS Support",
                "LHS Line Count",
                "RHS Line Count",
                "LHS ==> RHS Line Count",
                "Confidence",
                "Lift",
                "LHS Lines",
                "RHS Lines",
                "LHS ==> RHS Lines",
                "Bindings",
                "Source" if source else "",
            )
        )
    for item, association_rules, binds in patterns:
        if config.hide_support_zero and item.support == 0:
            continue
        variables = ""
        if binds:
            if config.hide_bindings:
                continue
            variables = "; ".join(
                f"{var} = {value}"
                for var, value in cast(Sequence[Tuple[str, str]], binds)
            )
        for arule in association_rules:
            writer.writerow(
                create_multiple_row(
                    config,
                    arule.lhs.name,
                    arule.rhs.name,
                    arule.lhs.support,
                    arule.rhs.support,
                    item.support,
                    len(arule.lhs.lines),
                    len(arule.rhs.lines),
                    len(item.lines),
                    arule.confidence,
                    arule.lift,
                    "; ".join(map(str, arule.lhs.lines)),
                    "; ".join(map(str, arule.rhs.lines)),
                    "; ".join(map(str, item.lines)),
                    variables,
                    source,
                )
            )
