# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from ._version import version as __version__

from typing import Optional

import doremi.parsing
import doremi.abstract
import doremi.concrete


def compose(
    source: str,
    scale: doremi.concrete.AnyScale = "C major",
    bpm: float = 120.0,
    scope: Optional[doremi.abstract.Scope] = None,
) -> doremi.concrete.Composition:

    scale = doremi.concrete.get_scale(scale)
    abstract_collection = doremi.abstract.abstracttree(source)
    num_beats, abstract_notes, scope = abstract_collection.evaluate(scope)

    return doremi.concrete.Composition(
        scale, bpm, num_beats, scope, abstract_collection, abstract_notes
    )


__all__ = (
    "__version__", "compose")
