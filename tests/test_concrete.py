# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

from fractions import Fraction

import doremi


def test_show_notes():
    composition = doremi.compose("do.... do'.... so.... la\nmi........ mi....")
    composition.show_notes()


def test_augmentation():
    assert doremi.compose("1st'", "C major").notes()[0].note.pitch == 60
    assert doremi.compose("2nd'", "C major").notes()[0].note.pitch == 62
    assert doremi.compose("3rd'", "C major").notes()[0].note.pitch == 64
    assert doremi.compose("4th'", "C major").notes()[0].note.pitch == 65
    assert doremi.compose("5th'", "C major").notes()[0].note.pitch == 67
    assert doremi.compose("6th'", "C major").notes()[0].note.pitch == 69
    assert doremi.compose("7th'", "C major").notes()[0].note.pitch == 71

    assert doremi.compose("do'", "C major").notes()[0].note.pitch == 60

    assert doremi.compose("do'+", "C major").notes()[0].note.pitch == 61
    assert doremi.compose("do'++", "C major").notes()[0].note.pitch == 62
    assert doremi.compose("do'+3", "C major").notes()[0].note.pitch == 63
    assert doremi.compose("do'-", "C major").notes()[0].note.pitch == 59
    assert doremi.compose("do'--", "C major").notes()[0].note.pitch == 58
    assert doremi.compose("do'-3", "C major").notes()[0].note.pitch == 57

    assert doremi.compose("do>").notes()[0].note == doremi.compose("re").notes()[0].note
    assert (
        doremi.compose("do>>").notes()[0].note == doremi.compose("mi").notes()[0].note
    )
    assert (
        doremi.compose("do>3").notes()[0].note == doremi.compose("fa").notes()[0].note
    )
    assert (
        doremi.compose("do>4").notes()[0].note == doremi.compose("so").notes()[0].note
    )
    assert (
        doremi.compose("do>5").notes()[0].note == doremi.compose("la").notes()[0].note
    )
    assert (
        doremi.compose("do>6").notes()[0].note == doremi.compose("ti").notes()[0].note
    )
    assert (
        doremi.compose("do>7").notes()[0].note == doremi.compose("do'").notes()[0].note
    )
    assert (
        doremi.compose("do>8").notes()[0].note == doremi.compose("re'").notes()[0].note
    )
    assert (
        doremi.compose("do>9").notes()[0].note == doremi.compose("mi'").notes()[0].note
    )

    assert (
        doremi.compose("do'>").notes()[0].note == doremi.compose("re'").notes()[0].note
    )
    assert (
        doremi.compose("do'>>").notes()[0].note == doremi.compose("mi'").notes()[0].note
    )
    assert (
        doremi.compose("do'>3").notes()[0].note == doremi.compose("fa'").notes()[0].note
    )
    assert (
        doremi.compose("do'>4").notes()[0].note == doremi.compose("so'").notes()[0].note
    )
    assert (
        doremi.compose("do'>5").notes()[0].note == doremi.compose("la'").notes()[0].note
    )
    assert (
        doremi.compose("do'>6").notes()[0].note == doremi.compose("ti'").notes()[0].note
    )
    assert (
        doremi.compose("do'>7").notes()[0].note
        == doremi.compose("do''").notes()[0].note
    )
    assert (
        doremi.compose("do'>8").notes()[0].note
        == doremi.compose("re''").notes()[0].note
    )
    assert (
        doremi.compose("do'>9").notes()[0].note
        == doremi.compose("mi''").notes()[0].note
    )

    assert (
        doremi.compose("do<").notes()[0].note == doremi.compose("ti,").notes()[0].note
    )
    assert (
        doremi.compose("do<<").notes()[0].note == doremi.compose("la,").notes()[0].note
    )
    assert (
        doremi.compose("do<3").notes()[0].note == doremi.compose("so,").notes()[0].note
    )
    assert (
        doremi.compose("do<4").notes()[0].note == doremi.compose("fa,").notes()[0].note
    )
    assert (
        doremi.compose("do<5").notes()[0].note == doremi.compose("mi,").notes()[0].note
    )
    assert (
        doremi.compose("do<6").notes()[0].note == doremi.compose("re,").notes()[0].note
    )
    assert (
        doremi.compose("do<7").notes()[0].note == doremi.compose("do,").notes()[0].note
    )
    assert (
        doremi.compose("do<8").notes()[0].note == doremi.compose("ti,,").notes()[0].note
    )
    assert (
        doremi.compose("do<9").notes()[0].note == doremi.compose("la,,").notes()[0].note
    )

    assert (
        doremi.compose("do,<").notes()[0].note == doremi.compose("ti,,").notes()[0].note
    )
    assert (
        doremi.compose("do,<<").notes()[0].note
        == doremi.compose("la,,").notes()[0].note
    )
    assert (
        doremi.compose("do,<3").notes()[0].note
        == doremi.compose("so,,").notes()[0].note
    )
    assert (
        doremi.compose("do,<4").notes()[0].note
        == doremi.compose("fa,,").notes()[0].note
    )
    assert (
        doremi.compose("do,<5").notes()[0].note
        == doremi.compose("mi,,").notes()[0].note
    )
    assert (
        doremi.compose("do,<6").notes()[0].note
        == doremi.compose("re,,").notes()[0].note
    )
    assert (
        doremi.compose("do,<7").notes()[0].note
        == doremi.compose("do,,").notes()[0].note
    )
    assert (
        doremi.compose("do,<8").notes()[0].note
        == doremi.compose("ti,,,").notes()[0].note
    )
    assert (
        doremi.compose("do,<9").notes()[0].note
        == doremi.compose("la,,,").notes()[0].note
    )

    assert (
        doremi.compose("do % 2").notes()[0].note
        == doremi.compose("do'").notes()[0].note
    )
    assert (
        doremi.compose("do % 4").notes()[0].note
        == doremi.compose("do''").notes()[0].note
    )
    assert (
        doremi.compose("do % 1/2").notes()[0].note
        == doremi.compose("do,").notes()[0].note
    )
    assert (
        doremi.compose("do % 1/4").notes()[0].note
        == doremi.compose("do,,").notes()[0].note
    )


def test_emphasis():
    notes = doremi.compose("do !do do").notes()
    assert notes[0].emphasis == 1.0 / 2.0
    assert notes[1].emphasis == 1.0
    assert notes[2].emphasis == 1.0 / 2.0

    notes = doremi.compose("do !!do do").notes()
    assert notes[0].emphasis == 1.0 / 3.0
    assert notes[1].emphasis == 1.0
    assert notes[2].emphasis == 1.0 / 3.0

    assert doremi.compose("do !do do").midi_events() == [
        (0.00, [(48, 64)]),
        (0.25, [(48, 0), (48, 127)]),
        (0.50, [(48, 0), (48, 64)]),
        (0.75, [(48, 0)]),
    ]
