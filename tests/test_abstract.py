# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from fractions import Fraction

from lark.tree import Tree
from lark.lexer import Token

from doremi.abstract import (
    AbstractNote,
    Scope,
    Word,
    Call,
    AugmentStep,
    AugmentDegree,
    AugmentRatio,
    Duration,
    Modified,
    Line,
    Assignment,
    NamedPassage,
    UnnamedPassage,
    evaluate,
    Collection,
    abstracttree,
)


def test_decorations():
    assert abstracttree("la") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 0, 0, None, None, 1)])])]
    )
    assert abstracttree("@la") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 1, 0, None, None, 1)])])]
    )
    assert abstracttree("@ @ la") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 2, 0, None, None, 1)])])]
    )

    assert abstracttree(">la") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 0, 1, None, None, 1)])])]
    )
    assert abstracttree("<<la") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 0, -2, None, None, 1)])])]
    )
    assert abstracttree("3>la") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 0, 3, None, None, 1)])])]
    )
    assert abstracttree("3< la") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 0, -3, None, None, 1)])])]
    )

    assert abstracttree("la+") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 0, 0, AugmentStep(1), None, 1)])])]
    )
    assert abstracttree("la + +") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 0, 0, AugmentStep(2), None, 1)])])]
    )
    assert abstracttree("la+2") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 0, 0, AugmentStep(2), None, 1)])])]
    )
    assert abstracttree("la-2") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 0, 0, AugmentStep(-2), None, 1)])])]
    )
    assert abstracttree("la- 3") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 0, 0, AugmentStep(-3), None, 1)])])]
    )

    assert abstracttree("la>") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Word("la"), 0, 0, AugmentDegree(1), None, 1)])]
            )
        ]
    )
    assert abstracttree("la > >") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Word("la"), 0, 0, AugmentDegree(2), None, 1)])]
            )
        ]
    )
    assert abstracttree("la>2") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Word("la"), 0, 0, AugmentDegree(2), None, 1)])]
            )
        ]
    )
    assert abstracttree("la<2") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Word("la"), 0, 0, AugmentDegree(-2), None, 1)])]
            )
        ]
    )
    assert abstracttree("la< 3") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Word("la"), 0, 0, AugmentDegree(-3), None, 1)])]
            )
        ]
    )

    assert abstracttree("la*2") == Collection(
        [
            UnnamedPassage(
                [
                    Line(
                        [
                            Modified(
                                Word("la"), 0, 0, AugmentRatio(Fraction(2, 1)), None, 1
                            )
                        ]
                    )
                ],
            )
        ]
    )
    assert abstracttree("la*2/3") == Collection(
        [
            UnnamedPassage(
                [
                    Line(
                        [
                            Modified(
                                Word("la"), 0, 0, AugmentRatio(Fraction(2, 3)), None, 1
                            )
                        ]
                    )
                ],
            )
        ]
    )

    assert abstracttree("la...") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Word("la"), 0, 0, None, Duration(Fraction(3, 1)), 1)])],
            )
        ]
    )
    assert abstracttree("la:3") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Word("la"), 0, 0, None, Duration(Fraction(3, 1)), 1)])],
            )
        ]
    )
    assert abstracttree("la:3/2") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Word("la"), 0, 0, None, Duration(Fraction(3, 2)), 1)])],
            )
        ]
    )
    assert abstracttree("la:3 / 2") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Word("la"), 0, 0, None, Duration(Fraction(3, 2)), 1)])],
            )
        ]
    )

    assert abstracttree("la ~ 4") == Collection(
        [UnnamedPassage([Line([Modified(Word("la"), 0, 0, None, None, 4)])])]
    )

    assert abstracttree("@ > la+... ~ 4") == Collection(
        [
            UnnamedPassage(
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
    aug1 = AugmentStep(1)
    dur3 = Duration(Fraction(3, 1))
    dur32 = Duration(Fraction(3, 2))

    x = Modified(Word("x"), 0, 0, None, None, 1)
    y = Modified(Word("y"), 0, 0, None, None, 1)

    assert abstracttree("f") == Collection(
        [UnnamedPassage([Line([Modified(Word("f"), 0, 0, None, None, 1)])])]
    )
    assert abstracttree("f()") == Collection(
        [UnnamedPassage([Line([Modified(Word("f"), 0, 0, None, None, 1)])])]
    )
    assert abstracttree("f(x)") == Collection(
        [UnnamedPassage([Line([Modified(Call(Word("f"), [x]), 0, 0, None, None, 1)])])]
    )
    assert abstracttree("f(x, y)") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Call(Word("f"), [x, y]), 0, 0, None, None, 1)])]
            )
        ]
    )

    assert abstracttree("@f(x, y)") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Call(Word("f"), [x, y]), 1, 0, None, None, 1)])]
            )
        ]
    )
    assert abstracttree(">f(x, y)") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Call(Word("f"), [x, y]), 0, 1, None, None, 1)])]
            )
        ]
    )
    assert abstracttree("f(x, y)+") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Call(Word("f"), [x, y]), 0, 0, aug1, None, 1)])]
            )
        ]
    )
    assert abstracttree("f(x, y)...") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Call(Word("f"), [x, y]), 0, 0, None, dur3, 1)])]
            )
        ]
    )
    assert abstracttree("f(x, y):3/2") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Call(Word("f"), [x, y]), 0, 0, None, dur32, 1)])]
            )
        ]
    )
    assert abstracttree("f(x, y) ~ 4") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Call(Word("f"), [x, y]), 0, 0, None, None, 4)])]
            )
        ]
    )

    assert abstracttree("@>f(x, y)+:3/2 ~ 4") == Collection(
        [
            UnnamedPassage(
                [Line([Modified(Call(Word("f"), [x, y]), 1, 1, aug1, dur32, 4)])]
            )
        ]
    )


def test_modified():
    aug1 = AugmentStep(1)
    dur3 = Duration(Fraction(3, 1))
    dur32 = Duration(Fraction(3, 2))

    la = Modified(Word("la"), 0, 0, None, None, 1)

    assert abstracttree("{la la la}") == Collection(
        [UnnamedPassage([Line([Modified([la, la, la], 0, 0, None, None, 1)])])]
    )
    assert abstracttree("@{la la la}") == Collection(
        [UnnamedPassage([Line([Modified([la, la, la], 1, 0, None, None, 1)])])]
    )
    assert abstracttree(">{la la la}") == Collection(
        [UnnamedPassage([Line([Modified([la, la, la], 0, 1, None, None, 1)])])]
    )
    assert abstracttree("{la la la}+") == Collection(
        [UnnamedPassage([Line([Modified([la, la, la], 0, 0, aug1, None, 1)])])]
    )
    assert abstracttree("{la la la}...") == Collection(
        [UnnamedPassage([Line([Modified([la, la, la], 0, 0, None, dur3, 1)])])]
    )
    assert abstracttree("{la la la}:3/2") == Collection(
        [UnnamedPassage([Line([Modified([la, la, la], 0, 0, None, dur32, 1)])])]
    )
    assert abstracttree("{la la la} ~ 4") == Collection(
        [UnnamedPassage([Line([Modified([la, la, la], 0, 0, None, None, 4)])])]
    )

    assert abstracttree("@>{la la la}+:3/2 ~ 4") == Collection(
        [UnnamedPassage([Line([Modified([la, la, la], 1, 1, aug1, dur32, 4)])])]
    )


def test_passage():
    do = Modified(Word("do"), 0, 0, None, None, 1)
    la = Modified(Word("la"), 0, 0, None, None, 1)

    assert abstracttree("do") == Collection([UnnamedPassage([Line([do])])])
    assert abstracttree("do\nla") == Collection(
        [UnnamedPassage([Line([do]), Line([la])])]
    )
    assert abstracttree("do do do\nla") == Collection(
        [UnnamedPassage([Line([do, do, do]), Line([la])])]
    )
    assert abstracttree("do do do\nla la la") == Collection(
        [UnnamedPassage([Line([do, do, do]), Line([la, la, la])])]
    )
    assert abstracttree("do\nla\ndo\nla") == Collection(
        [UnnamedPassage([Line([do]), Line([la]), Line([do]), Line([la])])]
    )
    assert abstracttree("do\n\nla") == Collection(
        [UnnamedPassage([Line([do])]), UnnamedPassage([Line([la])])]
    )
    assert abstracttree("do\n\n\nla") == Collection(
        [UnnamedPassage([Line([do])]), UnnamedPassage([Line([la])])]
    )
    assert abstracttree("do\n\nla\ndo") == Collection(
        [UnnamedPassage([Line([do])]), UnnamedPassage([Line([la]), Line([do])])]
    )
    assert abstracttree("do\n\n\nla\ndo") == Collection(
        [UnnamedPassage([Line([do])]), UnnamedPassage([Line([la]), Line([do])])]
    )
    assert abstracttree("do\n\nla\n\ndo") == Collection(
        [
            UnnamedPassage([Line([do])]),
            UnnamedPassage([Line([la])]),
            UnnamedPassage([Line([do])]),
        ]
    )
    assert abstracttree("do\n\n\nla\n\n\ndo") == Collection(
        [
            UnnamedPassage([Line([do])]),
            UnnamedPassage([Line([la])]),
            UnnamedPassage([Line([do])]),
        ]
    )

    assert abstracttree("f = do") == Collection(
        [NamedPassage(Assignment(Word("f"), []), [Line([do])])]
    )
    assert abstracttree("f(x) = do") == Collection(
        [NamedPassage(Assignment(Word("f"), [Word("x")]), [Line([do])])]
    )
    assert abstracttree("f(x, y) = do") == Collection(
        [NamedPassage(Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do])])]
    )

    assert abstracttree("f(x, y) = do la") == Collection(
        [NamedPassage(Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do, la])])]
    )
    assert abstracttree("f(x, y) = do\nla") == Collection(
        [
            NamedPassage(
                Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do]), Line([la])]
            )
        ]
    )
    assert abstracttree("f(x, y) =\ndo\nla") == Collection(
        [
            NamedPassage(
                Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do]), Line([la])]
            )
        ]
    )
    assert abstracttree("f(x, y) =\ndo\n\nla") == Collection(
        [
            NamedPassage(Assignment(Word("f"), [Word("x"), Word("y")]), [Line([do])]),
            UnnamedPassage([Line([la])]),
        ]
    )


def test_comments():
    do = Modified(Word("do"), 0, 0, None, None, 1)
    la = Modified(Word("la"), 0, 0, None, None, 1)

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
        == Collection([UnnamedPassage([Line([do]), Line([la])])])
    )
    assert (
        abstracttree(
            """do | one
la | two
"""
        )
        == Collection([UnnamedPassage([Line([do]), Line([la])])])
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
        == Collection([UnnamedPassage([Line([do])]), UnnamedPassage([Line([la])])])
    )
    assert (
        abstracttree(
            """do
| two
la | three
"""
        )
        == Collection([UnnamedPassage([Line([do])]), UnnamedPassage([Line([la])])])
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


def test_evaluate():
    assert evaluate(abstracttree("do").passages[0], Scope({}), 0, ()) == (
        1.0,
        [AbstractNote(0.0, 1.0, Word("do"))],
    )

    assert evaluate(abstracttree("do re mi").passages[0], Scope({}), 0, ()) == (
        3.0,
        [
            AbstractNote(0.0, 1.0, Word("do")),
            AbstractNote(1.0, 2.0, Word("re")),
            AbstractNote(2.0, 3.0, Word("mi")),
        ],
    )

    assert evaluate(abstracttree("do....").passages[0], Scope({}), 0, ()) == (
        4.0,
        [AbstractNote(0.0, 4.0, Word("do"))],
    )

    assert evaluate(abstracttree("do.. re.. mi..").passages[0], Scope({}), 0, ()) == (
        6.0,
        [
            AbstractNote(0.0, 2.0, Word("do")),
            AbstractNote(2.0, 4.0, Word("re")),
            AbstractNote(4.0, 6.0, Word("mi")),
        ],
    )

    assert evaluate(abstracttree("___").passages[0], Scope({}), 0, ()) == (
        3.0,
        [],
    )

    assert evaluate(abstracttree("do _ mi").passages[0], Scope({}), 0, ()) == (
        3.0,
        [
            AbstractNote(0.0, 1.0, Word("do")),
            AbstractNote(2.0, 3.0, Word("mi")),
        ],
    )

    assert evaluate(abstracttree("do __ mi").passages[0], Scope({}), 0, ()) == (
        4.0,
        [
            AbstractNote(0.0, 1.0, Word("do")),
            AbstractNote(3.0, 4.0, Word("mi")),
        ],
    )

    assert evaluate(abstracttree("do __ mi _").passages[0], Scope({}), 0, ()) == (
        5.0,
        [
            AbstractNote(0.0, 1.0, Word("do")),
            AbstractNote(3.0, 4.0, Word("mi")),
        ],
    )

    assert evaluate(abstracttree("do\nre\nmi").passages[0], Scope({}), 0, ()) == (
        1.0,
        [
            AbstractNote(0.0, 1.0, Word("do")),
            AbstractNote(0.0, 1.0, Word("re")),
            AbstractNote(0.0, 1.0, Word("mi")),
        ],
    )

    assert evaluate(abstracttree("do\n_\nre mi").passages[0], Scope({}), 0, ()) == (
        2.0,
        [
            AbstractNote(0.0, 1.0, Word("do")),
            AbstractNote(0.0, 1.0, Word("re")),
            AbstractNote(1.0, 2.0, Word("mi")),
        ],
    )

    assert evaluate(abstracttree(">do").passages[0], Scope({}), 0, ()) == (
        1.0,
        [AbstractNote(0.0, 1.0, Word("do"), octave=1)],
    )

    assert evaluate(abstracttree("do+1").passages[0], Scope({}), 0, ()) == (
        1.0,
        [AbstractNote(0.0, 1.0, Word("do"), augmentations=(AugmentStep(1),))],
    )
