# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from fractions import Fraction

from dataclasses import dataclass, field
from typing import List, Optional, Union, Generator

import lark

import doremi.parsing


class AST:
    pass


class Expression(AST):
    pass


@dataclass
class Word(Expression):
    val: lark.lexer.Token


@dataclass
class Call(Expression):
    function: Word
    args: List[Expression]
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


class Augmentation(AST):
    pass


@dataclass
class AugmentStep(Augmentation):
    amount: int
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


@dataclass
class AugmentDegree(Augmentation):
    amount: int
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


@dataclass
class AugmentRatio(Augmentation):
    amount: Fraction
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


@dataclass
class Duration(AST):
    amount: Fraction
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


@dataclass
class Modified(AST):
    expression: Union[Expression, List[Expression]]
    absolute: int
    octave: int
    augmentation: Augmentation
    duration: Duration
    repetition: int
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


@dataclass
class Line(AST):
    modified: List[Modified]
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


@dataclass
class Assignment(AST):
    function: Word
    args: List[Word]
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


@dataclass
class Passage(AST):
    assignment: Optional[Assignment]
    lines: List[Line]
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


@dataclass
class Passages(AST):
    nodes: List[Passage]
    comments: Optional[List[lark.lexer.Token]] = field(
        default=None, repr=False, compare=False, hash=False
    )
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )
    source: Optional[str] = field(default=None, repr=False, compare=False, hash=False)


def get_comments(
    node: Union[lark.tree.Tree, lark.lexer.Token]
) -> Generator[str, None, None]:
    if isinstance(node, lark.tree.Tree):
        if node.data == "start":
            for child in node.children:
                yield from get_comments(child)
        elif node.data == "assign_passage":
            for child in node.children:
                yield from get_comments(child)
        elif node.data == "passage":
            for child in node.children:
                yield from get_comments(child)
        elif node.data == "line":
            pass
        elif node.data == "assign":
            pass
        else:
            raise AssertionError(repr(node))

    else:
        if node.type == "BLANK" or node.type == "BLANK_END":
            yield node
        else:
            raise AssertionError(repr(node))


def to_ast(node: Union[lark.tree.Tree, lark.lexer.Token]) -> AST:
    if isinstance(node, lark.tree.Tree):
        if node.data == "assign_passage":
            subnodes = [x for x in node.children if isinstance(x, lark.tree.Tree)]

            if len(subnodes) == 2:
                assignment = to_ast(subnodes[0])
            else:
                assert len(subnodes) == 1
                assignment = None

            passage = subnodes[-1]
            assert isinstance(passage, lark.tree.Tree) and passage.data == "passage"

            return Passage(
                assignment,
                [
                    to_ast(x)
                    for x in passage.children
                    if not isinstance(x, lark.lexer.Token)
                ],
                node,
            )

        elif node.data == "assign":
            assert 1 <= len(node.children) <= 2

            subnode1 = node.children[0]
            assert isinstance(subnode1, lark.lexer.Token) and subnode1.type == "WORD"
            function = Word(subnode1)

            if len(node.children) == 2:
                subnode2 = node.children[1]
                assert (
                    isinstance(subnode2, lark.tree.Tree) and subnode2.data == "defargs"
                )
                assert all(
                    isinstance(x, lark.lexer.Token) and x.type == "WORD"
                    for x in subnode2.children
                )
                args = [Word(x) for x in subnode2.children]
            else:
                args = []

            return Assignment(function, args, node)

        elif node.data == "line":
            return Line([to_ast(x) for x in node.children], node)

        elif node.data == "modified":
            assert all(isinstance(x, lark.tree.Tree) for x in node.children)
            assert 1 <= len(node.children) <= 6
            index = 0

            if node.children[index].data == "absolute":
                absolute = len(node.children[index].children)
                index += 1
            else:
                absolute = 0

            if node.children[index].data == "octave":
                subnode = node.children[index].children[0].children
                assert all(isinstance(x, lark.lexer.Token) for x in subnode)
                if subnode[0].type == "INT":
                    octave = int(subnode[0])
                else:
                    octave = len(subnode)
                if subnode[-1].type == "DEGREE_DOWN":
                    octave *= -1
                index += 1
            else:
                octave = 0

            subnode = node.children[index]
            assert subnode.data == "expression"

            if isinstance(subnode.children[0], lark.lexer.Token):
                if len(subnode.children) == 1:
                    expression = to_ast(subnode.children[0])

                else:
                    function = to_ast(subnode.children[0])
                    subsubnode = subnode.children[1]
                    assert (
                        isinstance(subsubnode, lark.tree.Tree)
                        and subsubnode.data == "args"
                    )
                    args = [to_ast(x) for x in subsubnode.children]
                    expression = Call(function, args)

            else:
                expression = [to_ast(x) for x in subnode.children]

            index = -1

            if node.children[index].data == "repetition":
                repetition = int(node.children[index].children[0])
                index -= 1

            else:
                repetition = 1

            if node.children[index].data == "duration":
                subnode = node.children[index].children[0]
                assert isinstance(subnode, lark.tree.Tree)

                if subnode.data == "dot_duration":
                    duration = Duration(Fraction(len(subnode.children), 1))
                elif subnode.data == "ratio_duration":
                    ints = subnode.children[0].children
                    assert all(
                        isinstance(x, lark.lexer.Token) and x.type == "POSITIVE_INT"
                        for x in ints
                    )
                    if len(ints) == 1:
                        ratio = Fraction(int(ints[0]), 1)
                    elif len(ints) == 2:
                        ratio = Fraction(int(ints[0]), int(ints[1]))
                    else:
                        raise AssertionError(subnode.children[0])
                    duration = Duration(ratio, subnode)
                else:
                    raise AssertionError(subnode)

                index -= 1

            else:
                duration = Duration(Fraction(1, 1))

            if node.children[index].data == "augmentation":
                subnode = node.children[index].children[0]

                if subnode.data == "upward_step" or subnode.data == "downward_step":
                    assert all(
                        isinstance(x, lark.lexer.Token) for x in subnode.children
                    )
                    if subnode.children[-1].type == "INT":
                        amount = int(subnode.children[-1])
                    else:
                        amount = len(subnode.children)
                    if subnode.children[0].type == "STEP_DOWN":
                        amount *= -1
                    augmentation = AugmentStep(amount, subnode)

                elif (
                    subnode.data == "upward_degree" or subnode.data == "downward_degree"
                ):
                    assert all(
                        isinstance(x, lark.lexer.Token) for x in subnode.children
                    )
                    if subnode.children[-1].type == "INT":
                        amount = int(subnode.children[-1])
                    else:
                        amount = len(subnode.children)
                    if subnode.children[0].type == "DEGREE_DOWN":
                        amount *= -1
                    augmentation = AugmentDegree(amount, subnode)

                else:
                    ints = subnode.children[0].children
                    assert all(
                        isinstance(x, lark.lexer.Token) and x.type == "POSITIVE_INT"
                        for x in ints
                    )
                    if len(ints) == 1:
                        ratio = Fraction(int(ints[0]), 1)
                    elif len(ints) == 2:
                        ratio = Fraction(int(ints[0]), int(ints[1]))
                    else:
                        raise AssertionError(subnode.children[0])
                    augmentation = AugmentRatio(ratio, subnode)

                index -= 1

            else:
                augmentation = AugmentStep(0)

            return Modified(
                expression, absolute, octave, augmentation, duration, repetition, node
            )

        raise AssertionError(repr(node))

    else:
        if node.type == "WORD":
            return Word(node)

        else:
            raise AssertionError(repr(node))


def abstracttree(source: str) -> AST:
    parsingtree = doremi.parsing.parsingtree(source)
    assert parsingtree.data == "start"

    comments = list(get_comments(parsingtree))
    for i, x in enumerate(comments):
        assert i + 1 == x.line, [x.line for x in comments]

    passages = [
        to_ast(x) for x in parsingtree.children if not isinstance(x, lark.lexer.Token)
    ]
    return Passages(passages, comments, parsingtree, source)
