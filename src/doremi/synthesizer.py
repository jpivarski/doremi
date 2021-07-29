# BSD 3-Clause License; see https://github.com/jpivarski/doremi/blob/main/LICENSE

import ctypes
import ctypes.util
import pkg_resources
from typing import List

import numpy

import doremi.concrete


fluidsynth_name = (
    ctypes.util.find_library("fluidsynth")
    or ctypes.util.find_library("libfluidsynth")
    or ctypes.util.find_library("libfluidsynth-2")
    or ctypes.util.find_library("libfluidsynth-1")
)
if fluidsynth_name is None:
    raise ImportError("could not find the fluidsynth library")

fluidsynth = ctypes.CDLL(fluidsynth_name)

new_fluid_settings = fluidsynth.new_fluid_settings
new_fluid_settings.argtypes = []
new_fluid_settings.restype = ctypes.c_void_p

fluid_settings_setnum = fluidsynth.fluid_settings_setnum
fluid_settings_setnum.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
fluid_settings_setnum.restype = ctypes.c_int

fluid_settings_setint = fluidsynth.fluid_settings_setint
fluid_settings_setint.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
fluid_settings_setint.restype = ctypes.c_int

new_fluid_synth = fluidsynth.new_fluid_synth
new_fluid_synth.argtypes = [ctypes.c_void_p]
new_fluid_synth.restype = ctypes.c_void_p

# https://www.fluidsynth.org/api/group__soundfont__management.html#ga0ba0bc9d4a19c789f9969cd22d22bf66
fluid_synth_sfload = fluidsynth.fluid_synth_sfload
fluid_synth_sfload.argtypes = [
    ctypes.c_void_p,  # synth
    ctypes.c_char_p,  # filename: File to load
    ctypes.c_int,  # update_midi_presets: TRUE to re-assign presets for all MIDI channels
    # (equivalent to calling fluid_synth_program_reset())
]
fluid_synth_sfload.restype = ctypes.c_int

# https://www.fluidsynth.org/api/group__midi__messages.html#ga0c2f5db7b19f80f25c1e4263cf78b0d0
fluid_synth_program_select = fluidsynth.fluid_synth_program_select
fluid_synth_program_select.argtypes = [
    ctypes.c_void_p,  # synth
    ctypes.c_int,  # chan: MIDI channel number (0 to MIDI channel count - 1)
    ctypes.c_int,  # sfid: ID of a loaded SoundFont
    ctypes.c_int,  # bank: MIDI bank number
    ctypes.c_int,  # preset: MIDI program number
]
fluid_synth_program_select.restype = ctypes.c_int

# https://www.fluidsynth.org/api/group__midi__messages.html#ga038a0f309e8004f39cb5491514bfac54
fluid_synth_noteon = fluidsynth.fluid_synth_noteon
fluid_synth_noteon.argtypes = [
    ctypes.c_void_p,  # synth
    ctypes.c_int,  # chan: MIDI channel number (0 to MIDI channel count - 1)
    ctypes.c_int,  # key: MIDI note number (0-127)
    ctypes.c_int,  # vel: MIDI velocity (0-127, 0=noteoff)
]
fluid_synth_noteon.restype = ctypes.c_int

fluid_synth_noteoff = fluidsynth.fluid_synth_noteoff
fluid_synth_noteoff.argtypes = [
    ctypes.c_void_p,  # synth
    ctypes.c_int,  # chan
    ctypes.c_int,  # key
]
fluid_synth_noteoff.restype = ctypes.c_int

# https://www.fluidsynth.org/api/group__audio__rendering.html#ga7db368da2d74a73d05feaff4a6bb1da4
fluid_synth_write_float = fluidsynth.fluid_synth_write_float
fluid_synth_write_float.argtypes = [
    ctypes.c_void_p,  # synth
    ctypes.c_int,  # length: Count of audio frames to synthesize
    ctypes.c_void_p,  # lbuf: Array of floats to store left channel of audio
    ctypes.c_int,  # loff: Offset index in 'lout' for first sample
    ctypes.c_int,  # lincr: Increment between samples stored to 'lout'
    ctypes.c_void_p,  # rbuf: Array of floats to store right channel of audio
    ctypes.c_int,  # roff: Offset index in 'rout' for first sample
    ctypes.c_int,  # rincr: Increment between samples stored to 'rout'
]
fluid_synth_write_float.restype = ctypes.c_void_p


class Fluidsynth:
    def __init__(self):
        self.sample_rate = 44100

        self.settings = new_fluid_settings()
        fluid_settings_setnum(self.settings, b"synth.gain", 0.2)
        fluid_settings_setnum(self.settings, b"synth.sample-rate", self.rate)
        fluid_settings_setint(self.settings, b"synth.midi-channels", 256)

        self.synthesizer = new_fluid_synth(self.settings)

        filename = pkg_resources.resource_filename(
            "doremi", "data/Nice-Steinway-Lite-v3.0.sf2"
        )
        self.soundfont = fluid_synth_sfload(self.synthesizer, filename.encode(), 0)

        fluid_synth_program_select(self.synthesizer, 0, self.soundfont, 0, 0)

        self.cache = {}

    def __del__(self):
        delete_fluid_synth(self.synthesizer)
        delete_fluid_settings(self.settings)

    # def synthesize_midi(self, pitch: int, seconds: float) -> np.ndarray:
    #     key = ("M", pitch, seconds)
    #     if key not in self.cache:
    #         fluid_synth_noteon(self.synthesizer, 0, pitch, 127)

    #         samples = int(self.sample_rate * seconds)
    #         buf = ctypes.create_string_buffer(samples * np.float.itemsize)
    #         fluid_synth_write_float(self.synthesizer, samples, buf, 0, 2, buf, 1, 2)
    #         self.cache[key] = np.frombuffer(buf, dtype=np.float)

    #         fluid_synth_noteoff(self.synthesizer, 0, pitch)

    #     return self.cache[key]
