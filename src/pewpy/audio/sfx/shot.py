"""The bullets' sound."""

from pewpy.audio.sfx.shaping import fade, glide
from pewpy.audio.synth import FloatArray, highpass, oscillator


def shot() -> FloatArray:
    """The bullets: a quick falling "pew"."""
    tone = oscillator("square", glide(0.09, 1500, 320, 2.0))
    return fade(highpass(tone, 250), 0.035) * 0.3
