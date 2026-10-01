import random

import numpy as np
import pytest

from pewpy.scenery import params, props, settlement
from pewpy.scenery.background import Area
from pewpy.scenery.settlement import SETTLEMENTS, Prop, Surface
from pewpy.scenery.terrain import Terrain

WIDTH, LOOP = 2.4, 4.2


def knobs(name: str) -> params.Knobs:
    """The settlement's numbers in the preset of the same name."""
    found = params.resolve(name).settlement
    assert found is not None
    return found.layout


def depth(name: str) -> float:
    ground = params.resolve(name).ground
    assert ground is not None
    return ground.depth


@pytest.mark.parametrize("name", SETTLEMENTS)
def test_every_prop_stands_inside_the_ground_without_crossing_the_loop_end(name):
    layout = SETTLEMENTS[name](seeded(1), WIDTH, LOOP, knobs(name))
    assert layout.surface.shape == (round(LOOP / settlement.SURFACE_STEP), round(WIDTH / settlement.SURFACE_STEP))
    assert layout.props
    for prop in layout.props:
        assert prop.y - prop.length / 2 >= 0.0 and prop.y + prop.length / 2 <= LOOP + 1e-9
        assert prop.x - prop.width / 2 >= -0.03 and prop.x + prop.width / 2 <= WIDTH + 0.03
        assert prop.height > 0
        # Nothing reaches the ships: every biome keeps its tallest thing 0.1 behind the play plane.
        assert prop.height <= depth(name) - 0.1


def seeded(seed: int) -> random.Random:
    return random.Random(seed)  # noqa: S311 - layouts, not cryptography


def test_the_city_has_streets_pavements_and_buildings_of_every_size():
    layout = settlement.city(seeded(2), WIDTH, LOOP, knobs("city"))
    surfaces = set(np.unique(layout.surface).tolist())
    assert {Surface.STREET, Surface.PAVEMENT} <= surfaces
    heights = [prop.height for prop in layout.props if prop.kind == "building"]
    assert min(heights) < 0.13 and max(heights) > 0.3


def test_farmland_has_fields_farms_and_trees():
    layout = settlement.farmland(seeded(3), WIDTH, LOOP, knobs("farmland"))
    assert {Surface.WHEAT, Surface.DIRT_ROAD} <= set(np.unique(layout.surface).tolist())
    kinds = {prop.kind for prop in layout.props}
    assert {"house", "barn", "silo", "tree"} <= kinds


def test_refinery_has_tanks_stacks_and_plants():
    kinds = {prop.kind for prop in settlement.refinery(seeded(4), WIDTH, LOOP, knobs("refinery")).props}
    assert {"tank", "stack", "plant"} <= kinds


def test_props_stand_on_the_lowest_ground_under_them_and_rise_above_it_for_shadows():
    heights = np.zeros((40, 40))
    heights[8:17, 8:17] = np.linspace(0.02, 0.06, 9)[None, :]  # a slope rising to the right
    prop = Prop("building", x=0.24, y=0.24, width=0.06, length=0.06, height=0.2, seed=1)
    (placed,) = settlement.place([prop], heights, 0.02, 0.02)
    assert placed.base == pytest.approx(heights[12, 10])  # the low side of its footprint
    solid = settlement.occluders([placed], heights, 0.02, 0.02)
    assert solid[12, 12] == pytest.approx(heights[12, 10] + 0.2)
    assert solid[30, 30] == 0.0


@pytest.mark.parametrize("kind", sorted(props.BUILDERS))
@pytest.mark.parametrize("seed", range(12))  # enough for every kind's variants
def test_every_kind_of_prop_has_a_mesh_around_its_footprint(kind, seed):
    prop = Prop(kind, x=0.5, y=0.3, width=0.12, length=0.1, height=0.3 if kind == "building" else 0.06, seed=seed)
    vertices, triangles = props.strip_arrays([prop], first_y=0.2, colors=params.resolve("city").props)
    assert len(triangles) % 3 == 0 and len(triangles) > 0
    assert int(np.max(triangles)) < len(vertices)
    assert np.isfinite(vertices).all()
    assert np.allclose(np.linalg.norm(vertices[:, 3:6], axis=1), 1.0, atol=1e-3)  # proper normals
    # Model space: x as is, depth -y is the height, z up the screen from the strip's top edge.
    xs, heights, zs = vertices[:, 0], -vertices[:, 1], vertices[:, 2]
    reach = max(prop.width, prop.length) / 2 * 1.1 + 0.02  # palms lean, fronds droop past the footprint
    assert float(np.min(xs)) >= 0.5 - reach and float(np.max(xs)) <= 0.5 + reach
    assert float(np.min(heights)) >= -props.SUNK - 1e-6
    # Masts, chimneys, domes and flames (as big as the stack) stick out on top.
    assert float(np.max(heights)) <= prop.height * 1.6 + 0.09 + max(prop.width, prop.length)
    assert float(np.max(-zs)) <= 0.3 - 0.2 + reach


def test_props_of_a_kind_differ_by_their_seed():
    colors = params.resolve("city").props
    for kind in props.BUILDERS:
        shapes = set()
        for seed in range(12):
            vertices, _ = props.strip_arrays([Prop(kind, 0.5, 0.3, 0.12, 0.1, 0.3, seed)], 0.2, colors)
            shapes.add((len(vertices), round(float(vertices[:, :3].sum()), 4)))
        assert len(shapes) > 1, kind


def test_the_refinery_has_cooling_towers_and_the_farms_greenhouses():
    refinery = {
        prop.kind
        for seed in range(3)
        for prop in settlement.refinery(seeded(seed), WIDTH, LOOP, knobs("refinery")).props
    }
    farmland = {
        prop.kind
        for seed in range(3)
        for prop in settlement.farmland(seeded(seed), WIDTH, LOOP, knobs("farmland")).props
    }
    assert "cooling_tower" in refinery
    assert "greenhouse" in farmland


def test_a_built_up_terrain_splits_its_props_between_its_chunks():
    terrain = Terrain(Area(-1.0, 1.0, -1.3, 1.3), 1.0, params.resolve("city"), seed=5)
    assert terrain.layout is not None and terrain.props
    shares = [terrain.chunk_props(chunk) for chunk in range(terrain.chunks)]
    assert sum(len(share) for share in shares) == len(terrain.props)
