"""The sound effects, synthesized: arcade blips, sweeps and noise bursts. Numpy only, no Panda3D.

Each is a function returning mono samples (-1 to 1) at synth.RATE; EFFECTS names them all. "laser" loops: it
is a whole number of cycles of everything in it, so it repeats without a click.
"""

from collections.abc import Callable

import numpy as np

from pewpy.audio.synth import RATE, FloatArray, highpass, lowpass, noise, oscillator


def _time(seconds: float) -> FloatArray:
    return np.arange(int(seconds * RATE)) / RATE


def _glide(seconds: float, start: float, end: float, curve: float = 1.0) -> FloatArray:
    """A frequency going from `start` to `end` (exponentially, faster at first when `curve` > 1)."""
    progress = (_time(seconds) / seconds) ** (1 / curve)
    return start * (end / start) ** progress


def _fade(signal: FloatArray, decay: float, attack: float = 0.002) -> FloatArray:
    t = np.arange(len(signal)) / RATE
    return signal * np.minimum(t / attack, 1.0) * np.exp(-t / decay)


def _boom(seconds: float, cutoff: float, thump: float, seed: int) -> FloatArray:
    """An explosion: noise whose filter closes as it fades, over a low thump."""
    t = _time(seconds)
    rumble = noise(len(t), seed)
    bright = lowpass(rumble, cutoff)
    dark = lowpass(rumble, cutoff / 6)
    closing = np.exp(-t / (seconds / 5))
    body = (dark + (bright - dark) * closing) * np.exp(-t / (seconds / 3.5))
    low = oscillator("sine", _glide(seconds, thump, thump / 2.5, 3.0)) * np.exp(-t / (seconds / 4))
    return np.tanh(2.2 * body + 0.9 * low) * 0.8


def shot() -> FloatArray:
    """The bullets: a quick falling "pew"."""
    tone = oscillator("square", _glide(0.09, 1500, 320, 2.0))
    return _fade(highpass(tone, 250), 0.035) * 0.3


def missile() -> FloatArray:
    """A missile launched: a rising whoosh."""
    t = _time(0.35)
    whoosh = lowpass(noise(len(t), 7), 2500) * np.sin(np.pi * t / 0.35) ** 2
    tone = oscillator("saw", _glide(0.35, 140, 420)) * 0.25
    return lowpass(whoosh + tone, 3000) * 0.5


def laser() -> FloatArray:
    """The laser's hum, looping (1 s: every frequency a whole number of hertz)."""
    t = _time(1.0)
    hum = oscillator("saw", np.full(len(t), 110.0)) + 0.7 * oscillator("saw", np.full(len(t), 221.0))
    shimmer = 0.25 * oscillator("square", np.full(len(t), 662.0))
    wobble = 0.75 + 0.25 * np.sin(2 * np.pi * 12 * t)
    signal = (hum + shimmer) * wobble
    size = len(signal)  # filtered as one cycle of a repeating signal, so the ends meet
    spectrum = np.fft.rfft(signal)
    spectrum /= np.sqrt(1.0 + (np.fft.rfftfreq(size, 1.0 / RATE) / 1800) ** 4)
    return np.fft.irfft(spectrum, size) * 0.16


def hit() -> FloatArray:
    """An enemy hit: a short metallic tick."""
    t = _time(0.07)
    tick = highpass(noise(len(t), 8), 2500) + 0.6 * oscillator("triangle", np.full(len(t), 1100.0))
    return _fade(tick, 0.015) * 0.3


def explosion_small() -> FloatArray:
    return _boom(0.45, 4000, 160, 9) * 0.6


def explosion() -> FloatArray:
    return _boom(0.9, 3000, 110, 10) * 0.8


def explosion_big() -> FloatArray:
    """A boss going down."""
    return _boom(2.4, 2200, 80, 11)


def player_explosion() -> FloatArray:
    """The player's ship destroyed: a big blast and a falling wail."""
    t = _time(1.6)
    wail = oscillator("saw", _glide(1.6, 880, 55, 2.0)) * np.exp(-t / 0.6) * 0.3
    return np.tanh(_boom(1.6, 3000, 90, 12) + lowpass(wail, 2500))


def hurt() -> FloatArray:
    """The player hit: a harsh buzz, dropping."""
    t = _time(0.22)
    buzz = oscillator("square", _glide(0.22, 300, 90)) + 0.5 * noise(len(t), 13)
    return _fade(lowpass(buzz, 2500), 0.08) * 0.45


def blast() -> FloatArray:
    """A missile exploding."""
    return _boom(0.5, 3500, 130, 14) * 0.55


def pickup() -> FloatArray:
    """A weapon upgrade: a major arpeggio up."""
    parts = []
    for semitones in (0, 4, 7, 12):
        hertz = np.full(int(0.06 * RATE), 1046.5 * 2 ** (semitones / 12))
        parts.append(_fade(oscillator("square", hertz), 0.05, 0.001))
    return lowpass(np.concatenate(parts), 6000) * 0.3


def repair() -> FloatArray:
    """Repaired: a bright glide up with a sparkle."""
    t = _time(0.4)
    glide = oscillator("triangle", _glide(0.4, 400, 1600)) * np.sin(np.pi * t / 0.4)
    sparkle = oscillator("sine", np.full(len(t), 2637.0)) * (np.sin(2 * np.pi * 20 * t) > 0) * t / 0.4 * 0.3
    return (glide + sparkle) * 0.4


def switch() -> FloatArray:
    """The weapon switched: two quick blips."""
    first = _fade(oscillator("square", np.full(int(0.04 * RATE), 660.0)), 0.03, 0.001)
    second = _fade(oscillator("square", np.full(int(0.05 * RATE), 990.0)), 0.035, 0.001)
    return lowpass(np.concatenate([first, np.zeros(int(0.015 * RATE)), second]), 5000) * 0.25


def menu_move() -> FloatArray:
    return _fade(lowpass(oscillator("square", np.full(int(0.045 * RATE), 880.0)), 4000), 0.02, 0.001) * 0.2


def menu_choose() -> FloatArray:
    low = _fade(oscillator("square", np.full(int(0.06 * RATE), 660.0)), 0.05, 0.001)
    high = _fade(oscillator("square", np.full(int(0.12 * RATE), 1320.0)), 0.07, 0.001)
    return lowpass(np.concatenate([low, high]), 5000) * 0.25


def menu_back() -> FloatArray:
    high = _fade(oscillator("square", np.full(int(0.06 * RATE), 880.0)), 0.05, 0.001)
    low = _fade(oscillator("square", np.full(int(0.1 * RATE), 440.0)), 0.06, 0.001)
    return lowpass(np.concatenate([high, low]), 4000) * 0.25


def alarm() -> FloatArray:
    """A boss coming: a two-tone siren, three times."""
    t = _time(1.5)
    hertz = np.where((t * 4).astype(int) % 2 == 0, 620.0, 465.0)
    siren = oscillator("saw", hertz) * (0.6 + 0.4 * np.sin(np.pi * (t * 4 % 1)))
    return _fade(lowpass(siren, 2200), 1.2, 0.01) * 0.3


EFFECTS: dict[str, Callable[[], FloatArray]] = {
    "shot": shot,
    "missile": missile,
    "laser": laser,
    "hit": hit,
    "explosion_small": explosion_small,
    "explosion": explosion,
    "explosion_big": explosion_big,
    "player_explosion": player_explosion,
    "hurt": hurt,
    "blast": blast,
    "pickup": pickup,
    "repair": repair,
    "switch": switch,
    "menu_move": menu_move,
    "menu_choose": menu_choose,
    "menu_back": menu_back,
    "alarm": alarm,
}
