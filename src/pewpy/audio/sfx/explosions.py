"""Explosions, small to big, the player's, and a missile's blast."""

import numpy as np

from pewpy.audio.sfx.shaping import boom, glide, span
from pewpy.audio.synth import FloatArray, lowpass, oscillator


def explosion_small() -> FloatArray:
    return boom(0.45, 4000, 160, 9) * 0.6


def explosion() -> FloatArray:
    return boom(0.9, 3000, 110, 10) * 0.8


def explosion_big() -> FloatArray:
    """A boss going down."""
    return boom(2.4, 2200, 80, 11)


def player_explosion() -> FloatArray:
    """The player's ship destroyed: a big blast and a falling wail."""
    t = span(1.6)
    wail = oscillator("saw", glide(1.6, 880, 55, 2.0)) * np.exp(-t / 0.6) * 0.3
    return np.tanh(boom(1.6, 3000, 90, 12) + lowpass(wail, 2500))


def blast() -> FloatArray:
    """A missile exploding."""
    return boom(0.5, 3500, 130, 14) * 0.55
