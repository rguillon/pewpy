import random

import numpy as np

from pewpy.scenery.ground.kinds.savanna import Acacias, Savanna
from pewpy.scenery.ground.relief import Shape

KNOBS = {"size": 0.9, "bend_spacing": 1.6, "outcrop_share": 0.03}
STEP = 0.02


def savanna() -> Shape:
    return Savanna().shape(np.random.default_rng(0), 200, 80, 0.12, STEP, KNOBS)


def test_a_savanna_is_grass_with_a_sandy_riverbed_and_rock_outcrops() -> None:
    shape = savanna()
    assert shape.marks is not None
    assert set(np.unique(shape.marks)) == {0.0, 0.5, 1.0}
    rock = shape.marks == 1.0
    assert 0.0 < float(np.mean(rock)) < 0.1
    assert float(np.mean(shape.heights[rock])) > float(np.mean(shape.heights[shape.marks == 0.0]))


def test_acacias_stand_on_the_grass() -> None:
    shape = savanna()
    assert shape.marks is not None
    trees = Acacias().props(random.Random(0), shape, STEP, STEP, {"chance": 0.05, "size": 0.05, "height": [0.02, 0.03]})
    assert trees
    for tree in trees:
        assert (tree.kind, tree.width, tree.length) == ("tree", 0.05, 0.05)
        assert 0.02 <= tree.height <= 0.03
        assert shape.marks[round(tree.y / STEP), round(tree.x / STEP)] == 0.0  # grass, not sand or rock
