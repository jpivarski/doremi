# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

import subprocess


# \version "2.20.0"
# \paper {
#   page-breaking = #ly:one-line-auto-height-breaking
#   oddFooterMarkup = ##f
#   oddHeaderMarkup = ##f
#   bookTitleMarkup = ##f
#   scoreTitleMarkup = ##f
# }
# \parallelMusic voiceA,voiceB,voiceC {
# c''4 r4 g'' g'' a'' a'' g''2 c''4 c'' g'' g'' a'' a'' g''2 c''4 c'' g''8 g''8 ais''8 aes''8 g''2 |
# c'4 r4 g'2 g'4 a' g'2 c'4 c' g'2 g'4 a' g'2 c'4 c' g'8 g'8 ais'8 aes'8 g'2 |
# c4 r4 g g a a g2 c4 c g g a a g2 c4 c g8 g8 ais8 aes8 g2 |
# }
# \new StaffGroup <<
#   \new Staff \with { \consists "Merge_rests_engraver" } << \voiceA \\ \voiceB >>
#   \new Staff \with { \consists "Merge_rests_engraver" } { \clef bass \voiceC }
# >>
