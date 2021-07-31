# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Union, Generator

import lark

import doremi.parsing


def is_rest(word: str) -> bool:
    return all(x == "_" for x in word)


@dataclass
class AbstractNote:
    start: float
    stop: float
    word: "Word"
    emphasis: int = field(default=0)
    octave: int = field(default=0)
    augmentations: Tuple["Augmentation"] = field(default=())

    def copy(self) -> "AbstractNote":
        return AbstractNote(
            self.start,
            self.stop,
            self.word,
            self.emphasis,
            self.octave,
            self.augmentations,
        )

    def inplace_shift(self, shift: float) -> None:
        self.start += shift
        self.stop += shift

    def inplace_scale(self, scale: float) -> None:
        self.start *= scale
        self.stop *= scale


@dataclass
class Scope:
    symbols: Dict[lark.lexer.Token, "NamedPassage"]

    def has(self, symbol: lark.lexer.Token) -> bool:
        return symbol in self.symbols

    def get(self, symbol: lark.lexer.Token) -> Optional["NamedPassage"]:
        return self.symbols.get(symbol)

    def add(self, passage: "NamedPassage"):
        self.symbols[passage.assignment.function.val] = passage


@dataclass
class SubScope(Scope):
    parent: Scope

    def has(self, symbol: lark.lexer.Token) -> bool:
        if symbol in self.symbols:
            return True
        else:
            return self.parent.has(symbol)

    def get(self, symbol: lark.lexer.Token) -> Optional["NamedPassage"]:
        out = self.symbols.get(symbol)
        if out is not None:
            return out
        else:
            return self.parent.get(symbol)


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
    is_scaling: bool
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


@dataclass
class Modified(AST):
    expression: Union[Expression, List[Expression]]
    emphasis: int
    absolute: int
    octave: int
    augmentation: Augmentation
    duration: Optional[Duration]
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


class Passage(AST):
    pass


@dataclass
class NamedPassage(Passage):
    assignment: Assignment
    lines: List[Line]
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


@dataclass
class UnnamedPassage(Passage):
    lines: List[Line]
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )


def evaluate(
    node: Union[list, Word, Call, Modified, Line, Passage],
    scope: Scope,
    emphasis: int,
    octave: int,
    augmentations: Tuple[Augmentation],
    breadcrumbs: Tuple[str],
) -> Tuple[float, List[AbstractNote]]:

    if isinstance(node, list):
        last_stop = 0.0
        all_notes = []
        for subnode in node:
            duration, notes = evaluate(
                subnode, scope, emphasis, octave, augmentations, breadcrumbs
            )
            for note in notes:
                note.inplace_shift(last_stop)

            all_notes.extend(notes)
            last_stop += duration

        return last_stop, all_notes

    elif isinstance(node, Word):
        if scope.has(node.val):
            return evaluate(
                Call(node, []), scope, emphasis, octave, augmentations, breadcrumbs
            )
        elif is_rest(node.val):
            return float(len(node.val)), []
        else:
            note = AbstractNote(
                0.0,
                1.0,
                node,
                emphasis,
                octave,
                augmentations,
            )
            return 1.0, [note]

    elif isinstance(node, Call):
        if node.function.val in breadcrumbs:
            raise RecursiveFunction(node.function.val)

        namedpassage = scope.get(node.function.val)
        if namedpassage is None:
            raise UndefinedSymbol(node.function.val)

        parameters = namedpassage.assignment.args
        arguments = node.args
        if len(parameters) != len(arguments):
            raise MismatchingArguments(node.function.val)

        subscope = SubScope(
            {
                param.val: NamedPassage(Assignment(param, []), [arg])
                for param, arg in zip(parameters, arguments)
            },
            scope,
        )
        breadcrumbs = breadcrumbs + (node.function.val,)
        return evaluate(
            namedpassage, subscope, emphasis, octave, augmentations, breadcrumbs
        )

    elif isinstance(node, Modified):
        if node.absolute > 0:
            augmentations = augmentations[: -node.absolute]
        if node.augmentation is not None:
            augmentations = augmentations + (node.augmentation,)

        if isinstance(node.expression, Expression):
            natural_duration, notes = evaluate(
                node.expression,
                scope,
                emphasis + node.emphasis,
                octave + node.octave,
                augmentations,
                breadcrumbs,
            )

        else:
            natural_duration, notes = evaluate(
                node.expression,
                scope,
                emphasis + node.emphasis,
                octave + node.octave,
                augmentations,
                breadcrumbs,
            )

        if node.duration is not None:
            if node.duration.is_scaling:
                factor = float(node.duration.amount)
                natural_duration = natural_duration * factor
            else:
                factor = float(node.duration.amount) / natural_duration
                natural_duration = float(node.duration.amount)
            for note in notes:
                note.inplace_scale(factor)

        if node.repetition == 1:
            duration = natural_duration

        else:
            all_notes = list(notes)
            for i in range(1, node.repetition):
                new_notes = [x.copy() for x in notes]
                for note in new_notes:
                    note.inplace_shift(i * natural_duration)
                all_notes.extend(new_notes)

            duration = node.repetition * natural_duration
            notes = all_notes

        return duration, notes

    elif isinstance(node, Line):
        return evaluate(
            node.modified, scope, emphasis, octave, augmentations, breadcrumbs
        )

    elif isinstance(node, Passage):
        max_duration = 0.0
        all_notes = []
        for line in node.lines:
            duration, notes = evaluate(
                line, scope, emphasis, octave, augmentations, breadcrumbs
            )

            all_notes.extend(notes)
            if max_duration < duration:
                max_duration = duration

        return max_duration, all_notes

    else:
        raise AssertionError(repr(node))


@dataclass
class Collection(AST):
    passages: List[Passage]
    comments: Optional[List[lark.lexer.Token]] = field(
        default=None, repr=False, compare=False, hash=False
    )
    parsingtree: Optional[lark.tree.Tree] = field(
        default=None, repr=False, compare=False, hash=False
    )
    source: Optional[str] = field(default=None, repr=False, compare=False, hash=False)

    def evaluate(
        self, scope: Optional[Scope]
    ) -> Tuple[float, List[AbstractNote], Scope]:
        if scope is None:
            scope = Scope({})
        unnamed_passages: List[UnnamedPassage] = []
        for passage in self.passages:
            if isinstance(passage, NamedPassage):
                scope.add(passage)
            else:
                unnamed_passages.append(passage)

        try:
            duration, notes = evaluate(unnamed_passages, scope, 0, 0, (), ())
        except DoremiError as err:
            err.context = self.source
            raise

        return duration, notes, scope


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

            passage = subnodes[-1]
            assert isinstance(passage, lark.tree.Tree) and passage.data == "passage"
            lines = [
                to_ast(x)
                for x in passage.children
                if not isinstance(x, lark.lexer.Token)
            ]

            if len(subnodes) == 2:
                return NamedPassage(to_ast(subnodes[0]), lines, node)
            else:
                assert len(subnodes) == 1
                return UnnamedPassage(lines, node)

        elif node.data == "assign":
            assert 1 <= len(node.children) <= 2

            subnode1 = node.children[0]
            assert isinstance(subnode1, lark.lexer.Token) and subnode1.type == "WORD"
            if is_rest(subnode1):
                raise SymbolAllUnderscores(subnode1)

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

            if node.children[index].data == "emphasis":
                emphasis = len(node.children[index].children)
                index += 1
            else:
                emphasis = 0

            if node.children[index].data == "absolute":
                absolute = len(node.children[index].children)
                index += 1
            else:
                absolute = 0

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
                    expression = Call(function, args, subnode)

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
                    duration = Duration(Fraction(len(subnode.children), 1), False)
                elif (
                    subnode.data == "ratio_duration" or subnode.data == "scale_duration"
                ):
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
                    duration = Duration(
                        ratio, subnode.data == "scale_duration", subnode
                    )
                else:
                    raise AssertionError(subnode)

                index -= 1

            else:
                duration = None

            if node.children[index].data == "augmentation":
                subnode = node.children[index].children[0]

                if subnode.data == "upward_step" or subnode.data == "downward_step":
                    subnodes = subnode.children
                    if len(subnodes) == 1:
                        assert isinstance(subnodes[0], lark.lexer.Token)
                        if subnodes[0].type == "STEP_UPS":
                            amount = len(subnodes[0])
                        elif subnodes[0].type == "STEP_DOWNS":
                            amount = -len(subnodes[0])
                        else:
                            raise AssertionError(repr(subnodes[0]))
                    elif len(subnodes) == 2:
                        assert isinstance(subnodes[0], lark.lexer.Token)
                        assert isinstance(subnodes[1], lark.lexer.Token)
                        assert subnodes[1].type == "INT"
                        if subnodes[0].type == "STEP_UP":
                            amount = int(subnodes[1])
                        elif subnodes[0].type == "STEP_DOWN":
                            amount = -int(subnodes[1])
                        else:
                            raise AssertionError(repr(subnodes[0]))
                    else:
                        raise AssertionError(len(subnodes))

                    if amount == 0:
                        augmentation = None
                    else:
                        augmentation = AugmentStep(amount, subnode)

                elif (
                    subnode.data == "upward_degree" or subnode.data == "downward_degree"
                ):
                    subnodes = subnode.children
                    if len(subnodes) == 1:
                        assert isinstance(subnodes[0], lark.lexer.Token)
                        if subnodes[0].type == "DEGREE_UPS":
                            amount = len(subnodes[0])
                        elif subnodes[0].type == "DEGREE_DOWNS":
                            amount = -len(subnodes[0])
                        else:
                            raise AssertionError(repr(subnodes[0]))
                    elif len(subnodes) == 2:
                        assert isinstance(subnodes[0], lark.lexer.Token)
                        assert isinstance(subnodes[1], lark.lexer.Token)
                        assert subnodes[1].type == "INT"
                        if subnodes[0].type == "DEGREE_UP":
                            amount = int(subnodes[1])
                        elif subnodes[0].type == "DEGREE_DOWN":
                            amount = -int(subnodes[1])
                        else:
                            raise AssertionError(repr(subnodes[0]))
                    else:
                        raise AssertionError(len(subnodes))

                    if amount == 0:
                        augmentation = None
                    else:
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

                    if ratio == Fraction(1, 1):
                        augmentation = None
                    else:
                        augmentation = AugmentRatio(ratio, subnode)

                index -= 1

            else:
                augmentation = None

            if node.children[index].data == "octave":
                subnodes = node.children[index].children[0].children

                if len(subnodes) == 1:
                    assert isinstance(subnodes[0], lark.lexer.Token)
                    if subnodes[0].type == "OCTAVE_UPS":
                        octave = len(subnodes[0])
                    elif subnodes[0].type == "OCTAVE_DOWNS":
                        octave = -len(subnodes[0])
                    else:
                        raise AssertionError(repr(subnodes[0]))
                elif len(subnodes) == 2:
                    assert isinstance(subnodes[0], lark.lexer.Token)
                    assert isinstance(subnodes[1], lark.lexer.Token)
                    assert subnodes[1].type == "INT"
                    if subnodes[0].type == "OCTAVE_UP":
                        octave = int(subnodes[1])
                    elif subnodes[0].type == "OCTAVE_DOWN":
                        octave = -int(subnodes[1])
                    else:
                        raise AssertionError(repr(subnodes[0]))
                else:
                    raise AssertionError(len(subnodes))

                index -= 1

            else:
                octave = 0

            return Modified(
                expression,
                emphasis,
                absolute,
                octave,
                augmentation,
                duration,
                repetition,
                node,
            )

        raise AssertionError(repr(node))

    else:
        if node.type == "WORD":
            return Word(node)

        elif node.type == "CARDINAL":
            return Word(node)

        else:
            raise AssertionError(repr(node))


def abstracttree(source: str) -> AST:
    parsingtree = doremi.parsing.parsingtree(source)
    assert parsingtree.data == "start"

    try:
        comments = list(get_comments(parsingtree))
    except DoremiError as err:
        err.context = source
        raise

    for i, x in enumerate(comments):
        assert i + 1 == x.line, [x.line for x in comments]

    try:
        passages = [
            to_ast(x)
            for x in parsingtree.children
            if not isinstance(x, lark.lexer.Token)
        ]
    except DoremiError as err:
        err.context = source
        raise

    return Collection(passages, comments, parsingtree, source)


class DoremiError(Exception):
    error_message: str
    node: Union[lark.lexer.Token, lark.tree.Tree]
    context: Optional[str]

    def __str__(self) -> str:
        out = f"{self.error_message} on line {self.node.line}"

        if self.context is None:
            return out
        else:
            line = self.context.splitlines()[self.node.line - 1]

            return f"""{out}

    {line}
    {"-" * (self.node.column - 1) + "^"}"""


class SymbolAllUnderscores(DoremiError):
    def __init__(self, node: lark.tree.Tree):
        self.error_message = "symbols must not consist entirely of underscores (rest)"
        self.node = node
        self.context = None


class RecursiveFunction(DoremiError):
    def __init__(self, node: lark.tree.Tree):
        self.error_message = f"function (indirectly?) calls itself: {str(node)!r}"
        self.node = node
        self.context = None


class UndefinedSymbol(DoremiError):
    def __init__(self, node: lark.lexer.Token):
        self.error_message = (
            f"symbol has not been defined (misspelling?): {str(node)!r}"
        )
        self.node = node
        self.context = None


class MismatchingArguments(DoremiError):
    def __init__(self, node: lark.tree.Tree):
        self.error_message = "wrong number of arguments in function call"
        self.node = node
        self.context = None


class NoteNotInScale(DoremiError):
    def __init__(self, node: lark.tree.Tree):
        self.error_message = (
            "cannot augment by a scale degree because this note is not in the scale"
        )
        self.node = node
        self.context = None
