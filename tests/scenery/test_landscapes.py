import random

import numpy as np
import pytest

from pewpy.scenery import grounds, landscapes, params
from pewpy.scenery.background import Area
from pewpy.scenery.relief import Shape
from pewpy.scenery.terrain import Terrain

ROWS, COLUMNS, STEP = 210, 120, 0.02
GROUNDS = [name for name in params.backgrounds() if params.resolve(name).ground is not None]
WITH_FLUID = [name for name in GROUNDS if params.resolve(name).fluid is not None]


def seeded(seed: int) -> random.Random:
    return random.Random(seed)  # noqa: S311 - layouts, not cryptography


def shape_of(name: str) -> Shape:
    ground = params.resolve(name).ground
    assert ground is not None
    landscape = grounds.LANDSCAPES[ground.landscape]
    return landscape.shape(np.random.default_rng(3), ROWS, COLUMNS, ground.max_height, STEP, ground.shape)


def depth(name: str) -> float:
    ground = params.resolve(name).ground
    assert ground is not None
    return ground.depth


@pytest.mark.parametrize("name", GROUNDS)
def test_every_landscape_loops_and_stays_behind_the_ships(name):
    heights = shape_of(name).heights
    assert heights.shape == (ROWS, COLUMNS)
    assert np.isfinite(heights).all()
    # The row after the last one is the first one again: no cliff where the loop starts over.
    assert float(np.max(np.abs(heights[-1] - heights[0]))) <= float(np.max(np.abs(np.diff(heights, axis=0)))) + 1e-9
    assert float(np.max(heights)) <= depth(name) - 0.1


@pytest.mark.parametrize("name", WITH_FLUID)
def test_grounds_with_a_fluid_have_some_of_it_and_some_land(name):
    heights = shape_of(name).heights
    under = float(np.mean(heights < 0))
    assert 0.02 < under < 0.9


@pytest.mark.parametrize("name", [name for name in GROUNDS if name not in WITH_FLUID])
def test_grounds_without_a_fluid_have_nothing_below_their_base(name):
    assert float(np.min(shape_of(name).heights)) >= 0.0


def test_marks_stay_between_0_and_1():
    for name in GROUNDS:
        marks = shape_of(name).marks
        if marks is not None:
            assert float(np.min(marks)) >= 0.0 and float(np.max(marks)) <= 1.0


@pytest.mark.parametrize(("name", "kind"), [("desert", "palm"), ("swamp", "dead_tree")])
def test_flora_stands_on_land(name, kind):
    terrain = Terrain(Area(-1.0, 1.0, -1.3, 1.3), 1.0, params.resolve(name), seed=4)
    relief = terrain.relief
    props = [prop for prop in terrain.props if prop.kind == kind]
    assert props
    for prop in props:
        row = round(prop.y / relief.step_y) % relief.rows
        column = min(round(prop.x / relief.step_x), relief.columns - 1)
        assert relief.depth[row, column] < 0.0  # on land, not in the water


def test_scattering_is_random_but_reproducible():
    where = np.ones((10, 10), dtype=bool)
    first = landscapes.scatter(seeded(1), where, 0.5, 0.02, 0.02)
    assert first == landscapes.scatter(seeded(1), where, 0.5, 0.02, 0.02)
    assert 20 < len(first) < 80


@pytest.mark.parametrize(
    "generator", [*grounds.LANDSCAPES.values(), *grounds.FLORAS.values(), *grounds.SETTLEMENTS.values()]
)
def test_every_landscape_flora_and_settlement_names_its_numbers(generator):
    assert generator.knobs
    assert all(isinstance(name, str) for name in generator.knobs)
