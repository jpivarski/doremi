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

To allow notes shorter than an eighth note or to avoid clutter in a slow passage, durations can also be given as numbers. The number is separated from the note using a colon (sideways dots)...

Also talk about grouping (`{}`) here.
