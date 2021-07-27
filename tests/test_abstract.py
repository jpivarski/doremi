# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from fractions import Fraction

from lark.tree import Tree
from lark.lexer import Token

from doremi.abstract import (
    Word,
    Call,
    AugmentStep,
    AugmentDegree,
    AugmentRatio,
    Duration,
    Modified,
    Line,
    Assignment,
    Passage,
    Collection,
    abstracttree,
)


def test_decorations():
    aug = AugmentStep(0)
    dur = Duration(Fraction(1, 1))

    assert abstracttree("la") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, aug, dur, 1)])])]
    )
    assert abstracttree("@la") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 1, 0, aug, dur, 1)])])]
    )
    assert abstracttree("@ @ la") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 2, 0, aug, dur, 1)])])]
    )

    assert abstracttree(">la") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 1, aug, dur, 1)])])]
    )
    assert abstracttree("<<la") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, -2, aug, dur, 1)])])]
    )
    assert abstracttree("3>la") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 3, aug, dur, 1)])])]
    )
    assert abstracttree("3< la") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, -3, aug, dur, 1)])])]
    )

    assert abstracttree("la+") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentStep(1), dur, 1)])])]
    )
    assert abstracttree("la + +") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentStep(2), dur, 1)])])]
    )
    assert abstracttree("la+2") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentStep(2), dur, 1)])])]
    )
    assert abstracttree("la-2") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentStep(-2), dur, 1)])])]
    )
    assert abstracttree("la- 3") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentStep(-3), dur, 1)])])]
    )

    assert abstracttree("la>") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentDegree(1), dur, 1)])])]
    )
    assert abstracttree("la > >") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentDegree(2), dur, 1)])])]
    )
    assert abstracttree("la>2") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentDegree(2), dur, 1)])])]
    )
    assert abstracttree("la<2") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentDegree(-2), dur, 1)])])]
    )
    assert abstracttree("la< 3") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, AugmentDegree(-3), dur, 1)])])]
    )

    assert abstracttree("la*2") == Collection(
        [
            Passage(
                None,
                [
                    Line(
                        [
                            Modified(
                                Word("la"), 0, 0, AugmentRatio(Fraction(2, 1)), dur, 1
                            )
                        ]
                    )
                ],
            )
        ]
    )
    assert abstracttree("la*2/3") == Collection(
        [
            Passage(
                None,
                [
                    Line(
                        [
                            Modified(
                                Word("la"), 0, 0, AugmentRatio(Fraction(2, 3)), dur, 1
                            )
                        ]
                    )
                ],
            )
        ]
    )

    assert abstracttree("la...") == Collection(
        [
            Passage(
                None,
                [Line([Modified(Word("la"), 0, 0, aug, Duration(Fraction(3, 1)), 1)])],
            )
        ]
    )
    assert abstracttree("la:3") == Collection(
        [
            Passage(
                None,
                [Line([Modified(Word("la"), 0, 0, aug, Duration(Fraction(3, 1)), 1)])],
            )
        ]
    )
    assert abstracttree("la:3/2") == Collection(
        [
            Passage(
                None,
                [Line([Modified(Word("la"), 0, 0, aug, Duration(Fraction(3, 2)), 1)])],
            )
        ]
    )
    assert abstracttree("la:3 / 2") == Collection(
        [
            Passage(
                None,
                [Line([Modified(Word("la"), 0, 0, aug, Duration(Fraction(3, 2)), 1)])],
            )
        ]
    )

    assert abstracttree("la ~ 4") == Collection(
        [Passage(None, [Line([Modified(Word("la"), 0, 0, aug, dur, 4)])])]
    )

    assert abstracttree("@ > la+... ~ 4") == Collection(
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
                                Duration(Fraction(3, 1)),
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
    dur = Duration(Fraction(1, 1))
    dur3 = Duration(Fraction(3, 1))
    dur32 = Duration(Fraction(3, 2))

    x = Modified(Word("x"), 0, 0, aug, dur, 1)
    y = Modified(Word("y"), 0, 0, aug, dur, 1)

    assert abstracttree("f") == Collection(
        [Passage(None, [Line([Modified(Word("f"), 0, 0, aug, dur, 1)])])]
    )
    assert abstracttree("f()") == Collection(
        [Passage(None, [Line([Modified(Word("f"), 0, 0, aug, dur, 1)])])]
    )
    assert abstracttree("f(x)") == Collection(
        [Passage(None, [Line([Modified(Call(Word("f"), [x]), 0, 0, aug, dur, 1)])])]
    )
    assert abstracttree("f(x, y)") == Collection(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 0, 0, aug, dur, 1)])])]
    )

    assert abstracttree("@f(x, y)") == Collection(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 1, 0, aug, dur, 1)])])]
    )
    assert abstracttree(">f(x, y)") == Collection(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 0, 1, aug, dur, 1)])])]
    )
    assert abstracttree("f(x, y)+") == Collection(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 0, 0, aug1, dur, 1)])])]
    )
    assert abstracttree("f(x, y)...") == Collection(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 0, 0, aug, dur3, 1)])])]
    )
    assert abstracttree("f(x, y):3/2") == Collection(
        [
            Passage(
                None, [Line([Modified(Call(Word("f"), [x, y]), 0, 0, aug, dur32, 1)])]
            )
        ]
    )
    assert abstracttree("f(x, y) ~ 4") == Collection(
        [Passage(None, [Line([Modified(Call(Word("f"), [x, y]), 0, 0, aug, dur, 4)])])]
    )

    assert abstracttree("@>f(x, y)+:3/2 ~ 4") == Collection(
        [
            Passage(
                None, [Line([Modified(Call(Word("f"), [x, y]), 1, 1, aug1, dur32, 4)])]
            )
        ]
    )


def test_modified():
    aug = AugmentStep(0)
    aug1 = AugmentStep(1)
    dur = Duration(Fraction(1, 1))
    dur3 = Duration(Fraction(3, 1))
    dur32 = Duration(Fraction(3, 2))

    la = Modified(Word("la"), 0, 0, aug, dur, 1)

    assert abstracttree("{la la la}") == Collection(
        [Passage(None, [Line([Modified([la, la, la], 0, 0, aug, dur, 1)])])]
    )
    assert abstracttree("@{la la la}") == Collection(
        [Passage(None, [Line([Modified([la, la, la], 1, 0, aug, dur, 1)])])]
    )
    assert abstracttree(">{la la la}") == Collection(
        [Passage(None, [Line([Modified([la, la, la], 0, 1, aug, dur, 1)])])]
    )
    assert abstracttree("{la la la}+") == Collection(
        [Passage(None, [Line([Modified([la, la, la], 0, 0, aug1, dur, 1)])])]
    )
    assert abstracttree("{la la la}...") == Collection(
        [Passage(None, [Line([Modified([la, la, la], 0, 0, aug, dur3, 1)])])]
    )
    assert abstracttree("{la la la}:3/2") == Collection(
        [Passage(None, [Line([Modified([la, la, la], 0, 0, aug, dur32, 1)])])]
    )
    assert abstracttree("{la la la} ~ 4") == Collection(
        [Passage(None, [Line([Modified([la, la, la], 0, 0, aug, dur, 4)])])]
    )

    assert abstracttree("@>{la la la}+:3/2 ~ 4") == Collection(
        [Passage(None, [Line([Modified([la, la, la], 1, 1, aug1, dur32, 4)])])]
    )


def test_passage():
    do = Modified(Word("do"), 0, 0, AugmentStep(0), Duration(Fraction(1, 1)), 1)
    la = Modified(Word("la"), 0, 0, AugmentStep(0), Duration(Fraction(1, 1)), 1)

    assert abstracttree("do") == Collection([Passage(None, [Line([do])])])
    assert abstracttree("do\nla") == Collection(
        [Passage(None, [Line([do]), Line([la])])]
    )
    assert abstracttree("do do do\nla") == Collection(
        [Passage(None, [Line([do, do, do]), Line([la])])]
    )
    assert abstracttree("do do do\nla la la") == Collection(
        [Passage(None, [Line([do, do, do]), Line([la, la, la])])]
    )
    assert abstracttree("do\nla\ndo\nla") == Collection(
        [Passage(None, [Line([do]), Line([la]), Line([do]), Line([la])])]
    )
    assert abstracttree("do\n\nla") == Collection(
        [Passage(None, [Line([do])]), Passage(None, [Line([la])])]
    )
    assert abstracttree("do\n\n\nla") == Collection(
        [Passage(None, [Line([do])]), Passage(None, [Line([la])])]
    )
    assert abstracttree("do\n\nla\ndo") == Collection(
        [Passage(None, [Line([do])]), Passage(None, [Line([la]), Line([do])])]
    )
    assert abstracttree("do\n\n\nla\ndo") == Collection(
        [Passage(None, [Line([do])]), Passage(None, [Line([la]), Line([do])])]
    )
    assert abstracttree("do\n\nla\n\ndo") == Collection(
        [
            Passage(None, [Line([do])]),
            Passage(None, [Line([la])]),
            Passage(None, [Line([do])]),
        ]
    )
    assert abstracttree("do\n\n\nla\n\n\ndo") == Collection(
        [
            Passage(None, [Line([do])]),
            Passage(None, [Line([la])]),
            Passage(None, [Line([do])]),
        ]
    )

    assert abstracttree("f = do") == Collection(
        [Passage(Assignment(Word("f"), []), [Line([do])])]
    )
    assert abstracttree("f(x) = do") == Collection(
        [Passage(Assignment(Word("f"), [Word("x")]), [Line([do])])]
    )
    assert abstracttree("f(x, y) = do") == Collection(
        [Passage(Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do])])]
    )

    assert abstracttree("f(x, y) = do la") == Collection(
        [Passage(Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do, la])])]
    )
    assert abstracttree("f(x, y) = do\nla") == Collection(
        [
            Passage(
                Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do]), Line([la])]
            )
        ]
    )
    assert abstracttree("f(x, y) =\ndo\nla") == Collection(
        [
            Passage(
                Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do]), Line([la])]
            )
        ]
    )
    assert abstracttree("f(x, y) =\ndo\n\nla") == Collection(
        [
            Passage(Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do])]),
            Passage(None, [Line([la])]),
        ]
    )


def test_comments():
    do = Modified(Word("do"), 0, 0, AugmentStep(0), Duration(Fraction(1, 1)), 1)
    la = Modified(Word("la"), 0, 0, AugmentStep(0), Duration(Fraction(1, 1)), 1)

    assert abstracttree("""do""").comments == []
    assert (
        abstracttree(
            """do
"""
        ).comments
        == ["\n"]
    )
    assert abstracttree("""do | one""").comments == ["| one"]
    assert (
        abstracttree(
            """do | one
"""
        ).comments
        == ["| one\n"]
    )
    assert abstracttree("""do |one""").comments == ["|one"]
    assert (
        abstracttree(
            """do |one
"""
        ).comments
        == ["|one\n"]
    )
    assert (
        abstracttree(
            """do
la"""
        ).comments
        == ["\n"]
    )
    assert (
        abstracttree(
            """do
la
"""
        ).comments
        == ["\n", "\n"]
    )
    assert (
        abstracttree(
            """do   
la"""
        ).comments
        == ["\n"]
    )
    assert (
        abstracttree(
            """do   
la
"""
        ).comments
        == ["\n", "\n"]
    )
    assert (
        abstracttree(
            """do | one
la"""
        ).comments
        == ["| one\n"]
    )
    assert (
        abstracttree(
            """do | one
la
"""
        ).comments
        == ["| one\n", "\n"]
    )
    assert (
        abstracttree(
            """do | one
la | two"""
        ).comments
        == ["| one\n", "| two"]
    )
    assert (
        abstracttree(
            """do | one
la | two
"""
        ).comments
        == ["| one\n", "| two\n"]
    )
    assert (
        abstracttree(
            """do | one
la | two"""
        )
        == Collection([Passage(None, [Line([do]), Line([la])])])
    )
    assert (
        abstracttree(
            """do | one
la | two
"""
        )
        == Collection([Passage(None, [Line([do]), Line([la])])])
    )
    assert (
        abstracttree(
            """do
la | two"""
        ).comments
        == ["\n", "| two"]
    )
    assert (
        abstracttree(
            """do
la | two
"""
        ).comments
        == ["\n", "| two\n"]
    )
    assert (
        abstracttree(
            """do   
la | two"""
        ).comments
        == ["\n", "| two"]
    )
    assert (
        abstracttree(
            """do   
la | two
"""
        ).comments
        == ["\n", "| two\n"]
    )
    assert (
        abstracttree(
            """do
| two
la | three"""
        ).comments
        == ["\n", "| two\n", "| three"]
    )
    assert (
        abstracttree(
            """do
| two
la | three
"""
        ).comments
        == ["\n", "| two\n", "| three\n"]
    )
    assert (
        abstracttree(
            """do
| two
la | three"""
        )
        == Collection([Passage(None, [Line([do])]), Passage(None, [Line([la])])])
    )
    assert (
        abstracttree(
            """do
| two
la | three
"""
        )
        == Collection([Passage(None, [Line([do])]), Passage(None, [Line([la])])])
    )
    assert abstracttree("""f = do | one""").comments == ["| one"]
    assert (
        abstracttree(
            """f = do | one
"""
        ).comments
        == ["| one\n"]
    )
    assert (
        abstracttree(
            """f =
do | two"""
        ).comments
        == ["\n", "| two"]
    )
    assert (
        abstracttree(
            """f =
do | two
"""
        ).comments
        == ["\n", "| two\n"]
    )
    assert (
        abstracttree(
            """f = | one
do | two"""
        ).comments
        == ["| one\n", "| two"]
    )
    assert (
        abstracttree(
            """f = | one
do | two
"""
        ).comments
        == ["| one\n", "| two\n"]
    )
    assert (
        abstracttree(
            """| one
f =
do | three"""
        ).comments
        == ["| one\n", "\n", "| three"]
    )
    assert (
        abstracttree(
            """| one
f =
do | three
"""
        ).comments
        == ["| one\n", "\n", "| three\n"]
    )
    assert (
        abstracttree(
            """| one
f = | two
do | three"""
        ).comments
        == ["| one\n", "| two\n", "| three"]
    )
    assert (
        abstracttree(
            """| one
f = | two
do | three
"""
        ).comments
        == ["| one\n", "| two\n", "| three\n"]
    )
