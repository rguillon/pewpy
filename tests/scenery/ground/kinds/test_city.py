import random

import numpy as np

from pewpy.scenery import params
from pewpy.scenery.ground.kinds import SETTLEMENTS
from pewpy.scenery.ground.settlement import Surface

WIDTH, LOOP = 2.4, 4.2


def knobs(name: str) -> params.Knobs:
    """The settlement's numbers in the preset of the same name."""
    found = params.resolve(name).settlement
    assert found is not None
    return found.layout


def seeded(seed: int) -> random.Random:
    return random.Random(seed)  # noqa: S311 - layouts, not cryptography


def test_the_city_has_streets_pavements_and_buildings_of_every_size():
    layout = SETTLEMENTS["city"].layout(seeded(2), WIDTH, LOOP, knobs("city"))
    surfaces = set(np.unique(layout.surface).tolist())
    assert {Surface.STREET, Surface.PAVEMENT} <= surfaces
    heights = [prop.height for prop in layout.props if prop.kind == "building"]
    assert min(heights) < 0.13 and max(heights) > 0.3
