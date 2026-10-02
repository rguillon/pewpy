import random

import numpy as np
import pytest

from pewpy.scenery import params
from pewpy.scenery.background import Area
from pewpy.scenery.ground import kinds, settlement
from pewpy.scenery.ground.kinds import SETTLEMENTS
from pewpy.scenery.ground.landscapes import Flora, Landscape
from pewpy.scenery.ground.relief import Shape
from pewpy.scenery.ground.settlement import Settlement
from pewpy.scenery.ground.terrain import Terrain

ROWS, COLUMNS, STEP = 210, 120, 0.02
GROUNDS = [name for name in params.backgrounds() if params.resolve(name).ground is not None]
WITH_FLUID = [name for name in GROUNDS if params.resolve(name).fluid is not None]


def seeded(seed: int) -> random.Random:
    return random.Random(seed)


def shape_of(name: str) -> Shape:
    ground = params.resolve(name).ground
    assert ground is not None
    landscape = kinds.LANDSCAPES[ground.landscape]
    return landscape.shape(np.random.default_rng(3), ROWS, COLUMNS, ground.max_height, STEP, ground.shape)


def depth(name: str) -> float:
    ground = params.resolve(name).ground
    assert ground is not None
    return ground.depth


WIDTH, LOOP = 2.4, 4.2


def knobs(name: str) -> params.Knobs:
    """Return the settlement's numbers in the preset of the same name."""
    found = params.resolve(name).settlement
    assert found is not None
    return found.layout


@pytest.mark.parametrize("name", GROUNDS)
def test_every_landscape_loops_and_stays_behind_the_ships(name: str) -> None:
    heights = shape_of(name).heights
    assert heights.shape == (ROWS, COLUMNS)
    assert np.isfinite(heights).all()
    # The row after the last one is the first one again: no cliff where the loop starts over.
    assert float(np.max(np.abs(heights[-1] - heights[0]))) <= float(np.max(np.abs(np.diff(heights, axis=0)))) + 1e-9
    assert float(np.max(heights)) <= depth(name) - 0.1


@pytest.mark.parametrize("name", WITH_FLUID)
def test_grounds_with_a_fluid_have_some_of_it_and_some_land(name: str) -> None:
    heights = shape_of(name).heights
    under = float(np.mean(heights < 0))
    assert 0.02 < under < 0.9


@pytest.mark.parametrize("name", [name for name in GROUNDS if name not in WITH_FLUID])
def test_grounds_without_a_fluid_have_nothing_below_their_base(name: str) -> None:
    assert float(np.min(shape_of(name).heights)) >= 0.0


def test_marks_stay_between_0_and_1() -> None:
    for name in GROUNDS:
        marks = shape_of(name).marks
        if marks is not None:
            assert float(np.min(marks)) >= 0.0
            assert float(np.max(marks)) <= 1.0


@pytest.mark.parametrize(("name", "kind"), [("desert", "palm"), ("swamp", "dead_tree")])
def test_flora_stands_on_land(name: str, kind: str) -> None:
    terrain = Terrain(Area(-1.0, 1.0, -1.3, 1.3), 1.0, params.resolve(name), seed=4)
    relief = terrain.relief
    props = [prop for prop in terrain.props if prop.kind == kind]
    assert props
    for prop in props:
        row = round(prop.y / relief.step_y) % relief.rows
        column = min(round(prop.x / relief.step_x), relief.columns - 1)
        assert relief.depth[row, column] < 0.0  # on land, not in the water


@pytest.mark.parametrize("generator", [*kinds.LANDSCAPES.values(), *kinds.FLORAS.values(), *kinds.SETTLEMENTS.values()])
def test_every_landscape_flora_and_settlement_names_its_numbers(generator: Landscape | Flora | Settlement) -> None:
    assert generator.knobs
    assert all(isinstance(name, str) for name in generator.knobs)


@pytest.mark.parametrize("name", SETTLEMENTS)
def test_every_prop_stands_inside_the_ground_without_crossing_the_loop_end(name: str) -> None:
    layout = SETTLEMENTS[name].layout(seeded(1), WIDTH, LOOP, knobs(name))
    assert layout.surface.shape == (round(LOOP / settlement.SURFACE_STEP), round(WIDTH / settlement.SURFACE_STEP))
    assert layout.props
    for prop in layout.props:
        assert prop.y - prop.length / 2 >= 0.0
        assert prop.y + prop.length / 2 <= LOOP + 1e-9
        assert prop.x - prop.width / 2 >= -0.03
        assert prop.x + prop.width / 2 <= WIDTH + 0.03
        assert prop.height > 0
        # Nothing reaches the ships: every biome keeps its tallest thing 0.1 behind the play plane.
        assert prop.height <= depth(name) - 0.1
