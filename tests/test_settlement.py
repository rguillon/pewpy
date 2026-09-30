import random

import numpy as np
import pytest

from pewpy import prop_meshes, settlement
from pewpy.background import Area
from pewpy.settlement import SETTLEMENTS, Prop, Surface
from pewpy.terrain import BIOMES, Terrain

WIDTH, LOOP = 2.4, 4.2


@pytest.mark.parametrize("name", SETTLEMENTS)
def test_every_prop_stands_inside_the_ground_without_crossing_the_loop_end(name):
    layout = SETTLEMENTS[name](seeded(1), WIDTH, LOOP)
    assert layout.surface.shape == (round(LOOP / settlement.SURFACE_STEP), round(WIDTH / settlement.SURFACE_STEP))
    assert layout.props
    for prop in layout.props:
        assert prop.y - prop.length / 2 >= 0.0 and prop.y + prop.length / 2 <= LOOP + 1e-9
        assert prop.x - prop.width / 2 >= -0.03 and prop.x + prop.width / 2 <= WIDTH + 0.03
        assert prop.height > 0
        # Nothing reaches the ships: every biome keeps its tallest thing 0.1 behind the play plane.
        assert prop.height <= BIOMES[name].depth - 0.1


def seeded(seed: int) -> random.Random:
    return random.Random(seed)  # noqa: S311 - layouts, not cryptography


def test_the_city_has_streets_pavements_and_buildings_of_every_size():
    layout = settlement.city(seeded(2), WIDTH, LOOP)
    surfaces = set(np.unique(layout.surface).tolist())
    assert {Surface.STREET, Surface.PAVEMENT} <= surfaces
    heights = [prop.height for prop in layout.props if prop.kind == "building"]
    assert min(heights) < 0.13 and max(heights) > 0.3


def test_farmland_has_fields_farms_and_trees():
    layout = settlement.farmland(seeded(3), WIDTH, LOOP)
    assert {Surface.WHEAT, Surface.DIRT_ROAD} <= set(np.unique(layout.surface).tolist())
    kinds = {prop.kind for prop in layout.props}
    assert {"house", "barn", "silo", "tree"} <= kinds


def test_refinery_has_tanks_stacks_and_plants():
    kinds = {prop.kind for prop in settlement.refinery(seeded(4), WIDTH, LOOP).props}
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


@pytest.mark.parametrize(
    "kind",
    ["building", "house", "barn", "silo", "tank", "plant", "stack", "pipes", "tree", "hedge", "palm", "dead_tree"],
)
def test_every_kind_of_prop_has_a_mesh_around_its_footprint(kind):
    prop = Prop(kind, x=0.5, y=0.3, width=0.12, length=0.1, height=0.3 if kind == "building" else 0.06, seed=7)
    vertices, triangles = prop_meshes.strip_arrays([prop], first_y=0.2)
    assert len(triangles) % 3 == 0 and len(triangles) > 0
    assert int(np.max(triangles)) < len(vertices)
    assert np.isfinite(vertices).all()
    # Model space: x as is, depth -y is the height, z up the screen from the strip's top edge.
    xs, heights, zs = vertices[:, 0], -vertices[:, 1], vertices[:, 2]
    assert float(np.min(xs)) >= 0.5 - 0.07 and float(np.max(xs)) <= 0.5 + 0.07
    assert float(np.min(heights)) >= -prop_meshes.SUNK - 1e-6
    # Chimneys, domes and flames (as big as the stack) stick out on top.
    assert float(np.max(heights)) <= prop.height * 1.6 + 0.07 + max(prop.width, prop.length)
    assert float(np.max(-zs)) <= 0.3 - 0.2 + 0.07


def test_a_built_up_terrain_splits_its_props_between_its_chunks():
    terrain = Terrain(Area(-1.0, 1.0, -1.3, 1.3), 1.0, seed=5, biome="city")
    assert terrain.layout is not None and terrain.props
    shares = [terrain.chunk_props(chunk) for chunk in range(terrain.chunks)]
    assert sum(len(share) for share in shares) == len(terrain.props)
