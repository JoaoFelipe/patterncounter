"""Command-line interface."""
from __future__ import annotations

import sys
from typing import IO
from typing import Sequence

import click

from .counter import extract_metrics
from .display import display_patterns
from .parser import parse
from .sequences import Config
from .sequences import text_to_sequences


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
    "--line-number", "-n", is_flag=True, default=False, help="show line numbers"
)
@click.option("--line-text", "-t", is_flag=True, default=False, help="show line text")
@click.option("--file", "-f", type=click.File("r"), help="load input from file")
@click.option("--var", "-v", help="variable", multiple=True)
@click.argument("rules", nargs=-1)
def count(
    line_sep: str,
    interval_sep: str,
    element_sep: str,
    in_prefix: str,
    out_prefix: str,
    show_support_zero: bool,
    line_number: bool,
    line_text: bool,
    file: IO[str] | None,
    var: Sequence[str],
    rules: Sequence[str],
) -> None:
    """Count patterns in file."""
    if file is None:
        file = sys.stdin
    text = file.read()

    config = Config(
        in_prefix=in_prefix,
        out_prefix=out_prefix,
        linesep=line_sep,
        intervalsep=interval_sep,
        elementsep=element_sep,
        hide_support_zero=not show_support_zero,
        show_lines=line_number,
        show_text=line_text,
    )

    sequences = text_to_sequences(text, config)
    parsed_rules = [parse(rule) for rule in rules]
    result, bindings = extract_metrics(
        sequences, parsed_rules, var, in_prefix, out_prefix
    )
    display_patterns(sequences, parsed_rules, result, bindings, config)


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
    if file is None:
        file = sys.stdin
    text = file.read()
    lines = [lin for line in lines if (lin := line.strip(","))]

    length = max(len(line) for line in lines)
    file_lines = text.split(line_sep)
    for line in lines:
        number = ""
        if line_number:
            number = f"{line: <{length}}| "
        text = file_lines[int(line)].lstrip()
        click.echo(f"{number}{text}{line_sep}")


if __name__ == "__main__":
    main(prog_name="patterncounter")  # pragma: no cover
