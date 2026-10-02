"""A small synthesizer: plays MIDI songs (see pewpy.audio.midi) as audio, the 80s-synth way. Numpy only, no Panda3D.

Every channel's General MIDI program picks one of a few instruments (a bass, a pad, a lead, an arpeggio pluck,
keys); channel 9 holds the drums. Notes are drawn with band-limited oscillators, filtered with an envelope, and
mixed through the effects of the style: a stereo delay, a long reverb, a short gated reverb on the snare, and the
pads and bass ducking under the kick drum. Each stage in its own module: oscillators.py, filters.py, instruments.py
(and voices.py playing them), drums.py, effects.py, render.py.
"""

from pewpy.audio.synth.drums import DRUM_PANS, drum
from pewpy.audio.synth.effects import convolve, ducking, echo, impulse
from pewpy.audio.synth.filters import highpass, lowpass
from pewpy.audio.synth.instruments import BASS, BRASS, KEYS, LEAD, PAD, PLUCK, Instrument, instrument
from pewpy.audio.synth.oscillators import noise, oscillator
from pewpy.audio.synth.render import place, render, wav_bytes
from pewpy.audio.synth.signal import RATE, TAIL, FloatArray, frequency
from pewpy.audio.synth.voices import envelope, play_note, voice

__all__ = [
    "BASS",
    "BRASS",
    "DRUM_PANS",
    "KEYS",
    "LEAD",
    "PAD",
    "PLUCK",
    "RATE",
    "TAIL",
    "FloatArray",
    "Instrument",
    "convolve",
    "drum",
    "ducking",
    "echo",
    "envelope",
    "frequency",
    "highpass",
    "impulse",
    "instrument",
    "lowpass",
    "noise",
    "oscillator",
    "place",
    "play_note",
    "render",
    "voice",
    "wav_bytes",
]
