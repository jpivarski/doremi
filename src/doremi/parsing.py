# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

import lark

grammar = r"""
start: BLANK* lhs_passage (BLANK+ lhs_passage)* BLANK*

lhs_passage: lhs "=" BLANK? passage | passage
lhs: WORD | WORD "(" defargs? ")"
defargs: WORD ("," WORD)*
passage: line (BLANK line)*

line: modified+
modified: absolute? octave? expression augmentation? duration?

absolute: ABSOLUTE+

octave: upward_octave | downward_octave
upward_octave: (DEGREE_UP* | INT) DEGREE_UP
downward_octave: (DEGREE_DOWN* | INT) DEGREE_DOWN

augmentation: upward_step | downward_step | upward_degree | downward_degree | ratio_tune
upward_step: STEP_UP (STEP_UP* | INT)
downward_step: STEP_DOWN (STEP_DOWN* | INT)
upward_degree: DEGREE_UP (DEGREE_UP* | INT)
downward_degree: DEGREE_DOWN (DEGREE_DOWN* | INT)
ratio_tune: "*" ratio

duration: dot_duration | ratio_duration
dot_duration: DOT+
ratio_duration: ":" ratio

ratio: POSITIVE_INT ("/" POSITIVE_INT)?
expression: WORD | WORD "(" args? ")" | "{" modified+ "}"
args: modified ("," modified)*

INT: /(0|[1-9][0-9]*)/
POSITIVE_INT: /[1-9][0-9]*/
WORD: /[A-Za-z_#][A-Za-z_#0-9]*/
STEP_UP: "+"
STEP_DOWN: "-"
DEGREE_UP: ">"
DEGREE_DOWN: "<"
ABSOLUTE: "@"
DOT: "."
BLANK: /(\n|\#[^\n]*\n|\#[^\n]*)/

%import common.SH_COMMENT
%import common.CR
%import common.LF
%import common.WS_INLINE

%ignore WS_INLINE
"""


def parsingtree(source: str) -> lark.tree.Tree:
    return parsingtree.parser.parse(source)


parsingtree.parser = lark.Lark(grammar)

__all__ = "parser"
