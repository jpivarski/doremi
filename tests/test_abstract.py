# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from lark.tree import Tree
from lark.lexer import Token

from doremi.abstract import (
    Word,
    AugmentStep,
    AugmentDegree,
    AugmentRatio,
    Ratio,
    Duration,
    Group,
    Line,
    Passage,
    Passages,
    abstracttree,
)


def test_decorations():
    aug = AugmentStep(0)
    dur = Duration(Ratio(1, 1))

    assert abstracttree("la") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, aug, dur)])])]
    )
    assert abstracttree("@la") == Passages(
        [Passage([Line([Group(Word("la"), 1, 0, aug, dur)])])]
    )
    assert abstracttree("@ @ la") == Passages(
        [Passage([Line([Group(Word("la"), 2, 0, aug, dur)])])]
    )

    assert abstracttree(">la") == Passages(
        [Passage([Line([Group(Word("la"), 0, 1, aug, dur)])])]
    )
    assert abstracttree("<<la") == Passages(
        [Passage([Line([Group(Word("la"), 0, -2, aug, dur)])])]
    )
    assert abstracttree("3>la") == Passages(
        [Passage([Line([Group(Word("la"), 0, 3, aug, dur)])])]
    )
    assert abstracttree("3< la") == Passages(
        [Passage([Line([Group(Word("la"), 0, -3, aug, dur)])])]
    )

    assert abstracttree("la+") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentStep(1), dur)])])]
    )
    assert abstracttree("la + +") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentStep(2), dur)])])]
    )
    assert abstracttree("la+2") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentStep(2), dur)])])]
    )
    assert abstracttree("la-2") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentStep(-2), dur)])])]
    )
    assert abstracttree("la- 3") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentStep(-3), dur)])])]
    )

    assert abstracttree("la>") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentDegree(1), dur)])])]
    )
    assert abstracttree("la > >") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentDegree(2), dur)])])]
    )
    assert abstracttree("la>2") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentDegree(2), dur)])])]
    )
    assert abstracttree("la<2") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentDegree(-2), dur)])])]
    )
    assert abstracttree("la< 3") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentDegree(-3), dur)])])]
    )

    assert abstracttree("la*2") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentRatio(Ratio(2, 1)), dur)])])]
    )
    assert abstracttree("la*2/3") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, AugmentRatio(Ratio(2, 3)), dur)])])]
    )

    assert abstracttree("la...") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, aug, Duration(Ratio(3, 1)))])])]
    )
    assert abstracttree("la:3") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, aug, Duration(Ratio(3, 1)))])])]
    )
    assert abstracttree("la:3/2") == Passages(
        [Passage([Line([Group(Word("la"), 0, 0, aug, Duration(Ratio(3, 2)))])])]
    )
