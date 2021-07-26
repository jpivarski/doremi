# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

import math
import pkg_resources
import csv
import re

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Mapping, Optional, Union

import doremi.abstract


@dataclass
class Note:
    duration: Fraction


@dataclass
class Rest(Note):
    pass


@dataclass
class RealNote(Note):
    pitch: float  # Hz

    @property
    def frequency(self) -> float:
        return self.pitch

    def same_pitch_class(self, other: Note) -> bool:
        ratio = self.frequency / other.frequency
        return 2 ** math.log2(ratio) == ratio


@dataclass
class MIDINote(Note):
    pitch: int  # 60 = C4 (middle C)

    @property
    def frequency(self) -> float:
        # https://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies
        return 440.0 * 2.0 ** ((self.pitch - 69) / 12.0)

    def same_pitch_class(self, other: Note) -> bool:
        if isinstance(other, MIDINote):
            return abs(self.pitch - other.pitch) % 12 == 0
        else:
            ratio = self.frequency / other.frequency
            return 2 ** math.log2(ratio) == ratio


@dataclass
class Voice:
    notes: List[Note]


@dataclass
class Fragment:
    voices: List[Voice]


@dataclass
class Vocabulary:
    symbols: Dict[str, Fragment]


@dataclass
class Scale(Vocabulary):
    degrees: List[Note]


@dataclass
class Derived:
    parent: Vocabulary


def make_notes(
    source: Mapping[str, Union[None, float, str]], parent: Optional[Vocabulary] = None
) -> Vocabulary:
    symbols = {}
    for key, value in source.items():
        if value is None:
            symbols[key] = Fragment([Voice([Rest(Fraction(1, 1))])])

        elif isinstance(value, float):
            if value <= 0:
                raise ValueError("note frequencies (in Hz) must be positive")
            symbols[key] = Fragment([Voice([RealNote(Fraction(1, 1), value)])])

        elif value in notes:
            tmp = symbols[key] = Fragment([Voice([notes[value]])])

        else:
            raise ValueError(f"unrecognized note specification for scale: {value!r}")

    if parent is None:
        return Vocabulary(symbols)
    else:
        return Derived(symbols, parent)


def make_scale(source: Mapping[str, Union[None, float, str]]) -> Scale:
    symbols = make_notes(source).symbols
    frequencies = [
        (fragment.voices[0].notes[0].frequency, fragment.voices[0].notes[0])
        for key, fragment in symbols.items()
        if isinstance(fragment.voices[0].notes[0], (RealNote, MIDINote))
    ]
    frequencies.sort()
    return Scale(symbols, [note for _, note in frequencies])


notes: Dict[str, MIDINote] = {}
for i in range(128):
    notes[str(i)] = MIDINote(Fraction(1, 1), i)

# http://www.music.mcgill.ca/~ich/classes/mumt306/StandardMIDIfileformat.html
notes["A0"] = notes["a0"] = notes["21"]
notes["A#0"] = notes["a#0"] = notes["Bb0"] = notes["bb0"] = notes["22"]
notes["B0"] = notes["b0"] = notes["23"]
notes["C1"] = notes["c1"] = notes["24"]
notes["C#1"] = notes["c#1"] = notes["Db1"] = notes["db1"] = notes["25"]
notes["D1"] = notes["d1"] = notes["26"]
notes["D#1"] = notes["d#1"] = notes["Eb1"] = notes["eb1"] = notes["27"]
notes["E1"] = notes["e1"] = notes["28"]
notes["F1"] = notes["f1"] = notes["29"]
notes["F#1"] = notes["f#1"] = notes["Gb1"] = notes["gb1"] = notes["30"]
notes["G1"] = notes["g1"] = notes["31"]
notes["G#1"] = notes["g#1"] = notes["Ab1"] = notes["ab1"] = notes["32"]
notes["A1"] = notes["a1"] = notes["33"]
notes["A#1"] = notes["a#1"] = notes["Bb1"] = notes["bb1"] = notes["34"]
notes["B1"] = notes["b1"] = notes["35"]
notes["C2"] = notes["c2"] = notes["36"]
notes["C#2"] = notes["c#2"] = notes["Db2"] = notes["db2"] = notes["37"]
notes["D2"] = notes["d2"] = notes["38"]
notes["D#2"] = notes["d#2"] = notes["Eb2"] = notes["eb2"] = notes["39"]
notes["E2"] = notes["e2"] = notes["40"]
notes["F2"] = notes["f2"] = notes["41"]
notes["F#2"] = notes["f#2"] = notes["Gb2"] = notes["gb2"] = notes["42"]
notes["G2"] = notes["g2"] = notes["43"]
notes["G#2"] = notes["g#2"] = notes["Ab2"] = notes["ab2"] = notes["44"]
notes["A2"] = notes["a2"] = notes["45"]
notes["A#2"] = notes["a#2"] = notes["Bb2"] = notes["bb2"] = notes["46"]
notes["B2"] = notes["b2"] = notes["47"]
notes["C3"] = notes["c3"] = notes["48"]
notes["C#3"] = notes["c#3"] = notes["Db3"] = notes["db3"] = notes["49"]
notes["D3"] = notes["d3"] = notes["50"]
notes["D#3"] = notes["d#3"] = notes["Eb3"] = notes["eb3"] = notes["51"]
notes["E3"] = notes["e3"] = notes["52"]
notes["F3"] = notes["f3"] = notes["53"]
notes["F#3"] = notes["f#3"] = notes["Gb3"] = notes["gb3"] = notes["54"]
notes["G3"] = notes["g3"] = notes["55"]
notes["G#3"] = notes["g#3"] = notes["Ab3"] = notes["ab3"] = notes["56"]
notes["A3"] = notes["a3"] = notes["57"]
notes["A#3"] = notes["a#3"] = notes["Bb3"] = notes["bb3"] = notes["58"]
notes["B3"] = notes["b3"] = notes["59"]
notes["C4"] = notes["c4"] = notes["60"]
notes["C#4"] = notes["c#4"] = notes["Db4"] = notes["db4"] = notes["61"]
notes["D4"] = notes["d4"] = notes["62"]
notes["D#4"] = notes["d#4"] = notes["Eb4"] = notes["eb4"] = notes["63"]
notes["E4"] = notes["e4"] = notes["64"]
notes["F4"] = notes["f4"] = notes["65"]
notes["F#4"] = notes["f#4"] = notes["Gb4"] = notes["gb4"] = notes["66"]
notes["G4"] = notes["g4"] = notes["67"]
notes["G#4"] = notes["g#4"] = notes["Ab4"] = notes["ab4"] = notes["68"]
notes["A4"] = notes["a4"] = notes["69"]
notes["A#4"] = notes["a#4"] = notes["Bb4"] = notes["bb4"] = notes["70"]
notes["B4"] = notes["b4"] = notes["71"]
notes["C5"] = notes["c5"] = notes["72"]
notes["C#5"] = notes["c#5"] = notes["Db5"] = notes["db5"] = notes["73"]
notes["D5"] = notes["d5"] = notes["74"]
notes["D#5"] = notes["d#5"] = notes["Eb5"] = notes["eb5"] = notes["75"]
notes["E5"] = notes["e5"] = notes["76"]
notes["F5"] = notes["f5"] = notes["77"]
notes["F#5"] = notes["f#5"] = notes["Gb5"] = notes["gb5"] = notes["78"]
notes["G5"] = notes["g5"] = notes["79"]
notes["G#5"] = notes["g#5"] = notes["Ab5"] = notes["ab5"] = notes["80"]
notes["A5"] = notes["a5"] = notes["81"]
notes["A#5"] = notes["a#5"] = notes["Bb5"] = notes["bb5"] = notes["82"]
notes["B5"] = notes["b5"] = notes["83"]
notes["C6"] = notes["c6"] = notes["84"]
notes["C#6"] = notes["c#6"] = notes["Db6"] = notes["db6"] = notes["85"]
notes["D6"] = notes["d6"] = notes["86"]
notes["D#6"] = notes["d#6"] = notes["Eb6"] = notes["eb6"] = notes["87"]
notes["E6"] = notes["e6"] = notes["88"]
notes["F6"] = notes["f6"] = notes["89"]
notes["F#6"] = notes["f#6"] = notes["Gb6"] = notes["gb6"] = notes["90"]
notes["G6"] = notes["g6"] = notes["91"]
notes["G#6"] = notes["g#6"] = notes["Ab6"] = notes["ab6"] = notes["92"]
notes["A6"] = notes["a6"] = notes["93"]
notes["A#6"] = notes["a#6"] = notes["Bb6"] = notes["bb6"] = notes["94"]
notes["B6"] = notes["b6"] = notes["95"]
notes["C7"] = notes["c7"] = notes["96"]
notes["C#7"] = notes["c#7"] = notes["Db7"] = notes["db7"] = notes["97"]
notes["D7"] = notes["d7"] = notes["98"]
notes["D#7"] = notes["d#7"] = notes["Eb7"] = notes["eb7"] = notes["99"]
notes["E7"] = notes["e7"] = notes["100"]
notes["F7"] = notes["f7"] = notes["101"]
notes["F#7"] = notes["f#7"] = notes["Gb7"] = notes["gb7"] = notes["102"]
notes["G7"] = notes["g7"] = notes["103"]
notes["G#7"] = notes["g#7"] = notes["Ab7"] = notes["ab7"] = notes["104"]
notes["A7"] = notes["a7"] = notes["105"]
notes["A#7"] = notes["a#7"] = notes["Bb7"] = notes["bb7"] = notes["106"]
notes["B7"] = notes["b7"] = notes["107"]
notes["C8"] = notes["c8"] = notes["108"]
notes["C#8"] = notes["c#8"] = notes["Db8"] = notes["db8"] = notes["109"]
notes["D8"] = notes["d8"] = notes["110"]
notes["D#8"] = notes["d#8"] = notes["Eb8"] = notes["eb8"] = notes["111"]
notes["E8"] = notes["e8"] = notes["112"]
notes["F8"] = notes["f8"] = notes["113"]
notes["F#8"] = notes["f#8"] = notes["Gb8"] = notes["gb8"] = notes["114"]
notes["G8"] = notes["g8"] = notes["115"]
notes["G#8"] = notes["g#8"] = notes["Ab8"] = notes["ab8"] = notes["116"]
notes["A8"] = notes["a8"] = notes["117"]
notes["A#8"] = notes["a#8"] = notes["Bb8"] = notes["bb8"] = notes["118"]
notes["B8"] = notes["b8"] = notes["119"]
notes["C9"] = notes["c9"] = notes["120"]
notes["C#9"] = notes["c#9"] = notes["Db9"] = notes["db9"] = notes["121"]
notes["D9"] = notes["d9"] = notes["122"]
notes["D#9"] = notes["d#9"] = notes["Eb9"] = notes["eb9"] = notes["123"]
notes["E9"] = notes["e9"] = notes["124"]
notes["F9"] = notes["f9"] = notes["125"]
notes["F#9"] = notes["f#9"] = notes["Gb9"] = notes["gb9"] = notes["126"]
notes["G9"] = notes["g9"] = notes["127"]


# https://en.wikipedia.org/wiki/Solf%C3%A8ge#Movable_do_solf%C3%A8ge
solfedge = [
    "do",   # 0 half-steps above do (major)
    "ra",   # 1 half-steps above do
    "re",   # 2 half-steps above do (major)
    "me",   # 3 half-steps above do
    "mi",   # 4 half-steps above do (major)
    "fa",   # 5 half-steps above do (major)
    "se",   # 6 half-steps above do
    "so",   # 7 half-steps above do (major)
    "le",   # 8 half-steps above do
    "la",   # 9 half-steps above do (major)
    "te",   # 10 half-steps above do
    "ti",   # 11 half-steps above do (major)
]


def get_scale(name: str) -> Scale:
    lowered_name = name.lower()

    if lowered_name not in get_scale.scales:

        m = get_scale.tonic_name.match(lowered_name)
        if m is not None:
            tonic, accidental, mode = m.groups()
            if tonic is None:
                tonic = "c"
            if accidental is None:
                accidental = ""

            base_pitch = notes[tonic[0] + "4" + accidental].pitch
            keys = []
            pitches = []

            # https://allthescales.org/downloads.php
            allthescales = pkg_resources.resource_filename("doremi", "data/scale-list.csv")
            for row in csv.reader(open(allthescales)):
                if row[2].lower() == mode:
                    relative = 0
                    for step in [int(x) for x in row[3].strip()]:
                        print(relative)
                        pitches.append(base_pitch + relative)
                        relative += step

                    break
            else:
                raise ValueError(f"unrecognized mode name: {mode} (modes are single words, not hyphenated)")

        else:
            raise ValueError(f"scale name pattern must be like \"C# minor\", not {name}")

        print(keys)
        print(pitches)

        raise Exception

    return get_scale.scales[lowered_name]


get_scale.scales: Dict[str, Scale] = {}
get_scale.tonic_name = re.compile(r"^\s*([a-g](\#|b)?\s+)?([a-z]+)\s*$")
