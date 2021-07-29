# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from fractions import Fraction

import doremi


def test_compose():
    composition = doremi.compose("do ^do so")
    # composition.show_notes()

    # raise Exception
