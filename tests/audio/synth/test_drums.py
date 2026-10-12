import numpy as np
import pytest

from pewpy.audio.synth.drums import DRUM_PANS, drum


@pytest.mark.parametrize("pitch", [36, 38, 39, 42, 46, 49, 41, 45, 50, 80])
def test_every_drum_sounds(pitch: int) -> None:
    hit = drum(pitch)
    assert hit.ndim == 1
    assert len(hit) > 0
    assert 0 < np.max(np.abs(hit)) <= 1.0


def test_an_open_hat_rings_longer_than_a_closed_one_and_a_crash_longest() -> None:
    assert len(drum(42)) < len(drum(46)) < len(drum(49))


def test_drums_are_panned_within_the_stereo_field() -> None:
    assert all(-1.0 <= pan <= 1.0 for pan in DRUM_PANS.values())
