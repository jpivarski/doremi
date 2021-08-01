# Doremi (do-re-mi)

**The distraction-free text editor of musical programming languages.**

Try it out!

<p align="center">
  <a href="https://mybinder.org/v2/gh/jpivarski/doremi/main?urlpath=lab/tree/empty-template.ipynb">
    <img src="https://mybinder.org/badge_logo.svg" alt="Launch Binder" height="40">
  </a>
</p>

## Motivation

Since I've been tinkering with music composition, mostly to understand it better, I thought it could help if I could construct music out of functions. A lot of musical passages walk up or down the scale in patterns of one or two scale degrees, which would be easier to write as a formula into which I could plug in values (thinking like a programmer). So I looked into [musical programming languages](https://en.wikipedia.org/wiki/List_of_audio_programming_languages), but...

   1. Many of them operate at too low of a level: sound synthesis, rather than plain piano keys. By analogy, if music were text, I'd want a text editor, not a graphical design suite.
   2. Even the ones that stick to a piano's 12 equal-tempered tones operate at the level of absolute pitch. Layering musical passages makes more sense (to me) in relative pitch.
   3. Many of these languages aren't intended for composition; they expect you to know which notes you want to write before you write them. (Can you believe that?)
   4. Very few allow for functional composition, and most of those are dialects of Lisp or Forth, which gets too far away from the musical mindset.

Doremi is a simple language for jotting down musical ideas and immediately hearing what they sound like, particularly as functions:

```
f(x) = do x

f(so) f(la) f(ti) f(la)
```

is the same as

```
do so do la do ti do la
```

The use of solfège, rather than absolute pitches, keeps me in a relative mindset, and duration is primarily expressed with the length of ASCII art dots, rather than numbers:

```
do.. fa.... la do la.... so.. fa.... re.. do....
```

## Installation

Doremi is not on PyPI or conda-forge yet, so you'll have to install it from this repo. Beyond its built-in Python dependencies, it requires [FluidSynth](https://www.fluidsynth.org/) to synthesize sounds, and someday [Lilypond](http://lilypond.org/) to generate images of music in standard notation. Both are only required if you use their functionality, though it's hard to imagine not wanting to synthesizing sounds (perhaps we could [write MIDI files](https://pypi.org/project/MIDIUtil)?).

```bash
# get fluidsynth from a standard distribution, such as apt or conda
apt install fluidsynth
conda install -c conda-forge fluidsynth

# note: lilypond is not used yet
apt install lilypond

git clone https://github.com/jpivarski/doremi.git
cd doremi
pip install .   # gets Python dependencies (lark, regex, numpy)
```

## Set-up

The [empty-template.ipynb](https://github.com/jpivarski/doremi/blob/main/empty-template.ipynb) consists of the following:

```python
import doremi

doremi.compose("""

do.. re.. mi..

""").play()
```

Python is the host/implementation language; Doremi is inside the quoted string. The `compose` function can also

   * take a `scale` as a second argument (e.g. `"major"`, `"D minor"`, `"E Mixolydian"`, `"WholeTone"`) with 1490 modes to choose from, thanks to [allthescales.org](https://allthescales.org/). Alternatively, the scale can be constructed as a dict mapping note name (`str`) → pitch (`float` frequency or `str` note name)
   * take `bpm` (beats per minute) as a third argument (default is 120 BPM)

and a `Composition` object can

   * report `duration_in_seconds`
   * return a N×2 (stereo) sound waveform array from `fluidsynth()` (with `dtype` as `np.int16` or `np.float32`); uses [Nice-Steinway-Lite-v3.0.sf2](https://github.com/jpivarski/doremi/blob/main/src/doremi/data/Nice-Steinway-Lite-v3.0.sf2) from [soundfonts4u](https://sites.google.com/site/soundfonts4u/) or your own `soundfont`
   * `play()` the waveform in Jupyter (as shown above)
   * `show_notes()` as ASCII text

(future: `show()` an SVG graph of notes in Jupyter and show notes in standard musical notation with `lilypond`).

## Musical language

A basic composition is a line of [solfège](https://en.wikipedia.org/wiki/Solf%C3%A8ge) names on a single line, in which each note is followed by dots to indicate duration. One dot (or no dots) is an eighth note, two dots is a quarter note, four dots is a half note, eight dots is a whole note, etc.

A line of music should look a bit like ASCII art, with the horizontal scale roughly proportional to time.

```
mi mi mi do......
```

Rests (no sound) are underscores with the same lengths as dots.

```
mi mi mi ___ do......
```

### Notes

For our purposes, the solfège names of the 12 notes of a (equal-tempered) chromatic scale are

| name          | do | ra | re | me | mi | fa | se | so | le | la | te | ti |
|:--------------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| half-steps    | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | 10 | 11 |
| pronunciation | /doʊ/ | /ɹɑː/ | /ɹeɪ/ | /meɪ/ | /miː/ | /fɑː/ | /seɪ/ | /soʊ/ | /leɪ/ | /lɑː/ | /teɪ/ | /tiː/ |

This is a "moveable do" system: the _relative_ pitches of these notes are fixed, but the _absolute_ pitch of "do" is the key signature of the `scale` (passed to `compose` in Python; see above). If you want to transpose a composition, just pass a different scale name as the second argument of `compose`.

If you provide a `scale` as a Python dict, rather than picking one from the database, you can name the notes whatever you like, such as

```python
{"Sa": "c3", "Ri": "d3", "Ga": "e3", "Ma": "f3", "Pa": "g3", "Dha": "a3", "Ni": "b3"}
```

or

```python
{"স": "c3", "র": "d3", "গ": "e3", "ম": "f3", "প": "g3", "ধ": "a3", "ন": "b3"}
```

or (just-tempered)

```python
c3 = 130.82  # Hz
{"do": c3, "re": c3 * 9/8, "mi": c3 * 5/4, "fa": c3 * 4/3, "so": c3 * 3/2, "la": c3 * 5/3, "ti": c3 * 15/8}
```

(Note: at the moment, non-equal tempered notes can't be synthesized, so a just-tempered scale can't be played.)

In addition, the scale degrees can be referenced directly as `1st`, `2nd`, `3rd`, `4th`, etc. In a major scale, the following are equivalent:

```
mi mi mi do......
```

and

```
3rd 3rd 3rd 1st......
```

but set `scale="minor"` and the second becomes

```
me me me do......
```

Solfège is relative to the key, but scale degrees depend on the mode of the scale (and are good for exploring weird modes).

### Harmony

Sequential notes have to be arranged on a single line without line breaks because multiple lines represent multiple voices or chords.

```
do''.... ti'.... do''........
fa' .... re'.... mi' ........
la  .... so .... so  ........
fa, .... so,.... do  ........
```

![](https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/IV-V-I_in_C.png/320px-IV-V-I_in_C.png)

### Octaves

The single quotes (`'`) and commas (`,`) following each note indicate octaves: in a C scale, `do'` is middle C (following the [Helmholtz convention](https://en.wikipedia.org/wiki/Helmholtz_pitch_notation). Since the name of a note takes a variable number of characters, it can be helpful to line up the dots as much as possible. Rests (expressed as underscores) allow you to line up the notes.

```
do.... so.... me...... re.. do .. me.. re .. do.. ti,.. re.. so,....
  ____   ____   ______   __ do'....    so'....    me'...... re'.. do'....
```

### Long passages

Long musical passages are broken into paragraphs, separated by an empty line, like Markdown or TeX. The following is equivalent to the above:

```
do.... so.... me...... re..
  ____   ____   ______   __

do .. me.. re .. do.. ti,.. re.. so,....
do'....    so'....    me'...... re'.. do'....
```

### Durations

Basic durations are expressed as dots, with

   * one dot (or no dots) equivalent to an eighth note
   * two dots equivalent to a quarter note
   * four dots equivalent to a half note
   * eight dots equivalent to a whole note, etc.

To allow notes shorter than an eighth note, to construct [tuplets](https://en.wikipedia.org/wiki/Tuplet), or to avoid clutter in a slow passage, durations can also be assigned as numbers. The number is separated from the note using a colon (sideways dots) and it can be any _fraction_ (like `1/4`, not `0.25`).

```
mi mi mi do:6
```

is the same as

```
mi mi mi do......
```

To modify the timing of a group of notes, enclose them in curly brackets (`{` and `}`).

```
{mi mi mi}:2 do:4
```

This grouping is a general principle: any modification that applies to a single note applies to a group of notes in curly brackets. For example, octave marks (`'` and `,` described above).

```
{ {mi mi mi}:2 do:4 }'
```

(Plays one octave higher.)

The number after the colon specifies the total duration of the note or group. If, instead, you want to _multiply_ the duration by a factor, use `:*` instead of `:`. The following are equivalent:

```
{do so do le do so do se} : 6
```

and

```
{do so do le do so do se} :* 6/8
```

The first ensures that the phrase takes the time of 6 dots (eighth notes) and the second scales the time by a factor of 6/8. They're equivalent because the phrase itself adds up to 8 dots, but both are provided to avoid having to manually count it.

## Repetition

A note or phrase can be repeated by multiplying it (`*`). As with durations, this can apply to a single note or a group in curly brackets.

```
{do so do le do so do se} * 2
```

or

```
{do so do le do so do se} * 2
do, * 16
```

## Augmentations

The pitch of a note or a group of notes can be tweaked in three ways:

   * adding or subtracting half-steps: `+`, `++`, `+3`, `-1`, `-2`, `---`, etc.
   * shifting up or down by scale degrees: `>`, `>>`, `>3`, `<1`, `<<`, `<<<`, etc.
   * scaling the frequency of the sound: `% 3/2` for a perfect fifth, etc.

The symbols that augment by half-steps are plus (`+`) and minus (`-`), and the symbols that augment by scale degrees are greater than (`>`) and less than (`<`). In both cases, the sign can either be repeated or appear once followed by an integer.

Scaling by a frequency is different: it's always a percent sign (`%`) followed by a _fraction_ (like `3/2`, not `1.5`). (Note: at the moment, non-equal tempered notes can't be synthesized, so frequency-scaled notes can't be played.)

Thus, the phrase

```
do so do le do so do se
```

could have equivalently been written as

```
do so do so+1 do so do so-1
```

but if it were written as

```
do so do so>1 do so do so<1
```

then it would only be equivalent if the scale were `"chromatic"`. Scale degree augmentations are sensitive to the choice of scale; half-step augmentations are not.

## Preventing augmentation

Sometimes, we want to apply pitch augmentations to a group excluding some note, such as the root of the scale (`do` or `1st`). The symbol to keep a note "at where it is" is the at-sign (`@`).

In the following, the `do` is _not_ affected by the `-2` and `-4`.

```
{@do do' ti la so....}

{@do do' ti la so....}-2

{@do do' ti la so....}-4

do re mi le so....
```

(At-signs are cumulative: if two augmentations are applied to the same note, through nested grouping, `@@` would prevent all augmentation but `@` would only prevent the inner-nested augmentation.)

You may be wondering why we use at-signs at all when the above could have been written as

```
do {do' ti la so....}

do {do' ti la so....}-2

do {do' ti la so....}-4

do re mi le so....
```

The answer to that question gets at the core feature of this musical language...

## Defining new symbols

The 12 solfège words (or alternatively, whatever you've defined in your `scale`) and `1st`, `2nd`, `3rd`, `4th`, etc. are only the _first_ words to be defined. New ones can be added through assignment (`=`):

```
cascade = @do do' ti la so....

finale = do re mi le so....

cascade cascade-2 cascade-4 finale
```

These assignments are definitions, which are not played as part of the piece unless explicitly referenced. The only line in the above that gets synthesized into sound is the

```
cascade cascade-2 cascade-4 finale
```

which inserts the `cascade` phrase as though it were a note, augmenting it each time. The `finale` is also a predefined phrase, though these phrases and individual notes can be mixed.

```
cascade cascade-2 cascade-4 do re mi le so....
```

Phrases can also be played concurrently.

```
cascade cascade-2 cascade-4 do re mi le so....
____ cascade cascade-2 cascade-4 do ra do..
```

Also, new symbols can incorporate concurrent voices, such as the chords in this progression:

```
I =
do
mi
so

V =
ti,
re
so

vi =
do
mi
la

IV =
do
fa
la

I V vi IV
```

![](https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/I-V-vi-IV_chord_progression_in_C.png/320px-I-V-vi-IV_chord_progression_in_C.png)

(Perhaps these standard chord names should become built-in symbols.)

## Defining functions

Technically, a user-defined symbol is a zero-argument function. Functions take arguments, which are notes, other predefined phrases, or groups of them. Function arguments are surrounded by parentheses (`(` and `)`), but they are not separated by commas because commas are used to lower octaves. Grouping (with curly brackets) may be necessary to separate arguments.

The following `cascade` is a function of the high note from which the descent starts. It expresses the same musical phrase as in the previous section in a different way.

```
cascade(start) = do start start-1 start-3 start-5....

cascade(do') cascade(te) cascade(le) do re mi le so....
```

The following two argument function twists a familiar phrase around in different ways.

```
f(low high) = low high low high+1 low high low high-1

f(do so) f(do-2 so-2) f(do-4 so+3) do do do....
```
