"""Defines operations related to sequences."""

from copy import deepcopy
from dataclasses import dataclass
from typing import List
from typing import Set
from typing import Tuple
from typing import Union


TSequence = List[List[str]]


@dataclass
class Config:
    """Class for configuring pattern counter."""

    in_prefix: str = "In"
    out_prefix: str = "Out"
    show_lines: bool = True
    show_text: bool = False
    linesep: str = "-2"
    intervalsep: str = "-1"
    elementsep: str = " "
    hide_support_zero: bool = True


def strip_split(text: str, sep: str) -> List[str]:
    """Splits text using separator.

    Removes separator from end of text.
    """
    return text.strip().rstrip(sep).strip().split(sep)


def text_to_sequences(text: str, config: Union[Config, None] = None) -> List[TSequence]:
    """Converts text file to sequence."""
    config = config or Config()
    lines: List[TSequence] = []
    for line in strip_split(text, config.linesep):
        newline: TSequence = []
        lines.append(newline)
        for group in strip_split(line, config.intervalsep):
            newgroup: List[str] = []
            newline.append(newgroup)
            for element in strip_split(group, config.elementsep):
                if element:
                    newgroup.append(element)
    return lines


def in_out_sequence(
    sequence: TSequence, in_prefix: str = "In", out_prefix: str = "Out"
) -> Tuple[TSequence, Set[str]]:
    """Adds In and Out elements to sequence."""
    newsequence = deepcopy(sequence)
    all_names: Set[str] = set()
    current: Set[str] = set()
    for interval in newsequence:
        elements = set(interval)
        all_names |= elements
        if in_prefix:
            new_elements = elements - current
            for element in new_elements:
                interval.append(in_prefix + element)
        if out_prefix:
            removed_elements = current - elements
            for element in removed_elements:
                interval.append(out_prefix + element)
        current = elements
    return newsequence, all_names


def sequence_to_text(sequence: TSequence, config: Config) -> str:
    """Converts sequence to text."""
    return (
        f" {config.intervalsep} ".join(
            [config.elementsep.join(group) for group in sequence]
        )
        + f" {config.intervalsep} {config.linesep}"
    )
