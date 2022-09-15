"""Test cases for the __main__ module."""

import os
from pathlib import Path
from textwrap import dedent

import pytest
from click.testing import CliRunner

from patterncounter import __main__


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner(mix_stderr=True)


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


def test_count_succeeds_single_rule(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count,
        ["X", "-v", "X~A"],
        input="A -1 A B -1 -2 A -1 -2 A B -1 -2",
    )
    assert result.exit_code == 0
    assert result.output == dedent(
        """\
        Supp(X) = 0.6666666666666666

        [BINDING: X = B]
          Supp(B) = 0.6666666666666666
        """
    )


def test_count_succeeds_single_rule_csv(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count,
        ["X", "-v", "X~A", "--csv"],
        input="A -1 A B -1 -2 A -1 -2 A B -1 -2",
    )
    assert result.exit_code == 0
    assert (
        result.output
        == dedent(
            """\
        Name,Support,Lines,Bindings
        X,0.6666666666666666,0; 2,
        B,0.6666666666666666,0; 2,X = B
        """
        )
        .replace("\r\n", "\n")
        .replace("\n", os.linesep)
    )


def test_count_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count,
        ["[Y X]", "A", "-v", "X~A", "-v", "Y:A"],
        input="A -1 A B -1 -2 A -1 -2 A B -1 -2",
    )
    assert result.exit_code == 0
    assert result.output == dedent(
        """\
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
    )


def test_count_succeeds_csv(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count,
        ["[Y X]", "A", "-v", "X~A", "-v", "Y:A", "--csv"],
        input="A -1 A B -1 -2 A -1 -2 A B -1 -2",
    )
    assert result.exit_code == 0
    assert (
        result.output
        == dedent(
            """\
        LHS,RHS,LHS Support,RHS Support,LHS ==> RHS Support,"""
            """Confidence,Lift,LHS Lines,RHS Lines,LHS ==> RHS Lines,Bindings
        [Y X],A,0.6666666666666666,1.0,0.6666666666666666,"""
            """1.0,1.0,0; 2,0; 1; 2,0; 2,
        A,[Y X],1.0,0.6666666666666666,0.6666666666666666,"""
            """0.6666666666666666,1.0,0; 1; 2,0; 2,0; 2,
        [A B],A,0.6666666666666666,1.0,0.6666666666666666,"""
            """1.0,1.0,0; 2,0; 1; 2,0; 2,X = B; Y = A
        A,[A B],1.0,0.6666666666666666,0.6666666666666666,"""
            """0.6666666666666666,1.0,0; 1; 2,0; 2,0; 2,X = B; Y = A
        """
        )
        .replace("\r\n", "\n")
        .replace("\n", os.linesep)
    )


def test_count_succeeds_using_file(tmp_path: Path, runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    filename = tmp_path / "sequences.txt"
    filename.write_text("A -1 A B -1 -2 A -1 -2 A B -1 -2")
    result = runner.invoke(
        __main__.count, ["[Y X]", "A", "-v", "X~A", "-v", "Y:A", "-f", str(filename)]
    )
    assert result.exit_code == 0
    assert result.output == dedent(
        """\
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
    )


def test_count_succeeds_no_bindings(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count,
        ["[Y X]", "A", "-v", "X~A", "-v", "Y:A", "-b"],
        input="A -1 A B -1 -2 A -1 -2 A B -1 -2",
    )
    assert result.exit_code == 0
    assert result.output == dedent(
        """\
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
        """
    )


def test_count_succeeds_single_rule_no_bindings_csv(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count,
        ["X", "-v", "X~A", "-b", "--csv"],
        input="A -1 A B -1 -2 A -1 -2 A B -1 -2",
    )
    assert result.exit_code == 0
    assert (
        result.output
        == dedent(
            """\
        Name,Support,Lines,Bindings
        X,0.6666666666666666,0; 2,
        """
        )
        .replace("\r\n", "\n")
        .replace("\n", os.linesep)
    )


def test_count_succeeds_no_bindings_csv(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count,
        ["[Y X]", "A", "-v", "X~A", "-v", "Y:A", "-b", "--csv"],
        input="A -1 A B -1 -2 A -1 -2 A B -1 -2",
    )
    assert result.exit_code == 0
    assert (
        result.output
        == dedent(
            """\
        LHS,RHS,LHS Support,RHS Support,LHS ==> RHS Support,"""
            """Confidence,Lift,LHS Lines,RHS Lines,LHS ==> RHS Lines,Bindings
        [Y X],A,0.6666666666666666,1.0,0.6666666666666666,"""
            """1.0,1.0,0; 2,0; 1; 2,0; 2,
        A,[Y X],1.0,0.6666666666666666,0.6666666666666666,"""
            """0.6666666666666666,1.0,0; 1; 2,0; 2,0; 2,
        """
        )
        .replace("\r\n", "\n")
        .replace("\n", os.linesep)
    )


def test_count_show_zero_and_lines(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count,
        ["A", "b", "-z", "-t", "-n"],
        input="A -1 A B -1 -2 A -1 -2 A B -1 -2",
    )
    assert result.exit_code == 0
    assert result.output == dedent(
        """\
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
    )


def test_count_show_zero_csv(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count,
        ["A", "b", "-z", "-t", "--csv"],
        input="A -1 A B -1 -2 A -1 -2 A B -1 -2",
    )
    assert result.exit_code == 0
    assert (
        result.output
        == dedent(
            """\
        LHS,RHS,LHS Support,RHS Support,LHS ==> RHS Support,"""
            """Confidence,Lift,LHS Lines,RHS Lines,LHS ==> RHS Lines,Bindings
        A,b,1.0,0.0,0.0,0.0,nan,0; 1; 2,,,
        b,A,0.0,1.0,0.0,nan,nan,,0; 1; 2,,
        """
        )
        .replace("\r\n", "\n")
        .replace("\n", os.linesep)
    )


def test_count_nothing_found(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count, ["Z"], input="A -1 A B -1 -2 A -1 -2 A B -1 -2"
    )
    assert result.exit_code == 0
    assert result.output == ""


def test_count_single_nothing_found_csv(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count, ["Z", "--csv"], input="A -1 A B -1 -2 A -1 -2 A B -1 -2"
    )
    assert result.exit_code == 0
    assert result.output == ("Name,Support,Lines,Bindings\n").replace(
        "\r\n", "\n"
    ).replace("\n", os.linesep)


def test_count_multiple_nothing_found_csv(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        __main__.count, ["Z", "B", "--csv"], input="A -1 A B -1 -2 A -1 -2 A B -1 -2"
    )
    assert result.exit_code == 0
    assert result.output == (
        "LHS,RHS,LHS Support,RHS Support,LHS ==> RHS Support,"
        "Confidence,Lift,LHS Lines,RHS Lines,LHS ==> RHS Lines,Bindings\n"
    ).replace("\r\n", "\n").replace("\n", os.linesep)


def test_convert_items_filtering(runner: CliRunner) -> None:
    """It exist with a status code of zero."""
    result = runner.invoke(
        __main__.convert,
        [],
        input=dedent(
            """\
            @ITEM=1=A
            @ITEM=2=B
            @ITEM=100=OUTA
            @ITEM=200=OUTB
            @ITEM=1000=INA
            @ITEM=2000=INB
            @ITEM=10000=INITA
            @ITEM=20000=INITB
            10000 1000 1 -1 2000 1 2 -1 100 2 -1 -2
            10000 1000 1 -1 -2
            10000 1000 1 20000 2000 2 -1 -2"""
        ),
    )
    assert result.exit_code == 0
    assert result.output == dedent(
        """\
        A -1 A B -1 B -1 -2
        A -1 -2
        A B -1 -2
        """
    )


def test_convert_fails_for_undefined_items(tmp_path: Path, runner: CliRunner) -> None:
    """It exist with a status code of zero."""
    filename = tmp_path / "sequences.txt"
    filename.write_text(
        dedent(
            """\
            @CONVERTED_FROM_TEXT
            @ITEM=1=A
            @ITEM=2=B
            @ITEM=100=OUTA
            @ITEM=200=OUTB
            @ITEM=1000=INA
            @ITEM=2000=INB
            @ITEM=10000=INITA
            @ITEM=20000=INITB
            10000 1000 1 -1 2000 1 2 -1 100 2 -1 -2
            10000 1000 1 3 -1 -2
            10000 1000 1 20000 2000 2 4 -1 -2"""
        )
    )
    result = runner.invoke(__main__.convert, ["-s", "-f", str(filename)])
    assert result.exit_code == 1
    assert result.output == "The following element(s) were not found: 3, 4\n"


def test_show_in_and_out(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.show, [], input="A -1 A B -1 B -1 -2 A -1 -2")
    assert result.exit_code == 0
    assert result.output == dedent(
        """\
        A InA -1 A B InB -1 B OutA -1 -2
        A InA -1 -2
        """
    )
