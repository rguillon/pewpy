"""Rendering a whole song, and writing it as a WAV file."""

import numpy as np

from pewpy.audio.midi import DRUMS, Song
from pewpy.audio.synth.drums import DRUM_PANS, drum
from pewpy.audio.synth.effects import convolve, ducking, echo, impulse
from pewpy.audio.synth.instruments import instrument
from pewpy.audio.synth.signal import RATE, TAIL, FloatArray
from pewpy.audio.synth.voices import play_note


def place(target: FloatArray, sound: FloatArray, start: int) -> None:
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
            place(dry, sound, start)
            if note.pitch in (38, 39, 40):
                place(gated_send, sound, start)
            elif 41 <= note.pitch <= 50 and note.pitch not in (42, 44, 46):
                place(reverb_send, sound * 0.4, start)
            continue
        program = song.programs.get(note.channel, 0)
        spec = instrument(program)
        held = max(1, int(song.seconds(note.start + note.length) * RATE) - start)
        sound = play_note(program, note.pitch, held + int(spec.release * 5 * RATE), held) * loudness
        place(ducked if spec.ducks else dry, sound, start)
        place(delay_send, sound * spec.delay, start)
        place(reverb_send, sound * spec.reverb, start)
    mix = dry + ducked * ducking(song, count)[:, None]
    mix += echo(delay_send, 0.75 * 60.0 / song.tempo)  # a dotted eighth
    mix += convolve(reverb_send + 0.3 * delay_send, impulse(2.4, 0.7, 10)) * 0.5
    mix += convolve(gated_send, impulse(0.32, 1.0, 20, gated=True)) * 0.45
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
