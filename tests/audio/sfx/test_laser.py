import numpy as np

from pewpy.audio.sfx.laser import laser
from tests.audio.sfx.audible import assert_audible


def test_the_laser_hum_is_audible() -> None:
    assert_audible(laser(), 1.0)


def test_the_laser_loops_without_a_click() -> None:
    hum = laser()
    seam = abs(hum[0] - hum[-1])
    assert seam <= np.max(np.abs(np.diff(hum)))  # no bigger a jump from its end to its start than within it
