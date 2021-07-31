# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

import csv
import math
import numbers
import pkg_resources
import re
import sys

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Set, Tuple, Dict, Mapping, Optional, Union, TextIO, Callable

import lark

import doremi.abstract


class Note:
    pass


@dataclass
class RealNote(Note):
    frequency: float  # Hz

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Note):
            return self.frequency == other.frequency
        else:
            return False

    def octaves_difference(self, other: Note) -> int:
        return int(math.floor(other.frequency / self.frequency))

    def same_pitch_class(self, other: Note) -> bool:
        ratio = self.frequency / other.frequency
        return 2 ** math.log2(ratio) == ratio

    def with_octave(self, octave: int) -> Note:
        return RealNote(self.frequency * (2 ** octave))

    def with_augmentation(
        self, augmentation: doremi.abstract.Augmentation, scale: "Scale"
    ) -> Note:
        if isinstance(augmentation, doremi.abstract.AugmentStep):
            return RealNote(self.frequency * 2 ** (augmentation.amount / 12.0))

        elif isinstance(augmentation, doremi.abstract.AugmentDegree):
            scale_notes = list(scale.notes.values())
            for i, note in enumerate(scale_notes):
                if self.same_pitch_class(note):
                    octaves = note.octaves_difference(self)
                    more_octaves = (i + augmentation.amount) // len(scale_notes)
                    out = scale_notes[(i + augmentation.amount) % len(scale_notes)]
                    return out.with_octave(octaves + more_octaves)
            else:
                raise doremi.abstract.NoteNotInScale(augmentation.parsingtree)

        elif isinstance(augmentation, doremi.abstract.AugmentRatio):
            return RealNote(self.frequency * float(augmentation.amount))

        else:
            raise AssertionError(repr(augmentation))


@dataclass
class MIDINote(Note):
    pitch: int  # 60 = C4 (middle C)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MIDINote):
            return self.pitch == other.pitch
        elif isinstance(other, Note):
            return self.frequency == other.frequency
        else:
            return False

    @property
    def frequency(self) -> float:
        # https://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies
        return 440.0 * 2.0 ** ((self.pitch - 69) / 12.0)

    def octaves_difference(self, other: Note) -> int:
        if isinstance(other, MIDINote):
            return (other.pitch - self.pitch) // 12
        else:
            return int(math.floor(other.frequency / self.frequency))

    def same_pitch_class(self, other: Note) -> bool:
        if isinstance(other, MIDINote):
            return abs(self.pitch - other.pitch) % 12 == 0
        else:
            ratio = self.frequency / other.frequency
            return 2 ** math.log2(ratio) == ratio

    def with_octave(self, octave: int) -> Note:
        out = MIDINote(self.pitch + (12 * octave))
        if 0 <= out.pitch < 128:
            return out
        else:
            return RealNote(out.frequency)

    def with_augmentation(
        self, augmentation: doremi.abstract.Augmentation, scale: "Scale"
    ) -> Note:
        if isinstance(augmentation, doremi.abstract.AugmentStep):
            return MIDINote(self.pitch + augmentation.amount)

        elif isinstance(augmentation, doremi.abstract.AugmentDegree):
            scale_notes = list(scale.notes.values())
            for i, note in enumerate(scale_notes):
                if self.same_pitch_class(note):
                    octaves = note.octaves_difference(self)
                    more_octaves = (i + augmentation.amount) // len(scale_notes)
                    out = scale_notes[(i + augmentation.amount) % len(scale_notes)]
                    return out.with_octave(octaves + more_octaves)
            else:
                raise doremi.abstract.NoteNotInScale(augmentation.parsingtree)

        elif isinstance(augmentation, doremi.abstract.AugmentRatio):
            return RealNote(self.frequency * float(augmentation.amount))

        else:
            raise AssertionError(repr(augmentation))


@dataclass
class TimedNote:
    note: Note
    start: float  # real time in seconds
    stop: float  # real time in seconds
    emphasis: float  # 1.0 for maximum emphasis; no notes are at 0.0

    @property
    def duration(self):
        return self.stop - self.start


cardinal = re.compile("^([1-9][0-9]*)th$")


@dataclass
class Scale:
    notes: Dict[str, Note]
    accidentals: Dict[str, Note]
    name: Optional[str] = field(default=None, repr=False, compare=False, hash=False)
    tonic: Optional[str] = field(default=None, repr=False, compare=False, hash=False)

    def __getitem__(self, symbol: str) -> Note:
        degree = None
        if symbol == "1st":
            degree = 0
        elif symbol == "2nd":
            degree = 1
        elif symbol == "3rd":
            degree = 2
        m = cardinal.match(symbol)
        if m is not None:
            degree = int(m.group(1)) - 1

        if degree is not None:
            if degree >= len(self.notes):
                if isinstance(symbol, lark.lexer.Token):
                    raise doremi.abstract.UndefinedSymbol(symbol)
                else:
                    raise KeyError(f"symbol not found in scale: {symbol!r}")
            else:
                return list(self.notes.values())[degree]

        out = self.notes.get(symbol)
        if out is None:
            out = self.accidentals.get(symbol)
        if out is None:
            if isinstance(symbol, lark.lexer.Token):
                raise doremi.abstract.UndefinedSymbol(symbol)
            else:
                raise KeyError(f"symbol not found in scale: {symbol!r}")
        else:
            return out

    def __repr__(self) -> str:
        accidentals = ""
        if len(self.accidentals) > 0:
            accidentals = " (including " + " ".join(self.accidentals) + ")"

        # relies on dict-ordering (Python 3.6+)
        items = iter(self.notes.items())
        first_symbol, first_note = next(items)

        if all(isinstance(note, MIDINote) for _, note in self.notes.items()):
            diffs = {
                note.pitch - first_note.pitch: symbol
                for symbol, note in self.notes.items()
            }

            empty = "-" * min(len(symbol) for symbol in self.notes)
            if self.tonic is None:
                strings = [f"{first_symbol}({first_note.frequency} Hz)"]
            else:
                strings = [f"{first_symbol}({self.tonic})"]
            for i in range(1, len(solfedge)):
                if i in diffs:
                    strings.append(diffs[i])
                else:
                    strings.append(empty)

        else:
            base_frequency = first_note.frequency
            strings = [f"{first_symbol}({base_frequency:.3g} Hz)"]
            for symbol, note in items:
                ratio = note.frequency / base_frequency
                as_fraction = Fraction.from_float(ratio).limit_denominator(100)
                if 0.99 < ratio / as_fraction < 1.01:
                    strings.append(f"{symbol}({str(as_fraction)})")
                else:
                    strings.append(f"{symbol}({note.frequency} Hz)")

        return f"<Scale {self.name!r} {' '.join(strings)}{accidentals}>"


MakeScale = Mapping[str, Union[numbers.Real, str]]
AnyScale = Union[Scale, str, MakeScale]


@dataclass
class Composition:
    scale: Scale
    bpm: float
    num_beats: float
    scope: doremi.abstract.Scope
    abstract_collection: doremi.abstract.Collection
    abstract_notes: List[doremi.abstract.AbstractNote]

    def __repr__(self):
        scale = ""
        if self.scale.name is not None:
            scale = f" in {self.scale.name!r}"
        return f"<Composition{scale} {self.bpm} bpm ({len(self.abstract_notes)} notes)>"

    @property
    def beat_in_seconds(self) -> float:
        return 60.0 / self.bpm

    @property
    def duration_in_seconds(self) -> float:
        return self.num_beats * self.beat_in_seconds

    def notes(
        self,
        scale: Optional[AnyScale] = None,
        bpm: Optional[float] = None,
        emphasis_scaling: Callable[[int, int], float] = (
            lambda single, maximum: (single + 1) / (maximum + 1)
        ),
    ) -> List[TimedNote]:

        if scale is None:
            scale = self.scale
        else:
            scale = doremi.concrete.get_scale(scale)

        if bpm is None:
            bpm = self.bpm

        beat_in_seconds = 60.0 / bpm

        max_emphasis = max(x.emphasis for x in self.abstract_notes)

        notes = []
        for abstract_note in self.abstract_notes:
            try:
                note = scale[abstract_note.word.val]
            except doremi.abstract.DoremiError as err:
                err.context = self.abstract_collection.source
                raise

            if abstract_note.octave != 0:
                note = note.with_octave(abstract_note.octave)

            if len(abstract_note.augmentations) != 0:
                for augmentation in abstract_note.augmentations[::-1]:
                    note = note.with_augmentation(augmentation, scale)

            notes.append(
                TimedNote(
                    note,
                    0.5 * abstract_note.start * beat_in_seconds,
                    0.5 * abstract_note.stop * beat_in_seconds,
                    emphasis_scaling(abstract_note.emphasis, max_emphasis),
                )
            )

        return notes

    def midi_events(
        self,
        scale: Optional[AnyScale] = None,
        bpm: Optional[float] = None,
    ) -> List[Tuple[float, List[Tuple[int, int]]]]:

        notes = self.notes(scale, bpm)
        if not all(isinstance(note.note, MIDINote) for note in notes):
            raise ValueError(
                "midi_events can only be called if all notes are MIDINotes"
            )
        notes.sort(key=lambda note: note.start)

        events = []
        state = [0.0] * 128
        i = 0
        while i < len(notes):
            start = notes[i].start
            same_start = []
            while i < len(notes) and notes[i].start == start:
                same_start.append(notes[i])
                i += 1

            to_stop = [
                (stop, pitch)
                for pitch, stop in enumerate(state)
                if stop != 0.0 and stop <= start
            ]
            to_stop.sort()
            last_stop = None
            for stop, pitch in to_stop:
                if last_stop != stop:
                    events.append((stop, []))
                events[-1][1].append((pitch, 0))  # turn note off
                state[pitch] = 0.0
                last_stop = stop

            changes = []
            for note in same_start:
                pitch = note.note.pitch
                emphasis = int(math.ceil(note.emphasis * 127))
                if state[pitch] == 0.0:
                    changes.append((pitch, emphasis))  # turn note on
                    state[pitch] = note.stop
                else:
                    changes.append((pitch, 0))  # turn it off just before
                    changes.append((pitch, emphasis))  # turning it on again
                    if state[pitch] < note.stop:
                        state[pitch] = note.stop  # longest note wins

            if len(events) != 0 and events[-1][0] == start:
                events[-1][1].extend(changes)
            else:
                events.append((start, changes))

        to_stop = [(stop, pitch) for pitch, stop in enumerate(state) if stop != 0.0]
        to_stop.sort()

        last_stop = None
        for stop, pitch in to_stop:
            if last_stop != stop:
                events.append((stop, []))
            events[-1][1].append((pitch, 0))  # turn note off
            state[pitch] = 0.0
            last_stop = stop

        return events

    def fluidsynth(
        self,
        scale: Optional[AnyScale] = None,
        bpm: Optional[float] = None,
        soundfont: Optional[str] = None,
        sample_rate: int = 44100,
        dtype: object = "i2",
    ):
        import doremi.synthesizer

        events = self.midi_events(scale, bpm)

        fluidsynth = doremi.synthesizer.Fluidsynth(soundfont, sample_rate, dtype)

        try:
            array = fluidsynth.midi_synthesize(events)
        finally:
            fluidsynth.delete()

        return array

    def play(
        self,
        scale: Optional[AnyScale] = None,
        bpm: Optional[float] = None,
        soundfont: Optional[str] = None,
        sample_rate: int = 44100,
    ):
        import IPython.display

        array = self.fluidsynth(scale, bpm, soundfont, sample_rate)
        return IPython.display.Audio(array.sum(axis=1) // 2, rate=sample_rate)

    def show_notes(
        self,
        lines_per_beat: float = 1.0,
        stream: TextIO = sys.stdout,
        scale: Optional[AnyScale] = None,
        bpm: Optional[float] = None,
    ):
        if bpm is None:
            bpm = self.bpm
        notes = self.notes(scale, bpm)

        if all(isinstance(note.note, MIDINote) for note in notes):
            min_pitch = min(note.note.pitch for note in notes) - 2
            max_pitch = max(note.note.pitch for note in notes) + 3

            if min_pitch < 21 or max_pitch > 127:
                raise NotImplementedError

            print(
                "".join(
                    x.ljust(3) for x in names_flat[min_pitch - 21 : max_pitch - 21]
                ),
                file=stream,
            )
            print(
                "".join(
                    x.ljust(3) for x in names_sharp[min_pitch - 21 : max_pitch - 21]
                ),
                file=stream,
            )

            num_timesteps = int(math.ceil(self.num_beats * lines_per_beat))
            scale_factor = 60.0 / bpm

            for timestep in range(num_timesteps):
                chars = ["   " for i in range(max_pitch - min_pitch)]

                tlo, thi = timestep * scale_factor, (timestep + 1) * scale_factor
                start = [note for note in notes if tlo <= note.start < thi]
                going = [
                    note for note in notes if note.start < tlo and note.stop >= thi
                ]

                for note in going:
                    chars[note.note.pitch - min_pitch] = " | "
                for note in start:
                    chars[note.note.pitch - min_pitch] = " x "
                print("".join(chars), file=stream)

        else:
            raise NotImplementedError


names_flat = (
    ["", "Bb0", "", ""]
    + ["Db", "", "Eb", "", "", "Gb", "", "Ab", "", "Bb", "", ""]
    + ["Db", "", "Eb", "", "", "Gb", "", "Ab", "", "Bb", "", ""]
    + ["Db", "", "Eb", "", "", "Gb", "", "Ab", "", "Bb", "", ""]
    + ["Db", "", "Eb", "", "", "Gb", "", "Ab", "", "Bb", "", ""]
    + ["Db", "", "Eb", "", "", "Gb", "", "Ab", "", "Bb", "", ""]
    + ["Db", "", "Eb", "", "", "Gb", "", "Ab", "", "Bb", "", ""]
    + ["Db", "", "Eb", "", "", "Gb", "", "Ab", "", "Bb", "", ""]
    + ["Db", "", "Eb", "", "", "Gb", "", "Ab", "", "Bb", "", ""]
    + ["Db", "", "Eb", "", "", "Gb", ""]
)

names_sharp = (
    ["A0", "A#", "B0"]
    + ["C1", "C#", "D1", "D#", "E1", "F1", "F#", "G1", "G#", "A1", "A#", "B1"]
    + ["C2", "C#", "D2", "D#", "E2", "F2", "F#", "G2", "G#", "A2", "A#", "B2"]
    + ["C3", "C#", "D3", "D#", "E3", "F3", "F#", "G3", "G#", "A3", "A#", "B3"]
    + ["C4", "C#", "D4", "D#", "E4", "F4", "F#", "G4", "G#", "A4", "A#", "B4"]
    + ["C5", "C#", "D5", "D#", "E5", "F5", "F#", "G5", "G#", "A5", "A#", "B5"]
    + ["C6", "C#", "D6", "D#", "E6", "F6", "F#", "G6", "G#", "A6", "A#", "B6"]
    + ["C7", "C#", "D7", "D#", "E7", "F7", "F#", "G7", "G#", "A7", "A#", "B7"]
    + ["C8", "C#", "D8", "D#", "E8", "F8", "F#", "G8", "G#", "A8", "A#", "B8"]
    + ["C9", "C#", "D9", "D#", "E9", "F9", "F#", "G9"]
)

notes: Dict[str, MIDINote] = {}
for i in range(128):
    notes[str(i)] = MIDINote(i)

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


def make_scale(source: MakeScale, name: Optional[str] = None) -> Scale:
    included_notes: List[Tuple[str, Note]] = []
    for k, v in source.items():
        if doremi.abstract.is_rest(k):
            raise ValueError("symbols must not consist entirely of underscores (rest)")

        if isinstance(v, numbers.Real):
            if v <= 0:
                raise ValueError("note frequencies (in Hz) must be positive: {v!r}")
            included_notes.append((k, RealNote(value)))

        elif v in notes:
            included_notes.append((k, notes[v]))

        else:
            raise ValueError(f"unrecognized note specification for scale: {v!r}")

    included_notes.sort(key=lambda pair: pair[1].frequency)
    return Scale(dict(included_notes), {}, name)


# https://en.wikipedia.org/wiki/Solf%C3%A8ge#Movable_do_solf%C3%A8ge
solfedge = [
    "do",  # 0 half-steps above do (major)
    "ra",  # 1 half-steps above do
    "re",  # 2 half-steps above do (major)
    "me",  # 3 half-steps above do
    "mi",  # 4 half-steps above do (major)
    "fa",  # 5 half-steps above do (major)
    "se",  # 6 half-steps above do
    "so",  # 7 half-steps above do (major)
    "le",  # 8 half-steps above do
    "la",  # 9 half-steps above do (major)
    "te",  # 10 half-steps above do
    "ti",  # 11 half-steps above do (major)
]


def named_scale(name: str, accidentals: bool = True) -> Scale:
    lowered_name = name.lower()

    if lowered_name not in named_scale.cache:
        included = []
        excluded = []

        m = named_scale.base_name.match(lowered_name)
        if m is not None:
            tonic, accidental, mode = m.groups()
            if tonic is None:
                tonic = "C"
            if accidental is None:
                accidental = ""

            if mode == "major" or mode == "maj":
                mode = "ionian"
            elif mode == "minor" or mode == "min":
                mode = "aeolian"

            try:
                base_pitch = notes[tonic[0] + accidental + "3"].pitch
            except KeyError:
                raise ValueError(
                    f"unrecognized note name: {tonic[0].capitalize() + accidental}"
                )

            pitches = named_scale.data.get(mode)
            if pitches is not None:
                for i, x in enumerate(solfedge):
                    if i in pitches:
                        included.append((x, str(base_pitch + i)))
                    else:
                        excluded.append((x, str(base_pitch + i)))

            else:
                raise ValueError(
                    f"unrecognized mode name: {mode} (modes are single words, not hyphenated)"
                )

        else:
            raise ValueError(
                f'unrecognized scale name: {name} (must be like "C# minor", with a space between starting pitch, if present, and mode name)'
            )

        named_scale.cache[lowered_name] = (
            make_scale(dict(included)).notes,
            make_scale(dict(excluded)).notes,
            tonic[0].capitalize() + accidental,
        )

    included_notes, excluded_notes, tonic = named_scale.cache[lowered_name]
    if not accidentals:
        excluded_notes = {}
    return Scale(included_notes, excluded_notes, name, tonic)


named_scale.cache: Dict[str, Tuple[Dict[str, Note], Dict[str, Note], str]] = {}
named_scale.base_name = re.compile(r"^\s*([a-g](\#|b)?\s+)?([a-z]+)\s*$")

# https://allthescales.org/downloads.php
allthescales = pkg_resources.resource_filename("doremi", "data/scale-list.csv")
named_scale.data: Dict[str, Set[int]] = {}
with open(allthescales) as file:
    reader = csv.reader(file)
    next(reader)  # skip header
    for row in reader:
        full = [0]
        for x in row[3].strip()[:-1]:
            full.append(full[-1] + int(x))
        named_scale.data[row[2].lower()] = set(full)


def get_scale(source: AnyScale) -> Scale:
    if isinstance(source, Scale):
        return source
    elif isinstance(source, str):
        return named_scale(source)
    else:
        return make_scale(source)
