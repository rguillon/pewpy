"""A small synthesizer: plays MIDI songs (see midi.py) as audio, the 80s-synth way. Numpy only, no Panda3D.

Every channel's General MIDI program picks one of a few instruments (a bass, a pad, a lead, an arpeggio pluck,
keys); channel 9 holds the drums. Notes are drawn with band-limited oscillators, filtered with an envelope, and
mixed through the effects of the style: a stereo delay, a long reverb, a short gated reverb on the snare, and the
pads and bass ducking under the kick drum.
"""

from collections.abc import Callable
from dataclasses import dataclass
from functools import cache, lru_cache

import numpy as np

from pewpy.audio.midi import DRUMS, Song

RATE = 32_000  # samples per second
TAIL = 3.0  # seconds rendered past the end, for the release and reverb (wrapped to the start when looping)

FloatArray = np.ndarray


def frequency(pitch: float) -> float:
    return 440.0 * 2.0 ** ((pitch - 69) / 12)


def _poly_blep(phase: FloatArray, step: FloatArray) -> FloatArray:
    """The correction that removes most of the aliasing from a saw's jump (where phase wraps)."""
    out = np.zeros_like(phase)
    step = np.maximum(step, 1e-9)
    low = phase < step
    t = phase[low] / step[low]
    out[low] = t + t - t * t - 1.0
    high = phase > 1.0 - step
    t = (phase[high] - 1.0) / step[high]
    out[high] = t * t + t + t + 1.0
    return out


def oscillator(wave: str, hertz: FloatArray, phase: float = 0.0) -> FloatArray:
    """`wave` ("saw", "square", "triangle", "sine") following the frequency `hertz` (one per sample)."""
    step = hertz / RATE
    cycle = (np.cumsum(step) - step[0] + phase) % 1.0
    if wave == "sine":
        return np.sin(2 * np.pi * cycle)
    if wave == "triangle":
        return 1.0 - 4.0 * np.abs(cycle - 0.5)
    saw = 2.0 * cycle - 1.0 - _poly_blep(cycle, step)
    if wave == "saw":
        return saw
    shifted = (cycle + 0.5) % 1.0
    return saw - (2.0 * shifted - 1.0 - _poly_blep(shifted, step))  # square: two saws half a cycle apart


def noise(count: int, seed: int = 0) -> FloatArray:
    return np.random.default_rng(seed).uniform(-1.0, 1.0, count)


def _filters(signal: FloatArray, *responses: Callable[[FloatArray], FloatArray]) -> list[FloatArray]:
    """`signal` (mono, or stereo in columns) through each filter, given by its gain at every frequency: in the
    frequency domain, transformed once for them all (padded to a power of two: much faster, and nothing wraps
    around from the end to the start).
    """
    size = 1 << (len(signal) - 1).bit_length()
    hertz = np.fft.rfftfreq(size, 1.0 / RATE)
    spectrum = np.fft.rfft(signal, size, axis=0)
    gains = [response(hertz) for response in responses]
    shaped = [spectrum * (gain[:, None] if signal.ndim == 2 else gain) for gain in gains]
    return [np.fft.irfft(each, size, axis=0)[: len(signal)] for each in shaped]


def _filter(signal: FloatArray, response: Callable[[FloatArray], FloatArray]) -> FloatArray:
    return _filters(signal, response)[0]


def _lowpass_gain(cutoff: float, order: int = 2) -> Callable[[FloatArray], FloatArray]:
    return lambda hertz: 1.0 / np.sqrt(1.0 + (hertz / max(cutoff, 1.0)) ** (2 * order))


def lowpass(signal: FloatArray, cutoff: float, order: int = 2) -> FloatArray:
    """A Butterworth-shaped low-pass (12 dB per octave at order 2)."""
    if cutoff >= RATE / 2:
        return signal
    return _filter(signal, _lowpass_gain(cutoff, order))


def highpass(signal: FloatArray, cutoff: float, order: int = 2) -> FloatArray:
    return _filter(signal, lambda hertz: 1.0 / np.sqrt(1.0 + (cutoff / np.maximum(hertz, 1e-3)) ** (2 * order)))


def envelope(count: int, held: int, attack: float, decay: float, sustain: float, release: float) -> FloatArray:
    """An ADSR envelope over `count` samples, the key held for the first `held` (times in seconds)."""
    t = np.arange(count) / RATE
    rise = np.minimum(t / max(attack, 1e-4), 1.0)
    after = np.maximum(t - attack, 0.0)
    level = rise * (sustain + (1.0 - sustain) * np.exp(-after / max(decay, 1e-4)))
    if held < count:
        at_release = level[held - 1] if held > 0 else 0.0
        level[held:] = at_release * np.exp(-(t[held:] - t[held]) / max(release, 1e-4))
    return level


@dataclass(frozen=True)
class Instrument:
    wave: str = "saw"
    voices: int = 1  # detuned copies (a "supersaw" with more)
    detune: float = 0.0  # cents between the outermost voices
    sub: float = 0.0  # a square an octave below, this loud
    attack: float = 0.005
    decay: float = 0.3
    sustain: float = 0.7
    release: float = 0.15
    cutoff: float = 3000.0  # filter, Hz, once its envelope has decayed
    brightness: float = 2.0  # the filter opens this many times wider at the start of each note
    filter_decay: float = 0.2  # seconds
    vibrato: float = 0.0  # cents
    gain: float = 0.3
    pan: float = 0.0  # -1 left, 1 right
    spread: float = 0.0  # voices spread across the stereo field
    delay: float = 0.0  # send to the stereo delay
    reverb: float = 0.2  # send to the reverb
    ducks: bool = False  # ducks under the kick drum


BASS = Instrument(wave="saw", sub=0.6, decay=0.25, sustain=0.6, release=0.05, cutoff=420, brightness=3.0,
                  filter_decay=0.12, gain=0.45, reverb=0.03, ducks=True)  # fmt: skip
PAD = Instrument(wave="saw", voices=5, detune=24, attack=0.5, decay=1.0, sustain=0.85, release=1.2, cutoff=1500,
                 brightness=1.4, filter_decay=1.5, gain=0.13, spread=0.8, reverb=0.5, ducks=True)  # fmt: skip
LEAD = Instrument(wave="saw", voices=3, detune=14, attack=0.01, decay=0.4, sustain=0.75, release=0.25, cutoff=3800,
                  brightness=1.5, vibrato=18, gain=0.2, spread=0.3, delay=0.35, reverb=0.35)  # fmt: skip
PLUCK = Instrument(wave="square", decay=0.14, sustain=0.0, release=0.08, cutoff=1200, brightness=4.0,
                   filter_decay=0.08, gain=0.17, pan=0.25, delay=0.45, reverb=0.25)  # fmt: skip
KEYS = Instrument(wave="triangle", voices=2, detune=8, decay=0.8, sustain=0.3, release=0.4, cutoff=2500, gain=0.2,
                  spread=0.5, reverb=0.4)  # fmt: skip
BRASS = Instrument(wave="saw", voices=3, detune=10, attack=0.04, decay=0.5, sustain=0.8, release=0.3, cutoff=2200,
                   brightness=1.8, filter_decay=0.3, gain=0.16, spread=0.6, reverb=0.35)  # fmt: skip


def instrument(program: int) -> Instrument:
    """The instrument for a General MIDI program: its family decides."""
    if 32 <= program <= 39:  # basses
        return BASS
    if 88 <= program <= 95 or 48 <= program <= 55:  # pads, strings and choirs
        return PAD
    if program == 80 or 96 <= program <= 103:  # square lead, effects: plucks for arpeggios
        return PLUCK
    if 81 <= program <= 87:  # leads
        return LEAD
    if 56 <= program <= 63:  # brass
        return BRASS
    return KEYS


def _voice(spec: Instrument, pitch: int, count: int, held: int) -> FloatArray:
    """One note, stereo (count x 2), before velocity and volume."""
    t = np.arange(count) / RATE
    base = frequency(pitch)
    wobble = 2.0 ** (spec.vibrato / 1200 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(t / 0.3, 1.0))
    out = np.zeros((count, 2))
    for index in range(spec.voices):
        offset = (index / (spec.voices - 1) - 0.5) if spec.voices > 1 else 0.0
        hertz = np.full(count, base * 2.0 ** (offset * spec.detune / 1200)) * wobble
        tone = oscillator(spec.wave, hertz, phase=(index * 0.37) % 1.0)
        pan = np.clip(spec.pan + offset * 2 * spec.spread, -1.0, 1.0)
        out[:, 0] += tone * np.sqrt((1 - pan) / 2)
        out[:, 1] += tone * np.sqrt((1 + pan) / 2)
    out /= np.sqrt(spec.voices)
    if spec.sub:
        sub = oscillator("square", np.full(count, base / 2)) * spec.sub
        out += sub[:, None] * np.sqrt(0.5)
    # The filter's envelope: from bright to its cutoff, as a mix of the two (cheaper than a moving filter).
    bright, dark = _filters(out, _lowpass_gain(spec.cutoff * spec.brightness), _lowpass_gain(spec.cutoff))
    opening = np.exp(-t / spec.filter_decay)[:, None]
    shaped = dark + (bright - dark) * opening
    level = envelope(count, held, spec.attack, spec.decay, spec.sustain, spec.release)
    return shaped * level[:, None] * spec.gain


@lru_cache(maxsize=512)
def _note(program: int, pitch: int, count: int, held: int) -> FloatArray:
    return _voice(instrument(program), pitch, count, held)


def _sweep(count: int, start: float, end: float, speed: float) -> FloatArray:
    t = np.arange(count) / RATE
    return end + (start - end) * np.exp(-t * speed)


@cache
def drum(pitch: int) -> FloatArray:
    """A General MIDI drum (mono): kicks, snares and claps, hats, crashes, toms; anything else is a click."""
    if pitch in (35, 36):  # kick
        count = int(0.45 * RATE)
        body = oscillator("sine", _sweep(count, 160, 45, 30)) * np.exp(-np.arange(count) / (0.28 * RATE))
        click = lowpass(noise(count, 1), 3000) * np.exp(-np.arange(count) / (0.004 * RATE))
        return np.tanh(1.6 * body + 0.4 * click) * 0.9
    if pitch in (38, 39, 40):  # snare, clap
        count = int(0.35 * RATE)
        decay = np.exp(-np.arange(count) / (0.09 * RATE))
        rattle = highpass(lowpass(noise(count, 2), 7000), 900) * decay
        tone = oscillator("triangle", _sweep(count, 260, 180, 20)) * np.exp(-np.arange(count) / (0.05 * RATE))
        return (0.75 * rattle + 0.45 * tone) * (0.8 if pitch == 39 else 1.0)
    if pitch in (42, 44, 46):  # hats: closed, pedal, open
        length = 0.4 if pitch == 46 else 0.06
        count = int(length * RATE * 1.5)
        return highpass(noise(count, 3), 7000) * np.exp(-np.arange(count) / (length / 3 * RATE)) * 0.35
    if pitch in (49, 51, 52, 55, 57, 59):  # cymbals
        count = int(2.5 * RATE)
        return highpass(noise(count, 4), 4000) * np.exp(-np.arange(count) / (0.7 * RATE)) * 0.25
    if 41 <= pitch <= 50:  # toms, low to high
        count = int(0.6 * RATE)
        top = 90 + (pitch - 41) * 18
        body = oscillator("sine", _sweep(count, top * 1.6, top, 12)) * np.exp(-np.arange(count) / (0.22 * RATE))
        return body * 0.7
    count = int(0.03 * RATE)
    return highpass(noise(count, 5), 2000) * np.exp(-np.arange(count) / (0.005 * RATE)) * 0.3


DRUM_PANS = {42: 0.3, 44: 0.3, 46: 0.3, 41: -0.4, 43: -0.25, 45: -0.1, 47: 0.1, 48: 0.25, 50: 0.4, 49: -0.3, 57: 0.3}


def _impulse(seconds: float, decay: float, seed: int, gated: bool = False) -> FloatArray:
    """A stereo reverb's impulse response: decaying noise, darker as it fades (or flat then cut, gated)."""
    count = int(seconds * RATE)
    t = np.arange(count) / RATE
    shape = np.where(t < seconds * 0.85, 1.0, np.exp(-(t - seconds * 0.85) / 0.01)) if gated else np.exp(-t / decay)
    sides = [lowpass(noise(count, seed + side), 5000) * shape for side in (0, 1)]
    response = np.stack(sides, axis=1)
    response[: int(0.012 * RATE)] = 0.0  # a short pre-delay
    return response / np.sqrt(np.sum(response**2) / 2)


def _convolve(signal: FloatArray, response: FloatArray) -> FloatArray:
    size = len(signal) + len(response)
    fft_size = 1 << (size - 1).bit_length()
    out = np.empty_like(signal)
    for side in (0, 1):
        spectrum = np.fft.rfft(signal[:, side], fft_size) * np.fft.rfft(response[:, side], fft_size)
        out[:, side] = np.fft.irfft(spectrum, fft_size)[: len(signal)]
    return out


def _echo(signal: FloatArray, seconds: float, feedback: float = 0.45, repeats: int = 5) -> FloatArray:
    """A ping-pong delay: each repeat on the other side, quieter."""
    out = np.zeros_like(signal)
    step = int(seconds * RATE)
    mono = lowpass(signal.mean(axis=1), 3500)
    for repeat in range(1, repeats + 1):
        if repeat * step >= len(signal):
            break
        out[repeat * step :, repeat % 2] += mono[: len(signal) - repeat * step] * feedback**repeat
    return out


def _ducking(song: Song, count: int) -> FloatArray:
    """The volume of whatever ducks under the kick: down at each kick, back up quickly."""
    gain = np.ones(count)
    release = int(0.25 * RATE)
    curve = 1.0 - 0.6 * np.exp(-np.arange(release) / (0.07 * RATE))
    for note in song.notes:
        if note.channel == DRUMS and note.pitch in (35, 36):
            start = int(song.seconds(note.start) * RATE)
            end = min(count, start + release)
            if start < count:
                gain[start:end] = np.minimum(gain[start:end], curve[: end - start])
    return gain


def _place(target: FloatArray, sound: FloatArray, start: int) -> None:
    end = min(len(target), start + len(sound))
    if start < end:
        target[start:end] += sound[: end - start]


def render(song: Song, loop: bool = True) -> FloatArray:
    """`song` as stereo samples (count x 2, -1 to 1) at RATE. Looping, what rings past the end is wrapped onto the
    start, so it loops without a seam.
    """
    length = int(song.duration * RATE)
    count = length + int(TAIL * RATE)
    dry, ducked, delay_send, reverb_send, gated_send = (np.zeros((count, 2)) for _ in range(5))
    for note in song.notes:
        start = int(song.seconds(note.start) * RATE)
        loudness = (note.velocity / 127) * (song.volumes.get(note.channel, 100) / 100)
        if note.channel == DRUMS:
            hit = drum(note.pitch)
            pan = DRUM_PANS.get(note.pitch, 0.0)
            sound = np.stack([hit * np.sqrt((1 - pan) / 2), hit * np.sqrt((1 + pan) / 2)], axis=1) * loudness
            _place(dry, sound, start)
            if note.pitch in (38, 39, 40):
                _place(gated_send, sound, start)
            elif 41 <= note.pitch <= 50 and note.pitch not in (42, 44, 46):
                _place(reverb_send, sound * 0.4, start)
            continue
        program = song.programs.get(note.channel, 0)
        spec = instrument(program)
        held = max(1, int(song.seconds(note.start + note.length) * RATE) - start)
        sound = _note(program, note.pitch, held + int(spec.release * 5 * RATE), held) * loudness
        _place(ducked if spec.ducks else dry, sound, start)
        _place(delay_send, sound * spec.delay, start)
        _place(reverb_send, sound * spec.reverb, start)
    mix = dry + ducked * _ducking(song, count)[:, None]
    mix += _echo(delay_send, 0.75 * 60.0 / song.tempo)  # a dotted eighth
    mix += _convolve(reverb_send + 0.3 * delay_send, _impulse(2.4, 0.7, 10)) * 0.5
    mix += _convolve(gated_send, _impulse(0.32, 1.0, 20, gated=True)) * 0.45
    if loop:
        mix[: count - length] += mix[length:]
        mix = mix[:length]
    peak = np.max(np.abs(mix)) or 1.0
    return np.tanh(mix / peak * 1.3) / np.tanh(1.3) * 0.9


def wav_bytes(samples: FloatArray, rate: int = RATE) -> bytes:
    """Samples (-1 to 1; one column for mono, two for stereo) as a 16-bit WAV file."""
    import io
    import wave

    channels = 1 if samples.ndim == 1 else samples.shape[1]
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as out:
        out.setnchannels(channels)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(pcm.tobytes())
    return buffer.getvalue()
