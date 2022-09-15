"""Command-line interface."""
from __future__ import annotations

import sys
from typing import IO
from typing import Sequence

import click

from .counter import create_in_out_sequences
from .counter import extract_metrics
from .counter import mine_patterns
from .display import display_multiple_rule_csv
from .display import display_patterns
from .display import display_single_rule_csv
from .parser import parse
from .sequences import Config
from .sequences import convert_sequences
from .sequences import sequence_to_text
from .sequences import text_to_sequences


def file_or_stdin(file: IO[str] | None) -> str:
    """Returns file text or stdin."""
    if file is None:
        file = sys.stdin
    return file.read()


@click.group()
@click.version_option()
def main() -> None:
    """PatternCounter. This tool counts patterns from lists of sequences."""


@main.command()
@click.option("--line-sep", "-l", default="-2", help="line separator")
@click.option("--interval-sep", "-i", default="-1", help="interval separator")
@click.option("--element-sep", "-e", default=" ", help="element separator")
@click.option(
    "--in-prefix",
    default="In",
    help="prefix that is added to elements when they enter a slice",
)
@click.option(
    "--out-prefix",
    default="Out",
    help="prefix that is added to elements when they exit a slice",
)
@click.option(
    "--show-support-zero",
    "-z",
    is_flag=True,
    default=False,
    help="show rule when support is zero",
)
@click.option(
    "--hide-bindings",
    "-b",
    is_flag=True,
    default=False,
    help="hide bindings",
)
@click.option(
    "--line-number", "-n", is_flag=True, default=False, help="show line numbers"
)
@click.option("--line-text", "-t", is_flag=True, default=False, help="show line text")
@click.option("--file", "-f", type=click.File("r"), help="load input from file")
@click.option("--var", "-v", help="variable", multiple=True)
@click.option("--csv", "-c", is_flag=True, default=False, help="display result as csv")
@click.argument("rules", nargs=-1)
def count(
    line_sep: str,
    interval_sep: str,
    element_sep: str,
    in_prefix: str,
    out_prefix: str,
    show_support_zero: bool,
    hide_bindings: bool,
    line_number: bool,
    line_text: bool,
    file: IO[str] | None,
    var: Sequence[str],
    rules: Sequence[str],
    csv: bool,
) -> None:
    """Count patterns in file."""
    text = file_or_stdin(file)

    config = Config(
        in_prefix=in_prefix,
        out_prefix=out_prefix,
        linesep=line_sep,
        intervalsep=interval_sep,
        elementsep=element_sep,
        hide_support_zero=not show_support_zero,
        show_lines=line_number,
        show_text=line_text,
        hide_bindings=hide_bindings,
    )

    sequences = text_to_sequences(text, config)
    parsed_rules = [parse(rule) for rule in rules]
    result, bindings = extract_metrics(
        sequences, parsed_rules, var, in_prefix, out_prefix
    )
    patterns = mine_patterns(sequences, parsed_rules, result, bindings)
    if not csv:
        display_patterns(sequences, patterns, config)
    elif len(parsed_rules) == 1:
        display_single_rule_csv(patterns, config)
    else:
        display_multiple_rule_csv(patterns, config)


@main.command()
@click.option("--line-sep", "-l", default="-2", help="line separator")
@click.option("--file", "-f", type=click.File("r"), help="load input from file")
@click.option(
    "--line-number", "-n", is_flag=True, default=False, help="show line numbers"
)
@click.argument("lines", nargs=-1)
def select(
    line_sep: str, file: IO[str] | None, line_number: bool, lines: list[str]
) -> None:
    """Select lines from file."""
    text = file_or_stdin(file)
    lines = [lin for line in lines if (lin := line.strip(","))]

    length = max(len(line) for line in lines)
    file_lines = text.split(line_sep)
    for line in lines:
        number = ""
        if line_number:
            number = f"{line: <{length}}| "
        text = file_lines[int(line)].lstrip()
        click.echo(f"{number}{text}{line_sep}")


@main.command()
@click.option("--line-sep", "-l", default="-2", help="line separator")
@click.option("--interval-sep", "-i", default="-1", help="interval separator")
@click.option("--element-sep", "-e", default=" ", help="element separator")
@click.option(
    "--remove",
    "-r",
    default=("IN", "OUT", "INIT"),
    help="remove elements that start with prefix",
    multiple=True,
)
@click.option("--file", "-f", type=click.File("r"), help="load input from file")
@click.option(
    "--stop-on-failures", "-s", is_flag=True, default=False, help="stop on failures"
)
def convert(
    line_sep: str,
    interval_sep: str,
    element_sep: str,
    remove: Sequence[str],
    file: IO[str] | None,
    stop_on_failures: bool,
) -> None:
    """Convert spmf dictionary to sequence list."""
    text = file_or_stdin(file)

    special: list[str] = []
    lines: list[str] = []
    for line in text.split("\n"):
        line = line.strip()
        (special if line.startswith("@") else lines).append(line)
    text = "\n".join(lines)

    conversions = {}
    for line in special:
        if line.upper().startswith("@ITEM"):
            _, num, name = line.split("=")
            conversions[num] = name

    config = Config(linesep=line_sep, intervalsep=interval_sep, elementsep=element_sep)

    sequences = text_to_sequences(text, config)
    new_sequences, failures = convert_sequences(sequences, conversions, remove)
    if stop_on_failures and failures:
        print("The following element(s) were not found: " + ", ".join(failures))
        sys.exit(1)

    for sequence in new_sequences:
        print(f"{sequence_to_text(sequence, config)}")


@main.command()
@click.option("--line-sep", "-l", default="-2", help="line separator")
@click.option("--interval-sep", "-i", default="-1", help="interval separator")
@click.option("--element-sep", "-e", default=" ", help="element separator")
@click.option(
    "--in-prefix",
    default="In",
    help="prefix that is added to elements when they enter a slice",
)
@click.option(
    "--out-prefix",
    default="Out",
    help="prefix that is added to elements when they exit a slice",
)
@click.option(
    "--line-number", "-n", is_flag=True, default=False, help="show line numbers"
)
@click.option("--file", "-f", type=click.File("r"), help="load input from file")
def show(
    line_sep: str,
    interval_sep: str,
    element_sep: str,
    in_prefix: str,
    out_prefix: str,
    line_number: bool,
    file: IO[str] | None,
) -> None:
    """Show sequence list with In and Out."""
    text = file_or_stdin(file)

    config = Config(
        in_prefix=in_prefix,
        out_prefix=out_prefix,
        linesep=line_sep,
        intervalsep=interval_sep,
        elementsep=element_sep,
        show_lines=line_number,
    )

    sequences = text_to_sequences(text, config)
    new_sequences, _ = create_in_out_sequences(sequences, in_prefix, out_prefix)
    for line, sequence, _ in new_sequences:
        showline = f"{line}: " if config.show_lines else ""
        print(f"{showline}{sequence_to_text(sequence, config)}")


if __name__ == "__main__":
    main(prog_name="patterncounter")  # pragma: no cover
