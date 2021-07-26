# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

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

    def __repr__(self) -> str:
        return f"{type(self).__name__}({str(self.val)!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.val == other.val
        else:
            return NotImplemented



@dataclass
class Call(Expression):
    function: Word
    args: List[Expression]
    parsingtree: Optional[lark.tree.Tree] = field(default=None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.function}, {self.args})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.function == other.function and self.args == other.args
        else:
            return NotImplemented


@dataclass
class Ratio(AST):
    numerator: int
    denominator: int
    parsingtree: Optional[lark.tree.Tree] = field(default=None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.numerator}, {self.denominator})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return (
                self.numerator * other.denominator == other.numerator * self.denominator
            )
        else:
            return NotImplemented


class Augmentation(AST):
    pass


@dataclass
class AugmentStep(Augmentation):
    val: int
    parsingtree: Optional[lark.tree.Tree] = field(default=None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.val})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.val == other.val
        else:
            return NotImplemented


@dataclass
class AugmentDegree(Augmentation):
    val: int
    parsingtree: Optional[lark.tree.Tree] = field(default=None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.val})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.val == other.val
        else:
            return NotImplemented


@dataclass
class AugmentRatio(Augmentation):
    val: Ratio
    parsingtree: Optional[lark.tree.Tree] = field(default=None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.val})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.val == other.val
        else:
            return NotImplemented


@dataclass
class Duration(AST):
    val: Ratio
    parsingtree: Optional[lark.tree.Tree] = field(default=None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.val})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.val == other.val
        else:
            return NotImplemented


@dataclass
class Modified(AST):
    val: Union[Expression, List[Expression]]
    absolute: int
    octave: int
    augmentation: Augmentation
    duration: Duration
    parsingtree: Optional[lark.tree.Tree] = field(default=None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.val}, {self.absolute}, {self.octave}, {self.augmentation}, {self.duration})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return (
                self.val == other.val
                and self.absolute == other.absolute
                and self.octave == other.octave
                and self.augmentation == other.augmentation
                and self.duration == other.duration
            )
        else:
            return NotImplemented


@dataclass
class Line(AST):
    val: List[Modified]
    parsingtree: Optional[lark.tree.Tree] = field(default=None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.val})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.val == other.val
        else:
            return NotImplemented


@dataclass
class Passage(AST):
    # lhs: Optional
    val: List[Line]
    parsingtree: Optional[lark.tree.Tree] = field(default=None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.val})"  # LHS

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.val == other.val  # LHS
        else:
            return NotImplemented


@dataclass
class Passages(AST):
    val: List[Passage]
    comments: Optional[List[lark.lexer.Token]] = field(default=None)
    parsingtree: Optional[lark.tree.Tree] = field(default=None)
    source: Optional[str] = field(default=None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.val})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, type(self)):
            return self.val == other.val
        else:
            return NotImplemented


def get_comments(
    node: Union[lark.tree.Tree, lark.lexer.Token]
) -> Generator[str, None, None]:
    if isinstance(node, lark.tree.Tree):
        if node.data == "start":
            for child in node.children:
                yield from get_comments(child)
        elif node.data == "lhs_passage":
            for child in node.children:
                yield from get_comments(child)
        elif node.data == "passage":
            for child in node.children:
                yield from get_comments(child)
        elif node.data == "line":
            pass
        else:
            raise AssertionError(repr(node))

    else:
        if node.type == "BLANK":
            yield node
        else:
            raise AssertionError(repr(node))


def to_ast(node: Union[lark.tree.Tree, lark.lexer.Token]) -> AST:
    if isinstance(node, lark.tree.Tree):
        if node.data == "lhs_passage":
            if len(node.children) == 3:
                raise NotImplementedError
            else:
                assert len(node.children) == 1

            passage = node.children[-1]
            assert isinstance(passage, lark.tree.Tree) and passage.data == "passage"

            return Passage(
                [
                    to_ast(x)
                    for x in passage.children
                    if not isinstance(x, lark.lexer.Token)
                ],
                node,
            )

        elif node.data == "line":
            return Line([to_ast(x) for x in node.children], node)

        elif node.data == "modified":
            assert all(isinstance(x, lark.tree.Tree) for x in node.children)
            assert 1 <= len(node.children) <= 5
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
                    assert isinstance(subsubnode, lark.tree.Tree) and subsubnode.data == "args"
                    args = [to_ast(x) for x in subsubnode.children]
                    expression = Call(function, args)

            else:
                expression = [to_ast(x) for x in subnode.children]

            index = -1

            if node.children[index].data == "duration":
                subnode = node.children[index].children[0]
                assert isinstance(subnode, lark.tree.Tree)

                if subnode.data == "dot_duration":
                    duration = Duration(Ratio(len(subnode.children), 1), subnode)
                elif subnode.data == "ratio_duration":
                    ints = subnode.children[0].children
                    assert all(
                        isinstance(x, lark.lexer.Token) and x.type == "POSITIVE_INT"
                        for x in ints
                    )
                    if len(ints) == 1:
                        ratio = Ratio(int(ints[0]), 1, subnode.children[0])
                    elif len(ints) == 2:
                        ratio = Ratio(int(ints[0]), int(ints[1]), subnode.children[0])
                    else:
                        raise AssertionError(subnode.children[0])
                    duration = Duration(ratio, subnode)
                else:
                    raise AssertionError(subnode)

                index -= 1

            else:
                duration = Duration(Ratio(1, 1))

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
                        ratio = Ratio(int(ints[0]), 1, subnode.children[0])
                    elif len(ints) == 2:
                        ratio = Ratio(int(ints[0]), int(ints[1]), subnode.children[0])
                    else:
                        raise AssertionError(subnode.children[0])
                    augmentation = AugmentRatio(ratio, subnode)

                index -= 1

            else:
                augmentation = AugmentStep(0)

            return Modified(expression, absolute, octave, augmentation, duration, node)

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
