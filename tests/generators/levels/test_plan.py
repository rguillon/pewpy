import dataclasses

import pytest

from pewpy.generators.levels.plan import LevelPlan, WorldPlan


def test_a_level_is_by_day_clear_its_layout_its_own_and_its_ground_as_planned_unless_told() -> None:
    level = LevelPlan("Somewhere", "sentinel", "avalanche")
    assert (level.time_of_day, level.clouds, level.seed, level.scenery) == ("day", 0.0, 0, {})


def test_a_world_has_ground_units_unless_told() -> None:
    world = WorldPlan("Land", "savanna", (LevelPlan("Somewhere", "sentinel", "avalanche"),))
    assert world.ground_units
    assert world.scenery == {}
    with pytest.raises(dataclasses.FrozenInstanceError):
        world.name = "Sea"  # ty: ignore[invalid-assignment]
