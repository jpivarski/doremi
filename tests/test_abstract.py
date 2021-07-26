# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from lark.tree import Tree
from lark.lexer import Token

from doremi.abstract import (
    Word,
    Call,
    AugmentStep,
    AugmentDegree,
    AugmentRatio,
    Ratio,
    Duration,
    Modified,
    Line,
    Assignment,
    Passage,
    Passages,
    abstracttree,
)


def test_decorations():
    aug = AugmentStep(0)
    dur = Duration(Ratio(1, 1))

    assert abstracttree("la") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, aug, dur, 1)])])]
    )
    assert abstracttree("@la") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 1, 0, aug, dur, 1)])])]
    )
    assert abstracttree("@ @ la") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 2, 0, aug, dur, 1)])])]
    )

    assert abstracttree(">la") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 1, aug, dur, 1)])])]
    )
    assert abstracttree("<<la") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, -2, aug, dur, 1)])])]
    )
    assert abstracttree("3>la") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 3, aug, dur, 1)])])]
    )
    assert abstracttree("3< la") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, -3, aug, dur, 1)])])]
    )

    assert abstracttree("la+") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentStep(1), dur, 1)])])]
    )
    assert abstracttree("la + +") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentStep(2), dur, 1)])])]
    )
    assert abstracttree("la+2") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentStep(2), dur, 1)])])]
    )
    assert abstracttree("la-2") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentStep(-2), dur, 1)])])]
    )
    assert abstracttree("la- 3") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentStep(-3), dur, 1)])])]
    )

    assert abstracttree("la>") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentDegree(1), dur, 1)])])]
    )
    assert abstracttree("la > >") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentDegree(2), dur, 1)])])]
    )
    assert abstracttree("la>2") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentDegree(2), dur, 1)])])]
    )
    assert abstracttree("la<2") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentDegree(-2), dur, 1)])])]
    )
    assert abstracttree("la< 3") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentDegree(-3), dur, 1)])])]
    )

    assert abstracttree("la*2") == Passages(
        [
            Passage(
                None,
                [Line([Modified(Word("la"), 0, 0, AugmentRatio(Ratio(2, 1)), dur, 1)])],
            )
        ]
    )
    assert abstracttree("la*2/3") == Passages(
        [
            Passage(
                None,
                [Line([Modified(Word("la"), 0, 0, AugmentRatio(Ratio(2, 3)), dur, 1)])],
            )
        ]
    )

    assert abstracttree("la...") == Passages(
        [
            Passage(
                None,
                [Line([Modified(Word("la"), 0, 0, aug, Duration(Ratio(3, 1)), 1)])],
            )
        ]
    )
    assert abstracttree("la:3") == Passages(
        [
            Passage(
                None,
                [Line([Modified(Word("la"), 0, 0, aug, Duration(Ratio(3, 1)), 1)])],
            )
        ]
    )
    assert abstracttree("la:3/2") == Passages(
        [
            Passage(
                None,
                [Line([Modified(Word("la"), 0, 0, aug, Duration(Ratio(3, 2)), 1)])],
            )
        ]
    )
    assert abstracttree("la:3 / 2") == Passages(
        [
            Passage(
                None,
                [Line([Modified(Word("la"), 0, 0, aug, Duration(Ratio(3, 2)), 1)])],
            )
        ]
    )

    assert abstracttree("la ~ 4") == Passages(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, aug, dur, 4)])])]
    )

    assert abstracttree("@ > la+... ~ 4") == Passages(
        [
            Passage(
                None,
                [
                    Line(
                        [
                            Modified(
                                Word("la"),
                                1,
                                1,
                                AugmentStep(1),
                                Duration(Ratio(3, 1)),
                                4,
                            )
                        ]
                    )
                ],
            )
        ]
    )


def test_call():
    aug = AugmentStep(0)
    aug1 = AugmentStep(1)
    dur = Duration(Ratio(1, 1))
    dur3 = Duration(Ratio(3, 1))
    dur32 = Duration(Ratio(3, 2))

    x = Modified(Word("x"), 0, 0, aug, dur, 1)
    y = Modified(Word("y"), 0, 0, aug, dur, 1)

    assert abstracttree("f") == Passages(
        [Passage(None, [Line([Modified(Word("f"), 0, 0, aug, dur, 1)])])]
    )
    assert abstracttree("f()") == Passages(
        [Passage(None, [Line([Modified(Word("f"), 0, 0, aug, dur, 1)])])]
    )
    assert abstracttree("f(x)") == Passages(
        [Passage(None, [Line([Modified(Call(Word("f"), [x]), 0, 0, aug, dur, 1)])])]
    )
    assert abstracttree("f(x, y)") == Passages(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 0, 0, aug, dur, 1)])])]
    )

    assert abstracttree("@f(x, y)") == Passages(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 1, 0, aug, dur, 1)])])]
    )
    assert abstracttree(">f(x, y)") == Passages(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 0, 1, aug, dur, 1)])])]
    )
    assert abstracttree("f(x, y)+") == Passages(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 0, 0, aug1, dur, 1)])])]
    )
    assert abstracttree("f(x, y)...") == Passages(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 0, 0, aug, dur3, 1)])])]
    )
    assert abstracttree("f(x, y):3/2") == Passages(
        [
            Passage(
                None, [Line([Modified(Call(Word("f"), [x, y]), 0, 0, aug, dur32, 1)])]
            )
        ]
    )
    assert abstracttree("f(x, y) ~ 4") == Passages(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 0, 0, aug, dur, 4)])])]
    )

    assert abstracttree("@>f(x, y)+:3/2 ~ 4") == Passages(
        [
            Passage(
                None, [Line([Modified(Call(Word("f"), [x, y]), 1, 1, aug1, dur32, 4)])]
            )
        ]
    )


def test_modified():
    aug = AugmentStep(0)
    aug1 = AugmentStep(1)
    dur = Duration(Ratio(1, 1))
    dur3 = Duration(Ratio(3, 1))
    dur32 = Duration(Ratio(3, 2))

    la = Modified(Word("la"), 0, 0, aug, dur, 1)

    assert abstracttree("{la la la}") == Passages(
        [Passage(None, [Line([Modified([la, la, la], 0, 0, aug, dur, 1)])])]
    )
    assert abstracttree("@{la la la}") == Passages(
        [Passage(None, [Line([Modified([la, la, la], 1, 0, aug, dur, 1)])])]
    )
    assert abstracttree(">{la la la}") == Passages(
        [Passage(None, [Line([Modified([la, la, la], 0, 1, aug, dur, 1)])])]
    )
    assert abstracttree("{la la la}+") == Passages(
        [Passage(None, [Line([Modified([la, la, la], 0, 0, aug1, dur, 1)])])]
    )
    assert abstracttree("{la la la}...") == Passages(
        [Passage(None, [Line([Modified([la, la, la], 0, 0, aug, dur3, 1)])])]
    )
    assert abstracttree("{la la la}:3/2") == Passages(
        [Passage(None, [Line([Modified([la, la, la], 0, 0, aug, dur32, 1)])])]
    )
    assert abstracttree("{la la la} ~ 4") == Passages(
        [Passage(None, [Line([Modified([la, la, la], 0, 0, aug, dur, 4)])])]
    )

    assert abstracttree("@>{la la la}+:3/2 ~ 4") == Passages(
        [Passage(None, [Line([Modified([la, la, la], 1, 1, aug1, dur32, 4)])])]
    )


def test_passage():
    do = Modified(Word("do"), 0, 0, AugmentStep(0), Duration(Ratio(1, 1)), 1)
    la = Modified(Word("la"), 0, 0, AugmentStep(0), Duration(Ratio(1, 1)), 1)

    assert abstracttree("do") == Passages([Passage(None, [Line([do])])])
    assert abstracttree("do\nla") == Passages([Passage(None, [Line([do]), Line([la])])])
    assert abstracttree("do do do\nla") == Passages(
        [Passage(None, [Line([do, do, do]), Line([la])])]
    )
    assert abstracttree("do do do\nla la la") == Passages(
        [Passage(None, [Line([do, do, do]), Line([la, la, la])])]
    )
    assert abstracttree("do\nla\ndo\nla") == Passages(
        [Passage(None, [Line([do]), Line([la]), Line([do]), Line([la])])]
    )
    assert abstracttree("do\n\nla") == Passages(
        [Passage(None, [Line([do])]), Passage(None, [Line([la])])]
    )
    assert abstracttree("do\n\n\nla") == Passages(
        [Passage(None, [Line([do])]), Passage(None, [Line([la])])]
    )
    assert abstracttree("do\n\nla\ndo") == Passages(
        [Passage(None, [Line([do])]), Passage(None, [Line([la]), Line([do])])]
    )
    assert abstracttree("do\n\n\nla\ndo") == Passages(
        [Passage(None, [Line([do])]), Passage(None, [Line([la]), Line([do])])]
    )
    assert abstracttree("do\n\nla\n\ndo") == Passages(
        [
            Passage(None, [Line([do])]),
            Passage(None, [Line([la])]),
            Passage(None, [Line([do])]),
        ]
    )
    assert abstracttree("do\n\n\nla\n\n\ndo") == Passages(
        [
            Passage(None, [Line([do])]),
            Passage(None, [Line([la])]),
            Passage(None, [Line([do])]),
        ]
    )

    assert abstracttree("f = do") == Passages(
        [Passage(Assignment(Word("f"), []), [Line([do])])]
    )
    assert abstracttree("f(x) = do") == Passages(
        [Passage(Assignment(Word("f"), [Word("x")]), [Line([do])])]
    )
    assert abstracttree("f(x, y) = do") == Passages(
        [Passage(Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do])])]
    )

    assert abstracttree("f(x, y) = do la") == Passages(
        [Passage(Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do, la])])]
    )
    assert abstracttree("f(x, y) = do\nla") == Passages(
        [
            Passage(
                Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do]), Line([la])]
            )
        ]
    )
    assert abstracttree("f(x, y) =\ndo\nla") == Passages(
        [
            Passage(
                Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do]), Line([la])]
            )
        ]
    )
    assert abstracttree("f(x, y) =\ndo\n\nla") == Passages(
        [
            Passage(Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do])]),
            Passage(None, [Line([la])]),
        ]
    )
