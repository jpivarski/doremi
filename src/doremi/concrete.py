# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from fractions import Fraction

from dataclasses import dataclass, field

import doremi.abstract


@dataclass
class Note:
    duration: Fraction


@dataclass
class MIDINote(Note):
    pitch: int  # 60 = middle C


@dataclass
class RealNote(Note):
    pitch: float  # Hz
