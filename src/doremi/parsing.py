# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

import lark


grammar = r"""
start: BLANK* assign_passage (BLANK BLANK+ assign_passage)* BLANK_END*

assign_passage: assign "=" BLANK? passage | passage
assign: WORD | WORD "(" defargs? ")"
defargs: WORD+
passage: line (BLANK line)*

line: modified+
modified: emphasis? absolute? expression octave? augmentation? duration? repetition?

emphasis: EMPHASIS+
absolute: ABSOLUTE+
octave: upward_octave | downward_octave
upward_octave: OCTAVE_UP INT | OCTAVE_UPS
downward_octave: OCTAVE_DOWN INT | OCTAVE_DOWNS

augmentation: upward_step | downward_step | upward_degree | downward_degree | ratio_tune
upward_step: STEP_UPS | STEP_UP INT
downward_step: STEP_DOWNS | STEP_DOWN INT
upward_degree: DEGREE_UPS | DEGREE_UP INT
downward_degree: DEGREE_DOWNS | DEGREE_DOWN INT
ratio_tune: "*" ratio

duration: dot_duration | ratio_duration
dot_duration: DOT+
ratio_duration: ":" ratio

repetition: "~" POSITIVE_INT

ratio: POSITIVE_INT ("/" POSITIVE_INT)?
expression: WORD | WORD "(" args? ")" | "{" modified+ "}"
args: modified+

EMPHASIS: "!"
ABSOLUTE: "@"
OCTAVE_UP: "'"
OCTAVE_UPS: /\'+/
OCTAVE_DOWN: ","
OCTAVE_DOWNS: /,+/
STEP_UP: "+"
STEP_UPS: /\++/
STEP_DOWN: "-"
STEP_DOWNS: /-+/
DEGREE_UP: ">"
DEGREE_UPS: />+/
DEGREE_DOWN: "<"
DEGREE_DOWNS: /<+/
DOT: "."

INT: /(0|[1-9][0-9]*)/
POSITIVE_INT: /[1-9][0-9]*/
WORD: /[\p{L}_#][\p{L}_#0-9]*/

WS: /[ \t]/+
BLANK: /(\n|\|[^\n]*\n)/
BLANK_END: /(\n|\|[^\n]*\n|\|[^\n]*)/

%ignore WS
"""


def parsingtree(source: str) -> lark.tree.Tree:
    return parsingtree.parser.parse(source)


parsingtree.parser = lark.Lark(grammar, regex=True)

__all__ = "parser"
