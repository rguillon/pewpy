import numpy as np
import pytest

from pewpy.audio.sfx import EFFECTS, laser
from pewpy.audio.synth import RATE


@pytest.mark.parametrize("name", sorted(EFFECTS))
def test_every_effect_is_short_audible_and_in_range(name):
    sound = EFFECTS[name]()
    assert sound.ndim == 1
    assert 0.03 * RATE <= len(sound) <= 3 * RATE
    assert 0.01 < np.max(np.abs(sound)) <= 1.0


def test_the_laser_loops_without_a_click():
    hum = laser()
    seam = abs(hum[0] - hum[-1])
    assert seam <= np.max(np.abs(np.diff(hum)))  # no bigger a jump from its end to its start than within it
