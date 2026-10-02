import random

import numpy as np

from pewpy.scenery import params
from pewpy.scenery.ground.kinds import FLORAS, LANDSCAPES
from pewpy.scenery.ground.kinds.geysers import MAT, MOUND_SINTER
from pewpy.scenery.ground.relief import Shape

KNOBS = {
    "spring_spacing": 0.45,
    "spring_radius": [0.04, 0.14],
    "mat_width": 1.1,
    "mound_spacing": 1.2,
    "mound_radius": [0.2, 0.32],
    "steps": 4,
    "ridge_share": 0.2,
}


def basin(seed: int = 0) -> Shape:
    return LANDSCAPES["geysers"].shape(np.random.default_rng(seed), 300, 100, 0.3, 0.02, KNOBS)


def test_the_basin_has_pools_ringed_by_mats_and_terraced_mounds() -> None:
    shape = basin()
    assert shape.marks is not None
    pools = shape.heights < 0
    assert 0.005 < pools.mean() < 0.2  # some hot pools, mostly crust
    land = shape.marks[~pools]
    assert np.any((land > 0.05) & (land <= MAT))  # mats round the pools
    assert np.any(land >= MOUND_SINTER)  # terraces...
    assert np.any(land > 0.95)  # ...with water on their ledges
    assert float(np.max(shape.heights)) <= 0.3 + 0.03
    assert float(np.max(np.abs(shape.heights[-1] - shape.heights[0]))) < 0.05  # no cliff where the loop starts again


def test_the_basin_is_reproducible() -> None:
    assert np.array_equal(basin(3).heights, basin(3).heights)
    assert not np.array_equal(basin(3).heights, basin(4).heights)


def test_snags_stand_at_the_edge_of_the_mats() -> None:
    shape = basin()
    assert shape.marks is not None
    knobs = {"chance": 0.3, "size": 0.03, "height": [0.03, 0.05]}
    snags = FLORAS["snags"].props(random.Random(1), shape, 0.02, 0.02, knobs)
    assert snags
    assert {snag.kind for snag in snags} == {"dead_tree"}
    for snag in snags:
        mark = shape.marks[round(snag.y / 0.02) % 300, min(round(snag.x / 0.02), 99)]
        assert mark < MAT


def test_the_geysers_preset_resolves() -> None:
    scenery = params.resolve("geysers")
    assert scenery.ground is not None
    assert scenery.ground.landscape == "geysers"
    assert scenery.flora is not None
    assert scenery.flora.kind == "snags"
