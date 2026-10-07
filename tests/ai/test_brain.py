"""The AI's neural network."""

import numpy as np
import pytest

from pewpy.ai import sensors
from pewpy.ai.brain import FIRE_BIAS, OUTPUTS, RADAR_GAIN, Brain, parameter_count


def test_a_brain_needs_as_many_weights_as_its_shape() -> None:
    with pytest.raises(ValueError, match="weights"):
        Brain(np.zeros(3))
    assert Brain(np.zeros(parameter_count(hidden=(4, 3))), (4, 3)).think(np.zeros(sensors.SIZE)).shape == (OUTPUTS,)


def test_a_new_brain_flies_the_radars_move_to_aim_and_fires_at_what_it_can_hurt() -> None:
    brain = Brain.random(np.random.default_rng(1))
    view = np.zeros(sensors.SIZE)
    view[sensors.AIM] = 1.0  # aim right
    out = brain.think(view)
    assert out[0] == pytest.approx(RADAR_GAIN, abs=0.5)
    assert out[2] == pytest.approx(FIRE_BIAS, abs=0.5)  # nothing to shoot: the button released
    view[sensors.SHOOTABLE] = 1.0
    assert brain.think(view)[2] > 0
