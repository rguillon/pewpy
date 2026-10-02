import random

from pewpy.scenery import params
from pewpy.scenery.ground.kinds import SETTLEMENTS

WIDTH, LOOP = 2.4, 4.2


def knobs(name: str) -> params.Knobs:
    """The settlement's numbers in the preset of the same name."""
    found = params.resolve(name).settlement
    assert found is not None
    return found.layout


def seeded(seed: int) -> random.Random:
    return random.Random(seed)  # noqa: S311 - layouts, not cryptography


def test_refinery_has_tanks_stacks_and_plants():
    kinds = {prop.kind for prop in SETTLEMENTS["refinery"].layout(seeded(4), WIDTH, LOOP, knobs("refinery")).props}
    assert {"tank", "stack", "plant"} <= kinds


def test_the_refinery_has_cooling_towers():
    refinery = {
        prop.kind
        for seed in range(3)
        for prop in SETTLEMENTS["refinery"].layout(seeded(seed), WIDTH, LOOP, knobs("refinery")).props
    }
    assert "cooling_tower" in refinery
