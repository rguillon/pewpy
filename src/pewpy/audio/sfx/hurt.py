"""The player hit."""

from pewpy.audio.sfx.shaping import fade, glide, span
from pewpy.audio.synth import FloatArray, lowpass, noise, oscillator


def hurt() -> FloatArray:
    """The player hit: a harsh buzz, dropping."""
    t = span(0.22)
    buzz = oscillator("square", glide(0.22, 300, 90)) + 0.5 * noise(len(t), 13)
    return fade(lowpass(buzz, 2500), 0.08) * 0.45
