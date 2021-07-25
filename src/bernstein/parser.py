# BSD 3-Clause License; see https://github.com/jpivarski/bernstein/blob/main/LICENSE

import lark

grammar = r"""
start: blank* lhs_passages blank*

lhs_passages: lhs_passage (blank+ lhs_passage)+
lhs_passage: lhs "=" blank? passage | passage
lhs: word | word "(" args? ")"
args: word ("," word)*
passage: line (blank line)*

line: decorated+
decorated: absolute? octave? atom augmentation? duration?

absolute: ABSOLUTE+

octave: upward_octave | downward_octave
upward_octave: (DEGREE_UP* | INT) DEGREE_UP
downward_octave: (DEGREE_DOWN* | INT) DEGREE_DOWN

augmentation: upward_step | downward_step | upward_degree | downward_degree
upward_step: STEP_UP (STEP_UP* | INT)
downward_step: STEP_DOWN (STEP_DOWN* | INT)
upward_degree: DEGREE_UP (DEGREE_UP* | INT)
downward_degree: DEGREE_DOWN (DEGREE_DOWN* | INT)

duration: dot_duration | ratio_duration
dot_duration: DOT+
ratio_duration: ":" INT ("/" INT)?

atom: word | "{" decorated+ "}"
word: /[A-Za-z_#][A-Za-z_#0-9]+/

STEP_UP: "+"
STEP_DOWN: "-"
DEGREE_UP: ">"
DEGREE_DOWN: "<"
ABSOLUTE: "@"
DOT: "."
blank: /([ \t]*\#[^\n]*)?\n/

%import common.SH_COMMENT
%import common.INT
%import common.CR
%import common.LF
%import common.WS_INLINE

%ignore WS_INLINE
"""

parser = lark.Lark(grammar)

print(parser.parse("""
# stuff
hello>2... there.. @@@you:12

some(one, two) = {hey 2>wow}:12/3
things

""").pretty())
