import numpy as np
import pytest

from pewpy.scenery.ground.kinds import LANDSCAPES


def rng() -> np.random.Generator:
    return np.random.default_rng(0)


def test_mountains_stay_between_the_base_layer_and_their_highest_point() -> None:
    knobs = {"range_size": 1.1, "crest_size": 0.6}
    heights = LANDSCAPES["mountains"].shape(rng(), 200, 80, 0.5, 0.02, knobs).heights
    assert float(np.min(heights)) == 0.0  # flat valley floors
    assert float(np.max(heights)) == pytest.approx(0.5)
    assert float(np.max(np.abs(heights[-1] - heights[0]))) < 0.05  # no cliff where the loop starts again
