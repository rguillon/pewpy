import random

import numpy as np
import pytest

from pewpy.scenery import params
from pewpy.scenery.grounds import outposts
from pewpy.scenery.params import Outposts, SceneryError
from pewpy.scenery.relief import Shape
from pewpy.scenery.settlement import Layout, Prop, Surface
from pewpy.scenery.terrain import Area, Terrain

STEP = 0.02
KNOBS = Outposts(kinds=tuple(outposts.COMPOUNDS), spacing=1.0, size=(0.26, 0.4))
WORLDS = ("mountains", "forest", "swamp", "farmland", "ocean", "canyon", "refinery", "city")


def bumpy(rows: int = 200, columns: int = 150, seed: int = 0) -> Shape:
    rng = np.random.default_rng(seed)
    return Shape(rng.uniform(-0.05, 0.1, (rows, columns)), rng.uniform(0.0, 1.0, (rows, columns)))


def test_compounds_level_the_ground_under_them_and_stay_inside_the_loop():
    shape = bumpy()
    levelled, props, sites = outposts.build(random.Random(1), shape, STEP, KNOBS, fluid=True)  # noqa: S311
    rows, columns = shape.heights.shape
    assert sites
    for top, bottom, left, right in sites:
        assert 0 <= top < bottom <= rows * STEP
        assert 0 <= left < right <= (columns - 1) * STEP
        inside = levelled.heights[
            int(np.ceil(top / STEP)) : int(bottom / STEP), int(np.ceil(left / STEP)) : int(right / STEP)
        ]
        assert np.ptp(inside) < 1e-9  # flat
        assert float(np.min(inside)) >= outposts.DRY - 1e-9  # dry, over a fluid
        assert levelled.marks is not None
    assert len([prop for prop in props if prop.kind == "apron"]) <= len(sites)


def test_compounds_keep_apart():
    _, _, sites = outposts.build(random.Random(2), bumpy(), STEP, KNOBS, fluid=False)  # noqa: S311
    for index, site in enumerate(sites):
        for other in sites[index + 1 :]:
            assert not outposts._near(site, other)


@pytest.mark.parametrize("kind", outposts.COMPOUNDS)
def test_every_compound_has_its_buildings_on_its_lot(kind):
    knobs = Outposts(kinds=(kind,), spacing=1.0, size=(0.3, 0.3))
    _, props, sites = outposts.build(random.Random(3), bumpy(), STEP, knobs, fluid=False)  # noqa: S311
    main = outposts.COMPOUNDS[kind][0][0]
    assert any(prop.kind == main for prop in props)
    for prop in props:
        assert any(outposts._overlaps(prop, site, margin=0.0) for site in sites)


def test_a_settlement_makes_room_for_the_compounds():
    house = Prop("house", 0.5, 0.5, 0.04, 0.04, 0.03, 1)
    far_house = Prop("house", 2.0, 2.0, 0.04, 0.04, 0.03, 2)
    layout = Layout(
        np.zeros((400, 400), dtype=np.uint8), np.zeros((400, 400), dtype=np.uint8), [house, far_house], 2.0, 2.0
    )
    cleared = outposts.clear(layout, [(0.4, 0.7, 0.4, 0.7)], Surface.YARD)
    assert cleared.props == [far_house]
    assert cleared.surface[110, 110] == Surface.YARD
    assert cleared.surface[300, 300] == 0


@pytest.mark.parametrize("name", WORLDS)
def test_every_world_has_outposts(name):
    terrain = Terrain(Area(-1.6, 1.6, -1.0, 1.65), 0.3, params.resolve(name), seed=4)
    kinds = [prop.kind for prop in terrain.props]
    assert {"hangar", "warehouse", "radar", "dome", "containers"} & set(kinds)


def test_some_compounds_are_paved_and_some_stand_on_the_ground():
    shape = bumpy(400, 400)
    knobs = Outposts(kinds=tuple(outposts.COMPOUNDS), spacing=0.8, size=(0.3, 0.3))
    _, props, sites = outposts.build(random.Random(5), shape, STEP, knobs, fluid=False)  # noqa: S311
    aprons = sum(prop.kind == "apron" for prop in props)
    assert 0 < aprons < len(sites)


def test_unknown_compounds_are_reported():
    with pytest.raises(SceneryError, match=r"outposts\.kinds"):
        params.resolve("forest", {"outposts": {"kinds": ["castle"]}})


def test_a_ground_too_small_for_a_compound_has_none():
    shape = bumpy(rows=10, columns=10)  # 0.2 x 0.18: smaller than any compound
    flattened, props, sites = outposts.build(random.Random(0), shape, STEP, KNOBS, fluid=False)  # noqa: S311
    assert (sites, props) == ([], [])
    assert np.array_equal(flattened.heights, shape.heights)
