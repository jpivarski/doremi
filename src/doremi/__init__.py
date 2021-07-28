# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from ._version import version as __version__

import doremi.parsing
import doremi.abstract
import doremi.concrete

from doremi.concrete import (
    Note,
    RealNote,
    MIDINote,
    TimedNote,
    Scale,
    get_scale,
    Composition,
    compose,
    make_scale,
    named_scale,
    get_scale,
)

__all__ = (
    "__version__",
    "Note",
    "RealNote",
    "MIDINote",
    "TimedNote",
    "Scale",
    "get_scale",
    "Composition",
    "compose",
    "make_scale",
    "named_scale",
    "get_scale",
)
