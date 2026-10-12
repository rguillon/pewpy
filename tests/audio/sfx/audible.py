"""What every sound effect must be: mono, short, audible and in range."""

import numpy as np

from pewpy.audio.synth import RATE, FloatArray


def assert_audible(sound: FloatArray, seconds: float) -> None:
    """Check `sound` is a mono effect lasting about `seconds`, heard, and never clipping."""
    assert sound.ndim == 1
    assert abs(len(sound) / RATE - seconds) < 0.01
    assert 0.01 < np.max(np.abs(sound)) <= 1.0
