"""The lightning gun striking."""

from pewpy.audio.sfx.shaping import fade, glide, span
from pewpy.audio.synth import FloatArray, highpass, noise, oscillator


def zap() -> FloatArray:
    """Make the sound of the lightning gun striking: a crackling buzz, quickly gone."""
    t = span(0.18)
    buzz = oscillator("saw", glide(0.18, 1400, 500)) * (noise(len(t), 21) > 0.2)
    return fade(highpass(buzz + 0.6 * noise(len(t), 22), 600), 0.06) * 0.35
