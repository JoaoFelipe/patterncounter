"""Test cases for the __main__ module."""
from pathlib import Path

import pytest
from click.testing import CliRunner

from patterncounter import __main__


EXPECTED_OUTPUT_1 = """\
Supp([Y X], A) = 0.6666666666666666
Association Rule: [Y X] ==> A
  Supp([Y X]) = 0.6666666666666666
  Supp(A) = 1.0
  Conf = 1.0
  Lift = 1.0
Association Rule: A ==> [Y X]
  Supp(A) = 1.0
  Supp([Y X]) = 0.6666666666666666
  Conf = 0.6666666666666666
  Lift = 1.0

[BINDING: X = B; Y = A]
  Supp([A B], A) = 0.6666666666666666
  Association Rule: [A B] ==> A
    Supp([A B]) = 0.6666666666666666
    Supp(A) = 1.0
    Conf = 1.0
    Lift = 1.0
  Association Rule: A ==> [A B]
    Supp(A) = 1.0
    Supp([A B]) = 0.6666666666666666
    Conf = 0.6666666666666666
    Lift = 1.0
"""

EXPECTED_OUTPUT_2 = """\
Supp(A, b) = 0.0 | 0 lines
Association Rule: A ==> b
  Supp(A) = 1.0 | 3 lines: 0, 1, 2
    0: A -1 A B -1 -2
    1: A -1 -2
    2: A B -1 -2
  Supp(b) = 0.0 | 0 lines
  Conf = 0.0
  Lift = nan
Association Rule: b ==> A
  Supp(b) = 0.0 | 0 lines
  Supp(A) = 1.0 | 3 lines: 0, 1, 2
    0: A -1 A B -1 -2
    1: A -1 -2
    2: A B -1 -2
  Conf = nan
  Lift = nan
"""


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main)
    assert result.exit_code == 0


def test_select_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.select, ["1", "2"], input="a -1 -2 b -1 -2 c -1 -2 d -1 -2"
    )
    assert result.exit_code == 0
    assert result.output == "b -1 -2\nc -1 -2\n"


def test_select_succeeds_with_file(tmp_path: Path, runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    filename = tmp_path / "sequences.txt"
    filename.write_text("a -1 -2 b -1 -2 c -1 -2 d -1 -2")
    result = runner.invoke(__main__.select, ["1", "2", "-f", str(filename), "-n"])
    assert result.exit_code == 0
    assert result.output == "1| b -1 -2\n2| c -1 -2\n"


def test_count_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count,
        ["[Y X]", "A", "-v", "X~A", "-v", "Y:A"],
        input="A -1 A B -1 -2 A -1 -2 A B -1 -2",
    )
    assert result.exit_code == 0
    assert result.output == EXPECTED_OUTPUT_1


def test_count_succeeds_using_file(tmp_path: Path, runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    filename = tmp_path / "sequences.txt"
    filename.write_text("A -1 A B -1 -2 A -1 -2 A B -1 -2")
    result = runner.invoke(
        __main__.count, ["[Y X]", "A", "-v", "X~A", "-v", "Y:A", "-f", str(filename)]
    )
    assert result.exit_code == 0
    assert result.output == EXPECTED_OUTPUT_1


def test_count_show_zero_and_lines(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count,
        ["A", "b", "-z", "-t", "-n"],
        input="A -1 A B -1 -2 A -1 -2 A B -1 -2",
    )
    assert result.exit_code == 0
    assert result.output == EXPECTED_OUTPUT_2


def test_count_nothing_found(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count, ["Z"], input="A -1 A B -1 -2 A -1 -2 A B -1 -2"
    )
    assert result.exit_code == 0
    assert result.output == ""
