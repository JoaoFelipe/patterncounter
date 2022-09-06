# PatternCounter

[![PyPI](https://img.shields.io/pypi/v/patterncounter.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/patterncounter.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/patterncounter)][python version]
[![License](https://img.shields.io/pypi/l/patterncounter)][license]

[![Read the documentation at https://patterncounter.readthedocs.io/](https://img.shields.io/readthedocs/patterncounter/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/JoaoFelipe/patterncounter/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/JoaoFelipe/patterncounter/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/patterncounter/
[status]: https://pypi.org/project/patterncounter/
[python version]: https://pypi.org/project/patterncounter
[read the docs]: https://patterncounter.readthedocs.io/
[tests]: https://github.com/JoaoFelipe/patterncounter/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/JoaoFelipe/patterncounter
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

This tool allows to count patterns in lists of sequential groups using [rules](rules.md) and [variables](variables.md).

For the following examples, consider the following file (`sequences.txt`):

```
A -1 -2
B -1 -2
A B -1 -2
A -1 B C -1 -2
B -1 A B -1 A -1 C -1 -2
```

Example 1: Count how many sequences contain both the elements A and B:

```bash
$ patterncounter count "A B" -n -f sequences.txt
Supp((A B)) = 0.6 | 3 lines: 2, 3, 4
```

Example 2: Count how many sequences contain elements A and B at the same group:

```bash
$ patterncounter count "A & B" -n -f sequences.txt
Supp(A & B) = 0.4 | 2 lines: 2, 4
```

Example 3: Count how many sequences have an element B that after after A:

```bash
$ patterncounter count "A -> B" -n -f sequences.txt
Supp(A -> B) = 0.2 | 1 lines: 3
```

Example 4: Count in how many sequences the element B was removed within an interval of A:

```bash
$ patterncounter count "[A OutB]" -n -f sequences.txt
Supp([A OutB]) = 0.2 | 1 lines: 4
```

Example 5: Count in how many sequences there is an element C that occurs after an interval of A:

```bash
$ patterncounter count "[A] -> C" -n -f sequences.txt
Supp([A] -> C) = 0.4 | 2 lines: 3, 4
```

Example 6: Show results even when the pattern does not exist:

```bash
$ patterncounter count "Z" -n -f sequences.txt -z
Supp(Z) = 0.0 | 0 lines
```

In addition to using simple rules, it is possible to define multiple rules and calculated association rules metrics among them:

Example 7: Count both how many sequences have an interval of A, and how many sequences have an interval of A with an element B inside:

```bash
$ patterncounter count "[A]" "[A B]" -n -f sequences.txt
Supp([A], [A B]) = 0.4 | 2 lines: 2, 4
Association Rule: [A] ==> [A B]
  Supp([A]) = 0.8 | 4 lines: 0, 2, 3, 4
  Supp([A B]) = 0.4 | 2 lines: 2, 4
  Conf = 0.5
  Lift = 1.25
Association Rule: [A B] ==> [A]
  Supp([A B]) = 0.4 | 2 lines: 2, 4
  Supp([A]) = 0.8 | 4 lines: 0, 2, 3, 4
  Conf = 1.0
  Lift = 1.25
```

It is also possible to define variables.

Example 8: Count how many sequences have groups with two distinct elements:

```bash
$ patterncounter count "x & y" -v "x" -v "y" -n -f sequences.txt -z
Supp(x & y) = 0.6 | 3 lines: 2, 3, 4

[BINDING: x = B; y = A]
  Supp(B & A) = 0.4 | 2 lines: 2, 4

[BINDING: x = A; y = B]
  Supp(A & B) = 0.4 | 2 lines: 2, 4

[BINDING: x = B; y = C]
  Supp(B & C) = 0.2 | 1 lines: 3

[BINDING: x = A; y = C]
  Supp(A & C) = 0.0 | 0 lines

[BINDING: x = C; y = B]
  Supp(C & B) = 0.2 | 1 lines: 3

[BINDING: x = C; y = A]
  Supp(C & A) = 0.0 | 0 lines
```

Note that the result first shows the combined metrics (union).

Finally, given a file of sequences, it is also possible to select its lines (0-indexes):

```bash
$ patterncounter select -f sequences.txt -n 4
0| A -1 -2
2| A B -1 -2
4| B -1 A B -1 A -1 C -1 -2
```

## Installation

You can install _PatternCounter_ via [pip] from [PyPI]:

```console
$ pip install patterncounter
```

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_PatternCounter_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/JoaoFelipe/patterncounter/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/JoaoFelipe/patterncounter/blob/main/LICENSE
[contributor guide]: https://github.com/JoaoFelipe/patterncounter/blob/main/CONTRIBUTING.md
[command-line reference]: https://patterncounter.readthedocs.io/en/latest/usage.html
