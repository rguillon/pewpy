import random

import numpy as np
import pytest

from pewpy.scenery import landscapes
from pewpy.scenery.background import Area
from pewpy.scenery.terrain import BIOMES, Terrain

ROWS, COLUMNS, STEP = 210, 120, 0.02


def seeded(seed: int) -> random.Random:
    return random.Random(seed)  # noqa: S311 - layouts, not cryptography


def shape_of(name: str) -> landscapes.Shape:
    biome = BIOMES[name]
    assert biome.relief is not None
    return biome.relief(np.random.default_rng(3), ROWS, COLUMNS, biome.max_height, STEP)


@pytest.mark.parametrize("name", BIOMES)
def test_every_landscape_loops_and_stays_behind_the_ships(name):
    heights = shape_of(name).heights
    assert heights.shape == (ROWS, COLUMNS)
    assert np.isfinite(heights).all()
    # The row after the last one is the first one again: no cliff where the loop starts over.
    assert float(np.max(np.abs(heights[-1] - heights[0]))) <= float(np.max(np.abs(np.diff(heights, axis=0)))) + 1e-9
    assert float(np.max(heights)) <= BIOMES[name].depth - 0.1


@pytest.mark.parametrize("name", [name for name, biome in BIOMES.items() if biome.fluid])
def test_grounds_with_a_fluid_have_some_of_it_and_some_land(name):
    heights = shape_of(name).heights
    under = float(np.mean(heights < 0))
    assert 0.02 < under < 0.9


@pytest.mark.parametrize("name", [name for name, biome in BIOMES.items() if not biome.fluid])
def test_grounds_without_a_fluid_have_nothing_below_their_base(name):
    assert float(np.min(shape_of(name).heights)) >= 0.0


def test_marks_stay_between_0_and_1():
    for name in BIOMES:
        marks = shape_of(name).marks
        if marks is not None:
            assert float(np.min(marks)) >= 0.0 and float(np.max(marks)) <= 1.0


@pytest.mark.parametrize(("name", "kind"), [("desert", "palm"), ("swamp", "dead_tree")])
def test_flora_stands_on_land(name, kind):
    terrain = Terrain(Area(-1.0, 1.0, -1.3, 1.3), 1.0, seed=4, biome=name)
    relief = terrain.relief
    assert relief is not None
    props = [prop for prop in terrain.props if prop.kind == kind]
    assert props
    for prop in props:
        row = round(prop.y / relief.step_y) % relief.rows
        column = min(round(prop.x / relief.step_x), relief.columns - 1)
        assert relief.depth[row, column] < 0.0  # on land, not in the water


def test_scattering_is_random_but_reproducible():
    where = np.ones((10, 10), dtype=bool)
    first = landscapes._scatter(seeded(1), where, 0.5, 0.02, 0.02)
    assert first == landscapes._scatter(seeded(1), where, 0.5, 0.02, 0.02)
    assert 20 < len(first) < 80
