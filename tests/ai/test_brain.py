import numpy as np
import pytest

from pewpy.ai import sensors
from pewpy.ai.brain import FIRE_BIAS, OUTPUTS, RADAR_GAIN, WEAPON_BIAS, Brain, parameter_count, shapes


def test_a_brain_maps_a_view_to_its_outputs():
    brain = Brain.random(np.random.default_rng(0))
    out = brain.think(np.zeros(sensors.SIZE))
    assert out.shape == (OUTPUTS,)
    assert out[2] == pytest.approx(FIRE_BIAS)  # no input, no other bias: the fire button held...
    assert out[3] == pytest.approx(WEAPON_BIAS)  # ...the bullets wanted
    direct = brain.layers[-1]
    assert direct[sensors.AIM, 0] == direct[sensors.AIM + 1, 1] == RADAR_GAIN
    assert np.count_nonzero(direct) == 2  # the direct path starts closed but from the radar's move to aim


def test_a_new_brain_flies_the_radars_move_to_aim():
    brain = Brain.random(np.random.default_rng(0))
    view = np.zeros(sensors.SIZE)
    view[sensors.AIM : sensors.AIM + 2] = (1.0, 0.0)  # the move to aim: right
    out = brain.think(view)
    assert out[0] > 1.0 and abs(out[1]) < 1.0


def test_the_weights_are_one_flat_vector_shared_with_the_layers():
    assert parameter_count() == sum(rows * columns for rows, columns in shapes())
    brain = Brain(np.zeros(parameter_count()))
    brain.layers[-2][-1, -1] = 2.0  # the last output's bias, through the layer: the same numbers
    assert brain.weights.sum() == 2.0
    assert brain.think(np.zeros(sensors.SIZE))[-1] == 2.0


def test_the_direct_path_takes_the_inputs_straight_to_the_outputs():
    brain = Brain(np.zeros(parameter_count()))
    brain.layers[-1][5, 0] = 0.5  # the sixth input to the first output (the stick's x)
    view = np.zeros(sensors.SIZE)
    view[5] = 1.0
    assert brain.think(view)[0] == 0.5


def test_weights_of_the_wrong_size_are_refused():
    with pytest.raises(ValueError, match="weights"):
        Brain(np.zeros(10))
