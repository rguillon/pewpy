import random

import numpy as np

from pewpy.scenery import params
from pewpy.scenery.grounds import SETTLEMENTS
from pewpy.scenery.settlement import Surface

WIDTH, LOOP = 2.4, 4.2


def knobs(name: str) -> params.Knobs:
    """The settlement's numbers in the preset of the same name."""
    found = params.resolve(name).settlement
    assert found is not None
    return found.layout


def seeded(seed: int) -> random.Random:
    return random.Random(seed)  # noqa: S311 - layouts, not cryptography


def test_farmland_has_fields_farms_and_trees():
    layout = SETTLEMENTS["farmland"].layout(seeded(3), WIDTH, LOOP, knobs("farmland"))
    assert {Surface.WHEAT, Surface.DIRT_ROAD} <= set(np.unique(layout.surface).tolist())
    kinds = {prop.kind for prop in layout.props}
    assert {"house", "barn", "silo", "tree"} <= kinds


def test_the_farms_have_greenhouses():
    farmland = {
        prop.kind
        for seed in range(3)
        for prop in SETTLEMENTS["farmland"].layout(seeded(seed), WIDTH, LOOP, knobs("farmland")).props
    }
    assert "greenhouse" in farmland
