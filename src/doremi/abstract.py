# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from dataclasses import dataclass
from typing import List, Optional, Union, Generator

import lark

import doremi.parsing


class AST:
    pass


@dataclass
class Word(AST):
    val: lark.lexer.Token


@dataclass
class Augmentation(AST):
    val: int
    parsingtree: Optional[lark.tree.Tree]


@dataclass
class Ratio(AST):
    numerator: int
    denominator: int
    parsingtree: Optional[lark.tree.Tree]


@dataclass
class Duration(AST):
    val: Ratio
    parsingtree: Optional[lark.tree.Tree]


@dataclass
class Group(AST):
    val: Union[Word, List["Group"]]
    absolute: int
    octave: int
    augmentation: Augmentation
    duration: Duration
    parsingtree: lark.tree.Tree


@dataclass
class Line(AST):
    val: List[Group]
    parsingtree: lark.tree.Tree


@dataclass
class Passage(AST):
    # lhs: Option
    val: List[Line]
    parsingtree: lark.tree.Tree


@dataclass
class Passages(AST):
    val: List[Passage]
    comments: List[lark.lexer.Token]
    parsingtree: lark.tree.Tree
    source: str


def get_comments(node: Union[lark.tree.Tree, lark.lexer.Token]) -> Generator[str, None, None]:
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
    print(repr(node))

    if isinstance(node, lark.tree.Tree):
        if node.data == "lhs_passage":
            if len(node.children) == 3:
                raise NotImplementedError
            else:
                assert len(node.children) == 1

            passage = node.children[-1]
            assert isinstance(passage, lark.tree.Tree) and passage.data == "passage"

            return Passage([
                to_ast(x) for x in passage.children if not isinstance(x, lark.lexer.Token)
            ], node)

        elif node.data == "line":
            return Line([to_ast(x) for x in node.children], node)

        elif node.data == "group":
            assert all(isinstance(x, lark.tree.Tree) for x in node.children)
            assert 1 <= len(node.children) <= 5
            index = 0

            if node.children[index].data == "absolute":
                raise NotImplementedError
                index += 1
            else:
                absolute = 0

            if node.children[index].data == "octave":
                raise NotImplementedError
                index += 1
            else:
                octave = 0

            assert node.children[index].data == "atom"
            if isinstance(node.children[index].children[0], lark.lexer.Token):
                atom = to_ast(node.children[index].children[0])
            else:
                raise NotImplementedError

            index = -1

            if node.children[index].data == "duration":
                raise NotImplementedError
                index -= 1
            else:
                duration = Duration(Ratio(1, 0, None), None)

            if node.children[index].data == "augmentation":
                raise NotImplementedError
                index -= 1
            else:
                augmentation = Augmentation(0, None)

            return Group(atom, absolute, octave, augmentation, duration, node)

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


# print(abstracttree(""" # first
#   # second
# line1   # third
# line2    # fourth
#      # fifth
# line3      # sixth
#        # seventh
#         # eighth
# """))
